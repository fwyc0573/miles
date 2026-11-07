"""Exercise native eval scorer and inference memory restore with tiny tensors.

CPU mode injects zero-filled remaps and exercises orchestration with native CPU
tensor serialization; it does not qualify CUDA IPC. CUDA mode uses real TMS
allocations and native CUDA IPC buckets in separate processes sharing one GPU. Neither
mode loads Qwen, launches a server, trains Qwen, or qualifies the formal run.

The driver, actor score/sleep/wake/switch, TensorBackuper, and SGLang scheduler
release/resume methods are read from the installed sources without edits. The
model and pipeline are the existing 8-token score fixture; CUDA kernels use the
torch probability backend. DDP allocation policy is represented explicitly by
the native param_buffer/default/grad_buffer TMS tags, not a Megatron optimizer.

Examples, from the repository root:
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python3 -B -m \
    tests.manual.agent_opd.probe_eval_restore --mode cpu --report /path/to/report.json
  /opt/sglang/bin/python3 -B -m tests.manual.agent_opd.probe_eval_restore \
    --mode cuda --gpu-id 0 --report /path/to/report.json

An equality failure produces exit status 1 after both boundaries are measured.
The native _train_actor restore/forward control stops before optimizer work and
is separate from the untouched scorer. Baseline and post-sleep scores use the
same native scorer, inputs and full-vocabulary probability definition. Two
same-version cycles run the native placement-group publication transaction.
Control RPC uses local pipes, not Ray/HTTP; tensor transport is not replaced.
Adam state is initialized without any optimizer step.
"""

from __future__ import annotations

import argparse
import ast
import asyncio
import base64
import copy
import dataclasses
import gc
import importlib.util
import json
import logging
import multiprocessing as mp
import os
import sys
import tempfile
import time
import traceback
import uuid
from contextlib import contextmanager, nullcontext
from multiprocessing.connection import wait
from pathlib import Path
from types import SimpleNamespace

_ROOT = Path(__file__).resolve().parents[3]
_TASK_ID = "QWEN-P3-EVAL-RESTORE"


class _TrainingForwardObserved(BaseException):
    """Stop the native training call immediately after its logprob forward."""

    def __init__(self, scores):
        super().__init__("Synthetic control stopped after native training logprob forward; no optimizer step")
        self.scores = scores


class _WorkerError(RuntimeError):
    def __init__(self, method, error, evidence):
        super().__init__(error)
        self.method = method
        self.evidence = evidence


def _score_receipt(torch, values):
    """Own report comparisons on CPU, independent of native output residency."""
    return torch.cat(values).detach().to(device="cpu", copy=True)


def _published_weight_info(model):
    """Snapshot the actual startup addresses; never refresh after a weight load."""
    return {name: (param.data_ptr(), param.numel(), param.element_size())
            for name, param in model.named_parameters()}


def _tensor_bytes_equal(torch, actual, expected):
    actual, expected = actual.detach().cpu(), expected.detach().cpu()
    return (actual.dtype == expected.dtype and actual.shape == expected.shape
            and torch.equal(actual.contiguous().reshape(-1).view(torch.uint8),
                            expected.contiguous().reshape(-1).view(torch.uint8)))


def _prepare_inference_close(owner):
    from sglang.srt.managers.io_struct import ResumeMemoryOccupationReqInput

    if owner.offload_tags:
        owner.resume_memory_occupation(ResumeMemoryOccupationReqInput(tags=list(owner.offload_tags)))


def _close_allocations(torch, saver, handlers, mode):
    prepare_close = handlers.pop("prepare_close", None)
    if prepare_close is not None:
        prepare_close()
    if mode == "cpu":
        release_runtime = handlers.pop("release_runtime", None)
        if release_runtime is not None:
            release_runtime()
        handlers.clear()
        saver.regions.clear()
        gc.collect()
        return
    impl = saver._impl
    if impl is None:
        handlers.clear()
        gc.collect()
        return
    # TMS has no public pool disposal API. Its torch allocator requires an
    # interesting region for frees as well as allocations. The worker owns
    # this instance's pool and must release it before interpreter teardown.
    with impl._with_region_config(tag="default", enable_cpu_backup=False):
        release_runtime = handlers.pop("release_runtime", None)
        if release_runtime is not None:
            release_runtime()
        handlers.clear()
        gc.collect()
        torch.cuda.synchronize()
        pool = impl._primary_mem_pool
        impl._primary_mem_pool = None
        del pool
        torch.cuda.empty_cache()
        gc.collect()


def _native_methods(path, class_name, names, namespace):
    tree = ast.parse(path.read_text())
    node = next(item for item in tree.body if isinstance(item, ast.ClassDef) and item.name == class_name)
    node.bases = []
    node.decorator_list = []
    node.body = [item for item in node.body if getattr(item, "name", None) in names]
    assert {item.name for item in node.body} == names, (path, names)
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), "exec"), namespace)
    return namespace[class_name]


class _CpuRemap:
    """Model the declared backup policy with an adversarial zero-filled remap."""

    def __init__(self):
        self.regions = []

    def track(self, tensor, tag, backup):
        self.regions.append([tensor, tag, backup, None])
        return tensor

    def disable(self):
        return nullcontext()

    def pause(self, tag=None):
        for item in self.regions:
            tensor, tensor_tag, backup, snapshot = item
            if tag is None or tag == tensor_tag:
                assert snapshot is None, "native TMS pause requires an active allocation"
                item[3] = tensor.detach().clone() if backup else False

    def resume(self, tag=None):
        import torch

        with torch.no_grad():
            for item in self.regions:
                tensor, tensor_tag, _, snapshot = item
                if tag is None or tag == tensor_tag:
                    assert snapshot is not None, "native TMS resume requires a paused allocation"
                    tensor.copy_(snapshot) if snapshot is not False else tensor.zero_()
                    item[3] = None


def _allocate(torch, saver, mode, tag, backup, factory):
    if mode == "cpu":
        return saver.track(factory(), tag, backup)
    with saver.region(tag=tag, enable_cpu_backup=backup):
        return factory()


def test_native_tms_cleanup_lifecycle():
    """Check native owner/config methods with strict CPU allocation-state spies."""
    import torch
    import pytest

    tms_source = Path(os.environ["TMS_PYTHON_PACKAGE"])
    events = []
    flags = SimpleNamespace(interesting=False, backup=True, pool=None)
    cdll = SimpleNamespace(
        tms_get_interesting_region=lambda: flags.interesting,
        tms_get_enable_cpu_backup=lambda: flags.backup,
        tms_set_current_tag=lambda value: None,
        tms_set_interesting_region=lambda value: setattr(flags, "interesting", value),
        tms_set_enable_cpu_backup=lambda value: setattr(flags, "backup", value),
    )

    class Pool:
        def __init__(self, allocator=None):
            self.allocator = allocator

        def __del__(self):
            events.append(("pool_free", self.allocator, flags.interesting))

    @contextmanager
    def use_pool(pool):
        previous, flags.pool = flags.pool, pool
        try:
            yield
        finally:
            flags.pool = previous

    fake_torch = SimpleNamespace(cuda=SimpleNamespace(
        MemPool=Pool, use_mem_pool=use_pool, synchronize=lambda: None,
    ), distributed=SimpleNamespace(barrier=lambda *args: None))
    binary_cls = _native_methods(tms_source / "binary_wrapper.py", "BinaryWrapper", {"set_config"}, {})
    impl_cls = _native_methods(
        tms_source / "entrypoint.py", "_TorchMemorySaverImpl",
        {"_with_region_config", "disable", "region"},
        {"contextmanager": contextmanager, "torch": fake_torch, "_TAG_DEFAULT": "default"},
    )

    class StrictSaver(_CpuRemap):
        def __init__(self):
            super().__init__()
            self.resume_calls = []
            self._impl = impl_cls()
            self._impl._hook_mode = "torch"
            self._impl._binary_wrapper = binary_cls()
            self._impl._binary_wrapper.cdll = cdll
            self._impl._primary_mem_pool = Pool("tms")

        def resume(self, tag=None):
            self.resume_calls.append(tag)
            for _, allocation_tag, _, snapshot in self.regions:
                if tag is None or tag == allocation_tag:
                    assert snapshot is not None, "native active resume exits 1"
            super().resume(tag)

    for side, paused in [("sglang", False), ("actor", True), ("sglang", True)]:
        saver = StrictSaver()
        tag = "param_buffer" if side == "actor" else "weights"
        saver.track(torch.ones(1), tag, False)
        if paused:
            saver.pause(tag)

        def free():
            assert flags.interesting, "native torch free requires interesting region"
            assert all(item[3] is None for item in saver.regions), "native free cannot unmap paused allocation"
            events.append(("allocation_free", side))

        fake_torch.cuda.empty_cache = free
        if paused:
            with saver._impl._with_region_config(tag="default", enable_cpu_backup=False):
                with pytest.raises(AssertionError, match="paused allocation"):
                    free()
        if side == "actor":
            actor_cls = _native_methods(
                _ROOT / "miles/backends/megatron_utils/actor.py", "MegatronTrainRayActor", {"wake_up"},
                {"timer": lambda function: function, "with_logs": lambda function: function,
                 "logger": logging.getLogger(_TASK_ID), "torch_memory_saver": saver,
                 "lora_rollout_enabled": lambda args: False, "print_memory": lambda *args: None,
                 "clear_memory": lambda: None, "reload_process_groups": lambda: None},
            )
            owner = actor_cls()
            owner.args, owner._asleep = SimpleNamespace(offload_train=True), paused
            prepare_close = owner.wake_up
        else:
            import sglang

            owner_cls = _native_methods(
                Path(sglang.__file__).parent / "srt/managers/scheduler_components/weight_updater.py",
                "SchedulerWeightUpdaterManager", {"resume_memory_occupation"},
                {"torch": fake_torch, "GPU_MEMORY_ALL_TYPES": ("weights", "kv_cache", "cuda_graph"),
                 "GPU_MEMORY_TYPE_WEIGHTS": "weights", "GPU_MEMORY_TYPE_KV_CACHE": "kv_cache",
                 "GPU_MEMORY_TYPE_CUDA_GRAPH": "cuda_graph", "_import_static_state": lambda *args: None,
                 "ResumeMemoryOccupationReqOutput": SimpleNamespace},
            )
            owner = owner_cls()
            owner.offload_tags = {tag} if paused else set()
            owner.memory_saver_adapter, owner.tp_cpu_group = saver, None
            owner._assert_weight_cache_inactive = lambda *args: None
            owner.tp_worker = SimpleNamespace(model_runner=SimpleNamespace(model=None))
            owner.stashed_model_static_state = {}
            prepare_close = lambda: _prepare_inference_close(owner)
        handlers = {"prepare_close": prepare_close, "model": object()}
        start = len(events)
        _close_allocations(fake_torch, saver, handlers, "cuda")
        assert not handlers and not flags.interesting
        assert ("pool_free", "tms", True) in events[start:]
        assert saver.resume_calls == ([None] if side == "actor" else [tag] if paused else [])

    # Execute the installed torch-mode region/disable implementation, not a no-op.
    saver = StrictSaver()
    with saver._impl.region(tag="default", enable_cpu_backup=True):
        primary = flags.pool
        assert flags.interesting and primary.allocator == "tms"
        with saver._impl.disable():
            assert not flags.interesting and flags.pool.allocator is None
        assert flags.interesting and flags.pool is primary
    assert not flags.interesting
    del primary
    _close_allocations(fake_torch, saver, {}, "cuda")


def test_pinned_published_storage_rejects_address_movement():
    """Run the pinned native assert itself, including a storage-movement control."""
    import pytest
    import torch

    source = Path(os.environ["SGLANG_PINNED_WEIGHT_UPDATER_SOURCE"])
    native_cls = _native_methods(source, "WeightUpdater", {"_assert_published_storage_unmoved"}, {})
    model = torch.nn.Linear(8, 8, bias=False, dtype=torch.bfloat16)
    published = _published_weight_info(model)
    runner = SimpleNamespace(model=model, remote_instance_weight_transporter=SimpleNamespace(weight_info=published))
    native = native_cls()
    native.get_model, native.get_model_runner = lambda: model, lambda: runner
    native._assert_published_storage_unmoved()

    original = model.weight
    model.weight = torch.nn.Parameter(original.detach().clone())
    assert model.weight.data_ptr() != published["weight"][0]
    with pytest.raises(AssertionError, match="moved published parameters"):
        native._assert_published_storage_unmoved()
    assert runner.remote_instance_weight_transporter.weight_info == published
    model.weight = original
    native._assert_published_storage_unmoved()


def _scores(torch, model):
    tokens = torch.tensor([1, 2, 3, 4, 5, 6, 7], device=model.weight.device)
    return torch.log_softmax(model.weight.float()[tokens[:-1]], dim=-1).gather(
        -1, tokens[1:, None]
    ).squeeze(-1).detach().cpu()


def _actor(torch, saver, mode, device, evidence, peer):
    import pytest
    from tests.fast.backends.megatron_utils.score_rpc_fixtures import (
        ScoreModel, ScoreStore, install_cpu_runtime, load_score_actor, make_args, make_parallel, make_raw_data,
    )
    from miles.platforms import current_platform
    from miles.utils.tensor_backper import TensorBackuper

    monkeypatch = pytest.MonkeyPatch()
    store = ScoreStore()
    native_synchronize = torch.cuda.synchronize
    parallel = make_parallel(tp_group=torch.distributed.group.WORLD)
    install_cpu_runtime(monkeypatch, store, parallel)
    monkeypatch.setattr(current_platform, "current_device", lambda: device)
    if mode == "cpu":
        monkeypatch.setattr(torch.cuda, "synchronize", lambda *args: None)
    else:
        monkeypatch.setattr(torch.cuda, "synchronize", native_synchronize)
    actor_cls, namespace = load_score_actor()
    namespace.update(
        torch_memory_saver=saver,
        clear_memory=lambda **kwargs: None,
        print_memory=lambda *args: None,
        destroy_process_groups=lambda: None,
        reload_process_groups=lambda: None,
        lora_rollout_enabled=lambda args: False,
        is_first_replica_megatron_main_rank=lambda: False,
        logger=logging.getLogger(_TASK_ID),
        WitnessInfo=object,
        TrainStepOutput=SimpleNamespace,
        inverse_timer=lambda *args, **kwargs: nullcontext(),
    )
    lifecycle_names = {"sleep", "wake_up", "_switch_model", "_enable_weight_backup", "_weight_sync_reads_tms_backup", "_train_actor", "update_weights"}
    methods = _native_methods(
        _ROOT / "miles/backends/megatron_utils/actor.py", "MegatronTrainRayActor",
        lifecycle_names, namespace | {"is_lora_enabled": lambda args: False},
    )
    for name in lifecycle_names:
        setattr(actor_cls, name, getattr(methods, name))
    args = make_args(delayed=True)
    args.colocate = True
    args.rematerialize_param_from_master_weight = False
    args.compute_advantages_and_returns = True
    args.get_mismatch_metrics = True
    args.skip_actor_forward_only = False
    args.use_sampling_support_replay = False
    args.keep_old_actor = False
    args.rollout_num_gpus_per_engine = 1
    args.sglang = SimpleNamespace(base_args={"speculative_algorithm": None})
    args.lora_sync_sends_base = False
    args.ft_components = ()
    args.ci_test = True
    actor = actor_cls()
    actor.args = args
    actor.role = "actor"
    actor._active_model_tag = "actor"
    actor._cell_index = actor._rank = 0
    actor._asleep = False
    actor.model = [ScoreModel()]
    actor.model[0].model_companion.eval()
    actor.output_store_read = None
    actor._heartbeat = SimpleNamespace(bump=lambda: None)
    actor.with_ref = False
    actor.with_opd_teacher = False
    actor._last_rollout_id = None
    actor._clear_quantized_weight_workspaces = lambda: None
    actor.model[0].weight = torch.nn.Parameter(_allocate(
        torch, saver, mode, "param_buffer", False,
        lambda: actor.model[0].weight.detach().to(device=device, dtype=torch.bfloat16, copy=True),
    ))
    # Initialize native Adam moments without calling step(), including fixture
    # constructors that would themselves perform an optimizer update.
    master = _allocate(torch, saver, mode, "default", True,
                       lambda: torch.nn.Parameter(actor.model[0].weight.detach().float().clone()))
    optimizer = torch.optim.Adam([master], lr=0.01)
    master.grad = torch.ones_like(master)
    if mode == "cuda":
        with saver.region(tag="default", enable_cpu_backup=True):
            optimizer._init_group(optimizer.param_groups[0], [], [], [], [], [], [])
    else:
        optimizer._init_group(optimizer.param_groups[0], [], [], [], [], [], [])
        for value in optimizer.state[master].values():
            if isinstance(value, torch.Tensor):
                saver.track(value, "default", True)
    actor.optimizer = optimizer
    actor.model[0].weight.grad = _allocate(
        torch, saver, mode, "grad_buffer", False, lambda: torch.ones_like(actor.model[0].weight),
    )
    actor.weights_backuper = TensorBackuper.create(source_getter=actor.model[0].named_parameters)
    actor.weights_backuper.backup("actor")
    actor._get_actor_weights = lambda **kwargs: actor.weights_backuper.get("actor")
    original_compute = actor._compute_log_prob
    observations = []

    def compute(*args, **kwargs):
        observations.append(actor.model[0].weight.detach().cpu().clone())
        scores = original_compute(*args, **kwargs)
        if kwargs["store_prefix"] == "":
            raise _TrainingForwardObserved(scores)
        return scores

    actor._compute_log_prob = compute
    expected_weight = actor.model[0].weight.detach().cpu().clone()
    baseline_ref = actor.score_log_probs(0, store.put(make_raw_data()))
    expected_scores = _score_receipt(torch, store.values[baseline_ref.payload]["log_probs"])
    assert torch.unique(expected_scores).numel() > 1, "initial native scorer must be nonuniform"
    evidence["actor_baseline"] = {"native_scores": expected_scores.tolist()}
    expected_master = master.detach().cpu().clone()
    optimizer_before = copy.deepcopy(optimizer.state_dict())
    actor.sleep()

    from miles.backends.sglang_utils.sglang_api_client import SGLangApiClient
    from miles.backends.training_utils.weight_update.protocols.cuda_ipc import UpdateWeightFromTensor
    from miles.backends.training_utils.weight_update.updater import WeightUpdater

    class LocalApiClient(SGLangApiClient):
        async def _make_request(self, endpoint, payload=None, *, timeout=None):
            return _rpc(peer, "api", endpoint, payload or {}, os.getpid())

        async def flush_cache(self):
            return await self._make_request("flush_cache")

        async def pause_generation(self, mode="retract"):
            return await self._make_request("pause_generation", {"mode": mode})

        async def continue_generation(self):
            return await self._make_request("continue_generation")

        async def get_weight_version(self):
            return (await self._make_request("model_info"))["weight_version"]

    class TinyWeightIterator:
        def __init__(self, args, model, *, required_placement, **kwargs):
            self.placement = required_placement

        def iter_hf_weights(self, weights, *, include_base=True, adapters=(), materialize=True):
            assert include_base and not adapters and materialize
            yield [("weight", weights["weight"].to(device=device, copy=True))]

    client = LocalApiClient(server_url="local-control://tiny")
    actor.weight_updater = WeightUpdater(
        args, actor.model, weights_getter=actor._get_actor_weights,
        model_name="tiny", quantization_config=None, iterator_factory=TinyWeightIterator,
        parallel_state=parallel, is_lora=False,
    )
    assert type(actor.weight_updater.protocol) is UpdateWeightFromTensor
    if mode == "cpu":
        # No CUDA calls in CPU orchestration checks; CUDA uses the unmodified hook.
        actor.weight_updater.protocol.after_engines_resumed = lambda: None

    def publish(info):
        info = dataclasses.replace(info, rollout_engines=[client])
        output = actor.update_weights(info, "tiny-same-version", rollout_id=None)
        assert output.weight_version == 7 and not output.failed_cell_ids
        return output

    def score():
        ref = store.put(make_raw_data())
        output = actor.score_log_probs(0, ref)
        batch = store.values[output.payload]
        score_values = _score_receipt(torch, batch["log_probs"])
        uniform = torch.full_like(score_values, -torch.log(torch.tensor(8.0)))
        return {
            "weight_equal_at_forward": _tensor_bytes_equal(torch, observations[-1], expected_weight),
            "max_weight_error_at_forward": (observations[-1].float() - expected_weight.float()).abs().max().item(),
            "uniform_score_max_error": (score_values - uniform).abs().max().item(),
            "baseline_score_max_error": (score_values - expected_scores).abs().max().item(),
            "baseline_native_scores": expected_scores.tolist(),
            "native_scores": score_values.tolist(),
            "restored_original_sleep_state": actor._asleep,
            "weight_version": batch["metadata"]["weight_version"],
        }

    def control():
        actor.wake_up()
        raw_ref = store.put(make_raw_data())
        rollout_data, lease = namespace["get_rollout_data"](
            args=actor.args, rollout_data_ref=raw_ref, output_store_read=None,
            train_parallel_config=namespace["get_parallel_state"]().train_parallel_config(
                supports_precomputed_schedule=False,
            ),
        )
        with lease:
            try:
                actor._train_actor(0, rollout_data, witness_info=None, attempt=0)
            except _TrainingForwardObserved as observation:
                actual_scores = _score_receipt(torch, observation.scores["log_probs"])
            else:
                raise AssertionError("native training control did not stop after its forward")
        evidence["actor_native_restore_control"] = {
            "weight_equal_after_native_switch": _tensor_bytes_equal(torch, actor.model[0].weight, expected_weight),
            "actual_native_scores": actual_scores.tolist(),
            "baseline_native_scores": expected_scores.tolist(),
            "callsite": "MegatronTrainRayActor._train_actor",
            "stopped_before_optimizer_step": True,
        }
        master_equal = _tensor_bytes_equal(torch, master, expected_master)
        states_equal = optimizer.state_dict()["param_groups"] == optimizer_before["param_groups"] and all(
            _tensor_bytes_equal(torch, value, optimizer_before["state"][key][field])
            for key, state in optimizer.state_dict()["state"].items()
            for field, value in state.items() if isinstance(value, torch.Tensor)
        )
        result = {
            "weight_equal_after_native_switch": _tensor_bytes_equal(torch, actor.model[0].weight, expected_weight),
            "score_max_error_after_native_switch": (actual_scores - expected_scores).abs().max().item(),
            "optimizer_state_equal": states_equal,
            "master_equal": master_equal,
            "optimizer_steps": optimizer.state[master]["step"].item(),
            "weight_version": actor._get_actor_weight_version(),
            "callsite": "MegatronTrainRayActor._train_actor",
            "stopped_before_optimizer_step": True,
        }
        evidence["actor_native_restore_control"].update(result)
        actor.sleep()
        result["final_actor_asleep"] = actor._asleep
        return result

    return {"score": score, "control": control, "publish": publish,
            "prepare_close": actor.wake_up, "release_runtime": monkeypatch.undo}


def _sglang(torch, saver, mode, device, evidence):
    import msgspec
    import pytest
    from sglang.srt.disaggregation.utils import DisaggregationMode
    from sglang.srt.managers import io_struct
    from sglang.srt.managers.scheduler_components.weight_updater import SchedulerWeightUpdaterManager
    from sglang.srt.model_executor.model_runner_components import weight_updater as runner_module
    from sglang.srt.runtime_context import get_context, get_parallel, get_serving
    from sglang.srt.server_args import ServerArgs
    from sglang.srt.utils import MultiprocessingSerializer
    from sglang.srt.utils.patch_torch import monkey_patch_torch_reductions

    monkeypatch = pytest.MonkeyPatch()
    get_context().set_server_args(ServerArgs(
        model_path="tiny-local-probe", device=str(device.type),
        weight_cache_mode="off", weight_version="7",
        enable_memory_saver=mode == "cuda", enable_weights_cpu_backup=False,
    ))
    get_parallel().override_permanently(
        tp_rank=0, tp_group=SimpleNamespace(cpu_group=torch.distributed.group.WORLD),
    )
    sglang_root = Path(importlib.util.find_spec("sglang").origin).parent
    path = sglang_root / "srt/managers/scheduler_components/weight_updater.py"
    events = []
    transfers = []

    class TinyModel(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.weight = torch.nn.Parameter(_allocate(
                torch, saver, mode, "weights", False,
                # Match ScoreModel's CPU-initialized bytes before device transfer.
                lambda: torch.arange(64, dtype=torch.float32).reshape(8, 8).sin().to(device=device, dtype=torch.bfloat16),
            ))

        def load_weights(self, weights):
            weights = list(weights)
            assert len(weights) == 1 and weights[0][0] == "weight"
            name, tensor = weights[0]
            assert tensor.device == device and tensor.shape == self.weight.shape and tensor.dtype == self.weight.dtype
            with torch.no_grad():
                self.weight.copy_(tensor)
            transfers[-1]["native_load_weights_completed"] = True
            return {name}

    model = TinyModel()
    # Static-state restoration must not be mistaken for parameter restoration.
    model.register_buffer("static_state", torch.tensor([17], device=device))
    scheduler_cls = _native_methods(
        sglang_root / "srt/managers/scheduler.py", "Scheduler",
        {"handle_update_weight_version", "record_weight_version_change"},
        {"get_context": get_context, "get_serving": get_serving,
         "UpdateWeightVersionReqOutput": io_struct.UpdateWeightVersionReqOutput},
    )
    scheduler = scheduler_cls()
    scheduler._engine_paused = False
    scheduler.disaggregation_mode = DisaggregationMode.NULL
    # Only startup address metadata is represented here, not a remote engine.
    runner = SimpleNamespace(model=model, remote_instance_weight_transporter=SimpleNamespace(
        weight_info=_published_weight_info(model),
    ))
    runner.weight_updater = runner_module.WeightUpdater(
        tp_rank=0, device=device.type, gpu_id=device.index or 0, model_config=None,
        custom_weight_loaders={}, get_model=lambda: model,
        update_model_fields=lambda *args, **kwargs: None,
        recapture_cuda_graph=lambda: None, get_model_runner=lambda: runner,
    )
    tp_cls = _native_methods(
        sglang_root / "srt/managers/tp_worker.py", "TpModelWorker",
        {"weight_update_runners"}, {},
    )
    tp_base = _native_methods(
        sglang_root / "srt/managers/tp_worker.py", "BaseTpWorker",
        {"deserialize_own_rank"},
        {"get_parallel": get_parallel, "MultiprocessingSerializer": MultiprocessingSerializer,
         "monkey_patch_torch_reductions": monkey_patch_torch_reductions if mode == "cuda" else lambda: None},
    )
    tp_cls.deserialize_own_rank = tp_base.deserialize_own_rank
    tp_worker = tp_cls()
    tp_worker._model_runner = tp_worker.model_runner = runner
    native_deserialize = tp_worker.deserialize_own_rank

    def deserialize(values):
        bucket = native_deserialize(values)
        tensor = bucket["flattened_tensor"]
        assert tensor.device == device
        transfers.append({
            "device": str(tensor.device), "is_cuda": tensor.is_cuda,
            "receiver_pid": os.getpid(), "bucket_bytes": tensor.numel(),
            "native_receiver": "BaseTpWorker.deserialize_own_rank -> WeightUpdater._update_weights_from_flattened_bucket",
        })
        return bucket

    tp_worker.deserialize_own_rank = deserialize
    obj = SchedulerWeightUpdaterManager(
        tp_worker=tp_worker, draft_worker=None, memory_saver_adapter=saver,
        flush_cache=lambda **kwargs: True, is_fully_idle=lambda **kwargs: True,
        scheduler=scheduler,
    )
    expected = _scores(torch, model)
    evidence["sg_baseline"] = {"scores": expected.tolist()}
    expected_weight = model.weight.detach().cpu().clone()
    if mode == "cpu":
        get_device_module = torch.get_device_module
        monkeypatch.setattr(torch, "get_device_module", lambda device="cpu": get_device_module(device))
        monkeypatch.setattr(runner_module, "monkey_patch_torch_reductions", lambda: None)

    def api(endpoint, payload, sender_pid):
        events.append(endpoint)
        assert sender_pid != os.getpid(), "transport must cross process boundaries"
        if endpoint == "pause_generation":
            scheduler._engine_paused = True
            return {}
        if endpoint == "continue_generation":
            scheduler._engine_paused = False
            return {}
        if endpoint == "flush_cache":
            assert obj.flush_cache()
            return True
        if endpoint == "model_info":
            return {"weight_version": get_serving().weight_version}
        requests = {
            "begin_weight_update": (io_struct.BeginWeightUpdateReqInput, obj.begin_weight_update),
            "end_weight_update": (io_struct.EndWeightUpdateReqInput, obj.end_weight_update),
            "update_weights_from_tensor": (io_struct.UpdateWeightsFromTensorReqInput, obj.update_weights_from_tensor),
            "update_weight_version": (io_struct.UpdateWeightVersionReqInput, scheduler.handle_update_weight_version),
        }
        if endpoint == "begin_weight_update":
            assert payload["sync_base"] is True
            payload = {"selector": payload["selector"]}
        if endpoint == "end_weight_update":
            assert payload["expected_lora_checksums"] is None
            payload = {}
        if endpoint == "update_weight_version":
            assert payload["new_version"] == "7"
        if endpoint == "update_weights_from_tensor":
            assert payload["load_format"] == "flattened_bucket"
            payload = dict(payload, serialized_named_tensors=[base64.b64decode(value) for value in payload["serialized_named_tensors"]])
        req_type, native_method = requests[endpoint]
        output = native_method(req_type(**payload))
        if endpoint == "update_weights_from_tensor" and output.success:
            transfers[-1]["sender_pid"] = sender_pid
        return msgspec.structs.asdict(output)

    def observation():
        actual = _scores(torch, model)
        return {
            "weight_equal_after_native_resume": _tensor_bytes_equal(torch, model.weight, expected_weight),
            "score_max_error_after_native_resume": (actual - expected).abs().max().item(),
            "baseline_scores": expected.tolist(),
            "uniform_score_max_error": (actual + torch.log(torch.tensor(8.0))).abs().max().item(),
            "scores": actual.tolist(),
            "static_state_equal": model.static_state.item() == 17,
            "weight_version": get_serving().weight_version,
            "session_closed": obj._session is None,
            "engine_resumed": not scheduler._engine_paused,
            "offload_tags": sorted(obj.offload_tags),
            "engine_events": list(events),
            "native_transfers": copy.deepcopy(transfers),
            "source": str(path),
        }

    return {"offload": lambda tags: obj.release_memory_occupation(io_struct.ReleaseMemoryOccupationReqInput(tags=tags)),
            "onload": lambda tags: obj.resume_memory_occupation(io_struct.ResumeMemoryOccupationReqInput(tags=tags)),
            "observation": observation, "api": api, "prepare_close": lambda: _prepare_inference_close(obj),
            "release_runtime": monkeypatch.undo}


def _worker(connection, side, mode, gpu_id, rendezvous, peer):
    evidence = {}
    handlers = {}
    close_allocations = None
    try:
        import torch

        device = torch.device("cpu")
        if mode == "cuda":
            torch.cuda.set_device(gpu_id)
            device = torch.device("cuda", gpu_id)
            from torch_memory_saver import torch_memory_saver as saver

            saver.hook_mode = "torch"
        else:
            saver = _CpuRemap()
        close_allocations = lambda: _close_allocations(torch, saver, handlers, mode)
        torch.distributed.init_process_group("gloo", init_method=f"file://{rendezvous}", rank=0, world_size=1)
        from miles.utils.distributed_utils import init_gloo_group

        init_gloo_group()
        handlers = _actor(torch, saver, mode, device, evidence, peer) if side == "actor" else _sglang(torch, saver, mode, device, evidence)
        connection.send({"ready": True, "pid": os.getpid(), "torch": torch.__version__, "evidence": evidence})
        while True:
            channel = wait([connection, peer])[0] if side == "sglang" else connection
            method, args = channel.recv()
            if method == "close":
                break
            try:
                # Native actor publication uses disable() inside the normal
                # backed region. Pinned torch-hook disable() selects a separate
                # default allocator; this is not a preload-hook equivalence claim.
                with saver.region(tag="default", enable_cpu_backup=True) if mode == "cuda" else nullcontext():
                    result = handlers[method](*args)
                evidence[method] = result if isinstance(result, dict) else {"completed": True}
                channel.send({"result": result})
            except Exception:
                channel.send({"error": traceback.format_exc(), "evidence": evidence})
    except BaseException:
        connection.send({"error": traceback.format_exc(), "evidence": evidence})
    finally:
        try:
            if close_allocations is not None:
                close_allocations()
        finally:
            peer.close()
            connection.close()


def _rpc(connection, method, *args):
    connection.send((method, args))
    response = connection.recv()
    if "error" in response:
        raise _WorkerError(method, response["error"], response["evidence"])
    return response["result"]


async def _driver(actor_connection, sg_connection, result):
    from miles.backends.sglang_utils.sglang_api_client import SGLangApiClient
    from miles.ray.rollout.inference_controller import UpdatableEngines

    score_observations = result["actor_score"]
    transactions = result["transactions"]

    async def score(*args):
        try:
            score_observations.append(_rpc(actor_connection, "score"))
        except _WorkerError as error:
            result["worker_error"] = {"method": error.method, "evidence": error.evidence, "error": str(error)}
            raise
        return [SimpleNamespace(payload="scores")]

    async def offload(*, tags):
        _rpc(sg_connection, "offload", tags)

    async def onload(*, tags):
        _rpc(sg_connection, "onload", tags)

    async def prepare_eval():
        observation = _rpc(sg_connection, "observation")
        assert observation["session_closed"] and observation["engine_resumed"]

    info = UpdatableEngines(
        rollout_engines=[SGLangApiClient("local-control://tiny")],
        engine_gpu_counts=[1], engine_gpu_offsets=[0], engine_cell_ids=["tiny"],
        snapshot_cell_id_to_hashes={"tiny": "same-process-generation"},
    )

    async def start_update_weights(*, model_id):
        assert model_id is None
        transactions.append({"events": ["start"], "receiver_pool": info.receiver_pool})
        return info

    async def publish(*, info, rollout_id):
        assert rollout_id is None
        output = _rpc(actor_connection, "publish", info)
        transactions[-1]["events"].append("publish")
        transactions[-1]["weight_version"] = output.weight_version
        assert output.weight_version == 7 and not output.failed_cell_ids
        return output

    async def end_update_weights(**kwargs):
        assert kwargs["snapshot_cell_id_to_hashes"] == info.snapshot_cell_id_to_hashes
        assert not kwargs["failed_cell_ids"] and not kwargs["collect_checksums"]
        transactions[-1]["events"].append("end")
        return []

    async def abort_update_weights():
        transactions[-1]["events"].append("abort")

    async def set_weight_version(version, *, trainer_model_id):
        assert version == 7 and trainer_model_id is None
        transactions[-1]["events"].append("rollout_set_version")

    controller = SimpleNamespace(
        offload=offload, onload=onload, prepare_eval=prepare_eval,
        start_update_weights=start_update_weights, end_update_weights=end_update_weights,
        abort_update_weights=abort_update_weights,
    )
    actor_handle = SimpleNamespace(score_log_probs=score, update_weights=publish)
    executor = SimpleNamespace(set_weight_version=set_weight_version)

    @contextmanager
    def get(ref):
        yield {"metadata": {"rank": 0, "cp_rank": 0, "cp_size": 1}}

    namespace = dict(asyncio=asyncio, RolloutDataPack=object,
                     logger=logging.getLogger(_TASK_ID), quote=lambda value, **kwargs: value,
                     object_store=SimpleNamespace(get_instance=lambda: SimpleNamespace(get=get, remove=lambda ref: None)),
                     save_debug_train_data_for_rank=lambda *args, **kwargs: None,
                      GPU_MEMORY_TYPE_CUDA_GRAPH="cuda_graph", GPU_MEMORY_TYPE_KV_CACHE="kv_cache", GPU_MEMORY_TYPE_WEIGHTS="weights")
    publication_path = _ROOT / "miles/ray/placement_group.py"
    publication_nodes = [node for node in ast.parse(publication_path.read_text()).body
                         if getattr(node, "name", None) in {"update_weights", "_log_inference_engine_weight_checksums"}]
    exec(compile(ast.Module(body=publication_nodes, type_ignores=[]), str(publication_path), "exec"), namespace)
    path = _ROOT / "train.py"
    nodes = [node for node in ast.parse(path.read_text()).body
             if getattr(node, "name", None) in {"_rollout_offload_tags", "_score_eval_train_data", "_score_eval_datasets"}]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)
    args = SimpleNamespace(offload_rollout=True, offload_rollout_level=["weight", "kv_cache"],
                           log_inference_engine_weight_checksums=False)
    pack = SimpleNamespace(data_refs=[SimpleNamespace(payload="input")])
    for cycle in range(2):
        await namespace["_score_eval_train_data"](
            args, actor_handle, controller, cycle, {"synthetic": pack}, rollout_executor=executor,
        )
        assert len(score_observations) == cycle + 1, "native scorer did not return a measurement"
        observation = _rpc(sg_connection, "observation")
        result["sg_wake"] = observation
        control = _rpc(actor_connection, "control")
        result["actor_native_restore_control"] = control
        result["cycles"].append({"cycle": cycle, "actor_score": score_observations[-1],
                                 "sg_wake": observation, "actor_native_restore_control": control})


def _write_report(path, result, started):
    result["elapsed_seconds"] = time.monotonic() - started
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("cpu", "cuda"), required=True)
    parser.add_argument("--gpu-id", type=int, default=0)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    result = {
        "task_id": _TASK_ID, "mode": args.mode, "verdict": "INCOMPLETE", "actor_score": [],
        "cycles": [], "transactions": [], "workers": [],
        "worker_exits": [],
        "interpretation": "CPU-injected orchestration only; not CUDA IPC qualification" if args.mode == "cpu" else "real TMS and native CUDA IPC synthetic lifecycle",
        "cuda_ipc_qualified": False,
        "python": sys.version, "executable": sys.executable,
        "limits": ["synthetic model and Adam masters, not Megatron DDP/optimizer construction",
                   "single rank per component, not TP4/DP2",
                   "native process-group destroy/reload and Ray transport are not exercised",
                   "local control RPC shim, not Ray/HTTP server or CUDA graph capture",
                   "tiny load_weights destination and iterator, not Qwen/Megatron-to-HF conversion",
                   "CUDA mode uses supported TMS torch hook, not the formal worker preload hook",
                   "native training control stops after logprob forward before advantages/backward/update"],
    }
    context = mp.get_context("spawn")
    workers = []
    peers = context.Pipe()
    try:
        for index, side in enumerate(("actor", "sglang")):
            parent, child = context.Pipe()
            rendezvous = Path(tempfile.gettempdir()) / f"eval-restore-{side}-{uuid.uuid4().hex}"
            worker = context.Process(target=_worker, args=(child, side, args.mode, args.gpu_id, rendezvous, peers[index]))
            worker.start()
            child.close()
            workers.append((worker, parent))
        for worker, connection in workers:
            ready = connection.recv()
            if "error" in ready:
                raise _WorkerError("init", ready["error"], ready["evidence"])
            result["workers"].append(ready)
        asyncio.run(_driver(workers[0][1], workers[1][1], result))
        transfers = result["sg_wake"]["native_transfers"]
        engine_frame = ["pause_generation", "flush_cache", "begin_weight_update", "update_weights_from_tensor",
                        "end_weight_update", "update_weight_version", "continue_generation", "model_info"]
        passed = (
            len(result["cycles"]) == len(result["transactions"]) == len(transfers) == 2
            and result["sg_wake"]["engine_events"] == engine_frame * 2
            and all(row["weight_equal_at_forward"] and row["baseline_score_max_error"] == 0
                    and len(set(row["native_scores"])) > 1 and row["restored_original_sleep_state"]
                    and row["weight_version"] == 7 for row in result["actor_score"])
            and all(cycle["sg_wake"]["weight_equal_after_native_resume"]
                    and cycle["sg_wake"]["score_max_error_after_native_resume"] == 0
                    and len(set(cycle["sg_wake"]["scores"])) > 1
                    and cycle["sg_wake"]["static_state_equal"] and cycle["sg_wake"]["session_closed"]
                    and cycle["sg_wake"]["engine_resumed"] and cycle["sg_wake"]["weight_version"] == "7"
                    and cycle["actor_native_restore_control"]["weight_equal_after_native_switch"]
                    and cycle["actor_native_restore_control"]["score_max_error_after_native_switch"] == 0
                    and cycle["actor_native_restore_control"]["optimizer_state_equal"]
                    and cycle["actor_native_restore_control"]["master_equal"]
                    and cycle["actor_native_restore_control"]["optimizer_steps"] == 0
                    and cycle["actor_native_restore_control"]["weight_version"] == 7 for cycle in result["cycles"])
            and all(transaction["events"] == ["start", "publish", "end", "rollout_set_version"]
                    and transaction["weight_version"] == 7 for transaction in result["transactions"])
            and all(transfer["native_load_weights_completed"] and transfer["sender_pid"] != transfer["receiver_pid"]
                    and transfer["is_cuda"] == (args.mode == "cuda") for transfer in transfers)
        )
    except BaseException as error:
        result["verdict"] = "ERROR"
        result["error"] = traceback.format_exc()
        if isinstance(error, _WorkerError):
            result["worker_error"] = {"method": error.method, "evidence": error.evidence, "error": str(error)}
        _write_report(args.report, result, started)
        raise
    finally:
        try:
            cleanup_errors = []
            # Stop the receiver before the producer closes its peer pipe.
            for worker, connection in reversed(workers):
                if worker.is_alive():
                    try:
                        connection.send(("close", ()))
                    except (BrokenPipeError, EOFError):
                        cleanup_errors.append(traceback.format_exc())
            for worker, connection in reversed(workers):
                worker.join(timeout=30)
                result["worker_exits"].append({"pid": worker.pid, "exitcode": worker.exitcode})
                connection.close()
                if worker.exitcode != 0:
                    cleanup_errors.append(f"Probe worker did not exit successfully: exitcode={worker.exitcode}")
            for peer in peers:
                peer.close()
            if cleanup_errors:
                raise RuntimeError("\n".join(cleanup_errors))
        except BaseException:
            result["verdict"] = "ERROR"
            result["cleanup_error"] = traceback.format_exc()
            _write_report(args.report, result, started)
            raise
    result["verdict"] = "PASS" if passed else "FAIL"
    result["cuda_ipc_qualified"] = bool(passed and args.mode == "cuda")
    _write_report(args.report, result, started)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
