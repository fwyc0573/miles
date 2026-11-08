"""CPU native-callback integration; synthetic optimizer/collective export, real HF packaging."""

import ast
import json
import shutil
import subprocess
import sys
from contextlib import ExitStack, nullcontext
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from tests.fast.backends.megatron_utils.score_rpc_fixtures import ScoreModel
from tests.fast.test_qwen_text_export import _write_export
from tests.fast.test_qwen_text_export import single_thread_cpu as single_thread_cpu
from tests.manual.agent_opd import qwen_export, swe_evaluation, swe_hf_export
from transformers import AutoConfig

from miles.backends.training_utils.model_companion import ModelCompanionWeightVersionUtils
from miles.backends.training_utils.types import TrainStepOutcome, TrainStepOutput
from miles.utils.args.custom_function import CustomFunctionConfig
from miles.utils.args.custom_view import ImmutableNamespace, compute_custom_function_config

ROOT = Path(__file__).resolve().parents[2]
HOOK = "tests.manual.agent_opd.swe_hf_export.post_save"


@pytest.fixture
def case(tmp_path, monkeypatch):
    source, raw, reference = _write_export(tmp_path, monkeypatch)
    checkpoint = tmp_path / "owned" / "A-full" / "attempt-1" / "hf" / "step_49"
    configuration = {
        "root": str(tmp_path / "evaluations"),
        "owned_root": str(tmp_path / "owned"),
        "protected_sources": [str(source)],
        "reference_root": str(tmp_path / "unused-reference"),
        "allocation_identity": {"task_id": "fixture-swe", "creator": "fixture-user", "gpu_tag": "H200"},
        "task_ids": [f"fixture__task-{i}" for i in range(100)],
        "evaluation_contract": {"fixture": True},
    }
    config_path = tmp_path / "configuration.json"
    swe_evaluation.write_json(config_path, configuration)
    hook = CustomFunctionConfig(path=HOOK, config={"swe_evaluation_configuration": str(config_path)})
    args = ImmutableNamespace(
        hf_checkpoint=str(source),
        save_hf=str(checkpoint.parent / "step_{rollout_id}"),
        debug_rollout_only=False,
        offload_train=False,
        backend=SimpleNamespace(save=None),
        custom_megatron_post_save_hook_path=hook,
    )
    return SimpleNamespace(
        source=source,
        raw=raw,
        reference=reference,
        checkpoint=checkpoint,
        config=configuration,
        config_path=config_path,
        args=args,
        store=swe_evaluation.store_from_config(configuration),
    )


def _result(successful=50, *, success=True, run_kind="formal", native_rollout_id=50):
    return TrainStepOutput(
        outcome=TrainStepOutcome.NORMAL,
        optimizer_step={
            "cell": "A/full",
            "attempt": "attempt-1",
            "run_kind": run_kind,
            "update_successful": success,
            "successful_updates": successful,
            "attempted_rollout_id": native_rollout_id,
            "native_attempted_count": successful + 1,
            "native_skipped_count": 1,
        },
    )


def _copy_export(case, path=None):
    path = case.checkpoint if path is None else path
    shutil.copytree(case.raw, path)
    (path / ".complete").touch()
    return path


def _callback(
    case, *, result=None, native_rollout_id=50, checkpoint_index=49, get_weight_version=lambda: 907, path=None
):
    path = _copy_export(case, path)
    args = compute_custom_function_config(case.args, case.args.custom_megatron_post_save_hook_path)
    swe_hf_export.post_save(
        args,
        checkpoint_index,
        None,
        str(path),
        train_result=_result() if result is None else result,
        native_rollout_id=native_rollout_id,
        get_weight_version=get_weight_version,
    )
    return path


def _diagnostic(path):
    return swe_evaluation.read_json(path.parent.parent / "hf_publications" / f"{path.name}.json")


def _actor(case, monkeypatch):
    # Run the actual native train/save callback methods without importing Megatron/CUDA.
    path = ROOT / "miles/backends/megatron_utils/actor.py"
    tree = ast.parse(path.read_text())
    node = next(item for item in tree.body if isinstance(item, ast.ClassDef) and item.name == "MegatronTrainRayActor")
    node.bases = []
    node.body = [
        item
        for item in node.body
        if getattr(item, "name", None) in ("train", "save_model", "_get_actor_weight_version")
    ]
    for method in node.body:
        method.decorator_list = []
    namespace = {
        "ExitStack": ExitStack,
        "timer": lambda *args: nullcontext(),
        "dist": SimpleNamespace(get_rank=lambda: 0),
        "get_parallel_state": lambda: SimpleNamespace(train_parallel_config=lambda **kwargs: None),
        "get_rollout_data": lambda **kwargs: ({}, nullcontext()),
        "compute_custom_function_config": compute_custom_function_config,
        "ModelCompanionWeightVersionUtils": ModelCompanionWeightVersionUtils,
    }
    annotations = ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)
    exec(
        compile(ast.fix_missing_locations(ast.Module(body=[annotations, node], type_ignores=[])), str(path), "exec"),
        namespace,
    )
    checkpointing = ModuleType("megatron.training.checkpointing")

    def unexpected_native_save(*args, **kwargs):
        pytest.fail("HF-only callback must never request native/optimizer checkpoint I/O")

    checkpointing.get_checkpoint_name = unexpected_native_save
    monkeypatch.setitem(sys.modules, checkpointing.__name__, checkpointing)
    actor = namespace["MegatronTrainRayActor"]()
    actor.args, actor.role, actor._asleep = case.args, "actor", False
    actor._heartbeat = SimpleNamespace(bump=lambda: None)
    actor._last_rollout_id = actor._last_train_result = None
    actor.output_store_read = None
    actor.model = [ScoreModel()]
    actor._get_actor_weights = lambda **kwargs: dict(actor.model[0].named_parameters())
    actor._finalize_pending_async_save = lambda: None
    actor._publish_model_companion_info = lambda **kwargs: None
    actor.export_hf = lambda rollout_id, path: _copy_export(case, Path(path))
    return actor


def test_actual_actor_callback_after_skipped_attempt_binds_all_native_identities(case, monkeypatch):
    actor = _actor(case, monkeypatch)
    skipped = _result(49, success=False, native_rollout_id=49)
    successful = _result()
    actor._train_actor = lambda *args, **kwargs: skipped
    assert actor.train(49, object()) is skipped
    assert actor._last_train_result is skipped
    actor._train_actor = lambda *args, **kwargs: successful
    actor.model[0].model_companion.weight_version.data.fill_(907)
    assert actor.train(50, object()) is successful
    assert actor._last_train_result is successful
    before = {file.name: file.read_bytes() for file in case.source.iterdir()}
    original = swe_evaluation.EvaluationStore.enqueue_checkpoint
    observed = []

    def enqueue(store, **kwargs):
        package = swe_evaluation.read_json(Path(kwargs["checkpoint_dir"]) / "qwen_text_export.json")
        assert package["status"] == "packaged" and package["rollout_id"] == 50
        assert (case.checkpoint / ".complete").stat().st_mtime_ns >= (
            case.checkpoint / "qwen_text_export.json"
        ).stat().st_mtime_ns
        assert AutoConfig.from_pretrained(kwargs["checkpoint_dir"], local_files_only=True).model_type == "qwen3_5_text"
        observed.append(package)
        return original(store, **kwargs)

    monkeypatch.setattr(swe_evaluation.EvaluationStore, "enqueue_checkpoint", enqueue)
    monkeypatch.setattr(
        case.reference, "forward", lambda *args, **kwargs: pytest.fail("Packaging must not run a model forward")
    )
    actor.save_model(49)
    assert len(observed) == 1
    point_id = "A-full.attempt-1.HF50"
    manifest = case.store.manifest(point_id)
    assert manifest["checkpoint_dir"] == str(case.checkpoint)
    assert manifest["native_update"] == {
        "successful_update": 50,
        "rollout_id": 50,
        "checkpoint_index": 49,
        "weight_version": 907,
        "native_counters": {"successful_updates": 50, "native_attempted_count": 51, "native_skipped_count": 1},
    }
    assert case.store.state(point_id)["deadline_at"] is None
    assert _diagnostic(case.checkpoint)["status"] == "QUEUED"
    assert all("hf_publications" not in item["path"] for item in manifest["files"])
    assert before == {file.name: file.read_bytes() for file in case.source.iterdir()}
    # A new producer-independent process observes the durable queue, without a GPU or scorer.
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tests.manual.agent_opd.swe_evaluation",
            "--configuration",
            str(case.config_path),
            "--action",
            "queue",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    assert json.loads(result.stdout) == [point_id]


def test_original_four_argument_qwen_callback_is_unchanged(case, monkeypatch):
    actor = _actor(case, monkeypatch)
    actor.args = case.args.model_copy(
        update={
            "custom_megatron_post_save_hook_path": CustomFunctionConfig(
                path="tests.manual.agent_opd.qwen_export.post_save"
            )
        }
    )
    del actor._last_train_result
    actor._get_actor_weight_version = lambda: pytest.fail("Legacy callback must not inspect native training state")
    actor.save_model(49)
    package = swe_evaluation.read_json(case.checkpoint / "qwen_text_export.json")
    assert package["status"] == "packaged" and package["rollout_id"] == 49
    assert not case.store.queued()


def test_failed_native_attempt_clears_previous_train_result(case, monkeypatch):
    actor = _actor(case, monkeypatch)
    actor._last_train_result = _result()

    def fail(*args, **kwargs):
        raise RuntimeError("Injected native training failure")

    actor._train_actor = fail
    with pytest.raises(RuntimeError, match="native training"):
        actor.train(51, object())
    assert actor._last_rollout_id == 51 and actor._last_train_result is None


@pytest.mark.parametrize("successful", [2, 50])
def test_smoke_packages_without_formal_enqueue_even_at_formal_index(case, monkeypatch, successful):
    case.args = case.args.model_copy(update={"custom_megatron_post_save_hook_path": CustomFunctionConfig(path=HOOK)})
    monkeypatch.setattr(
        swe_hf_export, "store_from_config", lambda *args: pytest.fail("Smoke cannot enqueue a formal benchmark")
    )
    path = case.checkpoint.with_name(f"step_{successful - 1}")
    _callback(case, result=_result(successful, run_kind="smoke"), checkpoint_index=successful - 1, path=path)
    assert _diagnostic(path)["status"] == "SMOKE_PACKAGED"
    package = swe_evaluation.read_json(path / "qwen_text_export.json")
    assert package["successful_update"] == successful and package["weight_version"] == 907
    assert package["run_kind"] == "smoke" and case.store.queued() == ()
    assert "avg_at_n" not in package and "avg_at_n" not in _diagnostic(path)
    if successful == 50:
        with pytest.raises(ValueError, match="Only formal"):
            case.store.enqueue_checkpoint(
                point_id="smoke",
                checkpoint_dir=path,
                native_update=_diagnostic(path)["native_update"],
                source=case.source,
                task_ids=case.config["task_ids"],
                configuration=case.config["evaluation_contract"],
            )


@pytest.mark.parametrize("failure", ["skipped", "stale", "wrong-index", "bad-counters", "version-error", "no-result"])
def test_native_identity_failure_is_soft_and_retains_packaged_hf(case, failure):
    result, native_rollout_id, index = _result(), 50, 49

    def getter():
        return 907

    if failure == "skipped":
        result = _result(49, success=False)
    elif failure == "stale":
        native_rollout_id = 51
    elif failure == "wrong-index":
        index = 50
    elif failure == "bad-counters":
        result.optimizer_step["native_attempted_count"] = 99
    elif failure == "version-error":

        def getter():
            raise RuntimeError("Injected actual-model version inspection failure")

    elif failure == "no-result":
        result = TrainStepOutput(outcome=TrainStepOutcome.NORMAL)
    path = _callback(
        case, result=result, native_rollout_id=native_rollout_id, checkpoint_index=index, get_weight_version=getter
    )
    diagnostic = _diagnostic(path)
    assert diagnostic["status"] == "UNVERIFIED" and diagnostic["stage"] == "native_identity"
    assert swe_evaluation.read_json(path / "qwen_text_export.json")["status"] == "packaged"
    assert path.is_dir() and list(path.glob("*.safetensors")) and not case.store.queued()


@pytest.mark.parametrize("stage", ["metadata", "completion_marker", "enqueue"])
def test_auxiliary_io_failure_is_soft_has_durable_diagnostic_and_preserves_hf(case, monkeypatch, stage):
    if stage in ("metadata", "completion_marker"):
        original = swe_hf_export.write_json

        def fail(path, value):
            if Path(path).name == ("qwen_text_export.json" if stage == "metadata" else ".complete"):
                raise OSError("Injected auxiliary metadata failure")
            return original(path, value)

        monkeypatch.setattr(swe_hf_export, "write_json", fail)
    else:

        def fail(*args, **kwargs):
            raise OSError("Injected durable queue failure")

        monkeypatch.setattr(swe_evaluation.EvaluationStore, "enqueue_checkpoint", fail)
    path = _callback(case)
    diagnostic = _diagnostic(path)
    assert diagnostic["status"] == "UNVERIFIED" and diagnostic["stage"] == stage
    assert diagnostic["error"]["type"] == "OSError"
    assert diagnostic["native_update"]["weight_version"] == 907
    assert path.is_dir() and list(path.glob("*.safetensors")) and not case.store.queued()


def test_partial_queue_failure_does_not_mutate_immutable_hf_and_can_recover(case, monkeypatch):
    original = swe_evaluation.write_json

    def fail(path, row):
        if Path(path).name == "state.json":
            raise OSError("Injected queue crash after manifest")
        return original(path, row)

    monkeypatch.setattr(swe_evaluation, "write_json", fail)
    path = _callback(case)
    assert _diagnostic(path)["stage"] == "enqueue"
    point = "A-full.attempt-1.HF50"
    manifest = case.store.manifest(point)
    assert swe_evaluation._file_inventory(path) == manifest["files"]
    monkeypatch.setattr(swe_evaluation, "write_json", original)
    assert case.store.queued() == (point,)
    assert (
        case.store.enqueue_checkpoint(
            point_id=point,
            checkpoint_dir=path,
            native_update=manifest["native_update"],
            source=case.source,
            task_ids=case.config["task_ids"],
            configuration=case.config["evaluation_contract"],
        )
        == point
    )


def test_unverified_packaging_never_enqueues_and_records_diagnostic(case, monkeypatch):
    def fail(*args):
        raise RuntimeError("Injected packaging validator failure")

    monkeypatch.setattr(qwen_export, "_expected_shapes", fail)
    path = _callback(case)
    assert swe_evaluation.read_json(path / "qwen_text_export.json")["status"] == "unverified"
    assert _diagnostic(path)["stage"] == "packaging" and not case.store.queued()
    assert path.is_dir() and list(path.glob("*.safetensors"))


def test_native_conversion_io_still_propagates(case, monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("Injected native conversion I/O failure")

    monkeypatch.setattr(qwen_export, "save_file", fail)
    with pytest.raises(OSError, match="native conversion"):
        _callback(case)
    assert not case.store.queued()


def test_formal_save_outside_frozen_points_is_not_enqueued(case):
    path = case.checkpoint.with_name("step_1")
    _callback(case, result=_result(2), checkpoint_index=1, path=path)
    assert _diagnostic(path)["stage"] == "enqueue" and not case.store.queued()


def test_actual_rollout_directory_cannot_replace_successful_index(case):
    path = case.checkpoint.with_name("step_50")
    _callback(case, path=path)
    assert _diagnostic(path)["stage"] == "enqueue" and not case.store.queued()
    assert path.is_dir()


@pytest.mark.parametrize(
    "field,value", [("rollout_id", 49), ("weight_version", 50), ("successful_update", 100), ("checkpoint_index", 50)]
)
def test_store_requires_packaged_native_identity_agreement(case, field, value):
    path = _callback(case)
    point = "A-full.attempt-1.HF50"
    manifest = case.store.manifest(point)
    package = swe_evaluation.read_json(path / "qwen_text_export.json")
    swe_evaluation.write_json(path / "qwen_text_export.json", {**package, field: value})
    with pytest.raises(ValueError, match="publication"):
        case.store.enqueue_checkpoint(
            point_id="foreign",
            checkpoint_dir=path,
            native_update=manifest["native_update"],
            source=case.source,
            task_ids=case.config["task_ids"],
            configuration=case.config["evaluation_contract"],
        )
