"""Boundary and subprocess-status regressions for the SWE paired entrypoint."""

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

from tests.manual.agent_opd import run_swe_opd
from tests.manual.agent_opd.submit_swe_opd import _job_succeeded, _validate_paths
from tests.manual.agent_opd.swe_inputs import BASE_LOADER, TURN_DATA


_LENGTH_LIMITS = {"context_tokens": 131072, "prompt_tokens": 114688, "response_tokens": 16384}


def _recipe_config(profile="integration_config.json"):
    task = Path(__file__).resolve().parents[2] / "task_memory/task_2026-11-08_qwen35_swe_full_r256"
    config = json.loads((task / profile).read_text())
    # Relocate only the in-memory source fixture; archived recipes retain their provenance.
    config["inputs"] = {
        **{name: config["inputs"][name] for name in (
            "source_root", "source_manifest", "chat_template_path", "chat_template_kwargs",
        )},
        "steptron_root": "/fixture/steptron",
        "module_sha256": {BASE_LOADER: "a" * 64, TURN_DATA: "b" * 64},
        "turn_source": "all_assistants",
        "active_conversations": 32,
        "block_turns": 8,
    }
    return config


def _config(tmp_path):
    return {
        **_LENGTH_LIMITS,
        "local_mount": str(tmp_path), "repo": str(tmp_path), "shared_dir": str(tmp_path / "shared"),
        "admission_lock": str(tmp_path / "admission.lock"), "worker_local_root": str(tmp_path / "cache"),
        "run_root": "/mnt/codesign-exp/ycfeng/swe-fixture", "gpu_policy": str(tmp_path / "gpu-policy.json"),
        "pairs": {"A": {"startup_timeout": 60,
                        "student": {"path": "/mnt/codesign-exp/ycfeng/source-student"},
                        "teacher": {"path": "/mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-27B/model"}}},
    }


@pytest.mark.parametrize("field", ["context_tokens", "prompt_tokens", "response_tokens"])
@pytest.mark.parametrize("value", [None, 0, -1, True, 1.5])
def test_length_config_requires_explicit_positive_integers(tmp_path, field, value):
    config = _config(tmp_path)
    config[field] = value
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match=f"{field} must be an explicit positive integer"):
        run_swe_opd._config(path, "A", "full")


@pytest.mark.parametrize("field", ["context_tokens", "prompt_tokens", "response_tokens"])
def test_length_config_never_defaults_missing_limits(tmp_path, field):
    config = _config(tmp_path)
    del config[field]
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match=f"{field} must be an explicit positive integer"):
        run_swe_opd._config(path, "A", "full")


def test_prompt_and_response_budgets_must_fit_context(tmp_path):
    config = _config(tmp_path)
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    resolved = run_swe_opd._config(path, "A", "full")
    assert {name: resolved[name] for name in _LENGTH_LIMITS} == _LENGTH_LIMITS
    config["prompt_tokens"] += 1
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match="prompt_tokens \\+ response_tokens must not exceed context_tokens"):
        run_swe_opd._config(path, "A", "full")


@pytest.mark.parametrize("pair", ["A", "B"])
@pytest.mark.parametrize("protocol", ["full", "r256"])
def test_native_argv_separates_prompt_response_and_context_limits(tmp_path, pair, protocol):
    from miles.utils.args.runtime import AllConfig

    config = _recipe_config()
    config.update(_LENGTH_LIMITS, protocol=protocol)
    argv = shlex.split(run_swe_opd._training_args(config, pair, "http://teacher/generate", tmp_path, "lengths"))
    expected = {
        "--rollout-max-prompt-len": "114688",
        "--rollout-max-response-len": "16384",
        "--rollout-max-context-len": "131072",
        "--seq-length": "131072",
        "--sglang-context-length": "131072",
        "--swe-context-tokens": "131072",
    }
    for flag, value in expected.items():
        assert argv.count(flag) == 1 and argv[argv.index(flag) + 1] == value
    assert "--rollout-max-response-len 131072" not in shlex.join(argv)
    parser = argparse.ArgumentParser(add_help=False)
    AllConfig.add_arguments(parser)
    parsed, unknown = parser.parse_known_args(argv)
    assert parsed.rollout_max_prompt_len == config["prompt_tokens"]
    assert parsed.rollout_max_response_len == config["response_tokens"]
    assert parsed.rollout_max_context_len == parsed.sglang_context_length == config["context_tokens"]
    assert not any(flag in unknown for flag in expected if flag not in ("--seq-length", "--swe-context-tokens"))


def test_worker_dry_run_emits_explicit_limits_without_native_execution(tmp_path):
    config = _recipe_config()
    # Keep the archived recipe's full resource/model shapes while relocating only local paths.
    config.update(_config(tmp_path) | {"pairs": config["pairs"]})
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    result = subprocess.run(
        [sys.executable, "-m", "tests.manual.agent_opd.run_swe_opd", "--config", str(path),
         "--pair", "A", "--protocol", "full", "--role", "student", "--dry-run"],
        check=True, capture_output=True, text=True,
    )
    argv = shlex.split(result.stdout)
    assert argv.count("--rollout-max-prompt-len") == argv.count("--rollout-max-response-len") == 1
    assert argv[argv.index("--rollout-max-prompt-len") + 1] == "114688"
    assert argv[argv.index("--rollout-max-response-len") + 1] == "16384"
    assert "--rollout-max-response-len 131072" not in result.stdout


@pytest.mark.parametrize("field", ["shared_dir", "repo", "admission_lock", "worker_local_root", "gpu_policy"])
def test_cloud_paths_fail_before_any_submission(tmp_path, field):
    config = _config(tmp_path)
    config[field] = "/mnt/codesign-exp/another-user/receipts"
    with pytest.raises(ValueError):
        _validate_paths(config, tmp_path / "config.json")


def test_resolved_shared_path_must_stay_in_the_mount(tmp_path):
    config = _config(tmp_path)
    alias = tmp_path / "shared-alias"
    alias.symlink_to("/mnt/codesign-exp/another-user")
    config["shared_dir"] = str(alias)
    with pytest.raises(ValueError, match="resolve under"):
        _validate_paths(config, tmp_path / "config.json")


@pytest.mark.parametrize("role,expected", [("student", 137), ("teacher", 23)])
def test_cli_preserves_child_failure_status(tmp_path, monkeypatch, role, expected):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(_config(tmp_path)))
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", "fixture-job")
    monkeypatch.setenv("KUBEBRAIN_REPLICA", "0")
    monkeypatch.setattr(sys, "argv", ["run_swe_opd", "--config", str(path), "--pair", "A",
                                      "--protocol", "full", "--role", role])
    monkeypatch.setattr(run_swe_opd.signal, "signal", lambda *args: None)
    monkeypatch.setattr(run_swe_opd.paired, "_run_student", lambda *args, **kwargs: -9)

    def teacher(*args):
        raise subprocess.CalledProcessError(23, "native-teacher")

    monkeypatch.setattr(run_swe_opd.paired, "_run_teacher", teacher)
    assert run_swe_opd.main() == expected


@pytest.mark.parametrize(
    "phase,reason,student,expected",
    [
        ("Succeeded", None, {"succeeded": 1}, True),
        ("Stopped", "All critical tasks are finished.", {"succeeded": 1}, True),
        ("Stopped", "All critical tasks are finished.", {"failed": 1}, False),
        ("Stopped", "All critical tasks are finished.", {"running": 1}, False),
        ("Stopped", "Some critical tasks failed.", {"failed": 1}, False),
        ("Stopped", None, {"succeeded": 1}, False),
        ("Failed", "All critical tasks are finished.", {"succeeded": 1}, False),
    ],
)
def test_platform_critical_completion_is_not_a_training_failure(phase, reason, student, expected):
    job = {
        "metadata": {"annotations": {"rjob.brainpp.cn/system-stop-reason": reason}},
        "status": {"phase": phase, "taskStatuses": {"student": student, "teacher": {"stopped": 1}}},
    }
    tasks = {"student": {"is_critical": True, "replica": 1}, "teacher": {"is_critical": False, "replica": 1}}
    assert _job_succeeded(job, tasks) is expected


def test_partial_critical_replica_completion_remains_failed():
    job = {
        "metadata": {"annotations": {"rjob.brainpp.cn/system-stop-reason": "All critical tasks are finished."}},
        "status": {"phase": "Stopped", "taskStatuses": {"student": {"succeeded": 1, "stopped": 1}}},
    }
    assert not _job_succeeded(job, {"student": {"is_critical": True, "replica": 2}})


@pytest.mark.parametrize("turn_source", ["all_assistants", "loss_masked"])
def test_native_input_policy_reaches_registered_source_config(tmp_path, monkeypatch, turn_source):
    from miles.utils.args import custom_function
    from miles.utils.args.runtime import AllConfig

    config = _recipe_config()
    config.update(_LENGTH_LIMITS, protocol="r256")
    config["inputs"]["turn_source"] = turn_source
    argv = shlex.split(run_swe_opd._training_args(config, "A", "http://teacher/generate", tmp_path, "input-policy"))
    parser = argparse.ArgumentParser(add_help=False)
    AllConfig.add_arguments(parser)
    monkeypatch.setattr(sys, "argv", ["train.py", *argv])
    custom_function.add_user_provided_function_arguments(parser, config_class=AllConfig)
    parsed, unknown = parser.parse_known_args(argv)
    assert not any(value.startswith("--swe-") for value in unknown)
    custom_function.resolve_custom_function_configs(parsed, config_class=AllConfig)
    source = parsed.data_source_path.config
    source_fields = source.model_dump()
    for name in (
        "source_root", "source_manifest", "steptron_root", "module_sha256",
        "turn_source", "active_conversations", "block_turns",
    ):
        assert source_fields[f"swe_{name}"] == config["inputs"][name]
    assert source.swe_turn_source == turn_source
    assert source.swe_active_conversations == 32 and source.swe_block_turns == 8
    assert not any(flag in argv for flag in (
        "--swe-native-loader-path", "--swe-native-loader-sha256",
        "--swe-skip-masked-assistant-turns", "--swe-visual-filter-receipt",
    ))


@pytest.mark.parametrize("field", ["steptron_root", "module_sha256", "turn_source", "active_conversations", "block_turns"])
def test_native_input_recipe_requires_explicit_source_fields(tmp_path, field):
    config = _recipe_config()
    config.update(_LENGTH_LIMITS, protocol="r256")
    del config["inputs"][field]
    with pytest.raises(KeyError, match=field):
        run_swe_opd._training_args(config, "A", "http://teacher/generate", tmp_path, "missing-source-field")


@pytest.mark.parametrize("policy", [None, "round_robin"])
def test_native_router_policy_preserves_default_and_typed_transport(tmp_path, monkeypatch, policy):
    from tests.fast.test_swe_replay import _typed_swe_config

    from miles.backends.sglang_utils.router_args_utils import (
        compute_sglang_router_args,
        parse_router_args_argv,
        router_args_to_argv,
    )
    from miles.utils.args import custom_function
    from miles.utils.args.configs.router import RouterConfig
    from miles.utils.args.runtime import AllConfig, OrchestratorConfig
    from miles.utils.arguments import get_miles_extra_args_provider

    config = _recipe_config("deepswe_capacity_smoke_config.json")
    config.update(_LENGTH_LIMITS, protocol="r256")
    baseline = shlex.split(
        run_swe_opd._training_args(config, "A", "http://teacher/generate", tmp_path, "router-policy")
    )
    assert "--router-policy" not in baseline
    assert "--sglang-router-policy" not in baseline
    config["router_policy"] = policy
    argv = shlex.split(run_swe_opd._training_args(config, "A", "http://teacher/generate", tmp_path, "router-policy"))
    if policy is None:
        assert argv == baseline
    else:
        assert argv.count("--router-policy") == 1
        index = argv.index("--router-policy")
        assert argv[index + 1] == policy
        assert argv[:index] + argv[index + 2 :] == baseline
    assert "--sglang-router-policy" not in argv

    monkeypatch.setattr(sys, "argv", ["train.py", *argv])
    parser = argparse.ArgumentParser()
    get_miles_extra_args_provider()(parser)
    parsed, unknown = parser.parse_known_args(argv)
    assert not any(value.startswith(("--router-", "--swe-", "--scoring-lifetime-", "--tis-")) for value in unknown)
    custom_function.resolve_custom_function_configs(parsed)
    monkeypatch.setattr(sys, "argv", ["test"])
    typed = _typed_swe_config("r256", run_kind="smoke")
    typed = AllConfig.model_validate(
        typed.model_dump(mode="python")
        | RouterConfig.from_args(parsed)
        | {
            "sglang_router_policy": parsed.sglang_router_policy,
        }
    )
    orchestrator = OrchestratorConfig.slice_from(typed)
    restored = OrchestratorConfig.model_validate_json(orchestrator.model_dump_json())
    expected = "cache_aware" if policy is None else policy
    assert restored.router_args["policy"] == expected
    assert restored.sglang_router_policy is None
    router = compute_sglang_router_args(
        restored,
        host="127.0.0.1",
        port=30000,
        prometheus_port=30001,
        has_pd_disaggregation=False,
    )
    assert parse_router_args_argv(router_args_to_argv(router)).policy == expected


def test_expanded_student_bootstrap_transports_node_preflight(tmp_path, monkeypatch):
    config = _recipe_config("deepswe_capacity_expanded_config.json")
    config["startup_timeout"] = config["pairs"]["A"]["startup_timeout"]
    calls = []
    monkeypatch.setattr(run_swe_opd.native, "_run", lambda args, **kwargs: calls.append((args, kwargs)))
    run_swe_opd._train(config, "A", "http://teacher/generate")
    args, callbacks = calls[0]
    assert args.student_nodes == 2 and args.gpus_per_node == 8
    assert callbacks["prepare_training"] is run_swe_opd._prepare_training
    assert callbacks["prepare_node"] is run_swe_opd._prepare_node


@pytest.mark.parametrize("nodes,rank", [(1, 0), (2, 0), (2, 1)])
def test_scoring_source_preflight_runs_in_each_container(tmp_path, monkeypatch, nodes, rank):
    from types import SimpleNamespace

    config = {"image": "pinned-image", "training": {"release_scoring_output": True}}
    args = SimpleNamespace(swe_config=config, student_nodes=nodes, megatron_path=str(tmp_path / "Megatron-LM"))
    calls = []
    source = {"source_sha256": "verified-source"}
    monkeypatch.setattr(
        run_swe_opd.megatron_scoring_lifetime, "prepare_source",
        lambda path, **kwargs: calls.append((path, kwargs)) or source,
    )
    receipt = run_swe_opd._prepare_node(args, tmp_path / "run", rank)
    archive = tmp_path / "run/megatron_scoring_lifetime/source"
    if nodes == 2:
        archive /= f"rank-{rank}"
    assert calls == [(Path(args.megatron_path), {"image": "pinned-image", "release": True, "archive_dir": archive})]
    assert receipt == {"megatron_scoring_lifetime": source}


def test_expanded_rollout_recipe_preserves_eight_gpu_training(tmp_path, monkeypatch):
    from miles.utils.args import custom_function
    from miles.utils.arguments import get_miles_extra_args_provider

    config = _recipe_config("deepswe_capacity_expanded_config.json")
    config.update(_LENGTH_LIMITS, protocol="r256")
    argv = shlex.split(run_swe_opd._training_args(config, "A", "http://teacher/generate", tmp_path, "expanded"))
    for flag, value in {
        "--actor-num-nodes": "1",
        "--actor-num-gpus-per-node": "8",
        "--tensor-model-parallel-size": "2",
        "--context-parallel-size": "1",
        "--rollout-num-gpus": "16",
        "--sglang-config": config["sglang_config"],
    }.items():
        assert argv.count(flag) == 1
        assert argv[argv.index(flag) + 1] == value
    monkeypatch.setattr(sys, "argv", ["train.py", *argv])
    parser = argparse.ArgumentParser()
    get_miles_extra_args_provider()(parser)
    parsed, unknown = parser.parse_known_args(argv)
    assert "--rollout-num-gpus" not in unknown and "--sglang-config" not in unknown
    custom_function.resolve_custom_function_configs(parsed)
    assert parsed.rollout_num_gpus == 16
    assert parsed.sglang_config == config["sglang_config"]
    assert config["pairs"]["A"]["student"]["nodes"] == 2


@pytest.mark.parametrize(
    "profile",
    [
        "deepswe_capacity_smoke_config.json",
        "deepswe_capacity_round_robin_config.json",
        "deepswe_capacity_expanded_config.json",
        "deepswe_formal_config.json",
    ],
)
async def test_native_recipe_timeout_reaches_the_typed_qwen_generation_hook(tmp_path, monkeypatch, profile):
    import asyncio

    import httpx
    from tests.fast.test_qwen35_sample_lifecycle import _input
    from tests.fast.test_swe_replay import _typed_swe_config

    from miles.ray.rollout.rollout_executor import _compute_rollout_function_config
    from miles.rollout.base_types import GenerateFnInput
    from miles.rollout.generate_hub import single_turn
    from miles.rollout.inference_rollout import inference_rollout_common
    from miles.utils import http_utils
    from miles.utils.args import custom_function
    from miles.utils.args.custom_view import ImmutableNamespace
    from miles.utils.args.runtime import AllConfig, RolloutConfig
    from miles.utils.arguments import get_miles_extra_args_provider

    config = _recipe_config(profile)
    config.update(_LENGTH_LIMITS, protocol="r256")
    argv = shlex.split(run_swe_opd._training_args(config, "A", "http://teacher/generate", tmp_path, "timeout"))
    monkeypatch.setattr(sys, "argv", ["train.py", *argv])
    parser = argparse.ArgumentParser()
    get_miles_extra_args_provider()(parser)
    parsed, unknown = parser.parse_known_args(argv)
    assert "--sglang-router-request-timeout-secs" not in unknown
    custom_function.resolve_custom_function_configs(parsed)
    assert parsed.custom_generate_function_path.path == "tests.manual.agent_opd.qwen_alignment.generate"
    assert (
        parsed.rollout_function_path.config.swe_acquisition_seconds
        == config["training"]["acquisition_seconds"]
        == 1800
    )

    monkeypatch.setattr(sys, "argv", ["test"])
    template = _typed_swe_config("r256")
    typed = AllConfig.model_validate(
        template.model_dump(mode="python")
        | {
            "custom_generate_function_path": parsed.custom_generate_function_path,
            "sglang_router_request_timeout_secs": parsed.sglang_router_request_timeout_secs,
        }
    )
    rollout = RolloutConfig.slice_from(typed)
    restored = RolloutConfig.model_validate_json(rollout.model_dump_json())
    # Router startup resolves these mutable addresses before the rollout worker runs.
    restored.sglang_router_ip = "student"
    restored.sglang_router_port = 30002
    args = _compute_rollout_function_config(restored, restored.rollout_function_path)
    assert args.sglang_router_request_timeout_secs == config["request_timeout"] == 3600

    example = _input()
    tokenizer = example.state.tokenizer
    monkeypatch.setattr(inference_rollout_common, "load_tokenizer", lambda *args, **kwargs: tokenizer)
    monkeypatch.setattr(inference_rollout_common, "load_processor", lambda *args, **kwargs: None)
    monkeypatch.setattr(single_turn, "compute_routing_headers", lambda args, sample: {})
    state = inference_rollout_common.GenerateState(args)
    from tests.manual.agent_opd import qwen_alignment

    assert state.generate_function is qwen_alignment.generate
    loop = asyncio.get_running_loop()
    time = loop.time
    elapsed = 0
    monkeypatch.setattr(loop, "time", lambda: time() + elapsed)
    entered, cancelled = asyncio.Event(), asyncio.Event()

    async def stalled(request):
        nonlocal elapsed
        entered.set()
        elapsed += config["request_timeout"] + 1
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    input = GenerateFnInput(
        state=state, sample=example.sample, sampling_params=example.sampling_params, evaluation=True
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(stalled), timeout=None) as client:
        monkeypatch.setattr(http_utils, "_rollout_client", lambda: client)
        with pytest.raises(TimeoutError):
            await state.generate_function(input)
    assert entered.is_set() and cancelled.is_set()
    assert isinstance(state.args, ImmutableNamespace)


@pytest.mark.parametrize("enabled", [False, True])
def test_profile_object_reaches_native_custom_schema_without_unused_keys(tmp_path, monkeypatch, enabled):
    from miles.utils.args import custom_function
    from miles.utils.args.runtime import AllConfig

    config = _recipe_config()
    config.update(_LENGTH_LIMITS, protocol="full", profile={
        "enabled": enabled, "trend_window": 3, "baseline_updates": 4, "baseline_turns": 5,
    })
    argv = shlex.split(run_swe_opd._training_args(config, "A", "http://teacher/generate", tmp_path, "profile"))
    assert ("--swe-profile-enabled" in argv) is enabled
    assert "--profile" not in argv
    for name in ("trend_window", "baseline_updates", "baseline_turns"):
        flag = "--swe-profile-" + name.replace("_", "-")
        assert argv.count(flag) == 1 and argv[argv.index(flag) + 1] == str(config["profile"][name])
    parser = argparse.ArgumentParser(add_help=False)
    AllConfig.add_arguments(parser)
    monkeypatch.setattr(sys, "argv", ["train.py", *argv])
    custom_function.add_user_provided_function_arguments(parser, config_class=AllConfig)
    parsed, unknown = parser.parse_known_args(argv)
    assert not any(value.startswith("--swe-profile") for value in unknown)
    custom_function.resolve_custom_function_configs(parsed, config_class=AllConfig)
    for name in ("rollout_function_path", "custom_rm_path", "custom_megatron_optimizer_step_hook_path"):
        profile = getattr(parsed, name).config
        assert profile.swe_profile_enabled is enabled
        assert (profile.swe_profile_trend_window, profile.swe_profile_baseline_updates, profile.swe_profile_baseline_turns) == (3, 4, 5)
        assert type(profile).model_validate_json(profile.model_dump_json()) == profile


@pytest.mark.parametrize("profile", [None, [], {}, {"enabled": True, "unused": 5}, {"trend_window": 3},
                                    {"enabled": "true"}, {"enabled": 1}, {"enabled": True, "trend_window": 0},
                                    {"enabled": True, "baseline_updates": 1.5},
                                    {"enabled": True, "baseline_turns": True}])
def test_launcher_rejects_invalid_or_silent_unused_profile_blocks(tmp_path, profile):
    config = _config(tmp_path) | {"profile": profile}
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError):
        run_swe_opd._config(path, "A", "full")


def test_reused_launcher_profile_default_remains_disabled(tmp_path, monkeypatch):
    from miles.utils.args import custom_function
    from miles.utils.args.runtime import AllConfig

    config = _recipe_config()
    config.update(_LENGTH_LIMITS, protocol="r256")
    argv = shlex.split(run_swe_opd._training_args(config, "A", "http://teacher/generate", tmp_path, "no-profile"))
    assert not any(flag.startswith("--swe-profile") for flag in argv)
    parser = argparse.ArgumentParser(add_help=False)
    AllConfig.add_arguments(parser)
    monkeypatch.setattr(sys, "argv", ["train.py", *argv])
    custom_function.add_user_provided_function_arguments(parser, config_class=AllConfig)
    parsed, _ = parser.parse_known_args(argv)
    custom_function.resolve_custom_function_configs(parsed, config_class=AllConfig)
    assert parsed.rollout_function_path.config.swe_profile_enabled is False
