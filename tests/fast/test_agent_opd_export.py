"""Validate GLM decoder exports against the native MTP training configuration."""

import json

import pytest
import torch
from safetensors.torch import save_file

from tests.manual.agent_opd.rjob_benchmark import _check_export


@pytest.fixture
def glm_export(tmp_path):
    original, updated = tmp_path / "original", tmp_path / "updated"
    original.mkdir()
    updated.mkdir()
    weights = {
        name: torch.ones(8)
        for name in (
            "model.embed_tokens.weight",
            "model.layers.0.input_layernorm.weight",
            "model.layers.46.input_layernorm.weight",
            "model.norm.weight",
            "lm_head.weight",
            "model.layers.47.eh_proj.weight",
        )
    }
    save_file(weights, original / "model.safetensors")
    (original / "config.json").write_text(
        json.dumps({"model_type": "glm4_moe_lite", "num_hidden_layers": 47, "num_nextn_predict_layers": 1})
    )
    exported = {name: value + 1 for name, value in weights.items() if not name.startswith("model.layers.47.")}
    save_file(exported, updated / "model.safetensors")
    (updated / "model.safetensors.index.json").write_text(
        json.dumps({"weight_map": {name: "model.safetensors" for name in exported}})
    )
    (updated / ".complete").touch()
    (updated / "learning_identity.json").write_text(
        json.dumps(
            {
                "completed_optimizer_updates": 20,
                "rollout_id": 19,
                "enable_mtp_training": False,
                "mtp_num_layers": None,
            }
        )
    )
    return original, updated, exported


def test_decoder_export_omits_only_the_unbuilt_mtp_layer(glm_export):
    original, updated, _ = glm_export
    result = _check_export(original, updated)
    assert result["tensor_count"] == result["changed_tensor_samples"] == 5
    assert result["excluded_untrained_mtp_tensors"] == 1


def test_decoder_export_rejects_missing_boundary_weight(glm_export):
    original, updated, weights = glm_export
    del weights["model.embed_tokens.weight"]
    save_file(weights, updated / "model.safetensors")
    with pytest.raises(ValueError, match="tensor names/shapes"):
        _check_export(original, updated)


def test_decoder_export_rejects_incorrect_shard_mapping(glm_export):
    original, updated, weights = glm_export
    mapping = {name: "missing.safetensors" for name in weights}
    (updated / "model.safetensors.index.json").write_text(json.dumps({"weight_map": mapping}))
    with pytest.raises(ValueError, match="index"):
        _check_export(original, updated)


@pytest.mark.parametrize("corrupt_alias", [False, True])
def test_decoder_export_checks_shared_mtp_alias_values(glm_export, corrupt_alias):
    original, updated, weights = glm_export
    aliases = {
        "model.layers.47.embed_tokens.weight": "model.embed_tokens.weight",
        "model.layers.47.shared_head.head.weight": "lm_head.weight",
    }
    for alias, source in aliases.items():
        weights[alias] = weights[source].clone()
    if corrupt_alias:
        # The export sampler reads the first four values; aliases require full equality.
        weights["model.layers.47.embed_tokens.weight"][-1] += 1
    save_file(weights, updated / "model.safetensors")
    (updated / "model.safetensors.index.json").write_text(
        json.dumps({"weight_map": {name: "model.safetensors" for name in weights}})
    )
    if corrupt_alias:
        with pytest.raises(ValueError, match="Shared MTP alias"):
            _check_export(original, updated)
    else:
        result = _check_export(original, updated)
        assert result["tensor_count"] == 7
        assert result["decoder_tensor_count"] == result["changed_tensor_samples"] == 5
        assert result["verified_shared_mtp_aliases"] == sorted(aliases)


def test_decoder_export_rejects_untrained_mtp_parameters(glm_export):
    original, updated, weights = glm_export
    weights["model.layers.47.eh_proj.weight"] = torch.ones(8)
    save_file(weights, updated / "model.safetensors")
    with pytest.raises(ValueError, match="tensor names/shapes"):
        _check_export(original, updated)
