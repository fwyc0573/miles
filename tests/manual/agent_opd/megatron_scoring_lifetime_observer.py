"""Soft-only CUDA observations for the native PP1 scoring lifetime contrast.

The before-log-prob hook installs ordinary module hooks. They retain only a
weak reference and scalar storage metadata, do not synchronize, and never
change outputs, gradients, collectives, or the scoring callback.
"""

import hashlib
import json
import time
import weakref
from dataclasses import dataclass, field
from pathlib import Path

import torch
import torch.distributed as dist

from miles.utils.args.schema import A, Arg, BaseConfig


class ScoringLifetimeConfig(BaseConfig):
    scoring_lifetime_dir: A[str, Arg()]
    scoring_lifetime_source_sha256: A[str, Arg()]


@dataclass
class _ScoringObservation:
    args: object
    store_prefix: str
    pass_index: int
    microbatch_index: int = -1
    previous: object = None
    previous_storage: dict = field(default_factory=dict)
    handles: list = field(default_factory=list)

    def write(self, event, **values):
        rank = dist.get_rank() if dist.is_initialized() else 0
        directory = Path(self.args.scoring_lifetime_dir)
        directory.mkdir(parents=True, exist_ok=True)
        record = {
            "event": event,
            "rank": rank,
            "store_prefix": self.store_prefix,
            "scoring_pass_index": self.pass_index,
            "forward_microbatch_index": self.microbatch_index,
            "timestamp": time.time(),
            **values,
        }
        with (directory / f"rank_{rank}.jsonl").open("a") as stream:
            stream.write(json.dumps(record, allow_nan=False) + "\n")

    def soft(self, stage, function):
        try:
            function()
        except Exception as error:
            try:
                self.write("observer_unverified", stage=stage, error_type=type(error).__name__, error=str(error))
            except Exception:
                try:
                    print("MEGATRON_SCORING_LIFETIME_UNVERIFIED", stage, type(error).__name__, str(error), flush=True)
                except Exception:
                    pass

    def snapshot(self, event, **values):
        stats = torch.cuda.memory_stats()
        previous = self.previous() if self.previous is not None else None
        self.write(
            event,
            prior_full_output_alive=previous is not None,
            prior_full_output_storage=self.previous_storage,
            allocated_bytes=stats["allocated_bytes.all.current"],
            active_bytes=stats["active_bytes.all.current"],
            reserved_bytes=stats["reserved_bytes.all.current"],
            inactive_split_bytes=stats["inactive_split_bytes.all.current"],
            **values,
        )

    def forward_enter(self, module, inputs):
        if torch.is_grad_enabled():
            return

        def observe():
            self.microbatch_index += 1
            self.snapshot("forward_enter")

        self.soft("forward_enter", observe)

    def projection_enter(self, module, inputs):
        if not torch.is_grad_enabled():
            self.soft("projection_enter", lambda: self.snapshot("projection_enter", input_shape=list(inputs[0].shape)))

    def forward_exit(self, module, inputs, output):
        if torch.is_grad_enabled():
            return

        def observe():
            storage = output.untyped_storage()
            description = {
                "shape": list(output.shape),
                "dtype": str(output.dtype),
                "storage_bytes": storage.nbytes(),
                "storage_data_ptr": storage.data_ptr(),
            }
            self.snapshot("forward_exit", full_output_storage=description)
            self.previous = weakref.ref(output)
            self.previous_storage = description

        self.soft("forward_exit", observe)


def before_log_prob(args, model, store_prefix):
    """Observe this scoring pass; every failure remains a non-blocking receipt."""
    module = model[0]
    previous = getattr(module, "_scoring_lifetime_observation", None)
    state = _ScoringObservation(args, store_prefix, 0 if previous is None else previous.pass_index + 1)

    def install():
        # These optional Megatron imports are reached only inside the native CUDA actor.
        from megatron.core.pipeline_parallel import schedules
        from megatron.core.utils import get_attr_wrapped_model

        if previous is not None:
            for handle in previous.handles:
                handle.remove()
        source = Path(schedules.__file__)
        observed = hashlib.sha256(source.read_bytes()).hexdigest()
        state.write(
            "source_identity",
            source_path=str(source),
            source_sha256=observed,
            expected_source_sha256=args.scoring_lifetime_source_sha256,
            source_verified=observed == args.scoring_lifetime_source_sha256,
        )
        if observed != args.scoring_lifetime_source_sha256:
            state.write("observer_unverified", stage="source_identity", error="Actor schedule differs from preflight")
        projection = get_attr_wrapped_model(module, "output_layer")
        try:
            state.handles.append(module.register_forward_pre_hook(state.forward_enter))
            state.handles.append(projection.register_forward_pre_hook(state.projection_enter))
            state.handles.append(module.register_forward_hook(state.forward_exit))
        except Exception:
            for handle in state.handles:
                handle.remove()
            raise
        module._scoring_lifetime_observation = state

    state.soft("install", install)


before_log_prob.config_class = ScoringLifetimeConfig
