"""Replay the native per-token normalization without an optimizer or model weights.

Run with eight CPU/Gloo ranks for the recorded TP2/DP4/CP1/PP1 topology:
  python -m torch.distributed.run --standalone --nproc-per-node=8 --module \
    tests.manual.agent_opd.probe_qwen35_token_normalization \
    --pinned-source /path/to/extracted/megatron --source-receipt /path/to/receipt.json \
    --launch-receipt /path/to/launch.json --native-stdout /path/to/run.log \
    --report /path/to/report.json

The model/log-probability seam is synthetic. Miles' objective, OPD advantage
penalty and D12 MIS hook are unmodified. Selected pinned MCore functions are
compiled from their original AST nodes, with import/configuration/device seams
explicitly recorded. CPU collectives are real; this is not a CUDA/NCCL, model
backward, gradient-clipping, optimizer or historical-gradient replay.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import dataclasses
import datetime
import json
import logging
import os
import platform
import re
import sys
import types
from functools import partial
from pathlib import Path
from unittest.mock import patch

import torch
import torch.distributed as dist
from torch.autograd.variable import Variable

_TASK_ID = "QWEN-REVIEW-NATIVE-DENOMINATOR"
_EXPECTED_FLAGS = {
    "tensor_model_parallel_size": "2",
    "data_parallel_size": "4",
    "context_parallel_size": "1",
    "pipeline_model_parallel_size": "1",
    "calculate_per_token_loss": "True",
    "ddp_average_in_collective": "False",
    "use_distributed_optimizer": "True",
    "num_distributed_optimizer_instances": "1",
    "overlap_grad_reduce": "False",
    "accumulate_allreduce_grads_in_fp32": "True",
    "grad_reduce_in_bf16": "False",
    "bf16": "True",
    "fp16": "False",
    "loss_scale": "None",
    "optimizer_cpu_offload": "False",
    "use_tis": "True",
    "tis_level": "token",
    "tis_mode": "mask",
    "tis_lower_bound": "0.5",
    "tis_upper_bound": "2.0",
    "use_rs": "False",
    "tis_batch_normalize": "False",
    "true_on_policy_mode": "False",
    "use_rollout_logprobs": "False",
    "ddp_reduce_scatter_with_fp32_accumulation": "False",
    "overlap_param_gather": "False",
    "use_megatron_fsdp": "False",
    "use_precision_aware_optimizer": "False",
    "sequence_parallel": "True",
    "qk_layernorm": "True",
}


def _cli():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pinned-source", type=Path, required=True)
    parser.add_argument("--source-receipt", type=Path, required=True)
    parser.add_argument("--launch-receipt", type=Path, required=True)
    parser.add_argument("--native-stdout", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    return parser.parse_args()


def _flags(path):
    found = {}
    pattern = re.compile(r"^\s*(\w+)\s+(?:\.+\s+|\s)(.*?)\s*$")
    with path.open() as stream:
        for number, line in enumerate(stream, 1):
            match = pattern.match(line)
            if match:
                value = {"value": match[2], "line": number}
                if match[1] in found and found[match[1]]["value"] != value["value"]:
                    raise ValueError(f"Conflicting native values for {match[1]}")
                found[match[1]] = value
    for name, expected in _EXPECTED_FLAGS.items():
        if name not in found or found[name]["value"] != expected:
            raise ValueError(f"Required recorded flag {name}={expected}: {found.get(name)}")
    return found


def _parsed_flags(flags):
    values = {}
    for name, item in flags.items():
        value = item["value"]
        if value.startswith("torch.") and hasattr(torch, value[6:]):
            values[name] = getattr(torch, value[6:])
        else:
            try:
                values[name] = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                values[name] = value
    return types.SimpleNamespace(**values)


def _native(path, qualified_name, namespace, evidence):
    """Compile the original function node, without rewriting its body."""
    tree = ast.parse(path.read_text(), filename=str(path))
    body = tree.body
    for name in qualified_name.split("."):
        node = next(item for item in body if isinstance(item, (ast.FunctionDef, ast.ClassDef)) and item.name == name)
        body = node.body
    if not isinstance(node, ast.FunctionDef):
        raise ValueError(f"Expected function: {qualified_name}")
    module = ast.Module(
        body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), node],
        type_ignores=[],
    )
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), namespace)
    evidence.append(
        {
            "path": str(path),
            "function": qualified_name,
            "start": node.lineno,
            "end": node.end_lineno,
            "body_rewritten": False,
        }
    )
    return namespace[node.name]


def _native_class(path, name, namespace, evidence):
    node = next(
        item for item in ast.parse(path.read_text()).body if isinstance(item, ast.ClassDef) and item.name == name
    )
    module = ast.Module(
        body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), node],
        type_ignores=[],
    )
    exec(compile(ast.fix_missing_locations(module), str(path), "exec"), namespace)
    evidence.append(
        {"path": str(path), "class": name, "start": node.lineno, "end": node.end_lineno, "body_rewritten": False}
    )
    return namespace[name]


def _groups():
    rank = dist.get_rank()
    tp_rank, dp_rank = rank % 2, rank // 2
    selected = {}
    for ranks in ([2 * d, 2 * d + 1] for d in range(4)):
        group = dist.new_group(ranks=ranks, backend="gloo")
        if rank in ranks:
            selected["tp"] = group
    for ranks in ([t + 2 * d for d in range(4)] for t in range(2)):
        group = dist.new_group(ranks=ranks, backend="gloo")
        if rank in ranks:
            selected["dp_cp"] = group
    for member in range(8):
        group = dist.new_group(ranks=[member], backend="gloo")
        if rank == member:
            selected["cp"] = selected["pp"] = group
    selected.update(embd=None, pos_embd=None, dp=selected["dp_cp"], tp_dp_cp=dist.group.WORLD)
    return types.SimpleNamespace(**selected), tp_rank, dp_rank


def _args():
    from examples.infra_features.train_infer_mismatch_helper.mis import MisConfig
    from tests.fast.backends.training_utils.loss.loss_test_utils import make_args

    from miles.utils.args.custom_function import CustomFunctionConfig

    return make_args(
        true_on_policy_mode=False,
        calculate_per_token_loss=True,
        global_batch_size=8,
        use_opd=True,
        opd_type="sglang",
        opd_kl_coef=1.0,
        entropy_coef=0.0,
        observe_training_entropy=False,
        eps_clip=0.2,
        eps_clip_high=0.28,
        use_tis=True,
        get_mismatch_metrics=True,
        custom_tis_function_path=CustomFunctionConfig(
            path="examples.infra_features.train_infer_mismatch_helper.mis.compute_mis_weights_with_cp",
            config=MisConfig(
                tis_mode="mask",
                tis_level="token",
                tis_lower_bound=0.5,
                tis_upper_bound=2.0,
                use_rs=False,
                tis_batch_normalize=False,
            ),
        ),
    )


def _fixture(dp_rank, microbatch):
    from miles.backends.training_utils.loss.hub.opd import apply_opd_kl_to_advantages

    length = 4 + dp_rank if microbatch == 0 else 7 + 2 * dp_rank
    positions = torch.arange(length, dtype=torch.float64)
    # Match native rollout tensorization: data/rollout.py uses torch.int for original masks.
    mask = torch.ones(length, dtype=torch.int)
    mask[-1] = 0
    ratios = torch.tensor([0.25, 0.5, 1.0, 1.5, 2.0, 4.0], dtype=torch.float64)
    ratios = ratios[(positions.long() + dp_rank + microbatch) % ratios.numel()]
    # The final DP rank has an entirely TIS-rejected microbatch, but a nonempty original mask.
    if dp_rank == 3 and microbatch == 1:
        ratios.fill_(4.0)
    reverse_kl = (positions + 1 + 2 * dp_rank + microbatch) / 10
    features = torch.stack([(positions + 1) / (column + 1) + dp_rank + microbatch for column in range(4)], dim=1)
    batch = {
        "loss_masks": [mask],
        "total_lengths": [length + 1],
        "response_lengths": [length],
        "unconcat_tokens": [torch.zeros(length + 1, dtype=torch.long)],
        "log_probs": [torch.zeros(length, dtype=torch.float64)],
        "rollout_log_probs": [-ratios.log()],
        "teacher_log_probs": [-reverse_kl],
        "advantages": [torch.zeros(length, dtype=torch.float64)],
        "rollout_mask_sums": [mask.sum()],
    }
    apply_opd_kl_to_advantages(_args(), batch, batch["advantages"], batch["log_probs"])
    kept = mask.double() * ((ratios >= 0.5) & (ratios <= 2.0)).double()
    contributions = reverse_kl * ratios * kept
    return (
        batch,
        features,
        {
            "original_tokens": int(mask.sum()),
            "survivor_tokens": int(kept.sum()),
            "numerator": float(contributions.sum()),
            "gradient_numerator": (contributions[:, None] * features).sum(0),
        },
    )


def _set_miles_groups(state, groups, tp_rank, dp_rank):
    from miles.backends.training_utils.parallel import GroupInfo, set_parallel_state

    set_parallel_state(
        dataclasses.replace(
            state,
            tp=GroupInfo(rank=tp_rank, size=2, group=groups.tp),
            intra_dp=GroupInfo(rank=dp_rank, size=4, group=groups.dp_cp),
            intra_dp_cp=GroupInfo(rank=dp_rank, size=4, group=groups.dp_cp),
            cp=GroupInfo(rank=0, size=1, group=groups.cp),
            pp=GroupInfo(rank=0, size=1, group=groups.pp),
        )
    )


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def main():
    cli = _cli()
    launch = json.loads(cli.launch_receipt.read_text())
    flags = _flags(cli.native_stdout)
    source_receipt = json.loads(cli.source_receipt.read_text())
    if source_receipt["versions"]["megatron-core"] != "0.19.0+eb547f33e":
        raise ValueError("Require the recorded pinned MCore source, not a substituted revision")
    retained = {Path(item["retained"]): item["size"] for item in source_receipt["files"]}
    for relative in (
        "core/utils.py",
        "core/distributed/distributed_data_parallel.py",
        "core/distributed/distributed_data_parallel_config.py",
        "core/distributed/param_and_grad_buffer.py",
        "core/distributed/finalize_model_grads.py",
        "core/pipeline_parallel/schedules.py",
        "core/optimizer/optimizer.py",
        "training/training.py",
    ):
        path = cli.pinned_source / relative
        if path not in retained or path.stat().st_size != retained[path]:
            raise ValueError(f"Source path/size does not match the pinned extraction receipt: {path}")
    if int(os.environ.get("WORLD_SIZE", "0")) != 8:
        raise ValueError("Use eight CPU/Gloo ranks for TP2/DP4/CP1/PP1")
    from tests.fast.backends.training_utils.loss.loss_test_utils import make_parallel_state

    # The existing fixture only assumes a single-rank WORLD after distributed initialization.
    state = make_parallel_state()
    dist.init_process_group(backend="gloo", timeout=datetime.timedelta(seconds=120))
    try:
        groups, tp_rank, dp_rank = _groups()
        _set_miles_groups(state, groups, tp_rank, dp_rank)
        result = _replay(cli, groups, dp_rank, flags)
        ranks = [None] * 8
        dist.all_gather_object(ranks, result)
        if dist.get_rank() == 0:
            report = {
                "task_id": _TASK_ID,
                "status": "INCOMPLETE",
                "replay_status": "PASS",
                "python": platform.python_version(),
                "torch": torch.__version__,
                "executable": sys.executable,
                "argv": sys.argv,
                "launch_receipt": str(cli.launch_receipt),
                "launch_pair": launch["pair"],
                "launch_source_commit": launch["source_commit"],
                "native_stdout": str(cli.native_stdout),
                "resolved_flags": {name: flags[name] for name in _EXPECTED_FLAGS},
                "source_receipt": str(cli.source_receipt),
                "pinned_versions": source_receipt["versions"],
                "ranks": ranks,
                "pinned_torch_runtime": torch.__version__ == source_receipt["versions"]["torch"],
                "limits": [
                    "Synthetic model and selected log-probabilities; no full-model or CUDA/NCCL replay.",
                    "Historical A/B gradient buffers and optimizer consumption were not retained; runtime replay does not retroactively observe them.",
                    "No gradient clipping, optimizer construction, optimizer step, weight update or new training.",
                ],
            }
            _write(cli.report, report)
            print("QWEN35_NATIVE_TOKEN_NORMALIZATION", report["status"], str(cli.report), flush=True)
        return 0
    finally:
        dist.destroy_process_group()


class _Model(torch.nn.Module):
    """Synthetic selected log-probabilities; no tokenizer, vocabulary or model weights."""

    def __init__(self):
        super().__init__()
        self.theta = torch.nn.Parameter(torch.zeros(4, dtype=torch.float64))
        self.model_type = "synthetic selected log-probabilities"

    def set_input_tensor(self, value):
        if value != [None]:
            raise ValueError("This replay only supports PP1")

    def forward(self, features):
        return features @ self.theta


class _DataParallelBase(torch.nn.Module):
    def __init__(self, config, module):
        super().__init__()
        self.config, self.module = config, module

    def forward(self, *args):
        return self.module(*args)


class _RerunChecks:
    """Validation seam only: reject a nonfinite synthetic gradient, never retry."""

    def validate_result(self, *, result, rejection_func, **kwargs):
        if rejection_func(result).item():
            raise AssertionError(kwargs["message"])


@contextlib.contextmanager
def _gloo_coalescing(group, *, async_ops):
    # Gloo lacks NCCL's batched coalescing API. Do not replace the actual collective.
    if async_ops:
        raise ValueError("The recorded non-overlap path requires synchronous collectives")
    yield None


def _configuration(flags):
    native = _parsed_flags(flags)
    return types.SimpleNamespace(
        calculate_per_token_loss=native.calculate_per_token_loss,
        sequence_parallel=native.sequence_parallel,
        qk_layernorm=native.qk_layernorm,
        timers=None,
        no_sync_func=None,
        grad_scale_func=None,
        finalize_model_grads_func=None,
        enable_autocast=False,
        overlap_moe_expert_parallel_comm=False,
        deallocate_pipeline_outputs=True,
        num_moe_experts=None,
        mtp_num_layers=None,
        moe_router_enable_expert_bias=False,
        moe_router_load_balancing_type="none",
    )


def _load_native(cli, groups):
    root, evidence, collectives = cli.pinned_source, [], []
    module = types.ModuleType("qwen_normalization_native")
    sys.modules[module.__name__] = module
    ns = module.__dict__
    ns.update(
        torch=torch,
        Variable=Variable,
        dataclass=dataclasses.dataclass,
        dataclasses=dataclasses,
        contextmanager=contextlib.contextmanager,
        contextlib=contextlib,
        partial=partial,
        logging=logging,
        logger=logging.getLogger(_TASK_ID),
        nullcontext=contextlib.nullcontext,
        _BaseDataParallel=_DataParallelBase,
        has_config_logger_enabled=lambda config: False,
        is_graph_capturing=lambda: False,
        log_single_rank=lambda *args, **kwargs: None,
        get_rerun_state_machine=lambda: _RerunChecks(),
        _coalescing_manager=_gloo_coalescing,
        get_pp_last_rank=lambda group: dist.get_process_group_ranks(group)[-1],
        get_tensor_model_parallel_group_if_none=lambda group: group,
        parallel_state=types.SimpleNamespace(get_embedding_group=lambda **kwargs: None),
        set_current_microbatch=lambda model, index: None,
        _get_experimental_attention_variant_loss_scale_func=lambda config: None,
    )
    for name in ("get_attr_wrapped_model", "get_model_type", "get_model_config", "get_pg_size"):
        _native(root / "core/utils.py", name, ns, evidence)
    ddp_path = root / "core/distributed/distributed_data_parallel.py"
    buffer_path = root / "core/distributed/param_and_grad_buffer.py"
    _native_class(
        root / "core/distributed/distributed_data_parallel_config.py", "DistributedDataParallelConfig", ns, evidence
    )
    _native(root / "training/training.py", "get_megatron_ddp_config", ns, evidence)
    for name in ("_ParamAndGradBucket", "_ParamAndGradBucketGroup"):
        _native_class(buffer_path, name, ns, evidence)
    for name in ("shard_buffer", "partition_buckets"):
        _native(buffer_path, name, ns, evidence)
    scale_buffer = _native(buffer_path, "_ParamAndGradBuffer.scale_gradients", ns, evidence)

    @dataclasses.dataclass(frozen=True)
    class BufferKey:
        param_dtype: torch.dtype
        grad_dtype: torch.dtype
        is_expert_parallel: bool = False

    def group_params(params, grad_reduce_in_fp32, **kwargs):
        if len(params) != 1 or not grad_reduce_in_fp32:
            raise ValueError("The CPU allocation seam supports one dense parameter and FP32 communication")
        return {BufferKey(params[0].dtype, torch.float32): (params, [0])}

    class CPUBuffer:
        scale_gradients = scale_buffer

        def __init__(
            self,
            ddp_config,
            param_dtype,
            grad_dtype,
            named_params,
            group,
            bucket_size,
            names,
            scaling,
            indices,
            nccl_ub,
            pg_collection,
            param_layout,
        ):
            self.ddp_config, self.param_dtype = ddp_config, param_dtype
            self.data_parallel_group, self.data_parallel_world_size = group, group.size()
            self.params = [param for param, _ in named_params]
            self.grad_data = torch.zeros(4, dtype=grad_dtype)
            self.extra_main_grads = []
            self.params[0].main_grad = self.grad_data
            self.buckets = [
                ns["_ParamAndGradBucket"](
                    self.params,
                    None,
                    self.grad_data,
                    0,
                    4,
                    scaling,
                    0,
                    {self.params[0]: (0, 4, 0)},
                    [],
                )
            ]

    def process_groups(pg_collection, config, ddp_config):
        return {
            "dp_group": groups.dp_cp,
            "dp_cp_group": groups.dp_cp,
            "intra_dp_cp_group": groups.dp_cp,
            "expt_dp_group": groups.dp_cp,
            "intra_expt_dp_group": groups.dp_cp,
            "tp_group": groups.tp,
            "pp_group": groups.pp,
            "ep_group": groups.cp,
        }

    def reduce_scatter(output, input, **kwargs):
        collectives.append(
            {
                "kind": "reduce_scatter_tensor",
                "op": str(kwargs["op"]),
                "size": kwargs["group"].size(),
                "async_op": kwargs["async_op"],
                "dtype": str(input.dtype),
            }
        )
        return dist.reduce_scatter_tensor(output, input, **kwargs)

    ns.update(
        _ParamAndGradBuffer=CPUBuffer,
        group_params_for_buffers=group_params,
        ProcessGroupCollection=type(
            "Groups", (types.SimpleNamespace,), {"setup_process_groups_for_ddp": staticmethod(process_groups)}
        ),
        dist_reduce_scatter_func=reduce_scatter,
    )
    ddp_type = _native_class(ddp_path, "DistributedDataParallel", ns, evidence)
    finalizer_path = root / "core/distributed/finalize_model_grads.py"
    for item in ast.parse(finalizer_path.read_text()).body:
        if isinstance(item, ast.FunctionDef):
            _native(finalizer_path, item.name, ns, evidence)
    schedule_path = root / "core/pipeline_parallel/schedules.py"
    for name in (
        "custom_backward",
        "forward_step_calc_loss",
        "forward_step",
        "backward_step",
        "check_first_val_step",
        "forward_backward_no_pipelining",
    ):
        _native(schedule_path, name, ns, evidence)
    optimizer_path = root / "core/optimizer/optimizer.py"
    ns["native_scale_loss"] = _native(optimizer_path, "MegatronOptimizer.scale_loss", ns, evidence)
    ns["native_get_loss_scale"] = _native(optimizer_path, "MixedPrecisionOptimizer.get_loss_scale", ns, evidence)
    return ns, ddp_type, group_params, evidence, collectives


def _reference(dp_rank):
    fixtures = [_fixture(dp_rank, index) for index in range(2)]
    local = torch.tensor(
        [sum(ref[key] for _, _, ref in fixtures) for key in ("original_tokens", "survivor_tokens", "numerator")],
        dtype=torch.float64,
    )
    gradient = sum(ref["gradient_numerator"] for _, _, ref in fixtures)
    return fixtures, local, gradient


def _run_case(ns, ddp_type, group_params, groups, fixtures, denominator, reference, wrong_count, flags):
    from miles.backends.training_utils.loss.hub import losses
    from miles.backends.training_utils.loss.objective import loss_function

    model, config = _Model(), _configuration(flags)
    ddp_config = ns["get_megatron_ddp_config"](_parsed_flags(flags))
    grouping = group_params([model.theta], ddp_config.grad_reduce_in_fp32)
    key = next(iter(grouping))
    layout = types.SimpleNamespace(
        layouts={key: types.SimpleNamespace(param_index_map={model.theta: (0, 4, 0)}, param_indices=[0])}
    )
    ddp = ddp_type(config=config, ddp_config=ddp_config, module=model, pg_collection=groups, full_param_layout=layout)
    assert ddp.buffers[0].buckets[0].gradient_scaling_factor == 1.0
    scale_state = types.SimpleNamespace(grad_scaler=None, _scale_one=torch.tensor([1.0]))
    scale_state.get_loss_scale = types.MethodType(ns["native_get_loss_scale"], scale_state)
    config.grad_scale_func = partial(ns["native_scale_loss"], scale_state)
    counts, finalization = [], {}

    def finalize(models, num_tokens, **kwargs):
        finalization["local_original_or_control_count"] = int(num_tokens)
        finalization["pre_reduce_gradient"] = models[0].buffers[0].grad_data.tolist()
        ns["finalize_model_grads"](models, num_tokens, **kwargs)
        finalization["global_original_or_control_count"] = int(num_tokens)
        finalization["scaling_factor"] = float((1.0 / num_tokens).item())

    config.finalize_model_grads_func = finalize

    def step(iterator, ddp_model):
        batch, features, ref = next(iterator)
        output = ddp_model(features)

        def loss_callback(value):
            loss, count, log = loss_function(_args(), batch, 2, value, apply_megatron_loss_scaling=True)
            assert int(count) == ref["original_tokens"]
            assert torch.equal(
                batch["loss_masks"][0],
                torch.cat([torch.ones(features.size(0) - 1, dtype=torch.int), torch.zeros(1, dtype=torch.int)]),
            )
            counts.append(
                {
                    "original_tokens": int(count),
                    "survivor_tokens": ref["survivor_tokens"],
                    "loss_numerator": float(loss.detach()),
                }
            )
            if wrong_count:
                count = count.new_tensor(ref["survivor_tokens"])
            return loss, count, log

        return output, loss_callback

    mtp = types.ModuleType("megatron.core.transformer.multi_token_prediction")
    mtp.MTPLossAutoScaler = object
    original_zeros = torch.zeros

    # Capture the original allocator before patching, to prevent recursion in the seam.
    def cpu_zeros(*args, **kwargs):
        if kwargs.get("device") == "cuda":
            kwargs["device"] = "cpu"
        return original_zeros(*args, **kwargs)

    with patch.dict(sys.modules, {mtp.__name__: mtp}), patch.object(
        torch, "zeros", side_effect=cpu_zeros
    ), patch.object(torch.cuda, "current_stream", return_value=object()), patch.object(
        losses, "get_log_probs_and_entropy", side_effect=lambda value, **kwargs: {"log_probs": [value]}
    ):
        ns["forward_backward_no_pipelining"](
            forward_step_func=step,
            data_iterator=iter(fixtures),
            model=ddp,
            num_microbatches=2,
            seq_length=1,
            micro_batch_size=1,
            pg_collection=groups,
        )
    local_shard = ddp.buffers[0].grad_data.chunk(4)[groups.dp_cp.rank()].clone()
    gathered = [torch.empty_like(local_shard) for _ in range(4)]
    dist.all_gather(gathered, local_shard, group=groups.dp_cp)
    actual = torch.cat(gathered).double()
    expected = reference / denominator
    # Existing Miles native loss snapshot tolerance; buffer communication is FP32.
    torch.testing.assert_close(actual, expected, rtol=0, atol=2e-6)
    assert finalization["global_original_or_control_count"] == int(denominator)
    assert model.theta.grad is None, "Native DDP post-hooks must clear leaf grads after accumulation"
    return {
        "microbatches": counts,
        "finalization": finalization,
        "actual_gradient": actual.tolist(),
        "expected_gradient": expected.tolist(),
        "max_abs_error": float((actual - expected).abs().max()),
        "native_ddp_config": {
            name: getattr(ddp_config, name)
            for name in (
                "average_in_collective",
                "use_distributed_optimizer",
                "grad_reduce_in_fp32",
                "overlap_grad_reduce",
                "reduce_scatter_with_fp32_accumulation",
            )
        },
        "bucket_gradient_scaling_factor": ddp.buffers[0].buckets[0].gradient_scaling_factor,
        "loss_scaling_factor": float(scale_state.get_loss_scale().item()),
    }


def _replay(cli, groups, dp_rank, flags):
    ns, ddp_type, group_params, evidence, collectives = _load_native(cli, groups)
    fixtures, totals, reference_gradient = _reference(dp_rank)
    dist.all_reduce(totals, group=groups.dp_cp)
    dist.all_reduce(reference_gradient, group=groups.dp_cp)
    original_count, survivor_count, numerator = totals.tolist()
    assert original_count > survivor_count > 0
    correct = _run_case(
        ns,
        ddp_type,
        group_params,
        groups,
        fixtures,
        original_count,
        reference_gradient,
        wrong_count=False,
        flags=flags,
    )
    wrong = _run_case(
        ns, ddp_type, group_params, groups, fixtures, survivor_count, reference_gradient, wrong_count=True, flags=flags
    )
    actual_wrong = torch.tensor(wrong["actual_gradient"], dtype=torch.float64)
    actual_correct = torch.tensor(correct["actual_gradient"], dtype=torch.float64)
    if torch.allclose(actual_correct, actual_wrong, rtol=0, atol=2e-6):
        raise AssertionError("Negative control did not detect survivor-token normalization")
    assert len(collectives) == 2 and all(item["size"] == 4 and not item["async_op"] for item in collectives)
    return {
        "rank": dist.get_rank(),
        "dp_rank": dp_rank,
        "original_tokens": int(original_count),
        "survivor_tokens": int(survivor_count),
        "global_numerator": numerator,
        "reference_mean": numerator / original_count,
        "wrong_survivor_mean": numerator / survivor_count,
        "correct": correct,
        "wrong_survivor_negative_control": wrong,
        "negative_control_gradient_distance": float((actual_correct - actual_wrong).abs().max()),
        "collectives": collectives,
        "native_source_functions": evidence,
        "seams": [
            "Synthetic four-parameter selected-logprob model; full model/vocabulary kernels excluded.",
            "CPU one-bucket allocation/layout and process-group wiring; native DDP constructor and gradient post-hooks execute.",
            "Native bucket reduce-scatter executes real synchronous torch Gloo reduce_scatter_tensor; NCCL coalescing is a null batching context.",
            "CPU token-count allocation replaces the native CUDA allocation; current_stream sentinel has no CUDA events to wait for.",
            "No MTP/MoE/graph capture; import/logger/finite-gradient-check seams do not replace normalization math.",
            "Native optimizer get_loss_scale/scale_loss execute on a state-only unity-scale seam; no optimizer constructor or step.",
        ],
    }


if __name__ == "__main__":
    raise SystemExit(main())
