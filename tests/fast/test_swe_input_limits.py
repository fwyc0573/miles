"""Exercise the SWE adapter and native request builder at the length-limit boundary."""

from types import ModuleType, SimpleNamespace

import pytest
from tests.fast.ray.rollout.conftest import make_rollout_config
from tests.manual.agent_opd import swe_inputs

from miles.rollout.generate_utils.generate_endpoint_utils import (
    apply_sample_max_response_len,
    compute_prompt_ids_from_sample,
    compute_request_payload,
)
from miles.utils.args.custom_function import CustomFunctionConfig
from miles.utils.args.custom_view import compute_custom_function_config
from miles.utils.args.runtime import RolloutConfig


class _TokenCountTokenizer:
    """Use an explicit token count instead of estimating Qwen tokenization."""

    def apply_chat_template(self, messages, **kwargs):
        return messages[0]["content"]

    def encode(self, prompt, **kwargs):
        return list(range(int(prompt)))


@pytest.fixture
def adapter_factory(tmp_path, monkeypatch):
    """Inject the external Steptron stream; do not replace the adapter or request builder.

    Real pinned-source selection and mixer ordering are covered by check_swe_inputs.
    This portable fixture exposes only the external loader protocol the adapter uses.
    """
    source_path = tmp_path / "source.json"
    source_path.write_text("[]")
    for asset in ("tokenizer.json", "tokenizer_config.json", "template.jinja"):
        (tmp_path / asset).write_text("{}")
    source_file = {"path": str(source_path), "local_path": str(source_path), "sha256": "source"}
    population = swe_inputs.SWESourcePopulation((source_file,), {}, "manifest")
    adapters = []

    def create(prompt_lengths, *, prompt_limit=114688, response_limit=16384, context_limit=131072):
        items = iter([
            {"conversation": [
                {"role": "user", "content": str(length)},
                {"role": "assistant", "ground_truth": {
                    "data_path": str(source_path), "source_item_index": index, "source_row_index": index,
                    "source_message_count": 2, "assistant_turn_index": 1, "assistant_turn_ordinal": 1,
                    "num_context_messages": 1,
                }},
            ]}
            for index, length in enumerate(prompt_lengths)
        ])

        class TurnSource:
            def __init__(self, filelist, **kwargs):
                self.cursor = SimpleNamespace(epoch=0)
                self.active_remaining_turns = 0

        class BlockMixer:
            def __init__(self, sources, weights, *, trajectory_block_turns):
                self.emitted_turns = [0]

            def __next__(self):
                item = next(items)
                self.emitted_turns[0] += 1
                return item

            def close(self):
                pass

        native = ModuleType(swe_inputs.BASE_LOADER)
        native.OnlineTrajectoryTurnSource = TurnSource
        native.TurnBalancedTrajectoryBlockMixer = BlockMixer
        monkeypatch.setattr(swe_inputs, "load_pinned_modules", lambda root, pins: {swe_inputs.BASE_LOADER: native})
        hook = CustomFunctionConfig.model_validate({
            "path": "tests.manual.agent_opd.swe_inputs.NativeSWEDataSource",
            "config": {
                "swe_source_root": str(tmp_path), "swe_source_manifest": str(tmp_path / "manifest.json"),
                "swe_steptron_root": str(tmp_path), "swe_module_sha256": {swe_inputs.BASE_LOADER: "pin"},
                "swe_turn_source": "all_assistants", "swe_active_conversations": 1, "swe_block_turns": 8,
            },
        })
        rollout = make_rollout_config(
            hf_checkpoint=str(tmp_path), chat_template_path=str(tmp_path / "template.jinja"),
            apply_chat_template_kwargs={"preserve_thinking": True, "enable_thinking": True},
            n_samples_per_prompt=1, rollout_max_context_len=context_limit,
            rollout_max_prompt_len=prompt_limit, rollout_max_response_len=response_limit,
            data_source_path=hook,
        )
        adapter = swe_inputs.NativeSWEDataSource(
            compute_custom_function_config(rollout, hook), tokenizer=_TokenCountTokenizer(), population=population,
        )
        adapters.append(adapter)
        return rollout, adapter

    yield create
    for adapter in adapters:
        adapter.close()


def _request(rollout, adapter, sample):
    state = SimpleNamespace(processor=None, tokenizer=adapter.tokenizer)
    prompt_ids = compute_prompt_ids_from_sample(state, sample)
    sampling = apply_sample_max_response_len({"max_new_tokens": rollout.rollout_max_response_len}, sample)
    payload, halt_status = compute_request_payload(rollout, prompt_ids, sampling)
    assert halt_status is None
    return payload


def test_112k_prompt_is_inclusive_and_rejection_does_not_consume_a_slot(adapter_factory):
    rollout, adapter = adapter_factory([114688, 114689, 32])
    assert isinstance(rollout, RolloutConfig)
    boundary, short = [group[0] for group in adapter.get_samples(2)]

    assert [sample.metadata["source"]["prompt_token_count"] for sample in (boundary, short)] == [114688, 32]
    assert [sample.index for sample in (boundary, short)] == [0, 1]
    assert [sample.group_index for sample in (boundary, short)] == [0, 1]
    assert [sample.metadata["source"]["draw_index"] for sample in (boundary, short)] == [0, 2]
    assert adapter.skipped_overlength == 1 and adapter.draws == 3
    assert adapter.finished_conversations == ("source:0", "source:1", "source:2")
    assert boundary.max_seq_len == short.max_seq_len == 131072
    assert boundary.max_response_len == short.max_response_len == 16384
    assert {name: adapter.identity[name] for name in (
        "rollout_max_context_len", "rollout_max_prompt_len", "rollout_max_response_len",
    )} == {"rollout_max_context_len": 131072, "rollout_max_prompt_len": 114688, "rollout_max_response_len": 16384}
    boundary_payload = _request(rollout, adapter, boundary)
    short_payload = _request(rollout, adapter, short)
    assert boundary_payload["sampling_params"]["max_new_tokens"] == 16384
    assert len(boundary_payload["input_ids"]) + boundary_payload["sampling_params"]["max_new_tokens"] == 131072
    assert short_payload["sampling_params"]["max_new_tokens"] == 16384
    assert rollout.rollout_max_response_len == 16384


@pytest.mark.parametrize(("prompt_length", "expected_completion"), [(131000, 72), (131071, 1)])
def test_completion_is_reduced_when_the_context_has_less_than_16k_left(
    adapter_factory, prompt_length, expected_completion,
):
    rollout, adapter = adapter_factory([prompt_length], prompt_limit=131071)
    sample = adapter.get_samples(1)[0][0]
    assert sample.max_response_len == expected_completion
    payload = _request(rollout, adapter, sample)
    assert payload["sampling_params"]["max_new_tokens"] == expected_completion
    assert len(payload["input_ids"]) + expected_completion == 131072


@pytest.mark.parametrize("prompt_limit", [None, 0, 131072])
def test_prompt_limit_must_arrive_normalized_before_consuming_the_stream(adapter_factory, prompt_limit):
    with pytest.raises(ValueError, match="rollout_max_prompt_len"):
        adapter_factory([32], prompt_limit=prompt_limit)


@pytest.mark.parametrize("response_limit", [None, 0])
def test_response_limit_must_be_positive_before_consuming_the_stream(adapter_factory, response_limit):
    with pytest.raises(ValueError, match="rollout_max_response_len"):
        adapter_factory([32], response_limit=response_limit)
