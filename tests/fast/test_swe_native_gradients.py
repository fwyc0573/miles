"""CPU probe mechanics, not native Qwen/Megatron gradient acceptance."""

import argparse
import copy
import json
import shlex
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

from miles.utils.args.custom_function import CustomFunctionConfig
from miles.utils.args.custom_view import compute_custom_function_config
from miles.utils.args.runtime import AllConfig, OrchestratorConfig
from tests.fast.test_swe_replay import _typed_swe_config
from tests.fast.test_swe_tis import _native_case
from tests.manual.agent_opd import probe_swe_native_gradients as probe
from miles.backends.training_utils.loss.objective import compute_advantages_and_returns, loss_function


def _args(tmp_path):
    return SimpleNamespace(swe_native_gradient_dir=str(tmp_path), swe_native_gradient_parameter_suffix="weight",
                           swe_native_gradient_slice_size=8, swe_native_gradient_graph_nodes=64)


def _records(tmp_path, event):
    path = tmp_path / "native_gradients_rank_0.jsonl"
    return [row for row in map(json.loads, path.read_text().splitlines()) if row["event"] == event]


def test_combined_native_hook_cli_registration_from_generated_argv(tmp_path, monkeypatch):
    from miles.utils.args import custom_function
    from tests.manual.agent_opd.run_swe_opd import _training_args

    task = Path(__file__).resolve().parents[2] / "task_memory/task_2026-11-08_qwen35_swe_full_r256"
    config = json.loads((task / "evidence/training-native-gradient-config.json").read_text())
    config["protocol"] = "r256"
    config.update(prompt_tokens=114688, response_tokens=16384)
    argv = shlex.split(_training_args(config, "A", "http://teacher/generate", tmp_path, "registration-test"))
    parser = argparse.ArgumentParser(add_help=False)
    AllConfig.add_arguments(parser)
    monkeypatch.setattr(sys, "argv", ["train.py", *argv])
    partial, _ = parser.parse_known_args(argv)
    infos = custom_function._compute_custom_function_field_infos(partial, partial=True, config_class=AllConfig)
    paths = [info.path for info in infos]
    required = [f"{probe._MODULE}.before_train", f"{probe._MODULE}.optimizer", f"{probe._MODULE}.tis"]
    assert all(path in paths for path in required)
    assert "tests.manual.agent_opd.swe_replay.SweReplay" in paths
    assert paths.index(required[0]) < paths.index(required[1]) < paths.index("tests.manual.agent_opd.swe_replay.SweReplay")
    print("NATIVE_HOOK_REGISTRATION_ORDER", paths)
    custom_function.add_user_provided_function_arguments(parser, config_class=AllConfig)
    parsed, unknown = parser.parse_known_args(argv)
    assert not any(value.startswith(("--swe-", "--tis-")) for value in unknown)
    destinations = [action.dest for action in parser._actions]
    assert all(destinations.count(name) == 1 for name in probe.NativeGradientProbeConfig.model_fields)
    custom_function.resolve_custom_function_configs(parsed, config_class=AllConfig)
    hooks = [getattr(parsed, name) for name in ("custom_megatron_before_train_step_hook_path",
                                               "custom_megatron_optimizer_step_hook_path", "custom_tis_function_path")]
    assert [hook.path for hook in hooks] == required
    assert all(type(hook.config) is probe.NativeGradientProbeConfig for hook in hooks)
    assert all(hook.config == hooks[0].config for hook in hooks)
    assert all(hook.config.swe_native_gradient_parameter_suffix == "decoder.final_layernorm.weight" for hook in hooks)
    assert parsed.rollout_function_path.config.swe_successful_updates == 3
    assert hooks[-1].config.tis_token_lower == 0.5 and hooks[-1].config.tis_answer_upper == 1.001


def test_actual_typed_hook_factory_and_probe_view(tmp_path):
    parsed = _typed_swe_config("r256", run_kind="smoke")
    additions = vars(_args(tmp_path))
    shared_config = probe.NativeGradientProbeConfig.model_validate(
        parsed.custom_megatron_optimizer_step_hook_path.config.model_dump()
        | parsed.custom_tis_function_path.config.model_dump() | additions)
    parsed = AllConfig.model_validate(parsed.model_dump(mode="python") | {
        "custom_megatron_optimizer_step_hook_path": CustomFunctionConfig(path=f"{probe._MODULE}.optimizer", config=shared_config),
        "custom_tis_function_path": CustomFunctionConfig(path=f"{probe._MODULE}.tis", config=shared_config),
        "custom_megatron_before_train_step_hook_path": CustomFunctionConfig(
            path=f"{probe._MODULE}.before_train", config=shared_config),
    })
    component = OrchestratorConfig.slice_from(parsed)
    restored = OrchestratorConfig.model_validate_json(component.model_dump_json())
    args = compute_custom_function_config(restored, restored.custom_megatron_optimizer_step_hook_path)
    driver = probe.training_protocol(args)
    assert driver.budget == 3
    from miles.utils.args.trainer_utils import compute_trainer_config
    trainer = compute_trainer_config(parsed, parsed.raw_megatron.trainers[0])
    trainer = type(trainer).model_validate_json(trainer.model_dump_json())
    for name in ("custom_megatron_before_train_step_hook_path", "custom_megatron_optimizer_step_hook_path",
                 "custom_tis_function_path"):
        view = compute_custom_function_config(trainer, getattr(trainer, name))
        assert view.swe_native_gradient_dir == str(tmp_path)
        assert view.swe_native_gradient_parameter_suffix == "weight"
        assert view.swe_native_gradient_slice_size == 8
    args = args.model_copy(update={"custom_tis_function_path": args.custom_tis_function_path.model_copy(
        update={"config": shared_config.model_copy(update={"tis_answer_upper": 1.1})})})
    with pytest.raises(ValueError, match="frozen D4 thresholds"):
        probe.training_protocol(args)


@pytest.mark.parametrize("fail_sink", [False, True])
def test_live_native_loss_graph_observation_is_nonmodifying(tmp_path, monkeypatch, fail_sink):
    args, batch, logits, train = _native_case()
    compute_advantages_and_returns(args, batch)
    reference = logits.sum() * 0
    for l, s, q, mask in zip(train, batch["log_probs"], batch["teacher_log_probs"],
                              [[0, 0, 0], [1, 1, 1, 0], [0, 0]], strict=True):
        ratio = (l - s.detach()).exp()
        advantage = (q - s).detach()
        reference += (torch.tensor(mask) * torch.maximum(-ratio * advantage, -ratio.clamp(0.8, 1.28) * advantage)).sum()
    expected_gradient = torch.autograd.grad(reference / 7, logits, retain_graph=True)[0]
    batch["sample_indices"] = [0, 1, 2]
    additions = vars(_args(tmp_path))
    config = probe.NativeGradientProbeConfig.model_validate(args.custom_tis_function_path.config.model_dump() | additions | {
        "swe_cell": "A/r256", "swe_attempt": "cpu-mechanism", "swe_protocol": "r256",
        "swe_evidence_dir": str(tmp_path), "swe_teacher_identity": "A",
    })
    args.custom_tis_function_path = CustomFunctionConfig(path=f"{probe._MODULE}.tis", config=config)
    state = probe._Observation(_args(tmp_path), 0, 0)
    monkeypatch.setitem(probe._observations, str(tmp_path), state)
    if fail_sink:
        def broken(*args, **kwargs):
            raise BrokenPipeError("observer sink unavailable")
        monkeypatch.setattr(probe, "_append", broken)
    loss, _, _ = loss_function(args, batch, 1, logits, num_rollouts=3, num_step_tokens=torch.tensor(7))
    loss.backward()
    torch.testing.assert_close(logits.grad, expected_gradient)
    assert all(value.grad is None for value in batch["teacher_log_probs"] + batch["log_probs"])
    if not fail_sink:
        graph = _records(tmp_path, "live_loss_graph")[0]
        backward = _records(tmp_path, "live_logprob_backward")[0]
        incoming = _records(tmp_path, "post_tis_backward")[0]
        assert graph["detached_baseline_edge"] and backward["baseline_input_gradient_is_none"]
        assert graph["live_logprob_node"] == "CatBackward0"
        assert graph["saved_native_kl_flags"][0]["requires_grad"]
        assert graph["pg_loss_flags"][0]["device"] == "cpu"
        assert incoming["d_loss_d_pre_tis_pg_loss"] == pytest.approx([m / 7 for m in graph["survivor_masks"]])
        assert backward["d_loss_d_train_logprob"] == pytest.approx([-x for x in backward["d_loss_d_native_kl"]])


def test_aot_compiled_ppo_still_exposes_native_kl_boundary(tmp_path):
    scored = torch.tensor([-1.0, -2.0, -3.0])
    train = torch.tensor([-1.0, -2.1, -2.9], requires_grad=True)
    original = torch.tensor([1, 1, 0])
    native_kl = scored - torch.cat([train])
    masked_kl = torch.where(original.bool(), torch.nan_to_num(native_kl), 0)

    def ppo(value):
        ratio = (-value).exp()
        return torch.maximum(-ratio, -ratio.clamp(0.8, 1.28))

    pg = torch.compile(ppo, backend="aot_eager")(masked_kl)
    actual, source, live = probe._live_kl_input(pg, 64)
    torch.testing.assert_close(actual, native_kl)
    assert source.name() == "SubBackward0" and live.name() == "CatBackward0"


@pytest.mark.parametrize("sink_failure", [False, True])
def test_finalizer_and_actual_scale_are_delegated_once_and_restored(tmp_path, monkeypatch, sink_failure):
    args = _args(tmp_path)
    state = probe._Observation(args, 0, 0)
    model = torch.nn.Linear(2, 2, bias=False)
    model.weight.main_grad = torch.tensor([[2.0, -4.0], [6.0, -8.0]])
    calls = []

    def scale(factor):
        calls.append(("scale", factor.item()))
        model.weight.main_grad.mul_(factor)
        return "native scale result"

    model.scale_gradients = scale
    tokens = torch.tensor(7)

    def native_finalize(chunks, count, *, marker):
        calls.append(("finalize", marker))
        count.fill_(12)  # Explicit CPU delegate fixture; never labelled native DP.
        assert chunks[0].scale_gradients(torch.tensor(1 / 12)) == "native scale result"
        return "native finalizer result"

    monkeypatch.setattr(probe, "_ddp_info", lambda chunk: {"cpu_fixture_only": True})
    if sink_failure:
        monkeypatch.setattr(probe, "_append", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("disk full")))
    result = probe._wrap_finalizer(state, native_finalize)([model], tokens, marker="untouched")
    assert result == "native finalizer result"
    assert calls == [("finalize", "untouched"), ("scale", pytest.approx(1 / 12))]
    assert model.scale_gradients is scale
    torch.testing.assert_close(model.weight.main_grad, torch.tensor([[2.0, -4.0], [6.0, -8.0]]) / 12)
    if not sink_failure:
        before = _records(tmp_path, "finalizer_before")[0]
        scaled = _records(tmp_path, "parameter_gradient_scale")[0]
        assert before["native_local_num_tokens"] == 7 and scaled["native_global_num_tokens"] == 12
        assert scaled["after"]["values"] == pytest.approx([x / 12 for x in scaled["before"]["values"]])
        assert scaled["after"]["parameter_device"] == "cpu"


def test_true_finalizer_failure_not_suppressed_and_scale_restored(tmp_path, monkeypatch):
    model = SimpleNamespace(scale_gradients=lambda factor: None)
    original = model.scale_gradients
    state = probe._Observation(_args(tmp_path), 0, 0)
    monkeypatch.setattr(probe, "_ddp_info", lambda chunk: {})
    def native(chunks, count):
        raise RuntimeError("genuine native failure")
    with pytest.raises(RuntimeError, match="genuine native failure"):
        probe._wrap_finalizer(state, native)([model], torch.tensor(7))
    assert model.scale_gradients is original


def test_before_hook_handles_native_config_reset_without_nested_finalizers(tmp_path, monkeypatch):
    args = _args(tmp_path)
    model = torch.nn.Linear(2, 2, bias=False)
    leaf = torch.optim.AdamW(model.parameters(), lr=2e-6, betas=(0.9, 0.98), eps=1e-8, weight_decay=0.1)
    calls = []
    def native(chunks, count):
        calls.append(count.item())
    config = SimpleNamespace(finalize_model_grads_func=native, grad_scale_func=None)
    monkeypatch.setattr(probe, "_model_config", lambda chunk: config)
    monkeypatch.setattr(probe, "_ddp_info", lambda chunk: {"cpu_fixture_only": True})
    model.scale_gradients = lambda value: None
    probe.before_train(args, 0, 0, [model], leaf, None)
    first = config.finalize_model_grads_func
    probe.before_train(args, 1, 0, [model], leaf, None)
    assert config.finalize_model_grads_func is first
    config.finalize_model_grads_func([model], torch.tensor(7))
    config.finalize_model_grads_func = native  # Same reset as native setup_train_iteration_config.
    probe.before_train(args, 2, 0, [model], leaf, None)
    assert config.finalize_model_grads_func is not first
    config.finalize_model_grads_func([model], torch.tensor(9))
    assert calls == [7, 9]


def test_native_tis_failure_is_not_suppressed(tmp_path, monkeypatch):
    def native(*args, **kwargs):
        raise RuntimeError("true native TIS failure")
    monkeypatch.setattr(probe.swe_tis, "apply_tis", native)
    with pytest.raises(RuntimeError, match="true native TIS failure"):
        probe.tis(_args(tmp_path))


def test_real_cpu_adamw_step_metadata_not_weights(tmp_path):
    parameter = torch.nn.Parameter(torch.tensor([1.0]))
    leaf = torch.optim.AdamW([parameter], lr=2e-6, betas=(0.9, 0.98), eps=1e-8, weight_decay=0.1)
    wrapper = SimpleNamespace(optimizer=leaf)
    recorded = []
    for _ in range(3):
        parameter.grad = torch.tensor([0.25])
        leaf.step()
        recorded.append(probe._optimizer_snapshot(wrapper))
    assert len({row["wrapper_id"] for row in recorded}) == 1
    samples = [row["leaves"][0]["param_groups"][0]["state_sample"][0] for row in recorded]
    assert [row["state_step"] for row in samples] == [1, 2, 3]
    assert len({row["state_id"] for row in samples}) == 1
    group = recorded[-1]["leaves"][0]["param_groups"][0]
    assert group["lr"] == 2e-6 and group["betas"] == [0.9, 0.98] and group["eps"] == 1e-8 and group["weight_decay"] == 0.1
    assert not any(isinstance(value, torch.Tensor) for value in samples[0].values())
    assert "exp_avg" in samples[0]["state_keys"]


def test_optimizer_ack_survives_all_observer_io_errors(tmp_path, monkeypatch):
    args = _args(tmp_path)
    state = probe._Observation(args, 2, 0)
    monkeypatch.setitem(probe._observations, str(tmp_path), state)
    monkeypatch.setattr(probe, "_append", lambda *a, **kw: (_ for _ in ()).throw(BrokenPipeError("pipe")))
    result = {"successful_updates": 3, "bank": 1, "bank_visit": 1}
    calls = []
    def delegate(args, **kwargs):
        calls.append(kwargs["stage"])
        return result
    monkeypatch.setattr(probe.swe_training, "optimizer_step", delegate)
    assert probe.optimizer(args, stage="after_optimizer") is result
    assert calls == ["after_optimizer"]


def test_configuration_uses_existing_flag_carrier_without_recipe_edits(tmp_path):
    from tests.manual.agent_opd.run_swe_opd import _training_args
    task = Path(__file__).resolve().parents[2] / "task_memory/task_2026-11-08_qwen35_swe_full_r256"
    original = json.loads((task / "integration_config.json").read_text())
    original.update(prompt_tokens=114688, response_tokens=16384)
    unchanged = copy.deepcopy(original)
    configured = probe.configure_probe(original, str(tmp_path), "decoder.final_layernorm.weight")
    assert original == unchanged
    assert configured["pairs"] == original["pairs"] and configured["inputs"] == original["inputs"]
    assert configured["training"]["seed"] == original["training"]["seed"]
    assert configured["training"]["rollout_seed"] == original["training"]["rollout_seed"]
    configured["protocol"] = "r256"
    command = _training_args(configured, "A", "http://teacher/generate", tmp_path, "probe-test")
    assert f"{probe._MODULE}.before_train" in command and f"{probe._MODULE}.optimizer" in command and f"{probe._MODULE}.tis" in command
    assert "--swe-native-gradient-parameter-suffix decoder.final_layernorm.weight" in command
    assert "--swe-native-gradient-dir" in command
