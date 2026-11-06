"""CPU boundary for production RPC methods whose Megatron runtime is unavailable.

Only the CUDA pipeline, memory residency and packed-sequence SDK are replaced;
rollout loading/splitting, scheduling, scoring and RPC serialization stay native.
"""

import ast
import copy
import dataclasses
import random
from argparse import Namespace
from collections.abc import Callable, Iterator, Sequence
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
import torch.distributed as dist
from tests.fast.fixtures.args_fixtures import parser_defaults

from miles.backends.training_utils.data.rollout import DataIterator, get_batch, get_data_iterator, get_rollout_data
from miles.backends.training_utils.loss.hub.logit_processors import get_log_probs_and_entropy
from miles.backends.training_utils.metrics.log_utils import aggregate_forward_results
from miles.backends.training_utils.model_companion import ModelCompanion, ModelCompanionWeightVersionUtils
from miles.backends.training_utils.parallel import ParallelState, get_parallel_state
from miles.backends.training_utils.types import LogProbScoreBatch, LogProbScoreMetadata
from miles.platforms import current_platform
from miles.utils import object_store
from miles.utils.ft_utils.process_group_utils import GroupInfo
from miles.utils.object_store import BaseObjectStore, ObjectStoreGetResult, StoreObjectRef, ValueSpec
from miles.utils.timer import timer
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
        all_replay_managers=[],
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

    def wake():
        actor.lifecycle.append("wake")
        actor._asleep = False

    def sleep():
        actor.lifecycle.append("sleep")
        actor._asleep = True

    actor.wake_up = wake
    actor.sleep = sleep
    return actor


def install_cpu_runtime(monkeypatch, store, parallel):
    from miles.backends.training_utils import parallel as parallel_module

    monkeypatch.setattr(object_store, "_INSTANCE", store)
    monkeypatch.setattr(parallel_module, "_parallel_state", parallel)
    monkeypatch.setattr(current_platform, "current_device", lambda: torch.device("cpu"))
