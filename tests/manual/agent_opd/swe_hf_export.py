"""Package native SWE HF saves and durably enqueue formal evaluation points.

Use ``--custom-megatron-post-save-hook-path
tests.manual.agent_opd.swe_hf_export.post_save`` with native ``--save-hf`` and no
``--save``. Formal runs also pass ``--swe-evaluation-configuration`` pointing to
the existing EvaluationStore configuration, including ``task_ids`` and
``evaluation_contract``. Smoke runs package HF and record native identity without
creating a formal 400-attempt point. Native export/conversion I/O still propagates;
identity, metadata, and queue failures retain HF and remain training soft gates.
"""

import logging
import time
from collections.abc import Callable
from pathlib import Path

from tests.manual.agent_opd import qwen_export
from tests.manual.agent_opd.swe_evaluation import HF_UPDATES, read_json, store_from_config, write_json

from miles.backends.training_utils.types import TrainStepOutcome, TrainStepOutput
from miles.utils.args.custom_view import ImmutableNamespace
from miles.utils.args.schema import A, Arg, BaseConfig

logger = logging.getLogger(__name__)


class SweHFExportConfig(BaseConfig):
    swe_evaluation_configuration: A[
        str | None, Arg(help="EvaluationStore JSON configuration; required for formal SWE checkpoint enqueue.")
    ] = None


def _native_publication(train_result, native_rollout_id, checkpoint_index, get_weight_version):
    if not isinstance(train_result, TrainStepOutput) or train_result.outcome != TrainStepOutcome.NORMAL:
        raise ValueError("HF publication requires the actual completed native TrainStepOutput")
    record = train_result.optimizer_step
    if not isinstance(record, dict) or record.get("update_successful") is not True:
        raise ValueError("A skipped native optimizer attempt cannot publish an HF evaluation point")
    successful = record["successful_updates"]
    attempted, skipped = record["native_attempted_count"], record["native_skipped_count"]
    if (
        type(successful) is not int
        or successful <= 0
        or type(attempted) is not int
        or type(skipped) is not int
        or skipped < 0
        or attempted != successful + skipped
    ):
        raise ValueError("Native successful/attempted/skipped counters disagree")
    if (
        type(native_rollout_id) is not int
        or native_rollout_id < 0
        or record["attempted_rollout_id"] != native_rollout_id
    ):
        raise ValueError("The latest native train result does not belong to this rollout")
    if type(checkpoint_index) is not int or checkpoint_index != successful - 1:
        raise ValueError("Native HF directory index disagrees with the successful optimizer count")
    weight_version = get_weight_version()
    if type(weight_version) is not int or weight_version < 0:
        raise ValueError("The actual actor model weight version is unavailable")
    if record["run_kind"] not in ("formal", "smoke"):
        raise ValueError("HF publication requires an explicit formal or smoke run identity")
    return {
        "successful_update": successful,
        "rollout_id": native_rollout_id,
        "checkpoint_index": checkpoint_index,
        "weight_version": weight_version,
        "native_counters": {
            "successful_updates": successful,
            "native_attempted_count": attempted,
            "native_skipped_count": skipped,
        },
    }


def _diagnostic(checkpoint, publication):
    # Keep this outside the immutable HF inventory, including after partial enqueue.
    path = checkpoint.parent.parent / "hf_publications" / f"{checkpoint.name}.json"
    try:
        write_json(path, publication)
    except Exception:
        logger.exception("SWE HF publication diagnostic could not be persisted at %s; training continues", path)


def post_save(
    args: ImmutableNamespace,
    rollout_id: int,
    checkpoint_dir: str | None,
    hf_checkpoint_dir: str | None,
    *,
    train_result: TrainStepOutput | None = None,
    native_rollout_id: int | None = None,
    get_weight_version: Callable[[], int] | None = None,
) -> None:
    """Rank-zero bridge; ``rollout_id`` is the native successful-index save argument."""
    if checkpoint_dir is not None:
        raise ValueError("SWE publication supports HF only, not native/optimizer checkpoints")
    # Preserve the existing packaging semantics, including native conversion I/O errors.
    qwen_export.post_save(args, native_rollout_id, checkpoint_dir, hf_checkpoint_dir)
    checkpoint = Path(hf_checkpoint_dir).resolve()
    publication = {"checkpoint_dir": str(checkpoint), "observed_at": time.time(), "status": "UNVERIFIED"}
    stage = "packaging"
    try:
        package = read_json(checkpoint / "qwen_text_export.json")
        if package.get("status") != "packaged" or not (checkpoint / ".complete").is_file():
            raise ValueError("Native HF export and Qwen text packaging must both be complete")
        stage = "native_identity"
        native = _native_publication(train_result, native_rollout_id, rollout_id, get_weight_version)
        record = train_result.optimizer_step
        publication.update(
            native_update=native, run_kind=record["run_kind"], cell=record["cell"], attempt=record["attempt"]
        )
        stage = "metadata"
        write_json(
            checkpoint / "qwen_text_export.json",
            {**package, **native, "source": str(Path(args.hf_checkpoint).resolve()), "run_kind": record["run_kind"]},
        )
        stage = "completion_marker"
        # Republish the native marker after packaging and identity metadata, not before.
        write_json(checkpoint / ".complete", {})
        if record["run_kind"] == "smoke":
            publication.update(status="SMOKE_PACKAGED", formal_evaluation=False)
        else:
            stage = "enqueue"
            if native["successful_update"] not in HF_UPDATES:
                raise ValueError("Formal SWE HF publication is limited to the frozen successful-update points")
            if args.swe_evaluation_configuration is None:
                raise ValueError("Formal SWE HF publication requires --swe-evaluation-configuration")
            config = read_json(args.swe_evaluation_configuration)
            point_id = f"{record['cell'].replace('/', '-')}.{record['attempt']}.HF{native['successful_update']}"
            store_from_config(config).enqueue_checkpoint(
                point_id=point_id,
                checkpoint_dir=checkpoint,
                native_update=native,
                source=args.hf_checkpoint,
                task_ids=config["task_ids"],
                configuration=config["evaluation_contract"],
            )
            publication.update(status="QUEUED", point_id=point_id, formal_evaluation=True)
    except Exception as error:
        publication.update(stage=stage, error={"type": type(error).__name__, "message": str(error)})
        logger.exception("SWE HF publication is unverified; preserve HF and repair %s; training continues", stage)
    _diagnostic(checkpoint, publication)


post_save.config_class = SweHFExportConfig
post_save.with_train_state = True
