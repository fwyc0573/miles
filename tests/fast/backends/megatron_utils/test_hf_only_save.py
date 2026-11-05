"""Check checkpoint dispatch without importing GPU-only Megatron libraries."""

import ast
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from miles.backends.training_utils.checkpoint.io import write_checkpoint_dir
from miles.utils.hf_utils.config import HF_EXPORT_COMPLETE_MARKER


@pytest.fixture
def save_worker():
    source = Path(__file__).resolve().parents[4] / "miles/backends/megatron_utils/actor.py"
    tree = ast.parse(source.read_text())
    actor = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "MegatronTrainRayActor")
    methods = [
        node for node in actor.body if isinstance(node, ast.FunctionDef) and node.name in ("save_model", "export_hf")
    ]
    for method in methods:
        method.decorator_list = []
    native_save, hf_save = Mock(), Mock()
    namespace = {
        "save": native_save,
        "save_hf_model": hf_save,
        "write_checkpoint_dir": write_checkpoint_dir,
        "HF_EXPORT_COMPLETE_MARKER": HF_EXPORT_COMPLETE_MARKER,
        "is_lora_model": lambda model: False,
    }
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(source), "exec"), namespace)
    worker = SimpleNamespace(
        args=SimpleNamespace(
            debug_rollout_only=False,
            backend=SimpleNamespace(save=None),
            save_hf="/checkpoints/hf/{rollout_id}",
            hf_checkpoint="/models/original",
            custom_megatron_post_save_hook_path=None,
        ),
        role="actor",
        _heartbeat=Mock(),
        _finalize_pending_async_save=Mock(),
        model=object(),
        optimizer=object(),
        opt_param_scheduler=object(),
        snapshot_publisher=Mock(),
        _named_actor_weights=Mock(return_value=[("decoder.weight", object())]),
    )
    worker.save_model = namespace["save_model"].__get__(worker)
    worker.export_hf = namespace["export_hf"].__get__(worker)
    return worker, native_save, hf_save


@pytest.mark.parametrize("export_fails", [False, True])
def test_hf_only_save_skips_native_staging_and_propagates_export_errors(save_worker, export_fails, tmp_path):
    """The actual actor methods export collectively without an unrequested native save."""
    worker, native_save, hf_save = save_worker
    worker.args.save_hf = str(tmp_path / "hf" / "{rollout_id}")
    worker.snapshot_publisher.write_model.side_effect = RuntimeError("HF export failed") if export_fails else None
    with pytest.raises(RuntimeError, match="HF export failed") if export_fails else nullcontext():
        worker.save_model(19, force_sync=True)
    native_save.assert_not_called()
    hf_save.assert_not_called()
    worker.snapshot_publisher.write_model.assert_called_once_with(
        tmp_path / "hf" / "19",
        weights=dict(worker._named_actor_weights.return_value),
        hf_checkpoint=worker.args.hf_checkpoint,
    )
    assert (tmp_path / "hf" / "19" / ".complete").exists() is not export_fails


def test_native_save_keeps_existing_order(save_worker):
    worker, native_save, hf_save = save_worker
    worker.args.backend.save = "/checkpoints/native"
    calls = Mock()
    calls.attach_mock(native_save, "native")
    calls.attach_mock(hf_save, "hf")
    worker.save_model(19, force_sync=True)
    assert [item[0] for item in calls.mock_calls] == ["native", "hf"]
    assert "raise_on_error" not in hf_save.call_args.kwargs


def test_explicit_hf_export_uses_the_published_weight_stream(save_worker, tmp_path):
    """An inference export must avoid the whole-model Bridge serializer."""
    worker, _, hf_save = save_worker
    worker.export_hf(19, str(tmp_path / "hf"))
    hf_save.assert_not_called()
    worker.snapshot_publisher.write_model.assert_called_once_with(
        tmp_path / "hf",
        weights=dict(worker._named_actor_weights.return_value),
        hf_checkpoint=worker.args.hf_checkpoint,
    )
    assert (tmp_path / "hf" / ".complete").is_file()


def test_explicit_lora_export_merges_base_and_writes_adapter(save_worker, tmp_path, monkeypatch):
    worker, _, hf_save = save_worker
    merged = {"decoder.weight": object()}
    merge = Mock(return_value=merged)
    monkeypatch.setitem(worker.export_hf.__func__.__globals__, "is_lora_model", lambda model: True)
    monkeypatch.setitem(worker.export_hf.__func__.__globals__, "merge_lora_into_weights", merge)
    worker.export_hf(19, str(tmp_path / "hf"))
    hf_save.assert_not_called()
    merge.assert_called_once_with(worker.model, dict(worker._named_actor_weights.return_value))
    worker.snapshot_publisher.write_model.assert_called_once_with(
        tmp_path / "hf", weights=merged, hf_checkpoint=worker.args.hf_checkpoint
    )
    worker.snapshot_publisher.write_adapter.assert_called_once_with(None, tmp_path / "hf" / "adapter")
    assert (tmp_path / "hf" / ".complete").is_file()
