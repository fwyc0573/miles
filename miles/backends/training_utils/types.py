from dataclasses import dataclass
from enum import auto
from typing import Literal

import torch
from typing_extensions import NotRequired, TypedDict

from miles.utils.object_store import StoreObjectRef

try:
    from enum import StrEnum
except ImportError:
    from backports.strenum import StrEnum


class TrainStepOutcome(StrEnum):
    NORMAL = auto()
    DISCARDED_SHOULD_RETRY = auto()


@dataclass(frozen=True)
class TrainStepOutput:
    outcome: TrainStepOutcome
    values: StoreObjectRef | None = None


class LogProbScoreMetadata(TypedDict):
    rollout_id: int
    weight_version: int
    cell_index: int
    rank: int
    dp_rank: int
    dp_size: int
    tp_rank: int
    tp_size: int
    cp_rank: int
    cp_size: int
    pp_rank: int
    pp_size: int
    qkv_format: str
    allgather_cp: bool
    response_layout: Literal["response", "zigzag"]
    rollout_temperature: float
    log_probs_backend: str
    true_on_policy_mode: bool
    use_rollout_sampling_mask: bool


class LogProbScoreBatch(TypedDict):
    """One PP-last/TP0 rank's raw response scores, in native DP-shard row order.

    Tokens and original response masks are full native input receipts, without
    padding or CP slicing. CP>1 scores use the native zigzag response slicing,
    including when the model forward uses all-gather CP. Join source identity and
    rollout versions by ``sample_indices``.
    """

    log_probs: list[torch.Tensor | list[float]]
    tokens: list[torch.Tensor | list[int]]
    loss_masks: list[torch.Tensor | list[int]]
    sample_indices: list[int]
    total_lengths: list[int]
    response_lengths: list[int]
    max_seq_lens: NotRequired[list[int]]
    metadata: LogProbScoreMetadata
