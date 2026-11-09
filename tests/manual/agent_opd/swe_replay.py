"""Sealed full/r256 banks on Miles' native rollout and data-source lifecycle."""

import asyncio
import copy
import json
import logging
import math
import time
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from miles.rollout.base_types import (
    BaseRolloutFn, RolloutFnTrainInput, RolloutFnTrainOutput, compute_kv_cache_namespace, stamp_kv_cache_namespace,
)
from miles.utils.args.schema import A, Arg, BaseConfig
from miles.utils.types import Sample

logger = logging.getLogger(__name__)


class SweReplayConfig(BaseConfig):
    swe_cell: A[str, Arg()]
    swe_attempt: A[str, Arg()]
    swe_protocol: A[str, Arg(choices=["full", "r256"])]
    swe_evidence_dir: A[str, Arg()]
    swe_teacher_identity: A[str, Arg()]
    swe_run_kind: A[str, Arg(choices=["formal", "smoke"])] = "formal"
    swe_bank_slots: A[int, Arg()] = 256
    swe_bank_min_fraction: A[float, Arg()] = 0.9
    swe_acquisition_seconds: A[float, Arg()] = 1800.0
    swe_bank_uses: A[int, Arg()] = 50
    swe_successful_updates: A[int, Arg()] = 200
    swe_context_tokens: A[int, Arg()] = 131072


@dataclass(frozen=True)
class BankPosition:
    successful_updates: int
    bank: int
    visit: int


class ReplaySchedule:
    """Only an acknowledged successful optimizer call commits a bank visit."""

    def __init__(self, protocol: str, *, bank_uses: int, updates: int):
        if protocol not in ("full", "r256") or bank_uses <= 0 or updates <= 0:
            raise ValueError("Invalid replay schedule")
        self.uses = 1 if protocol == "full" else bank_uses
        self.limit = updates
        self.successful = 0
        self._last_attempt = None

    @property
    def position(self) -> BankPosition:
        return BankPosition(self.successful, self.successful // self.uses, self.successful % self.uses + 1)

    def commit(self, *, attempted_rollout_id: int, successful: bool) -> None:
        if self._last_attempt is not None and attempted_rollout_id <= self._last_attempt:
            raise ValueError("Repeated or out-of-order optimizer acknowledgement")
        if self.successful >= self.limit:
            raise ValueError("The successful-update budget is exhausted")
        self._last_attempt = attempted_rollout_id
        self.successful += int(successful)


@dataclass(frozen=True)
class CanonicalTrajectory:
    """Tuple-backed scientific payload; each visit materializes a private Sample."""

    slot: int
    teacher_identity: str
    tokens: tuple[int, ...]
    original_mask: tuple[int, ...]
    behavior_log_probs: tuple[float, ...]
    teacher_log_probs: tuple[float, ...]
    sample_json: str

    @classmethod
    def seal(cls, slot: int, sample: Sample, teacher_identity: str):
        if sample.status not in (Sample.Status.COMPLETED, Sample.Status.TRUNCATED):
            raise ValueError(f"Invalid completed slot status: {sample.status}")
        response_length = sample.response_length
        mask = sample.loss_mask if sample.loss_mask is not None else [1] * response_length
        b, q = sample.rollout_log_probs, sample.teacher_log_probs
        if not response_length or response_length >= len(sample.tokens) or sample.remove_sample:
            raise ValueError("A sealed trajectory needs a prompt and eligible generated tokens")
        if b is None or q is None or not (len(b) == len(q) == len(mask) == response_length):
            raise ValueError("Canonical behavior, teacher and original-mask lengths must match")
        if not all(x in (0, 1) for x in mask) or not any(mask):
            raise ValueError("A canonical trajectory needs a nonempty binary original target mask")
        if not all(math.isfinite(x) for x in (*b, *q)):
            raise ValueError("A canonical trajectory has nonfinite original scores")
        if sample.rollout_store_plan is not None or sample.rollout_routed_experts is not None:
            raise ValueError("Dense Qwen replay retains inline token payloads, not transient routed-store ownership")
        # Native Sample serialization owns version spans and source metadata.
        value = sample.to_dict()
        value["loss_mask"] = list(mask)
        value["teacher_log_probs"] = list(q)
        value["rollout_log_probs"] = list(b)
        value["reward"] = {"reward": 0.0}
        value["opd_reverse_kl"] = None
        if hasattr(q, "tolist"):
            value["teacher_log_probs"] = q.tolist()
        if hasattr(b, "tolist"):
            value["rollout_log_probs"] = b.tolist()
        q, b = value["teacher_log_probs"], value["rollout_log_probs"]
        return cls(slot, teacher_identity, tuple(sample.tokens), tuple(mask), tuple(b), tuple(q), json.dumps(value))

    def materialize(self, *, teacher_identity: str, position: BankPosition, rollout_id: int, cell: str, attempt: str):
        if teacher_identity != self.teacher_identity:
            raise ValueError("A canonical teacher target cannot cross teacher identity")
        sample = Sample.from_dict(json.loads(self.sample_json))
        sample.tokens = list(self.tokens)
        sample.loss_mask = list(self.original_mask)
        sample.rollout_log_probs = list(self.behavior_log_probs)
        sample.teacher_log_probs = list(self.teacher_log_probs)
        sample.opd_reverse_kl = None
        sample.train_metadata = {
            **(sample.train_metadata or {}),
            "source_uid": sample.metadata["source"]["uid"],
            "swe_cell": cell, "swe_attempt": attempt,
            "swe_teacher_identity": self.teacher_identity,
            "swe_bank": position.bank, "swe_bank_visit": position.visit,
            "swe_slot": self.slot, "swe_successful_before": position.successful_updates,
            "swe_attempted_rollout_id": rollout_id,
            "generation_weight_versions": [call.to_dict() for call in sample.weight_versions],
        }
        return sample


def append_record(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, allow_nan=False) + "\n")
        stream.flush()


class AcquisitionFailed(RuntimeError):
    pass


async def acquire_bank(
    candidates: list[list[Sample]],
    generate: Callable,
    *,
    teacher_identity: str,
    seconds: float,
    minimum: int,
    persist: Callable[[dict], None],
    started_at: float | None = None,
) -> tuple[CanonicalTrajectory, ...]:
    """One absolute deadline includes generation, teacher scoring and validation.

    Cancellation is not awaited indefinitely: a task that suppresses cancellation
    owns only its private Sample and cannot publish into this or the next bank.
    """
    started = time.time() if started_at is None else started_at
    deadline = asyncio.get_running_loop().time() + seconds
    deadline_at = time.time() + seconds
    slots = {}
    for slot, group in enumerate(candidates):
        if len(group) != 1:
            raise ValueError("SWE banks require native n=1 sample groups")
        slots[slot] = copy.deepcopy(group[0])
        slots[slot].metadata["swe_acquisition"] = {
            **slots[slot].metadata.get("swe_acquisition", {}),
            "slot": slot, "started_at": started, "deadline_at": deadline_at,
        }
    def record(value):
        try:
            persist(value)
        except Exception:
            try:
                logger.exception("SWE acquisition evidence unverified; healthy collection continues")
            except Exception:
                pass

    record({"event": "acquisition_start", "started_at": started, "deadline_at": deadline_at,
             "slots": [{"slot": i, "source_uid": s.metadata["source"]["uid"], "sample_index": s.index}
                       for i, s in slots.items()]})

    async def execute(slot, candidate):
        try:
            sample = await generate(candidate)
            return slot, CanonicalTrajectory.seal(slot, sample, teacher_identity), None, asyncio.get_running_loop().time()
        except (Exception, asyncio.CancelledError) as error:
            return slot, None, f"{type(error).__name__}: {error}", asyncio.get_running_loop().time()

    tasks = {asyncio.create_task(execute(slot, candidate)): slot for slot, candidate in slots.items()}
    completed = {}
    pending = set(tasks)
    try:
        while pending:
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                break
            done, pending = await asyncio.wait(pending, timeout=remaining, return_when=asyncio.FIRST_COMPLETED)
            for task in sorted(done, key=lambda task: task.result()[3]):
                slot, trajectory, error, ended = task.result()
                if ended > deadline:
                    trajectory, error = None, "Acquisition deadline elapsed"
                if trajectory is not None:
                    completed[slot] = trajectory
                record({"event": "slot_finished", "slot": slot, "source_uid": slots[slot].metadata["source"]["uid"],
                         "status": "completed" if trajectory is not None else "invalid", "error": error,
                         "sample": json.loads(trajectory.sample_json) if trajectory is not None else None,
                         "ended_at": time.time()})
            await asyncio.sleep(0)
    finally:
        for task in pending:
            task.cancel()
            # Consume exceptions without installing any result-persistence callback.
            task.add_done_callback(lambda t: t.exception() if not t.cancelled() else None)
    missing = [i for i in slots if i not in completed]
    record({"event": "acquisition_sealed" if len(completed) >= minimum else "acquisition_failed",
             "actual_turns": len(completed), "membership": sorted(completed), "missing_slots": missing,
             "pending_slots": sorted(tasks[t] for t in pending), "ended_at": time.time()})
    if len(completed) < minimum:
        raise AcquisitionFailed(f"Only {len(completed)} valid trajectories; need {minimum}")
    return tuple(completed[i] for i in sorted(completed))


def post_process_rewards(args, samples, **kwargs):
    from miles.rollout import on_policy_distillation as opd

    pending = [sample for sample in samples if sample.teacher_log_probs is None]
    if pending:
        teacher_args = args.model_copy(update={"reward_key": "teacher_response"})
        opd.post_process_rewards(teacher_args, pending)
    return [0.0] * len(samples), [0.0] * len(samples)


def _teacher_receipt(path, record):
    try:
        append_record(path, record)
    except Exception:
        try:
            logger.exception("Teacher stage evidence unverified; preserve the actual request/validation outcome")
        except Exception:
            pass


@contextmanager
def _teacher_stage(args, sample, stage, *, deadline_at):
    started_at, started_clock = time.time(), time.monotonic()
    acquisition = sample.metadata.get("swe_acquisition", {})
    identity = {
        "cell": args.swe_cell, "attempt": args.swe_attempt, "source_uid": sample.metadata["source"]["uid"],
        "sample_index": sample.index, "bank": acquisition.get("bank"), "slot": acquisition.get("slot"),
        "stage": stage, "endpoint": args.rm_url, "teacher_identity": args.swe_teacher_identity,
        "input_tokens": len(sample.tokens), "response_tokens": sample.response_length,
        "started_at": started_at, "deadline_at": deadline_at,
        "acquisition_deadline_at": acquisition.get("deadline_at"),
        "request_timeout_secs": args.sglang_router_request_timeout_secs,
    }
    path = Path(args.swe_evidence_dir) / "teacher_stages.jsonl"
    _teacher_receipt(path, {**identity, "event": "start", "status": "started"})
    status, error = "success", None
    try:
        yield
    except BaseException as exception:
        status = "cancelled" if isinstance(exception, asyncio.CancelledError) else "error"
        error = f"{type(exception).__name__}: {exception}"
        raise
    finally:
        _teacher_receipt(path, {**identity, "event": "end", "status": status, "error": error,
                               "ended_at": time.time(), "elapsed_seconds": time.monotonic() - started_clock})


async def score_teacher(args, sample, **kwargs):
    from miles.rollout import on_policy_distillation as opd

    acquisition_deadline = sample.metadata.get("swe_acquisition", {}).get("deadline_at")
    timeout = args.sglang_router_request_timeout_secs
    deadlines = [value for value in (acquisition_deadline, time.time() + timeout if timeout is not None else None) if value is not None]
    request_deadline = min(deadlines) if deadlines else None
    with _teacher_stage(args, sample, "teacher_request", deadline_at=request_deadline):
        response = await opd._post_json(args.rm_url, opd._score_payload(sample.tokens), timeout_secs=timeout)
    with _teacher_stage(args, sample, "teacher_validation", deadline_at=acquisition_deadline):
        scores = opd._trim_input_field(response["meta_info"], "input_token_logprobs", sample.response_length)
        if [item[1] for item in scores] != sample.tokens[-sample.response_length:]:
            raise ValueError("Teacher scores do not match canonical response token IDs")
        if not all(math.isfinite(float(item[0])) for item in scores):
            raise ValueError("Teacher canonical response scores contain nonfinite values")
    sample.metadata["teacher_scoring"] = {"endpoint": args.rm_url, "identity": args.swe_teacher_identity,
                                          "scored_tokens": len(scores), "token_ids_match": True}
    return {"reward": 0.0, "teacher_response": response}


score_teacher.config_class = SweReplayConfig


class SweReplay(BaseRolloutFn):
    config_class = SweReplayConfig

    def __init__(self, input):
        super().__init__(input)
        self.args = input.args
        self.source = input.data_source
        self.directory = Path(self.args.swe_evidence_dir)
        self.schedule = ReplaySchedule(self.args.swe_protocol, bank_uses=self.args.swe_bank_uses,
                                       updates=self.args.swe_successful_updates)
        self.bank = ()
        self.bank_id = None
        self.bank_tokens = 0
        self.pending_rollout = None
        self.native_state = None

    def on_train_result(self, rollout_id: int, record: dict):
        if self.pending_rollout != rollout_id or record["attempted_rollout_id"] != rollout_id:
            raise ValueError("Unexpected native optimizer acknowledgement")
        if record["cell"] != self.args.swe_cell or record["attempt"] != self.args.swe_attempt:
            raise ValueError("Optimizer acknowledgement belongs to another attempt")
        if record["successful_updates"] != self.schedule.successful + int(record["update_successful"]):
            raise ValueError("Native and replay successful-update counters differ")
        self.schedule.commit(attempted_rollout_id=self.pending_rollout, successful=record["update_successful"])
        self.pending_rollout = None
        if self.schedule.successful >= self.schedule.limit or self.schedule.position.bank != self.bank_id:
            self.bank = ()
            self.bank_id = None
            self.bank_tokens = 0

    async def _generate(self, sample):
        from miles.rollout.inference_rollout.inference_rollout_common import GenerateState, generate_and_rm

        if self.native_state is None:
            self.native_state = GenerateState(self.args)
        params = {**self.native_state.sampling_params, "sampling_seed": self.args.rollout_seed}
        sample.metadata["swe_sampling_seed"] = params["sampling_seed"]
        generated = await generate_and_rm(self.native_state, sample, params, evaluation=False)
        if not isinstance(generated, Sample):
            raise TypeError("A SWE acquisition slot must return exactly one native Sample")
        post_process_rewards(self.args, [generated])
        return generated

    async def __call__(self, input):
        if not isinstance(input, RolloutFnTrainInput):
            raise ValueError("SWE replay is training-only; configure a separate native evaluation function")
        if self.pending_rollout is not None:
            raise RuntimeError("The previous native optimizer attempt has not been acknowledged")
        if self.schedule.successful >= self.schedule.limit:
            raise StopAsyncIteration("SWE successful-update budget complete")
        position = self.schedule.position
        if self.bank_id != position.bank:
            started_at, started_clock = time.time(), time.monotonic()
            candidates = self.source.get_samples(self.args.swe_bank_slots)
            if len(candidates) != self.args.swe_bank_slots:
                raise ValueError("The native data source did not supply the fixed candidate-slot count")
            for group in candidates:
                group[0].metadata["swe_acquisition"] = {"bank": position.bank}
            stamp_kv_cache_namespace(candidates, namespace=compute_kv_cache_namespace(self.args, input))
            self.bank = await acquire_bank(
                candidates, self._generate, teacher_identity=self.args.swe_teacher_identity,
                seconds=max(0.0, self.args.swe_acquisition_seconds - (time.monotonic() - started_clock)),
                started_at=started_at,
                minimum=math.ceil(self.args.swe_bank_slots * self.args.swe_bank_min_fraction),
                persist=lambda record: append_record(self.directory / f"bank_{position.bank}.jsonl", record),
            )
            self.bank_id = position.bank
            self.bank_tokens = sum(sum(trajectory.original_mask) for trajectory in self.bank)
        samples = [[t.materialize(teacher_identity=self.args.swe_teacher_identity, position=position,
                                  rollout_id=input.rollout_id, cell=self.args.swe_cell, attempt=self.args.swe_attempt)]
                   for t in self.bank]
        for group in samples:
            group[0].train_metadata["current_weight_version"] = input.weight_version
            group[0].train_metadata["swe_actual_bank_turns"] = len(self.bank)
            group[0].train_metadata["swe_original_bank_tokens"] = self.bank_tokens
        self.pending_rollout = input.rollout_id
        return RolloutFnTrainOutput(samples=samples)

    def load(self, directory):
        raise RuntimeError("HF-only SWE attempts cannot restore optimizer/RNG/replay state")


class SuccessfulUpdateDriver:
    """The native callback result is authoritative; no filesystem/log polling."""

    def __init__(self, budget: int):
        self.budget = budget
        self.successful = 0
        self.last_result = None

    def rollout_ids(self, start: int):
        if start != 0:
            raise ValueError("HF-only SWE attempts must start from the original model at rollout 0")
        attempted = start
        while self.successful < self.budget:
            yield attempted
            attempted += 1

    def accept(self, outputs):
        if not outputs or any(output.optimizer_step is None for output in outputs):
            raise ValueError("Native optimizer result missing; it cannot be interpreted as a successful update")
        result = outputs[0].optimizer_step
        if any(output.optimizer_step != result for output in outputs):
            raise ValueError("Native worker optimizer results disagree")
        expected = self.successful + int(result["update_successful"])
        if result["successful_updates"] != expected or expected > self.budget:
            raise ValueError("Native successful-update counter is discontinuous")
        self.successful = result["successful_updates"]
        self.last_result = result
        return result


def training_protocol(args):
    if args.rollout_function_path is None or args.rollout_function_path.path != "tests.manual.agent_opd.swe_replay.SweReplay":
        raise ValueError("SWE replay requires its native canonical-bank rollout function")
    if args.custom_rm_path is None or args.custom_rm_path.path != "tests.manual.agent_opd.swe_replay.score_teacher":
        raise ValueError("SWE replay requires its native canonical-token teacher scoring function")
    if args.use_critic or args.fully_async or args.keep_old_actor or args.reset_optimizer_states:
        raise ValueError("SWE replay requires one synchronous native actor and persistent optimizer/current scores")
    if not args.compute_advantages_and_returns or args.skip_actor_forward_only or args.use_rollout_logprobs:
        raise ValueError("SWE replay requires a fresh independent native actor scoring pass on every visit")
    if args.save is not None:
        raise ValueError("SWE attempts save HF only, not distributed/optimizer checkpoints")
    if not (args.use_dynamic_batch_size and args.use_dynamic_global_batch_size and args.allow_partial_train_step):
        raise ValueError("SWE valid subsets require native dynamic/partial rollout-side scheduling")
    if args.num_rollout != args.swe_successful_updates:
        raise ValueError("num_rollout must name this run's successful-update budget (formal 200 or explicit smoke)")
    if args.swe_run_kind == "formal":
        for name in ("swe_successful_updates", "swe_bank_slots", "swe_bank_uses", "swe_acquisition_seconds",
                     "swe_bank_min_fraction", "swe_context_tokens"):
            if getattr(args, name) != SweReplayConfig.model_fields[name].default:
                raise ValueError("Formal SWE runs require the frozen budget; shorter runs must be explicitly smoke")
    if not args.use_tis or args.custom_tis_function_path.path != "tests.manual.agent_opd.swe_tis.apply_tis":
        raise ValueError("SWE replay requires the native custom binary two-level TIS function")
    from tests.manual.agent_opd.swe_tis import SweTISConfig

    if args.custom_tis_function_path.config != SweTISConfig():
        raise ValueError("SWE replay requires the frozen D4 thresholds")
    if args.custom_reward_post_process_path is None or args.custom_reward_post_process_path.path != "tests.manual.agent_opd.swe_replay.post_process_rewards":
        raise ValueError("SWE replay requires its canonical-target-preserving native reward postprocessor")
    if args.use_output_store:
        raise ValueError("Dense SWE replay requires inline canonical token payloads, not transient output-store objects")
    contract = {
        "loss_type": "policy_loss", "use_opd": True, "opd_type": "sglang", "opd_log_prob_top_k": 0,
        "opd_kl_coef": 1.0, "advantage_estimator": "grpo", "normalize_advantages": False,
        "eps_clip": 0.2, "eps_clip_high": 0.28, "eps_clip_c": None, "kl_coef": 0.0,
        "use_kl_loss": False, "entropy_coef": 0.0, "use_opsm": False, "true_on_policy_mode": False,
        "calculate_per_token_loss": True, "optimizer": "adam", "adam_beta1": 0.9,
        "adam_beta2": 0.98, "adam_eps": 1e-8, "weight_decay": 0.1, "lr": 2e-6,
        "lr_decay_style": "constant", "lr_warmup_iters": 0,
        "n_samples_per_prompt": 1, "rollout_temperature": 1.0, "rollout_top_p": 1.0, "rollout_top_k": -1,
    }
    for name, expected in contract.items():
        if getattr(args, name) != expected:
            raise ValueError(f"S4 requires {name}={expected!r}")
    return SuccessfulUpdateDriver(args.swe_successful_updates)
