from functools import partial
from types import SimpleNamespace
from typing import Any

import pytest
import torch
import train as train_driver
from tests.fast.fixtures.driver_fakes import (
    FakeInferenceController,
    FakeObjectStore,
    FakeRemoteMethod,
    FakeRolloutExecutor,
    FakeTrainingModel,
    FakeWorkerManager,
)

from miles.backends.megatron_utils.megatron_config import MegatronConfig, MegatronTrainerConfig
from miles.backends.training_utils.types import TrainStepOutcome, TrainStepOutput
from miles.ray.train_actor import WeightUpdateOutput
from miles.ray import placement_group, wiring
from miles.utils import object_store
from miles.utils.data import RolloutDataPack
from miles.utils.async_utils import with_disposer
from miles.utils.orchestration_utils import ArgvOrchestratorStartupInfo


def _make_args(**overrides: Any) -> SimpleNamespace:
    args = SimpleNamespace(
        api_server_host="127.0.0.1",
        api_server_port=None,
        check_weight_update_allow_quant_error=False,
        check_weight_update_equal=False,
        check_weight_update_selector=None,
        check_weight_update_skip_list=None,
        colocate_memory_peak_device="cpu",
        debug_exit_after_rollout=None,
        eval_interval=None,
        eval_uses_snapshots=False,
        eval_train_log_probs=False,
        ft_components=[],
        fully_async=False,
        hf_checkpoint="/base/checkpoint",
        num_critic_only_steps=0,
        num_rollout=0,
        offload_rollout=False,
        offload_rollout_level="",
        offload_train=False,
        save=None,
        save_hf=None,
        save_interval=None,
        save_trigger_sentinel=None,
        skip_eval_before_train=False,
        start_rollout_id=0,
        use_critic=False,
    )
    for key, value in overrides.items():
        setattr(args, key, value)
    args.raw_megatron = MegatronConfig(
        trainers=[
            MegatronTrainerConfig(
                trainer_id=role,
                model_id=None,
                role=role,
                actor_index=0 if role == "actor" else None,
                overrides={},
            )
            for role in (["actor", "critic"] if args.use_critic else ["actor"])
        ],
        base_args={},
    )
    return args


def _startup_info(args: SimpleNamespace) -> ArgvOrchestratorStartupInfo:
    return ArgvOrchestratorStartupInfo(args=args, all_args=args)


def _install_driver_fakes(
    monkeypatch: pytest.MonkeyPatch,
    args: SimpleNamespace,
    events: list[str],
    *,
    num_rollout_per_epoch: int = 4,
) -> SimpleNamespace:
    components = SimpleNamespace(
        inference_controller=FakeInferenceController(events),
        rollout_executor=FakeRolloutExecutor(events),
        actor_model=FakeTrainingModel(events, "actor"),
        critic_model=FakeTrainingModel(events, "critic") if args.use_critic else None,
        cell_operations=object(),
    )
    capability = SimpleNamespace(cell_operations=lambda: components.cell_operations)

    handles = {"actor": components.actor_model}
    if args.use_critic:
        handles["critic"] = components.critic_model

    def create_trainer_handles(
        _args: SimpleNamespace, *, trainer_configs: list[MegatronTrainerConfig], capability: Any
    ) -> dict[str, FakeTrainingModel]:
        assert [config.trainer_id for config in trainer_configs] == list(handles)
        return handles

    async def create_rollout_components(
        _args: SimpleNamespace, *, capability: Any, trainer_handles: dict[str, FakeTrainingModel]
    ) -> tuple[Any, Any, int]:
        assert trainer_handles is handles
        return components.inference_controller, components.rollout_executor, num_rollout_per_epoch

    async def create_training_models(
        _args: SimpleNamespace, _executor: Any, *, handles: dict[str, FakeTrainingModel]
    ) -> tuple[Any, Any]:
        assert handles["actor"] is components.actor_model
        if args.use_critic:
            assert handles["critic"] is components.critic_model
        return components.actor_model, components.critic_model

    async def update_weights(
        _args: Any, _model: Any, _executor: Any, _inference_controller: Any, *, rollout_id: int | None = None
    ) -> None:
        events.append(f"update_weights:{rollout_id}")

    monkeypatch.setattr(train_driver, "init_orchestration_script", lambda _startup_info, *, disposer: capability)
    monkeypatch.setattr(train_driver, "create_trainer_handles", create_trainer_handles)
    monkeypatch.setattr(train_driver, "create_rollout_components", create_rollout_components)
    monkeypatch.setattr(train_driver, "create_training_models", create_training_models)
    monkeypatch.setattr(train_driver, "maybe_start_mini_ft_controller", lambda _args: None)
    monkeypatch.setattr(train_driver, "update_weights", update_weights)
    monkeypatch.setattr(train_driver, "remove_rollout_data_refs", lambda *_args, **_kwargs: None)
    return components


class TestEvalOnlyRun:
    async def test_eval_only_prepares_inference_and_runs_exactly_one_eval(self, monkeypatch: pytest.MonkeyPatch):
        """A run with no rollouts but an eval interval evaluates once and generates or trains nothing."""
        events: list[str] = []
        args = _make_args(num_rollout=0, eval_interval=2)
        components = _install_driver_fakes(monkeypatch, args, events)

        await with_disposer(train_driver.train, _startup_info(args))

        assert events.count("prepare_eval") == 1
        assert events.count("eval:0") == 1
        assert events.index("prepare_eval") < events.index("eval:0")
        assert components.actor_model.trained == []
        assert not [event for event in events if event.startswith(("prepare_rollout", "generate_start"))]


class TestEvalBeforeTrain:
    async def test_fresh_run_evaluates_the_initial_checkpoint_at_step_zero(self, monkeypatch: pytest.MonkeyPatch):
        events: list[str] = []
        args = _make_args(num_rollout=2, eval_interval=1)
        _install_driver_fakes(monkeypatch, args, events)

        await with_disposer(train_driver.train, _startup_info(args))

        assert events.index("eval:0") < events.index("prepare_rollout:0")

    async def test_resumed_run_evaluates_the_completed_rollout_not_the_next_one(self, monkeypatch: pytest.MonkeyPatch):
        """start_rollout_id is the loaded checkpoint's rollout plus one, so dispatching it
        would ask for a checkpoint that does not exist yet and, in staging mode, export
        into the directory the first resumed iteration goes on to overwrite."""
        events: list[str] = []
        args = _make_args(num_rollout=5, eval_interval=1, start_rollout_id=3)
        _install_driver_fakes(monkeypatch, args, events)

        await with_disposer(train_driver.train, _startup_info(args))

        assert events.index("eval:2") < events.index("prepare_rollout:3")
        assert "eval:3" not in events[: events.index("prepare_rollout:3")]


class TestFinalEval:
    async def test_the_last_rollout_is_always_evaluated_even_off_cadence(self, monkeypatch: pytest.MonkeyPatch):
        """The final point carries force=True because training is over and backpressure is
        free, but the cadence check has to reach it first: with num_rollout not a multiple
        of eval_interval, the final weights would otherwise never be measured."""
        events: list[str] = []
        args = _make_args(num_rollout=3, eval_interval=2)
        _install_driver_fakes(monkeypatch, args, events)

        await with_disposer(train_driver.train, _startup_info(args))

        assert [event for event in events if event.startswith("eval:")] == ["eval:0", "eval:1", "eval:2"]

    async def test_an_off_cadence_final_eval_follows_the_last_handoff(self, monkeypatch: pytest.MonkeyPatch):
        """The last rollout skips its handoff only when no final eval follows; an off-cadence
        final eval must still see the engine onloaded with the trained weights."""
        events: list[str] = []
        args = _make_args(num_rollout=3, eval_interval=2, offload_rollout=True)
        _install_driver_fakes(monkeypatch, args, events)

        await with_disposer(train_driver.train, _startup_info(args))

        final = events[events.index("actor_train:2") : events.index("eval:2")]
        assert final.index("onload_weights") < final.index("update_weights:2") < final.index("onload_kv")

    async def test_the_last_rollout_skips_the_handoff_without_an_eval(self, monkeypatch: pytest.MonkeyPatch):
        events: list[str] = []
        args = _make_args(num_rollout=3, offload_rollout=True)
        _install_driver_fakes(monkeypatch, args, events)

        await with_disposer(train_driver.train, _startup_info(args))

        assert "update_weights:1" in events
        assert "update_weights:2" not in events
        assert "onload_weights" not in events[events.index("actor_train:2") :]


class TestWeightEqualityCheck:
    async def test_weight_equality_check_is_routed_to_the_inference_controller(self, monkeypatch: pytest.MonkeyPatch):
        """--check-weight-update-equal must reach the inference controller with every comparison option intact."""
        events: list[str] = []
        args = _make_args(
            check_weight_update_equal=True,
            check_weight_update_allow_quant_error=True,
            check_weight_update_selector="layers.0",
            check_weight_update_skip_list=["lm_head", "embed_tokens"],
        )
        components = _install_driver_fakes(monkeypatch, args, events)

        await with_disposer(train_driver.train, _startup_info(args))

        assert components.inference_controller.check_weights_calls == [
            dict(
                action="compare",
                allow_quant_error=True,
                selector="layers.0",
                skip_list=["lm_head", "embed_tokens"],
            )
        ]

    async def test_no_weight_comparison_without_the_flag(self, monkeypatch: pytest.MonkeyPatch):
        """The comparison reloads weights on every engine, so an ordinary run must never trigger it."""
        events: list[str] = []
        args = _make_args(check_weight_update_equal=False)
        components = _install_driver_fakes(monkeypatch, args, events)

        await with_disposer(train_driver.train, _startup_info(args))

        assert components.inference_controller.check_weights_calls == []


class TestCriticValuesHandoff:
    async def test_critic_outputs_reach_the_actor_and_are_released_after_training(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Critic value references reach actor training and remain live until it consumes them."""
        events: list[str] = []
        args = _make_args(num_rollout=1, use_critic=True)
        components = _install_driver_fakes(monkeypatch, args, events)
        store = FakeObjectStore()
        monkeypatch.setattr(object_store, "_INSTANCE", store)
        ref = store.put({"values": ["critic-values"]})
        values = [TrainStepOutput(outcome=TrainStepOutcome.NORMAL, values=ref)]
        components.critic_model.train_outputs[0] = values

        def consume_critic_values(external_data: list[TrainStepOutput]) -> None:
            assert external_data is values
            assert store.get(external_data[0].values).value == {"values": ["critic-values"]}

        components.actor_model.consume_external_data = consume_critic_values

        await with_disposer(train_driver.train, _startup_info(args))

        assert store.consumed == [ref]
        assert not store.contains(ref)


class TestApiServerWiring:
    async def test_api_server_receives_the_sync_driver_handles(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Only an enabled API server receives the live actor and inference controller handles."""
        started_with: list[dict[str, Any]] = []
        monkeypatch.setattr(placement_group, "start_api_server", lambda **kwargs: started_with.append(kwargs))
        disabled_events: list[str] = []
        disabled_args = _make_args(api_server_port=None)
        _install_driver_fakes(monkeypatch, disabled_args, disabled_events)
        await with_disposer(train_driver.train, _startup_info(disabled_args))
        assert started_with == []

        enabled_events: list[str] = []
        enabled_args = _make_args(api_server_port=8080)
        components = _install_driver_fakes(monkeypatch, enabled_args, enabled_events)
        await with_disposer(train_driver.train, _startup_info(enabled_args))

        assert len(started_with) == 1
        assert started_with[0]["trainer_models"] == {"actor": components.actor_model}
        assert started_with[0]["inference_controller"] is components.inference_controller
        assert started_with[0]["cell_operations"] is components.cell_operations


class TestCheckpointPublication:
    async def test_checkpoint_and_eval_share_the_completed_rollout_cadence(self, monkeypatch: pytest.MonkeyPatch):
        events: list[str] = []
        args = _make_args(
            num_rollout=40, save="/checkpoints/native", save_interval=20, eval_interval=20, skip_eval_before_train=True
        )
        components = _install_driver_fakes(monkeypatch, args, events, num_rollout_per_epoch=100)

        await with_disposer(train_driver.train, _startup_info(args))

        assert components.actor_model.saved == [19, 39]
        assert [event for event in events if event.startswith("eval:")] == ["eval:19", "eval:39"]
        for rollout_id in components.actor_model.saved:
            assert (
                events.index(f"executor_save:{rollout_id}")
                < events.index(f"actor_save:{rollout_id}")
                < events.index(f"eval:{rollout_id}")
            )

    @pytest.mark.parametrize("export_fails", [False, True])
    async def test_hf_only_export_needs_no_rollout_checkpoint(self, monkeypatch: pytest.MonkeyPatch, export_fails: bool):
        """The full driver reaches export without requesting resumable data progress."""
        events: list[str] = []
        args = _make_args(num_rollout=20, save_hf="/checkpoints/hf/{rollout_id}", save_interval=20)
        components = _install_driver_fakes(monkeypatch, args, events, num_rollout_per_epoch=100)

        async def reject_rollout_checkpoint(rollout_id):
            raise AssertionError("the orchestration only saves when --save is set")

        components.rollout_executor.save = reject_rollout_checkpoint
        if export_fails:

            async def fail_export(rollout_id, force_sync=False):
                raise OSError("HF export failed")

            components.actor_model.save_model = fail_export
            with pytest.raises(OSError, match="HF export failed"):
                await with_disposer(train_driver.train, _startup_info(args))
        else:
            await with_disposer(train_driver.train, _startup_info(args))
            assert components.actor_model.saved == [19]

    async def test_rollout_save_failure_does_not_publish_a_model_checkpoint(self, monkeypatch: pytest.MonkeyPatch):
        """A resumable model checkpoint must not precede its matching data progress."""
        events: list[str] = []
        args = _make_args(num_rollout=1, save="/checkpoints/native", save_interval=20)
        components = _install_driver_fakes(monkeypatch, args, events)

        async def fail_rollout_save(rollout_id):
            raise OSError("rollout state write failed")

        components.rollout_executor.save = fail_rollout_save

        with pytest.raises(OSError, match="rollout state write failed"):
            await with_disposer(train_driver.train, _startup_info(args))

        assert components.actor_model.saved == []


class TestTerminalLifecycle:
    @pytest.mark.parametrize("audit_fails", [False, True])
    async def test_final_audit_runs_with_live_api_and_cells(
        self, monkeypatch: pytest.MonkeyPatch, audit_fails: bool
    ) -> None:
        """Final audits retain a working observation endpoint even when the audit raises."""
        events: list[str] = []
        args = _make_args()
        components = _install_driver_fakes(monkeypatch, args, events)

        def close_api() -> None:
            events.append("api_closed")

        async def final_audit() -> None:
            assert "api_closed" not in events
            assert "actor_dispose" not in events
            assert "inference_dispose" not in events
            events.append("audit")
            if audit_fails:
                raise RuntimeError("audit failed")

        monkeypatch.setattr(train_driver, "maybe_start_api_server", lambda *args, **kwargs: close_api)
        monkeypatch.setattr(components.rollout_executor, "_dispose", final_audit)

        if audit_fails:
            with pytest.raises(RuntimeError, match="audit failed"):
                await with_disposer(train_driver.train, _startup_info(args))
        else:
            await with_disposer(train_driver.train, _startup_info(args))

        assert events.count("audit") == 1
        assert events.index("audit") < events.index("api_closed") < events.index("actor_dispose")
        assert "inference_dispose" in events

    async def test_model_creation_failure_still_disposes_rollout(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Startup failure before the API exists still releases the rollout components."""
        events: list[str] = []
        args = _make_args()
        _install_driver_fakes(monkeypatch, args, events)

        async def fail_creation(*args: Any, handles: dict[str, FakeTrainingModel]) -> None:
            raise RuntimeError("model creation failed")

        monkeypatch.setattr(train_driver, "create_training_models", fail_creation)
        with pytest.raises(RuntimeError, match="model creation failed"):
            await with_disposer(train_driver.train, _startup_info(args))

        assert events == ["executor_dispose", "inference_dispose"]

    async def test_train_disposes_all_created_component_controllers(self, monkeypatch: pytest.MonkeyPatch):
        """Every component the driver created must be disposed, or its watchers outlive the run."""
        events: list[str] = []
        args = _make_args(use_critic=True)
        _install_driver_fakes(monkeypatch, args, events)

        await with_disposer(train_driver.train, _startup_info(args))

        assert sorted(event for event in events if event.endswith("_dispose")) == [
            "actor_dispose",
            "critic_dispose",
            "executor_dispose",
            "inference_dispose",
        ]

    async def test_train_releases_its_worker_manager_after_component_disposal(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The driver releases its own manager only after every component has been disposed."""
        events: list[str] = []
        args = _make_args(use_critic=True)
        manager = FakeWorkerManager(events)
        _install_driver_fakes(monkeypatch, args, events)

        def init_orchestration_script(_startup_info: ArgvOrchestratorStartupInfo, *, disposer: Any) -> None:
            disposer.add(partial(wiring.shutdown_worker_manager, manager))

        monkeypatch.setattr(train_driver, "init_orchestration_script", init_orchestration_script)
        monkeypatch.setattr(wiring.ray, "kill", manager.kill)

        await with_disposer(train_driver.train, _startup_info(args))

        assert manager.killed == [manager]
        assert all(
            events.index(event) < events.index("manager_shutdown") for event in events if event.endswith("_dispose")
        )
        assert events.index("manager_shutdown") < events.index("manager_kill")


class TestOutputStoreRelease:
    async def test_each_rollout_is_released_once_it_has_trained(self, monkeypatch: pytest.MonkeyPatch):
        """The executor may delete a rollout's stored objects only after every trainer read them."""
        events: list[str] = []
        args = _make_args(num_rollout=3)
        components = _install_driver_fakes(monkeypatch, args, events)
        trained_at_release: list[tuple[int, list[int]]] = []

        async def release(rollout_id: int) -> None:
            trained_at_release.append((rollout_id, list(components.actor_model.trained)))

        components.rollout_executor.release = FakeRemoteMethod(release)

        await with_disposer(train_driver.train, _startup_info(args))

        assert trained_at_release == [(0, [0]), (1, [0, 1]), (2, [0, 1, 2])]


class TestEvalTrainLogProbs:
    @pytest.mark.parametrize("level", ["weight", "kv_cache,weight", "kv_cache", ""])
    async def test_released_weights_are_restored_by_the_native_same_version_publication_before_kv(
        self, monkeypatch, tmp_path, level
    ):
        events = []
        args = _make_args(
            offload_rollout=bool(level), offload_rollout_level=level,
            log_inference_engine_weight_checksums=False,
            save_debug_train_data=str(tmp_path / "{rollout_id}_{rank}.pt"), qkv_format="thd",
        )
        store = FakeObjectStore()
        monkeypatch.setattr(object_store, "_INSTANCE", store)
        monkeypatch.setattr(train_driver, "update_weights", placement_group.update_weights)
        source = torch.tensor([[0.0, 2.0], [3.0, -1.0]])
        engine = source.clone()
        original_scores = torch.log_softmax(source, dim=-1)
        info = SimpleNamespace(snapshot_cell_id_to_hashes={"cell0": "workers0"})
        executor = SimpleNamespace(version=7)

        async def offload(*, tags):
            events.append(("offload", list(tags)))
            if train_driver.GPU_MEMORY_TYPE_WEIGHTS in tags:
                engine.zero_()

        async def onload(*, tags):
            events.append(("onload", list(tags)))
            if train_driver.GPU_MEMORY_TYPE_WEIGHTS not in tags:
                torch.testing.assert_close(engine, source, rtol=0, atol=0)

        async def start_update_weights(*, model_id):
            assert model_id is None
            events.append(("start_update", None))
            return info

        async def actor_update(*, info: Any, rollout_id):
            assert info.snapshot_cell_id_to_hashes == {"cell0": "workers0"} and rollout_id is None
            events.append(("actor_publish", 7))
            engine.copy_(source)
            return WeightUpdateOutput(weight_version=7, failed_cell_ids=())

        async def end_update_weights(**kwargs):
            assert kwargs == dict(
                snapshot_cell_id_to_hashes={"cell0": "workers0"}, failed_cell_ids=(),
                checksum_model_id=None, collect_checksums=False,
            )
            events.append(("end_update", None))
            return []

        async def set_weight_version(version, *, trainer_model_id):
            assert trainer_model_id is None and version == executor.version == 7
            events.append(("consumed_version", version))

        async def prepare_eval():
            events.append(("prepare_eval", None))
            torch.testing.assert_close(engine, source, rtol=0, atol=0)

        async def score(*_args):
            events.append(("score", None))
            return [store.put(dict(metadata=dict(rank=0, cp_rank=0, cp_size=1), log_probs=[torch.tensor([-1.0])]))]

        executor.set_weight_version = set_weight_version
        controller = SimpleNamespace(
            offload=offload, onload=onload, start_update_weights=start_update_weights,
            end_update_weights=end_update_weights, prepare_eval=prepare_eval,
        )
        pack = RolloutDataPack(data_ref=store.put({"tokens": [[1, 2]]}))
        await train_driver._score_eval_train_data(
            args, SimpleNamespace(score_log_probs=score, update_weights=actor_update), controller, 19, {"monitor": pack},
            rollout_executor=executor,
        )
        torch.testing.assert_close(engine, source, rtol=0, atol=0)
        torch.testing.assert_close(torch.log_softmax(engine, dim=-1), original_scores, rtol=0, atol=0)
        assert torch.unique(original_scores).numel() > 1 and executor.version == 7
        names = [name for name, _ in events]
        if "weight" in level:
            assert names == [
                "offload", "score", "onload", "start_update", "actor_publish", "end_update",
                "consumed_version", "onload", "prepare_eval",
            ]
            assert events[2][1] == [train_driver.GPU_MEMORY_TYPE_WEIGHTS]
            assert events[-2][1] == [
                train_driver.GPU_MEMORY_TYPE_CUDA_GRAPH,
                *([train_driver.GPU_MEMORY_TYPE_KV_CACHE] if "kv_cache" in level else []),
            ]
        elif level:
            assert names == ["offload", "score", "onload", "prepare_eval"]
        else:
            assert names == ["score"]
        assert store._values == {}

    @pytest.mark.parametrize("restore_failure", [None, "onload", "prepare_eval"])
    async def test_preparation_failure_is_soft_only_after_successful_restoration(
        self, monkeypatch, caplog, restore_failure
    ):
        events = []
        args = _make_args(offload_rollout=True, offload_rollout_level="kv_cache,weight")
        store = FakeObjectStore()
        monkeypatch.setattr(object_store, "_INSTANCE", store)
        packs = {"monitor": RolloutDataPack(data_ref=store.put({"tokens": [[1, 2]]}))}
        inference = SimpleNamespace(resident=True)

        async def offload(*, tags):
            events.append("offload")
            inference.resident = False
            raise ValueError("monitor preparation failed")

        async def onload(*, tags):
            events.append("onload")
            if restore_failure == "onload":
                raise OSError("onload restoration failed")
            inference.resident = True

        async def prepare_eval():
            events.append("prepare_eval")
            if restore_failure == "prepare_eval":
                raise OSError("prepare_eval restoration failed")

        async def score(*_args):
            pytest.fail("An incompletely prepared observer must not run the actor forward")

        log_error = train_driver.logger.error

        def record_error(*args, **kwargs):
            assert inference.resident and events[-1] == "prepare_eval"
            events.append("unverified")
            log_error(*args, **kwargs)

        monkeypatch.setattr(train_driver.logger, "error", record_error)
        inference.offload = offload
        inference.onload = onload
        inference.prepare_eval = prepare_eval
        actor = SimpleNamespace(score_log_probs=score)

        async def publish(*_args):
            events.append("publish")

        monkeypatch.setattr(train_driver, "update_weights", publish)

        if restore_failure is None:
            await train_driver._score_eval_train_data(args, actor, inference, 19, packs, rollout_executor=None)
            assert events == ["offload", "onload", "publish", "onload", "prepare_eval", "unverified"]
            assert "unverified: preparation failed" in caplog.text
            assert "monitor preparation failed" in caplog.text
        else:
            with pytest.raises(OSError, match=f"{restore_failure} restoration failed"):
                await train_driver._score_eval_train_data(args, actor, inference, 19, packs, rollout_executor=None)
            assert events == ["offload", "onload"] + (
                ["publish", "onload", "prepare_eval"] if restore_failure == "prepare_eval" else []
            )
            assert "unverified" not in caplog.text
        assert store._values == {}

    async def test_monitor_preparation_failure_restores_and_training_continues(self, monkeypatch, tmp_path, caplog):
        events = []
        args = _make_args(
            num_rollout=2,
            eval_interval=1,
            eval_train_log_probs=True,
            offload_train=True,
            offload_rollout=True,
            offload_rollout_level="kv_cache,weight",
            save_debug_train_data=str(tmp_path / "{rollout_id}_{rank}.pt"),
            qkv_format="thd",
        )
        components = _install_driver_fakes(monkeypatch, args, events)
        store = FakeObjectStore()
        monkeypatch.setattr(object_store, "_INSTANCE", store)
        offload_failed = False
        native_offload = components.inference_controller.offload

        async def offload(*, tags):
            nonlocal offload_failed
            if not offload_failed:
                offload_failed = True
                events.append("monitor_offload_failed")
                raise ValueError("monitor preparation failed")
            await native_offload(tags)

        async def onload(*, tags):
            events.append("monitor_residency_restored")

        async def evaluate(rollout_id, *, return_train_data):
            assert return_train_data
            events.append(f"eval:{rollout_id}")
            return {"monitor": RolloutDataPack(data_ref=store.put({"tokens": [[1, 2]]}))}

        async def score(rollout_id, pack):
            events.append(f"score:{rollout_id}")
            return [store.put(dict(metadata=dict(rank=0, cp_rank=0, cp_size=1), log_probs=[torch.tensor([-1.0])]))]

        components.inference_controller.offload = offload
        components.inference_controller.onload = onload
        components.rollout_executor.eval = evaluate
        components.actor_model.score_log_probs = score
        await with_disposer(train_driver.train, _startup_info(args))

        restored = events.index("monitor_residency_restored")
        assert events.index("monitor_offload_failed") < restored
        assert restored < events.index("prepare_eval", restored) < events.index("generate_start:0")
        assert components.actor_model.trained == [0, 1]
        assert components.rollout_executor.released == [0, 1]
        assert [event for event in events if event.startswith("score:")] == ["score:0", "score:1"]
        assert store._values == {}
        assert "unverified: preparation failed" in caplog.text

    async def test_monitoring_follows_baseline_and_all_published_d9_points(self, monkeypatch, tmp_path):
        events = []
        args = _make_args(
            num_rollout=100,
            eval_interval=20,
            eval_train_log_probs=True,
            save_debug_train_data=str(tmp_path / "{rollout_id}_{rank}.pt"),
            qkv_format="thd",
        )
        components = _install_driver_fakes(monkeypatch, args, events, num_rollout_per_epoch=100)
        store = FakeObjectStore()
        monkeypatch.setattr(object_store, "_INSTANCE", store)

        async def evaluate(rollout_id, *, return_train_data):
            assert return_train_data
            events.append(f"eval:{rollout_id}")
            return {"monitor": RolloutDataPack(data_ref=store.put({"tokens": [[1, 2]]}))}

        async def score(rollout_id, pack):
            assert store.contains(pack.data_ref)
            events.append(f"score:{rollout_id}")
            return [store.put(dict(metadata=dict(rank=0, cp_rank=0, cp_size=1), log_probs=[torch.tensor([-1.0])]))]

        components.rollout_executor.eval = evaluate
        components.actor_model.score_log_probs = score
        await with_disposer(train_driver.train, _startup_info(args))

        points = [0, 19, 39, 59, 79, 99]
        assert [event for event in events if event.startswith("score:")] == [f"score:{point}" for point in points]
        assert events.index("score:0") < events.index("actor_train:0")
        for point in points[1:]:
            assert events.index(f"actor_train:{point}") < events.index(f"update_weights:{point}")
            assert (
                events.index(f"update_weights:{point}") < events.index(f"eval:{point}") < events.index(f"score:{point}")
            )
        assert components.actor_model.trained == list(range(100))
        assert components.rollout_executor.released == list(range(100))
        assert store._values == {}
        assert sorted(path.name for path in tmp_path.glob("*.pt")) == sorted(
            f"eval_monitor_{point}_0.pt" for point in points
        )

    @pytest.mark.parametrize("failure", [None, "score", "dump", "cancel", "preparation_cancel"])
    async def test_scoring_cleanup_and_residency_are_finally_restored(self, monkeypatch, tmp_path, caplog, failure):
        import asyncio

        events = []
        args = _make_args(
            offload_rollout=True,
            offload_rollout_level="kv_cache,weight",
            save_debug_train_data=str(tmp_path / "{rollout_id}_{rank}.pt"),
            qkv_format="thd",
        )
        store = FakeObjectStore()
        monkeypatch.setattr(object_store, "_INSTANCE", store)
        input_ref = store.put({"tokens": [[1, 2]]})
        removed = []
        remove = store.remove

        def record_remove(ref):
            removed.append(ref)
            remove(ref)

        monkeypatch.setattr(store, "remove", record_remove)
        packs = {"monitor/short": RolloutDataPack(data_ref=input_ref)}
        actor = SimpleNamespace(sleeping=True)
        inference = SimpleNamespace(resident=True)
        payload = dict(
            metadata=dict(rank=7, cp_rank=1, cp_size=2, qkv_format="thd", weight_version=20),
            log_probs=[torch.tensor([float("nan"), -2.0])],
        )

        async def offload(*, tags):
            inference.resident = False
            events.append("offload")
            if failure == "preparation_cancel":
                raise asyncio.CancelledError()

        async def onload(*, tags):
            assert actor.sleeping
            inference.resident = True
            events.append("onload")

        async def prepare():
            events.append("prepare_eval")

        async def publish(*_args):
            assert actor.sleeping
            events.append("publish")

        monkeypatch.setattr(train_driver, "update_weights", publish)

        async def score(rollout_id, pack):
            assert rollout_id == 19 and pack.data_ref is input_ref
            assert not inference.resident
            actor.sleeping = False
            try:
                events.append("score")
                if failure == "score":
                    raise ValueError("observer forward failed")
                if failure == "cancel":
                    raise asyncio.CancelledError()
                return [store.put(payload)]
            finally:
                actor.sleeping = True

        actor.score_log_probs = score
        inference.offload = offload
        inference.onload = onload
        inference.prepare_eval = prepare
        log_error = train_driver.logger.error
        logged_after_restoration = []

        def record_error(*args, **kwargs):
            logged_after_restoration.append(inference.resident and actor.sleeping and events[-1] == "prepare_eval")
            log_error(*args, **kwargs)

        monkeypatch.setattr(train_driver.logger, "error", record_error)
        if failure == "dump":

            def fail_dump(*args, **kwargs):
                raise OSError("observer output failed")

            monkeypatch.setattr(train_driver, "save_debug_train_data_for_rank", fail_dump)

        if failure in {"cancel", "preparation_cancel"}:
            with pytest.raises(asyncio.CancelledError):
                await train_driver._score_eval_train_data(args, actor, inference, 19, packs, rollout_executor=None)
        else:
            await train_driver._score_eval_train_data(args, actor, inference, 19, packs, rollout_executor=None)
        assert actor.sleeping and inference.resident
        assert events == ["offload"] + ([] if failure == "preparation_cancel" else ["score"]) + [
            "onload",
            "publish",
            "onload",
            "prepare_eval",
        ]
        assert store._values == {}
        assert len(removed) == len(set(removed)) == (1 if failure in {"score", "cancel", "preparation_cancel"} else 2)
        assert logged_after_restoration == ([True] if failure in {"score", "dump"} else [])
        if failure in {"score", "dump"}:
            assert "unverified: scoring/dump failed" in caplog.text
        if failure is None:
            dump = torch.load(tmp_path / "eval_monitor%2Fshort_19_7.pt", weights_only=False)
            assert dump["cp_rank"] == 1 and dump["cp_size"] == 2
            assert dump["rollout_data"]["metadata"]["weight_version"] == 20
            assert torch.isnan(dump["rollout_data"]["log_probs"][0][0])

    async def test_one_failed_dataset_does_not_discard_other_scoring(self, monkeypatch, tmp_path, caplog):
        args = _make_args(save_debug_train_data=str(tmp_path / "{rollout_id}_{rank}.pt"), qkv_format="thd")
        store = FakeObjectStore()
        monkeypatch.setattr(object_store, "_INSTANCE", store)
        packs = {name: RolloutDataPack(data_ref=store.put({"dataset": name})) for name in ("bad", "good")}

        async def score(rollout_id, pack):
            if store.get(pack.data_ref).value["dataset"] == "bad":
                raise ValueError("bad observation")
            return [store.put(dict(metadata=dict(rank=0, cp_rank=0, cp_size=1), log_probs=[-1.0]))]

        await train_driver._score_eval_train_data(
            args, SimpleNamespace(score_log_probs=score), None, 19, packs, rollout_executor=None
        )
        assert (tmp_path / "eval_good_19_0.pt").exists()
        assert store._values == {}
        assert "unverified: scoring/dump failed" in caplog.text
