"""Replay pinned native serialized artifacts; no ACS/model/GPU execution."""

import asyncio
import copy
import shutil
import sys
import time
from pathlib import Path

import pytest
from tests.fast import test_swe_evaluation as lifecycle
from tests.manual.agent_opd import swe_evaluation as swe
from tests.manual.agent_opd import swe_native_evaluation as native

case = lifecycle.case
FIXTURES = Path(__file__).parent / "fixtures" / "swe_native"
REFERENCE = FIXTURES / "reference"
TASK = "astropy__astropy-12907"


def test_native_patch_application_failure_is_model_false():
    assert (
        native.native_outcome(TASK, FIXTURES / "submitted.json", FIXTURES / "apply_patch_fail.json", REFERENCE) is False
    )


@pytest.mark.parametrize("exit_status", ["exit_env_error", "exit_api", "exit_error"])
def test_native_infrastructure_autosubmission_is_not_model_false(exit_status):
    with pytest.raises(ValueError, match="infrastructure"):
        native.native_outcome(TASK, FIXTURES / f"{exit_status}.json", FIXTURES / "unresolved.json", REFERENCE)


@pytest.mark.parametrize("exit_status", ["submitted", "exit_context"])
def test_native_model_outcome_retains_original_scoring(exit_status):
    assert (
        native.native_outcome(TASK, FIXTURES / f"{exit_status}.json", FIXTURES / "unresolved.json", REFERENCE) is False
    )


@pytest.fixture
def native_case(case, tmp_path, monkeypatch):
    from miles.utils.chat_template_utils.tito_tokenizer import Qwen35TITOTokenizer, resolve_fixed_chat_template

    store, _, _, source, tasks = case
    store.reference_root = REFERENCE.resolve()
    tasks = [TASK, *tasks[1:]]
    dataset, manifest = tmp_path / "dataset.json", tmp_path / "benchmark.json"
    all_tasks = tasks + [f"native__task-{i}" for i in range(400)]
    swe.write_json(dataset, [{"instance_id": task} for task in all_tasks])
    swe.write_json(manifest, {"source_group": "swe", "benchmark": {"task_ids": all_tasks}})
    source_file = tmp_path / "source.py"
    source_file.write_text("# Pinned native source identity fixture.\n")
    template, _ = resolve_fixed_chat_template("qwen35")
    runtime = {
        "swe_commit": swe.SWE_COMMIT,
        "source_sha256": {str(source_file): native._sha(source_file), str(template): native._sha(template)},
        "chat_template": str(template),
        "input_sha256": {str(path): native._sha(path) for path in (dataset, manifest)},
        "dataset_path": str(dataset),
        "manifest_path": str(manifest),
        "swe_source_root": str(tmp_path),
        "python_paths": [],
        "python": sys.executable,
        "kill_grace_seconds": 1,
        "model_name": "qwen35-4b",
        "url": "http://evaluation-worker:31000",
        "server_reader_id": "server",
        "baseline_weight_version": "original",
        "server_identity": {
            "model_path": str(source),
            "weight_version": "original",
            "tool_call_parser": Qwen35TITOTokenizer.tool_call_parser,
            "reasoning_parser": Qwen35TITOTokenizer.reasoning_parser,
            "context_length": 131072,
            "preserve_thinking": True,
            "enable_thinking": True,
            "chat_template_sha256": native._sha(template),
        },
    }
    # Replay the real native_config payload generated in the native Python3.10
    # environment. This seam does not import optional ACS dependencies into CI.
    payload = swe.read_json(FIXTURES / "native_config.json")

    def config(runtime, *, request, dataset_index):
        result = copy.deepcopy(payload)
        result["dataset"].update(name_or_path=runtime["dataset_path"], range_str=str(dataset_index))
        result["model"].update(
            model_name=runtime["model_name"],
            inference_args={"seed": request["seed"], "custom_upstream_url": runtime["url"] + "/v1/chat/completions"},
        )
        return result

    monkeypatch.setattr(native, "native_config", config)
    contract = native.evaluation_contract(runtime)
    point_id = "native-baseline"
    store.enqueue_baseline(point_id=point_id, source=source, task_ids=tasks, configuration=contract)
    store.reader_enter(point_id, "server", {"pid": "CPU fixture"})
    runner = native.NativeSweRunner(store, point_id, runtime)
    request = store.request(point_id, TASK, 0)
    return runner, request, time.time() + 100, payload, source_file


def _saved_native_attempt(native_case, *, graded=True, published=True):
    runner, request, deadline, *_ = native_case
    destination = runner.store._point(runner.point_id) / "native" / f"{TASK}.{request['seed']}" / "original"
    invocation = {
        "request": request,
        "runtime": runner.runtime,
        "deadline_at": deadline,
        "reference_root": str(runner.store.reference_root),
        "allocation_identity": runner.store.allocation_identity,
    }
    swe.write_json(destination / "invocation.json", invocation)
    trajectory = destination / "trajectories" / f"{TASK}.json"
    trajectory.parent.mkdir(parents=True)
    shutil.copyfile(FIXTURES / "submitted.json", trajectory)
    config_path = destination / "config.toml"
    config_path.write_text(
        (FIXTURES / "native_config.toml")
        .read_text()
        .replace(
            swe.read_json(FIXTURES / "native_config.json")["dataset"]["name_or_path"], runner.runtime["dataset_path"]
        )
    )
    wire = destination / "requests" / "000000.json"
    swe.write_json(
        wire,
        {
            "url": runner.runtime["url"] + "/v1/chat/completions",
            "body": {"temperature": 1.0, "top_p": 0.95, "seed": request["seed"]},
            "n": 1,
            "max_tokens": None,
        },
    )
    result = destination / "check_results" / f"{TASK}.json"
    if graded:
        result.parent.mkdir(parents=True)
        shutil.copyfile(FIXTURES / "apply_patch_fail.json", result)
        if published:
            native._publish_outcome(
                destination,
                request,
                runner.runtime,
                trajectory,
                result,
                config_path,
                [str(wire)],
                runner.store.reference_root,
            )
    return destination


@pytest.mark.parametrize("published", [True, False])
def test_interrupted_parent_recovers_completed_native_false_without_generation(native_case, monkeypatch, published):
    destination = _saved_native_attempt(native_case, published=published)
    runner, request, deadline, *_ = native_case

    async def forbidden(*args, **kwargs):
        pytest.fail("A completed scored model attempt must not start another native child")

    monkeypatch.setattr(asyncio, "create_subprocess_exec", forbidden)
    result = asyncio.run(runner(request, deadline))
    assert result["success"] is False
    assert (destination / "outcome.json").is_file()
    assert len(list(destination.parent.iterdir())) == 1


@pytest.mark.parametrize("group", ["source_sha256", "input_sha256"])
def test_updated_self_supplied_hashes_cannot_replace_manifest_pins(native_case, group):
    runner, *_ = native_case
    runtime = copy.deepcopy(runner.runtime)
    path = next(iter(runtime[group]))
    Path(path).write_text(Path(path).read_text() + "\n")
    runtime[group][path] = native._sha(path)
    with pytest.raises(ValueError, match="immutable point manifest"):
        native.NativeSweRunner(runner.store, runner.point_id, runtime)


def test_changed_native_harness_config_is_rejected_on_resume(native_case):
    runner, _, _, payload, _ = native_case
    payload["agent"]["prompt_file"] = "different.yaml"
    with pytest.raises(ValueError, match="harness configuration"):
        native.NativeSweRunner(runner.store, runner.point_id, runner.runtime)


def test_runtime_endpoint_location_can_change_without_scientific_change(native_case):
    runner, *_ = native_case
    runtime = copy.deepcopy(runner.runtime)
    runtime["url"] = "http://replacement-worker:31000"
    assert native.NativeSweRunner(runner.store, runner.point_id, runtime).runtime["url"] == runtime["url"]


def test_missing_native_grader_recovers_only_complete_trajectory(native_case):
    destination = _saved_native_attempt(native_case, graded=False, published=False)
    runner, request, deadline, *_ = native_case
    outcome, trajectory = runner._recover(request, deadline)
    assert outcome is None
    assert trajectory["path"] == str(destination / "trajectories" / f"{TASK}.json")
    assert trajectory["sha256"] == native._sha(trajectory["path"])


@pytest.mark.parametrize("artifact", ["trajectory", "grader", "config", "request"])
def test_changed_completed_native_evidence_is_not_rerolled(native_case, monkeypatch, artifact):
    destination = _saved_native_attempt(native_case)
    runner, request, deadline, *_ = native_case
    raw = swe.read_json(destination / "outcome.json")["raw"]
    path = Path(raw["request_paths"][0] if artifact == "request" else raw["native_artifacts"][artifact]["path"])
    path.write_bytes(path.read_bytes() + b"\n")

    async def forbidden(*args, **kwargs):
        pytest.fail("Changed completed native evidence must not regenerate a scored attempt")

    monkeypatch.setattr(asyncio, "create_subprocess_exec", forbidden)
    with pytest.raises(ValueError, match="bytes changed"):
        asyncio.run(runner(request, deadline))


def test_native_patch_failure_persisted_as_irreversible_false(native_case):
    _saved_native_attempt(native_case)
    runner, request, deadline, *_ = native_case
    outcome = asyncio.run(runner(request, deadline))
    store, point_id = runner.store, runner.point_id
    store.start(point_id, allocation=lifecycle.ALLOCATION)
    store.record(point_id, request, success=outcome["success"], raw=outcome["raw"])
    assert request["uid"] not in store.summary(point_id)["missing_attempt_ids"]
    with pytest.raises(ValueError, match="rerolled"):
        store.record(point_id, request, success=True, raw=outcome["raw"])


@pytest.mark.parametrize("field", ["exit_status", "autosubmit_exit_status", "autosubmit_reason"])
def test_each_native_environment_exit_cause_keeps_slot_missing(tmp_path, field):
    trajectory = swe.read_json(FIXTURES / "exit_env_error.json")
    original = trajectory["meta"]
    trajectory["meta"] = {"patch": original["patch"], field: original[field]}
    path = tmp_path / "trajectory.json"
    swe.write_json(path, trajectory)
    with pytest.raises(native.NativeInfrastructureError):
        native.native_outcome(TASK, path, FIXTURES / "unresolved.json", REFERENCE)


def test_native_environment_failure_precedes_patch_grader_false():
    with pytest.raises(native.NativeInfrastructureError):
        native.native_outcome(TASK, FIXTURES / "exit_env_error.json", FIXTURES / "apply_patch_fail.json", REFERENCE)
