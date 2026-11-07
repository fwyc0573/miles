"""CPU boundary for production RPC methods whose Megatron runtime is unavailable.

Scoring replaces the CUDA pipeline, memory residency and packed-sequence SDK;
rollout loading/splitting, scheduling, scoring and RPC serialization stay native.
Publication checks also substitute PG construction, conversion, engine transport
and worker termination while retaining the native transaction owners.
"""

import ast
import copy
import dataclasses
import logging
import os
import random
from argparse import Namespace
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager, nullcontext
from functools import partial
from pathlib import Path
from types import MethodType, SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest
import torch
import torch.distributed as dist
from tests.fast.fixtures.args_fixtures import parser_defaults

from miles.backends.training_utils.data.rollout import DataIterator, get_batch, get_data_iterator, get_rollout_data
from miles.backends.training_utils.loss.hub.logit_processors import get_log_probs_and_entropy
from miles.backends.training_utils.metrics.log_utils import aggregate_forward_results
from miles.backends.training_utils.model_companion import (
    ModelCompanion,
    ModelCompanionInstallationUtils,
    ModelCompanionWeightVersionUtils,
)
from miles.backends.training_utils.parallel import ParallelState, get_parallel_state
from miles.backends.training_utils.types import LogProbScoreBatch, LogProbScoreMetadata
from miles.ray.train_actor import WeightUpdateOutput
from miles.platforms import current_platform
from miles.utils import object_store
from miles.utils.ft_utils.process_group_utils import GroupInfo
from miles.utils.object_store import BaseObjectStore, ObjectStoreGetResult, StoreObjectRef, ValueSpec
from miles.utils.timer import timer
from miles.utils.tensor_backper import TensorBackuper
from miles.utils.tracking_utils.structured_log import with_logs

_ROOT = Path(__file__).resolve().parents[4]


class ScoreStore(BaseObjectStore):
    def __init__(self):
        self.values = {}
        self.specs = {}
        self.reads = []
        self.releases = []
        self.removed = []

    def put(self, value, value_spec=None):
        key = str(len(self.values))
        self.values[key] = copy.deepcopy(value)
        self.specs[key] = value_spec
        return object_store._MooncakeStoreObjectRef(payload=key)

    def get(self, ref):
        self.reads.append(ref.payload)
        return ObjectStoreGetResult(self.values[ref.payload], lambda _: self.releases.append(ref.payload))

    def remove(self, ref):
        self.removed.append(ref.payload)


class _Dumper:
    def __init__(self, *args, **kwargs):
        pass

    def wrap_forward_step(self, fn):
        return fn

    def finalize(self, model):
        pass


class ScoreModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.weight = torch.nn.Parameter(torch.arange(64, dtype=torch.float32).reshape(8, 8).sin())
        self.add_module("model_companion", ModelCompanion(pipeline_rank=0, chunk_index=0, replica_id=(0, 0, 0)))
        self.model_companion.weight_version.data.fill_(7)
        self.config = SimpleNamespace(timers=object(), hidden_dropout=0, attention_dropout=0)

    def forward(self, input_ids, **kwargs):
        parallel = get_parallel_state()
        width = self.weight.size(1) // parallel.tp.size
        return self.weight[input_ids, parallel.tp.rank * width : (parallel.tp.rank + 1) * width]


def _execute_nodes(path, names, namespace):
    nodes = [node for node in ast.parse(path.read_text()).body if getattr(node, "name", None) in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), namespace)


def load_score_actor():
    namespace = dict(
        torch=torch,
        dist=dist,
        random=random,
        np=np,
        dataclasses=dataclasses,
        Any=object,
        _get_all_rng_states=lambda: (torch.get_rng_state(),),
        _set_all_rng_states=lambda state: torch.set_rng_state(state),
        Callable=Callable,
        Sequence=Sequence,
        Iterator=Iterator,
        contextmanager=contextmanager,
        partial=partial,
        TrainerConfig=Namespace,
        DDP=torch.nn.Module,
        GPTModel=torch.nn.Module,
        DataIterator=DataIterator,
        DumperMegatronUtil=_Dumper,
        DumperPhase=SimpleNamespace(FWD_ONLY="forward_only"),
        get_batch=get_batch,
        get_model_config=lambda model: model.config,
        get_packed_seq_params=lambda batch, args: None,
        aggregate_forward_results=aggregate_forward_results,
        filter_keys=lambda batch, keys: {key: batch[key] for key in keys},
        mpu=SimpleNamespace(is_pipeline_last_stage=lambda: get_parallel_state().is_pp_last_stage),
        get_parallel_state=get_parallel_state,
        get_data_iterator=get_data_iterator,
        get_rollout_data=get_rollout_data,
        get_log_probs_and_entropy=get_log_probs_and_entropy,
        with_logs=with_logs,
        timer=timer,
        object_store=object_store,
        StoreObjectRef=StoreObjectRef,
        ValueSpec=ValueSpec,
        RolloutBatch=dict,
        LogProbScoreBatch=LogProbScoreBatch,
        LogProbScoreMetadata=LogProbScoreMetadata,
        ModelCompanionWeightVersionUtils=ModelCompanionWeightVersionUtils,
        ModelCompanionInstallationUtils=ModelCompanionInstallationUtils,
        all_replay_managers=[],
        nullcontext=nullcontext,
        WeightUpdateOutput=WeightUpdateOutput,
        UpdatableEngines=SimpleNamespace,
        print_memory=lambda *args: None,
        clear_memory=lambda **kwargs: None,
        reload_process_groups=lambda: None,
        destroy_process_groups=lambda: None,
        lora_rollout_enabled=lambda args: False,
        is_lora_enabled=lambda args: False,
        is_first_replica_megatron_main_rank=lambda: False,
        partition=lambda values, predicate: (
            [value for value in values if not predicate(value)],
            [value for value in values if predicate(value)],
        ),
        fault_hook_controller=SimpleNamespace(with_context=lambda context: nullcontext()),
        FaultHookContext=lambda **kwargs: kwargs,
        logger=logging.getLogger(__name__),
    )

    def pipeline(**kwargs):
        assert kwargs["forward_only"] and kwargs["collect_non_loss_data"]
        results = []
        for _ in range(kwargs["num_microbatches"]):
            output, callback = kwargs["forward_step_func"](kwargs["data_iterator"][0], kwargs["model"][0])
            results.append(callback(output))
        return results

    namespace["get_forward_backward_func"] = lambda: pipeline
    _execute_nodes(_ROOT / "miles/backends/megatron_utils/initialize.py", {"RandomState"}, namespace)
    _execute_nodes(_ROOT / "miles/backends/megatron_utils/model.py", {"forward_only"}, namespace)
    tree = ast.parse((_ROOT / "miles/backends/megatron_utils/actor.py").read_text())
    actor_node = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "MegatronTrainRayActor")
    names = {
        "score_log_probs",
        "_log_prob_scoring_state",
        "_store_log_prob_scores",
        "_compute_log_prob",
        "_set_replay_stage",
        "_get_actor_weight_version",
        "_get_actor_weights",
        "_switch_model",
        "_enable_weight_backup",
        "_weight_sync_reads_tms_backup",
        "_switches_models",
        "sleep",
        "wake_up",
        "_update_receiver_weights",
    }
    actor_node.bases = []
    actor_node.body = [node for node in actor_node.body if getattr(node, "name", None) in names]
    constants = [
        node for node in tree.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
        and node.target.id == "LOG_PROBS_VALUE_SPEC"
    ]
    module = ast.Module(body=[*constants, actor_node], type_ignores=[])
    exec(compile(module, str(_ROOT / "miles/backends/megatron_utils/actor.py"), "exec"), namespace)
    return namespace["MegatronTrainRayActor"], namespace


def make_parallel(*, dp_rank=0, dp_size=1, cp_rank=0, cp_size=1, tp_rank=0, tp_size=1, tp_group=None, cp_group=None):
    one = GroupInfo(rank=0, size=1, group=None)
    return ParallelState(
        intra_dp=GroupInfo(rank=dp_rank, size=dp_size, group=None),
        intra_dp_cp=GroupInfo(rank=dp_rank * cp_size + cp_rank, size=dp_size * cp_size, group=None),
        indep_dp=one,
        cp=GroupInfo(rank=cp_rank, size=cp_size, group=cp_group),
        tp=GroupInfo(rank=tp_rank, size=tp_size, group=tp_group),
        pp=one,
        ep=one,
        etp=one,
    )


def make_args(*, delayed=False, allgather_cp=False, qkv_format="thd", dynamic=False):
    values = dict(
        delay_split_train_data_by_dp=delayed,
        enable_sample_ownership_checker=False,
        enable_witness=False,
        qkv_format=qkv_format,
        data_pad_size_multiplier=4 if qkv_format == "bshd" else 1,
        true_on_policy_mode=False,
        train_backend="megatron",
        log_probs_backend="torch",
        rollout_temperature=1.0,
        log_probs_chunk_size=-1,
        debug_unified_grad_fused_logprob=False,
        loss_type="policy_loss",
        allgather_cp=allgather_cp,
        use_rollout_entropy=False,
        use_sampling_support_replay=True,
        lora_dropout=0,
        custom_megatron_before_log_prob_hook_path=None,
        offload_train=True,
        use_dynamic_batch_size=dynamic,
        use_dynamic_global_batch_size=False,
        allow_partial_train_step=False,
        balance_data=True,
        balance_by_flops=False,
        global_batch_size=4,
        micro_batch_size=1,
        max_tokens_per_gpu=12,
        backend=Namespace(global_batch_size=4, micro_batch_size=1, seq_length=16, compress_ratios=None, vocab_size=8),
    )
    return Namespace(**(parser_defaults() | values))


def make_raw_data():
    tokens = [[1, 2, 3, 4, 5, 6, 7], [2, 1, 3, 4], [3, 1, 2, 4, 6, 7], [2, 4, 1, 3, 5]]
    return dict(
        tokens=tokens,
        total_lengths=[len(value) for value in tokens],
        response_lengths=[3, 1, 4, 2],
        loss_masks=[[1, 0, 1], [1], [0, 1, 1, 1], [1, 0]],
        sample_indices=[103, 5, 77, 29],
        rollout_ids=[0, 1, 2, 3],
    )


def make_actor(actor_cls, args, *, asleep=True):
    actor = actor_cls()
    actor.args = args
    actor.role = "actor"
    actor.with_ref = actor.with_opd_teacher = False
    actor._active_model_tag = "actor"
    actor._cell_index = 0
    actor._rank = 0
    actor._asleep = asleep
    actor._last_rollout_id = 2
    actor.model = [ScoreModel()]
    actor.model[0].model_companion.eval()
    actor.optimizer = torch.optim.Adam([actor.model[0].weight], lr=0.01)
    actor.model[0].weight.grad = torch.ones_like(actor.model[0].weight)
    actor.optimizer.step()
    actor.opt_param_scheduler = SimpleNamespace(num_steps=19)
    actor._get_actor_weights = lambda **kwargs: dict(actor.model[0].named_parameters())
    actor.output_store_read = None
    actor.lifecycle = []
    actor._heartbeat = SimpleNamespace(bump=lambda: actor.lifecycle.append("heartbeat"))
    actor.weights_backuper = TensorBackuper.create(source_getter=actor.model[0].named_parameters)
    actor.weights_backuper.backup("actor")

    def wake():
        actor.lifecycle.append("wake")
        actor._asleep = False

    def sleep():
        actor.lifecycle.append("sleep")
        actor._asleep = True

    actor.wake_up = wake
    actor.sleep = sleep
    return actor


class UnbackedParameterRemap:
    """Replace parameter storage on resume; backed Adam tensors restore separately."""

    def __init__(self, parameter, backed_tensors):
        self.parameter = parameter
        self.backed_tensors = backed_tensors
        self.snapshots = None
        self.remaps = 0

    def pause(self, tag=None):
        assert tag is None
        if self.snapshots is None:
            self.snapshots = [tensor.detach().clone() for tensor in self.backed_tensors]

    def resume(self, tag=None):
        assert tag is None and self.snapshots is not None
        with torch.no_grad():
            self.parameter.data = torch.zeros_like(self.parameter)
            for tensor, snapshot in zip(self.backed_tensors, self.snapshots, strict=True):
                tensor.copy_(snapshot)
        self.snapshots = None
        self.remaps += 1

    def disable(self):
        return nullcontext()


def install_unbacked_remap(actor, namespace):
    """Use native sleep/wake around a non-backed parameter and backed FP32 Adam."""
    del actor.sleep, actor.wake_up
    actor._clear_quantized_weight_workspaces = lambda: None
    master = torch.nn.Parameter(actor.model[0].weight.detach().clone())
    actor.optimizer = torch.optim.Adam([master], lr=0.01)
    master.grad = torch.ones_like(master)
    actor.optimizer.step()
    backed = [master, *(value for value in actor.optimizer.state[master].values() if isinstance(value, torch.Tensor))]
    saver = UnbackedParameterRemap(actor.model[0].weight, backed)
    namespace["torch_memory_saver"] = saver
    actor._asleep = False
    actor.sleep()
    return saver, master


@contextmanager
def eval_publication(scoring, fault):
    """Native publication owners with CPU conversion/transport and PG faults."""
    import train
    import miles.utils.reloadable_process_group as pg_module
    import miles.backends.training_utils.weight_update.updater as updater_module
    from miles.backends.training_utils.weight_update.updater import WeightUpdater
    from miles.ray import placement_group
    from miles.ray.train.cell import TrainerCell
    from miles.ray.train.cell_state import StateAllocatedAlive
    from miles.ray.train.group import TrainerController
    from miles.utils.async_utils import CancellableTasks
    from miles.utils.ft_utils.health_checker import ActivenessTracker
    from miles.utils.ft_utils.indep_dp import IndepDPInfo
    from miles.utils.workers.worker_handle import BaseWorkerHandle, WorkerUnreachableError

    with pytest.MonkeyPatch.context() as patch:
        args = make_args()
        args.colocate = True
        args.offload_rollout = True
        args.offload_rollout_level = "kv_cache,weight"
        args.log_inference_engine_weight_checksums = False
        actor = make_actor(scoring.actor_cls, args)
        actor._get_actor_weights = MethodType(scoring.actor_cls._get_actor_weights, actor)
        engine_weights = actor.model[0].weight.detach().clone()
        events = []
        pg = SimpleNamespace(group=None, inner_args=(), inner_kwargs={})
        reload_calls = 0

        def new_group(*args, **kwargs):
            nonlocal reload_calls
            reload_calls += 1
            events.append("reload_pg")
            if fault == "persistent" or reload_calls == 1:
                raise RuntimeError("Injected process-group construction failure")
            return SimpleNamespace(active=True)

        def destroy(group):
            group.active = False
            events.append("destroy_pg")

        patch.setattr(pg_module.ReloadableProcessGroup, "GROUPS", {os.getpid(): [pg]})
        patch.setattr(pg_module, "old_new_group_dict", {os.getpid(): new_group})
        patch.setattr(pg_module.dist, "destroy_process_group", destroy)
        saver, master = install_unbacked_remap(actor, scoring.namespace)
        scoring.namespace["reload_process_groups"] = pg_module.reload_process_groups
        scoring.namespace["destroy_process_groups"] = pg_module.destroy_process_groups
        patch.setattr(updater_module, "get_gloo_group", lambda: None)
        updater = object.__new__(WeightUpdater)
        updater.args = args
        updater.is_lora = False
        updater.weights_getter = actor._get_actor_weights

        def buckets(weights, **kwargs):
            assert pg.group is not None and pg.group.active, "model gather requires a live PG"
            yield list(weights.items())

        def send(bucket):
            events.append("send_bucket")
            engine_weights.copy_(dict(bucket)["weight"])

        updater._hf_weight_iterator = SimpleNamespace(
            placement=SimpleNamespace(gather_pp=True), iter_hf_weights=buckets,
        )
        updater.protocol = SimpleNamespace(
            begin_sync=lambda *args: True, use_weight_update_session=False,
            is_sender=True, group_name="cpu",
            cell_updaters_of_cell_id={"engine0": SimpleNamespace(cell_id="engine0", is_errored=False)},
            send_bucket=send, after_base_weights=lambda: None,
            finalize=lambda version: events.append(("finalize", version)),
            after_engines_resumed=lambda: None,
        )
        updater.conn_status = SimpleNamespace(needs_reconnect=lambda snapshot: False)
        actor.weight_updater = updater

        async def score(rollout_id, rollout_data_ref):
            if fault == "unavailable":
                raise WorkerUnreachableError("Injected dead worker")
            return actor.score_log_probs(rollout_id, rollout_data_ref)

        async def publish(info, debug_weight_update_id, rollout_id):
            if fault == "unavailable":
                raise WorkerUnreachableError("Worker remains dead")
            assert rollout_id is None
            return actor._update_receiver_weights(info, debug_weight_update_id, rollout_id)

        handle = Mock(spec=BaseWorkerHandle)
        handle.score_log_probs = score
        handle.update_weights = publish
        cell = object.__new__(TrainerCell)
        cell.args = args
        cell.cell_id = "trainer0"
        cell.cell_index = 0
        cell._disposed = False
        cell._cancellabel_tasks = CancellableTasks()
        cell._state = StateAllocatedAlive(worker_handles=[handle], indep_dp_info=IndepDPInfo.create_trivial())

        async def confirm_dead():
            events.append("cell_killed")

        cell._kill_workers_and_confirm_dead = confirm_dead
        controller = object.__new__(TrainerController)
        controller.args = args
        controller._cells_by_id = {"trainer0": cell}
        controller._health_checker_activeness = ActivenessTracker(active=False)
        controller._debug_trainer_load_state_timestamp = 0.0
        info = SimpleNamespace(
            rollout_engines=[SimpleNamespace()], engine_cell_ids=["engine0"],
            snapshot_cell_id_to_hashes={"engine0": "workers0"}, receiver_pool="rollout",
        )

        async def offload(*, tags):
            engine_weights.zero_()
            events.append(("offload", list(tags)))

        async def onload(*, tags):
            events.append(("onload", list(tags)))

        async def start_update_weights(*, model_id):
            assert model_id is None
            events.append("start_update")
            return info

        async def end_update_weights(**kwargs):
            assert kwargs["snapshot_cell_id_to_hashes"] == info.snapshot_cell_id_to_hashes
            assert kwargs["failed_cell_ids"] == ()
            events.append("end_update")
            return []

        async def abort_update_weights():
            events.append("abort_update")

        async def prepare_eval():
            events.append("prepare_eval")

        async def set_version(version, *, trainer_model_id):
            assert version == 7 and trainer_model_id is None
            events.append(("consumed_version", version))

        inference = SimpleNamespace(
            offload=offload, onload=onload, start_update_weights=start_update_weights,
            end_update_weights=end_update_weights, abort_update_weights=abort_update_weights,
            prepare_eval=prepare_eval,
        )
        patch.setattr(train, "update_weights", placement_group.update_weights)
        yield SimpleNamespace(
            actor=actor, saver=saver, master=master, engine_weights=engine_weights,
            events=events, pg=pg, cell=cell, controller=controller, inference=inference,
            executor=SimpleNamespace(set_weight_version=set_version),
        )


def install_cpu_runtime(monkeypatch, store, parallel):
    from miles.backends.training_utils import parallel as parallel_module

    monkeypatch.setattr(object_store, "_INSTANCE", store)
    monkeypatch.setattr(parallel_module, "_parallel_state", parallel)
    monkeypatch.setattr(current_platform, "current_device", lambda: torch.device("cpu"))
    monkeypatch.setattr(torch.cuda, "synchronize", lambda: None)
