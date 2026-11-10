"""CPU-only probe input, cgroup discovery, comparison, and subprocess isolation checks."""

import copy
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.manual.agent_opd import probe_tms_allocator as probe


def _argv(output):
    return ["--launch-receipt", "launch.json", "--native-source-receipt", "source.json",
            "--transient-mib", "1024", "--moment-mib", "64", "--output-dir", str(output)]


@pytest.mark.parametrize("flag,value", [("--transient-mib", "0"), ("--transient-mib", "-1"),
                                        ("--moment-mib", "0"), ("--moment-mib", "not-a-number")])
def test_positive_sizes(flag, value, tmp_path):
    argv = _argv(tmp_path)
    argv[argv.index(flag) + 1] = value
    with pytest.raises(SystemExit) as error:
        probe._parser().parse_args(argv)
    assert error.value.code == 2


def test_help_has_no_worker_imports():
    command = [sys.executable, "-I", str(Path(probe.__file__).resolve()), "--help"]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    assert completed.returncode == 0
    assert "--transient-mib" in completed.stdout and "--moment-mib" in completed.stdout
    assert "Traceback" not in completed.stderr


@pytest.mark.parametrize("membership,mount,expected,counter", [
    ("0::/work/probe\n", "1 0 0:1 / /sys/fs/cgroup rw - cgroup2 cgroup rw\n",
     "/sys/fs/cgroup/work/probe", "memory.current"),
    ("0::/\n", "1 0 0:1 /kubepods/work/probe /sys/fs/cgroup rw - cgroup2 cgroup rw\n",
     "/sys/fs/cgroup", "memory.current"),
    ("2:memory:/docker/probe\n", "1 0 0:1 /docker /sys/fs/cgroup/memory rw - cgroup cgroup rw,memory\n",
     "/sys/fs/cgroup/memory/probe", "memory.usage_in_bytes"),
])
def test_cgroup_resolution(monkeypatch, membership, mount, expected, counter):
    files = {"/proc/self/cgroup": membership, "/proc/self/mountinfo": mount}
    monkeypatch.setattr(Path, "read_text", lambda self: files[str(self)])
    monkeypatch.setattr(Path, "exists", lambda self: str(self) == f"{expected}/{counter}")
    directory, actual_counter, _ = probe._cgroup_location()
    assert str(directory) == expected and actual_counter == counter


def _case(*, late):
    before = {"cuda": {"reserved_bytes": 1024 if late else 128, "inactive_split_bytes": 896 if late else 0},
              "host": {"rss_bytes": 100, "cgroup": {"current_bytes": 200}}}
    paused = {"host": {"rss_bytes": 100 + (1024 if late else 128),
                       "cgroup": {"current_bytes": 200 + (1024 if late else 128)}}}
    return {"status": "passed", "moment_state_bytes": 128,
            "phases": {"before_pause": before, "paused": paused},
            "transient_range": {"start": 100, "end": 1124},
            "persistent_ranges": {"exp_avg": {"start": 100 if late else 2000},
                                  "exp_avg_sq": {"start": 164 if late else 2064}}}


def test_comparison_reports_order_effect_without_formal_root_claim():
    result = probe._comparison({"late_moments": _case(late=True), "early_moments": _case(late=False)})
    assert result["status"] == "complete"
    assert result["allocator_order_effect_observed"]
    assert result["late_init_rss_pause_delta_larger"]
    assert result["formal_run_root_cause_proven"] is False


def test_identical_results_are_a_valid_negative_result():
    case = _case(late=False)
    result = probe._comparison({"late_moments": case, "early_moments": copy.deepcopy(case)})
    assert result["status"] == "complete"
    assert result["allocator_order_effect_observed"] is False
    assert result["late_init_rss_pause_delta_larger"] is False


def test_failed_case_does_not_skip_independent_case(monkeypatch, tmp_path):
    seen = []

    def run(command, *, check):
        name = command[command.index("--case") + 1]
        seen.append(name)
        probe._write_json(tmp_path / f"{name}.json", {"status": "failed" if len(seen) == 1 else "passed"})
        return SimpleNamespace(returncode=23 if len(seen) == 1 else 0)

    monkeypatch.setattr(probe.subprocess, "run", run)
    assert probe.main(_argv(tmp_path)) == 1
    summary = json.loads((tmp_path / "summary.json").read_text())
    assert seen == list(probe._CASES)
    assert summary["cases"]["late_moments"]["returncode"] == 23
    assert summary["cases"]["early_moments"]["status"] == "passed"
    assert summary["comparison"]["status"] == "incomplete"


def test_existing_outputs_are_not_overwritten(tmp_path):
    (tmp_path / "early_moments.json").write_text("retained evidence\n")
    with pytest.raises(FileExistsError):
        probe.main(_argv(tmp_path))
    assert (tmp_path / "early_moments.json").read_text() == "retained evidence\n"


def test_snapshot_retains_blocks_without_stack_frames():
    segment = {"device": 0, "address": 100, "total_size": 1024, "allocated_size": 128,
               "active_size": 128, "stream": 0, "segment_type": "large", "segment_pool_id": (0, 0),
               "blocks": [{"address": 100, "size": 128, "requested_size": 128,
                           "state": "active_allocated", "frames": [{"filename": "synthetic"}]}]}
    result = probe._segments([segment])[0]
    assert result["total_size"] == 1024 and result["blocks"][0]["state"] == "active_allocated"
    assert "frames" not in result["blocks"][0]


def test_case_reexec_uses_native_environment_owner(monkeypatch, tmp_path):
    calls = {}

    def compute(args, context, *, fp8_scales):
        calls["owner_args"] = vars(args)
        return {"LD_PRELOAD": "/native/formal-preload.so", "TMS_INIT_ENABLE": "1",
                "TMS_INIT_ENABLE_CPU_BACKUP": "1"}

    def config(**defaults):
        return SimpleNamespace(model_fields={name: SimpleNamespace(default=value) for name, value in defaults.items()})

    modules = {
        "miles.ray.specs.train": SimpleNamespace(compute_trainer_env_vars=compute),
        "miles.utils.args.configs.train": SimpleNamespace(TrainConfig=config(train_backend="megatron", train_env_vars="{}")),
        "miles.utils.args.configs.cluster": SimpleNamespace(ClusterConfig=config(
            offload_train_target="cpu", offload_train_disk_dir=None, offload_train_disk_chunk_mb=256)),
        "miles.utils.args.configs.debug": SimpleNamespace(DebugConfig=config(dumper_source_patcher_config_train=None)),
        "miles.utils.environ": SimpleNamespace(default_fp8_block_scaling_fp32_scales=lambda: "native-default"),
    }
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)
    for name in probe._ALLOCATOR_ENV:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("TMPDIR", "/worker-tmp/probe/tmp")
    monkeypatch.setenv("NCCL_MIN_NCHANNELS", "native-platform-value")
    monkeypatch.setattr(sys, "argv", [probe.__file__, *_argv(tmp_path), "--case", "late_moments"])
    monkeypatch.setattr(probe.os, "execve", lambda executable, command, env: calls.update(command=command, env=env))
    receipt = {"training_argv": ["--offload-train"], "resolved_experiment": {"worker_local_root": "/worker-tmp"}}
    probe._prepare_case(probe._parser().parse_args(_argv(tmp_path)), receipt)
    assert calls["owner_args"]["offload_train"] is True and calls["owner_args"]["train_env_vars"] == {}
    assert calls["env"]["LD_PRELOAD"] == "/native/formal-preload.so"
    assert calls["env"]["NCCL_MIN_NCHANNELS"] == "native-platform-value"
    assert calls["command"][-1] == "--prepared"


def test_bootstrap_exception_is_retained_without_cuda(monkeypatch, tmp_path):
    launch = tmp_path / "launch.json"
    launch.write_text("{}")
    argv = _argv(tmp_path)
    argv[argv.index("--launch-receipt") + 1] = str(launch)
    args = probe._parser().parse_args([*argv, "--case", "late_moments"])

    def fail(args, receipt):
        raise RuntimeError("synthetic bootstrap failure before CUDA")

    monkeypatch.setattr(probe, "_prepare_case", fail)
    assert probe._case(args) == 1
    report = json.loads((tmp_path / "late_moments.json").read_text())
    assert report["status"] == "failed" and report["phases"] == {}
    assert report["error"] == "synthetic bootstrap failure before CUDA"


def test_interrupted_report_update_preserves_last_receipt(monkeypatch, tmp_path):
    path = tmp_path / "case.json"
    probe._write_json(path, {"phase": "before_pause"}, exclusive=True)

    def interrupted(source, destination):
        raise RuntimeError("synthetic interruption before rename")

    monkeypatch.setattr(probe.os, "replace", interrupted)
    with pytest.raises(RuntimeError, match="before rename"):
        probe._write_json(path, {"phase": "paused"})
    assert json.loads(path.read_text()) == {"phase": "before_pause"}
