"""Independent D4/S4 reference, exact masks and native CPU gradient checks."""

import math
from functools import partial
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import patch

import pytest
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel

from miles.backends.training_utils.loss.objective import compute_advantages_and_returns, loss_function
from miles.backends.training_utils.loss.hub.logit_processors import get_log_probs_and_entropy
from miles.backends.training_utils.loss.hub.losses import _training_mask_counts
from miles.utils.args.custom_function import CustomFunctionConfig
from tests.fast.backends.training_utils.loss.loss_test_utils import make_args, make_parallel_state
from tests.fast.dist_utils import init_gloo, run_multiprocess
from tests.ci.ci_register import register_cpu_ci
from tests.manual.agent_opd.swe_tis import SweTISConfig, compute_tis
from tests.manual.agent_opd.swe_training import ZeroTISSurvivors, optimizer_step, reduce_token_sums, reduce_training_masks

register_cpu_ci(est_time=50, suite="stage-b-cpu", labels=["precision"])


def reference(s, b, masks):
    outputs = []
    for student, behavior, mask in zip(s, b, masks, strict=True):
        selected = [x - y for x, y, m in zip(student, behavior, mask, strict=True) if m]
        finite = bool(selected) and all(math.isfinite(x) for x in selected)
        answer = math.exp(sum(selected) / len(selected)) if finite else float("nan")
        outputs.append([int(bool(m) and math.isfinite(x) and math.isfinite(y)
                            and 0.5 <= math.exp(x - y) <= 2 and 0.9897 <= answer <= 1.001)
                        for x, y, m in zip(student, behavior, mask, strict=True)])
    return outputs


def test_threshold_edges_masks_and_nonfinite():
    ratios = [[0.5, 2.0], [0.9897], [1.001], [0.98969], [1.00101], [0.5 - 1e-7, 2 + 1e-7], [1.0, float("nan")]]
    s = [[math.log(r) for r in values] for values in ratios]
    b = [[0.0] * len(values) for values in ratios]
    masks = [[1, 1], [1], [1], [1], [1], [1, 1], [1, 0]]
    result = compute_tis([torch.tensor(x, dtype=torch.float64) for x in s],
                         [torch.tensor(x, dtype=torch.float64) for x in b],
                         [torch.tensor(x) for x in masks], SweTISConfig())
    assert [x.tolist() for x in result.masks] == reference(s, b, masks)
    assert [x.tolist() for x in result.masks][:3] == [[1, 1], [1], [1]]
    assert not any(x.requires_grad for x in result.masks)


def _native_case():
    make_parallel_state()
    args = make_args(loss_type="policy_loss", calculate_per_token_loss=True, global_batch_size=3,
                     use_opd=True, opd_type="sglang", opd_kl_coef=1.0, kl_coef=0.0, entropy_coef=0.0,
                     eps_clip_high=0.28, observe_training_entropy=False, use_tis=True,
                     custom_tis_function_path=CustomFunctionConfig(path="tests.manual.agent_opd.swe_tis.apply_tis",
                                                                    config=SweTISConfig()))
    torch.manual_seed(17)
    logits = torch.randn(1, 15, 8, requires_grad=True)
    batch = {"total_lengths": [5, 6, 4], "response_lengths": [3, 4, 2],
             "unconcat_tokens": [torch.tensor([0, 1, 2, 3, 4]), torch.tensor([0, 1, 2, 3, 4, 5]), torch.tensor([0, 1, 2, 3])],
             "loss_masks": [torch.tensor([1, 0, 1]), torch.tensor([1, 1, 1, 0]), torch.tensor([1, 1])],
             "rewards": [0.0] * 3, "sample_indices": [0, 1, 2]}
    train = get_log_probs_and_entropy(logits, args=args, unconcat_tokens=batch["unconcat_tokens"],
                                     total_lengths=batch["total_lengths"], response_lengths=batch["response_lengths"],
                                     with_entropy=False)["log_probs"]
    batch["log_probs"] = [x.detach().clone().requires_grad_() for x in train]
    batch["rollout_log_probs"] = [batch["log_probs"][0].detach() - torch.tensor([math.log(0.49), 0, -math.log(0.49)]),
                                  batch["log_probs"][1].detach().clone(),
                                  batch["log_probs"][2].detach() - math.log(1.01)]
    batch["teacher_log_probs"] = [x.detach().clone().add_(0.3).requires_grad_() for x in train]
    return args, batch, logits, train


def _optimizer_context(directory, batch, log, *, attempt):
    data = {"metadata": [{"swe_successful_before": 0, "swe_bank": 0, "swe_bank_visit": 1,
                           "generation_weight_versions": [], "current_weight_version": 0,
                           "swe_actual_bank_turns": 3, "swe_original_bank_tokens": 7}],
            "num_microbatches": [1], "tokens": batch["unconcat_tokens"]}
    config = SimpleNamespace(swe_evidence_dir=str(directory), swe_cell="A/r256", swe_attempt=attempt,
                             swe_teacher_identity="A", swe_run_kind="smoke", swe_protocol="r256")
    return config, dict(rollout_id=0, step_id=0, data_iterator=[SimpleNamespace(rollout_data=data)],
                        model=[torch.nn.Linear(2, 2)], losses_reduced=[log])


@pytest.mark.parametrize("omitted", ["kl", "rejection", "mask_evidence"])
def test_optional_diagnostic_omissions_keep_actual_survivors(tmp_path, omitted):
    args, batch, logits, _ = _native_case()
    compute_advantages_and_returns(args, batch)
    _, _, log = loss_function(args, batch, 1, logits, num_rollouts=3, num_step_tokens=torch.tensor(7))
    if omitted == "mask_evidence":
        log.pop("mask_evidence")
    else:
        log["token_sums"].pop("kl_before_tis_numerator" if omitted == "kl" else "answer_rejected_tokens")
    config, context = _optimizer_context(tmp_path, batch, log, attempt=omitted)
    context["optimizer"] = torch.optim.AdamW([logits], lr=2e-6)
    optimizer_step(config, stage="before_optimizer", update_successful=False, **context)
    result = optimizer_step(config, stage="after_optimizer", update_successful=False, **context)
    assert result["original_tokens"] == 7 and result["surviving_tokens"] == 3
    assert result["actual_turns"] == 3
    if omitted == "mask_evidence":
        assert not result["mask_evidence_verified"]
    else:
        assert not result["diagnostics_verified"]
        assert result["kl_before_tis_numerator" if omitted == "kl" else "answer_rejected_tokens"] is None


@pytest.mark.parametrize("failure", [BrokenPipeError, OSError])
@pytest.mark.parametrize("sink", ["stdout", "file"])
def test_diagnostic_sink_failure_after_real_update_still_returns_ack(tmp_path, monkeypatch, failure, sink):
    args, batch, logits, _ = _native_case()
    compute_advantages_and_returns(args, batch)
    loss, _, log = loss_function(args, batch, 1, logits, num_rollouts=3, num_step_tokens=torch.tensor(7))
    loss.backward()
    attempt = f"{sink}-{failure.__name__}"
    config, context = _optimizer_context(tmp_path, batch, log, attempt=attempt)
    optimizer = torch.optim.AdamW([logits], lr=2e-6, betas=(0.9, 0.98), eps=1e-8, weight_decay=0.1)
    context["optimizer"] = optimizer
    optimizer_step(config, stage="before_optimizer", update_successful=False, **context)
    before = logits.detach().clone()
    optimizer.step()

    def unavailable(*args, **kwargs):
        raise failure("diagnostic sink unavailable")

    with monkeypatch.context() as patch:
        from tests.manual.agent_opd import swe_training

        if sink == "stdout":
            patch.setattr("builtins.print", unavailable)
        else:
            patch.setattr(swe_training, "append_record", unavailable)
        patch.setattr(swe_training.logger, "warning", unavailable)
        result = optimizer_step(config, stage="after_optimizer", update_successful=True, **context)
    assert result["successful_updates"] == 1
    assert optimizer.state[logits]["step"].item() == 1
    assert not torch.equal(logits, before)
    from tests.manual.agent_opd import swe_training

    assert swe_training._receipts[(str(tmp_path), "A/r256", attempt)].pending == {}


@pytest.mark.parametrize("clipped", [False, True])
def test_native_surrogate_gradient_detach_and_original_denominator(clipped):
    args, batch, logits, train = _native_case()
    if clipped:
        shifts = torch.tensor([math.log(1.5), math.log(0.7), math.log(1.1), 0.0])
        batch["log_probs"][1] = batch["log_probs"][1].detach().sub(shifts).requires_grad_()
        batch["rollout_log_probs"][1] = batch["log_probs"][1].detach().clone()
        batch["teacher_log_probs"][1] = batch["log_probs"][1].detach().add(torch.tensor([0.3, -0.4, 0.2, 0.0])).requires_grad_()
    compute_advantages_and_returns(args, batch)
    expected_masks = reference([x.tolist() for x in batch["log_probs"]],
                               [x.tolist() for x in batch["rollout_log_probs"]],
                               [x.tolist() for x in batch["loss_masks"]])
    assert expected_masks == [[0, 0, 0], [1, 1, 1, 0], [0, 0]]
    expected = logits.sum() * 0
    for l, s, q, mask in zip(train, batch["log_probs"], batch["teacher_log_probs"], expected_masks, strict=True):
        advantage = (q - s).detach()
        ratio = (l - s.detach()).exp()
        expected += (torch.tensor(mask) * torch.maximum(-ratio * advantage, -ratio.clamp(0.8, 1.28) * advantage)).sum()
    expected /= 7
    expected_grad = torch.autograd.grad(expected, logits, retain_graph=True)[0]
    actual, count, log = loss_function(args, batch, 1, logits, num_rollouts=3, num_step_tokens=torch.tensor(7))
    actual.backward()
    torch.testing.assert_close(actual, expected)
    torch.testing.assert_close(logits.grad, expected_grad)
    assert count.item() == 7
    assert log["training_mask_counts"].tolist() == [7, 3, 3]
    assert log["token_sums"]["kl_before_tis_numerator"].item() == pytest.approx(-1.3 if clipped else -2.1, abs=1e-6)
    assert all(x.grad is None for x in batch["teacher_log_probs"] + batch["log_probs"])
    assert all(not x.requires_grad for x in batch["advantages"])
    native_post = log["values"][log["keys"].index("opd_reverse_kl") + 1].item()
    assert native_post == pytest.approx(-0.1 if clipped else -0.9, abs=1e-6)


def test_global_guard_runs_before_step_and_does_not_use_missing_logs(tmp_path, monkeypatch):
    args, batch, logits, _ = _native_case()
    compute_advantages_and_returns(args, batch)
    _, _, log = loss_function(args, batch, 1, logits, num_rollouts=3, num_step_tokens=torch.tensor(7))
    data = {"metadata": [{"swe_successful_before": 0, "swe_bank": 0, "swe_bank_visit": 1,
                           "generation_weight_versions": [], "current_weight_version": 0,
                           "swe_actual_bank_turns": 3, "swe_original_bank_tokens": 7}],
            "num_microbatches": [1], "tokens": batch["unconcat_tokens"]}
    config = SimpleNamespace(swe_evidence_dir=str(tmp_path), swe_cell="A/r256", swe_attempt="test", swe_teacher_identity="A",
                             swe_run_kind="smoke", swe_protocol="r256")
    kwargs = dict(rollout_id=0, step_id=0, data_iterator=[SimpleNamespace(rollout_data=data)],
                  model=[torch.nn.Linear(2, 2)], optimizer=torch.optim.AdamW([logits], lr=2e-6), losses_reduced=[log])
    data["metadata"][0]["swe_original_bank_tokens"] = 8
    optimizer_step(config, stage="before_optimizer", update_successful=False, **kwargs)
    from tests.manual.agent_opd import swe_training

    def unavailable(*args):
        raise OSError("evidence disk unavailable")

    with monkeypatch.context() as patch:
        patch.setattr(swe_training, "append_record", unavailable)
        skipped = optimizer_step(config, stage="after_optimizer", update_successful=False, **kwargs)
    assert skipped["successful_updates"] == 0
    assert not skipped["bank_membership_verified"]
    data["metadata"][0]["swe_original_bank_tokens"] = 7
    optimizer_step(config, stage="before_optimizer", update_successful=False, **kwargs)
    success = optimizer_step(config, stage="after_optimizer", update_successful=True, **kwargs)
    assert success["successful_updates"] == 1
    data["metadata"][0]["swe_successful_before"] = 1
    batch["rollout_log_probs"] = [x - math.log(1.01) for x in batch["log_probs"]]
    _, _, rejected_log = loss_function(args, batch, 1, logits, num_rollouts=3, num_step_tokens=torch.tensor(7))
    assert rejected_log["training_mask_counts"][1].item() == 0
    kwargs["losses_reduced"] = [rejected_log]
    with pytest.raises(ZeroTISSurvivors):
        optimizer_step(config, stage="before_optimizer", update_successful=False, **kwargs)
    assert (tmp_path / "failed_batches.jsonl").exists()
    assert (tmp_path / "zero_tis_rollout_0_rank_0.pt").exists()
    evidence = torch.load(tmp_path / "zero_tis_rollout_0_rank_0.pt", weights_only=False)
    assert all(mask.sum().item() == 0 for item in evidence for mask in item["survivor_masks"])
    omitted = reduce_token_sums([{"keys": [], "values": torch.tensor([0])}], device="cpu", contribute=True, expected_microbatches=1)
    assert not omitted["diagnostics_verified"] and omitted["kl_before_tis_numerator"] is None
    with pytest.raises(RuntimeError, match="unknown, not zero"):
        reduce_training_masks([{}], device="cpu", contribute=True, count_turns=True, expected_microbatches=1)


def _gloo_gradient_and_guard(rank, world_size, port, *, directory):
    init_gloo(rank, world_size, port=port)
    torch.set_num_threads(1)
    # Exercise native tensor calculations eagerly; compiler/kernel qualification
    # belongs to the required GPU run, not this CPU/Gloo gradient check.
    torch.compiler.set_stance("force_eager")
    from miles.backends.training_utils.parallel import GroupInfo, ParallelState, set_parallel_state

    trivial = GroupInfo(rank=0, size=1, group=None)
    dp = GroupInfo(rank=rank, size=world_size, group=dist.group.WORLD)
    tp = GroupInfo(rank=0, size=1, group=[dist.new_group([r]) for r in range(world_size)][rank])
    set_parallel_state(ParallelState(intra_dp=dp, intra_dp_cp=dp, cp=trivial, tp=tp, pp=trivial,
                                    ep=trivial, etp=trivial, indep_dp=trivial))
    torch.manual_seed(9)
    model = DistributedDataParallel(torch.nn.Linear(2, 8, bias=False))
    reference_model = torch.nn.Linear(2, 8, bias=False)
    reference_model.load_state_dict(model.module.state_dict())
    optimizer = torch.optim.AdamW(model.parameters(), lr=2e-6, betas=(0.9, 0.98), eps=1e-8, weight_decay=0.1)
    args = make_args(calculate_per_token_loss=True, true_on_policy_mode=False, use_opd=True, opd_type="sglang",
                     kl_coef=0.0, entropy_coef=0.0, eps_clip_high=0.28, observe_training_entropy=False, use_tis=True,
                     custom_tis_function_path=CustomFunctionConfig(path="tests.manual.agent_opd.swe_tis.apply_tis",
                                                                    config=SweTISConfig()))
    config = SimpleNamespace(swe_evidence_dir=directory, swe_cell="A/r256", swe_attempt="gloo", swe_teacher_identity="A",
                             swe_run_kind="smoke", swe_protocol="r256")
    data = {"num_microbatches": [2], "tokens": [[0, 1, 2, 3]] * 2,
            "metadata": [{"swe_successful_before": 0, "swe_bank": 0, "swe_bank_visit": 1,
                           "generation_weight_versions": [], "current_weight_version": 0,
                           "swe_actual_bank_turns": 4, "swe_original_bank_tokens": 6}]}

    def native_microbatch(index, reject_all=False):
        inputs = torch.arange(8, dtype=torch.float32).reshape(1, 4, 2) / 8 + (rank + index) / 10
        logits = model(inputs)
        batch = {"total_lengths": [4], "response_lengths": [2], "unconcat_tokens": [torch.tensor([0, 1, 2, 3])],
                 "loss_masks": [torch.tensor([1, 0]) if rank == 0 else torch.tensor([1, 1])],
                 "sample_indices": [rank * 2 + index], "rewards": [0.0]}
        scores = get_log_probs_and_entropy(logits, args=args, unconcat_tokens=batch["unconcat_tokens"],
                                          total_lengths=[4], response_lengths=[2], with_entropy=False)["log_probs"]
        batch["log_probs"] = [x.detach() for x in scores]
        batch["teacher_log_probs"] = [x.detach() + 0.3 for x in scores]
        batch["rollout_log_probs"] = [x.detach() - math.log(1.01) if rank == 0 or reject_all else x.detach() for x in scores]
        compute_advantages_and_returns(args, batch)
        loss, _, log = loss_function(args, batch, 2, logits, num_rollouts=4, num_step_tokens=torch.tensor(6))
        loss.backward()
        return log

    logs = [native_microbatch(i) for i in range(2)]
    expected = 0
    for index in range(2):
        inputs = torch.arange(8, dtype=torch.float32).reshape(1, 4, 2) / 8 + (1 + index) / 10
        values = reference_model(inputs).log_softmax(-1)[0, 1:3]
        l = values[torch.arange(2), torch.tensor([2, 3])]
        expected += (-0.3 * (l - l.detach()).exp()).sum() / 6
    expected.backward()
    torch.testing.assert_close(model.module.weight.grad, reference_model.weight.grad, rtol=2e-5, atol=1e-7)
    kwargs = dict(rollout_id=0, step_id=0, data_iterator=[SimpleNamespace(rollout_data=data)],
                  model=[model.module], optimizer=optimizer, losses_reduced=logs)
    optimizer_step(config, stage="before_optimizer", update_successful=False, **kwargs)
    optimizer.step()
    with patch("builtins.print", side_effect=BrokenPipeError("rank-0 stdout unavailable")) if rank == 0 else nullcontext():
        record = optimizer_step(config, stage="after_optimizer", update_successful=True, **kwargs)
    acknowledgements = [None] * world_size
    dist.all_gather_object(acknowledgements, record)
    assert all(result == record for result in acknowledgements)
    assert record["original_tokens"] == 6 and record["surviving_tokens"] == 4
    assert record["kl_before_tis_numerator"] == pytest.approx(-1.8, abs=1e-6)
    assert record["successful_updates"] == 1
    before = model.module.weight.detach().clone()
    data["metadata"][0]["swe_successful_before"] = 1
    data["metadata"][0]["swe_bank_visit"] = 2
    for rollout_id, missing in enumerate(("mask_evidence", "kl", "all"), start=1):
        optimizer.zero_grad()
        logs = [native_microbatch(i) for i in range(2)]
        if missing == "mask_evidence" and rank == 0:
            logs[0].pop("mask_evidence")
        if missing == "kl":
            logs[0]["token_sums"].pop("kl_before_tis_numerator" if rank == 0 else "answer_rejected_tokens")
        if missing == "all":
            if rank == 0:
                logs[0].pop("token_sums")
                logs[0]["keys"] = []
            else:
                logs[0].pop("mask_evidence")
        kwargs.update(rollout_id=rollout_id, losses_reduced=logs)
        optimizer_step(config, stage="before_optimizer", update_successful=False, **kwargs)
        result = optimizer_step(config, stage="after_optimizer", update_successful=False, **kwargs)
        assert result["original_tokens"] == 6 and result["surviving_tokens"] == 4 and result["actual_turns"] == 4
        if missing == "mask_evidence":
            assert not result["mask_evidence_verified"] and result["diagnostics_verified"]
        else:
            assert not result["diagnostics_verified"] and result["kl_before_tis_numerator"] is None
        assert result["successful_updates"] == 1
    if rank == 0:
        logs[0].pop("training_mask_counts")
    with pytest.raises(RuntimeError, match="unknown, not zero"):
        optimizer_step(config, stage="before_optimizer", update_successful=False, **kwargs)
    optimizer.zero_grad()
    logs = [native_microbatch(i, reject_all=True) for i in range(2)]
    if rank == 0:
        logs[0]["token_sums"].pop("kl_before_tis_numerator")
    else:
        logs[0].pop("mask_evidence")
    kwargs.update(rollout_id=4, losses_reduced=logs)
    with pytest.raises(ZeroTISSurvivors):
        optimizer_step(config, stage="before_optimizer", update_successful=False, **kwargs)
    torch.testing.assert_close(model.module.weight, before, rtol=0, atol=0)
    assert optimizer.state[model.module.weight]["step"].item() == 1
    dist.destroy_process_group()


def test_cpu_gloo_gradient_global_mask_and_real_adam_counter(tmp_path):
    run_multiprocess(partial(_gloo_gradient_and_guard, directory=str(tmp_path)))


def _gloo_cp_tis(rank, world_size, port):
    init_gloo(rank, world_size, port=port)
    torch.set_num_threads(1)
    from miles.backends.training_utils.data.context_parallel import get_local_response_loss_masks, slice_log_prob_with_cp
    from miles.backends.training_utils.parallel import GroupInfo, ParallelState, set_parallel_state
    from tests.manual.agent_opd.swe_tis import apply_tis

    trivial = GroupInfo(rank=0, size=1, group=None)
    cp = GroupInfo(rank=rank, size=world_size, group=dist.group.WORLD)
    set_parallel_state(ParallelState(intra_dp=trivial, intra_dp_cp=cp, cp=cp, tp=trivial, pp=trivial,
                                    ep=trivial, etp=trivial, indep_dp=trivial))
    s = torch.zeros(8, dtype=torch.float64)
    b = -torch.tensor([math.log(x) for x in [0.5, 2, 1, 1, 0.49, 1 / 0.49, 1, 1]], dtype=torch.float64)
    mask = torch.tensor([1, 1, 0, 1, 1, 1, 1, 1])
    local_s, local_b = [slice_log_prob_with_cp(x, 12, 8) for x in [s, b]]
    pg_loss = torch.ones_like(local_s, requires_grad=True)
    config = SimpleNamespace(qkv_format="thd", **SweTISConfig().model_dump())
    actual, masks, metrics = apply_tis(config, pg_loss=pg_loss, train_log_probs=[local_s], rollout_log_probs=[local_b],
                                     teacher_log_probs=[local_s + 0.3], loss_masks=[mask], total_lengths=[12], response_lengths=[8])
    expected = torch.tensor(reference([s.tolist()], [b.tolist()], [mask.tolist()])[0])
    assert masks[0].tolist() == expected.tolist()
    actual.sum().backward()
    torch.testing.assert_close(pg_loss.grad, slice_log_prob_with_cp(expected.double(), 12, 8), rtol=0, atol=0)
    sums = reduce_token_sums([{"token_sums": metrics["token_sums"], "keys": ["loss"], "values": torch.tensor([7, 0])}],
                             device="cpu", contribute=True, expected_microbatches=1)
    counts = _training_mask_counts(get_local_response_loss_masks([12], [8], [mask]),
                                   get_local_response_loss_masks([12], [8], masks))
    actual_counts = reduce_training_masks([{"training_mask_counts": counts}], device="cpu", contribute=True,
                                         count_turns=rank == 0, expected_microbatches=1)
    assert actual_counts == {"original_tokens": 7, "surviving_tokens": 5, "actual_turns": 1}
    assert sums["kl_before_tis_numerator"] == pytest.approx(-2.1)
    dist.destroy_process_group()


def test_cpu_gloo_cp_geometric_mean_and_exact_token_sums():
    run_multiprocess(_gloo_cp_tis)
