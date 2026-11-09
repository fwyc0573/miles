"""`Sample.max_response_len` lowers `max_new_tokens` for that sample only, in both rollout paths."""

import json
from contextlib import nullcontext
from types import SimpleNamespace

import pytest
from tests.fast import test_swe_input_limits
from tests.fast.ray.rollout.conftest import make_args
from tests.fast.rollout.inference_rollout.conftest import make_state

from miles.rollout import sglang_rollout
from miles.rollout.base_types import GenerateFnOutput
from miles.rollout.generate_utils.generate_endpoint_utils import apply_sample_max_response_len
from miles.rollout.inference_rollout import inference_rollout_common as common
from miles.utils.types import Sample

_RUN_PARAMS = {"temperature": 1.0, "max_new_tokens": 100}
adapter_factory = test_swe_input_limits.adapter_factory


class TestApplySampleMaxResponseLen:
    def test_unset_keeps_the_run_params(self):
        assert apply_sample_max_response_len(_RUN_PARAMS, Sample(prompt="p")) is _RUN_PARAMS

    @pytest.mark.parametrize("limit", [1, 40, 100])
    def test_a_limit_up_to_the_run_value_is_applied(self, limit):
        params = apply_sample_max_response_len(_RUN_PARAMS, Sample(prompt="p", max_response_len=limit))

        assert params == {"temperature": 1.0, "max_new_tokens": limit}
        assert _RUN_PARAMS["max_new_tokens"] == 100

    def test_a_run_without_a_bound_accepts_any_positive_limit(self):
        unbounded = {"temperature": 1.0, "max_new_tokens": None}
        params = apply_sample_max_response_len(unbounded, Sample(prompt="p", max_response_len=10**6))

        assert params["max_new_tokens"] == 10**6
        with pytest.raises(ValueError, match="must be an int"):
            apply_sample_max_response_len(unbounded, Sample(prompt="p", max_response_len=0))

    @pytest.mark.parametrize("limit", [101, 0, -1, True, 40.0, "40"])
    def test_a_limit_outside_the_run_bound_is_rejected(self, limit):
        with pytest.raises(ValueError, match=r"must be an int in \[1, 100\]"):
            apply_sample_max_response_len(_RUN_PARAMS, Sample(prompt="p", index=3, max_response_len=limit))


class _RecordingGenerate:
    def __init__(self) -> None:
        self.max_new_tokens: list[int] = []

    async def __call__(self, input):
        self.max_new_tokens.append(input.sampling_params["max_new_tokens"])
        return GenerateFnOutput(samples=input.sample)


@pytest.mark.parametrize(("limit", "expected"), [(None, 100), (40, 40)])
async def test_inference_rollout_passes_the_sample_budget(limit, expected):
    generate = _RecordingGenerate()
    run_params = dict(_RUN_PARAMS)

    await common.generate_and_rm(
        make_state(generate), Sample(index=1, max_response_len=limit), sampling_params=run_params
    )

    assert generate.max_new_tokens == [expected]
    assert run_params == _RUN_PARAMS


@pytest.mark.parametrize(("limit", "expected"), [(None, 100), (40, 40)])
async def test_legacy_rollout_passes_the_sample_budget(monkeypatch, limit, expected):
    generate = _RecordingGenerate()
    run_params = dict(_RUN_PARAMS)
    args = make_args(
        partial_rollout=False,
        mask_offpolicy_in_partial_rollout=False,
        group_rm=True,
        custom_generate_function_path="recording",
    )
    legacy_state = SimpleNamespace(aborted=False, semaphore=nullcontext(), dp_rank_context=nullcontext)
    monkeypatch.setattr(sglang_rollout, "GenerateState", lambda _args: legacy_state)
    monkeypatch.setattr(sglang_rollout, "load_generate_function", lambda _path: generate)

    await sglang_rollout.generate_and_rm(args, Sample(index=1, max_response_len=limit), run_params)

    assert generate.max_new_tokens == [expected]
    assert run_params == _RUN_PARAMS


def test_the_budget_survives_retry_and_serialization():
    sample = Sample(prompt="p", max_response_len=40)
    sample.reset_for_retry()

    assert sample.max_response_len == 40
    assert Sample.from_dict(sample.to_dict()).max_response_len == 40


@pytest.fixture
def native_swe_source(adapter_factory):
    """Reuse the parent adapter fixture's pinned-module/source/mixer boundary."""

    def build(lengths, *, prompt_limit=114688, response_limit=16384):
        _, source = adapter_factory(lengths, prompt_limit=prompt_limit, response_limit=response_limit)
        return source

    return build


async def test_native_swe_prompt_limit_preserves_slots_and_generation_budget(native_swe_source, caplog, tmp_path):
    source = native_swe_source([64, 114689, 114688, 128])
    with caplog.at_level("INFO"):
        samples = [group[0] for group in source.get_samples(3)]
    assert [sample.metadata["source"]["prompt_token_count"] for sample in samples] == [64, 114688, 128]
    assert [sample.metadata["source"]["source_item_index"] for sample in samples] == [0, 2, 3]
    assert [sample.index for sample in samples] == [0, 1, 2]
    assert [sample.group_index for sample in samples] == [0, 1, 2]
    assert [sample.max_seq_len for sample in samples] == [131072] * 3
    assert [sample.max_response_len for sample in samples] == [16384] * 3
    assert [len(source.tokenizer.encode(sample.prompt)) for sample in samples] == [64, 114688, 128]
    assert source.skipped_overlength == 1
    assert source.draws == 4
    assert [sample.metadata["source"]["draw_index"] for sample in samples] == [0, 2, 3]
    assert source.finished_conversations == ("source:0", "source:1", "source:2", "source:3")
    rejects = [
        json.loads(record.message.split(" ", 1)[1])
        for record in caplog.records
        if record.message.startswith("NATIVE_SWE_INPUT_REJECT ")
    ]
    assert len(rejects) == 1
    assert rejects[0]["reason"] == "prompt_above_prompt_limit"
    assert rejects[0]["source"]["prompt_token_count"] == 114689
    assert rejects[0]["rollout_max_prompt_len"] == 114688
    assert rejects[0]["rollout_max_context_len"] == 131072

    generate = _RecordingGenerate()
    run_params = {"temperature": 1.0, "max_new_tokens": 16384}
    for sample in samples:
        await common.generate_and_rm(make_state(generate), sample, sampling_params=run_params, evaluation=True)
    assert generate.max_new_tokens == [16384] * 3
    assert run_params == {"temperature": 1.0, "max_new_tokens": 16384}

    source.save(tmp_path / "receipt")
    receipt = json.loads((tmp_path / "receipt" / "native_swe_inputs.json").read_text())
    assert receipt["accepted_turns"] == 3 and receipt["skipped_overlength"] == 1
    assert receipt["identity"]["rollout_max_context_len"] == 131072
    assert receipt["identity"]["rollout_max_prompt_len"] == 114688
    assert receipt["identity"]["rollout_max_response_len"] == 16384
    assert receipt["emitted_turns"] == 4
    assert receipt["identity"]["length_reject"] == "prompt_token_count > rollout_max_prompt_len"
    assert receipt["identity"]["generation_budget"] == (
        "min(rollout_max_response_len, rollout_max_context_len - prompt_token_count)"
    )


@pytest.mark.parametrize("response_limit,expected", [(16384, [16383, 1, 16384]), (131072, [16383, 1, 131008])])
async def test_native_swe_explicit_prompt_limit_keeps_remaining_context_budget(
    native_swe_source,
    caplog,
    response_limit,
    expected,
):
    source = native_swe_source([114689, 131071, 131072, 64], prompt_limit=131071, response_limit=response_limit)
    with caplog.at_level("INFO"):
        samples = [group[0] for group in source.get_samples(3)]
    assert [sample.metadata["source"]["source_item_index"] for sample in samples] == [0, 1, 3]
    assert [sample.metadata["source"]["prompt_token_count"] for sample in samples] == [114689, 131071, 64]
    assert [sample.index for sample in samples] == [0, 1, 2]
    assert [sample.group_index for sample in samples] == [0, 1, 2]
    assert [sample.max_seq_len for sample in samples] == [131072] * 3
    assert [sample.max_response_len for sample in samples] == expected
    assert source.skipped_overlength == 1
    assert source.identity["rollout_max_prompt_len"] == 131071
    rejects = [
        json.loads(record.message.split(" ", 1)[1])
        for record in caplog.records
        if record.message.startswith("NATIVE_SWE_INPUT_REJECT ")
    ]
    assert len(rejects) == 1
    assert rejects[0]["reason"] == "prompt_above_prompt_limit"
    assert rejects[0]["source"]["prompt_token_count"] == 131072
    assert rejects[0]["rollout_max_prompt_len"] == 131071

    generate = _RecordingGenerate()
    run_params = {"temperature": 1.0, "max_new_tokens": response_limit}
    for sample in samples:
        await common.generate_and_rm(make_state(generate), sample, sampling_params=run_params, evaluation=True)
    assert generate.max_new_tokens == expected
    assert run_params == {"temperature": 1.0, "max_new_tokens": response_limit}


@pytest.mark.parametrize(
    "prompt_length,prompt_limit,expected",
    [(4366, 114688, 16384), (114687, 114688, 16384), (114688, 114688, 16384), (131071, 131071, 1)],
)
async def test_swe_replay_preserves_source_budget_in_native_request(
    native_swe_source, monkeypatch, tmp_path, prompt_length, prompt_limit, expected
):
    from tests.fast.test_qwen35_sample_lifecycle import _native_response
    from tests.fast.test_swe_replay import _typed_swe_config
    from tests.manual.agent_opd.swe_replay import SweReplay

    from miles.rollout import on_policy_distillation as opd
    from miles.rollout.base_types import RolloutFnConstructorInput
    from miles.rollout.generate_hub import single_turn
    from miles.utils.args.custom_function import CustomFunctionConfig
    from miles.utils.args.custom_view import compute_custom_function_config
    from miles.utils.args.runtime import RolloutConfig

    source = native_swe_source([prompt_length], prompt_limit=prompt_limit)
    candidate = source.get_samples(1)[0][0]
    assert candidate.max_response_len == expected
    tokenizer = SimpleNamespace(encode=source.tokenizer.encode, decode=lambda ids, **kwargs: "fresh completion")
    monkeypatch.setattr(common, "load_tokenizer", lambda *args, **kwargs: tokenizer)
    monkeypatch.setattr(common, "load_processor", lambda *args, **kwargs: None)

    rollout = RolloutConfig.slice_from(_typed_swe_config("r256", run_kind="smoke"))
    replay_config = rollout.rollout_function_path.config.model_copy(
        update={"swe_evidence_dir": str(tmp_path / "replay")}
    )
    rollout = rollout.model_copy(
        update={
            "rollout_function_path": rollout.rollout_function_path.model_copy(update={"config": replay_config}),
            "custom_rm_path": rollout.custom_rm_path.model_copy(update={"config": replay_config}),
            "custom_generate_function_path": CustomFunctionConfig(
                path="tests.manual.agent_opd.qwen_alignment.generate"
            ),
            "rollout_max_context_len": 131072,
            "rollout_max_prompt_len": prompt_limit,
            "rollout_max_response_len": 16384,
            "rollout_seed": 1729,
        }
    )
    args = compute_custom_function_config(rollout, rollout.rollout_function_path)
    replay = SweReplay(RolloutFnConstructorInput(args=args, data_source=source))
    requests = []

    async def student_post(url, payload, **kwargs):
        requests.append(payload)
        response = _native_response()
        info = response["meta_info"]
        info["prompt_tokens"] = len(payload["input_ids"])
        info["prefill_weight_versions"][0]["end"] = info["prompt_tokens"]
        info["output_token_logprobs"] = info["output_token_logprobs"][: payload["sampling_params"]["max_new_tokens"]]
        info["weight_versions"][0]["end"] = len(info["output_token_logprobs"])
        return response

    async def teacher_post(url, payload, **kwargs):
        tokens = payload["input_ids"][prompt_length:]
        return {"meta_info": {"input_token_logprobs": [[None, 0], *[[-0.2, token] for token in tokens]]}}

    monkeypatch.setattr(single_turn, "post", student_post)
    monkeypatch.setattr(opd, "_post_json", teacher_post)
    generated = await replay._generate(candidate)

    assert len(requests) == 1
    request = requests[0]
    assert request["sampling_params"]["max_new_tokens"] == expected
    assert len(request["input_ids"]) == prompt_length
    assert len(request["input_ids"]) + request["sampling_params"]["max_new_tokens"] <= 131072
    assert (
        request["sampling_params"]["sampling_seed"]
        == generated.metadata["swe_sampling_seed"]
        == args.rollout_seed
        == 1729
    )
    assert generated is candidate and generated.max_response_len == expected
    assert replay.native_state.sampling_params["max_new_tokens"] == 16384
    assert "sampling_seed" not in replay.native_state.sampling_params
    assert request["sampling_params"] == {
        **replay.native_state.sampling_params,
        "max_new_tokens": expected,
        "sampling_seed": args.rollout_seed,
    }
