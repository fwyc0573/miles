"""Source metadata symlinks must remain inside the explicitly authorized roots."""

import json
from pathlib import Path

import pytest

from tests.manual.agent_opd.inspect_qwen35_assets import _model_metadata


@pytest.mark.parametrize("filename", ["config.json", "model.safetensors.index.json"])
def test_metadata_escape_is_rejected_before_read(tmp_path, monkeypatch, filename):
    source = tmp_path / "source"
    source.mkdir()
    outside = tmp_path / "outside.json"
    outside.write_text("{}")
    (source / filename).symlink_to(outside)
    original_read = Path.read_text

    def forbid_outside(file, *args, **kwargs):
        assert file.resolve() != outside, "An unauthorized file was read"
        return original_read(file, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", forbid_outside)
    with pytest.raises(ValueError, match="outside the authorized"):
        _model_metadata(source, (source,))


def test_authorized_model_metadata_and_shards(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "config.json").write_text(
        json.dumps({"model_type": "qwen3_5", "architectures": ["Qwen3_5ForConditionalGeneration"]})
    )
    (source / "model.safetensors.index.json").write_text(
        json.dumps({"weight_map": {"weight": "weights.safetensors"}})
    )
    (source / "weights.safetensors").write_bytes(b"fixture")
    result = _model_metadata(source, (source,))
    assert result["model_type"] == "qwen3_5"
    assert result["all_indexed_shards_exist"]
    assert result["shards"] == [{"name": "weights.safetensors", "size": 7}]
