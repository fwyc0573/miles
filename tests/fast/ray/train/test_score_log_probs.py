from types import SimpleNamespace

import pytest
import ray
from tests.ci.ci_register import register_cpu_ci
from tests.fast.ray.train.conftest import get_raw_actor_handles, make_alive_cell

from miles.ray.train.group import TrainerController
from miles.utils import object_store
from miles.utils.data import RolloutDataPack
from miles.utils.ft_utils.health_checker import ActivenessTracker
from miles.utils.object_store import _MooncakeStoreObjectRef
from miles.utils.workers.rpc.common.metadata import collect_rpc_method_specs

register_cpu_ci(est_time=60, suite="stage-b-cpu", labels=["megatron"])


def _make_controller(cells, *, active):
    controller = object.__new__(TrainerController)
    controller._cells_by_id = {cell.cell_id: cell for cell in cells}
    controller._health_checker_activeness = ActivenessTracker(active=active)
    return controller


@pytest.mark.parametrize("active", [False, True])
@pytest.mark.asyncio
async def test_native_cell_fanout_unwraps_refs_preserves_order_and_restores_health(active):
    cells = [make_alive_cell(index, alive_cell_indices=[0, 1]) for index in [1, 0]]
    for cell in cells:
        handles = get_raw_actor_handles(cell)
        ray.get(handles[0].set_score_return_value.remote(_MooncakeStoreObjectRef(payload=f"score-{cell.cell_index}")))
        ray.get(handles[1].set_score_return_value.remote(None))
    controller = _make_controller(cells, active=active)
    data = RolloutDataPack(data_ref=[_MooncakeStoreObjectRef(payload="dp0"), _MooncakeStoreObjectRef(payload="dp1")])

    refs = await controller.score_log_probs(9, data)

    assert [ref.payload for ref in refs] == ["score-0", "score-1"]
    assert controller._health_checker_activeness.get().active is active
    for cell in cells:
        for handle in get_raw_actor_handles(cell):
            assert ray.get(handle.get_calls.remote()) == [
                ("score_log_probs", (), dict(rollout_id=9, rollout_data_ref=data.data_ref))
            ]


@pytest.mark.asyncio
async def test_scoring_failure_is_not_retried_or_killed_and_successful_cell_refs_are_released(monkeypatch):
    cells = [make_alive_cell(index, alive_cell_indices=[0, 1]) for index in [0, 1]]
    for handle in get_raw_actor_handles(cells[0]):
        ray.get(handle.set_fail_methods.remote(["score_log_probs"]))
    for handle in get_raw_actor_handles(cells[1]):
        ray.get(handle.set_score_return_value.remote(_MooncakeStoreObjectRef(payload="successful")))
    removed = []
    monkeypatch.setattr(object_store, "_INSTANCE", SimpleNamespace(remove=lambda ref: removed.append(ref.payload)))
    controller = _make_controller(cells, active=False)

    with pytest.raises(Exception, match="Injected failure in score_log_probs"):
        await controller.score_log_probs(9, RolloutDataPack(data_ref=_MooncakeStoreObjectRef(payload="input")))

    assert removed == ["successful", "successful"]
    assert all(cell.is_alive for cell in cells)
    assert controller._health_checker_activeness.get().active is False
    for cell in cells:
        for handle in get_raw_actor_handles(cell):
            assert [call[0] for call in ray.get(handle.get_calls.remote())] == ["score_log_probs"]


def test_controller_scoring_rpc_pack_and_result_roundtrip():
    spec = collect_rpc_method_specs(TrainerController)["score_log_probs"]
    pack = RolloutDataPack(sample_indices=[7], data_ref=_MooncakeStoreObjectRef(payload="input"))
    query = dict(rollout_id=9, rollout_data=pack)
    assert spec.serializer.decode_query(spec.serializer.encode_query(query)) == query
    refs = [_MooncakeStoreObjectRef(payload="output")]
    assert spec.serializer.decode_result(spec.serializer.encode_result(refs)) == refs
    assert spec.is_async


@ray.remote(num_cpus=0)
class ScoreGate:
    """Observe and release synchronous remote scoring calls without cancelling them."""

    def __init__(self):
        self.entered = set()
        self.finished = {}
        self.releases = {}
        self.changed = asyncio.Event()

    async def wait(self, worker_id):
        self.entered.add(worker_id)
        release = self.releases.setdefault(worker_id, asyncio.Event())
        self.changed.set()
        await release.wait()

    async def finish(self, worker_id, asleep):
        self.finished[worker_id] = asleep
        self.changed.set()

    async def release(self, worker_id):
        self.releases.setdefault(worker_id, asyncio.Event()).set()

    async def wait_entered(self, worker_ids):
        while not set(worker_ids).issubset(self.entered):
            self.changed.clear()
            await self.changed.wait()

    async def wait_finished(self, worker_ids):
        while not set(worker_ids).issubset(self.finished):
            self.changed.clear()
            await self.changed.wait()

    async def get_status(self):
        return dict(entered=sorted(self.entered), finished=dict(self.finished))


async def _gated_scoring(monkeypatch, cells):
    gate = ScoreGate.remote()
    worker_ids = []
    removed = []
    for cell in cells:
        for index, handle in enumerate(get_raw_actor_handles(cell)):
            worker_id = f"{cell.cell_index}-{index}"
            worker_ids.append(worker_id)
            await handle.set_score_gate.remote(gate, worker_id)
            await handle.set_score_return_value.remote(_MooncakeStoreObjectRef(payload=worker_id))
    monkeypatch.setattr(object_store, "_INSTANCE", SimpleNamespace(remove=lambda ref: removed.append(ref.payload)))
    controller = _make_controller(cells, active=False)
    caller_finally = []

    async def call():
        try:
            return await controller.score_log_probs(9, RolloutDataPack(data_ref=_MooncakeStoreObjectRef(payload="input")))
        finally:
            caller_finally.append(await gate.get_status.remote())

    task = asyncio.create_task(call())
    await gate.wait_entered.remote(worker_ids)
    return gate, worker_ids, removed, controller, caller_finally, task


@pytest.mark.asyncio
async def test_failed_ray_rank_drains_slow_sibling_before_driver_finally(monkeypatch):
    cell = make_alive_cell(0, alive_cell_indices=[0])
    await get_raw_actor_handles(cell)[0].set_fail_methods.remote(["score_log_probs"])
    gate, worker_ids, removed, controller, caller_finally, task = await _gated_scoring(monkeypatch, [cell])
    try:
        await gate.release.remote(worker_ids[0])
        await gate.wait_finished.remote([worker_ids[0]])
        done, _ = await asyncio.wait([task], timeout=0.25)
        assert not done, "controller finished while the healthy synchronous Ray actor still held GPU residency"
        assert not caller_finally
        assert not (await gate.get_status.remote())["finished"].get(worker_ids[1], False)
        assert not removed
    finally:
        for worker_id in worker_ids:
            await gate.release.remote(worker_id)
        await gate.wait_finished.remote(worker_ids)
        await asyncio.gather(task, return_exceptions=True)
        ray.kill(gate)
    with pytest.raises(Exception, match="Injected failure in score_log_probs"):
        task.result()
    assert caller_finally[0]["finished"] == {worker_id: True for worker_id in worker_ids}
    assert removed == [worker_ids[1]]
    assert cell.is_alive and controller._health_checker_activeness.get().active is False


@pytest.mark.asyncio
async def test_cancelled_outer_call_drains_every_remote_cell_before_driver_finally(monkeypatch):
    cells = [make_alive_cell(index, alive_cell_indices=[0, 1]) for index in [0, 1]]
    gate, worker_ids, removed, controller, caller_finally, task = await _gated_scoring(monkeypatch, cells)
    try:
        task.cancel("cancel scoring")
        done, _ = await asyncio.wait([task], timeout=0.25)
        assert not done, "outer cancellation abandoned live synchronous Ray scoring calls"
        task.cancel("cancel scoring again")
        await gate.release.remote(worker_ids[0])
        await gate.wait_finished.remote([worker_ids[0]])
        done, _ = await asyncio.wait([task], timeout=0.25)
        assert not done and not caller_finally
        assert not removed
    finally:
        for worker_id in worker_ids:
            await gate.release.remote(worker_id)
        await gate.wait_finished.remote(worker_ids)
        await asyncio.gather(task, return_exceptions=True)
        ray.kill(gate)
    assert task.cancelled()
    assert caller_finally[0]["finished"] == {worker_id: True for worker_id in worker_ids}
    assert removed == worker_ids
    assert all(cell.is_alive for cell in cells)
    assert controller._health_checker_activeness.get().active is False
import asyncio
