"""Exercise driver cancellation through real controller and synchronous worker Ray handles."""

import asyncio
from types import SimpleNamespace

import pytest
import ray
import torch
import train as train_driver
from tests.ci.ci_register import register_cpu_ci
from tests.fast.ray.train.test_score_log_probs import ScoreGate

from miles.ray.train.group import TrainerController
from miles.ray import placement_group
from miles.ray.train_actor import WeightUpdateOutput
from miles.utils import object_store
from miles.utils.data import RolloutDataPack
from miles.utils.ft_utils.health_checker import ActivenessTracker
from miles.utils.object_store import RayObjectStore
from miles.utils.workers.ray_worker_handle import RayWorkerHandle

register_cpu_ci(est_time=120, suite="stage-b-cpu", labels=["megatron"])

@ray.remote(num_cpus=0)
class SynchronousScoreWorker:
    def __init__(self, gate, rank):
        self.gate = gate
        self.rank = rank
        self.asleep = True
        self.store = RayObjectStore(frees_objects=False)

    def score_log_probs(self, *, rollout_id, rollout_data_ref):
        self.asleep = False
        try:
            ray.get(self.gate.wait.remote(self.rank))
            with self.store.get(rollout_data_ref) as data:
                result = self.store.put(
                    dict(
                        log_probs=[[-1.0]],
                        sample_indices=data["sample_indices"],
                        metadata=dict(rank=self.rank, cp_rank=0, cp_size=1, rollout_id=rollout_id),
                    )
                )
            return result
        finally:
            self.asleep = True
            ray.get(self.gate.finish.remote(self.rank, self.asleep))


@ray.remote(num_cpus=0)
class RemoteScoreController(TrainerController):
    def __init__(self, workers):
        handles = [RayWorkerHandle(worker) for worker in workers]
        self._cells_by_id = {
            "cell0": SimpleNamespace(cell_index=0, is_alive=True, _get_worker_handles=lambda: handles)
        }
        self._health_checker_activeness = ActivenessTracker(active=False)


@pytest.mark.parametrize("restore_failure", [None, "onload", "publish", "end_update", "version", "kv_graph", "prepare_eval"])
async def test_driver_cancellation_drains_remote_controller_before_cleanup_and_restore(
    ray_local_mode, monkeypatch, tmp_path, restore_failure
):
    gate = ScoreGate.remote()
    workers = [SynchronousScoreWorker.remote(gate, rank) for rank in range(2)]
    controller = RemoteScoreController.remote(workers)
    ranks = [0, 1]
    removals = []
    events = []
    store = RayObjectStore(frees_objects=False)
    native_remove = store.remove

    def remove(ref):
        removals.append((ref, ray.get(gate.get_status.remote())["finished"]))
        native_remove(ref)

    monkeypatch.setattr(store, "remove", remove)
    monkeypatch.setattr(object_store, "_INSTANCE", store)
    pack = RolloutDataPack(data_ref=store.put(dict(tokens=[[1, 2]], sample_indices=[7])))
    onload_entered = asyncio.Event()
    onload_release = asyncio.Event()
    publish_entered = asyncio.Event()
    publish_release = asyncio.Event()

    async def offload(*, tags):
        events.append("offload")

    async def onload(*, tags):
        assert (await gate.get_status.remote())["finished"] == {rank: True for rank in ranks}
        phase = "onload" if train_driver.GPU_MEMORY_TYPE_WEIGHTS in tags else "kv_graph"
        events.append(phase)
        if phase == "onload":
            assert tags == [train_driver.GPU_MEMORY_TYPE_WEIGHTS]
            onload_entered.set()
            await onload_release.wait()
        else:
            assert tags == [train_driver.GPU_MEMORY_TYPE_CUDA_GRAPH, train_driver.GPU_MEMORY_TYPE_KV_CACHE]
        if restore_failure == phase:
            raise OSError("residency restoration failed")

    async def prepare_eval():
        events.append("prepare_eval")
        if restore_failure == "prepare_eval":
            raise OSError("residency restoration failed")

    async def start_update_weights(*, model_id):
        assert model_id is None
        events.append("start_update")
        return SimpleNamespace(snapshot_cell_id_to_hashes={"cell0": "workers0"})

    async def publish(*, info, rollout_id):
        assert rollout_id is None and info.snapshot_cell_id_to_hashes == {"cell0": "workers0"}
        assert len(removals) == 3
        events.append("publish")
        publish_entered.set()
        await publish_release.wait()
        if restore_failure == "publish":
            raise OSError("residency restoration failed")
        return WeightUpdateOutput(weight_version=7, failed_cell_ids=())

    async def end_update_weights(**kwargs):
        assert kwargs["snapshot_cell_id_to_hashes"] == {"cell0": "workers0"} and kwargs["failed_cell_ids"] == ()
        events.append("end_update")
        if restore_failure == "end_update":
            raise OSError("residency restoration failed")
        return []

    async def abort_update_weights():
        events.append("abort_update")

    async def set_weight_version(version, *, trainer_model_id):
        assert version == 7 and trainer_model_id is None
        events.append("version")
        if restore_failure == "version":
            raise OSError("residency restoration failed")

    monkeypatch.setattr(train_driver, "update_weights", placement_group.update_weights)

    args = SimpleNamespace(
        offload_rollout=True,
        offload_rollout_level="kv_cache,weight",
        save_debug_train_data=str(tmp_path / "{rollout_id}_{rank}.pt"),
        qkv_format="thd",
        log_inference_engine_weight_checksums=False,
    )
    task = asyncio.create_task(
        train_driver._score_eval_train_data(
            args,
            SimpleNamespace(score_log_probs=RayWorkerHandle(controller).score_log_probs, update_weights=publish),
            SimpleNamespace(
                offload=offload, onload=onload, prepare_eval=prepare_eval,
                start_update_weights=start_update_weights, end_update_weights=end_update_weights,
                abort_update_weights=abort_update_weights,
            ),
            19,
            {"monitor": pack},
            rollout_executor=SimpleNamespace(set_weight_version=set_weight_version),
        )
    )
    try:
        await asyncio.wait_for(gate.wait_entered.remote(ranks), timeout=30)
        for message in ["cancel monitoring", "cancel monitoring again"]:
            task.cancel(message)
            done, _ = await asyncio.wait([task], timeout=0.25)
            assert not done, "driver cancellation abandoned its remote controller RPC"
            assert not removals and events == ["offload"]
            with store.get(pack.data_ref) as data:
                assert data["sample_indices"] == [7]
        await gate.release.remote(ranks[0])
        await gate.wait_finished.remote([ranks[0]])
        task.cancel("cancel while the second worker is running")
        done, _ = await asyncio.wait([task], timeout=0.25)
        assert not done and not removals and not onload_entered.is_set()
        await gate.release.remote(ranks[1])
        await asyncio.wait_for(onload_entered.wait(), timeout=30)
        task.cancel("cancel while residency is being restored")
        done, _ = await asyncio.wait([task], timeout=0.25)
        assert not done and events == ["offload", "onload"]
        onload_release.set()
        if restore_failure != "onload":
            await asyncio.wait_for(publish_entered.wait(), timeout=30)
            task.cancel("cancel while same-version weights are being published")
            done, _ = await asyncio.wait([task], timeout=0.25)
            assert not done and events == ["offload", "onload", "start_update", "publish"]
    finally:
        for rank in ranks:
            await gate.release.remote(rank)
        await asyncio.wait_for(gate.wait_finished.remote(ranks), timeout=30)
        onload_release.set()
        publish_release.set()
        await asyncio.wait_for(asyncio.gather(task, return_exceptions=True), timeout=30)
        for actor in [controller, *workers, gate]:
            ray.kill(actor)

    if restore_failure:
        with pytest.raises(OSError, match="residency restoration failed"):
            task.result()
        phases = ["offload", "onload", "start_update", "publish", "end_update", "version", "kv_graph", "prepare_eval"]
        assert events == phases[: phases.index(restore_failure) + 1] + (
            ["abort_update"] if restore_failure == "publish" else []
        )
    else:
        with pytest.raises(asyncio.CancelledError, match="cancel monitoring"):
            task.result()
        assert events == ["offload", "onload", "start_update", "publish", "end_update", "version", "kv_graph", "prepare_eval"]
    assert len(removals) == len({ref for ref, _ in removals}) == 3
    assert pack.data_ref in [ref for ref, _ in removals]
    assert all(finished == {rank: True for rank in ranks} for _, finished in removals)
    for rank in ranks:
        payload = torch.load(tmp_path / f"eval_monitor_19_{rank}.pt", weights_only=False)["rollout_data"]
        assert payload["sample_indices"] == [7] and payload["metadata"]["rank"] == rank
