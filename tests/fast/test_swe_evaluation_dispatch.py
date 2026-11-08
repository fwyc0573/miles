"""Real local process handoff to a CPU receipt stub; never native GPU/scorer PASS."""

import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from tests.manual.agent_opd import check_swe_native_async as native_check
from tests.manual.agent_opd import submit_swe_opd
from tests.manual.agent_opd import watch_swe_evaluations as watch
from tests.manual.agent_opd.swe_evaluation import read_json, write_json

REAL_POPEN = subprocess.Popen
ROOT = Path(__file__).resolve().parents[2]
NATIVE_PUBLIC_MOUNT = "juicefs+s3://oss.i.shaipower.com/tenant:/mnt/shared-storage/tenant"

STUB = """
import argparse, json, os, sys, time
from pathlib import Path
parser = argparse.ArgumentParser()
for field in ("config", "configuration", "point", "receipt"):
    parser.add_argument("--" + field, required=True)
parser.add_argument("--qualification-attempt", action="append")
args = parser.parse_args()
evaluation = json.loads(Path(args.configuration).read_text())
fixture = evaluation["fixture"]
events = Path(fixture["events"])
events.mkdir(parents=True, exist_ok=True)
(events / (args.point + ".started.json")).write_text(json.dumps({"pid": os.getpid(), "argv": sys.argv[1:]}))
mode = fixture["modes"].get(args.point, "admitted")
receipt = Path(args.receipt)
receipt.parent.mkdir(parents=True, exist_ok=True)
pending = receipt.with_name(receipt.name + ".pending")
if mode == "missing":
    sys.exit(2)
if mode == "pending":
    pending.write_text("{")
    sys.exit(2)
denied = mode == "denied" or (mode == "admission" and Path(fixture["deny_until"]).exists())
row = {"point": args.point, "configuration": args.configuration, "config": args.config,
       "job_id": None if denied else "cpu-fixture-eval-" + args.point,
       "admission": {"submitted": not denied, "admitted": not denied}}
if mode == "bad-receipt":
    row["point"] = "another-point"
with pending.open("x") as stream:
    json.dump(row, stream)
os.link(pending, receipt)
pending.unlink()
if denied:
    sys.exit(2)
while Path(fixture["hold"]).exists():
    time.sleep(0.01)
(events / (args.point + ".exited.json")).write_text(json.dumps({"exit_code": 1 if mode == "failed" else 0}))
sys.exit(1 if mode == "failed" else 0)
"""


@pytest.fixture
def inputs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("KUBEBRAIN_RJOB_NAME", raising=False)
    configuration, config_path = tmp_path / "evaluation.json", tmp_path / "integration.json"
    evaluation = {
        "owned_root": str(tmp_path / "owned"),
        "evaluation_contract": {"fixture": "no-scorer"},
        "dispatch": {"local_mount": str(tmp_path), "directory": str(tmp_path / "dispatch"), "poll_seconds": 0.02},
        "fixture": {
            "events": str(tmp_path / "events"),
            "hold": str(tmp_path / "hold"),
            "deny_until": str(tmp_path / "deny"),
            "modes": {},
        },
    }
    config = {
        "local_mount": str(tmp_path),
        "checkpoint": {"hook_args": {"swe_evaluation_configuration": str(configuration)}},
    }
    write_json(configuration, evaluation)
    write_json(config_path, config)
    stub = tmp_path / "cpu_evaluator.py"
    stub.write_text(STUB)
    real_popen, calls = watch.subprocess.Popen, []

    def popen(argv, **kwargs):
        assert argv[:5] == [sys.executable, "-u", "-B", "-m", "tests.manual.agent_opd.submit_swe_evaluation"]
        assert kwargs["cwd"] == tmp_path
        calls.append(argv)
        return real_popen([sys.executable, "-u", str(stub), *argv[5:]], **kwargs)

    monkeypatch.setattr(watch.subprocess, "Popen", popen)
    return SimpleNamespace(
        root=tmp_path,
        config=config,
        config_path=config_path,
        evaluation=evaluation,
        configuration=configuration,
        job="training-actual-job",
        calls=calls,
        hold=tmp_path / "hold",
        deny=tmp_path / "deny",
    )


def _point(inputs, update=50, *, job=None):
    return f"A-full.{inputs.job if job is None else job}.HF{update}"


def _ready(inputs, update=50, *, job=None):
    job = inputs.job if job is None else job
    return watch.notify_ready(
        inputs.configuration,
        inputs.evaluation,
        job_id=job,
        point_id=_point(inputs, update, job=job),
        checkpoint_dir=Path(inputs.evaluation["owned_root"]) / job / "hf" / f"step_{update - 1}",
    )


def _wait(predicate):
    deadline = time.monotonic() + 5
    while not predicate():
        if time.monotonic() >= deadline:
            raise AssertionError("CPU process handoff did not reach the expected state")
        time.sleep(0.01)


def _running(inputs):
    watcher = watch.EvaluationWatcher(inputs.config_path, inputs.configuration, inputs.job)
    finished, result, errors = threading.Event(), [], []

    def run():
        try:
            result.append(watcher.run(finished.is_set))
        except Exception as error:
            errors.append(error)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return watcher, finished, thread, result, errors


def _close(inputs, running):
    inputs.hold.unlink(missing_ok=True)
    running[1].set()
    running[2].join(5)
    assert not running[2].is_alive() and not running[4]


def test_real_process_handoff_and_completed_training_drains_live_evaluator(inputs):
    inputs.hold.touch()
    ready = _ready(inputs)
    running = _running(inputs)
    watcher, finished, thread, result, _ = running
    try:
        _wait(lambda: watcher.rows.get(_point(inputs), {}).get("status") == "ADMITTED")
        assert len(inputs.calls) == 1 and ready.exists()
        argv = inputs.calls[0]
        assert argv[argv.index("--configuration") + 1] == str(watcher.configuration)
        assert read_json(watcher.configuration) == inputs.evaluation
        assert read_json(watcher.config_path) == inputs.config
        finished.set()
        time.sleep(0.06)
        assert thread.is_alive() and watcher.children
    finally:
        _close(inputs, running)
    assert result == [0] and len(inputs.calls) == 1
    assert watcher.rows[_point(inputs)]["status"] == "EVALUATOR_EXITED"
    assert read_json(watcher.directory / "observer.json")["training_terminal_observed"] is True


def test_unrelated_job_notifications_are_ignored_and_same_job_has_one_watcher(inputs):
    inputs.hold.touch()
    _ready(inputs, job="another-training-job")
    ready = _ready(inputs)
    unrelated = read_json(ready)
    unrelated.update(job_id="another-training-job", point_id="unrelated")
    write_json(ready.parent / "unrelated.json", unrelated)
    running = _running(inputs)
    try:
        _wait(lambda: len(running[0].children) == 1)
        second = watch.EvaluationWatcher(inputs.config_path, inputs.configuration, inputs.job)
        with pytest.raises(BlockingIOError):
            second.run(lambda: True)
        time.sleep(0.05)
        assert len(inputs.calls) == 1
    finally:
        _close(inputs, running)


def test_proven_denial_is_queued_not_launched_and_rechecks_fresh_admission(inputs):
    inputs.deny.touch()
    inputs.evaluation["fixture"]["modes"][_point(inputs)] = "admission"
    write_json(inputs.configuration, inputs.evaluation)
    _ready(inputs)
    running = _running(inputs)
    try:
        _wait(lambda: len(inputs.calls) >= 2)
        assert not any(row.get("evaluation_job_id") for row in running[0].rows.values())
        receipts = list((running[0].directory / "receipts").glob("*.json"))
        assert receipts and all(read_json(path)["admission"]["submitted"] is False for path in receipts)
        inputs.deny.unlink()
        _wait(lambda: running[0].rows[_point(inputs)]["status"] == "EVALUATOR_EXITED")
        checks = len(inputs.calls)
        time.sleep(0.06)
        assert len(inputs.calls) == checks
    finally:
        _close(inputs, running)
    assert running[3] == [0]


def test_denial_after_actual_training_terminal_is_retained_without_infinite_wait(inputs):
    inputs.evaluation["fixture"]["modes"][_point(inputs)] = "denied"
    write_json(inputs.configuration, inputs.evaluation)
    ready = _ready(inputs)
    watcher = watch.EvaluationWatcher(inputs.config_path, inputs.configuration, inputs.job)
    assert watcher.run(lambda: True) == 2
    assert watcher.rows[_point(inputs)]["status"] == "ADMISSION_DENIED" and ready.exists()
    assert len(inputs.calls) == 1


def test_explicit_observer_restart_rechecks_only_proven_denied_submission(inputs):
    inputs.deny.touch()
    inputs.evaluation["fixture"]["modes"][_point(inputs)] = "admission"
    write_json(inputs.configuration, inputs.evaluation)
    _ready(inputs)
    first = watch.EvaluationWatcher(inputs.config_path, inputs.configuration, inputs.job)
    assert first.run(lambda: True) == 2 and len(inputs.calls) == 1
    inputs.deny.unlink()
    second = watch.EvaluationWatcher(inputs.config_path, inputs.configuration, inputs.job)
    assert second.run(lambda: True) == 0 and len(inputs.calls) == 2
    assert second.rows[_point(inputs)]["admission_check"] == 2


@pytest.mark.parametrize("mode", ["pending", "missing", "failed"])
def test_unknown_or_exited_evaluator_is_never_automatically_resubmitted(inputs, mode):
    inputs.evaluation["fixture"]["modes"][_point(inputs)] = mode
    write_json(inputs.configuration, inputs.evaluation)
    _ready(inputs)
    running = _running(inputs)
    try:
        expected = "EVALUATOR_EXITED" if mode == "failed" else "UNVERIFIED"
        _wait(lambda: running[0].rows.get(_point(inputs), {}).get("status") == expected)
        time.sleep(0.07)
        assert len(inputs.calls) == 1
    finally:
        _close(inputs, running)
    restarted = watch.EvaluationWatcher(inputs.config_path, inputs.configuration, inputs.job)
    restarted.run(lambda: True)
    assert len(inputs.calls) == 1


def test_observation_failure_preserves_child_handle_and_other_points_continue(inputs):
    inputs.hold.touch()
    inputs.evaluation["fixture"]["modes"][_point(inputs)] = "bad-receipt"
    write_json(inputs.configuration, inputs.evaluation)
    _ready(inputs)
    _ready(inputs, 100)
    running = _running(inputs)
    try:
        _wait(lambda: len(running[0].children) == 2)
        _wait(lambda: running[0].rows[_point(inputs, 100)]["status"] == "ADMITTED")
        _wait(lambda: running[0].rows[_point(inputs)]["status"] == "UNVERIFIED")
        assert running[0].rows[_point(inputs)]["status"] == "UNVERIFIED"
        running[1].set()
        time.sleep(0.05)
        assert running[2].is_alive() and len(running[0].children) == 2
    finally:
        _close(inputs, running)
    assert running[3] == [1] and len(inputs.calls) == 2


def test_local_journal_failure_does_not_launch_uncertain_point_or_block_other_point(inputs, monkeypatch):
    _ready(inputs)
    _ready(inputs, 100)
    original = watch.write_json

    def fail(path, row):
        path = Path(path)
        if path.parent.name == "dispatch" and path.name == f"{_point(inputs)}.json":
            raise OSError("CPU fixture local journal failure")
        return original(path, row)

    monkeypatch.setattr(watch, "write_json", fail)
    watcher = watch.EvaluationWatcher(inputs.config_path, inputs.configuration, inputs.job)
    assert watcher.run(lambda: True) == 1 and len(inputs.calls) == 1
    assert inputs.calls[0][inputs.calls[0].index("--point") + 1] == _point(inputs, 100)
    assert read_json(watcher.directory / "observer.json")["unverified_paths"]


def test_frozen_evaluation_and_local_notification_paths_are_enforced(inputs):
    ready = _ready(inputs)
    watcher = watch.EvaluationWatcher(inputs.config_path, inputs.configuration, inputs.job)
    assert set(read_json(ready)) == {"point_id", "job_id", "checkpoint_dir", "configuration"}
    changed = {**inputs.evaluation, "evaluation_contract": {"changed": True}}
    with pytest.raises(ValueError, match="Frozen"):
        watch.notify_ready(
            inputs.configuration,
            changed,
            job_id=inputs.job,
            point_id=_point(inputs),
            checkpoint_dir=Path(inputs.evaluation["owned_root"]) / inputs.job / "hf" / "step_49",
        )
    assert read_json(watcher.configuration) == inputs.evaluation
    outside = {
        **inputs.evaluation,
        "dispatch": {**inputs.evaluation["dispatch"], "directory": "/mnt/codesign-exp/another-user"},
    }
    with pytest.raises(ValueError, match="local"):
        watch._dispatch_scope(inputs.configuration, outside, inputs.job)
    alias = inputs.root / "escape"
    alias.symlink_to("/mnt/codesign-exp/another-user")
    outside["dispatch"]["directory"] = str(alias)
    with pytest.raises(ValueError, match="resolve under"):
        watch._dispatch_scope(inputs.configuration, outside, inputs.job)


def test_restart_with_prior_handoff_or_pending_is_unverified_not_safe_retry(inputs):
    _ready(inputs)
    watcher = watch.EvaluationWatcher(inputs.config_path, inputs.configuration, inputs.job)
    write_json(
        watcher.directory / "dispatch" / f"{_point(inputs)}.json", {"point_id": _point(inputs), "status": "STARTING"}
    )
    assert watcher.run(lambda: True) == 1
    assert not inputs.calls


def test_standalone_completion_requires_an_actual_matching_terminal_receipt(inputs):
    terminal = inputs.root / "trainer.terminal.json"
    assert watch._terminal_receipt(terminal, inputs.job) is False
    write_json(terminal, {"job": inputs.job, "status": {"phase": "Running"}})
    with pytest.raises(ValueError, match="terminated"):
        watch._terminal_receipt(terminal, inputs.job)
    write_json(terminal, {"job": "another-job", "status": {"phase": "Succeeded"}})
    with pytest.raises(ValueError, match="actual"):
        watch._terminal_receipt(terminal, inputs.job)
    write_json(terminal, {"job": inputs.job, "status": {"phase": "Succeeded"}})
    assert watch._terminal_receipt(terminal, inputs.job) is True


def test_standalone_cli_uses_same_dispatch_and_actual_terminal_receipt(inputs, monkeypatch):
    inputs.evaluation["fixture"]["modes"][_point(inputs)] = "denied"
    write_json(inputs.configuration, inputs.evaluation)
    _ready(inputs)
    receipt = inputs.root / "trainer.json"
    write_json(receipt.with_suffix(".terminal.json"), {"job": inputs.job, "status": {"phase": "Succeeded"}})
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "watch_swe_evaluations",
            "--config",
            str(inputs.config_path),
            "--configuration",
            str(inputs.configuration),
            "--job",
            inputs.job,
            "--trainer-receipt",
            str(receipt),
        ],
    )
    assert watch.main() == 2 and len(inputs.calls) == 1


def test_worker_dispatch_and_cross_job_symlinks_are_rejected(inputs, monkeypatch):
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", inputs.job)
    with pytest.raises(ValueError, match="never on an RJob"):
        watch.EvaluationWatcher(inputs.config_path, inputs.configuration, inputs.job)
    monkeypatch.delenv("KUBEBRAIN_RJOB_NAME")
    directory = Path(inputs.evaluation["dispatch"]["directory"])
    other = directory / "other-job"
    other.mkdir(parents=True)
    (directory / inputs.job).symlink_to(other)
    with pytest.raises(ValueError, match="another job"):
        _ready(inputs)
    assert not inputs.calls


def _local_training(inputs, monkeypatch, release):
    monkeypatch.setenv("STEPMIND_BACKEND", "rjob")
    monkeypatch.setenv("BRAINPP_ACCESS_KEY", "cpu-fixture-access")
    monkeypatch.setenv("BRAINPP_SECRET_KEY", "cpu-fixture-secret")
    inputs.config.update(
        admission_lock=str(inputs.root / "admission.lock"),
        gpu_policy=str(inputs.root / "policy.json"),
        api_timeout_seconds=1,
        creator="fixture-user",
        gpu_tag="H200",
        phase="fixture",
        image="cpu-fixture-image",
        mounts=[],
        charged_group="fixture-group",
    )
    write_json(inputs.config_path, inputs.config)
    write_json(inputs.config["gpu_policy"], {"task_annotation": "fixture", "task_id": "fixture-task"})
    monkeypatch.setattr(submit_swe_opd, "_validate_paths", lambda *args: None)
    monkeypatch.setattr(
        submit_swe_opd, "_task_specs", lambda *args: {"student": {"gpu": 1, "replica": 1, "is_critical": True}}
    )
    monkeypatch.setattr(submit_swe_opd, "_worker_command", lambda *args, **kwargs: "cpu-fixture-training")
    monkeypatch.setattr(submit_swe_opd.socket, "gethostbyname", lambda *args: "192.0.2.1")
    monkeypatch.setattr(
        submit_swe_opd, "policy_admission_snapshot", lambda *args, **kwargs: {"admitted": True, "preemptible": False}
    )
    client = SimpleNamespace(
        group="fixture",
        version="v1",
        namespace="fixture",
        plural="fixture",
        api=SimpleNamespace(
            get_namespaced_custom_object=lambda **kwargs: {
                "metadata": {"name": inputs.job, "uid": "cpu-fixture-uid"},
                "status": {"phase": "Succeeded"},
            }
        ),
    )
    workers = SimpleNamespace(
        rjob=SimpleNamespace(meta=SimpleNamespace(name=inputs.job)), wait=lambda: release.wait(5), resources=[]
    )

    class ResourceConfig(SimpleNamespace):
        def __iter__(self):
            # Replay the native ResourceConfig iterator's list mutation, without platform dependencies.
            if NATIVE_PUBLIC_MOUNT not in self.mounts:
                self.mounts.append(NATIVE_PUBLIC_MOUNT)
            for task in self.task_specs:
                yield task, self

    def submit(resource, **kwargs):
        list(iter(resource))
        workers.resources.append(resource)
        return workers

    for name in (
        "steptron",
        "steptron.exp",
        "steptron.utils",
        "steptron.exp.base_exp",
        "steptron.utils.stepmind",
        "steptron.utils.stepmind_control",
    ):
        monkeypatch.setitem(sys.modules, name, ModuleType(name))
    sys.modules["steptron.exp.base_exp"].ResourceConfig = ResourceConfig
    sys.modules["steptron.utils.stepmind"].get_rjob_client = lambda: client
    sys.modules["steptron.utils.stepmind_control"].RJobBackend = lambda: SimpleNamespace(submit=submit)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "submit_swe_opd",
            "--config",
            str(inputs.config_path),
            "--pair",
            "A",
            "--protocol",
            "full",
            "--receipt",
            str(inputs.root / "trainer.json"),
        ],
    )
    return client, workers


def test_actual_local_training_entrypoint_dispatches_before_wait_and_drains_after_wait(inputs, monkeypatch):
    inputs.hold.touch()
    _ready(inputs)
    release, result = threading.Event(), []
    _local_training(inputs, monkeypatch, release)
    thread = threading.Thread(target=lambda: result.append(submit_swe_opd.main()), daemon=True)
    thread.start()
    try:
        _wait(lambda: (inputs.root / "events" / f"{_point(inputs)}.started.json").exists())
        assert thread.is_alive() and not (inputs.root / "trainer.terminal.json").exists()
        release.set()
        _wait(lambda: (inputs.root / "trainer.terminal.json").exists())
        assert thread.is_alive(), "Only completed training may wait for evaluation drain"
    finally:
        inputs.hold.unlink(missing_ok=True)
        release.set()
        thread.join(5)
    assert result == [0] and len(inputs.calls) == 1 and not thread.is_alive()


@pytest.mark.parametrize("mounts", [[], [NATIVE_PUBLIC_MOUNT]])
def test_training_resource_owns_mounts_without_changing_dispatch_config(inputs, monkeypatch, mounts):
    release = threading.Event()
    release.set()
    _, workers = _local_training(inputs, monkeypatch, release)
    inputs.config["mounts"] = mounts
    write_json(inputs.config_path, inputs.config)
    before = inputs.config_path.read_bytes()
    starts, waits = [], []
    start, wait = submit_swe_opd.start_dispatch, workers.wait

    def observe(path, config, job):
        observer = start(path, config, job)
        starts.append((config, observer))
        return observer

    def wait_once():
        waits.append(True)
        return wait()

    monkeypatch.setattr(submit_swe_opd, "start_dispatch", observe)
    workers.wait = wait_once
    assert submit_swe_opd.main() == 0
    assert len(starts) == len(waits) == len(workers.resources) == 1
    config, observer = starts[0]
    resource = workers.resources[0]
    assert observer is not None and observer.training_finished.is_set() and not observer.thread.is_alive()
    assert resource.mounts is not config["mounts"]
    assert resource.mounts == [NATIVE_PUBLIC_MOUNT] and config["mounts"] == mounts
    assert all(resource.mounts[index] is mount for index, mount in enumerate(config["mounts"]))
    assert inputs.config_path.read_bytes() == before
    assert read_json(inputs.config_path) == config
    assert read_json(inputs.root / "trainer.terminal.json")["native_execution_succeeded"] is True


def test_real_file_drift_rejects_observer_without_failing_healthy_training(inputs, monkeypatch, caplog):
    release = threading.Event()
    release.set()
    _, workers = _local_training(inputs, monkeypatch, release)
    backend = sys.modules["steptron.utils.stepmind_control"].RJobBackend()
    starts, waits = [], []
    start, wait = submit_swe_opd.start_dispatch, workers.wait

    def submit(resource, **kwargs):
        result = backend.submit(resource, **kwargs)
        config = read_json(inputs.config_path)
        config["phase"] = "cpu-fixture-changed-after-submission"
        write_json(inputs.config_path, config)
        return result

    def observe(*args):
        observer = start(*args)
        starts.append(observer)
        return observer

    def wait_once():
        waits.append(True)
        return wait()

    monkeypatch.setattr(
        sys.modules["steptron.utils.stepmind_control"], "RJobBackend", lambda: SimpleNamespace(submit=submit)
    )
    monkeypatch.setattr(submit_swe_opd, "start_dispatch", observe)
    workers.wait = wait_once
    assert submit_swe_opd.main() == 0
    assert starts == [None] and waits == [True] and not inputs.calls
    assert read_json(inputs.config_path)["phase"] == "cpu-fixture-changed-after-submission"
    assert "Training integration configuration changed after submission" in caplog.text
    assert read_json(inputs.root / "trainer.terminal.json")["native_execution_succeeded"] is True


def test_observer_start_failure_does_not_fail_healthy_local_training(inputs, monkeypatch):
    release = threading.Event()
    release.set()
    _local_training(inputs, monkeypatch, release)
    monkeypatch.setattr(
        watch, "EvaluationWatcher", lambda *args: (_ for _ in ()).throw(ValueError("CPU observer fixture failure"))
    )
    assert submit_swe_opd.main() == 0 and not inputs.calls


@pytest.mark.parametrize("terminal_available", [True, False])
def test_native_wait_failure_drains_observer_and_preserves_original_exception(inputs, monkeypatch, terminal_available):
    inputs.hold.touch()
    _ready(inputs)
    release = threading.Event()
    client, workers = _local_training(inputs, monkeypatch, release)
    failure = RuntimeError("CPU native wait observed terminal Failed capacity failure")
    queried = threading.Event()

    def wait():
        assert release.wait(5)
        raise failure

    def terminal(**kwargs):
        queried.set()
        if not terminal_available:
            raise OSError("CPU terminal evidence query unavailable")
        return {"metadata": {"name": inputs.job, "uid": "cpu-fixture-uid"}, "status": {"phase": "Failed"}}

    workers.wait = wait
    client.api.get_namespaced_custom_object = terminal
    observers, errors = [], []
    start = submit_swe_opd.start_dispatch

    def observe(*args):
        observer = start(*args)
        observers.append(observer)
        return observer

    monkeypatch.setattr(submit_swe_opd, "start_dispatch", observe)

    def run():
        try:
            submit_swe_opd.main()
        except Exception as error:
            errors.append(error)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    try:
        _wait(lambda: (inputs.root / "events" / f"{_point(inputs)}.started.json").exists())
        release.set()
        _wait(lambda: bool(errors) or (observers and observers[0].training_finished.is_set()))
        assert thread.is_alive() and not errors, "Native failure must wait for the already-started evaluator to drain"
        assert queried.is_set()
        receipt = inputs.root / "trainer.terminal.json"
        if terminal_available:
            assert read_json(receipt)["status"]["phase"] == "Failed"
            assert read_json(receipt)["native_execution_succeeded"] is False
        else:
            assert not receipt.exists()
    finally:
        inputs.hold.unlink(missing_ok=True)
        release.set()
        if observers and observers[0] is not None:
            watch.finish_dispatch(observers[0])
        thread.join(5)
    assert errors == [failure] and not thread.is_alive() and len(inputs.calls) == 1
    assert (inputs.root / "events" / f"{_point(inputs)}.exited.json").exists()
    assert not observers[0].thread.is_alive()


def test_failed_evaluator_does_not_change_healthy_native_training_ack(inputs, monkeypatch):
    inputs.evaluation["fixture"]["modes"][_point(inputs)] = "failed"
    write_json(inputs.configuration, inputs.evaluation)
    _ready(inputs)
    release = threading.Event()
    release.set()
    _local_training(inputs, monkeypatch, release)
    assert submit_swe_opd.main() == 0 and len(inputs.calls) == 1
    terminal = read_json(inputs.root / "trainer.terminal.json")
    assert terminal["native_execution_succeeded"] is True
    row = read_json(inputs.root / "dispatch" / inputs.job / "dispatch" / f"{_point(inputs)}.json")
    assert row["status"] == "EVALUATOR_EXITED" and row["exit_code"] == 1


def _qualification_ready(inputs, update):
    return watch.notify_ready(
        inputs.configuration,
        inputs.evaluation,
        job_id=inputs.job,
        point_id=f"qualification.A-full.{inputs.job}.HF{update}",
        checkpoint_dir=Path(inputs.evaluation["owned_root"]) / inputs.job / "hf" / f"step_{update - 1}",
    )


def test_explicit_qualification_notification_uses_same_process_and_selected_slots(inputs):
    inputs.evaluation.update(
        root=str(inputs.root / "qualification-evaluations"), task_ids=[f"task-{i}" for i in range(100)]
    )
    inputs.evaluation["dispatch"]["qualification_attempt_ids"] = ["task-0#attempt-0", "task-1#attempt-3"]
    write_json(inputs.configuration, inputs.evaluation)
    _qualification_ready(inputs, 2)
    _qualification_ready(inputs, 3)
    watcher = watch.EvaluationWatcher(inputs.config_path, inputs.configuration, inputs.job)
    assert watcher.run(lambda: True) == 0 and len(inputs.calls) == 2
    for argv in inputs.calls:
        selected = [argv[index + 1] for index, arg in enumerate(argv) if arg == "--qualification-attempt"]
        assert selected == inputs.evaluation["dispatch"]["qualification_attempt_ids"]
        assert "--qualification-checkpoint" not in argv and "--original-source" not in argv
    assert len(watcher.rows) == 2 and all(row["status"] == "EVALUATOR_EXITED" for row in watcher.rows.values())


@pytest.mark.parametrize(
    "selection",
    [[], None, ["unknown#attempt-0"], ["task-0#attempt-4"], ["task-0#attempt-0"] * 2, "task-0#attempt-0", "all"],
)
def test_qualification_dispatch_rejects_nonexplicit_or_unfrozen_slots(inputs, selection):
    inputs.evaluation.update(
        root=str(inputs.root / "qualification-evaluations"), task_ids=[f"task-{i}" for i in range(100)]
    )
    if selection == "all":
        selection = [f"task-{i}#attempt-{attempt}" for i in range(100) for attempt in range(4)]
    inputs.evaluation["dispatch"]["qualification_attempt_ids"] = selection
    write_json(inputs.configuration, inputs.evaluation)
    with pytest.raises(ValueError, match="Qualification"):
        watch.EvaluationWatcher(inputs.config_path, inputs.configuration, inputs.job)
    assert not inputs.calls


def test_qualification_cannot_relax_formal_guard_or_freeze_into_wrong_store(inputs):
    inputs.evaluation.update(
        root=str(inputs.root / "qualification-evaluations"), task_ids=[f"task-{i}" for i in range(100)]
    )
    write_json(inputs.configuration, inputs.evaluation)
    with pytest.raises(ValueError, match="qualification"):
        _qualification_ready(inputs, 2)
    with pytest.raises(ValueError, match="formal"):
        _ready(inputs, 2)
    inputs.evaluation["dispatch"]["qualification_attempt_ids"] = ["task-0#attempt-0"]
    inputs.evaluation["root"] = str(inputs.root / "evaluations")
    with pytest.raises(ValueError, match="qualification-evaluations"):
        watch.validate_dispatch(inputs.configuration, inputs.evaluation)
    inputs.evaluation["root"] = str(inputs.root / "qualification-evaluations")
    with pytest.raises(ValueError, match="formal"):
        watch._validate_notification(
            {
                "point_id": _point(inputs),
                "job_id": inputs.job,
                "checkpoint_dir": str(Path(inputs.evaluation["owned_root"]) / inputs.job / "hf" / "step_49"),
                "configuration": str(inputs.configuration),
            },
            inputs.evaluation,
            inputs.job,
            inputs.configuration,
        )


def _native_fork_inputs(inputs):
    config = inputs.config
    config.update(
        repo=str(inputs.root / "repo"),
        shared_dir=str(inputs.root / "shared"),
        worker_local_root="/var/tmp",
        worker_python=sys.executable,
        cuda_compat_dir=str(inputs.root / "cuda"),
        evaluation_resources={"cpu_per_node": 1, "memory_gb_per_node": 1, "host_network": False, "gang_start": False},
        training={"run_kind": "smoke", "successful_updates": 3, "bank_slots": 8, "bank_uses": 2, "save_interval": 2},
    )
    config["checkpoint"]["post_save_hook"] = "tests.manual.agent_opd.swe_hf_export.post_save"
    inputs.evaluation.update(
        root="/mnt/codesign-exp/ycfeng/cpu-identity-only/qualification-evaluations",
        owned_root="/mnt/codesign-exp/ycfeng/cpu-identity-only",
        allocation_identity={"task_id": "fixture-task", "creator": config["creator"], "gpu_tag": config["gpu_tag"]},
        server={
            "python": sys.executable,
            "image": config["image"],
            "repo": config["repo"],
            "local_root": "/var/tmp",
            "startup_timeout": 1,
        },
        task_ids=[f"task-{i}" for i in range(100)],
    )
    inputs.evaluation["dispatch"]["qualification_attempt_ids"] = ["task-0#attempt-0"]
    write_json(inputs.configuration, inputs.evaluation)
    write_json(inputs.config_path, config)


@pytest.mark.parametrize("fault_evidence_available", [True, False])
def test_manual_launcher_actual_hf2_submitter_rejects_child_key_before_admission_and_hf3_drains(
    inputs, monkeypatch, fault_evidence_available, capsys
):
    release, result = threading.Event(), []
    _local_training(inputs, monkeypatch, release)
    _native_fork_inputs(inputs)
    native_check._validate(inputs.config, inputs.config_path)
    for field in ("SR_USER_TOKEN", "SESSION_ROUTER_USER_TOKEN", "AK_BASEMIND", "SK_BASEMIND"):
        monkeypatch.setenv(field, "cpu-private-fixture")
    monkeypatch.setenv("PYTHONPATH", str(ROOT))
    stub_popen = watch.subprocess.Popen

    def popen(argv, **kwargs):
        if argv[argv.index("--point") + 1].endswith(".HF2"):
            inputs.calls.append(argv)
            return REAL_POPEN(argv, **kwargs)
        return stub_popen(argv, **kwargs)

    monkeypatch.setattr(watch.subprocess, "Popen", popen)
    if not fault_evidence_available:
        write = native_check.write_json

        def persist(path, row):
            if Path(path).name == "fault.json":
                raise OSError("CPU auxiliary fault-record write failure")
            return write(path, row)

        monkeypatch.setattr(native_check, "write_json", persist)
    inputs.hold.touch()
    _qualification_ready(inputs, 2)
    thread = threading.Thread(target=lambda: result.append(native_check.main()), daemon=True)
    thread.start()
    directory = Path(inputs.evaluation["dispatch"]["directory"]) / inputs.job
    point2, point3 = (f"qualification.A-full.{inputs.job}.HF{update}" for update in (2, 3))
    try:
        _wait(
            lambda: (directory / "dispatch" / f"{point2}.json").exists()
            and read_json(directory / "dispatch" / f"{point2}.json")["status"] == "UNVERIFIED"
        )
        if fault_evidence_available:
            fault = read_json(directory / "fault.json")
            assert (
                set(fault) == {"point_id", "field", "at"}
                and fault["point_id"] == point2
                and fault["field"] == "AK_BASEMIND"
            )
        else:
            assert "SWE_NATIVE_ASYNC_FAULT_EVIDENCE_UNVERIFIED" in capsys.readouterr().out
        log = next((directory / "logs").glob(f"{point2}.*.log")).read_text()
        assert "Native ACS evaluation requires inherited AK_BASEMIND" in log and "cpu-private-fixture" not in log
        assert os.environ["AK_BASEMIND"] == "cpu-private-fixture"
        assert not list((directory / "receipts").glob(f"{point2}*"))
        assert thread.is_alive() and not (inputs.root / "trainer.terminal.json").exists()
        _qualification_ready(inputs, 3)
        _wait(
            lambda: (directory / "dispatch" / f"{point3}.json").exists()
            and read_json(directory / "dispatch" / f"{point3}.json")["status"] == "ADMITTED"
        )
        release.set()
        _wait(lambda: (inputs.root / "trainer.terminal.json").exists())
        assert thread.is_alive(), "The actual local training main must retain and drain its live HF3 child"
    finally:
        inputs.hold.unlink(missing_ok=True)
        release.set()
        thread.join(5)
    assert result == [0] and not thread.is_alive() and len(inputs.calls) == 2
    assert read_json(inputs.root / "trainer.terminal.json")["native_execution_succeeded"] is True
    summary = read_json(directory / "observer.json")
    assert summary["points"][point2]["status"] == "UNVERIFIED"
    assert summary["points"][point3]["status"] == "EVALUATOR_EXITED" and summary["points"][point3]["exit_code"] == 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("run_kind", "formal"),
        ("successful_updates", 200),
        ("bank_slots", 256),
        ("bank_uses", 50),
        ("save_interval", 50),
    ],
)
def test_manual_native_async_guard_rejects_formal_or_changed_profile(inputs, monkeypatch, field, value):
    release = threading.Event()
    _local_training(inputs, monkeypatch, release)
    _native_fork_inputs(inputs)
    inputs.config["training"][field] = value
    with pytest.raises(ValueError, match="smoke3/8/2/save2"):
        native_check._validate(inputs.config, inputs.config_path)
    assert not inputs.calls


def test_manual_native_async_guard_requires_local_execution_and_one_slot(inputs, monkeypatch):
    release = threading.Event()
    _local_training(inputs, monkeypatch, release)
    _native_fork_inputs(inputs)
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", "cpu-worker")
    with pytest.raises(ValueError, match="local only"):
        native_check._validate(inputs.config, inputs.config_path)
    monkeypatch.delenv("KUBEBRAIN_RJOB_NAME")
    inputs.evaluation["dispatch"]["qualification_attempt_ids"] = ["task-0#attempt-0", "task-1#attempt-1"]
    write_json(inputs.configuration, inputs.evaluation)
    with pytest.raises(ValueError, match="exactly one"):
        native_check._validate(inputs.config, inputs.config_path)
    assert not inputs.calls
