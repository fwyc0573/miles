"""Real tiny hybrid-model regressions for the Miles Qwen text export contract."""

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch
from safetensors.torch import load_file, save_file
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoTokenizer,
    Qwen2Tokenizer,
    Qwen3_5Config,
    Qwen3_5ForConditionalGeneration,
    Qwen3_5TextConfig,
    Qwen3_5VisionConfig,
)

from miles.backends.training_utils.weight_update import snapshot_publisher
from miles.utils.args.custom_function import CustomFunctionConfig
from miles.utils.args.custom_view import ImmutableNamespace, compute_custom_function_config
from miles.utils.function_registry import load_function
from tests.manual.agent_opd import qwen_export


@pytest.fixture(autouse=True)
def single_thread_cpu():
    threads = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(threads)


def _reference(tied=True, dtype=torch.float32):
    torch.manual_seed(42)
    text = Qwen3_5TextConfig(
        vocab_size=16,
        hidden_size=16,
        intermediate_size=32,
        num_hidden_layers=2,
        num_attention_heads=2,
        num_key_value_heads=1,
        head_dim=8,
        linear_key_head_dim=4,
        linear_value_head_dim=4,
        linear_num_key_heads=2,
        linear_num_value_heads=2,
        linear_conv_kernel_dim=2,
        layer_types=["linear_attention", "full_attention"],
        max_position_embeddings=64,
        rope_parameters={
            "rope_type": "default",
            "rope_theta": 10000,
            "partial_rotary_factor": 0.5,
            "mrope_section": [1, 1, 0],
            "mrope_interleaved": True,
        },
        tie_word_embeddings=tied,
        eos_token_id=15,
        pad_token_id=0,
        dtype=dtype,
        mtp_num_hidden_layers=1,
        mtp_use_dedicated_embeddings=False,
    )
    vision = Qwen3_5VisionConfig(
        depth=1,
        hidden_size=16,
        intermediate_size=32,
        num_heads=2,
        out_hidden_size=16,
        num_position_embeddings=16,
        patch_size=2,
        temporal_patch_size=1,
    )
    config = Qwen3_5Config(text_config=text, vision_config=vision, tie_word_embeddings=tied)
    return Qwen3_5ForConditionalGeneration(config).to(dtype).eval()


def _write_export(tmp_path: Path, monkeypatch, *, tied=True, dtype=torch.float32, omit_head=False):
    source, path = tmp_path / "source", tmp_path / "export"
    source.mkdir()
    path.mkdir()
    reference = _reference(tied=tied, dtype=dtype)
    reference.save_pretrained(source)
    tokenizer = Qwen2Tokenizer(
        vocab={"t0": 0, "a": 1, "b": 2, "c": 3, **{f"t{i}": i for i in range(4, 16)}},
        merges=[],
        unk_token="t0",
        eos_token="t15",
        pad_token="t0",
    )
    tokenizer.chat_template = (
        "{% for message in messages %}{% if message.content is string %}{{ message.content }}"
        "{% else %}{% for part in message.content %}{{ part.text }}{% endfor %}{% endif %}{% endfor %}"
    )
    tokenizer.save_pretrained(source)
    (source / "preprocessor_config.json").write_text('{"image_processor_type": "Qwen3VLImageProcessor"}')

    def buckets(weights):
        decoder = [(name, tensor) for name, tensor in weights.items() if not name.startswith("model.visual.")]
        for start in range(0, len(decoder), 7):
            yield decoder[start : start + 7]
        yield [(name, tensor) for name, tensor in weights.items() if name.startswith("model.visual.")]
        yield [("mtp.fc.weight", torch.randn(16, 32))]

    weights = {name: tensor.clone() for name, tensor in reference.state_dict().items()}
    if omit_head:
        weights.pop("lm_head.weight")
    iterator = SimpleNamespace(placement=SimpleNamespace(is_full_gather=True), iter_hf_weights=buckets)
    publisher = snapshot_publisher.SnapshotPublisher(iterator)
    monkeypatch.setattr(snapshot_publisher.dist, "get_rank", lambda: 0)
    publisher.write_model(path, weights=weights, hf_checkpoint=str(source))
    return source, path, reference


@pytest.fixture
def raw_export(tmp_path, monkeypatch):
    return _write_export(tmp_path, monkeypatch)


def _change_tensor(path: Path, name: str, value: torch.Tensor | None):
    index_path = path / "model.safetensors.index.json"
    index = json.loads(index_path.read_text())
    shard = index["weight_map"][name]
    tensors = load_file(path / shard)
    if value is None:
        tensors.pop(name)
        index["weight_map"].pop(name)
    else:
        tensors[name] = value
    save_file(tensors, path / shard)
    index_path.write_text(json.dumps(index))


@pytest.mark.parametrize("tied", [True, False])
@pytest.mark.parametrize("dtype", [torch.float32, torch.bfloat16])
def test_real_hybrid_decoder_roundtrip(tmp_path, monkeypatch, tied, dtype):
    source, path, reference = _write_export(tmp_path, monkeypatch, tied=tied, dtype=dtype)
    source_bytes = {file.name: file.read_bytes() for file in source.iterdir()}
    report = qwen_export.export_text_checkpoint(source, path)
    config = AutoConfig.from_pretrained(path, local_files_only=True)
    assert type(config) is Qwen3_5TextConfig
    assert config.architectures == ["Qwen3_5ForCausalLM"]
    assert config.mtp_num_hidden_layers == 0
    assert "vision_config" not in config.to_dict()
    assert config.rope_parameters == reference.config.text_config.rope_parameters
    assert not (path / "preprocessor_config.json").exists()
    reloaded, loading = AutoModelForCausalLM.from_pretrained(
        path, local_files_only=True, dtype="auto", output_loading_info=True
    )
    reloaded.eval()
    for category in ("missing_keys", "unexpected_keys", "mismatched_keys", "error_msgs"):
        assert not loading[category]
    assert (reloaded.lm_head.weight is reloaded.model.embed_tokens.weight) is tied
    for name, tensor in reloaded.state_dict().items():
        raw_name = name.replace("model.", "model.language_model.", 1) if name.startswith("model.") else name
        assert tensor.dtype == dtype
        assert torch.equal(tensor, reference.state_dict()[raw_name])
    tokens = torch.tensor([[1, 2, 3, 4, 5]])
    with torch.no_grad():
        before = reference(tokens, use_cache=False).logits
        after = reloaded(tokens, use_cache=False).logits
        assert torch.equal(before, after)
        assert torch.equal(
            reference.generate(tokens, max_new_tokens=2, do_sample=False),
            reloaded.generate(tokens, max_new_tokens=2, do_sample=False),
        )
    original_tokenizer = AutoTokenizer.from_pretrained(source, local_files_only=True)
    tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
    assert tokenizer.get_vocab() == original_tokenizer.get_vocab()
    messages = [{"role": "user", "content": "a b c"}]
    assert tokenizer.apply_chat_template(messages) == original_tokenizer.apply_chat_template(messages)
    assert tokenizer.encode("a b c") == [1, 2, 3]
    index = json.loads((path / "model.safetensors.index.json").read_text())
    saved = {
        name: tensor
        for shard in set(index["weight_map"].values())
        for name, tensor in load_file(path / shard).items()
    }
    expected = set(reloaded.state_dict()) - ({"lm_head.weight"} if tied else set())
    assert set(saved) == expected
    assert len(set(index["weight_map"].values())) > 1
    assert set(index["weight_map"].values()) == {file.name for file in path.glob("*.safetensors")}
    assert index["metadata"]["total_size"] == sum(tensor.numel() * tensor.element_size() for tensor in saved.values())
    assert report["status"] == "packaged" and report["reload_verified"] is False
    assert report["saved_tensor_count"] == len(expected)
    assert report["excluded_tensors"] and "mtp.fc.weight" in report["excluded_tensors"]
    assert source_bytes == {file.name: file.read_bytes() for file in source.iterdir()}
    # The declared text package also survives the official HF serializer.
    resaved = tmp_path / "text_resaved"
    reloaded.save_pretrained(resaved, max_shard_size="2KB")
    again = AutoModelForCausalLM.from_pretrained(resaved, local_files_only=True, dtype="auto").eval()
    with torch.no_grad():
        assert torch.equal(after, again(tokens, use_cache=False).logits)


def test_tied_source_may_omit_lm_head(tmp_path, monkeypatch):
    source, path, _ = _write_export(tmp_path, monkeypatch, omit_head=True)
    qwen_export.export_text_checkpoint(source, path)
    _, loading = AutoModelForCausalLM.from_pretrained(path, local_files_only=True, output_loading_info=True)
    assert not loading["missing_keys"]


@pytest.mark.parametrize(
    "name,value,message",
    [
        ("model.language_model.layers.0.linear_attn.A_log", None, "coverage mismatch"),
        ("model.language_model.layers.1.self_attn.k_proj.weight", torch.zeros(1), "shape"),
        ("model.language_model.norm.weight", torch.zeros(16, dtype=torch.int32), "dtype"),
        ("lm_head.weight", torch.zeros(16, 16), "Tied embedding"),
    ],
)
def test_decoder_contract_errors_precede_mutation(raw_export, name, value, message):
    source, path, _ = raw_export
    _change_tensor(path, name, value)
    before = {file.name: file.read_bytes() for file in path.iterdir()}
    with pytest.raises(qwen_export.QwenTextExportError, match=message):
        qwen_export.export_text_checkpoint(source, path)
    assert before == {file.name: file.read_bytes() for file in path.iterdir()}


def test_untied_decoder_requires_lm_head(tmp_path, monkeypatch):
    source, path, _ = _write_export(tmp_path, monkeypatch, tied=False, omit_head=True)
    with pytest.raises(qwen_export.QwenTextExportError, match="lm_head.weight"):
        qwen_export.export_text_checkpoint(source, path)


def test_shard_index_must_match_actual_tensors(raw_export):
    source, path, _ = raw_export
    index_path = path / "model.safetensors.index.json"
    index = json.loads(index_path.read_text())
    index["weight_map"].pop("model.language_model.norm.weight")
    index_path.write_text(json.dumps(index))
    with pytest.raises(qwen_export.QwenTextExportError, match="disagree with the shard index"):
        qwen_export.export_text_checkpoint(source, path)


def test_tokenizer_mismatch_is_not_accepted(raw_export):
    source, path, _ = raw_export
    (path / "tokenizer.json").write_text("{}")
    with pytest.raises(qwen_export.QwenTextExportError, match="tokenizer asset"):
        qwen_export.export_text_checkpoint(source, path)


def test_mixed_fp32_decoder_tensors_are_preserved(tmp_path, monkeypatch):
    source, path, _ = _write_export(tmp_path, monkeypatch, dtype=torch.bfloat16)
    name = "model.language_model.layers.0.linear_attn.A_log"
    index = json.loads((path / "model.safetensors.index.json").read_text())
    tensor = load_file(path / index["weight_map"][name])[name].float()
    _change_tensor(path, name, tensor)
    report = qwen_export.export_text_checkpoint(source, path)
    index = json.loads((path / "model.safetensors.index.json").read_text())
    text_name = name.replace("model.language_model.", "model.")
    saved = load_file(path / index["weight_map"][text_name])[text_name]
    assert saved.dtype == torch.float32 and torch.equal(saved, tensor)
    assert report["tensor_dtypes"]["F32"] == 1
    assert report["dtype"] == "torch.bfloat16"


def test_native_hook_uses_immutable_view_and_soft_contract_verdict(raw_export, caplog):
    source, path, _ = raw_export
    hook = CustomFunctionConfig(path="tests.manual.agent_opd.qwen_export.post_save")
    view = compute_custom_function_config(ImmutableNamespace(hf_checkpoint=str(source)), hook)
    _change_tensor(path, "model.language_model.layers.0.linear_attn.A_log", None)
    load_function(hook)(view, 99, None, str(path))
    report = json.loads((path / "qwen_text_export.json").read_text())
    assert report["status"] == "unverified" and report["rollout_id"] == 99
    assert "coverage mismatch" in report["reason"]
    assert "training continues" in caplog.text
    assert AutoConfig.from_pretrained(path, local_files_only=True).model_type == "qwen3_5"


def test_conversion_io_errors_keep_native_failure_behavior(raw_export, monkeypatch):
    source, path, _ = raw_export

    def fail(*args, **kwargs):
        raise OSError("Injected export disk failure")

    monkeypatch.setattr(qwen_export, "save_file", fail)
    with pytest.raises(OSError, match="Injected export disk failure"):
        qwen_export.post_save(ImmutableNamespace(hf_checkpoint=str(source)), 99, None, str(path))
    assert json.loads((path / "qwen_text_export.json").read_text())["status"] == "unverified"
    assert not list(path.glob("*.text-export"))


def test_unexpected_auxiliary_validator_error_is_nonblocking(raw_export, monkeypatch, caplog):
    source, path, _ = raw_export

    def fail(config):
        raise RuntimeError("Injected model-schema validator failure")

    monkeypatch.setattr(qwen_export, "_expected_shapes", fail)
    qwen_export.post_save(ImmutableNamespace(hf_checkpoint=str(source)), 99, None, str(path))
    report = json.loads((path / "qwen_text_export.json").read_text())
    assert report["status"] == "unverified"
    assert "Injected model-schema validator failure" in report["reason"]
    assert "training continues" in caplog.text


@pytest.mark.parametrize("invalid", [False, True])
def test_auxiliary_report_io_failure_is_nonblocking(raw_export, monkeypatch, caplog, invalid):
    source, path, _ = raw_export
    if invalid:
        _change_tensor(path, "model.language_model.layers.0.linear_attn.A_log", None)
    original_write = Path.write_text

    def fail_report(file, *args, **kwargs):
        if file.name == "qwen_text_export.json":
            raise OSError("Injected auxiliary report disk failure")
        return original_write(file, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_report)
    qwen_export.post_save(ImmutableNamespace(hf_checkpoint=str(source)), 99, None, str(path))
    assert "Injected auxiliary report disk failure" in caplog.text
    assert "unverified" in caplog.text
    assert not (path / "qwen_text_export.json").exists()
    expected_type = "qwen3_5" if invalid else "qwen3_5_text"
    assert AutoConfig.from_pretrained(path, local_files_only=True).model_type == expected_type


def test_conversion_never_writes_the_source(raw_export):
    source, _, _ = raw_export
    before = {file.name: file.read_bytes() for file in source.iterdir()}
    with pytest.raises(qwen_export.QwenTextExportError, match="must not be the source"):
        qwen_export.export_text_checkpoint(source, source)
    with pytest.raises(ValueError, match="must not be the source"):
        qwen_export.post_save(ImmutableNamespace(hf_checkpoint=str(source)), 99, None, str(source))
    assert before == {file.name: file.read_bytes() for file in source.iterdir()}
