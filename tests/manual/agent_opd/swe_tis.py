"""Binary two-level TIS and original-mask measurements for native OPD."""

from dataclasses import dataclass
from numbers import Integral
from typing import Any

import torch

from miles.utils.args.schema import A, Arg, BaseConfig


class SweTISConfig(BaseConfig):
    tis_token_lower: A[float, Arg()] = 0.5
    tis_token_upper: A[float, Arg()] = 2.0
    tis_answer_lower: A[float, Arg()] = 0.9897
    tis_answer_upper: A[float, Arg()] = 1.001


@dataclass(frozen=True)
class TISResult:
    masks: list[torch.Tensor]
    token_pass: list[torch.Tensor]
    answer_pass: list[torch.Tensor]
    finite: list[torch.Tensor]


def compute_tis(
    student: list[torch.Tensor],
    behavior: list[torch.Tensor],
    original_masks: list[torch.Tensor],
    config: SweTISConfig,
) -> TISResult:
    """Use original eligible tokens for the answer's geometric mean, never survivors."""
    masks, tokens, answers, finite_masks = [], [], [], []
    for s, b, mask in zip(student, behavior, original_masks, strict=True):
        if s.ndim != 1 or s.shape != b.shape or s.shape != mask.shape:
            raise ValueError("TIS requires matching one-dimensional response tensors")
        if not ((mask == 0) | (mask == 1)).all():
            raise ValueError("The original target mask must be binary")
        eligible = mask.bool()
        finite = torch.isfinite(s) & torch.isfinite(b)
        delta = s.detach().double() - b.detach().double()
        ratio = delta.exp()
        token = finite & (ratio >= config.tis_token_lower) & (ratio <= config.tis_token_upper)
        count = eligible.sum()
        # A nonfinite eligible score rejects its answer, rather than silently
        # changing the original-token denominator or geometric-mean population.
        answer_ratio = torch.where(eligible, delta, 0).sum().div(count.clamp_min(1)).exp()
        answer = (
            (count > 0)
            & (finite | ~eligible).all()
            & (answer_ratio >= config.tis_answer_lower)
            & (answer_ratio <= config.tis_answer_upper)
        ).expand_as(mask)
        masks.append((eligible & token & answer).to(mask.dtype).detach())
        tokens.append(token.detach())
        answers.append(answer.detach())
        finite_masks.append(finite.detach())
    return TISResult(masks, tokens, answers, finite_masks)


def token_sums(student, reverse_kl, original_masks, result: TISResult, sample_indices):
    """Measure existing native scores once per sample; CP partials remain additive."""
    device = original_masks[0].device
    zero = torch.zeros((), dtype=torch.float64, device=device)
    sums = {
        name: zero.clone() for name in (
            "kl_before_tis_numerator", "nonfinite_tokens", "token_rejected_tokens", "answer_rejected_tokens"
        )
    }
    rows, indices = [], []
    for s, k, m, f, t, a, index in zip(
        student, reverse_kl, original_masks, result.finite, result.token_pass, result.answer_pass,
        sample_indices, strict=True,
    ):
        if s.ndim != 1 or s.shape != k.shape or s.shape != m.shape:
            raise ValueError("Turn sums require matching native response tensors")
        if isinstance(index, bool) or not isinstance(index, Integral):
            raise ValueError("Turn sums require native integer sample indices")
        indices.append(int(index))
        eligible = m.bool()
        row = torch.stack((torch.where(eligible, k.detach().double(), 0).sum(),
                           torch.where(eligible, -s.detach().double(), 0).sum(), m.double().sum()))
        rows.append(row)
        sums["kl_before_tis_numerator"] += row[0]
        sums["nonfinite_tokens"] += (eligible & ~f).double().sum()
        sums["token_rejected_tokens"] += (eligible & ~t).double().sum()
        sums["answer_rejected_tokens"] += (eligible & ~a).double().sum()
    return sums, {"sample_indices": indices, "values": torch.stack(rows)}


def apply_tis(
    args,
    *,
    pg_loss: torch.Tensor,
    train_log_probs: list[torch.Tensor],
    rollout_log_probs: list[torch.Tensor],
    teacher_log_probs: list[torch.Tensor] | None,
    loss_masks: list[torch.Tensor],
    total_lengths: list[int],
    response_lengths: list[int],
    max_seq_lens=None,
    sample_indices=None,
    opd_reverse_kl=None,
    **kwargs: Any,
):
    # Defer native parallel utilities so the pure calculation needs no runtime.
    from miles.backends.training_utils.data.context_parallel import (
        all_gather_with_cp, get_local_response_loss_masks, slice_log_prob_with_cp,
    )

    def gather(values):
        return [all_gather_with_cp(x.detach(), n, r, args.qkv_format,
                                   max_seq_lens[i] if max_seq_lens is not None else None)
                for i, (x, n, r) in enumerate(zip(values, total_lengths, response_lengths, strict=True))]

    result = compute_tis(gather(train_log_probs), gather(rollout_log_probs), loss_masks, args)
    local_masks = get_local_response_loss_masks(
        total_lengths, response_lengths, loss_masks, args.qkv_format, max_seq_lens
    )

    def local(values):
        return [slice_log_prob_with_cp(x, n, r, args.qkv_format,
                                      max_seq_lens[i] if max_seq_lens is not None else None)
                for i, (x, n, r) in enumerate(zip(values, total_lengths, response_lengths, strict=True))]

    local_result = TISResult(*(local(getattr(result, name))
                              for name in ("masks", "token_pass", "answer_pass", "finite")))
    # Measurement failures are auxiliary, unlike failures in native TIS itself.
    # No collective is inside this block, so every rank reaches the optimizer's
    # fixed aggregation order even when one rank cannot measure its partials.
    try:
        sums, turn_sums = token_sums(train_log_probs, opd_reverse_kl, local_masks, local_result, sample_indices)
    except Exception as error:
        sums, turn_sums = {}, {"error": f"{type(error).__name__}: {error}"}
    # Both branches share the exact mask used by the native loss reducer. The
    # where also avoids propagating NaN on a rejected token through 0 * NaN.
    retained = torch.cat(local_result.masks).bool()
    pg_loss = torch.where(retained, pg_loss, 0)
    return pg_loss, result.masks, {
        "swe_tis_retained": retained.float(),
        "token_sums": sums,
        "turn_sums": turn_sums,
        "mask_evidence": {
            "sample_indices": sample_indices,
            "original_masks": local_masks,
            "survivor_masks": local_result.masks,
            "student": [x.detach() for x in train_log_probs],
            "behavior": [x.detach() for x in rollout_log_probs],
            "teacher": [x.detach() for x in teacher_log_probs] if teacher_log_probs is not None else None,
        },
    }


apply_tis.config_class = SweTISConfig
