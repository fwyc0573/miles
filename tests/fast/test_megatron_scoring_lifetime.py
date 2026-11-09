"""Pinned-source lifetime contrast and soft-only observation boundaries.

Set MILES_PINNED_MEGATRON_SCHEDULE to the retained qualified schedules.py to
execute its real PP1 schedule, forward step, callback branch, and backward
step on CPU. SDK metadata/groups and the unused CUDA token counter are mocked;
no schedule implementation is copied and no CUDA/fused-scorer claim follows.
"""

import argparse
import ast
import contextlib
import hashlib
import json
import os
import shlex
import sys
import weakref
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
import torch

from miles.utils.args.custom_function import resolve_custom_function_configs
from miles.utils.args.custom_view import ImmutableNamespace, compute_custom_function_config
from miles.utils.args.runtime import AllConfig, TrainerConfig
from miles.utils.args.trainer_utils import compute_trainer_config
from miles.utils.arguments import get_miles_extra_args_provider
from tests.manual.agent_opd import megatron_scoring_lifetime as lifetime
from tests.manual.agent_opd import megatron_scoring_lifetime_observer as observer
from tests.manual.agent_opd import run_swe_opd


@pytest.fixture
def pinned_source():
    path = os.environ.get("MILES_PINNED_MEGATRON_SCHEDULE")
    if path is None:
        pytest.skip("The actual qualified Megatron source must be explicitly supplied")
    source = Path(path).read_bytes()
    assert hashlib.sha256(source).hexdigest() == lifetime.source_manifest()["before_sha256"]
    return source


@pytest.fixture
def pinned_checkout(tmp_path, monkeypatch, pinned_source):
    root = tmp_path / "megatron-fixture"
    target = root / lifetime.source_manifest()["source_path"]
    target.parent.mkdir(parents=True)
    target.write_bytes(pinned_source)
    git = lifetime._git

    def fixture_git(directory, *arguments):
        if arguments == ("rev-parse", "HEAD"):
            return lifetime.source_manifest()["megatron_commit"].encode()
        if arguments[0] == "show":
            return pinned_source
        return git(directory, *arguments)

    monkeypatch.setattr(lifetime, "_git", fixture_git)
    monkeypatch.setattr(
        lifetime.importlib.metadata, "version", lambda name: lifetime.source_manifest()["distribution_version"]
    )
    return root, target


def _prepare(root, archive, release):
    return lifetime.prepare_source(
        root, image=lifetime.source_manifest()["image"], release=release, archive_dir=archive
    )


def test_pinned_patch_is_exact_and_idempotent(pinned_checkout, tmp_path):
    root, target = pinned_checkout
    original = target.read_bytes()
    red = _prepare(root, tmp_path / "red", False)
    assert target.read_bytes() == original
    assert not red["patch_applied"]
    green = _prepare(root, tmp_path / "green", True)
    assert green["patch_applied"]
    assert hashlib.sha256(target.read_bytes()).hexdigest() == lifetime.expected_source_sha256(True)
    assert not _prepare(root, tmp_path / "green", True)["patch_applied"]
    assert (tmp_path / "green" / "schedules.before.py").read_bytes() == original
    assert (tmp_path / "green" / "schedules.after.py").read_bytes() == target.read_bytes()
    assert (tmp_path / "green" / lifetime._PATCH.name).read_bytes() == lifetime._PATCH.read_bytes()
    assert len((tmp_path / "green" / "preflight.jsonl").read_text().splitlines()) == 2
    with pytest.raises(ValueError, match="Unrecognized scoring schedule"):
        _prepare(root, tmp_path / "red-after-green", False)


def test_drift_is_rejected_without_altering_source(pinned_checkout, tmp_path):
    root, target = pinned_checkout
    target.write_bytes(target.read_bytes() + b"\n# unrelated change\n")
    before = target.read_bytes()
    with pytest.raises(ValueError, match="Unrecognized scoring schedule"):
        _prepare(root, tmp_path / "archive", True)
    assert target.read_bytes() == before
    assert not (tmp_path / "archive").exists()


def test_patch_identity_is_checked_before_mutation(pinned_checkout, tmp_path, monkeypatch):
    root, target = pinned_checkout
    patch = tmp_path / "changed.patch"
    patch.write_bytes(lifetime._PATCH.read_bytes() + b"\n")
    monkeypatch.setattr(lifetime, "_PATCH", patch)
    before = target.read_bytes()
    with pytest.raises(ValueError, match="verified two-indentation diff"):
        _prepare(root, tmp_path / "archive", True)
    assert target.read_bytes() == before


@pytest.mark.parametrize("field", ["image", "commit", "version"])
def test_dependency_identity_is_checked_before_mutation(pinned_checkout, tmp_path, monkeypatch, field):
    root, target = pinned_checkout
    before = target.read_bytes()
    image = lifetime.source_manifest()["image"]
    if field == "image":
        image = "unqualified-image"
    elif field == "commit":
        monkeypatch.setattr(lifetime, "_git", lambda *args: b"another-commit")
    else:
        monkeypatch.setattr(lifetime.importlib.metadata, "version", lambda name: "another-version")
    with pytest.raises(ValueError, match="identity differs|qualified pinned image"):
        lifetime.prepare_source(root, image=image, release=True, archive_dir=tmp_path / "archive")
    assert target.read_bytes() == before


class _CPUTorch:
    def __getattr__(self, name):
        return getattr(torch, name)

    def zeros(self, *args, **kwargs):
        if kwargs.get("device") == "cuda":
            kwargs["device"] = "cpu"
        return torch.zeros(*args, **kwargs)


def _native_cpu_pass(source, monkeypatch, *, backward=False):
    names = {
        "forward_backward_no_pipelining",
        "forward_step",
        "forward_step_calc_loss",
        "check_first_val_step",
        "_get_experimental_attention_variant_loss_scale_func",
        "backward_step",
    }
    tree = ast.parse(source)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {node.name for node in functions} == names
    future = ast.parse("from __future__ import annotations").body
    module = ast.Module(body=future + functions, type_ignores=[])
    config = SimpleNamespace(
        timers=None,
        no_sync_func=None,
        overlap_moe_expert_parallel_comm=False,
        finalize_model_grads_func=None,
        enable_autocast=False,
        calculate_per_token_loss=True,
        grad_scale_func=None,
        deallocate_pipeline_outputs=False,
    )
    namespace = {
        "torch": _CPUTorch(),
        "contextlib": contextlib,
        "get_model_config": lambda model: config,
        "get_model_type": lambda model: "gpt",
        "get_attr_wrapped_model": getattr,
        "set_current_microbatch": lambda model, index: setattr(model, "current_microbatch", index),
    }
    mtp = ModuleType("megatron.core.transformer.multi_token_prediction")
    mtp.MTPLossAutoScaler = object()
    monkeypatch.setitem(sys.modules, mtp.__name__, mtp)
    exec(compile(module, "qualified-Megatron-schedules.py", "exec"), namespace)
    prior, live_counts, callback_indices = [], [], []
    weight = torch.nn.Parameter(torch.arange(21, dtype=torch.float64).reshape(7, 3) / 21)

    class Model(torch.nn.Module):
        def set_input_tensor(self, inputs):
            pass

        def forward(self, inputs):
            live_counts.append(sum(reference() is not None for reference in prior))
            output = inputs @ weight.t()
            prior.append(weakref.ref(output))
            return output

    model = Model()

    def callback(output, non_loss_data=False):
        callback_indices.append(model.current_microbatch)
        values = torch.log_softmax(output, dim=-1)[0, :, 2]
        if non_loss_data:
            return {"log_probs": values.clone()}
        loss = -values.sum()
        return loss, torch.tensor(values.numel()), {"loss": loss.detach().clone()}

    def forward_step(iterator, module):
        return module(next(iterator)), callback

    inputs = [torch.arange(12, dtype=torch.float64).reshape(1, 4, 3) / 12 + i for i in range(3)]
    context = contextlib.nullcontext() if backward else torch.no_grad()
    with context:
        outputs = namespace["forward_backward_no_pipelining"](
            forward_step_func=forward_step,
            data_iterator=iter(inputs),
            model=model,
            num_microbatches=3,
            seq_length=4,
            micro_batch_size=1,
            forward_only=not backward,
            collect_non_loss_data=not backward,
            pg_collection=SimpleNamespace(tp=object(), cp=SimpleNamespace(size=lambda: 1)),
        )
    return {
        "live_counts": live_counts,
        "callback_indices": callback_indices,
        "outputs": outputs,
        "alive_after_return": sum(reference() is not None for reference in prior),
        "gradient": weight.grad,
    }


@pytest.mark.parametrize("backward", [False, True])
def test_actual_schedule_callback_red_green(pinned_checkout, tmp_path, monkeypatch, backward):
    root, target = pinned_checkout
    red = _native_cpu_pass(target.read_bytes(), monkeypatch, backward=backward)
    _prepare(root, tmp_path / "green", True)
    green = _native_cpu_pass(target.read_bytes(), monkeypatch, backward=backward)
    assert red["callback_indices"] == green["callback_indices"] == [0, 1, 2]
    assert red["alive_after_return"] == green["alive_after_return"] == 0
    assert green["live_counts"] == [0, 0, 0]
    if backward:
        assert red["live_counts"] == [0, 0, 0]
        torch.testing.assert_close(red["gradient"], green["gradient"], rtol=0, atol=0)
    else:
        assert red["live_counts"] == [0, 1, 1]
    for original, patched in zip(red["outputs"], green["outputs"], strict=True):
        for key in original:
            torch.testing.assert_close(original[key], patched[key], rtol=0, atol=0)


def _observation(tmp_path):
    return observer._ScoringObservation(ImmutableNamespace(scoring_lifetime_dir=str(tmp_path)), "", 0)


def _cpu_memory(monkeypatch):
    monkeypatch.setattr(
        torch.cuda,
        "memory_stats",
        lambda: {
            "allocated_bytes.all.current": 11,
            "active_bytes.all.current": 13,
            "reserved_bytes.all.current": 17,
            "inactive_split_bytes.all.current": 3,
        },
    )


def test_observer_retains_no_output_and_leaves_hooks_transparent(tmp_path, monkeypatch):
    _cpu_memory(monkeypatch)
    state = _observation(tmp_path)
    model = torch.nn.Linear(3, 7)
    model.register_forward_pre_hook(state.forward_enter)
    model.register_forward_pre_hook(state.projection_enter)
    model.register_forward_hook(state.forward_exit)
    inputs = torch.ones(4, 3)
    with torch.no_grad():
        expected = torch.nn.functional.linear(inputs, model.weight, model.bias)
        output = model(inputs)
        torch.testing.assert_close(output, expected, rtol=0, atol=0)
        reference = weakref.ref(output)
        del output
        assert reference() is None and state.previous() is None
        model(inputs)
    records = [json.loads(row) for row in (tmp_path / "rank_0.jsonl").read_text().splitlines()]
    entries = [row for row in records if row["event"] == "forward_enter"]
    assert [row["forward_microbatch_index"] for row in entries] == [0, 1]
    assert [row["prior_full_output_alive"] for row in entries] == [False, False]
    assert entries[-1]["prior_full_output_storage"]["storage_bytes"] == expected.untyped_storage().nbytes()
    assert entries[-1]["inactive_split_bytes"] == 3
    before = len(records)
    model(inputs).sum().backward()
    assert len((tmp_path / "rank_0.jsonl").read_text().splitlines()) == before


@pytest.mark.parametrize("failure", ["memory", "write"])
def test_observer_failure_cannot_change_forward_or_backward(tmp_path, monkeypatch, failure):
    _cpu_memory(monkeypatch)
    state = _observation(tmp_path)
    if failure == "memory":
        monkeypatch.setattr(
            torch.cuda, "memory_stats", lambda: (_ for _ in ()).throw(RuntimeError("memory observer failed"))
        )
    else:
        monkeypatch.setattr(state, "write", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("receipt failed")))
    model = torch.nn.Linear(3, 7)
    model.register_forward_pre_hook(state.forward_enter)
    model.register_forward_pre_hook(state.projection_enter)
    model.register_forward_hook(state.forward_exit)
    inputs = torch.ones(4, 3)
    with torch.no_grad():
        expected = torch.nn.functional.linear(inputs, model.weight, model.bias)
        torch.testing.assert_close(model(inputs), expected, rtol=0, atol=0)
    model(inputs).sum().backward()
    assert model.weight.grad is not None
    if failure == "memory":
        assert all(
            json.loads(row)["event"] == "observer_unverified"
            for row in (tmp_path / "rank_0.jsonl").read_text().splitlines()
        )


@pytest.mark.parametrize("failure", [None, "source", "registration"])
def test_native_hook_installation_is_soft_and_pass_scoped(tmp_path, monkeypatch, failure):
    _cpu_memory(monkeypatch)
    source = tmp_path / "schedules.py"
    source.write_bytes(b"source identity fixture\n")
    parallel = ModuleType("megatron.core.pipeline_parallel")
    parallel.schedules = SimpleNamespace(__file__=str(source))
    utilities = ModuleType("megatron.core.utils")
    utilities.get_attr_wrapped_model = getattr
    monkeypatch.setitem(sys.modules, parallel.__name__, parallel)
    monkeypatch.setitem(sys.modules, utilities.__name__, utilities)
    args = ImmutableNamespace(
        scoring_lifetime_dir=str(tmp_path / "observations"),
        scoring_lifetime_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
    )

    class Model(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.output_layer = torch.nn.Linear(3, 7)

        def forward(self, inputs):
            return self.output_layer(inputs)

    model = Model()
    if failure == "source":
        args = args.model_copy(update={"scoring_lifetime_source_sha256": "different-source"})
    elif failure == "registration":
        monkeypatch.setattr(
            model.output_layer,
            "register_forward_pre_hook",
            lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("registration failed")),
        )
    observer.before_log_prob(args, [model], "")
    inputs = torch.ones(4, 3)
    with torch.no_grad():
        model(inputs)
    records = [json.loads(row) for row in (tmp_path / "observations" / "rank_0.jsonl").read_text().splitlines()]
    if failure == "registration":
        assert not model._forward_pre_hooks and not model._forward_hooks
        assert records[-1]["event"] == "observer_unverified"
    else:
        observer.before_log_prob(args, [model], "score_")
        assert model._scoring_lifetime_observation.pass_index == 1
        assert len(model._forward_pre_hooks) == len(model._forward_hooks) == 1
        with torch.no_grad():
            model(inputs)
        if failure == "source":
            assert any(row["event"] == "observer_unverified" for row in records)


@pytest.mark.parametrize("release", [False, True])
def test_combined_cli_typed_before_log_prob_installs_without_swe_attempt(tmp_path, monkeypatch, release):
    """Execute the actual native caller and typed transport, excluding GPU compute."""
    from tests.fast.test_swe_replay import _typed_swe_config

    root = Path(__file__).resolve().parents[2]
    source = tmp_path / "schedules.py"
    source.write_bytes(b"source identity fixture\n")
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    config = json.loads(
        (root / "task_memory/task_2026-11-08_qwen35_swe_full_r256/capacity_smoke_config.json").read_text()
    )
    config["protocol"] = "r256"
    config["training"]["release_scoring_output"] = release
    argv = shlex.split(run_swe_opd._training_args(config, "A", "http://teacher/generate", tmp_path, "typed-attempt"))
    argv[argv.index("--scoring-lifetime-source-sha256") + 1] = source_sha
    monkeypatch.setattr(sys, "argv", ["train.py", *argv])
    parser = argparse.ArgumentParser()
    get_miles_extra_args_provider()(parser)
    parsed, _ = parser.parse_known_args(argv)
    resolve_custom_function_configs(parsed)
    actions = [option for action in parser._actions for option in action.option_strings]
    assert len(actions) == len(set(actions))
    assert set(observer.ScoringLifetimeConfig.model_fields) == {
        "scoring_lifetime_dir",
        "scoring_lifetime_source_sha256",
    }
    assert not hasattr(parsed, "swe_attempt")
    assert parsed.custom_rm_path.config.swe_attempt == "typed-attempt"

    monkeypatch.setattr(sys, "argv", ["test"])
    typed = _typed_swe_config("r256", run_kind="smoke")
    names = ("custom_megatron_before_log_prob_hook_path", "custom_rm_path", "custom_megatron_optimizer_step_hook_path")
    typed = AllConfig.model_validate(typed.model_dump(mode="python") | {name: getattr(parsed, name) for name in names})
    trainer = compute_trainer_config(typed, typed.raw_megatron.trainers[0])
    trainer = TrainerConfig.model_validate_json(trainer.model_dump_json())
    view = compute_custom_function_config(trainer, trainer.custom_megatron_before_log_prob_hook_path)
    assert isinstance(view, ImmutableNamespace) and not hasattr(view, "swe_attempt")
    assert trainer.custom_megatron_optimizer_step_hook_path.config.swe_attempt == "typed-attempt"

    parallel = ModuleType("megatron.core.pipeline_parallel")
    parallel.schedules = SimpleNamespace(__file__=str(source))
    utilities = ModuleType("megatron.core.utils")
    utilities.get_attr_wrapped_model = getattr
    monkeypatch.setitem(sys.modules, parallel.__name__, parallel)
    monkeypatch.setitem(sys.modules, utilities.__name__, utilities)
    _cpu_memory(monkeypatch)

    class Model(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.output_layer = torch.nn.Linear(3, 7)

        def forward(self, inputs):
            return self.output_layer(inputs)

    class Dumper:
        def __init__(self, *args, **kwargs):
            pass

        def wrap_forward_step(self, function):
            return function

        def finalize(self, model):
            pass

    path = root / "miles/backends/megatron_utils/model.py"
    function = next(
        node
        for node in ast.parse(path.read_text()).body
        if isinstance(node, ast.FunctionDef) and node.name == "forward_only"
    )
    namespace = {
        "torch": torch,
        "DumperMegatronUtil": Dumper,
        "DumperPhase": SimpleNamespace(FWD_ONLY="forward_only"),
        "get_model_config": lambda model: SimpleNamespace(hidden_dropout=0, attention_dropout=0),
        "get_forward_backward_func": lambda: None,
        "mpu": SimpleNamespace(is_pipeline_last_stage=lambda: False),
    }
    module = ast.Module(body=ast.parse("from __future__ import annotations").body + [function], type_ignores=[])
    exec(compile(module, str(path), "exec"), namespace)
    model = Model()
    assert namespace["forward_only"](None, trainer, [model], [], [], rollout_id=0) == {}
    records_path = Path(view.scoring_lifetime_dir) / "rank_0.jsonl"
    records = [json.loads(row) for row in records_path.read_text().splitlines()]
    assert records[0]["event"] == "source_identity" and records[0]["source_verified"]
    assert not any(row["event"] == "observer_unverified" for row in records)
    assert len(model._forward_pre_hooks) == len(model._forward_hooks) == 1
    assert len(model.output_layer._forward_pre_hooks) == 1
    with torch.no_grad():
        output = model(torch.ones(4, 3))
        reference = weakref.ref(output)
        del output
        assert reference() is None and model._scoring_lifetime_observation.previous() is None
    records = [json.loads(row) for row in records_path.read_text().splitlines()]
    assert [row["event"] for row in records] == [
        "source_identity",
        "forward_enter",
        "projection_enter",
        "forward_exit",
    ]
    assert all("attempt" not in row for row in records)


def test_student_preflight_precedes_training_preparation(tmp_path, monkeypatch):
    calls = []
    args = SimpleNamespace(
        swe_config={"training": {"release_scoring_output": True}, "image": "fixture-image"},
        megatron_path="fixture-megatron",
        student_nodes=1,
        pair="A",
        teacher_url="fixture-teacher",
    )
    monkeypatch.setattr(lifetime, "prepare_source", lambda *args, **kwargs: calls.append("preflight") or {})

    def training(*args):
        calls.append("training_args")
        raise RuntimeError("stop before native launch")

    monkeypatch.setattr(run_swe_opd, "_training_args", training)
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", "fixture")
    run_swe_opd._prepare_node(args, tmp_path, 0)
    with pytest.raises(RuntimeError, match="stop before native launch"):
        run_swe_opd._prepare_training(args, tmp_path)
    assert calls == ["preflight", "training_args"]


def test_default_training_skips_preflight(tmp_path, monkeypatch):
    args = SimpleNamespace(swe_config={"training": {}}, pair="A", teacher_url="fixture-teacher")
    monkeypatch.setattr(lifetime, "prepare_source", lambda *args, **kwargs: pytest.fail("default must not patch"))
    monkeypatch.setattr(
        run_swe_opd, "_training_args", lambda *args: (_ for _ in ()).throw(RuntimeError("unchanged default"))
    )
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", "fixture")
    with pytest.raises(RuntimeError, match="unchanged default"):
        run_swe_opd._prepare_training(args, tmp_path)


@pytest.mark.parametrize("release", [False, True])
def test_contrast_adds_only_observation_arguments(tmp_path, release):
    root = Path(__file__).resolve().parents[2]
    config = json.loads(
        (root / "task_memory/task_2026-11-08_qwen35_swe_full_r256/capacity_smoke_config.json").read_text()
    )
    config["protocol"] = "r256"
    config["training"].pop("release_scoring_output", None)
    baseline = shlex.split(run_swe_opd._training_args(config, "A", "fixture-teacher", tmp_path, "fixture-attempt"))
    config["training"]["release_scoring_output"] = release
    observed = shlex.split(run_swe_opd._training_args(config, "A", "fixture-teacher", tmp_path, "fixture-attempt"))
    expected = {
        "--custom-megatron-before-log-prob-hook-path": "tests.manual.agent_opd.megatron_scoring_lifetime_observer.before_log_prob",
        "--scoring-lifetime-dir": str(tmp_path / "megatron_scoring_lifetime" / "observations"),
        "--scoring-lifetime-source-sha256": lifetime.expected_source_sha256(release),
    }
    for name, value in expected.items():
        index = observed.index(name)
        assert observed[index + 1] == value
        del observed[index : index + 2]
    assert observed == baseline
