"""CPU fault injection for durable SWE lifecycle; never native benchmark acceptance."""

import asyncio
import os
import shutil
import sys
from pathlib import Path

import pytest
from tests.ci.ci_register import register_cpu_ci
from tests.manual.agent_opd import swe_evaluation as swe
from tests.manual.agent_opd.swe_native_evaluation import _stop_child_tree

# Measured testcase runtime: 137.325s with qualification fixtures; retain CPU headroom.
register_cpu_ci(est_time=180, suite="stage-b-cpu", labels=["eval", "ckpt"])

REFERENCE = Path("/data/ycfeng/steptron/.worktrees/step3p6-replay-v1")
ALLOCATION_IDENTITY = {"task_id": "fixture-swe", "creator": "fixture-user", "gpu_tag": "H200"}
ALLOCATION = {
    "job_id": "fixture-local", "eval_gpus": 2,
    "admission": {
        "job": "fixture-local", "submitted": True, "admitted": True, "scope": "task", "preemptible": False,
        "requested_gpus": 2, "committed_gpus": 62, "ceiling_gpus": 64,
        "creator": "fixture-user", "gpu_tag": "H200",
        "evaluated_at": "2026-11-08T20:00:00+00:00",
        "policy": {"task_id": "fixture-swe", "personal_nonpreemptible_gpus": 56,
                   "temporary_task_allocation": {"expires_at": "2026-11-08T21:00:00+00:00",
                                                 "nonpreemptible_gpus": 64}},
    },
}


@pytest.fixture
def case(tmp_path, monkeypatch):
    # Isolate only the reference scorer import; assertions below exercise the real store.
    # Ordinary CI lacks the user's external Steptron checkout.
    if not REFERENCE.is_dir():
        import types

        module = types.ModuleType("playground.users.ycfeng.MOPD.bounded_replay_evaluation")
        module.FourAttempts = _FourAttemptsFixture
        monkeypatch.setitem(sys.modules, module.__name__, module)
    source = tmp_path / "original4b"
    source.mkdir()
    (source / "weights").write_bytes(b"original-source")
    store = swe.EvaluationStore(
        tmp_path / "evaluations", owned_root=tmp_path / "owned", protected_sources=[source], reference_root=REFERENCE,
        allocation_identity=ALLOCATION_IDENTITY,
    )
    hf = tmp_path / "owned" / "A-full" / "attempt-1" / "hf" / "step_199"
    hf.mkdir(parents=True)
    for filename in (".complete", "config.json", "tokenizer.json", "tokenizer_config.json"):
        (hf / filename).write_text("{}")
    (hf / "model-1.safetensors").write_bytes(b"fixture-not-real-hf")
    swe.write_json(hf / "model.safetensors.index.json", {"weight_map": {"fixture": "model-1.safetensors"}})
    tasks = [f"fixture__task-{i}" for i in range(100)]
    native = {
        "successful_update": 200,
        "rollout_id": 213,
        "checkpoint_index": 199,
        "weight_version": "native-v214",
        "native_counters": {"optimizer_success": 200, "optimizer_skip": 14},
    }
    swe.write_json(hf / "qwen_text_export.json", {"status": "packaged", "run_kind": "formal", "source": str(source), **native})
    enqueue = {
        "point_id": "A-full.attempt-1.HF200",
        "checkpoint_dir": hf,
        "native_update": native,
        "source": source,
        "task_ids": tasks,
        "configuration": {"scope": "formal_subset"},
    }
    store.enqueue_checkpoint(**enqueue)
    return store, enqueue, hf, source, tasks


class _FourAttemptsFixture:
    """Test-only port of the reference's 400-slot summary for portable CPU CI."""

    def __init__(self, tasks, *, seeds, scope, domain):
        self.tasks, self.seeds, self.rows = tasks, seeds, []

    def record(self, task_id, attempt, *, success, raw):
        self.rows.append(
            {
                "kind": "result",
                "uid": f"{task_id}#attempt-{attempt}",
                "task_id": task_id,
                "attempt": attempt,
                "success": success,
                "raw": raw,
            }
        )

    def infra_failure(self, task_id, attempt, *, error, raw):
        self.rows.append(
            {
                "kind": "infra_failure",
                "uid": f"{task_id}#attempt-{attempt}",
                "task_id": task_id,
                "attempt": attempt,
                "error": error,
                "raw": raw,
            }
        )

    def summarize(self):
        completed = {(row["task_id"], row["attempt"]): row["success"] for row in self.rows if row["kind"] == "result"}
        missing = [
            f"{task}#attempt-{attempt}"
            for task in self.tasks
            for attempt in range(4)
            if (task, attempt) not in completed
        ]
        successes = sum(completed.values())
        return {
            "denominator": 400,
            "completed": len(completed),
            "successes": successes,
            "missing_attempt_ids": missing,
            "avg_at_n": None if missing else successes / 400,
            "raw_records": self.rows,
            "status": "INCOMPLETE" if missing else "COMPLETE",
        }


def _start(case, now=None):
    store, enqueue, *_ = case
    assert store.start(enqueue["point_id"], allocation=ALLOCATION, now=now)
    return store, enqueue["point_id"]


def _finish_all(store, point_id, success=False):
    for task in store.manifest(point_id)["task_ids"]:
        for attempt in range(4):
            request = store.request(point_id, task, attempt)
            store.record(point_id, request, success=success, raw={"fixture": True})
    return store.settle(point_id)


def test_native_mapping_not_update_minus_one(case):
    store, enqueue, *_ = case
    manifest = store.manifest(enqueue["point_id"])
    assert manifest["native_update"]["successful_update"] == 200
    assert manifest["native_update"]["rollout_id"] == 213
    assert store.state(enqueue["point_id"])["deadline_at"] is None
    assert store.queued() == (enqueue["point_id"],)


@pytest.mark.parametrize("partial", ["missing-marker", "unverified-package", "missing-shard"])
def test_partial_export_rejected(case, partial):
    store, enqueue, hf, *_ = case
    if partial == "missing-marker":
        (hf / ".complete").unlink()
    elif partial == "unverified-package":
        row = swe.read_json(hf / "qwen_text_export.json")
        row["status"] = "unverified"
        swe.write_json(hf / "qwen_text_export.json", row)
    else:
        (hf / "model-1.safetensors").unlink()
    with pytest.raises(ValueError):
        store.enqueue_checkpoint(**(enqueue | {"point_id": "partial"}))
    assert not (store._point("partial") / "manifest.json").exists()


def test_idempotent_enqueue_and_identity_conflict(case):
    store, enqueue, *_ = case
    assert store.enqueue_checkpoint(**enqueue) == enqueue["point_id"]
    changed = enqueue["native_update"] | {"weight_version": "different"}
    with pytest.raises(ValueError, match="immutable|publication"):
        store.enqueue_checkpoint(**(enqueue | {"native_update": changed}))


def test_missing_score_is_null_no_shrunken_denominator(case):
    store, point_id = _start(case)
    request = store.request(point_id, store.manifest(point_id)["task_ids"][0], 0)
    store.record(point_id, request, success=True, raw={"fixture": True})
    summary = store.settle(point_id)
    assert summary["denominator"] == 400 and summary["completed"] == 1
    assert summary["avg_at_n"] is None
    with pytest.raises(ValueError, match="Incomplete"):
        store.release(point_id)


def test_completed_model_failure_cannot_reroll(case):
    store, point_id = _start(case)
    request = store.request(point_id, store.manifest(point_id)["task_ids"][0], 0)
    store.record(point_id, request, success=False, raw={"native": "unresolved"})
    with pytest.raises(ValueError, match="rerolled"):
        store.record(point_id, request, success=True, raw={"native": "resolved"})
    assert request["uid"] not in store.summary(point_id)["missing_attempt_ids"]


def test_complete400_avg_and_hf200_release_bytes(case):
    store, point_id = _start(case)
    summary = _finish_all(store, point_id, success=True)
    expected_bytes = sum(item["bytes"] for item in store.manifest(point_id)["files"])
    assert summary["denominator"] == 400 and summary["avg_at_n"] == 1.0
    receipt = store.release(point_id)
    assert receipt["deleted_bytes"] == expected_bytes and receipt["status"] == "RELEASED"
    assert not case[2].exists()
    assert case[3].is_dir()
    assert store.release(point_id) == receipt


def test_live_reader_blocks_release_and_recovery(case):
    store, point_id = _start(case)
    store.reader_enter(point_id, "server", {"pid": "fixture"})
    _finish_all(store, point_id)
    with pytest.raises(ValueError, match="readers"):
        store.release(point_id)
    store.reader_exit(point_id, "server", {"platform_status": "SUCCEEDED", "all_children_exited": True})
    assert store.release(point_id)["status"] == "RELEASED"


def test_restart_keeps_original_deadline_and_requires_reader_exit(case):
    store, point_id = _start(case, now=1000)
    store.reader_enter(point_id, "crashed-worker", {"pid": "fixture"})
    restarted = swe.EvaluationStore(
        store.root, owned_root=store.owned_root, protected_sources=store.protected_sources, reference_root=REFERENCE,
        allocation_identity=ALLOCATION_IDENTITY,
    )
    with pytest.raises(ValueError, match="proven exited"):
        restarted.resume(point_id, diagnosis="worker crashed", remedy="new worker", now=1100)
    restarted.reader_exit(point_id, "crashed-worker", {"actual_terminal_receipt": "fixture"})
    assert restarted.resume(point_id, diagnosis="worker crashed", remedy="replacement admitted", now=1100) == "QUEUED"
    assert restarted.start(point_id, allocation=ALLOCATION, now=1200)
    state = restarted.state(point_id)
    assert state["first_started_at"] == 1000 and state["deadline_at"] == 1000 + 72 * 3600


def test_restart_after_deadline_never_renews(case):
    store, point_id = _start(case, now=1000)
    state = store.state(point_id)
    assert store.resume(point_id, diagnosis="infrastructure", remedy="fixed", now=state["deadline_at"]) == "EXPIRED"
    assert store.state(point_id)["deadline_at"] == state["deadline_at"]
    with pytest.raises(ValueError):
        store.release(point_id)
    assert case[2].is_dir()


def test_queue_wait_does_not_start_deadline_and_no_capacity_skip(case):
    store, enqueue, hf, *_ = case
    for i in range(16):
        another = hf.parents[3] / f"attempt-{i + 2}" / "hf" / hf.name
        shutil.copytree(hf, another)
        store.enqueue_checkpoint(**(enqueue | {"point_id": f"queued-{i}", "checkpoint_dir": another}))
    assert len(store.queued()) == 17
    assert all(store.state(point)["first_started_at"] is None for point in store.queued())


def test_manifest_survives_crash_before_queue_state(case):
    store, enqueue, *_ = case
    (store._point(enqueue["point_id"]) / "state.json").unlink()
    assert store.queued() == (enqueue["point_id"],)
    assert store.state(enqueue["point_id"])["first_started_at"] is None


def test_same_owned_hf_cannot_be_enqueued_as_new_point(case):
    store, enqueue, *_ = case
    with pytest.raises(ValueError, match="another immutable"):
        store.enqueue_checkpoint(**(enqueue | {"point_id": "duplicate"}))


@pytest.mark.parametrize("total", [65, -1])
def test_resource_admission_includes_eval_gpus(case, total):
    store, enqueue, *_ = case
    with pytest.raises(ValueError, match="admission"):
        store.start(enqueue["point_id"], allocation=ALLOCATION | {
            "admission": ALLOCATION["admission"] | {"committed_gpus": total}})


def test_baseline_and_history_protected(case):
    store, enqueue, hf, source, tasks = case
    store.enqueue_baseline(point_id="original4b", source=source, task_ids=tasks, configuration={})
    assert store.release("original4b") == {"status": "PROTECTED_SOURCE", "deleted_bytes": 0}
    with pytest.raises(ValueError, match="scope|protected"):
        store.enqueue_checkpoint(**(enqueue | {"checkpoint_dir": source, "point_id": "unsafe"}))
    assert source.is_dir() and hf.is_dir()


def test_mutated_hf_and_foreign_file_not_deleted(case):
    store, point_id = _start(case)
    _finish_all(store, point_id)
    (case[2] / "not-owned").write_text("other writer")
    with pytest.raises(ValueError, match="unowned"):
        store.release(point_id)
    assert (case[2] / "model-1.safetensors").is_file()


def test_symlink_source_not_owned(case):
    store, enqueue, hf, source, *_ = case
    (hf / "source-link").symlink_to(source / "weights")
    with pytest.raises(ValueError, match="symlink"):
        store.enqueue_checkpoint(**(enqueue | {"point_id": "unsafe-link"}))
    assert (source / "weights").read_bytes() == b"original-source"


def test_release_recovery_after_unlink_before_receipt(case, monkeypatch):
    store, point_id = _start(case)
    _finish_all(store, point_id)
    original = swe.write_json
    interrupted = False

    def fail_receipt(path, row):
        nonlocal interrupted
        if Path(path).name == "release.json" and row["deleted_files"] and not interrupted:
            interrupted = True
            raise OSError("fault injection after first unlink")
        return original(path, row)

    monkeypatch.setattr(swe, "write_json", fail_receipt)
    with pytest.raises(OSError, match="fault injection"):
        store.release(point_id)
    monkeypatch.setattr(swe, "write_json", original)
    receipt = store.release(point_id)
    assert receipt["status"] == "RELEASED"
    assert receipt["deleted_bytes"] == sum(item["bytes"] for item in receipt["files"])


def test_hung_head_does_not_block_later_seed_persistence_and_missing_only_restart(case):
    store, enqueue, _, _, tasks = case
    point_id = enqueue["point_id"]

    async def scenario():
        held = asyncio.Event()
        later = asyncio.Event()

        async def runner(request, deadline):
            if request["attempt"] == 0 and request["task_id"] == tasks[0]:
                held.set()
                await asyncio.Event().wait()
            if request["attempt"] == 1 and request["task_id"] == tasks[0]:
                later.set()
            return {"success": False, "raw": {"fixture": request["uid"]}}

        job = asyncio.create_task(swe.evaluate(store, point_id, runner=runner, allocation=ALLOCATION))
        await held.wait()
        await later.wait()
        for _ in range(100):
            if store.summary(point_id)["completed"]:
                break
            await asyncio.sleep(0)
        summary = store.summary(point_id)
        assert summary["completed"] > 0
        assert f"{tasks[0]}#attempt-0" in summary["missing_attempt_ids"]
        job.cancel()
        with pytest.raises(asyncio.CancelledError):
            await job
        first_deadline = store.state(point_id)["deadline_at"]
        saved = {path.name: path.read_bytes() for path in (store._point(point_id) / "results").glob("*.json")}
        expected_missing = set(store.summary(point_id)["missing_attempt_ids"])
        store.resume(point_id, diagnosis="fixture hung child", remedy="fixture unblocked")
        issued = set()

        async def recovered(request, deadline):
            issued.add(request["uid"])
            return {"success": True, "raw": {"fixture": "recovery"}}

        result = await swe.evaluate(store, point_id, runner=recovered, allocation=ALLOCATION)
        assert issued == expected_missing and result["completed"] == 400
        assert store.state(point_id)["deadline_at"] == first_deadline
        assert all((store._point(point_id) / "results" / name).read_bytes() == raw for name, raw in saved.items())

    asyncio.run(scenario())


def test_child_tree_cleanup_reaps_native_subprocess(tmp_path):
    async def scenario():
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-c", "import time; time.sleep(60)", start_new_session=True
        )
        await _stop_child_tree(process, 0.1)
        assert process.returncode is not None
        with pytest.raises(ProcessLookupError):
            os.kill(process.pid, 0)

    asyncio.run(scenario())


def test_four_seed_cancellation_joins_slow_native_cleanup(case, tmp_path):
    store, enqueue, *_ = case

    async def scenario():
        processes, cleanups = [], []
        ready = asyncio.Event()
        command = (
            "import signal,time; from pathlib import Path; "
            "signal.signal(signal.SIGTERM, lambda *args: (time.sleep(float(__import__('sys').argv[2])), exit(0))); "
            "Path(__import__('sys').argv[1]).touch(); time.sleep(60)"
        )

        async def runner(request, deadline):
            marker = tmp_path / str(request["seed"])
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-c", command, str(marker), str(0.05 + 0.2 * request["attempt"]), start_new_session=True
            )
            processes.append(process)
            try:
                while not marker.exists():
                    await asyncio.sleep(0.01)
                if all((tmp_path / str(seed)).exists() for seed in swe.SEEDS):
                    ready.set()
                await process.wait()
            finally:
                await _stop_child_tree(process, 1)
                cleanups.append(process.pid)

        job = asyncio.create_task(swe.evaluate(store, enqueue["point_id"], runner=runner, allocation=ALLOCATION))
        try:
            await asyncio.wait_for(ready.wait(), 5)
            job.cancel()
            with pytest.raises(asyncio.CancelledError):
                await job
            assert len(cleanups) == 4
            for process in processes:
                assert process.returncode == 0
                with pytest.raises(ProcessLookupError):
                    os.kill(process.pid, 0)
            assert all(reader["status"] == "EXITED" for reader in store.state(enqueue["point_id"])["readers"].values())
        finally:
            for process in processes:
                await _stop_child_tree(process, 1)

    asyncio.run(scenario())


def test_manifest_order_not_library_order(tmp_path):
    ids = [f"fixture__task-{i}" for i in range(500)]
    swe.write_json(tmp_path / "manifest.json", {"source_group": "swe", "benchmark": {"task_ids": ids}})
    swe.write_json(tmp_path / "library.json", [{"instance_id": task} for task in reversed(ids)])
    assert swe.benchmark_tasks(tmp_path / "manifest.json", tmp_path / "library.json") == tuple(ids[:100])


def test_absolute_deadline_cancels_hung_attempt_and_preserves_hf(case, monkeypatch):
    store, enqueue, hf, *_ = case
    monkeypatch.setattr(swe, "EVALUATION_SECONDS", 0.5)
    cleaned = []

    async def runner(request, deadline):
        if request["attempt"] == 0:
            try:
                await asyncio.Event().wait()
            finally:
                cleaned.append(request["uid"])
        return {"success": False, "raw": {"fixture": True}}

    result = asyncio.run(swe.evaluate(store, enqueue["point_id"], runner=runner, allocation=ALLOCATION))
    assert cleaned and result["avg_at_n"] is None and result["denominator"] == 400
    assert store.state(enqueue["point_id"])["status"] == "EXPIRED" and hf.is_dir()
    with pytest.raises(ValueError, match="Incomplete"):
        store.release(enqueue["point_id"])


def test_live_reader_proof_required_after_cleanup_failure(case):
    store, point_id = _start(case)
    store.reader_enter(point_id, "child-not-reaped", {"process_group": "fixture"})
    store.settle(point_id)
    with pytest.raises(ValueError, match="proven exited"):
        store.resume(point_id, diagnosis="failed cleanup", remedy="relaunch")


def test_completed_later_point_remains_queued_while_first_running(case):
    store, enqueue, hf, *_ = case
    another = hf.parents[3] / "another-cell" / "hf" / hf.name
    shutil.copytree(hf, another)
    store.enqueue_checkpoint(**(enqueue | {"point_id": "later", "checkpoint_dir": another}))
    store.start(enqueue["point_id"], allocation=ALLOCATION)
    assert store.queued() == ("later",)


def test_corrupt_native_archive_prevents_release(case):
    store, point_id = _start(case)
    artifact = store._point(point_id) / "native" / "grader.json"
    swe.write_json(artifact, {"status": "unresolved"})
    import hashlib

    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    tasks = store.manifest(point_id)["task_ids"]
    for task in tasks:
        for attempt in range(4):
            store.record(
                point_id,
                store.request(point_id, task, attempt),
                success=False,
                raw={"native_artifacts": {"grader": {"path": str(artifact), "sha256": digest}}},
            )
    store.settle(point_id)
    swe.write_json(artifact, {"status": "resolved"})
    with pytest.raises(ValueError, match="bytes changed"):
        store.release(point_id)
    assert case[2].is_dir()


def test_existing_checkpoint_evaluator_seam_enqueues_without_native_dependencies(case, monkeypatch):
    from types import SimpleNamespace

    from tests.manual.agent_opd.swe_evaluation_fn import SweEvaluationFn

    from miles.rollout.base_types import RolloutFnConstructorInput, RolloutFnEvalInput
    from miles.rollout.checkpoint_eval import is_checkpoint_eval_fn

    store, enqueue, hf, source, tasks = case
    configuration = {
        "root": str(store.root),
        "owned_root": str(store.owned_root),
        "protected_sources": [str(source)],
        "reference_root": str(REFERENCE),
        "allocation_identity": ALLOCATION_IDENTITY,
        "task_ids": tasks,
        "evaluation_contract": enqueue["configuration"],
        "publications": {
            "213": {"point_id": enqueue["point_id"], "native_update": enqueue["native_update"], "source": str(source)}
        },
    }
    config_path = hf.parents[3] / "configuration.json"
    swe.write_json(config_path, configuration)
    monkeypatch.setenv("MILES_SWE_EVALUATION_CONFIGURATION", str(config_path))
    assert is_checkpoint_eval_fn("tests.manual.agent_opd.swe_evaluation_fn.SweEvaluationFn")
    backend = SweEvaluationFn(RolloutFnConstructorInput(args=SimpleNamespace(), data_source=None))
    output = asyncio.run(backend.evaluate_checkpoint(str(hf), RolloutFnEvalInput(rollout_id=213, hf_dir=str(hf))))
    assert output.metrics == {"swe_enqueued": 1} and output.data == {}
    (hf / ".complete").unlink()
    failure = asyncio.run(backend.evaluate_checkpoint(str(hf), RolloutFnEvalInput(rollout_id=213, hf_dir=str(hf))))
    assert failure.metrics == {"swe_enqueue_unverified": 1}
    assert hf.is_dir()


@pytest.fixture
def qualification_case(case):
    original_store, _, _, source, tasks = case
    store = swe.EvaluationStore(
        original_store.root.parent / "qualification-evaluations",
        owned_root=original_store.owned_root,
        protected_sources=original_store.protected_sources,
        reference_root=REFERENCE,
        allocation_identity=ALLOCATION_IDENTITY,
    )
    hf = store.owned_root / "A-r256" / "smoke-attempt" / "hf" / "step_2"
    hf.mkdir(parents=True)
    for filename in ("config.json", "tokenizer.json", "tokenizer_config.json"):
        (hf / filename).write_text("{}")
    (hf / "model-1.safetensors").write_bytes(b"fixture-smoke-not-real-hf")
    swe.write_json(hf / "model.safetensors.index.json", {"weight_map": {"fixture": "model-1.safetensors"}})
    native = {
        "successful_update": 3,
        "checkpoint_index": 2,
        "rollout_id": 2,
        "weight_version": 3,
        "native_counters": {"successful_updates": 3, "native_attempted_count": 3, "native_skipped_count": 0},
    }
    swe.write_json(
        hf / "qwen_text_export.json",
        {
            "status": "packaged",
            "source": str(source),
            "run_kind": "smoke",
            **native,
        },
    )
    swe.write_json(hf / ".complete", {})
    publication = hf.parent.parent / "hf_publications" / "step_2.json"
    swe.write_json(
        publication,
        {
            "checkpoint_dir": str(hf),
            "status": "SMOKE_PACKAGED",
            "run_kind": "smoke",
            "formal_evaluation": False,
            "native_update": native,
            "cell": "A/r256",
            "attempt": "smoke-attempt",
        },
    )
    enqueue = {
        "point_id": "qualification.A-r256-smoke-HF3",
        "checkpoint_dir": hf,
        "source": source,
        "task_ids": tasks,
        "configuration": {"fixture": "unchanged-full400-contract"},
    }
    return store, enqueue, hf, source, native, publication


def test_qualification_preserves_actual_smoke_identity_and_full400(qualification_case):
    store, enqueue, hf, source, native, _ = qualification_case
    before = {path.name: path.read_bytes() for path in hf.iterdir()}
    original_bytes = (source / "weights").read_bytes()
    assert store.enqueue_qualification_checkpoint(**enqueue) == enqueue["point_id"]
    manifest = store.manifest(enqueue["point_id"])
    assert manifest["run_kind"] == "qualification" and manifest["owned"] is True
    assert manifest["checkpoint_dir"] == str(hf) and manifest["native_update"] == native
    assert manifest["configuration"] == enqueue["configuration"]
    assert len(manifest["task_ids"]) == 100 and manifest["seeds"] == list(swe.SEEDS)
    summary = store.summary(enqueue["point_id"])
    assert summary["completed"] == 0 and summary["denominator"] == 400
    assert len(summary["missing_attempt_ids"]) == 400 and summary["avg_at_n"] is None
    assert store.state(enqueue["point_id"])["deadline_at"] is None
    assert store.enqueue_qualification_checkpoint(**enqueue) == enqueue["point_id"]
    assert store.manifest(enqueue["point_id"]) == manifest
    assert {path.name: path.read_bytes() for path in hf.iterdir()} == before
    assert (source / "weights").read_bytes() == original_bytes


def test_qualification_cannot_bypass_the_formal_update_gate(qualification_case):
    store, enqueue, _, _, native, _ = qualification_case
    assert swe.HF_UPDATES == (50, 100, 150, 200)
    with pytest.raises(ValueError, match="not an HF evaluation point"):
        store.enqueue_checkpoint(**enqueue, native_update=native)
    assert not (store._point(enqueue["point_id"]) / "manifest.json").exists()


@pytest.mark.parametrize(
    "root,point",
    [
        ("evaluations", "qualification.smoke"),
        ("qualification-evaluations", "A-r256.HF50"),
        ("qualification-evaluations", "qualification."),
    ],
)
def test_qualification_namespace_is_explicit(qualification_case, root, point):
    store, enqueue, *_ = qualification_case
    store.root = store.root.parent / root
    with pytest.raises(ValueError, match="qualification|Identity"):
        store.enqueue_qualification_checkpoint(**(enqueue | {"point_id": point}))
    assert not (store._point(point) / "manifest.json").exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", "QUEUED"),
        ("run_kind", "formal"),
        ("formal_evaluation", True),
        ("checkpoint_dir", "/unrelated/hf/step_2"),
    ],
)
def test_qualification_requires_the_actual_smoke_publication(qualification_case, field, value):
    store, enqueue, _, _, _, publication = qualification_case
    row = swe.read_json(publication)
    swe.write_json(publication, row | {field: value})
    with pytest.raises(ValueError, match="SMOKE_PACKAGED"):
        store.enqueue_qualification_checkpoint(**enqueue)


@pytest.mark.parametrize(
    "field,value",
    [
        ("run_kind", "formal"),
        ("successful_update", 4),
        ("checkpoint_index", 3),
        ("rollout_id", 3),
        ("weight_version", 4),
        ("native_counters", {"successful_updates": 3, "native_attempted_count": 4, "native_skipped_count": 1}),
        ("source", "/unrelated/original-4b"),
    ],
)
def test_qualification_package_and_native_publication_must_match(qualification_case, field, value):
    store, enqueue, hf, *_ = qualification_case
    package = swe.read_json(hf / "qwen_text_export.json")
    swe.write_json(hf / "qwen_text_export.json", package | {field: value})
    swe.write_json(hf / ".complete", {})
    with pytest.raises(ValueError, match="smoke|identity|counters"):
        store.enqueue_qualification_checkpoint(**enqueue)


@pytest.mark.parametrize(
    "field,value",
    [
        ("successful_updates", 4),
        ("native_attempted_count", 4),
        ("native_skipped_count", -1),
        ("native_attempted_count", True),
    ],
)
def test_qualification_rejects_inconsistent_native_counters(qualification_case, field, value):
    store, enqueue, hf, _, _, publication = qualification_case
    row = swe.read_json(publication)
    row["native_update"]["native_counters"][field] = value
    swe.write_json(publication, row)
    package = swe.read_json(hf / "qwen_text_export.json")
    package["native_counters"][field] = value
    swe.write_json(hf / "qwen_text_export.json", package)
    swe.write_json(hf / ".complete", {})
    with pytest.raises(ValueError, match="counters"):
        store.enqueue_qualification_checkpoint(**enqueue)


@pytest.mark.parametrize(
    "field,value",
    [
        ("successful_update", 0),
        ("rollout_id", -1),
        ("weight_version", "3"),
        ("checkpoint_index", 3),
    ],
)
def test_qualification_rejects_non_native_update_version_index(qualification_case, field, value):
    store, enqueue, _, _, _, publication = qualification_case
    row = swe.read_json(publication)
    row["native_update"][field] = value
    swe.write_json(publication, row)
    with pytest.raises(ValueError, match="native|index"):
        store.enqueue_qualification_checkpoint(**enqueue)


@pytest.mark.parametrize("failure", ["missing-marker", "stale-marker", "unpackaged", "missing-shard"])
def test_qualification_rejects_partial_or_stale_exports(qualification_case, failure):
    store, enqueue, hf, *_ = qualification_case
    if failure == "missing-marker":
        (hf / ".complete").unlink()
    elif failure == "stale-marker":
        stale = (hf / "qwen_text_export.json").stat().st_mtime_ns - 1
        os.utime(hf / ".complete", ns=(stale, stale))
    elif failure == "unpackaged":
        package = swe.read_json(hf / "qwen_text_export.json")
        swe.write_json(hf / "qwen_text_export.json", package | {"status": "unverified"})
    else:
        (hf / "model-1.safetensors").unlink()
    with pytest.raises(ValueError, match="Partial|Stale|incomplete"):
        store.enqueue_qualification_checkpoint(**enqueue)
    assert not (store._point(enqueue["point_id"]) / "manifest.json").exists()


def test_qualification_protects_original_and_current_owned_root(qualification_case, tmp_path):
    store, enqueue, hf, source, *_ = qualification_case
    store.owned_root = source.parent
    with pytest.raises(ValueError, match="protected"):
        store.enqueue_qualification_checkpoint(**(enqueue | {"checkpoint_dir": source}))
    store.owned_root = tmp_path / "another-owned-root"
    with pytest.raises(ValueError, match="owned root"):
        store.enqueue_qualification_checkpoint(**enqueue)
    with pytest.raises(ValueError, match="protected original"):
        store.enqueue_qualification_checkpoint(**(enqueue | {"source": hf}))
    assert (source / "weights").read_bytes() == b"original-source"


def test_qualification_never_releases_even_after_all400_slots_complete(qualification_case):
    store, enqueue, hf, source, *_ = qualification_case
    store.enqueue_qualification_checkpoint(**enqueue)
    point = enqueue["point_id"]
    inventory = swe._file_inventory(hf)
    assert store.release(point) == {"status": "PROTECTED_QUALIFICATION", "deleted_bytes": 0}
    store.start(point, allocation=ALLOCATION)
    assert _finish_all(store, point)["status"] == "COMPLETE"
    assert store.release(point) == {"status": "PROTECTED_QUALIFICATION", "deleted_bytes": 0}
    assert store.state(point)["status"] == "COMPLETE" and swe._file_inventory(hf) == inventory
    assert not (store._point(point) / "release.json").exists()
    assert source.is_dir()


def test_accounting_distinguishes_unstarted_failure_events_and_recovered_slots(case):
    store, point = _start(case)
    initial = store.summary(point)
    assert initial["accounting"]["unstarted"] == 400 and initial["accounting"]["attempted"] == 0
    request = store.request(point, case[4][0], 0)
    failure = store.infra_failure(point, request, {"type": "ConnectionError", "message": "fixture connection failure"})
    assert failure.is_file()
    failed = store.settle(point)
    assert failed["accounting"] == {
        "attempted": 1,
        "successful": 0,
        "model_failed": 0,
        "timed_out": 0,
        "infra_failed": 1,
        "skipped": 0,
        "unstarted": 399,
        "in_progress": 0,
        "failure_events": 1,
    }
    assert failed["failure_paths"] == [str(failure)]
    assert failed["denominator"] == 400 and failed["avg_at_n"] is None
    assert request["uid"] in failed["missing_attempt_ids"]
    deadline = store.state(point)["deadline_at"]
    store.resume(point, diagnosis="fixture connection failed", remedy="fixture connection repaired")
    assert store.start(point, allocation=ALLOCATION)
    store.record(point, request, success=True, raw={"fixture": "recovery"})
    second = store.request(point, case[4][1], 0)
    store.record(point, second, success=False, raw={"fixture": "completed model failure"})
    recovered = store.summary(point)
    assert recovered["accounting"] == {
        "attempted": 2,
        "successful": 1,
        "model_failed": 1,
        "timed_out": 0,
        "infra_failed": 0,
        "skipped": 0,
        "unstarted": 398,
        "in_progress": 0,
        "failure_events": 1,
    }
    assert recovered["failure_paths"] == [str(failure)] and failure.is_file()
    assert store.state(point)["deadline_at"] == deadline
    with pytest.raises(ValueError, match="rerolled"):
        store.record(point, second, success=True, raw={"fixture": "forbidden reroll"})


def test_accounting_active_recovery_uses_existing_native_reader(case, monkeypatch):
    store, point = _start(case)
    request = store.request(point, case[4][0], 0)
    monkeypatch.setattr(swe.time, "time", lambda: 100.0)
    store.infra_failure(point, request, {"type": "TimeoutError", "message": "fixture timeout"})
    monkeypatch.setattr(swe.time, "time", lambda: 101.0)
    store.reader_enter(point, "native-reader", {"request": request, "destination": "fixture-native-directory"})
    assert store.summary(point)["accounting"]["in_progress"] == 1
    assert store.summary(point)["accounting"]["timed_out"] == 0
    monkeypatch.setattr(swe.time, "time", lambda: 102.0)
    store.reader_exit(point, "native-reader", {"returncode": 0, "all_live_group_members_exited": True})
    reader = store.state(point)["readers"]["native-reader"]
    assert reader["started_at"] == 101.0 and reader["finished_at"] == 102.0
    assert store.summary(point)["accounting"]["infra_failed"] == 1
    store.record(point, request, success=True, raw={"fixture": "recovered scored outcome"})
    counts = store.summary(point)["accounting"]
    assert counts["successful"] == 1 and counts["attempted"] == 1 and counts["failure_events"] == 1
    assert counts["infra_failed"] == counts["timed_out"] == counts["in_progress"] == 0


def test_accounting_timeout_cancellation_leave_subsequent_healthy_outcome(case):
    store, enqueue, _, _, tasks = case
    point = enqueue["point_id"]
    cleaned = []

    async def scenario():
        async def runner(request, deadline):
            if request["attempt"] == 0 and request["task_id"] == tasks[0]:
                raise TimeoutError("fixture isolated timeout")
            if request["attempt"] == 0 and request["task_id"] == tasks[1]:
                return {"success": True, "raw": {"fixture": "subsequent healthy attempt"}}
            try:
                await asyncio.Event().wait()
            finally:
                cleaned.append(request["uid"])

        job = asyncio.create_task(swe.evaluate(store, point, runner=runner, allocation=ALLOCATION))
        try:
            while store.summary(point)["completed"] != 1:
                await asyncio.sleep(0)
        finally:
            job.cancel()
            with pytest.raises(asyncio.CancelledError):
                await job

    asyncio.run(scenario())
    summary = store.summary(point)
    counts = summary["accounting"]
    assert counts["successful"] == 1 and counts["timed_out"] == 1
    assert counts["infra_failed"] == len(cleaned) and counts["failure_events"] == len(cleaned) + 1
    assert counts["attempted"] == len(cleaned) + 2 and counts["unstarted"] == 398 - len(cleaned)
    assert counts["model_failed"] == counts["skipped"] == counts["in_progress"] == 0
    assert summary["denominator"] == 400 and summary["avg_at_n"] is None
    assert all(row["status"] == "EXITED" and "finished_at" in row for row in store.state(point)["readers"].values())
    failure_types = [swe.read_json(path)["error"]["type"] for path in summary["failure_paths"]]
    assert failure_types.count("TimeoutError") == 1 and failure_types.count("CancelledError") == len(cleaned)


def test_accounting_failure_and_reader_io_errors_are_not_suppressed(case, monkeypatch):
    store, point = _start(case)
    request = store.request(point, case[4][0], 0)
    original = swe.write_json

    def fail_evidence(path, value):
        if Path(path).parent.name == "failures" or "finished_at" in value.get("readers", {}).get("native", {}):
            raise OSError("fixture durable storage unavailable")
        return original(path, value)

    monkeypatch.setattr(swe, "write_json", fail_evidence)
    with pytest.raises(OSError, match="storage unavailable"):
        store.infra_failure(point, request, {"type": "RuntimeError", "message": "fixture native failure"})
    store.reader_enter(point, "native", {"request": request})
    with pytest.raises(OSError, match="storage unavailable"):
        store.reader_exit(point, "native", {"all_live_group_members_exited": True})
    assert store.state(point)["readers"]["native"]["status"] == "RUNNING"
    assert not list((store._point(point) / "failures").glob("*.json"))
