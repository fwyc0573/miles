"""Check checkpoint dispatch without importing GPU-only Megatron libraries."""

import ast
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


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
    namespace = {"save": native_save, "save_hf_model": hf_save}
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(source), "exec"), namespace)
    worker = SimpleNamespace(
        args=SimpleNamespace(
            debug_rollout_only=False,
            backend=SimpleNamespace(save=None),
            save_hf="/checkpoints/hf/{rollout_id}",
            custom_megatron_post_save_hook_path=None,
        ),
        role="actor",
        _heartbeat=Mock(),
        _finalize_pending_async_save=Mock(),
        model=object(),
        optimizer=object(),
        opt_param_scheduler=object(),
        snapshot_publisher=object(),
    )
    worker.save_model = namespace["save_model"].__get__(worker)
    worker.export_hf = namespace["export_hf"].__get__(worker)
    return worker, native_save, hf_save


@pytest.mark.parametrize("export_fails", [False, True])
def test_hf_only_save_skips_native_staging_and_propagates_export_errors(save_worker, export_fails):
    """The actual actor methods export collectively without an unrequested native save."""
    worker, native_save, hf_save = save_worker
    hf_save.side_effect = RuntimeError("HF export failed") if export_fails else None
    with pytest.raises(RuntimeError, match="HF export failed") if export_fails else nullcontext():
        worker.save_model(19, force_sync=True)
    native_save.assert_not_called()
    hf_save.assert_called_once_with(
        worker.args,
        19,
        worker.model,
        publisher=worker.snapshot_publisher,
        path="/checkpoints/hf/19",
        raise_on_error=True,
    )


def test_native_save_keeps_existing_order(save_worker):
    worker, native_save, hf_save = save_worker
    worker.args.backend.save = "/checkpoints/native"
    calls = Mock()
    calls.attach_mock(native_save, "native")
    calls.attach_mock(hf_save, "hf")
    worker.save_model(19, force_sync=True)
    assert [item[0] for item in calls.mock_calls] == ["native", "hf"]
    assert "raise_on_error" not in hf_save.call_args.kwargs
