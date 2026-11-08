"""Replay one captured 256-turn bank for a two-update, native capacity smoke.

Only the acquisition generator is replaced. SweReplay still seals the original
payload, privately materializes every visit, and commits native optimizer ACKs.
The normal colocated inference-engine startup/offload path remains enabled.
"""

import json
from pathlib import Path

from miles.utils.args.custom_function import CustomFunctionConfig
from miles.utils.args.schema import A, Arg, BaseConfig
from miles.utils.types import Sample
from tests.manual.agent_opd import swe_replay, swe_training


class SavedBankConfig(BaseConfig):
    # Replay flags belong to the existing teacher/optimizer hooks. Declaring
    # only this new flag preserves the parser's all-or-none sharing contract.
    swe_saved_bank_path: A[str, Arg()]


def read_saved_bank(path: Path, *, teacher_identity: str, slots: int):
    """Accept the existing acquisition JSONL, not a debug train-data dump."""
    start, sealed, completed = None, None, {}
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            event = record["event"]
            if sealed is not None:
                raise ValueError("Saved capacity input must contain exactly one sealed bank")
            if event == "acquisition_start":
                if start is not None:
                    raise ValueError("Saved capacity input contains multiple acquisitions")
                start = record
            elif event == "slot_finished":
                slot = record["slot"]
                if start is None or slot in completed or record["status"] != "completed":
                    raise ValueError("Saved capacity input needs one successful original receipt per slot")
                sample = Sample.from_dict(record["sample"])
                if record["source_uid"] != sample.metadata["source"]["uid"]:
                    raise ValueError("Saved slot receipt and original sample source identity differ")
                if sample.metadata["teacher_scoring"]["identity"] != teacher_identity:
                    raise ValueError("Saved capacity targets belong to another teacher identity")
                completed[slot] = swe_replay.CanonicalTrajectory.seal(slot, sample, teacher_identity)
            elif event == "acquisition_sealed":
                sealed = record
            else:
                raise ValueError(f"Saved capacity input contains an unsuccessful acquisition event: {event}")
    membership = list(range(slots))
    if (start is None or sealed is None or sealed["membership"] != membership
            or sealed["actual_turns"] != slots or sealed["missing_slots"] or sealed["pending_slots"]
            or sorted(completed) != membership or [item["slot"] for item in start["slots"]] != membership):
        raise ValueError("Saved capacity input must be a complete sealed bank with its original slot order")
    for receipt in start["slots"]:
        sample = json.loads(completed[receipt["slot"]].sample_json)
        if (receipt["source_uid"] != sample["metadata"]["source"]["uid"]
                or receipt["sample_index"] != sample["index"]):
            raise ValueError("Saved acquisition and sample source/index identity differ")
    return tuple(completed[slot] for slot in membership)


def _validate_smoke(args):
    if args.swe_run_kind != "smoke":
        raise ValueError("Saved-bank capacity input is smoke-only, never a formal training input")
    if (args.swe_protocol, args.swe_bank_slots, args.swe_bank_uses, args.swe_successful_updates) != ("r256", 256, 2, 2):
        raise ValueError("Saved-bank capacity smoke requires one 256-turn r256 bank and two successful updates")


class CapacityReplay(swe_replay.SweReplay):
    config_class = SavedBankConfig

    def __init__(self, input):
        _validate_smoke(input.args)
        path = Path(input.args.swe_saved_bank_path)
        if path.resolve() == (Path(input.args.swe_evidence_dir) / "bank_0.jsonl").resolve():
            raise ValueError("Capacity smoke evidence must not append to the original saved bank")
        super().__init__(input)
        self._saved_slots = {trajectory.slot: trajectory for trajectory in read_saved_bank(
            path, teacher_identity=self.args.swe_teacher_identity, slots=self.args.swe_bank_slots,
        )}

    async def _generate(self, candidate):
        slot = candidate.metadata["swe_acquisition"]["slot"]
        trajectory = self._saved_slots[slot]
        sample = Sample.from_dict(json.loads(trajectory.sample_json))
        if (candidate.index != sample.index or candidate.metadata["source"]["uid"] != sample.metadata["source"]["uid"]
                or candidate.prompt != sample.prompt):
            raise ValueError("Capacity input must revisit the original ordered source candidates")
        # Keep original status, acquisition timestamps, sampling seed and all
        # generation version spans; this is not a new generation/teacher call.
        sample.train_metadata = {**(sample.train_metadata or {}), "swe_saved_bank_path": self.args.swe_saved_bank_path}
        del self._saved_slots[slot]
        return sample

    async def __call__(self, input):
        output = await super().__call__(input)
        if self._saved_slots or len(output.samples) != self.args.swe_bank_slots:
            raise ValueError("Capacity smoke must consume the complete original saved bank without dropping slots")
        return output


def optimizer_step(*args, **kwargs):
    """Keep native counters, actual mask reductions and the D7 stop unchanged."""
    return swe_training.optimizer_step(*args, **kwargs)


def training_protocol(args):
    _validate_smoke(args)
    rollout = args.rollout_function_path
    if rollout is None or rollout.path != "tests.manual.agent_opd.probe_swe_capacity.CapacityReplay":
        raise ValueError("Capacity smoke requires the saved-bank native acquisition function")
    # Only the acquisition function differs. Validate every existing training
    # constraint through its owner rather than duplicating the S4 contract.
    canonical = CustomFunctionConfig(path="tests.manual.agent_opd.swe_replay.SweReplay")
    return swe_replay.training_protocol(args.model_copy(update={"rollout_function_path": canonical}))


optimizer_step.config_class = swe_replay.SweReplayConfig
optimizer_step.training_protocol = training_protocol
