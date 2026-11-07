import asyncio
import logging
import os
from urllib.parse import quote

from sglang.srt.constants import GPU_MEMORY_TYPE_CUDA_GRAPH, GPU_MEMORY_TYPE_KV_CACHE, GPU_MEMORY_TYPE_WEIGHTS

from miles.backends.training_utils.metrics.train_dump import save_debug_train_data_for_rank
from miles.ray.placement_group import (
    create_rollout_components,
    create_trainer_handles,
    create_training_models,
    maybe_start_api_server,
    update_weights,
)
from miles.ray.rollout.eval_dispatch import EvalDispatcher
from miles.ray.specs.train import compute_trainer_configs
from miles.utils import object_store
from miles.utils.async_utils import Disposer, with_disposer
from miles.utils.data import RolloutDataPack, remove_rollout_data_refs, remove_train_output_refs
from miles.utils.ft_utils.mini_ft_controller import maybe_start_mini_ft_controller
from miles.utils.lora.utils import lora_rollout_enabled
from miles.utils.misc import should_run_periodic_action
from miles.utils.orchestration_utils import (
    OrchestratorStartupInfo,
    init_orchestration_script,
    parse_orchestrator_startup_info,
)

logger = logging.getLogger(__name__)


def _rollout_offload_tags(args) -> list[str]:
    tags = [GPU_MEMORY_TYPE_CUDA_GRAPH]
    if "kv_cache" in args.offload_rollout_level:
        tags.append(GPU_MEMORY_TYPE_KV_CACHE)
    if "weight" in args.offload_rollout_level:
        tags.append(GPU_MEMORY_TYPE_WEIGHTS)
    return tags


async def _score_eval_train_data(
    args, actor_model, inference_controller, rollout_id: int, packs: dict[str, RolloutDataPack], *, rollout_executor
) -> None:
    # Cancelling a driver wait does not stop its remote controller or workers.
    # Keep the scoring transaction, including residency restoration, alive.
    pending = asyncio.create_task(
        _score_eval_datasets(args, actor_model, inference_controller, rollout_id, packs, rollout_executor=rollout_executor)
    )
    cancellation: asyncio.CancelledError | None = None
    while not pending.done():
        try:
            await asyncio.shield(pending)
        except asyncio.CancelledError as error:
            if cancellation is None:
                cancellation = error
    pending.result()
    if cancellation is not None:
        raise cancellation


async def _score_eval_datasets(
    args, actor_model, inference_controller, rollout_id: int, packs: dict[str, RolloutDataPack], *, rollout_executor
) -> None:
    refs = [ref for pack in packs.values() for ref in pack.data_refs]
    offload_tags = _rollout_offload_tags(args) if args.offload_rollout else []
    offload_started = False
    observer_errors: list[tuple[str | None, Exception]] = []
    try:
        if not packs:
            logger.warning("Evaluation train logprobs unverified: no input packs at rollout %s", rollout_id)
            return
        if offload_tags:
            offload_started = True
            await inference_controller.offload(tags=offload_tags)
        for dataset, pack in packs.items():
            try:
                results = await actor_model.score_log_probs(rollout_id, pack)
                refs.extend(results)
                for ref in results:
                    with object_store.get_instance().get(ref) as payload:
                        metadata = payload["metadata"]
                        save_debug_train_data_for_rank(
                            args,
                            rollout_id=f"eval_{quote(dataset, safe='')}_{rollout_id}",
                            rollout_data=payload,
                            rank=metadata["rank"],
                            cp_rank=metadata["cp_rank"],
                            cp_size=metadata["cp_size"],
                        )
                if not results:
                    raise ValueError("The actor returned no scoring payloads")
            except Exception as error:
                observer_errors.append((dataset, error))
    except Exception as error:
        observer_errors.append((None, error))
    finally:
        try:
            for ref in refs:
                try:
                    object_store.get_instance().remove(ref)
                except Exception:
                    logger.exception("Evaluation train logprobs unverified: reference cleanup failed")
        finally:
            if offload_started:
                if GPU_MEMORY_TYPE_WEIGHTS in offload_tags:
                    # Unbacked weight storage must be republished before KV/graph resume.
                    await inference_controller.onload(tags=[GPU_MEMORY_TYPE_WEIGHTS])
                    await update_weights(args, actor_model, rollout_executor, inference_controller)
                await inference_controller.onload(tags=[tag for tag in offload_tags if tag != GPU_MEMORY_TYPE_WEIGHTS])
                await inference_controller.prepare_eval()
    for dataset, error in observer_errors:
        context = (
            f"preparation failed at rollout {rollout_id}"
            if dataset is None
            else f"scoring/dump failed for dataset {dataset} at rollout {rollout_id}"
        )
        logger.error(
            "Evaluation train logprobs unverified: %s",
            context,
            exc_info=(type(error), error, error.__traceback__),
        )


async def train(startup_info: OrchestratorStartupInfo, *, disposer: Disposer):
    args = startup_info.args
    assert not args.fully_async, "--fully-async requires the async driver: run train_async.py"
    capability = init_orchestration_script(startup_info, disposer=disposer)
    trainer_handles = create_trainer_handles(
        args, trainer_configs=compute_trainer_configs(args), capability=capability
    )

    if args.colocate_memory_peak_device == "gpu":
        assert (
            args.offload_train and args.offload_rollout
        ), "--colocate-memory-peak-device gpu requires --offload-train and --offload-rollout"
        assert not args.use_critic, "--colocate-memory-peak-device gpu is not wired for the critic path"

    # create the rollout manager, with sglang engines inside.
    # need to initialize rollout manager first to calculate num_rollout
    inference_controller, rollout_executor, num_rollout_per_epoch = await create_rollout_components(
        args, capability=capability, trainer_handles=trainer_handles
    )
    disposer.add(inference_controller, rollout_executor)

    # create the actor and critic models
    actor_model, critic_model = await create_training_models(args, rollout_executor, handles=trainer_handles)
    disposer.add(critic_model, actor_model)

    disposer.add(
        maybe_start_api_server(
            args,
            trainer_models={"actor": actor_model},
            inference_controller=inference_controller,
            capability=capability,
        )
    )
    disposer.add(rollout_executor)
    maybe_start_mini_ft_controller(args)

    # always update weight first so that sglang has the loaded weights from training.
    await update_weights(args, actor_model, rollout_executor, inference_controller)

    if args.check_weight_update_equal:
        await inference_controller.check_weights(
            action="compare",
            allow_quant_error=args.check_weight_update_allow_quant_error,
            selector=args.check_weight_update_selector,
            skip_list=args.check_weight_update_skip_list,
        )

    if args.offload_rollout:
        await inference_controller.onload_kv()

    async def score_eval_train_data(rollout_id, packs):
        await _score_eval_train_data(
            args, actor_model, inference_controller, rollout_id, packs, rollout_executor=rollout_executor
        )

    eval_dispatcher = EvalDispatcher(
        args,
        actor_model,
        rollout_executor,
        **({"eval_train_data_callback": score_eval_train_data} if args.eval_train_log_probs else {}),
    )
    disposer.add(eval_dispatcher.drain)

    # special case for eval-only
    if args.num_rollout == 0 and args.eval_interval is not None:
        await inference_controller.prepare_eval()
        await eval_dispatcher.dispatch(0, hf_dir=args.hf_checkpoint)

    async def offload_train():
        if args.use_critic:
            return
        if args.offload_train:
            await actor_model.offload()
        else:
            await actor_model.clear_memory()

    async def save(rollout_id, force_sync=False):
        force_sync = force_sync or rollout_id == args.num_rollout - 1

        async def save_training_model(model):
            if args.use_critic and args.offload_train:
                await model.onload()
            await model.save_model(rollout_id, force_sync=force_sync)
            if args.use_critic and args.offload_train:
                await model.offload()

        # Resumable checkpoints include data progress; standalone HF exports do not.
        if args.save is not None:
            await rollout_executor.save(rollout_id)
        if (not args.use_critic) or (rollout_id >= args.num_critic_only_steps):
            await save_training_model(actor_model)
        if args.use_critic:
            await save_training_model(critic_model)

    if args.num_rollout > args.start_rollout_id and args.eval_interval is not None and not args.skip_eval_before_train:
        await inference_controller.prepare_eval()
        if args.start_rollout_id == 0:
            await eval_dispatcher.dispatch(0, hf_dir=args.hf_checkpoint)
        else:
            await eval_dispatcher.dispatch(args.start_rollout_id - 1)

    # train loop.
    # note that for async training, one can change the position of the sync operation(ray.get).
    for rollout_id in range(args.start_rollout_id, args.num_rollout):
        await inference_controller.prepare_rollout(rollout_id)
        rollout_data_pack = await rollout_executor.get(rollout_id)

        if args.offload_rollout:
            if args.colocate_memory_peak_device == "gpu":
                await inference_controller.offload_kv()
                await actor_model.onload()
                await inference_controller.offload_weights()
            else:
                await inference_controller.offload(tags=_rollout_offload_tags(args))

        if args.use_critic:
            values = await critic_model.train(rollout_id, rollout_data_pack)
            if args.offload_train:
                await critic_model.offload()
            if rollout_id >= args.num_critic_only_steps:
                await actor_model.train(rollout_id, rollout_data_pack, external_data=values)
                if args.offload_train:
                    await actor_model.offload()
            remove_train_output_refs(values)
        else:
            await actor_model.train(rollout_id, rollout_data_pack)
        remove_rollout_data_refs(args, rollout_data_pack)
        await rollout_executor.release(rollout_id)

        external_save = args.save_trigger_sentinel is not None and os.path.exists(args.save_trigger_sentinel)
        if external_save or should_run_periodic_action(
            rollout_id, args.save_interval, num_rollout_per_epoch, args.num_rollout
        ):
            await save(rollout_id, force_sync=external_save)
            if external_save:
                os.remove(args.save_trigger_sentinel)

        # One predicate for both blocks: the handoff below exists to feed this eval on the last rollout.
        eval_due = should_run_periodic_action(rollout_id, args.eval_interval, num_rollout_per_epoch, args.num_rollout)
        if rollout_id + 1 < args.num_rollout or eval_due:
            if args.colocate_memory_peak_device == "gpu":
                await actor_model.clear_memory()
                if lora_rollout_enabled(args):
                    await actor_model.offload_grad_buffer()
                await inference_controller.onload_weights()
                await offload_train()
            else:
                await offload_train()
                if args.offload_rollout:
                    await inference_controller.onload_weights()
            await update_weights(args, actor_model, rollout_executor, inference_controller, rollout_id=rollout_id)
            if args.offload_rollout:
                await inference_controller.onload_kv()

        if eval_due:
            await inference_controller.prepare_eval()
            await eval_dispatcher.dispatch(rollout_id, force=rollout_id == args.num_rollout - 1)

        if (
            args.debug_exit_after_rollout is not None
            and (rollout_id - args.start_rollout_id + 1) >= args.debug_exit_after_rollout
        ):
            logger.info(
                "debug_exit_after_rollout=%d reached at rollout_id=%d, exiting",
                args.debug_exit_after_rollout,
                rollout_id,
            )
            break


if __name__ == "__main__":
    asyncio.run(with_disposer(train, parse_orchestrator_startup_info()))
