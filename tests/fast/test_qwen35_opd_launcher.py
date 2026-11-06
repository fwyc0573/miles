"""CPU regressions for native Qwen three-pair launch and sampled-token provenance."""

import argparse
import ast
import asyncio
import copy
import dataclasses
import hashlib
import importlib.util
import json
import logging
import math
import os
import shlex
import sys
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Optional, TypedDict

import pytest
import torch
from examples.agentic_opd.glm_turns import token_hash
from examples.agentic_opd.rollout import post_process_rewards
from examples.infra_features.train_infer_mismatch_helper.mis import MisConfig
from tests.fast.fixtures.args_fixtures import parser_defaults
from tests.fast.backends.megatron_utils.score_rpc_fixtures import (
    ScoreModel,
    _execute_nodes,
    make_args as scoring_args,
    make_raw_data,
)
from tests.fast.backends.megatron_utils.test_score_log_probs import scoring
from tests.fast.test_train import _install_driver_fakes, _make_args as driver_args, _startup_info, train_driver
from tests.fast.test_qwen35_monitoring import _fault_run, native_fixture, native_run
from tests.manual.agent_opd import alignment, inspect_qwen35 as inspector
from tests.manual.agent_opd import qwen_alignment, run_qwen35_opd as launcher

from miles.utils.args.configs.algo import AlgoConfig
from miles.utils.args.configs.data import DataConfig
from miles.utils.args.configs.eval import EvalConfig
from miles.utils.arguments import (
    _resolve_sample_ownership_check,
    _validate_rematerialize_param_from_master_weight,
    get_miles_extra_args_provider,
    validate_eval_train_log_probs,
)
from miles.utils.args.runtime import TrainerConfig
from miles.utils.async_utils import with_disposer
from miles.ray.rollout.train_data_conversion import ROLLOUT_DATA_VALUE_SPEC
from miles.utils.lora.utils import is_lora_enabled, is_multi_lora_enabled
from miles.rollout.base_types import GenerateFnInput
from miles.rollout.generate_hub import single_turn
from miles.utils.external_utils.command_utils import ExecuteTrainConfig
from miles.utils.external_utils.command_utils.base_backend import BaseCommandBackend
from miles.utils.external_utils.command_utils.ray_backend import backend as ray_backend
from miles.utils.types import Sample


def _args(pair="A", *extra):
    student, teacher = launcher._PAIRS[pair]
    args = launcher._parser().parse_args([
        "--pair", pair, "--student", f"/mnt/codesign-exp/ycfeng/models/{student}",
        "--teacher", f"/mnt/codesign-exp/ycfeng/models/{teacher}",
        "--teacher-url", "http://teacher:30000/generate",
        "--population-dir", "/mnt/codesign-exp/ycfeng/qwen35/population",
        "--output-root", "/mnt/codesign-exp/ycfeng/qwen35/runs", "--shared-dir", "/data/ycfeng/qwen35/records",
        "--gpus-per-node", "8", "--student-engine-gpus", "4" if pair == "C" else "2",
        "--max-tokens-per-gpu", "131072", "--sglang-mem-fraction-static", "0.5",
        "--sglang-max-running-requests", "8", "--sglang-chunked-prefill-size", "8192",
        "--sglang-router-request-timeout-secs", "3600", *extra,
    ])
    launcher._validate_args(args)
    return args


def _flags(argv):
    values = {}
    current = None
    for token in argv:
        if token.startswith("--"):
            current = token
            assert token not in values, f"Duplicate launch flag: {token}"
            values[token] = []
        else:
            assert current is not None
            values[current].append(token)
    return values


@pytest.mark.parametrize("pair,tp,layers,offload", [("A", 2, 32, False), ("B", 2, 32, False), ("C", 4, 64, True)])
def test_native_command_utils_composes_full_student_and_external_teacher(monkeypatch, pair, tp, layers, offload):
    args = _args(pair)
    run = args.output_root / pair / "test"
    train_args = launcher._training_args(args, run)
    commands, submissions = [], []
    monkeypatch.setenv("MILES_SCRIPT_EXTERNAL_RAY", "1")
    monkeypatch.setenv("MILES_SCRIPT_ENABLE_RAY_SUBMIT", "1")
    monkeypatch.setattr(BaseCommandBackend, "exec_command_cpu", lambda self, cmd, **kwargs: commands.append(cmd))
    monkeypatch.setattr(ray_backend.RayCommandBackend, "_ray_env_vars", lambda self, **kwargs: {})
    monkeypatch.setattr(ray_backend, "run_ray_job", lambda **kwargs: submissions.append(kwargs))
    config = ExecuteTrainConfig(num_nodes=1, output_dir=str(run), run_id="test")
    config.create_backend().execute_train(
        train_args=train_args, num_gpus_per_node=8,
        megatron_model_type=launcher.DenseArgs(model_name=launcher._PAIRS[pair][0]).recipe.megatron_model_type,
        extra_env_vars={"NCCL_SOCKET_IFNAME": "platform-nic"},
    )
    assert len(submissions) == 1
    submission = submissions[0]
    argv = shlex.split(submission["entrypoint"])
    assert argv[0] == "python3" and argv[1].endswith("/train.py")
    flags = _flags(argv[2:])
    expected = {
        "--num-layers": str(layers), "--tensor-model-parallel-size": str(tp),
        "--context-parallel-size": "1", "--hf-checkpoint": str(args.student), "--ref-load": str(args.student),
        "--rm-url": args.teacher_url, "--num-rollout": "100", "--rollout-batch-size": "8",
        "--n-samples-per-prompt": "1", "--global-batch-size": "8", "--max-tokens-per-gpu": "131072",
        "--rollout-max-context-len": "131072", "--rollout-max-response-len": "8192",
        "--sglang-context-length": "131072", "--eval-max-context-len": "131072", "--eval-max-response-len": "8192",
        "--rollout-temperature": "1", "--eval-temperature": "1", "--rollout-top-p": "1", "--eval-top-p": "1",
        "--rollout-top-k": "-1", "--eval-top-k": "-1", "--rollout-seed": "42", "--seed": "42",
        "--eval-interval": "20", "--n-samples-per-eval-prompt": "1", "--save-interval": "100",
        "--custom-megatron-post-save-hook-path": "tests.manual.agent_opd.qwen_export.post_save",
        "--save-hf": str(run / "hf" / "step_{rollout_id}"),
        "--optimizer": "adam", "--lr": "2e-6", "--lr-decay-style": "constant", "--lr-warmup-iters": "0",
        "--weight-decay": "0", "--adam-beta1": "0.9", "--adam-beta2": "0.98",
        "--opd-log-prob-top-k": "0", "--opd-kl-coef": "1", "--tis-level": "token", "--tis-mode": "mask",
        "--tis-lower-bound": "0.5", "--tis-upper-bound": "2", "--eps-clip": "0.2", "--eps-clip-high": "0.28",
        "--entropy-coef": "0", "--num-gpus-per-node": "8", "--actor-num-gpus-per-node": "8",
    }
    for flag, value in expected.items():
        assert flags[flag] == [value]
    assert flags["--eval-prompt-data"] == ["monitor", str(args.population_dir / "monitor.jsonl")]
    for flag in ("--rollout-shuffle", "--eval-train-log-probs", "--colocate", "--offload-train", "--offload-rollout", "--use-tis", "--calculate-per-token-loss"):
        assert flags[flag] == []
    for flag in ("--sglang-config", "--rollout-num-gpus", "--save", "--load", "--apply-chat-template", "--eval-hf-dir", "--eval-num-gpus", "--use-rollout-routing-replay", "--use-rs", "--tis-batch-normalize", "--normalize-advantages"):
        assert flag not in flags
    assert ("--optimizer-cpu-offload" in flags) == offload
    assert str(args.teacher) not in argv
    assert submission["runtime_env"]["env_vars"]["NCCL_SOCKET_IFNAME"] == "platform-nic"
    assert all("ray start" not in command for command in commands)


def test_required_capacity_inputs_have_no_inherited_token_default():
    parser = launcher._parser()
    action = next(action for action in parser._actions if action.dest == "max_tokens_per_gpu")
    assert action.required and action.default is None
    assert "--micro-batch-size" not in launcher._training_args(_args(), Path("/run"))


def test_native_false_defaults_and_baseline_eval_are_verified_not_guessed():
    parser = argparse.ArgumentParser()
    for cls in (MisConfig, AlgoConfig, DataConfig, EvalConfig):
        cls.add_arguments(parser)
    flags = _flags(shlex.split(launcher._training_args(_args(), Path("/run"))))
    known_options = parser._option_string_actions
    subset = [token for flag, values in flags.items() if flag in known_options for token in (flag, *values)]
    parsed = parser.parse_args(subset)
    assert parsed.use_rs is False and parsed.tis_batch_normalize is False
    assert parsed.tis_mode == "mask" and parsed.tis_level == "token"
    assert parsed.use_rollout_logprobs is False and parsed.normalize_advantages is False
    assert parsed.skip_eval_before_train is False and parsed.apply_chat_template is False
    assert parsed.eval_train_log_probs is True


def test_native_parser_accepts_sglang_and_custom_mis_flags(monkeypatch):
    argv = shlex.split(launcher._training_args(_args("C"), Path("/run")))
    monkeypatch.setattr(sys, "argv", ["train.py", *argv])
    parser = argparse.ArgumentParser()
    get_miles_extra_args_provider()(parser)
    parsed, unknown = parser.parse_known_args(argv)
    # Megatron's own parser is absent in the CPU environment. Every remaining
    # option belongs to that parser, not an unregistered launcher/scorer flag.
    assert set(_flags(unknown)) == {
        "--tensor-model-parallel-size", "--sequence-parallel", "--pipeline-model-parallel-size",
        "--context-parallel-size", "--expert-model-parallel-size", "--expert-tensor-parallel-size",
        "--recompute-granularity", "--recompute-method", "--recompute-num-layers", "--seq-length",
        "--optimizer", "--lr-decay-style", "--lr-warmup-iters", "--weight-decay", "--adam-beta1", "--adam-beta2",
        "--optimizer-cpu-offload", "--overlap-cpu-optimizer-d2h-h2d", "--use-precision-aware-optimizer",
        "--attention-dropout", "--hidden-dropout", "--accumulate-allreduce-grads-in-fp32",
        "--attention-softmax-in-fp32", "--attention-backend",
    }
    assert parsed.sglang_router_request_timeout_secs == 3600
    assert parsed.sglang_context_length == 131072
    assert parsed.tis_mode == "mask" and parsed.use_rs is False and parsed.tis_batch_normalize is False
    assert parsed.eval_train_log_probs is True


def test_zero_rollouts_uses_native_eval_without_any_save():
    flags = _flags(shlex.split(launcher._training_args(_args("A", "--num-rollout", "0"), Path("/run"))))
    assert flags["--num-rollout"] == ["0"]
    assert flags["--eval-interval"] == ["20"] and "--eval-train-log-probs" in flags
    assert not any(flag.startswith("--save") and "debug" not in flag for flag in flags)
    assert "--custom-megatron-post-save-hook-path" not in flags


@pytest.fixture
def native_model_setup():
    """Execute native setup/scheduling, replacing only GPU model/optimizer factories.

    MEGATRON_PATH can name a read-only reference checkout when this CPU Python
    does not have Megatron installed. No imports from that environment are used.
    """
    if "MEGATRON_PATH" in os.environ:
        package = Path(os.environ["MEGATRON_PATH"]) / "megatron"
    else:
        spec = importlib.util.find_spec("megatron")
        if spec is None:
            pytest.skip("Native scheduler source requires Megatron or read-only MEGATRON_PATH")
        package = Path(next(iter(spec.submodule_search_locations)))
    scheduler_path = package / "core/optimizer_param_scheduler.py"
    namespace = dict(
        torch=torch, math=math, logging=logging, Any=Any, Optional=Optional, TypedDict=TypedDict,
        logger=logging.getLogger(__name__), log_single_rank=lambda *args, **kwargs: None,
    )
    # The real constructor must enforce lr_decay_steps > 0, not a test imitation.
    names = {node.name for node in ast.parse(scheduler_path.read_text()).body
             if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    _execute_nodes(scheduler_path, names, namespace)
    model = [ScoreModel()]
    optimizers = []
    def create_optimizer(*, config, **kwargs):
        optimizer = torch.optim.Adam(model[0].parameters(), lr=config.lr,
                                     betas=(config.adam_beta1, config.adam_beta2), weight_decay=config.weight_decay)
        optimizers.append(optimizer)
        return optimizer
    namespace.update(
        TrainerConfig=TrainerConfig, DDP=ScoreModel, MegatronOptimizer=torch.optim.Optimizer,
        dataclasses=dataclasses,
        OptimizerConfig=dataclasses.make_dataclass("CpuOptimizerConfig", [
            ("optimizer", str), ("lr", float), ("adam_beta1", float), ("adam_beta2", float), ("weight_decay", float),
        ]),
        ModelType=SimpleNamespace(encoder_or_decoder=object()),
        is_lora_enabled=is_lora_enabled, is_multi_lora_enabled=is_multi_lora_enabled,
        get_model_provider_func=lambda args, role: object(), get_model=lambda *args: model,
        is_first_replica_megatron_main_rank=lambda: False, get_megatron_optimizer=create_optimizer,
    )
    _execute_nodes(Path(launcher.U.repo_base_dir) / "miles/backends/megatron_utils/model.py",
                   {"setup_model_and_optimizer", "get_optimizer_param_scheduler", "_is_muon_optimizer"}, namespace)
    return SimpleNamespace(setup=namespace["setup_model_and_optimizer"], model=model, optimizers=optimizers)


def _setup_args_from_launcher(monkeypatch, pair, num_rollout):
    argv = shlex.split(launcher._training_args(_args(pair, "--num-rollout", str(num_rollout)), Path("/run")))
    monkeypatch.setattr(sys, "argv", ["train.py", *argv])
    parser = argparse.ArgumentParser()
    get_miles_extra_args_provider()(parser)
    # Project only scheduler/optimizer inputs from actual launcher output. The
    # full Megatron model parser needs CUDA-only dependencies absent on this host.
    for name in ("optimizer", "lr-decay-style"):
        parser.add_argument(f"--{name}")
    for name in ("lr-warmup-iters", "lr-decay-iters"):
        parser.add_argument(f"--{name}", type=int)
    for name in ("weight-decay", "adam-beta1", "adam-beta2"):
        parser.add_argument(f"--{name}", type=float)
    parsed, _ = parser.parse_known_args(argv)
    backend = SimpleNamespace(
        optimizer=parsed.optimizer, lr=parsed.lr, adam_beta1=parsed.adam_beta1, adam_beta2=parsed.adam_beta2,
        weight_decay=parsed.weight_decay, global_batch_size=parsed.global_batch_size,
        train_iters=None, lr_decay_iters=parsed.lr_decay_iters, lr_decay_style=parsed.lr_decay_style,
        lr_warmup_iters=parsed.lr_warmup_iters, lr_warmup_init=0, lr_warmup_fraction=None,
        min_lr=0, lr_wsd_decay_iters=None, lr_wsd_decay_style=None,
        start_weight_decay=parsed.weight_decay, end_weight_decay=parsed.weight_decay,
        weight_decay_incr_style="constant", use_checkpoint_opt_param_scheduler=True,
        override_opt_param_scheduler=False, moe_use_upcycling=False, use_gloo_process_groups=False,
        mutable=nullcontext,
    )
    values = parser_defaults() | vars(parsed)
    trainer = TrainerConfig.model_construct(**(values | {"backend": backend}))
    return trainer, SimpleNamespace(**(dict(trainer) | values))


@pytest.mark.parametrize("pair", ["A", "B", "C"])
@pytest.mark.parametrize("num_rollout", [0, 100])
def test_native_setup_for_baseline_or_formal_budget(monkeypatch, native_model_setup, pair, num_rollout):
    args, validation_args = _setup_args_from_launcher(monkeypatch, pair, num_rollout)
    _resolve_sample_ownership_check(validation_args)
    _validate_rematerialize_param_from_master_weight(validation_args)
    validate_eval_train_log_probs(validation_args)
    assert validation_args.enable_sample_ownership_checker is False
    assert validation_args.rematerialize_param_from_master_weight is False
    arguments_path = Path(launcher.U.repo_base_dir) / "miles/utils/arguments.py"
    disable_optimizer_loading = next(
        node for node in ast.walk(ast.parse(arguments_path.read_text()))
        if isinstance(node, ast.If) and isinstance(node.test, ast.Attribute)
        and isinstance(node.test.value, ast.Name) and node.test.value.id == "args"
        and node.test.attr == "debug_disable_optimizer"
    )
    exec(compile(ast.Module(body=[disable_optimizer_loading], type_ignores=[]), str(arguments_path), "exec"),
         {"args": validation_args})
    before = native_model_setup.model[0].weight.detach().clone()
    model, optimizer, scheduler = native_model_setup.setup(args)
    assert model is native_model_setup.model and model[0].lora_attached is False
    torch.testing.assert_close(model[0].weight, before, rtol=0, atol=0)
    assert args.num_rollout == num_rollout
    if num_rollout == 0:
        assert validation_args.no_load_optim is True and validation_args.no_save_optim is True
        assert optimizer is scheduler is None
        assert native_model_setup.optimizers == []
        assert args.backend.train_iters is None and args.backend.lr_decay_iters is None
    else:
        assert optimizer is native_model_setup.optimizers[0]
        assert scheduler.optimizer is optimizer
        assert args.backend.train_iters == args.backend.lr_decay_iters == 100
        assert scheduler.lr_decay_steps == scheduler.wd_incr_steps == 800
        assert scheduler.max_lr == 2e-6 and scheduler.lr_decay_style == "constant" and scheduler.lr_warmup_steps == 0
        assert optimizer.param_groups[0]["betas"] == (0.9, 0.98)
        assert optimizer.param_groups[0]["weight_decay"] == 0 and len(optimizer.state) == 0


@pytest.mark.parametrize("pair", ["A", "B", "C"])
@pytest.mark.parametrize("asleep", [False, True])
def test_baseline_native_scoring_needs_no_optimizer(monkeypatch, native_model_setup, scoring, pair, asleep):
    args, _ = _setup_args_from_launcher(monkeypatch, pair, 0)
    model, optimizer, scheduler = native_model_setup.setup(args)
    actor = scoring.actor_cls()
    actor.args = scoring_args(delayed=True, dynamic=True)
    actor.args.debug_disable_optimizer = args.debug_disable_optimizer
    actor.args.num_rollout = args.num_rollout
    actor.role, actor._active_model_tag, actor._cell_index = "actor", "actor", 0
    actor._asleep, actor._last_rollout_id = asleep, None
    actor.model, actor.optimizer, actor.opt_param_scheduler = model, optimizer, scheduler
    actor.output_store_read = None
    actor._heartbeat = SimpleNamespace(bump=lambda: None)
    actor._get_actor_weights = lambda **kwargs: dict(model[0].named_parameters())
    # Memory/process-group SDK boundaries; the production RPC restores residency.
    actor.wake_up = lambda: setattr(actor, "_asleep", False)
    actor.sleep = lambda: setattr(actor, "_asleep", True)
    raw = make_raw_data()
    before = model[0].weight.detach().clone()
    version = actor._get_actor_weight_version()
    ref = actor.score_log_probs(0, scoring.store.put(raw, ROLLOUT_DATA_VALUE_SPEC))
    batch = scoring.store.values[ref.payload]
    assert optimizer is scheduler is None and native_model_setup.optimizers == []
    assert sum(value.numel() for value in batch["log_probs"]) == sum(raw["response_lengths"])
    assert all(torch.isfinite(value).all() and not value.requires_grad for value in batch["log_probs"])
    assert batch["metadata"]["weight_version"] == actor._get_actor_weight_version() == version
    assert batch["metadata"]["use_rollout_sampling_mask"] is False
    assert actor._asleep is asleep and actor._last_rollout_id is None
    assert model[0].weight.grad is None
    torch.testing.assert_close(model[0].weight, before, rtol=0, atol=0)


@pytest.mark.parametrize("pair", ["A", "B", "C"])
async def test_baseline_native_driver_evaluates_without_training_or_saving(monkeypatch, pair):
    _, config = _setup_args_from_launcher(monkeypatch, pair, 0)
    args = driver_args(**vars(config))
    args.start_rollout_id = 0
    events = []
    components = _install_driver_fakes(monkeypatch, args, events)
    await with_disposer(train_driver.train, _startup_info(args))
    assert events.count("eval:0") == 1
    assert components.actor_model.trained == components.actor_model.saved == []
    assert not any(event.startswith(("prepare_rollout:", "generate_start:", "actor_export_hf:")) for event in events)
    assert events.count("update_weights:None") == 1  # Initial publication is not an optimizer update.


@pytest.mark.parametrize("teacher", sorted(launcher._READ_ONLY_MODELS))
def test_exact_approved_model_sources_are_accepted_without_reads(teacher):
    args = _args("C", "--teacher", str(teacher))
    assert args.teacher == teacher


@pytest.mark.parametrize("extra", [
    ("--teacher", "/mnt/codesign-exp/another-user/model"),
    ("--teacher", "/mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-27B"),
    ("--output-root", "/mnt/codesign-exp/another-user/runs"),
    ("--teacher-url", "http://user:secret@teacher:30000/generate"),
    ("--teacher-url", "http://teacher:30000"),
    ("--student-engine-gpus", "3"),
    ("--sglang-mem-fraction-static", "1"),
    ("--max-tokens-per-gpu", "0"),
])
def test_invalid_scope_endpoint_or_topology_fails_before_submission(extra):
    with pytest.raises(ValueError):
        _args("A", *extra)


def test_platform_nccl_values_are_preserved_and_channel_conflicts_rejected(monkeypatch):
    for key, value in {
        "NCCL_SOCKET_IFNAME": "platform-nic", "NCCL_IB_HCA": "platform-hca", "NCCL_NVLS_ENABLE": "0",
        "NCCL_MIN_NCHANNELS": "8", "NCCL_MAX_NCHANNELS": "8", "SGLANG_DETERMINISTIC_NCCL_NCHANNELS": "8",
    }.items():
        monkeypatch.setenv(key, value)
    env = launcher._runtime_env(ExecuteTrainConfig())
    assert env["NCCL_SOCKET_IFNAME"] == "platform-nic" and env["NCCL_IB_HCA"] == "platform-hca"
    assert env["NCCL_NVLS_ENABLE"] == "0" and env["NCCL_MIN_NCHANNELS"] == env["NCCL_MAX_NCHANNELS"] == "8"
    monkeypatch.setenv("NCCL_MAX_NCHANNELS", "16")
    with pytest.raises(ValueError, match="conflicts"):
        launcher._runtime_env(ExecuteTrainConfig())


def _population(tmp_path, monkeypatch):
    monkeypatch.setattr(launcher, "_PERSONAL_ROOT", tmp_path)
    population = tmp_path / "population"
    population.mkdir()
    student = tmp_path / "student"
    student.mkdir()
    (student / "tokenizer.json").write_text("tokenizer identity")
    report = {
        "status": "passed", "limits": {"context_tokens": 131072, "response_tokens": 8192},
        "selection_seed": 42, "chat_template": {"kwargs": {"enable_thinking": True, "preserve_thinking": True}},
        "split": {"monitoring_stratum_counts": {name: 8 for name in ("short", "medium", "long")}, "checks": {"overlap": []}},
        "qwen_tokenizer": {"assets": {"tokenizer.json": launcher._sha256(student / "tokenizer.json")}}, "datasets": {},
    }
    for name, rows in (("train", 8), ("monitor", 24)):
        path = population / f"{name}.jsonl"
        path.write_text((json.dumps({"prompt": "test", "metadata": {}}) + "\n") * rows)
        report["datasets"][name] = {"path": str(path), "rows": rows, "sha256": launcher._sha256(path)}
    (population / "population.json").write_text(json.dumps(report))
    return SimpleNamespace(population_dir=population, student=student), report


def test_frozen_population_byte_identity_is_enforced_without_rerendering(tmp_path, monkeypatch):
    args, report = _population(tmp_path, monkeypatch)
    receipt = launcher._check_population(args)
    assert receipt["datasets"] == report["datasets"]
    path = args.population_dir / "train.jsonl"
    path.write_text(path.read_text() + "\n")
    with pytest.raises(ValueError, match="bytes changed"):
        launcher._check_population(args)


@pytest.mark.parametrize("field,value", [("status", "incomplete"), ("selection_seed", 1)])
def test_invalid_population_is_not_launched(tmp_path, monkeypatch, field, value):
    args, report = _population(tmp_path, monkeypatch)
    report[field] = value
    (args.population_dir / "population.json").write_text(json.dumps(report))
    with pytest.raises(ValueError):
        launcher._check_population(args)


def test_receipt_write_failure_is_auxiliary_not_a_training_gate(monkeypatch):
    def unavailable(*args):
        raise OSError("test evidence volume failure")
    monkeypatch.setattr(launcher, "_write_json", unavailable)
    launcher._record_receipt(Path("/records/launch.json"), {"status": "unverified"})


def _score_args(external=True):
    return SimpleNamespace(**(parser_defaults() | dict(
        rm_url="http://external-teacher:30000/generate" if external else None,
        sglang_model_routers={"teacher": ("named-teacher", 30001)},
        sglang_router_ip="student", sglang_router_port=30002, sglang_router_request_timeout_secs=3600,
    )))


def _generation_input(sample=None, **sampling_overrides):
    if sample is None:
        sample = Sample(prompt="rendered", index=7, group_index=3)
        sample.metadata = {
            "source": {"uid": "source-uid", "group_id": "source-task", "category": "thinking_only",
                       "prompt_token_count": 2, "prompt_sha256": token_hash([11, 12])},
            "thinking_enabled": True, "tools": [], "history": [{"role": "user", "content": "original history"}],
        }
    args = _score_args()
    args.sglang = SimpleNamespace(common_value=lambda name: name == "enable_deterministic_inference")
    args.rollout_temperature = 1
    args.rollout_max_response_len = 8192
    args.rollout_max_context_len = 131072
    tokenizer = SimpleNamespace(encode=lambda prompt, **kwargs: [11, 12], decode=lambda ids, **kwargs: "fresh completion")
    return GenerateFnInput(
        state=SimpleNamespace(args=args, tokenizer=tokenizer, processor=None), sample=sample,
        sampling_params={"temperature": 1, "top_p": 1, "top_k": -1, "max_new_tokens": 8192, **sampling_overrides},
        evaluation=True,
    )


def _native_observation(monkeypatch, input, *, prefill_version="published-73", prefill_ids=(13, 14)):
    """Run real native request composition/update with deterministic endpoint fixtures."""
    requests = []
    async def post(url, payload, **kwargs):
        requests.append((url, copy.deepcopy(payload)))
        if payload["sampling_params"]["max_new_tokens"] > 0:
            return {"text": "fresh completion", "meta_info": {
                "prompt_tokens": 2, "finish_reason": {"type": "stop"},
                "output_token_logprobs": [[-0.2, 13], [-0.3, 14]],
                "weight_versions": [{"version": "published-73", "start": 0, "end": 2}],
                "prefill_weight_versions": [{"version": "published-73", "start": 0, "end": 2}],
            }}
        ids = prefill_ids if url == "http://student:30002/generate" else (13, 14)
        meta = {"input_token_logprobs": [[None, 12], [-0.2, ids[0]], [-0.3, ids[1]]]}
        if url == "http://student:30002/generate" and prefill_version is not None:
            meta.update(weight_version=prefill_version, prefill_weight_versions=[{
                "version": prefill_version, "start": 0, "end": 4,
            }])
        return {"meta_info": meta}
    monkeypatch.setattr(single_turn, "post", post)
    monkeypatch.setattr(single_turn, "compute_routing_headers", lambda args, sample: {})
    monkeypatch.setattr(qwen_alignment.opd, "_post_json", post)
    monkeypatch.setattr(alignment, "_post_json", post)
    monkeypatch.setattr(qwen_alignment, "ReasoningParser", lambda **kwargs: SimpleNamespace(
        parse_non_stream=lambda text: ("fresh reasoning", "fresh body")))
    async def observe():
        output = await qwen_alignment.generate(input)
        await qwen_alignment.score_teacher(input.args, output.samples)
        return output.samples
    return asyncio.run(observe()), requests


@pytest.mark.parametrize("external,endpoint", [(True, "http://external-teacher:30000/generate"), (False, "http://named-teacher:30001/generate")])
def test_teacher_scores_original_tokens_and_records_real_endpoint(monkeypatch, external, endpoint):
    args = _score_args(external)
    sample = Sample(tokens=[11, 12, 13, 14], response_length=2, rollout_log_probs=[-0.2, -0.3])
    requests, rescores = [], []
    result = {"meta_info": {"input_token_logprobs": [[None, 11], [-0.1, 12], [-0.2, 13], [-0.3, 14]]}}
    async def post(url, payload, **kwargs):
        requests.append((url, payload, kwargs))
        return result
    async def rescore(args, sample):
        rescores.append(sample)
    monkeypatch.setattr(qwen_alignment.opd, "_post_json", post)
    monkeypatch.setattr(qwen_alignment, "rescore_student", rescore)
    reward = asyncio.run(qwen_alignment.score_teacher(args, sample))
    assert requests[0][0] == endpoint and requests[0][1]["input_ids"] == sample.tokens
    assert requests[0][1]["sampling_params"]["max_new_tokens"] == 0
    assert sample.metadata["teacher_scoring"]["endpoint"] == endpoint
    assert "model" not in sample.metadata["teacher_scoring"]
    assert rescores == [sample] and sample.rollout_log_probs == [-0.2, -0.3]
    sample.reward = reward
    args.reward_key, args.opd_log_prob_top_k = "reward", 0
    args.model_copy = lambda update: SimpleNamespace(**(vars(args) | update))
    assert post_process_rewards(args, [sample]) == ([0.0], [0.0])
    assert sample.teacher_log_probs.tolist() == pytest.approx([-0.2, -0.3])


@pytest.mark.parametrize("bad_scores", [[[-0.2, 99], [-0.3, 14]], [[float("nan"), 13], [-0.3, 14]], [[-0.3, 14]]])
def test_bad_teacher_token_ids_missing_scores_or_nonfinite_values_are_not_silenced(monkeypatch, bad_scores):
    async def post(*args, **kwargs):
        return {"meta_info": {"input_token_logprobs": [[None, 11], *bad_scores]}}
    monkeypatch.setattr(qwen_alignment.opd, "_post_json", post)
    with pytest.raises(ValueError, match="sampled Qwen completion"):
        asyncio.run(qwen_alignment.score_teacher(_score_args(), Sample(tokens=[11, 12, 13, 14], response_length=2)))


def test_missing_named_teacher_never_falls_back_to_student():
    args = _score_args(False)
    args.sglang_model_routers = {}
    with pytest.raises(ValueError, match="distinct named teacher"):
        asyncio.run(qwen_alignment.score_teacher(args, Sample()))


def test_zero_length_teacher_response_keeps_empty_native_target(monkeypatch):
    async def post(*args, **kwargs):
        return {"meta_info": {"input_token_logprobs": [[None, 11], [-0.1, 12]]}}
    async def rescore(*args):
        return None
    monkeypatch.setattr(qwen_alignment.opd, "_post_json", post)
    monkeypatch.setattr(qwen_alignment, "rescore_student", rescore)
    sample = Sample(tokens=[11, 12], response_length=0)
    asyncio.run(qwen_alignment.score_teacher(_score_args(), sample))
    assert sample.metadata["teacher_scoring"]["scored_tokens"] == 0
    assert sample.metadata["teacher_scoring"]["mean_logprob"] is None


def test_generation_retains_prefix_completion_ids_and_minimal_train_identity(monkeypatch):
    sample = Sample(prompt="rendered", tokens=[11, 12, 13, 14], response_length=2, index=7, group_index=3)
    sample.metadata = {
        "source": {"uid": "source-uid", "group_id": "source-task", "category": "thinking_only", "prompt_token_count": 2, "prompt_sha256": token_hash([11, 12])},
        "thinking_enabled": True, "tools": [], "history": [{"role": "user", "content": "original history"}],
        "original_completion": {"content": "historical target must never enter train metadata"},
    }
    async def native_generate(input):
        return SimpleNamespace(samples=sample)
    input = _generation_input(sample)
    monkeypatch.setattr(qwen_alignment, "generate_single_turn", native_generate)
    monkeypatch.setattr(qwen_alignment, "ReasoningParser", lambda **kwargs: SimpleNamespace(parse_non_stream=lambda text: ("fresh reasoning", "fresh body")))
    result = asyncio.run(qwen_alignment.generate(input))
    assert result.samples.tokens == [11, 12, 13, 14] and sample.response_length == 2
    assert sample.train_metadata["source_uid"] == "source-uid"
    assert sample.train_metadata["source_group_id"] == "source-task"
    assert sample.train_metadata["completion_sha256"] == token_hash([13, 14])
    assert "original_completion" not in sample.train_metadata
    assert sample.metadata["original_completion"]["content"].startswith("historical target")
    sample.metadata["source"]["prompt_sha256"] = hashlib.sha256(b"different").hexdigest()
    with pytest.raises(ValueError, match="recorded rendered history"):
        asyncio.run(qwen_alignment.generate(input))


def test_probability_declarations_follow_real_native_requests_and_endpoint_versions(monkeypatch):
    input = _generation_input(sampling_seed=91, stop=["termination only"])
    # Neither stale defaults nor historical/category metadata own the request.
    input.args.rollout_temperature = 0.7
    input.sample.metadata["sampling_params"] = {"temperature": 0.2, "top_p": 0.5, "top_k": 8}
    input.sample.metadata["probability_definition"] = {"decode": "historical fiction", "teacher": "unverified"}
    before = copy.deepcopy(input.sampling_params)
    sample, requests = _native_observation(monkeypatch, input)
    definition = sample.metadata["probability_definition"]
    assert definition == {
        "decode": "full_vocabulary_log_softmax", "prefill": "full_vocabulary_log_softmax",
        "sampling_distribution": "student_decode", "sampling_params": before,
    }
    assert requests[0][1]["sampling_params"] == before == input.sampling_params
    prefill_url, payload = requests[-1]
    assert prefill_url == "http://student:30002/generate"
    assert payload["input_ids"] == sample.tokens
    assert payload["sampling_params"] == {"temperature": 0, "top_p": 1, "top_k": -1,
                                          "max_new_tokens": 0, "skip_special_tokens": False}
    assert payload["return_logprob"] is True and payload["logprob_start_len"] == 1
    assert payload["extra_key"].startswith("alignment-")
    scored = sample.metadata["student_rescoring"]
    assert scored["probability_definition"] == "full_vocabulary_log_softmax"
    assert scored["scored_weight_versions"] == scored["sampled_weight_versions"] == ["published-73"]
    assert scored["versions_match"] is True and scored["training_logprobs_replaced"] is False
    raw = sample.to_dict()
    assert inspector._decode_version(raw, 2) == "published-73"
    for comparison in ("decode", "prefill"):
        inspector._probability_check(raw, {"rollout_temperature": 1, "use_rollout_sampling_mask": False}, comparison)
    assert inspector._prefill(raw, "published-73").tolist() == pytest.approx([-0.2, -0.3])
    assert sample.rollout_log_probs == [-0.2, -0.3]
    assert "teacher" not in definition  # No remote teacher semantic receipt was verified.


@pytest.mark.parametrize("sampling_overrides,verdict", [
    ({}, "PASS"), ({"temperature": 0.7}, "INCOMPLETE"), ({"top_p": 0.9}, "INCOMPLETE"),
    ({"json_schema": '{"type":"object"}'}, "INCOMPLETE"), ({"logit_bias": {"13": 2}}, "INCOMPLETE"),
])
def test_reader_verdict_tracks_actual_request_probability_definition(
    monkeypatch, tmp_path, native_run, native_fixture, sampling_overrides, verdict,
):
    input = _generation_input(**sampling_overrides)
    sample, _ = _native_observation(monkeypatch, input)
    assert ("decode" in sample.metadata["probability_definition"]) == (verdict == "PASS")
    assert sample.metadata["probability_definition"]["sampling_params"] == input.sampling_params
    def mutate(dump, batch):
        dump["samples"][0]["metadata"]["probability_definition"] = sample.metadata["probability_definition"]
    report = _fault_run(tmp_path, native_run, native_fixture, mutate)
    assert report["verdict"] == verdict
    issues = report["checkpoints"][0]["decode"]["overall"]["issues"]
    assert ("probability_definition_mismatch" in {issue["code"] for issue in issues}) == (verdict == "INCOMPLETE")


@pytest.mark.parametrize("flag", ["nondeterministic", "recompute_logprobs_via_prefill", "use_sampling_support_replay"])
def test_unresolved_decode_probability_source_is_not_declared(monkeypatch, flag):
    input = _generation_input()
    if flag == "nondeterministic":
        input.args.sglang = SimpleNamespace(common_value=lambda name: False)
    else:
        setattr(input.args, flag, True)
    definition = qwen_alignment._decode_probability_definition(input)
    assert "decode" not in definition
    with pytest.raises(inspector.EvidenceError, match="not declared full-vocabulary"):
        inspector._probability_check({"metadata": {"probability_definition": definition}},
                                     {"rollout_temperature": 1, "use_rollout_sampling_mask": False}, "decode")


@pytest.mark.parametrize("prefill_version", [None, "different-actual-version"])
def test_prefill_versions_are_never_filled_from_decode_or_zero(monkeypatch, prefill_version):
    sample, _ = _native_observation(monkeypatch, _generation_input(), prefill_version=prefill_version)
    scored = sample.metadata["student_rescoring"]
    assert scored["status"] == "measured" and scored["versions_match"] is False
    assert scored["scored_weight_versions"] == ([] if prefill_version is None else [prefill_version])
    assert scored["sampled_weight_versions"] == ["published-73"]
    with pytest.raises(inspector.EvidenceError, match="Prefill actual consumed version"):
        inspector._prefill(sample.to_dict(), "published-73")


def test_unverified_prefill_ids_have_no_probability_declaration(monkeypatch):
    sample, _ = _native_observation(monkeypatch, _generation_input(), prefill_ids=(99, 14))
    assert sample.metadata["student_rescoring"]["status"] == "unverified"
    assert "probability_definition" not in sample.metadata["student_rescoring"]
    assert "prefill" not in sample.metadata["probability_definition"]
    assert sample.rollout_log_probs == [-0.2, -0.3]
    with pytest.raises(inspector.EvidenceError, match="unverified"):
        inspector._prefill(sample.to_dict(), "published-73")
