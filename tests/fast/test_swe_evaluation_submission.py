"""Local-only submission fixtures; no real credentials, platform calls or grading."""

import copy
import fcntl
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from tests.fast import test_swe_evaluation as lifecycle
from tests.manual.agent_opd import rjob_budget
from tests.manual.agent_opd import submit_swe_evaluation as submit
from tests.manual.agent_opd import swe_evaluation as swe

case = lifecycle.case
qualification_case = lifecycle.qualification_case


@pytest.fixture
def inputs(tmp_path, monkeypatch):
    policy = {
        "task_id": "fixture-task",
        "task_annotation": "miles.ycfeng/task",
        "personal_nonpreemptible_gpus": 56,
        "temporary_task_allocation": {"expires_at": "2026-11-08T21:00:00+00:00", "nonpreemptible_gpus": 64},
    }
    policy_path = tmp_path / "policy.json"
    policy_path.write_text(json.dumps(policy))
    config = {
        "local_mount": str(tmp_path),
        "repo": str(tmp_path / "miles checkout"),
        "shared_dir": str(tmp_path / "shared"),
        "admission_lock": str(tmp_path / "shared-admission.lock"),
        "worker_local_root": "/var/tmp",
        "gpu_policy": str(policy_path),
        "creator": "i-fengyicheng",
        "gpu_tag": "H200",
        "api_timeout_seconds": 20,
        "phase": "fixture",
        "worker_python": "/opt/sglang/bin/python3",
        "image": "fixture-image@sha256:pinned",
        "charged_group": "step_main",
        "cuda_compat_dir": "/usr/local/cuda-13.0/compat",
        "mounts": ["juicefs+s3://oss.i.shaipower.com/codesign-exp:/mnt/codesign-exp"],
        "envs": {"OMP_NUM_THREADS": "1"},
        "pairs": {
            "A": {
                "teacher": {
                    "cpu_per_node": 16,
                    "memory_gb_per_node": 128,
                    "nodes": 1,
                    "gpus_per_node": 2,
                    "host_network": False,
                    "gang_start": False,
                }
            }
        },
    }
    evaluation = {
        "allocation_identity": {"task_id": policy["task_id"], "creator": config["creator"], "gpu_tag": "H200"},
        "server": {
            "python": config["worker_python"],
            "image": config["image"],
            "repo": config["repo"],
            "local_root": config["worker_local_root"],
            "startup_timeout": 1800,
        },
        "root": "/mnt/codesign-exp/ycfeng/fixture/qualification",
        "owned_root": "/mnt/codesign-exp/ycfeng/fixture/weights",
        "original_source": "/mnt/codesign-exp/ycfeng/source-original-4b",
        "task_ids": [f"fixture__task-{index}" for index in range(100)],
        "evaluation_contract": {"native_config": "fixture-contract"},
    }
    config_path, configuration, receipt = (
        tmp_path / "integration.json",
        tmp_path / "evaluation.json",
        tmp_path / "new.json",
    )
    config_path.write_text(json.dumps(config))
    configuration.write_text(json.dumps(evaluation))
    monkeypatch.setenv("STEPMIND_BACKEND", "rjob")
    monkeypatch.setenv("BRAINPP_ACCESS_KEY", "synthetic-access")
    monkeypatch.setenv("BRAINPP_SECRET_KEY", "synthetic-secret")
    monkeypatch.setenv("SR_USER_TOKEN", "synthetic-private-router-token")
    monkeypatch.setenv("AK_BASEMIND", "synthetic-native-access-key")
    monkeypatch.setenv("SK_BASEMIND", "synthetic-native-secret-key")
    monkeypatch.setenv("EXP_ID", "fixture-original-exp-id")
    monkeypatch.delenv("SESSION_ROUTER_USER_TOKEN", raising=False)
    monkeypatch.delenv("KUBEBRAIN_RJOB_NAME", raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(submit.socket, "gethostbyname", lambda hostname: "192.0.2.1")
    return SimpleNamespace(
        config=config,
        evaluation=evaluation,
        policy=policy,
        config_path=config_path,
        configuration=configuration,
        receipt=receipt,
        point="qualification.local",
    )


def _cli(inputs, monkeypatch, *extra):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "submit_swe_evaluation",
            "--config",
            str(inputs.config_path),
            "--configuration",
            str(inputs.configuration),
            "--point",
            inputs.point,
            "--receipt",
            str(inputs.receipt),
            *extra,
        ],
    )


def _is_locked(path):
    with path.open("a") as competing:
        try:
            fcntl.flock(competing, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        return False


def _platform(
    inputs, monkeypatch, *, committed=0, now="2026-11-08T20:00:00+00:00", status="succeeded", wait_error=None
):
    events, resources = [], []

    class Api:
        def list_namespaced_custom_object(self, **kwargs):
            assert _is_locked(Path(inputs.config["admission_lock"]))
            events.append(("snapshot", kwargs))
            items = (
                []
                if not committed
                else [
                    {
                        "metadata": {
                            "name": "fixture-existing",
                            "labels": {"kubebrain.brainpp.cn/creator": "i-fengyicheng"},
                            "annotations": {"miles.ycfeng/task": "fixture-task"},
                        },
                        "status": {"phase": "Pending"},
                        "spec": {
                            "taskSpecs": {
                                "teacher": {
                                    "replicas": 1,
                                    "positiveTags": ["H200"],
                                    "template": {
                                        "spec": {
                                            "containers": [{"resources": {"requests": {"nvidia.com/gpu": committed}}}]
                                        }
                                    },
                                }
                            }
                        },
                    }
                ]
            )
            return {"metadata": {}, "items": items}

    client = SimpleNamespace(api=Api(), group="fixture", version="v1", namespace="fixture", plural="rjobs")
    admission = submit.policy_admission_snapshot

    def snapshot(*args, **kwargs):
        return admission(*args, **kwargs, now=datetime.fromisoformat(now))

    monkeypatch.setattr(submit, "policy_admission_snapshot", snapshot)

    class Backend:
        def submit(self, resource, **kwargs):
            assert _is_locked(Path(inputs.config["admission_lock"]))
            assert not inputs.receipt.exists(), "The final rendezvous must not expose partial JSON"
            assert "miles.utils" in sys.modules
            events.append(("submit", kwargs))
            resources.append(resource)

            def wait():
                assert not _is_locked(Path(inputs.config["admission_lock"]))
                allocation = json.loads(inputs.receipt.read_text())
                assert allocation["admission"]["submitted"] is True
                assert allocation["job_id"] == "fixture-actual-job"
                events.append(("wait", None))
                if wait_error is not None:
                    raise wait_error

            def poll():
                events.append(("poll", None))
                return status

            return SimpleNamespace(
                rjob=SimpleNamespace(meta=SimpleNamespace(name="fixture-actual-job")), wait=wait, poll=poll
            )

    for name in (
        "steptron",
        "steptron.exp",
        "steptron.utils",
        "steptron.exp.base_exp",
        "steptron.utils.stepmind",
        "steptron.utils.stepmind_control",
    ):
        monkeypatch.setitem(sys.modules, name, ModuleType(name))
    sys.modules["steptron.exp.base_exp"].ResourceConfig = SimpleNamespace
    sys.modules["steptron.utils.stepmind"].get_rjob_client = lambda: client
    sys.modules["steptron.utils.stepmind_control"].RJobBackend = Backend
    return events, resources


def _allocation(inputs):
    admission = rjob_budget.policy_admission_snapshot(
        SimpleNamespace(
            api=SimpleNamespace(list_namespaced_custom_object=lambda **kwargs: {"metadata": {}, "items": []}),
            group="fixture",
            version="v1",
            namespace="fixture",
            plural="rjobs",
        ),
        policy=inputs.policy,
        creator="i-fengyicheng",
        gpu_tag="H200",
        requested_gpus=2,
        timeout=20,
        now=datetime.fromisoformat("2026-11-08T20:00:00+00:00"),
    )
    admission.update(submitted=True, job="fixture-actual-job")
    return {"job_id": "fixture-actual-job", "eval_gpus": 2, "point": inputs.point, "admission": admission}


def test_dry_run_is_local_cpu_only_and_hides_private_environment(inputs, monkeypatch, capsys):
    _cli(
        inputs,
        monkeypatch,
        "--dry-run",
        "--original-source",
        inputs.evaluation["original_source"],
        "--qualification-attempt",
        "fixture__task-0#attempt-0",
        "--qualification-attempt",
        "fixture__task-1#attempt-3",
    )
    before = set(sys.modules)
    assert submit.main() == 0
    output = capsys.readouterr().out
    result = json.loads(output)
    assert not inputs.receipt.exists()
    assert not (set(sys.modules) - before) & {"steptron", "steptron.utils.stepmind", "ray"}
    assert all(
        value not in output
        for value in (
            "synthetic-private-router-token",
            "synthetic-secret",
            "synthetic-native-access-key",
            "synthetic-native-secret-key",
        )
    )
    assert result["requested_gpus"] == 2 and result["submitted"] is False
    assert result["tasks"]["evaluation"]["cpu"] == 16 and result["tasks"]["evaluation"]["mem_gb"] == 128
    script = shlex.split(result["command"])[2]
    argv = shlex.split(script.splitlines()[-1])[1:]
    assert argv[0] == inputs.config["worker_python"] and "--worker" in argv
    assert argv.count("--qualification-attempt") == 2
    assert argv[-4:] == [
        "--qualification-attempt",
        "fixture__task-0#attempt-0",
        "--qualification-attempt",
        "fixture__task-1#attempt-3",
    ]
    assert "swe_evaluation_config" not in result["command"]


@pytest.mark.parametrize("committed,preemptible", [(0, False), (62, False), (64, True)])
def test_fresh_snapshot_submit_and_receipt_share_the_lock(inputs, monkeypatch, capsys, committed, preemptible):
    events, resources = _platform(inputs, monkeypatch, committed=committed)
    _cli(inputs, monkeypatch)
    assert submit.main() == 0
    assert [event[0] for event in events] == ["snapshot", "submit", "wait", "poll"]
    resource = resources[0]
    assert resource.preemptible is preemptible
    assert resource.annotations[inputs.policy["task_annotation"]] == inputs.policy["task_id"]
    assert (
        resource.annotations["kubebrain.brainpp.cn/filestore-volume"]
        == f"192.0.2.1:{inputs.config['local_mount']}:{inputs.config['local_mount']}"
    )
    assert resource.image == inputs.config["image"] and resource.mounts == inputs.config["mounts"]
    assert resource.pull_code is False and resource.charged_group == "step_main"
    assert resource.task_specs["evaluation"]["gpu"] == 2 and resource.task_specs["evaluation"]["replica"] == 1
    assert (
        resource.envs["SR_USER_TOKEN"] == resource.envs["SESSION_ROUTER_USER_TOKEN"] == "synthetic-private-router-token"
    )
    assert resource.envs["PYTHONPATH"] == inputs.config["repo"]
    assert resource.envs["OMP_NUM_THREADS"] == "1"
    assert resource.envs["AK_BASEMIND"] == "synthetic-native-access-key"
    assert resource.envs["SK_BASEMIND"] == "synthetic-native-secret-key"
    allocation = json.loads(inputs.receipt.read_text())
    assert allocation["admission"]["requested_gpus"] == allocation["eval_gpus"] == 2
    assert allocation["admission"]["preemptible"] is preemptible
    assert not inputs.receipt.with_name(inputs.receipt.name + ".pending").exists()
    submit.validate_allocation(allocation, requested_gpus=2, expected=inputs.evaluation["allocation_identity"])
    output = capsys.readouterr().out
    for text in (output, inputs.receipt.read_text(), events[1][1]["command"]):
        assert all(
            value not in text
            for value in (
                "synthetic-private-router-token",
                "synthetic-secret",
                "synthetic-native-access-key",
                "synthetic-native-secret-key",
            )
        )


def test_expired_personal_ceiling_denies_without_backend_submit(inputs, monkeypatch):
    events, resources = _platform(inputs, monkeypatch, committed=56, now="2026-11-08T21:00:00+00:00")
    _cli(inputs, monkeypatch)
    assert submit.main() == 2
    assert [event[0] for event in events] == ["snapshot"] and resources == []
    receipt = json.loads(inputs.receipt.read_text())
    assert receipt["job_id"] is None and receipt["admission"]["submitted"] is False
    assert receipt["admission"]["scope"] == "personal" and receipt["admission"]["preemptible"] is False


@pytest.mark.parametrize("status", ["failed", "killed", "stopped", "unknown"])
def test_terminal_non_success_cannot_be_reported_as_success(inputs, monkeypatch, status):
    _platform(inputs, monkeypatch, status=status)
    _cli(inputs, monkeypatch)
    assert submit.main() == 1


def test_native_wait_failure_is_not_swallowed_or_retried(inputs, monkeypatch):
    events, _ = _platform(inputs, monkeypatch, wait_error=RuntimeError("fixture-native-wait-failure"))
    _cli(inputs, monkeypatch)
    with pytest.raises(RuntimeError, match="fixture-native-wait-failure"):
        submit.main()
    assert [event[0] for event in events] == ["snapshot", "submit", "wait"]
    with pytest.raises(FileExistsError):
        submit.main()
    assert [event[0] for event in events] == ["snapshot", "submit", "wait"]


@pytest.mark.parametrize("field", ["configuration", "receipt"])
def test_cloud_or_outside_mount_configuration_and_receipt_are_rejected(inputs, field):
    paths = {"configuration": inputs.configuration, "receipt": inputs.receipt}
    paths[field] = Path("/mnt/codesign-exp/another-user/fixture.json")
    with pytest.raises(ValueError, match="under local_mount"):
        submit._validate_inputs(
            inputs.config, inputs.evaluation, inputs.config_path, paths["configuration"], paths["receipt"], None
        )


def test_configuration_symlink_escape_and_cloud_artifact_escape_are_rejected(inputs, tmp_path):
    alias = tmp_path / "alias.json"
    alias.symlink_to("/mnt/codesign-exp/another-user/fixture.json")
    with pytest.raises(ValueError, match="under local_mount"):
        submit._validate_inputs(inputs.config, inputs.evaluation, inputs.config_path, alias, inputs.receipt, None)
    evaluation = copy.deepcopy(inputs.evaluation)
    evaluation["root"] = "/mnt/codesign-exp/another-user/evaluation"
    with pytest.raises(ValueError, match="personal cloud"):
        submit._validate_inputs(
            inputs.config, evaluation, inputs.config_path, inputs.configuration, inputs.receipt, None
        )


@pytest.mark.parametrize("field,value", [("image", "unrelated-image"), ("python", "/native/python3.10")])
def test_cross_interpreter_and_image_deployment_mismatch_fail(inputs, field, value):
    evaluation = copy.deepcopy(inputs.evaluation)
    evaluation["server"][field] = value
    with pytest.raises(ValueError, match="deployment must match"):
        submit._validate_inputs(
            inputs.config, evaluation, inputs.config_path, inputs.configuration, inputs.receipt, None
        )


def test_explicit_resource_sizing_is_honored_without_a_new_hardware_guess(inputs):
    config = copy.deepcopy(inputs.config)
    config["evaluation_resources"] = {
        "cpu_per_node": 24,
        "memory_gb_per_node": 192,
        "host_network": False,
        "gang_start": False,
    }
    task = submit._task_specs(config)["evaluation"]
    assert (task["cpu"], task["mem_gb"], task["gpu"], task["replica"]) == (24, 192, 2, 1)
    config["evaluation_resources"]["gpus_per_node"] = 8
    with pytest.raises(ValueError, match="two-GPU"):
        submit._task_specs(config)


@pytest.mark.parametrize("worker,wrong_cwd", [(True, False), (False, True)])
def test_submission_refuses_worker_or_wrong_local_root(inputs, monkeypatch, tmp_path, worker, wrong_cwd):
    if worker:
        monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", "fixture-forbidden-nested-worker")
    if wrong_cwd:
        (tmp_path / "subdir").mkdir()
        monkeypatch.chdir(tmp_path / "subdir")
    _cli(inputs, monkeypatch)
    with pytest.raises(ValueError, match="local"):
        submit.main()
    assert not inputs.receipt.exists()


def test_private_tokens_are_inherited_and_config_tokens_are_refused(inputs, monkeypatch):
    monkeypatch.delenv("SR_USER_TOKEN")
    monkeypatch.setenv("SESSION_ROUTER_USER_TOKEN", "synthetic-other-alias")
    envs = submit._worker_environment(inputs.config)
    assert envs["SR_USER_TOKEN"] == envs["SESSION_ROUTER_USER_TOKEN"] == "synthetic-other-alias"
    monkeypatch.setenv("SR_USER_TOKEN", "synthetic-mismatch")
    with pytest.raises(ValueError, match="matching token aliases"):
        submit._worker_environment(inputs.config)
    config = copy.deepcopy(inputs.config)
    config["envs"]["SR_USER_TOKEN"] = "synthetic-never-store"
    with pytest.raises(ValueError, match="not stored in configuration"):
        submit._worker_environment(config)


def test_atomic_receipt_publication_refuses_overwrite(inputs):
    pending = inputs.receipt.with_name(inputs.receipt.name + ".pending")
    inputs.receipt.write_text("preserved-receipt")
    with pending.open("x") as stream, pytest.raises(FileExistsError):
        submit._publish_receipt(stream, pending, inputs.receipt, {"submitted": True})
    assert inputs.receipt.read_text() == "preserved-receipt"


@pytest.mark.parametrize("baseline", [False, True])
def test_worker_waits_for_receipt_enqueues_only_explicit_source_then_execs_native(inputs, monkeypatch, baseline):
    allocation, events = _allocation(inputs), []
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", allocation["job_id"])
    module = ModuleType("tests.manual.agent_opd.rjob_warmup")
    monkeypatch.setattr(submit.time, "monotonic", lambda: 100.0)

    def wait(path, deadline):
        assert path == inputs.receipt and deadline == 1900.0
        events.append("bounded-wait")
        return allocation

    module._wait_file = wait
    monkeypatch.setitem(sys.modules, module.__name__, module)

    def enqueue(**kwargs):
        events.append("enqueue-baseline")
        assert kwargs == {
            "point_id": inputs.point,
            "source": Path(inputs.evaluation["original_source"]),
            "task_ids": inputs.evaluation["task_ids"],
            "configuration": inputs.evaluation["evaluation_contract"],
        }

    monkeypatch.setattr(submit, "store_from_config", lambda evaluation: SimpleNamespace(enqueue_baseline=enqueue))
    executed = []
    monkeypatch.setattr(submit.os, "execv", lambda python, argv: (events.append("exec-native"), executed.append(argv)))
    args = SimpleNamespace(
        receipt=inputs.receipt,
        configuration=inputs.configuration,
        point=inputs.point,
        original_source=Path(inputs.evaluation["original_source"]) if baseline else None,
        qualification_checkpoint=None,
        qualification_attempts=["fixture__task-0#attempt-0", "fixture__task-1#attempt-3"],
    )
    submit._prepare_worker(inputs.config, inputs.evaluation, args)
    assert events == (
        ["bounded-wait", "enqueue-baseline", "exec-native"] if baseline else ["bounded-wait", "exec-native"]
    )
    assert executed[0][0] == inputs.config["worker_python"]
    assert executed[0][4] == "tests.manual.agent_opd.run_swe_evaluation"
    assert executed[0][-4:] == [
        "--qualification-attempt",
        "fixture__task-0#attempt-0",
        "--qualification-attempt",
        "fixture__task-1#attempt-3",
    ]


def test_receipt_wait_timeout_stops_before_enqueue_or_native_exec(inputs, monkeypatch):
    module = ModuleType("tests.manual.agent_opd.rjob_warmup")

    def wait(path, deadline):
        raise TimeoutError("fixture-receipt-not-published")

    module._wait_file = wait
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setattr(submit.os, "execv", lambda *args: pytest.fail("Native worker must not start without receipt"))
    args = SimpleNamespace(receipt=inputs.receipt)
    with pytest.raises(TimeoutError, match="not-published"):
        submit._prepare_worker(inputs.config, inputs.evaluation, args)


def test_wrong_job_receipt_never_enqueues_a_baseline(inputs, monkeypatch):
    module = ModuleType("tests.manual.agent_opd.rjob_warmup")
    module._wait_file = lambda *args: _allocation(inputs)
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", "fixture-other-job")
    monkeypatch.setattr(submit, "store_from_config", lambda *args: pytest.fail("Foreign receipt cannot enqueue"))
    args = SimpleNamespace(receipt=inputs.receipt, point=inputs.point)
    with pytest.raises(ValueError, match="actual two-GPU"):
        submit._prepare_worker(inputs.config, inputs.evaluation, args)


def test_existing_receipt_and_pending_attempt_are_never_reused(inputs, monkeypatch):
    _cli(inputs, monkeypatch, "--dry-run")
    pending = inputs.receipt.with_name(inputs.receipt.name + ".pending")
    pending.write_text("unfinished-admission-investigate-before-relaunch")
    with pytest.raises(FileExistsError, match="new receipt"):
        submit.main()
    assert pending.read_text() == "unfinished-admission-investigate-before-relaunch"


def test_worker_enqueue_uses_real_protected_baseline_identity_without_overwriting(inputs, monkeypatch, tmp_path):
    source = tmp_path / "protected-source"
    source.mkdir()
    weight = source / "original-weight.safetensors"
    weight.write_bytes(b"synthetic-protected-weight-bytes")
    before = weight.stat()
    evaluation = {
        **inputs.evaluation,
        "root": str(tmp_path / "qualification"),
        "owned_root": str(tmp_path / "new-weights"),
        "reference_root": str(tmp_path / "reference"),
        "protected_sources": [str(source)],
        "original_source": str(source),
    }
    allocation = _allocation(inputs)
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", allocation["job_id"])
    module = ModuleType("tests.manual.agent_opd.rjob_warmup")
    module._wait_file = lambda *args: allocation
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setattr(submit.os, "execv", lambda *args: None)
    args = SimpleNamespace(
        receipt=inputs.receipt,
        configuration=inputs.configuration,
        point=inputs.point,
        original_source=source,
        qualification_checkpoint=None,
        qualification_attempts=["fixture__task-0#attempt-0"],
    )
    submit._prepare_worker(inputs.config, evaluation, args)
    store = swe.store_from_config(evaluation)
    manifest = store.manifest(inputs.point)
    assert manifest["owned"] is False and manifest["native_update"] is None and manifest["files"] == []
    assert manifest["checkpoint_dir"] == str(source) and len(manifest["task_ids"]) == 100
    assert store.state(inputs.point)["status"] == "QUEUED"
    submit._prepare_worker(inputs.config, evaluation, args)
    assert store.manifest(inputs.point) == manifest
    assert (
        weight.read_bytes() == b"synthetic-protected-weight-bytes" and weight.stat().st_mtime_ns == before.st_mtime_ns
    )
    evaluation["evaluation_contract"] = {"native_config": "different-contract-must-not-overwrite"}
    with pytest.raises(ValueError, match="immutable"):
        submit._prepare_worker(inputs.config, evaluation, args)
    assert store.manifest(inputs.point) == manifest


def test_exec_adapter_preserves_native_worker_exit_code(inputs):
    inputs.receipt.write_text(json.dumps(_allocation(inputs)))
    code = """
import json, os, sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from tests.manual.agent_opd import submit_swe_evaluation as submit
config, evaluation, receipt = map(Path, sys.argv[1:])
config, evaluation = json.loads(config.read_text()), json.loads(evaluation.read_text())
module = ModuleType('tests.manual.agent_opd.rjob_warmup')
module._wait_file = lambda path, deadline: json.loads(path.read_text())
sys.modules[module.__name__] = module
os.environ['KUBEBRAIN_RJOB_NAME'] = 'fixture-actual-job'
submit._worker_argv = lambda *args: [sys.executable, '-B', '-c', 'raise SystemExit(23)']
args = SimpleNamespace(receipt=receipt, configuration=Path(sys.argv[2]), point='qualification.local',
                       original_source=None, qualification_attempts=None, qualification_checkpoint=None)
submit._prepare_worker(config, evaluation, args)
raise AssertionError('exec must replace, not return from, the adapter')
"""
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[2]), PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run(
        [sys.executable, "-B", "-c", code, str(inputs.config_path), str(inputs.configuration), str(inputs.receipt)],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 23 and result.stdout == "" and result.stderr == ""


@pytest.mark.parametrize("name", ["AK_BASEMIND", "SK_BASEMIND"])
@pytest.mark.parametrize("absent", [True, False])
def test_native_acs_keys_are_required_without_fallback(inputs, monkeypatch, name, absent):
    if absent:
        monkeypatch.delenv(name)
    else:
        monkeypatch.setenv(name, "")
    with pytest.raises(ValueError, match=name):
        submit._worker_environment(inputs.config)


@pytest.mark.parametrize("name", ["AK_BASEMIND", "SK_BASEMIND"])
def test_native_acs_config_file_credentials_are_refused(inputs, name):
    config = copy.deepcopy(inputs.config)
    config["envs"][name] = "synthetic-must-never-be-configured"
    with pytest.raises(ValueError, match="not stored in configuration"):
        submit._worker_environment(config)


@pytest.fixture
def qualification_inputs(inputs):
    original = inputs.evaluation["original_source"]
    inputs.config["pairs"]["A"]["student"] = {"path": original}
    inputs.config["pairs"]["B"] = {"student": {"path": original}}
    inputs.evaluation.update(
        root="/mnt/codesign-exp/ycfeng/fixture/qualification-evaluations",
        protected_sources=[original],
        reference_root="/fixture/reference",
    )
    inputs.checkpoint = Path(inputs.evaluation["owned_root"]) / "smoke" / "hf" / "step_2"
    inputs.config_path.write_text(json.dumps(inputs.config))
    inputs.configuration.write_text(json.dumps(inputs.evaluation))
    return inputs


def test_owned_qualification_dry_run_hands_off_checkpoint_and_attempts(qualification_inputs, monkeypatch, capsys):
    data = qualification_inputs
    _cli(
        data,
        monkeypatch,
        "--dry-run",
        "--qualification-checkpoint",
        str(data.checkpoint),
        "--qualification-attempt",
        "fixture__task-0#attempt-0",
    )
    assert submit.main() == 0
    preview = json.loads(capsys.readouterr().out)
    script = shlex.split(preview["command"])[2]
    argv = shlex.split(script.splitlines()[-1])[1:]
    assert "--original-source" not in argv and "--worker" in argv
    assert argv[argv.index("--qualification-checkpoint") + 1] == str(data.checkpoint)
    assert argv[-2:] == ["--qualification-attempt", "fixture__task-0#attempt-0"]
    assert not data.receipt.exists()


def test_owned_checkpoint_and_original_source_are_mutually_exclusive(inputs, monkeypatch):
    _cli(
        inputs,
        monkeypatch,
        "--qualification-checkpoint",
        "/fixture/hf/step_2",
        "--original-source",
        inputs.evaluation["original_source"],
    )
    with pytest.raises(SystemExit) as error:
        submit.main()
    assert error.value.code == 2 and not inputs.receipt.exists()


@pytest.mark.parametrize(
    "attempts",
    [
        None,
        [],
        ["foreign#attempt-0"],
        ["fixture__task-0#attempt-0", "fixture__task-0#attempt-0"],
        ["fixture__task-0#attempt-4"],
    ],
)
def test_owned_qualification_requires_exact_explicit_attempts(qualification_inputs, attempts):
    data = qualification_inputs
    with pytest.raises(ValueError, match="distinct explicit slots"):
        submit._validate_qualification_checkpoint(data.config, data.evaluation, data.point, data.checkpoint, attempts)


def test_owned_qualification_cannot_request_all400(qualification_inputs):
    data = qualification_inputs
    attempts = [f"{task}#attempt-{attempt}" for task in data.evaluation["task_ids"] for attempt in range(4)]
    with pytest.raises(ValueError, match="not all"):
        submit._validate_qualification_checkpoint(data.config, data.evaluation, data.point, data.checkpoint, attempts)


@pytest.mark.parametrize("change", ["namespace", "point", "original", "unprotected", "checkpoint"])
def test_owned_qualification_refuses_formal_or_unprotected_identity(qualification_inputs, change):
    data = qualification_inputs
    if change == "namespace":
        data.evaluation["root"] = "/mnt/codesign-exp/ycfeng/fixture/evaluations"
    elif change == "point":
        data.point = "A-r256.HF50"
    elif change == "original":
        data.config["pairs"]["B"]["student"]["path"] = "/mnt/codesign-exp/ycfeng/other-original"
    elif change == "unprotected":
        data.evaluation["protected_sources"] = []
    else:
        data.checkpoint = Path(data.evaluation["original_source"])
    with pytest.raises(ValueError, match="qualification|original|owned root|protected"):
        submit._validate_qualification_checkpoint(
            data.config, data.evaluation, data.point, data.checkpoint, ["fixture__task-0#attempt-0"]
        )


def test_owned_qualification_receipt_identifies_source_without_credentials(qualification_inputs, monkeypatch, capsys):
    data = qualification_inputs
    events, _ = _platform(data, monkeypatch)
    _cli(
        data,
        monkeypatch,
        "--qualification-checkpoint",
        str(data.checkpoint),
        "--qualification-attempt",
        "fixture__task-0#attempt-0",
    )
    assert submit.main() == 0
    receipt = json.loads(data.receipt.read_text())
    assert receipt["run_kind"] == "qualification" and receipt["qualification_checkpoint"] == str(data.checkpoint)
    assert receipt["point"] == data.point
    for text in (data.receipt.read_text(), capsys.readouterr().out, events[1][1]["command"]):
        assert all(
            value not in text
            for value in (
                "synthetic-private-router-token",
                "synthetic-native-access-key",
                "synthetic-native-secret-key",
            )
        )


def test_worker_enqueues_actual_owned_qualification_before_native_exec(inputs, qualification_case, monkeypatch):
    store, enqueue, hf, source, native, _ = qualification_case
    evaluation = {
        **inputs.evaluation,
        "root": str(store.root),
        "owned_root": str(store.owned_root),
        "protected_sources": [str(source)],
        "original_source": str(source),
        "reference_root": str(store.reference_root),
        "evaluation_contract": enqueue["configuration"],
    }
    allocation = _allocation(inputs) | {
        "point": enqueue["point_id"],
        "run_kind": "qualification",
        "qualification_checkpoint": str(hf),
    }
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", allocation["job_id"])
    module = ModuleType("tests.manual.agent_opd.rjob_warmup")
    module._wait_file = lambda *args: allocation
    monkeypatch.setitem(sys.modules, module.__name__, module)
    executed = []

    def execute(python, argv):
        queued = swe.store_from_config(evaluation)
        assert queued.manifest(enqueue["point_id"])["native_update"] == native
        assert queued.state(enqueue["point_id"])["status"] == "QUEUED"
        executed.append(argv)

    monkeypatch.setattr(submit.os, "execv", execute)
    args = SimpleNamespace(
        receipt=inputs.receipt,
        configuration=inputs.configuration,
        point=enqueue["point_id"],
        original_source=None,
        qualification_checkpoint=hf,
        qualification_attempts=["fixture__task-0#attempt-0"],
    )
    submit._prepare_worker(inputs.config, evaluation, args)
    manifest = swe.store_from_config(evaluation).manifest(enqueue["point_id"])
    assert manifest["owned"] is True and manifest["run_kind"] == "qualification"
    assert manifest["checkpoint_dir"] == str(hf)
    assert executed[0][4] == "tests.manual.agent_opd.run_swe_evaluation"
    assert executed[0][-2:] == ["--qualification-attempt", "fixture__task-0#attempt-0"]
    assert "--qualification-checkpoint" not in executed[0]
    summary = swe.store_from_config(evaluation).summary(enqueue["point_id"])
    assert summary["completed"] == 0 and len(summary["missing_attempt_ids"]) == 400 and summary["avg_at_n"] is None
    allocation["qualification_checkpoint"] = "/another/hf/step_2"
    with pytest.raises(ValueError, match="exact owned qualification checkpoint"):
        submit._prepare_worker(inputs.config, evaluation, args)
    assert len(executed) == 1
