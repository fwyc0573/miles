"""Shared-engine eval packs contain only the evaluation samples and never advance training."""

from copy import deepcopy
from unittest.mock import AsyncMock

import pytest
import torch
from tests.fast.fixtures.driver_fakes import FakeObjectStore
from tests.fast.ray.rollout.conftest import make_args, make_sample
from tests.fast.train_parallel_config_utils import make_train_parallel_config

from miles.ray.rollout import rollout_executor as executor_module
from miles.ray.rollout.rollout_executor import RolloutExecutor
from miles.rollout.base_types import RolloutFnEvalOutput
from miles.utils import object_store
from miles.utils.types import WeightVersionsPerCall, WeightVersionSpan
from miles.utils.workers.rpc.common.metadata import collect_rpc_method_specs


def _executor(monkeypatch, *, data, **overrides):
    executor = RolloutExecutor.__new__(RolloutExecutor)
    executor.args = make_args(n_samples_per_prompt=1, global_batch_size=2, rewards_normalization=False, **overrides)
    executor.use_legacy_rollout_v1 = False
    executor.eval_generate_rollout = AsyncMock(return_value=RolloutFnEvalOutput(data=data))
    executor._refresh_inference_runtime_mut_state = AsyncMock()
    executor._metric_checker = None
    executor.custom_convert_samples_to_train_data_func = None
    executor.custom_reward_post_process_func = None
    executor._train_parallel_configs_of_model_id = {
        None: make_train_parallel_config(dp_size=2, supports_precomputed_schedule=True)
    }
    executor.get = AsyncMock(side_effect=AssertionError("evaluation must not consume training"))
    executor.release = AsyncMock(side_effect=AssertionError("evaluation must not release a training rollout"))
    executor.last_get_rollout_id_of_model_id = {None: 19}
    executor._unreleased_store_refs = {19: {"training-ref": object()}}
    executor.data_source = object()
    monkeypatch.setattr(executor_module, "log_eval_rollout_data", lambda *args: {})
    store = FakeObjectStore()
    monkeypatch.setattr(object_store, "_INSTANCE", store)
    return executor, store


@pytest.mark.parametrize("delayed", [False, True])
async def test_actual_conversion_retains_all_eval_rows_masks_probs_and_original_dump(monkeypatch, tmp_path, delayed):
    samples = [
        make_sample(
            index=i,
            tokens=[10, 11, 20 + i, 30 + i],
            response_length=2,
            loss_mask=[1, 0],
            rollout_log_probs=[-0.1 - i, float("nan")],
            teacher_log_probs=[-0.2 - i, -1.0],
            metadata={"source_id": f"source-{i}", "prefix_length": 2},
            weight_versions=[
                WeightVersionsPerCall(
                    spans=[WeightVersionSpan(version="20", abs_start=2, abs_end=4)],
                    prefill_spans=[WeightVersionSpan(version="20", abs_start=0, abs_end=2)],
                    output_start=2,
                    prompt_tokens=2,
                )
            ],
        )
        for i in range(5)
    ]
    original = deepcopy(samples)
    executor, store = _executor(
        monkeypatch,
        data={"monitor": {"samples": samples, "rewards": [s.reward for s in samples]}},
        delay_split_train_data_by_dp=delayed,
        save_debug_rollout_data=str(tmp_path / "{rollout_id}.pt"),
    )

    packs = await executor.eval(19, return_train_data=True)

    assert packs["monitor"].sample_indices == list(range(5))
    shards = [store.get(ref).value for ref in packs["monitor"].data_refs]
    assert sum(len(shard["tokens"]) for shard in shards) == 5
    actual = {index: (shard, pos) for shard in shards for pos, index in enumerate(shard["sample_indices"])}
    for index, sample in enumerate(samples):
        shard, pos = actual[index]
        assert shard["tokens"][pos] == sample.tokens
        assert shard["loss_masks"][pos] == [1, 0]
        assert shard["rollout_log_probs"][pos][0] == sample.rollout_log_probs[0]
        assert shard["teacher_log_probs"][pos] == sample.teacher_log_probs
        assert shard["weight_versions"][pos] == [sample.weight_versions[0].to_dict()]
    assert samples == original
    dump = torch.load(tmp_path / "eval_19.pt", weights_only=False)
    assert dump["samples"][0]["metadata"]["source_id"] == "source-0"
    assert dump["metadata"]["eval_dataset_names"] == ["monitor"] * 5
    assert executor.last_get_rollout_id_of_model_id == {None: 19}
    assert list(executor._unreleased_store_refs) == [19]
    executor.get.assert_not_awaited()
    executor.release.assert_not_awaited()
    assert executor._train_parallel_configs_of_model_id[None].supports_precomputed_schedule


async def test_disabled_eval_never_converts_or_allocates(monkeypatch):
    executor, store = _executor(monkeypatch, data={})
    monkeypatch.setattr(executor, "_convert_eval_train_data", lambda data: pytest.fail("unexpected conversion"))

    assert await executor.eval(0) is None
    assert store._values == {}


async def test_conversion_failure_is_soft_and_partial_pack_refs_are_cleaned(monkeypatch, caplog):
    samples = [make_sample(index=i) for i in range(2)]
    executor, store = _executor(monkeypatch, data={"monitor": {"samples": samples}})
    put = store.put

    def fail_second_put(*args, **kwargs):
        if store._values:
            raise RuntimeError("object store put failed")
        return put(*args, **kwargs)

    monkeypatch.setattr(store, "put", fail_second_put)
    assert await executor.eval(0, return_train_data=True) == {}
    assert store._values == {}
    assert "unverified: conversion failed" in caplog.text


async def test_native_eval_dump_errors_still_raise(monkeypatch):
    executor, _ = _executor(monkeypatch, data={})

    def fail_dump(*args, **kwargs):
        raise OSError("native rollout dump failed")

    monkeypatch.setattr(executor_module, "save_debug_rollout_data", fail_dump)
    with pytest.raises(OSError, match="native rollout dump failed"):
        await executor.eval(0, return_train_data=True)


@pytest.mark.parametrize("sharded", [False, True])
def test_eval_rpc_return_keeps_nested_pack_and_reference_types(sharded):
    store = FakeObjectStore()
    refs = [store.put({"tokens": [[1, 2]]}) for _ in range(2)]
    packs = {"monitor": executor_module.RolloutDataPack(sample_indices=[0, 1], data_ref=refs if sharded else refs[0])}
    serializer = collect_rpc_method_specs(RolloutExecutor)["eval"].serializer

    restored = serializer.decode_result(serializer.encode_result(packs))

    assert restored == packs
    assert isinstance(restored["monitor"], executor_module.RolloutDataPack)
    assert all(type(ref) is type(refs[0]) for ref in restored["monitor"].data_refs)
    assert serializer.decode_result(serializer.encode_result(None)) is None
