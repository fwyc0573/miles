"""CPU process/endpoint fixtures for the single-point worker, never native scores."""

import asyncio
import builtins
import copy
import json
import sys
from pathlib import Path

import pytest

from tests.fast import test_swe_evaluation as lifecycle
from tests.manual.agent_opd import run_swe_evaluation as worker
from tests.manual.agent_opd import swe_evaluation as swe
from tests.manual.agent_opd import swe_evaluation_config as assembly
from tests.manual.agent_opd import swe_native_evaluation as native

case = lifecycle.case
FIXTURES = Path(__file__).parent / "fixtures" / "swe_native"


@pytest.fixture
def configuration(case, tmp_path, monkeypatch):
    from miles.utils.chat_template_utils.tito_tokenizer import Qwen35TITOTokenizer, resolve_fixed_chat_template

    store, _, hf, source, tasks = case
    template, _ = resolve_fixed_chat_template("qwen35")
    manifest = tmp_path / "benchmark.json"
    dataset = tmp_path / "dataset.json"
    all_tasks = [*tasks, *[f"fixture__other-{i}" for i in range(400)]]
    swe.write_json(manifest, {"source_group": "swe", "benchmark": {"task_ids": all_tasks}})
    swe.write_json(dataset, [{"instance_id": task} for task in reversed(all_tasks)])
    payload = swe.read_json(FIXTURES / "native_config.json")
    payload["dataset"]["name_or_path"] = str(dataset)

    def native_config(runtime, *, request, dataset_index):
        result = copy.deepcopy(payload)
        result["dataset"]["range_str"] = str(dataset_index)
        result["model"]["inference_args"] = {
            "custom_upstream_url": runtime["url"] + "/v1/chat/completions",
            "seed": request["seed"],
        }
        return result

    monkeypatch.setattr(native, "native_config", native_config)
    pins_path = tmp_path / "source-pins.json"
    swe.write_json(
        pins_path,
        {
            "snapshot_path": str(tmp_path / "swe-agents"),
            "swe_commit": swe.SWE_COMMIT,
            "source_sha256": {str(template): native._sha(template)},
            "benchmark_library_sha256": native._sha(dataset),
            "benchmark_manifest": str(manifest),
            "task_ids": tasks,
            "configuration_payloads": [payload] * 4,
            "qwen_template": {"path": str(template), "sha256": native._sha(template)},
        },
    )
    policy_path, integration_path = tmp_path / "policy.json", tmp_path / "integration.json"
    swe.write_json(policy_path, lifecycle.ALLOCATION["admission"]["policy"])
    student = {"path": str(source), "mem_fraction_static": 0.7, "max_running_requests": 1, "chunked_prefill_size": 8192}
    swe.write_json(
        integration_path,
        {
            "pairs": {pair: {"student": student, "startup_timeout": 2} for pair in ("A", "B")},
            "worker_python": sys.executable,
            "image": "fixture-pinned-image",
            "repo": str(Path(__file__).resolve().parents[2]),
            "worker_local_root": str(tmp_path),
            "gpu_policy": str(policy_path),
            "creator": lifecycle.ALLOCATION_IDENTITY["creator"],
            "gpu_tag": "H200",
        },
    )
    inputs = {
        "source_pins": str(pins_path),
        "integration_config": str(integration_path),
        "protected_sources": [str(source)],
        "baseline_weight_version": "source-fixture",
        "url": "http://127.0.0.1:31000",
        "server_reader_id": "supplied-native-endpoint",
        "native_python": sys.executable,
        "python_paths": ["/fixture/step_align", "/fixture/harbor/src"],
        "dataset_path": str(dataset),
        "manifest_sha256": native._sha(manifest),
        "kill_grace_seconds": 0.5,
        "server_request_timeout": 1,
        "server_cleanup_grace_seconds": 2,
        "root": str(store.root),
        "owned_root": str(store.owned_root),
        "reference_root": str(store.reference_root),
        "server_identity": {
            "model_path": str(hf),
            "weight_version": "native-v214",
            "sglang_version": "fixture-sglang",
            "tool_call_parser": Qwen35TITOTokenizer.tool_call_parser,
            "reasoning_parser": Qwen35TITOTokenizer.reasoning_parser,
            "context_length": 131072,
            "preserve_thinking": True,
            "enable_thinking": True,
            "chat_template_sha256": native._sha(template),
        },
    }
    config = assembly.build_configuration(inputs)
    # This fixture replaces the pre-existing synthetic manifest's contract before execution.
    point = case[1]["point_id"]
    point_manifest = store.manifest(point)
    point_manifest["configuration"] = config["evaluation_contract"]
    swe.write_json(store._point(point) / "manifest.json", point_manifest)
    return config, inputs


def test_configuration_binds_ordered_100_four_seeds_and_supplied_endpoint(configuration):
    config, inputs = configuration
    assert config["runtime"]["server_identity"] == inputs["server_identity"]
    assert config["runtime"]["server_reader_id"] == "supplied-native-endpoint"
    assert len(config["task_ids"]) == 100
    assert config["task_ids"][0] == "fixture__task-0"  # NOT dataset[:100].
    for attempt, seed in enumerate(swe.SEEDS):
        assert seed == 1729 + attempt
    model = config["evaluation_contract"]["native_config"]["model"]
    assert (model["temperature"], model["top_p"], model["max_context_tokens"]) == (1.0, 0.95, 131072)
    assert "max_tokens" not in model and "top_k" not in model
    assert model["drop_thinking"] == "never"
    assert config["parser_validation"] == "CANDIDATE_PENDING_NATIVE_VERIFICATION"
    env = worker._native_environment(config)
    assert env["PYTHONPATH"].split(":") == [
        config["server"]["repo"],
        config["runtime"]["swe_source_root"] + "/src",
        config["reference_root"],
        *inputs["python_paths"],
    ]
    assert env["CUDA_VISIBLE_DEVICES"] == "" and env["PYTHONNOUSERSITE"] == "1"


@pytest.mark.parametrize(
    "field,value",
    [
        ("context_length", 8192),
        ("preserve_thinking", False),
        ("sglang_version", None),
        ("weight_version", None),
    ],
)
def test_configuration_rejects_guessed_or_changed_identity(configuration, field, value):
    _, inputs = configuration
    inputs["server_identity"][field] = value
    with pytest.raises(ValueError):
        assembly.build_configuration(inputs)


@pytest.mark.parametrize(
    "field,value",
    [
        ("tool_call_parser", "step3p5"),
        ("reasoning_parser", "deepseek-r1"),
        ("chat_template_sha256", "wrong-template"),
    ],
)
def test_gpu_worker_rejects_wrong_qwen_identity(configuration, field, value):
    config, _ = configuration
    config["runtime"]["server_identity"][field] = value
    with pytest.raises(ValueError, match="registered Qwen"):
        worker._validate_qwen_runtime(config)


def _prior_results(store, point):
    """Fixture setup: 398 already-completed slots must never be issued again."""
    results = store._point(point) / "results"
    results.mkdir()
    for task in store.manifest(point)["task_ids"]:
        for attempt in range(4):
            if task == "fixture__task-0" and attempt < 2:
                continue
            request = store.request(point, task, attempt)
            (results / f"{task}.{request['seed']}.json").write_text(
                json.dumps(
                    {
                        "request": request,
                        "success": True,
                        "raw": {"cpu_fixture": True},
                    }
                )
            )


class _EvaluationProcess:
    """In-process CPU boundary standing in for the separately isolated native child."""

    def __init__(self, coroutine):
        self.pid, self.returncode = -1, None
        self.task = asyncio.create_task(self._run(coroutine))

    async def _run(self, coroutine):
        try:
            await coroutine
            self.returncode = 0
        except BaseException:
            self.returncode = 1
            raise

    async def wait(self):
        await asyncio.shield(self.task)
        return self.returncode


@pytest.fixture
def runtime(configuration, case, monkeypatch):
    config, _ = configuration
    store, enqueue, *_ = case
    point = enqueue["point_id"]
    _prior_results(store, point)
    events, processes, issued = [], [], []
    create = asyncio.create_subprocess_exec
    stop = native._stop_child_tree
    enter, exit_reader, release = store.reader_enter, store.reader_exit, store.release
    monkeypatch.setattr(worker, "store_from_config", lambda _: store)

    def reader_enter(point, reader, evidence):
        events.append(("enter", reader))
        return enter(point, reader, evidence)

    def reader_exit(point, reader, evidence):
        events.append(("exit", reader))
        return exit_reader(point, reader, evidence)

    def release_point(point):
        events.append(("release", point))
        assert all(row["status"] == "EXITED" for row in store.state(point)["readers"].values())
        assert processes[0].returncode is not None
        assert not native._live_group_members(processes[0].pid)
        return release(point)

    monkeypatch.setattr(store, "reader_enter", reader_enter)
    monkeypatch.setattr(store, "reader_exit", reader_exit)
    monkeypatch.setattr(store, "release", release_point)

    async def runner(request, deadline):
        issued.append(request["uid"])
        return {"success": False, "raw": {"cpu_fixture": True}}

    native_runner = {"call": runner}

    async def spawn(*command, **kwargs):
        if command[2:4] == ("-m", "sglang.launch_server"):
            assert events[-1][0] == "enter"
            assert store.state(point)["readers"][events[-1][1]]["status"] == "RUNNING"
            process = await create(sys.executable, "-c", "import time; time.sleep(60)", start_new_session=True)
        else:
            events.append(("evaluate", point))
            process = _EvaluationProcess(
                swe.evaluate(store, point, runner=native_runner["call"], allocation=lifecycle.ALLOCATION)
            )
        processes.append(process)
        return process

    async def cleanup(process, grace):
        if isinstance(process, _EvaluationProcess):
            if not process.task.done():
                process.task.cancel()
            await asyncio.gather(process.task, return_exceptions=True)
            events.append(("native-cleanup", process.pid))
        else:
            await stop(process, grace)
            events.append(("server-cleanup", process.pid))

    async def ready(process, configuration, manifest, deadline):
        events.append(("load", process.pid))
        identity = configuration["runtime"]["server_identity"] | {
            "model_path": manifest["checkpoint_dir"],
            "weight_version": (
                manifest["native_update"]["weight_version"]
                if manifest["owned"]
                else configuration["runtime"]["baseline_weight_version"]
            ),
        }
        return identity, {"model_info": {"cpu_fixture": True}, "server_info": {}}

    monkeypatch.setattr(worker, "_check_port", lambda url: None)
    monkeypatch.setattr(worker.asyncio, "create_subprocess_exec", spawn)
    monkeypatch.setattr(worker, "_wait_server", ready)
    monkeypatch.setattr(native, "_stop_child_tree", cleanup)
    return config, point, store, events, processes, issued, native_runner, create, stop


def test_completed_point_stops_owned_server_before_reader_exit_release_and_excludes_foreign(runtime, case):
    config, point, store, events, processes, issued, _, create, stop = runtime

    async def run():
        foreign = await create(sys.executable, "-c", "import time; time.sleep(60)", start_new_session=True)
        try:
            result = await worker.run_point(config, point, lifecycle.ALLOCATION)
            assert foreign.returncode is None
            return result
        finally:
            await stop(foreign, 1)

    result = asyncio.run(run())
    assert result["summary"]["completed"] == 400 and result["summary"]["avg_at_n"] == 398 / 400
    assert result["release"]["status"] == "RELEASED"
    assert issued == ["fixture__task-0#attempt-0", "fixture__task-0#attempt-1"]
    server_reader = result["server_reader_id"]
    assert events.index(("enter", server_reader)) < events.index(("load", processes[0].pid))
    assert events.index(("server-cleanup", processes[0].pid)) < events.index(("exit", server_reader))
    assert events.index(("exit", server_reader)) < events.index(("release", point))
    assert case[3].is_dir() and not case[2].exists()


def test_infrastructure_missing_slot_retains_hf_and_completed_false_without_retry(runtime, case):
    config, point, store, events, processes, issued, native_runner, *_ = runtime

    async def runner(request, deadline):
        issued.append(request["uid"])
        if request["attempt"] == 1:
            raise RuntimeError("CPU infrastructure fixture")
        return {"success": False, "raw": {"cpu_fixture": True}}

    native_runner["call"] = runner
    result = asyncio.run(worker.run_point(config, point, lifecycle.ALLOCATION))
    assert result["summary"]["completed"] == 399 and result["summary"]["avg_at_n"] is None
    assert store.state(point)["status"] == "INCOMPLETE"
    assert len(issued) == 2 and len(set(issued)) == 2
    assert case[2].is_dir() and case[3].is_dir()
    assert not any(kind == "release" for kind, _ in events)
    deadline = store.state(point)["deadline_at"]
    with pytest.raises(ValueError, match="diagnose/resume"):
        asyncio.run(worker.run_point(config, point, lifecycle.ALLOCATION))
    assert store.state(point)["deadline_at"] == deadline
    assert processes[0].returncode is not None


def test_startup_failure_cleans_server_and_retains_hf(runtime, case, monkeypatch):
    config, point, store, events, processes, *_ = runtime

    async def fail(*args):
        raise ValueError("Unverified native endpoint identity")

    monkeypatch.setattr(worker, "_wait_server", fail)
    with pytest.raises(ValueError, match="identity"):
        asyncio.run(worker.run_point(config, point, lifecycle.ALLOCATION))
    assert case[2].is_dir()
    assert processes[0].returncode is not None
    assert all(row["status"] == "EXITED" for row in store.state(point)["readers"].values())
    assert not any(kind == "release" for kind, _ in events)


def test_failed_server_cleanup_preserves_reader_and_hf(runtime, case, monkeypatch):
    config, point, store, _, processes, _, _, _, stop = runtime
    cleanup = native._stop_child_tree

    async def fail(process, grace):
        if isinstance(process, _EvaluationProcess):
            return await cleanup(process, grace)
        raise RuntimeError("CPU server cleanup failure fixture")

    monkeypatch.setattr(native, "_stop_child_tree", fail)

    async def run():
        try:
            with pytest.raises(RuntimeError, match="cleanup failure"):
                await worker.run_point(config, point, lifecycle.ALLOCATION)
            assert any(row["status"] == "RUNNING" for row in store.state(point)["readers"].values())
            assert case[2].is_dir()
            assert not (store._point(point) / "release.json").exists()
            receipt = next((store._point(point) / "workers").glob("*/worker.json"))
            assert swe.read_json(receipt)["status"] == "CLEANUP_FAILED"
        finally:
            await stop(processes[0], 1)

    asyncio.run(run())


def test_wrong_task_allocation_is_rejected_before_server_reader(runtime):
    config, point, store, events, *_ = runtime
    allocation = copy.deepcopy(lifecycle.ALLOCATION)
    allocation["admission"]["policy"]["task_id"] = "foreign-task"
    with pytest.raises(ValueError, match="different task"):
        asyncio.run(worker.run_point(config, point, allocation))
    assert store.state(point)["readers"] == {} and events == []


def test_baseline_loads_original_path_and_never_deletes_source(runtime, case):
    config, point, store, *_ = runtime
    manifest = store.manifest(point)
    manifest.update(owned=False, checkpoint_dir=str(case[3]), native_update=None, files=[])
    swe.write_json(store._point(point) / "manifest.json", manifest)
    result = asyncio.run(worker.run_point(config, point, lifecycle.ALLOCATION))
    assert result["release"] == {"status": "PROTECTED_SOURCE", "deleted_bytes": 0}
    assert case[3].is_dir() and (case[3] / "weights").read_bytes() == b"original-source"
    receipt = swe.read_json(Path(result["evidence"]) / "start.json")
    command = receipt["command"]
    assert command[command.index("--model-path") + 1] == str(case[3])
    assert command[command.index("--weight-version") + 1] == "source-fixture"


def test_parent_cancellation_joins_native_cleanup_before_server_reader_exit(runtime, case):
    config, point, store, events, processes, _, native_runner, *_ = runtime
    started = asyncio.Event()
    cleaned = []

    async def hung(request, deadline):
        started.set()
        try:
            await asyncio.Future()
        finally:
            await asyncio.sleep(0.01)
            cleaned.append(request["uid"])

    native_runner["call"] = hung

    async def run():
        task = asyncio.create_task(worker.run_point(config, point, lifecycle.ALLOCATION))
        await started.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    assert cleaned
    assert events.index(("native-cleanup", -1)) < events.index(("server-cleanup", processes[0].pid))
    assert store.state(point)["status"] == "INCOMPLETE" and case[2].is_dir()
    assert all(row["status"] == "EXITED" for row in store.state(point)["readers"].values())


def test_observed_endpoint_settings_are_checked_without_trusting_config(configuration, case):
    config, _ = configuration
    store, enqueue, *_ = case
    manifest = store.manifest(enqueue["point_id"])
    identity = config["runtime"]["server_identity"]
    args = {
        "model_path": manifest["checkpoint_dir"],
        "tokenizer_path": manifest["checkpoint_dir"],
        "tp_size": 2,
        "dtype": "bfloat16",
        "context_length": 131072,
        "tool_call_parser": identity["tool_call_parser"],
        "reasoning_parser": identity["reasoning_parser"],
        "chat_template": config["server"]["chat_template"],
        "default_chat_template_kwargs": {"preserve_thinking": True, "enable_thinking": True},
    }
    model = {
        "model_path": manifest["checkpoint_dir"],
        "tokenizer_path": manifest["checkpoint_dir"],
        "weight_version": "native-v214",
        "served_model_name": config["runtime"]["model_name"],
        "architectures": ["Qwen3_5ForCausalLM"],
        "tool_call_parser": identity["tool_call_parser"],
        "reasoning_parser": identity["reasoning_parser"],
    }
    info = {"server_args": args, "version": identity["sglang_version"]}
    assert worker._check_identity(config, manifest, model, info) == identity
    model["model_path"] = "/foreign/model"
    with pytest.raises(ValueError, match="path"):
        worker._check_identity(config, manifest, model, info)


def test_native_role_constructs_reviewed_runner_and_uses_real_store(runtime, monkeypatch):
    config, point, store, *_ = runtime
    reader_id = config["runtime"]["server_reader_id"]
    store.reader_enter(point, reader_id, {"cpu_fixture": True})
    issued = []

    async def native_model_fixture(self, request, deadline_at):
        assert isinstance(self, native.NativeSweRunner)
        issued.append(request["uid"])
        return {"success": False, "raw": {"cpu_fixture": True}}

    # The actual reviewed constructor still checks pins, tasks, harness, path,
    # version, parsers and the live server reader; only model/ACS execution is fake.
    monkeypatch.setattr(native.NativeSweRunner, "__call__", native_model_fixture)
    result = asyncio.run(worker._native_run(config | {"allocation": lifecycle.ALLOCATION}, point))
    assert result["completed"] == 400 and len(issued) == 2
    assert store.state(point)["readers"][reader_id]["status"] == "RUNNING"
    assert not (store._point(point) / "release.json").exists()


def test_native_configuration_and_constructor_do_not_import_gpu_chat_modules(configuration, case, monkeypatch):
    _, inputs = configuration
    import_module = builtins.__import__

    def cpu_import(name, *args, **kwargs):
        if name.startswith(("sglang", "miles.utils.chat_template_utils")):
            raise AssertionError("Native construction must not import GPU chat/template dependencies")
        return import_module(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", cpu_import)
    config = assembly.build_configuration(inputs)
    store, enqueue, *_ = case
    store.reader_enter(enqueue["point_id"], config["runtime"]["server_reader_id"], {"cpu_fixture": True})
    assert native.NativeSweRunner(store, enqueue["point_id"], config["runtime"])


@pytest.fixture
def qualification(configuration, case, tmp_path):
    config, _ = configuration
    config = copy.deepcopy(config)
    config["root"] = str(tmp_path / "qualification-evaluations")
    config["runtime"]["server_identity"].update(
        model_path=str(case[3]),
        weight_version=config["runtime"]["baseline_weight_version"],
    )
    store = swe.store_from_config(config)
    point = "qualification.original4b.fixture"
    store.enqueue_baseline(
        point_id=point,
        source=case[3],
        task_ids=config["task_ids"],
        configuration=config["evaluation_contract"],
    )
    return config, point, store


@pytest.mark.parametrize(
    "selection",
    [
        None,
        [],
        ["foreign__task#attempt-0"],
        ["fixture__task-0#attempt-4"],
        ["fixture__task-0#attempt-00"],
        ["fixture__task-0#attempt-0", "fixture__task-0#attempt-0"],
    ],
)
def test_qualification_rejects_ambiguous_or_foreign_selection_before_start(qualification, selection):
    _, point, store = qualification
    with pytest.raises(ValueError, match="Qualification"):
        worker._qualification_requests(store, point, selection)
    assert store.state(point)["readers"] == {} and store.state(point)["first_started_at"] is None


def test_qualification_rejects_formal_store_or_point_and_completion(qualification, configuration, case):
    _, point, store = qualification
    uid = "fixture__task-0#attempt-0"
    with pytest.raises(ValueError, match="separate"):
        worker._qualification_requests(case[0], case[1]["point_id"], [uid])
    with pytest.raises(ValueError, match="separate"):
        worker._qualification_requests(store, "formal-point", [uid])
    all_slots = [f"{task}#attempt-{attempt}" for task in configuration[0]["task_ids"] for attempt in range(4)]
    with pytest.raises(ValueError, match="leave unexecuted slots missing"):
        worker._qualification_requests(store, point, all_slots)


@pytest.fixture
def qualification_runtime(qualification, monkeypatch):
    config, point, store = qualification
    create, stop = asyncio.create_subprocess_exec, native._stop_child_tree
    events, servers, children, issued = [], [], [], []
    settings = {"hung": False, "infrastructure_failure": False}
    monkeypatch.setattr(worker, "store_from_config", lambda _: store)
    monkeypatch.setattr(worker, "_check_port", lambda url: None)
    monkeypatch.setattr(store, "release", lambda _: pytest.fail("Qualification must never invoke HF release"))

    async def native_model_fixture(self, request, deadline):
        assert isinstance(self, native.NativeSweRunner)
        issued.append(request["uid"])
        child = await create(
            sys.executable,
            "-c",
            "import time; time.sleep(60)" if settings["hung"] else "pass",
            start_new_session=True,
        )
        children.append(child)
        reader = "cpu-native-child-" + str(child.pid)
        store.reader_enter(point, reader, {"pid": child.pid, "cpu_fixture": True, "run_kind": "qualification"})
        try:
            await child.wait()
        finally:
            await stop(child, 1)
            events.append(("child-cleanup", child.pid))
            store.reader_exit(point, reader, {"all_live_group_members_exited": True, "cpu_fixture": True})
        if settings["infrastructure_failure"]:
            raise RuntimeError("CPU qualification infrastructure failure")
        return {"success": False, "raw": {"cpu_fixture": True}}

    monkeypatch.setattr(native.NativeSweRunner, "__call__", native_model_fixture)

    async def spawn(*command, **kwargs):
        if command[2:4] == ("-m", "sglang.launch_server"):
            server_readers = [
                reader
                for reader, row in store.state(point)["readers"].items()
                if reader.startswith("server-") and row["status"] == "RUNNING"
            ]
            assert len(server_readers) == 1
            server_reader = server_readers[0]
            events.append(("server-start", server_reader))
            process = await create(sys.executable, "-c", "import time; time.sleep(60)", start_new_session=True)
            servers.append(process)
            return process
        child_config = swe.read_json(command[command.index("--configuration") + 1])
        selected = [command[i + 1] for i, arg in enumerate(command) if arg == "--qualification-attempt"]
        return _EvaluationProcess(worker._native_run(child_config, point, qualification_attempts=selected))

    async def cleanup(process, grace):
        if isinstance(process, _EvaluationProcess):
            if not process.task.done():
                process.task.cancel()
            await asyncio.gather(process.task, return_exceptions=True)
            events.append(("native-cleanup", -1))
        else:
            await stop(process, grace)
            events.append(("server-cleanup", process.pid))

    async def ready(process, configuration, manifest, deadline):
        events.append(("load", process.pid))
        return configuration["runtime"]["server_identity"], {"model_info": {"cpu_fixture": True}, "server_info": {}}

    monkeypatch.setattr(worker.asyncio, "create_subprocess_exec", spawn)
    monkeypatch.setattr(worker, "_wait_server", ready)
    monkeypatch.setattr(native, "_stop_child_tree", cleanup)
    return config, point, store, events, servers, children, issued, settings


def test_qualification_runs_only_explicit_slots_leaves_398_missing_and_never_releases(qualification_runtime):
    config, point, store, events, servers, children, issued, _ = qualification_runtime
    selected = ["fixture__task-0#attempt-0", "fixture__task-1#attempt-3"]
    before = (store._point(point) / "manifest.json").read_bytes()
    result = asyncio.run(worker.run_point(config, point, lifecycle.ALLOCATION, qualification_attempts=selected))
    assert result["run_kind"] == "qualification" and result["status"] == "INCOMPLETE"
    assert result["summary"]["completed"] == 2 and result["summary"]["avg_at_n"] is None
    assert len(result["summary"]["missing_attempt_ids"]) == 398
    assert issued == selected and "release" not in result
    assert (store._point(point) / "manifest.json").read_bytes() == before
    assert store.manifest(point)["seeds"] == list(swe.SEEDS)
    assert all(
        child.returncode is not None and not native._live_group_members(child.pid) for child in [*servers, *children]
    )
    assert all(reader["status"] == "EXITED" for reader in store.state(point)["readers"].values())
    assert events.index(("native-cleanup", -1)) < events.index(("server-cleanup", servers[0].pid))
    for name in ("start", "server", "cleanup", "worker"):
        assert swe.read_json(Path(result["evidence"]) / (name + ".json"))["run_kind"] == "qualification"
    receipt = next((store._point(point) / "qualification_runs").glob("*.json"))
    assert swe.read_json(receipt)["executed_attempt_ids"] == selected
    assert not (store._point(point) / "release.json").exists()


def test_qualification_preserves_deadline_and_completed_slots_after_explicit_diagnosed_resume(qualification_runtime):
    config, point, store, _, _, _, issued, _ = qualification_runtime
    selected = ["fixture__task-0#attempt-0"]
    asyncio.run(worker.run_point(config, point, lifecycle.ALLOCATION, qualification_attempts=selected))
    deadline = store.state(point)["deadline_at"]
    result_path = next((store._point(point) / "results").glob("*.json"))
    before = result_path.read_bytes()
    with pytest.raises(ValueError, match="diagnose/resume"):
        asyncio.run(worker.run_point(config, point, lifecycle.ALLOCATION, qualification_attempts=selected))
    store.resume(point, diagnosis="CPU explicit qualification continuation", remedy="CPU fixture inspected")
    result = asyncio.run(
        worker.run_point(
            config,
            point,
            lifecycle.ALLOCATION,
            qualification_attempts=[*selected, "fixture__task-0#attempt-1"],
        )
    )
    assert issued == [*selected, "fixture__task-0#attempt-1"]
    assert store.state(point)["deadline_at"] == deadline and result_path.read_bytes() == before
    assert result["summary"]["avg_at_n"] is None and len(result["summary"]["missing_attempt_ids"]) == 398


def test_qualification_infrastructure_failure_is_missing_without_retry(qualification_runtime):
    config, point, _, _, _, _, issued, settings = qualification_runtime
    settings["infrastructure_failure"] = True
    selected = ["fixture__task-0#attempt-0"]
    result = asyncio.run(worker.run_point(config, point, lifecycle.ALLOCATION, qualification_attempts=selected))
    assert issued == selected and result["summary"]["completed"] == 0
    assert result["summary"]["avg_at_n"] is None and len(result["summary"]["missing_attempt_ids"]) == 400


def test_qualification_cancellation_joins_owned_children_and_server(qualification_runtime):
    config, point, store, _, servers, children, _, settings = qualification_runtime
    settings["hung"] = True

    async def run():
        task = asyncio.create_task(
            worker.run_point(
                config,
                point,
                lifecycle.ALLOCATION,
                qualification_attempts=["fixture__task-0#attempt-0"],
            )
        )
        while not children:
            await asyncio.sleep(0.01)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task

    asyncio.run(run())
    assert all(
        child.returncode is not None and not native._live_group_members(child.pid) for child in [*servers, *children]
    )
    assert all(reader["status"] == "EXITED" for reader in store.state(point)["readers"].values())
    assert store.state(point)["status"] == "INCOMPLETE" and store.summary(point)["avg_at_n"] is None
    assert not (store._point(point) / "release.json").exists()


def test_launch_preserves_gpu_registry_rejection_after_native_config_acceptance(qualification, monkeypatch):
    config, _, store = qualification
    config["runtime"]["server_identity"]["tool_call_parser"] = "step3p5"
    config["evaluation_contract"] = native.evaluation_contract(config["runtime"])
    point = "qualification.wrong-parser.fixture"
    store.enqueue_baseline(
        point_id=point,
        source=config["original_source"],
        task_ids=config["task_ids"],
        configuration=config["evaluation_contract"],
    )
    monkeypatch.setattr(worker, "store_from_config", lambda _: store)
    with pytest.raises(ValueError, match="registered Qwen"):
        asyncio.run(
            worker.run_point(
                config,
                point,
                lifecycle.ALLOCATION,
                qualification_attempts=["fixture__task-0#attempt-0"],
            )
        )
    assert store.state(point)["readers"] == {} and store.state(point)["first_started_at"] is None
