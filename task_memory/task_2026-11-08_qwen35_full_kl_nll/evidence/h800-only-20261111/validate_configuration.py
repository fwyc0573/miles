"""Record CPU-only configuration checks for the independent H800-only attempts."""

import copy
import difflib
import json
import os
import shlex
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

from tests.fast.test_swe_replay import _configuration_reads, _typed_swe_config
from tests.manual.agent_opd import run_swe_opd
from tests.manual.agent_opd.run_qwen35_opd import _runtime_env
from tests.manual.agent_opd.swe_replay import ReplaySchedule, SweReplayConfig

from miles.utils.args.custom_view import compute_custom_function_config
from miles.utils.args.runtime import AllConfig, OrchestratorConfig, RolloutConfig
from miles.utils.external_utils.command_utils.base_backend import ExecuteTrainConfig, ExecuteTrainRequest
from miles.utils.external_utils.command_utils.common import train_env_vars
from miles.utils.function_registry import load_function


BASE = "6b450939305f3c3ae2cdbffea9d4a705dcfac5e6"
TASK = Path("task_memory/task_2026-11-08_qwen35_full_kl_nll")
OUT = TASK / "evidence/h800-only-20261111/verified3"
CONFIG = TASK / "formal_config.json"


def write_new(name, content):
    with (OUT / name).open("x") as output:
        output.write(content)


def flags(argv):
    result = defaultdict(list)
    index = 0
    while index < len(argv):
        name = argv[index]
        assert name.startswith("--"), name
        index += 1
        value = True
        if index < len(argv) and not argv[index].startswith("--"):
            value = argv[index]
            index += 1
        result[name].append(value)
    assert all(len(values) == 1 for values in result.values()), result
    return dict(result)


def formal_contract(pair, actual):
    typed = _typed_swe_config("full", pair=pair)
    payload = typed.model_dump(mode="python")
    backend = dict(typed.raw_megatron.base_args)
    replay_values = {}
    contract_fields = _configuration_reads(Path("tests/manual/agent_opd/swe_replay.py"), "training_protocol")
    for name, values in actual.items():
        field = name.removeprefix("--").replace("-", "_")
        raw = values[0]
        try:
            value = json.loads(raw) if isinstance(raw, str) else raw
        except json.JSONDecodeError:
            value = raw
        if field in SweReplayConfig.model_fields:
            replay_values[field] = value
        if field in contract_fields and field in AllConfig.model_fields and not field.endswith("_path"):
            payload[field] = value
        if field in backend:
            backend[field] = value
    replay = SweReplayConfig.model_validate(replay_values)
    for name in ("rollout_function_path", "custom_rm_path", "custom_megatron_optimizer_step_hook_path"):
        hook = getattr(typed, name)
        assert hook.path == actual["--" + name.replace("_", "-")][0]
        payload[name] = hook.model_copy(update={"config": replay})
    payload["raw_megatron"] = typed.raw_megatron.model_copy(update={"base_args": backend})
    parsed = AllConfig.model_validate(payload)
    sliced = OrchestratorConfig.slice_from(parsed)
    restored = OrchestratorConfig.model_validate_json(sliced.model_dump_json())
    hook = restored.custom_megatron_optimizer_step_hook_path
    merged = compute_custom_function_config(restored, hook)
    driver = load_function(hook).training_protocol(merged)
    assert driver.budget == 200 and driver.successful == 0
    assert next(driver.rollout_ids(0)) == 0
    schedule = ReplaySchedule(merged.swe_protocol, bank_uses=merged.swe_bank_uses, updates=driver.budget)
    positions = []
    for update in range(driver.budget):
        positions.append([schedule.position.bank, schedule.position.visit])
        schedule.commit(attempted_rollout_id=update, successful=True)
    assert positions == [[bank, 1] for bank in range(200)]
    assert parsed.update_weights_timeout == RolloutConfig.model_fields["update_weights_timeout"].default == 600
    return {"budget": driver.budget, "initial_successful": driver.successful, "start_rollout_id": 0,
            "bank_uses_field": merged.swe_bank_uses, "effective_bank_uses": schedule.uses,
            "successful_bank_visits": len(positions), "distinct_banks": 200, "all_visits": 1,
            "initial_weight_sync_timeout": parsed.update_weights_timeout,
            "profile_enabled": merged.swe_profile_enabled}


def main():
    OUT.mkdir()
    baseline_text = subprocess.check_output(["git", "show", f"{BASE}:{CONFIG}"], text=True)
    current_text = CONFIG.read_text()
    baseline, current = json.loads(baseline_text), json.loads(current_text)
    changed = {key: {"before": baseline[key], "after": current[key]}
               for key in baseline.keys() | current.keys() if baseline.get(key) != current.get(key)}
    assert set(changed) == {"phase", "run_root", "shared_dir"}, changed
    assert current["gpu_tag"] == "H800" and current["charged_group"] == "codesign"
    assert current["phase"] == "full-kl-nll-h800-only-20261111"
    assert Path(current["run_root"]).name == "formal-h800-only-112k-20261111"
    assert Path(current["shared_dir"]).name == "formal-h800-only-112k-20261111"
    assert not Path(current["shared_dir"]).exists(), "New attempt shared root already exists"
    write_new("baseline_config.json", baseline_text)
    write_new("candidate_config.json", current_text)
    write_new("config.diff", "".join(difflib.unified_diff(baseline_text.splitlines(True), current_text.splitlines(True),
                                                         fromfile=f"{BASE}:formal_config.json", tofile="formal_config.json")))
    cases = []
    env = dict(os.environ)
    for pair in ("A", "B"):
        for module, extra, name in (
            ("submit_swe_opd", ["--receipt", str((OUT / f"{pair}-unused-receipt.json").resolve())], "submission"),
            ("run_swe_opd", ["--role", "train"], "native-argv"),
        ):
            command = [sys.executable, "-B", "-m", f"tests.manual.agent_opd.{module}",
                       "--config", str(CONFIG), "--pair", pair, "--protocol", "full", *extra, "--dry-run"]
            result = subprocess.run(command, text=True, capture_output=True, env=env, timeout=60)
            write_new(f"{pair}-{name}.stdout", result.stdout)
            write_new(f"{pair}-{name}.stderr", result.stderr)
            cases.append({"pair": pair, "entry": name, "command": command, "returncode": result.returncode})
            assert result.returncode == 0, result.stderr
        submission = json.loads((OUT / f"{pair}-submission.stdout").read_text())
        assert submission["submitted"] is False and submission["requested_gpus"] == 36
        assert (submission["tasks"]["student"]["replica"], submission["tasks"]["student"]["gpu"]) == (4, 8)
        assert (submission["tasks"]["teacher"]["replica"], submission["tasks"]["teacher"]["gpu"]) == (1, 4)
        assert submission["gpu_policy"]["personal_nonpreemptible_gpus"] is None
        assert "NCCL_SOCKET_IFNAME" not in submission["command"] and "NCCL_IB_HCA" not in submission["command"]
        actual = flags(shlex.split((OUT / f"{pair}-native-argv.stdout").read_text()))
        old = copy.deepcopy(baseline)
        old["protocol"] = "full"
        old_run = Path(old["run_root"]) / "full/student" / pair / "dry-run"
        before = flags(shlex.split(run_swe_opd._training_args(old, pair, "http://teacher:30000/generate", old_run, "dry-run")))
        normalized = {key: [value.replace(current["run_root"], baseline["run_root"]) if isinstance(value, str) else value
                            for value in values] for key, values in actual.items()}
        assert normalized == before, {key for key in normalized.keys() | before.keys() if normalized.get(key) != before.get(key)}
        assert not ({"--save-interval", "--custom-megatron-post-save-hook-path", "--swe-evaluation-configuration",
                     "--load", "--ckpt-step", "--start-rollout-id", "--update-weights-timeout"} & actual.keys())
        contract = formal_contract(pair, actual)
        cases.append({"pair": pair, "entry": "comparison-and-real-formal-contract", "flag_count": len(actual),
                      "all_flags_equal_except_output_root": True, "formal_contract": contract})
    execution = ExecuteTrainConfig(num_nodes=1, run_id="h800-only-cpu-check", output_dir=current["run_root"])
    with patch.dict(os.environ, {"NCCL_SOCKET_IFNAME": "host-nic-must-not-leak", "NCCL_IB_HCA": "host-hca-must-not-leak"}):
        runtime = _runtime_env(execution)
        request = ExecuteTrainRequest(train_args="", num_gpus_per_node=8, megatron_model_type="qwen3.5-4B",
                                      train_script="train.py", train_backend_fsdp=False, extra_env_vars=runtime,
                                      megatron_path=current["megatron_path"], before_ray_job_submit=None,
                                      prepare_cmd={}, extra_manifests=[])
        native_env = train_env_vars(request, {}, config=execution)
    assert "NCCL_SOCKET_IFNAME" not in native_env and "NCCL_IB_HCA" not in native_env
    assert native_env["CUDA_DEVICE_MAX_CONNECTIONS"] == "1"
    write_new("native-environment.json", json.dumps(native_env, indent=2) + "\n")
    lifecycle_paths = ["tests/manual/agent_opd/qwen_alignment.py", "tests/manual/agent_opd/swe_replay.py",
                       "tests/manual/agent_opd/swe_inputs.py", "tests/manual/agent_opd/swe_training.py",
                       "tests/manual/agent_opd/distillation_profile.py", "tests/manual/agent_opd/run_swe_opd.py",
                       "tests/manual/agent_opd/run_qwen35_opd.py", "tests/manual/agent_opd/qwen35_pair_worker.py"]
    result = subprocess.run(["git", "diff", "--exit-code", BASE, "--", *lifecycle_paths], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout
    summary = {"task_id": "profile-h800-only-config-20261111", "baseline_commit": BASE, "status": "PASS",
               "python": sys.version, "working_directory": str(Path.cwd()), "changed_fields": changed,
               "commands_and_checks": cases, "combined_requested_gpus": 72, "hardware": "H800", "charged_group": "codesign",
               "no_host_nccl_nic_hca_forwarding": True, "runtime_unchanged_paths": lifecycle_paths,
               "lifecycle_evidence_reused": str(TASK / "test_report_2026-11-10_formal_configuration.md"),
               "limits": "CPU post-parse schema/driver validation; no native GPU parser, platform admission, mounts, assets, or training"}
    write_new("comparison.json", json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
