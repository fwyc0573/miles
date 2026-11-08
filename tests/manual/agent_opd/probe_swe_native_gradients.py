"""Opt-in observations of the real SWE loss graph and Megatron finalization.

The three existing hooks delegate production TIS/optimizer behavior unchanged.
Only the native finalizer callable and each DDP instance's scale method are
wrapped; no collective, objective, model forward or optimizer step is added.
CPU executions test probe mechanics only, never native gradient acceptance.

Prepare a separate three-update probe configuration (does not launch a job)::

    python -m tests.manual.agent_opd.probe_swe_native_gradients \
        --config integration_config.json --output probe_config.json \
        --evidence-dir /mounted/task/evidence/native-gradients \
        --parameter-suffix decoder.final_layernorm.weight
"""

import argparse
import copy
import functools
import hashlib
import inspect
import json
import time
from dataclasses import dataclass, field
from pathlib import Path

import torch
import torch.distributed as dist

from miles.utils.args.schema import A, Arg, BaseConfig
from tests.manual.agent_opd import swe_replay, swe_tis, swe_training


_MODULE = "tests.manual.agent_opd.probe_swe_native_gradients"


class GradientProbeConfig(BaseConfig):
    swe_native_gradient_dir: A[str, Arg()]
    swe_native_gradient_parameter_suffix: A[str, Arg()]
    swe_native_gradient_slice_size: A[int, Arg()] = 8
    swe_native_gradient_graph_nodes: A[int, Arg()] = 64


class NativeGradientProbeConfig(swe_replay.SweReplayConfig, swe_tis.SweTISConfig, GradientProbeConfig):
    """One CLI namespace shared by all three observational lifecycle hooks."""


@dataclass
class _Observation:
    args: object
    rollout_id: int
    step_id: int
    graph_calls: int = 0
    handles: list = field(default_factory=list)
    finalizer_configs: dict = field(default_factory=dict)
    samples: dict = field(default_factory=dict)


_observations = {}


def _rank():
    return dist.get_rank() if dist.is_initialized() else 0


def _append(state, event, **values):
    path = Path(state.args.swe_native_gradient_dir)
    path.mkdir(parents=True, exist_ok=True)
    record = dict(event=event, rank=_rank(), rollout_id=state.rollout_id,
                  step_id=state.step_id, timestamp=time.time(), **values)
    with (path / f"native_gradients_rank_{_rank()}.jsonl").open("a") as stream:
        stream.write(json.dumps(record, allow_nan=False) + "\n")


def _soft(state, event, function):
    """Observer failures do not escape a native hook or backward callback."""
    try:
        return function()
    except Exception as error:
        try:
            _append(state, "observer_unverified", stage=event,
                    error_type=type(error).__name__, error=str(error))
        except Exception:
            pass
        return None


def _scalar(value):
    return value.detach().item() if isinstance(value, torch.Tensor) else value


def _class_info(value):
    cls = type(value)
    return f"{cls.__module__}.{cls.__qualname__}"


def _callable_info(function):
    if isinstance(function, functools.partial):
        return {"partial": _callable_info(function.func), "keywords": {
            name: _callable_info(value) for name, value in function.keywords.items() if callable(value)
        }}
    path = inspect.getsourcefile(function)
    return {"name": f"{function.__module__}.{function.__qualname__}", "path": path,
            "source_sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest() if path else None}


def _tensor_flags(values):
    return [{"requires_grad": x.requires_grad, "is_leaf": x.is_leaf,
             "grad_fn": x.grad_fn.name() if x.grad_fn is not None else None,
             "dtype": str(x.dtype), "device": str(x.device), "shape": list(x.shape)} for x in values]


def _samples(tensor, indices):
    return tensor.detach().flatten()[indices].float().cpu().tolist()


def _group_info(group):
    # All calls are local process-group metadata reads, not communication.
    return {"ranks": dist.get_process_group_ranks(group),
            "size": dist.get_world_size(group), "backend": str(dist.get_backend(group))}


def _ddp_info(model):
    return {"class": _class_info(model), "dp_cp": _group_info(model.dp_cp_group),
            "tp": _group_info(model.tp_group),
            "native_scale_delegate": _callable_info(model.scale_gradients),
            "native_sync_delegate": _callable_info(model.finish_grad_sync),
            "config": {name: getattr(model.ddp_config, name) for name in (
                "average_in_collective", "use_distributed_optimizer", "overlap_grad_reduce",
                "num_distributed_optimizer_instances")},
            "buffers": [{"class": _class_info(buffer),
                         "gradient_scaling_factor": _scalar(buffer.gradient_scaling_factor),
                         "data_parallel_group": _group_info(buffer.data_parallel_group)}
                        for buffer in model.buffers + model.expert_parallel_buffers]}


def _parameter(model, suffix):
    matches = [(name, p) for name, p in model.named_parameters() if name.endswith(suffix)]
    if len(matches) != 1:
        raise ValueError(f"Gradient parameter suffix must match once; got {[name for name, _ in matches]}")
    return matches[0]


def _parameter_slice(model, args):
    name, parameter = _parameter(model, args.swe_native_gradient_parameter_suffix)
    gradient = parameter.main_grad
    indices = torch.arange(min(args.swe_native_gradient_slice_size, gradient.numel()), device=gradient.device)
    return {"parameter": name, "parameter_device": str(parameter.device),
            "parameter_requires_grad": parameter.requires_grad, "gradient_attr": "main_grad",
            "gradient_dtype": str(gradient.dtype), "indices": indices.cpu().tolist(),
            "values": _samples(gradient, indices)}


def _wrap_scale(state, model, native_scale, num_tokens, chunk):
    @functools.wraps(native_scale)
    def scale(factor, *args, **kwargs):
        before = _soft(state, "scale_before", lambda: _parameter_slice(model, state.args))
        result = native_scale(factor, *args, **kwargs)
        _soft(state, "scale_after", lambda: _append(
            state, "parameter_gradient_scale", chunk=chunk, factor=_scalar(factor),
            factor_dtype=str(factor.dtype) if isinstance(factor, torch.Tensor) else type(factor).__name__,
            native_global_num_tokens=_scalar(num_tokens), before=before,
            after=_parameter_slice(model, state.args)))
        return result
    return scale


def _wrap_finalizer(state, native_finalize):
    @functools.wraps(native_finalize)
    def finalize(model, num_tokens=None, *args, **kwargs):
        _soft(state, "finalizer_before", lambda: _append(
            state, "finalizer_before", native_local_num_tokens=_scalar(num_tokens),
            delegate=_callable_info(native_finalize), topology=[_ddp_info(chunk) for chunk in model]))
        installed = []
        for index, chunk in enumerate(model):
            def install(chunk=chunk, index=index):
                original = chunk.scale_gradients
                replacement = _wrap_scale(state, chunk, original, num_tokens, index)
                chunk.scale_gradients = replacement
                installed.append((chunk, original))
            _soft(state, "scale_install", install)
        try:
            result = native_finalize(model, num_tokens, *args, **kwargs)
        finally:
            for chunk, original in installed:
                _soft(state, "scale_restore", lambda chunk=chunk, original=original:
                      setattr(chunk, "scale_gradients", original))
        _soft(state, "finalizer_after", lambda: _append(
            state, "finalizer_after", native_global_num_tokens=_scalar(num_tokens)))
        return result
    return finalize


def _model_config(model):
    # Defer the optional native dependency; never replace its implementation.
    from megatron.core.utils import get_model_config

    return get_model_config(model)


def before_train(args, rollout_id, step_id, model, optimizer, opt_param_scheduler):
    """Install observations only on the configured native finalizer seam."""
    # Optional Megatron import is deferred; CPU probe tests do not initialize it.
    state = _observations.get(args.swe_native_gradient_dir)
    if state is None:
        state = _Observation(args, rollout_id, step_id)
        _observations[args.swe_native_gradient_dir] = state
    state.args, state.rollout_id, state.step_id, state.graph_calls = args, rollout_id, step_id, 0
    state.samples.clear()
    for handle in state.handles:
        _soft(state, "graph_hook_cleanup", handle.remove)
    state.handles.clear()

    def install():
        for chunk in model:
            config = _model_config(chunk)
            current = config.finalize_model_grads_func
            previous = state.finalizer_configs.get(id(config))
            if previous is None or current is not previous:
                wrapped = _wrap_finalizer(state, current)
                config.finalize_model_grads_func = wrapped
                state.finalizer_configs[id(config)] = wrapped
        _append(state, "before_train", optimizer=_optimizer_snapshot(optimizer),
                model_classes=[_class_info(chunk) for chunk in model],
                grad_scale_delegate=_callable_info(config.grad_scale_func) if config.grad_scale_func else None)

    _soft(state, "before_train", install)


def _live_kl_input(pg_loss, limit):
    """Find the saved actual native s-l tensor without traversing model graphs.

    Native policy_loss's nan_to_num saves its differentiable SubBackward input.
    This boundary is outside compiled PPO math, including AOTAutograd. The
    baseline edge must be absent and the live logprob edge must be CatBackward.
    No graph/source substitution is attempted if this observation is unavailable.
    """
    pending, visited, matches = [pg_loss.grad_fn], set(), []
    while pending and len(visited) < limit:
        node = pending.pop()
        if node is None or node in visited:
            continue
        visited.add(node)
        name = node.name()
        if name == "NanToNumBackward0":
            value = node._saved_self
            source = value.grad_fn
            if source is not None and source.name() == "SubBackward0":
                edges = source.next_functions
                if len(edges) == 2 and edges[0][0] is None and edges[1][0] is not None and edges[1][0].name() == "CatBackward0":
                    matches.append((value, source, edges[1][0]))
                    continue
        if name == "CatBackward0":
            continue
        pending.extend(child for child, _ in node.next_functions)
    if len(matches) != 1:
        raise ValueError(f"Actual native KL/logprob graph boundary unverified: {len(matches)} matches")
    return matches[0]


def _observe_graph(state, args, pg_loss, result, kwargs):
    actual_kl, subtraction, live_logprob = _live_kl_input(pg_loss, args.swe_native_gradient_graph_nodes)
    masks = result[2]["mask_evidence"]
    original = torch.cat(masks["original_masks"])
    retained = torch.cat(masks["survivor_masks"])
    positions = torch.arange(pg_loss.numel(), device=pg_loss.device)
    chosen = []
    for eligible in (original.bool() & retained.bool(), original.bool() & ~retained.bool()):
        chosen.append(positions[eligible][:args.swe_native_gradient_slice_size])
    indices = torch.cat(chosen).unique(sorted=True)
    state.graph_calls += 1
    call = state.graph_calls
    state.samples[call] = {"sample_indices": kwargs["sample_indices"], "indices": indices.cpu().tolist()}
    _append(state, "live_loss_graph", call=call, sample_indices=kwargs["sample_indices"],
            native_kl_node=subtraction.name(), live_logprob_node=live_logprob.name(),
            detached_baseline_edge=subtraction.next_functions[0][0] is None,
            pg_loss_flags=_tensor_flags([pg_loss]),
            saved_native_kl_flags=_tensor_flags([actual_kl]),
            scored_student_flags=_tensor_flags(kwargs["train_log_probs"]),
            teacher_flags=_tensor_flags(kwargs["teacher_log_probs"]),
            behavior_flags=_tensor_flags(kwargs["rollout_log_probs"]),
            original_mask_flags=_tensor_flags(kwargs["loss_masks"]),
            survivor_mask_flags=_tensor_flags(result[1]), indices=indices.cpu().tolist(),
            actual_native_s_minus_l=_samples(actual_kl, indices),
            original_masks=_samples(original, indices), survivor_masks=_samples(retained, indices),
            original_tokens=int(original.sum().item()), surviving_tokens=int(retained.sum().item()))

    def token_gradient(grad_inputs, grad_outputs):
        _soft(state, "live_logprob_backward", lambda: _append(
            state, "live_logprob_backward", call=call, indices=indices.cpu().tolist(),
            baseline_input_gradient_is_none=grad_inputs[0] is None,
            d_loss_d_train_logprob=_samples(grad_inputs[1], indices),
            d_loss_d_native_kl=_samples(grad_outputs[0], indices),
            boundary="after_local_loss_reduction_before_native_parameter_finalization"))
        return None

    def pg_gradient(gradient):
        _soft(state, "post_tis_backward", lambda: _append(
            state, "post_tis_backward", call=call, indices=indices.cpu().tolist(),
            d_loss_d_pre_tis_pg_loss=_samples(gradient, indices)))
        return None

    state.handles.extend([subtraction.register_hook(token_gradient), pg_loss.register_hook(pg_gradient)])


def tis(args, **kwargs):
    """Delegate exact native TIS, then attach non-modifying graph observations."""
    result = swe_tis.apply_tis(args, **kwargs)
    state = _observations.get(args.swe_native_gradient_dir)
    if state is not None:
        _soft(state, "live_loss_graph", lambda: _observe_graph(state, args, kwargs["pg_loss"], result, kwargs))
    return result


def _optimizer_leaves(optimizer):
    if "chained_optimizers" in vars(optimizer):
        return [leaf for child in optimizer.chained_optimizers for leaf in _optimizer_leaves(child)]
    if "optimizer" in vars(optimizer):
        return _optimizer_leaves(optimizer.optimizer)
    return [optimizer]


def _optimizer_snapshot(optimizer):
    leaves = []
    for leaf in _optimizer_leaves(optimizer):
        groups = []
        for group in leaf.param_groups:
            states = []
            # Observe one existing state per group, never copy moment/weight tensors.
            for index, parameter in enumerate(group["params"]):
                if parameter in leaf.state and leaf.state[parameter]:
                    value = leaf.state[parameter]
                    states.append({"param_index": index, "parameter_id": id(parameter),
                                   "state_id": id(value), "state_keys": sorted(value),
                                   "state_step": _scalar(value["step"]) if "step" in value else None})
                    break
            groups.append({"lr": group["lr"], "betas": list(group["betas"]), "eps": group["eps"],
                           "weight_decay": group["weight_decay"], "param_count": len(group["params"]),
                           "group_step": _scalar(group["step"]) if "step" in group else None,
                           "group_keys": sorted(group), "state_sample": states})
        leaves.append({"class": _class_info(leaf), "id": id(leaf), "state_id": id(leaf.state),
                       "param_groups": groups,
                       "adam_w_mode": leaf.adam_w_mode if "adam_w_mode" in vars(leaf) else None})
    return {"wrapper_class": _class_info(optimizer), "wrapper_id": id(optimizer), "leaves": leaves}


def _source_inputs(data_iterator):
    data = data_iterator[0].rollout_data
    return {name: _tensor_flags(data[name]) for name in (
        "teacher_log_probs", "rollout_log_probs", "log_probs", "advantages", "loss_masks")}


def _graph_source_values(state, data_iterator):
    data = data_iterator[0].rollout_data
    by_index = {sample_index: index for index, sample_index in enumerate(data["sample_indices"])}
    for call, sample in state.samples.items():
        rows = [by_index[index] for index in sample["sample_indices"]]
        values = {}
        for name in ("teacher_log_probs", "rollout_log_probs", "log_probs", "advantages"):
            tensor = torch.cat([data[name][row] for row in rows])
            indices = torch.tensor(sample["indices"], device=tensor.device)
            values[name] = _samples(tensor, indices)
        _append(state, "live_graph_source_values", call=call,
                sample_indices=sample["sample_indices"], indices=sample["indices"], **values)


def optimizer(args, **kwargs):
    """Preserve mandatory D7, native success ACK and its original driver signal."""
    state = _observations.get(args.swe_native_gradient_dir)
    if state is not None:
        if kwargs["stage"] == "before_optimizer":
            _soft(state, "graph_source_values", lambda: _graph_source_values(state, kwargs["data_iterator"]))
        _soft(state, "optimizer_boundary", lambda: _append(
            state, "optimizer_boundary", stage=kwargs["stage"],
            source_inputs=_source_inputs(kwargs["data_iterator"]),
            sample_indices=kwargs["data_iterator"][0].rollout_data["sample_indices"],
            metadata=[{name: row[name] for name in (
                "swe_bank", "swe_bank_visit", "swe_successful_before", "swe_slot", "sample_index")}
                      for row in kwargs["data_iterator"][0].rollout_data["metadata"]],
            optimizer=_optimizer_snapshot(kwargs["optimizer"])))
    result = swe_training.optimizer_step(args, **kwargs)
    if state is not None and kwargs["stage"] == "after_optimizer":
        _soft(state, "optimizer_ack", lambda: _append(state, "optimizer_ack", native_result=result))
    return result


def training_protocol(args):
    """Explicit observational TIS adapter; delegate every frozen science check."""
    hook = args.custom_tis_function_path
    if hook.path != f"{_MODULE}.tis":
        raise ValueError("Native gradient probe requires its explicitly delegating TIS hook")
    fields = swe_tis.SweTISConfig.model_fields
    native_config = swe_tis.SweTISConfig.model_validate({name: dict(hook.config)[name] for name in fields})
    native_hook = hook.model_copy(update={"path": "tests.manual.agent_opd.swe_tis.apply_tis", "config": native_config})
    return swe_replay.training_protocol(args.model_copy(update={"custom_tis_function_path": native_hook}))


before_train.config_class = NativeGradientProbeConfig
tis.config_class = NativeGradientProbeConfig
optimizer.config_class = NativeGradientProbeConfig
optimizer.training_protocol = training_protocol


def configure_probe(config, evidence_dir, parameter_suffix, slice_size=8):
    """Copy only the explicit probe shape/hooks; retain sources, weights and seeds."""
    result = copy.deepcopy(config)
    result["training"].update(run_kind="smoke", successful_updates=3, bank_slots=8, bank_uses=2)
    result["tis"].update(
        custom_megatron_before_train_step_hook_path=f"{_MODULE}.before_train",
        custom_megatron_optimizer_step_hook_path=f"{_MODULE}.optimizer",
        custom_tis_function_path=f"{_MODULE}.tis",
        swe_native_gradient_dir=str(evidence_dir),
        swe_native_gradient_parameter_suffix=parameter_suffix,
        swe_native_gradient_slice_size=slice_size,
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--parameter-suffix", required=True)
    parser.add_argument("--slice-size", type=int, default=8)
    args = parser.parse_args()
    result = configure_probe(json.loads(args.config.read_text()), args.evidence_dir, args.parameter_suffix, args.slice_size)
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
