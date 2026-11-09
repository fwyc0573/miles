"""Miles external-evaluator seam that durably enqueues and returns immediately.

Set MILES_SWE_EVALUATION_CONFIGURATION to the parent-authored task configuration.
``publications`` maps native rollout IDs to {point_id, native_update, source}.
Prefer calling EvaluationStore.enqueue_checkpoint in the parent's existing
post-packaging hook: it publishes immediately even if the trainer later exits.
Configure --save-hf, no --eval-hf-dir; this backend must not use snapshot GC.
"""

import logging
import os

from tests.manual.agent_opd.swe_evaluation import read_json, store_from_config

from miles.rollout.base_types import RolloutFnEvalOutput
from miles.rollout.checkpoint_eval import CheckpointEvalFn

logger = logging.getLogger(__name__)


class SweEvaluationFn(CheckpointEvalFn):
    async def evaluate_checkpoint(self, checkpoint_dir, input):
        try:
            config = read_json(os.environ["MILES_SWE_EVALUATION_CONFIGURATION"])
            publication = config["publications"][str(input.rollout_id)]
            store = store_from_config(config)
            store.enqueue_checkpoint(
                point_id=publication["point_id"],
                checkpoint_dir=checkpoint_dir,
                native_update=publication["native_update"],
                source=publication["source"],
                task_ids=config["task_ids"],
                configuration=config["evaluation_contract"],
            )
        except Exception:
            # Auxiliary enqueue failure is observable, never a training hard gate.
            logger.exception("SWE enqueue is unverified; preserve HF and repair the durable queue; training continues")
            return RolloutFnEvalOutput(data={}, metrics={"swe_enqueue_unverified": 1})
        return RolloutFnEvalOutput(data={}, metrics={"swe_enqueued": 1})
