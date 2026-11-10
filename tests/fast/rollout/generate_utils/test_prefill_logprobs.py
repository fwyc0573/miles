import base64
import io
from types import SimpleNamespace

import pytest
from PIL import Image
from tests.fast.fixtures.args_fixtures import sglang_router_args
from tests.fast.fixtures.sglang_config_fixtures import make_sglang_config

from miles.rollout.generate_utils import prefill_logprobs
from miles.utils.types import Sample


@pytest.mark.parametrize("tokens,response_length,start,scored_items,expected", [
    ([10, 20], 1, 0, [(None, 10), (-0.1, 20)], [-0.1]),
    ([10, 20, 21, 22], 3, 0, [(None, 10), (-0.1, 20), (-0.2, 21), (-0.3, 22)], [-0.1, -0.2, -0.3]),
    ([10, 11, 12, 20], 1, 2, [(None, 12), (-0.1, 20)], [-0.1]),
    ([10, 11, 12, 20, 21, 22], 3, 2, [(None, 12), (-0.1, 20), (-0.2, 21), (-0.3, 22)], [-0.1, -0.2, -0.3]),
])
@pytest.mark.asyncio
async def test_recompute_rollout_logprobs_via_prefill_uses_response_tail(monkeypatch, tokens, response_length, start, scored_items, expected):
    sample = Sample(
        tokens=tokens,
        response_length=response_length,
        rollout_log_probs=[-9.0] * response_length,
        status=Sample.Status.COMPLETED,
    )
    args = SimpleNamespace(recompute_logprobs_via_prefill=True, lora_rank=0, lora_adapter_path=None)
    seen = {}

    async def fake_post(url, payload, headers=None):
        seen["url"] = url
        seen["payload"] = payload
        seen["headers"] = headers
        return {"meta_info": {"input_token_logprobs": scored_items}}

    monkeypatch.setattr(prefill_logprobs, "post", fake_post)

    await prefill_logprobs.recompute_rollout_logprobs_via_prefill(
        args,
        sample,
        url="http://localhost/generate",
        sampling_params={"temperature": 1, "max_new_tokens": 128},
        headers={"X-Test": "1"},
    )

    assert sample.rollout_log_probs == expected
    assert sample.metadata["rollout_log_probs_source"] == "sglang_prefill_recompute"
    assert seen["url"] == "http://localhost/generate"
    assert seen["headers"] == {"X-Test": "1"}
    assert seen["payload"]["input_ids"] == sample.tokens
    assert seen["payload"]["return_logprob"] is True
    assert seen["payload"]["logprob_start_len"] == start
    assert seen["payload"]["sampling_params"]["max_new_tokens"] == 0
    assert seen["payload"]["sampling_params"]["temperature"] == 0


@pytest.mark.parametrize("lora_rank,adapter_path,train_only,expected_lora", [
    (0, None, False, None),
    (8, None, False, "miles_lora"),
    (0, "adapter-on-disk", False, "miles_lora"),
    (8, None, True, None),
])
@pytest.mark.asyncio
async def test_prefill_scoring_retains_adapter_images_and_request_sampling(monkeypatch, lora_rank, adapter_path, train_only, expected_lora):
    image = Image.new("L", (2, 2), color=63)
    sample = Sample(tokens=[10, 11, 20], response_length=1, status=Sample.Status.COMPLETED,
                    multimodal_inputs={"images": [image]})
    args = SimpleNamespace(recompute_logprobs_via_prefill=True, lora_rank=lora_rank,
                           lora_adapter_path=adapter_path, lora_train_only=train_only)
    sampling_params = {"temperature": 1, "max_new_tokens": 128, "skip_special_tokens": True,
                       "top_p": 0.8, "stop": ["done"], "repetition_penalty": 1.1}
    original_sampling_params = dict(sampling_params)
    seen = {}

    async def post(url, payload, headers=None):
        seen.update(payload)
        return {"meta_info": {"input_token_logprobs": [(None, 11), (-0.1, 20)]}}

    monkeypatch.setattr(prefill_logprobs, "post", post)
    await prefill_logprobs.recompute_rollout_logprobs_via_prefill(
        args, sample, url="http://localhost/generate", sampling_params=sampling_params,
    )

    assert seen["sampling_params"] == {
        "temperature": 0, "max_new_tokens": 0, "skip_special_tokens": False,
        "top_p": 0.8, "stop": ["done"], "repetition_penalty": 1.1,
    }
    assert sampling_params == original_sampling_params
    assert seen.get("lora_path") == expected_lora
    if expected_lora is None:
        assert "lora_path" not in seen
    assert seen["logprob_start_len"] == 1
    assert seen["return_logprob"] is True
    assert set(seen) == {"input_ids", "sampling_params", "return_logprob", "logprob_start_len", "image_data"} | ({"lora_path"} if expected_lora else set())
    image_prefix, encoded_image = seen["image_data"][0].split(",", 1)
    assert image_prefix == "data:image/png;base64"
    decoded = Image.open(io.BytesIO(base64.b64decode(encoded_image)))
    assert decoded.mode == "RGB" and decoded.size == (2, 2)
    assert decoded.getpixel((0, 0)) == (63, 63, 63)
    assert sample.rollout_log_probs == [-0.1]


@pytest.mark.parametrize("tokens,response_length", [([20], 1), ([20], 2), ([], 0)])
def test_prefill_scoring_keeps_missing_prompt_error(tokens, response_length):
    sample = Sample(tokens=tokens, response_length=response_length, status=Sample.Status.COMPLETED)
    args = SimpleNamespace(lora_rank=0, lora_adapter_path=None)

    with pytest.raises(ValueError, match="Cannot recompute rollout logprobs via prefill without at least one prompt token"):
        prefill_logprobs._build_prefill_scoring_payload(args, sample, {})


@pytest.mark.parametrize("response_length", [-1, 3, 4])
def test_response_scoring_rejects_invalid_lengths(response_length):
    from miles.rollout.on_policy_distillation import _score_payload

    with pytest.raises(ValueError, match="nonnegative response_length and at least one prompt token"):
        _score_payload([10, 20, 30], response_length=response_length)


@pytest.mark.parametrize("selection", [
    {},
    {"top_k": 2, "token_ids": [20, 30]},
    {"top_k": 2, "token_ids_positions": [[], [], [], [20], [30]]},
])
@pytest.mark.parametrize("scope", [{}, {"response_length": None}])
def test_full_input_scoring_keeps_default_topk_position_contract(selection, scope):
    from miles.rollout.on_policy_distillation import _score_payload

    payload = _score_payload([10, 11, 12, 20, 30], extra_key="student-key", **selection, **scope)
    expected = {
        "input_ids": [10, 11, 12, 20, 30],
        "sampling_params": {"temperature": 0, "max_new_tokens": 0, "skip_special_tokens": False},
        "return_logprob": True,
        "logprob_start_len": 0,
        "extra_key": "student-key",
    }
    if selection:
        expected["top_logprobs_num"] = 2
        if "token_ids_positions" in selection:
            expected["token_ids_logprob_positions"] = [[], [], [], [20], [30]]
        else:
            expected["token_ids_logprob"] = [20, 30]
    assert payload == expected


@pytest.mark.parametrize("scores,error", [
    ([(None, 11), (-0.1, 999)], "token alignment mismatch"),
    ([(None, 11)], "token alignment mismatch"),
    ([(None, 20)], "None for a response-token logprob"),
    ([], "did not include input_token_logprobs"),
])
@pytest.mark.asyncio
async def test_recompute_rollout_logprobs_via_prefill_checks_token_alignment(monkeypatch, scores, error):
    sample = Sample(tokens=[10, 11, 20], response_length=1, status=Sample.Status.COMPLETED)
    args = SimpleNamespace(recompute_logprobs_via_prefill=True, lora_rank=0, lora_adapter_path=None)

    async def fake_post(url, payload, headers=None):
        return {"meta_info": {"input_token_logprobs": scores}}

    monkeypatch.setattr(prefill_logprobs, "post", fake_post)

    with pytest.raises(ValueError, match=error):
        await prefill_logprobs.recompute_rollout_logprobs_via_prefill(
            args,
            sample,
            url="http://localhost/generate",
            sampling_params={},
        )


@pytest.mark.asyncio
async def test_recompute_samples_flushes_each_batch_and_batches_prefill_score(monkeypatch):
    samples = [
        Sample(tokens=[10, 11, 20], response_length=1, status=Sample.Status.COMPLETED),
        Sample(tokens=[10, 11, 21], response_length=1, status=Sample.Status.COMPLETED),
    ]
    args = SimpleNamespace(
        recompute_logprobs_via_prefill=True,
        lora_rank=0,
        lora_adapter_path=None,
        **sglang_router_args("round_robin"),
        sglang=make_sglang_config(),
    )
    calls = []

    async def fake_post(url, payload, action="post", headers=None):
        calls.append((url, payload, action, headers))
        if url.endswith("/flush_cache"):
            return {}
        return [
            {"meta_info": {"input_token_logprobs": [(None, 11), (-float(tokens[-1]), tokens[-1])]}}
            for tokens in payload["input_ids"]
        ]

    monkeypatch.setattr(prefill_logprobs, "post", fake_post)

    await prefill_logprobs.recompute_samples_rollout_logprobs_via_prefill(
        args,
        samples,
        url="http://localhost/generate",
        sampling_params={"max_new_tokens": 32},
    )

    assert [sample.rollout_log_probs for sample in samples] == [[-20.0], [-21.0]]
    assert [call[0] for call in calls] == [
        "http://localhost/flush_cache",
        "http://localhost/generate",
    ]
    assert [call[2] for call in calls] == ["post", "post"]
    assert calls[1][1]["input_ids"] == [[10, 11, 20], [10, 11, 21]]
    assert calls[1][1]["logprob_start_len"] == 1


@pytest.mark.asyncio
async def test_recompute_samples_batches_by_logprob_start_len(monkeypatch):
    samples = [
        Sample(tokens=[10, 11, 20], response_length=1, status=Sample.Status.COMPLETED),
        Sample(tokens=[10, 11, 12, 21], response_length=1, status=Sample.Status.COMPLETED),
        Sample(tokens=[10, 11, 22], response_length=1, status=Sample.Status.COMPLETED),
    ]
    args = SimpleNamespace(
        recompute_logprobs_via_prefill=True,
        lora_rank=0,
        lora_adapter_path=None,
        **sglang_router_args("round_robin"),
        sglang=make_sglang_config(),
    )
    calls = []

    async def fake_post(url, payload, action="post", headers=None):
        calls.append((url, payload, action, headers))
        if url.endswith("/flush_cache"):
            return {}
        return [
            {
                "meta_info": {
                    "input_token_logprobs": [
                        (None, tokens[-2]),
                        (-float(tokens[-1]), tokens[-1]),
                    ]
                }
            }
            for tokens in payload["input_ids"]
        ]

    monkeypatch.setattr(prefill_logprobs, "post", fake_post)

    await prefill_logprobs.recompute_samples_rollout_logprobs_via_prefill(
        args,
        samples,
        url="http://localhost/generate",
        sampling_params={"max_new_tokens": 32},
    )

    assert [sample.rollout_log_probs for sample in samples] == [
        [-20.0],
        [-21.0],
        [-22.0],
    ]
    assert [call[0] for call in calls] == [
        "http://localhost/flush_cache",
        "http://localhost/generate",
        "http://localhost/flush_cache",
        "http://localhost/generate",
    ]
    assert calls[1][1]["logprob_start_len"] == 1
    assert calls[1][1]["input_ids"] == [[10, 11, 20], [10, 11, 22]]
    assert calls[3][1]["logprob_start_len"] == 2
    assert calls[3][1]["input_ids"] == [[10, 11, 12, 21]]
