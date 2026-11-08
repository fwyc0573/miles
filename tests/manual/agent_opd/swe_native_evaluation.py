"""Execute the pinned SWE-Agent ACS pipeline against a parent-owned Qwen server.

The parent starts/pins the server and registers its HF reader before invoking the
independent evaluator. This module neither submits RJobs nor stages/copies weights.
Each seed runs one native task at a time. Native query retries/grading are reused.
"""

import argparse
import asyncio
import contextlib
import copy
import hashlib
import os
import runpy
import shutil
import signal
import sys
import threading
import time
import uuid
from pathlib import Path

from tests.manual.agent_opd.swe_evaluation import SEEDS, SWE_COMMIT, benchmark_tasks, read_json, write_json

INFRASTRUCTURE_AUTOSUBMIT_CAUSES = {
    "exit_env_error": "env_error",
    "exit_api": "api_error",
    "exit_error": "runtime_error",
}


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class NativeInfrastructureError(ValueError):
    """A native attempt that must remain missing rather than receive a model score."""


def native_outcome(task, trajectory_path, result_path, reference_root):
    trajectory, result = read_json(trajectory_path), read_json(result_path)
    _model_trajectory(trajectory)
    if not isinstance(result, dict) or result.get("instance_id") != task:
        raise ValueError("Native grader identity is unverified")
    # The pinned native grader returns a string, not a test report, for a
    # rejected model patch. It is a completed False even though no tests ran.
    if result.get("status") == "apply_patch_fail":
        if not isinstance(result.get("detail"), str) or not result["detail"]:
            raise ValueError("Native patch application failure has no error detail")
        return False
    reference_swe = Path(reference_root) / "tests/e2e/mopd_step3p6_bounded_replay/swe_formal.py"
    return runpy.run_path(str(reference_swe))["outcome"](task, trajectory_path, result_path)


def _model_trajectory(trajectory):
    if not isinstance(trajectory, dict):
        raise ValueError("Native trajectory must be a JSON object")
    meta = trajectory.get("meta") or trajectory.get("metadata") or {}
    if not isinstance(meta, dict):
        raise ValueError("Native trajectory metadata is unverified")
    exits = [meta.get("exit_status"), meta.get("autosubmit_exit_status")]
    prefix = "submitted ("
    exits = [
        (
            status[len(prefix) : -1].strip()
            if isinstance(status, str) and status.startswith(prefix) and status.endswith(")")
            else status
        )
        for status in exits
    ]
    if (
        trajectory.get("error_type")
        or meta.get("error_type")
        or any(status in INFRASTRUCTURE_AUTOSUBMIT_CAUSES for status in exits)
        or meta.get("autosubmit_reason") in INFRASTRUCTURE_AUTOSUBMIT_CAUSES.values()
    ):
        raise NativeInfrastructureError("Native trajectory ended with an infrastructure failure; keep the slot missing")
    return meta


def _runtime_contract(runtime):
    # Endpoint/reader identities are allocation locations. Model path/version
    # are owned by the point manifest, not the shared scientific configuration.
    frozen = {
        name: value for name, value in runtime.items() if name not in ("url", "server_reader_id", "server_identity")
    }
    frozen["server_identity"] = {
        name: value
        for name, value in runtime["server_identity"].items()
        if name not in ("model_path", "weight_version")
    }
    return frozen


def _config_contract(config):
    def toml_fields(value):
        if isinstance(value, dict):
            return {name: toml_fields(item) for name, item in value.items() if item is not None}
        if isinstance(value, list):
            return [toml_fields(item) for item in value]
        return value

    # Native TOML serialization omits None-valued dictionary fields.
    config = copy.deepcopy(config)
    config["model"]["inference_args"].pop("custom_upstream_url")
    config["model"]["inference_args"].pop("seed")
    config["dataset"].pop("range_str")
    return toml_fields(config)


def evaluation_contract(runtime):
    """Build once at enqueue; every native start/resume must match this manifest value."""
    return {
        "runtime": _runtime_contract(runtime),
        "native_config": _config_contract(native_config(runtime, request={"seed": SEEDS[0]}, dataset_index=0)),
    }


def _verify_runtime(runtime, configuration):
    if _runtime_contract(runtime) != configuration["runtime"]:
        raise ValueError("Native scientific runtime/source/input pins differ from the immutable point manifest")
    _verify_sources(runtime)


def _verify_sources(runtime):
    if runtime["swe_commit"] != SWE_COMMIT:
        raise ValueError("Use the original SWE-Agent source, not the later context-error patch")
    for group in ("source_sha256", "input_sha256"):
        for path, digest in runtime[group].items():
            if _sha(path) != digest:
                raise ValueError(f"Pinned native source/input changed: {path}")
    if any(runtime[name] not in runtime["input_sha256"] for name in ("dataset_path", "manifest_path")):
        raise ValueError("Native benchmark library and ordered manifest must both be pinned")


def native_config(runtime, *, request, dataset_index):
    # Optional native dependencies are intentionally absent from CPU lifecycle tests.
    from playground.agenticeval.sweagents_configs import SweAgentACSEvalConfig

    config = SweAgentACSEvalConfig().to_dict()
    config.update(repeat=1, concurrency=1, check_concurrency=1, save_stepeval_checkpoint=False, use_exit_code=False)
    config["check"]["concurrency"] = 1
    config["dataset"].update(name_or_path=runtime["dataset_path"], range_str=str(dataset_index))
    config["model"].update(
        model_name=runtime["model_name"],
        max_context_tokens=131072,
        inference_args={
            "custom_upstream_url": runtime["url"].rstrip("/") + "/v1/chat/completions",
            "seed": request["seed"],
        },
    )
    if (
        config["model"]["temperature"],
        config["model"]["top_p"],
        config["model"]["top_k"],
        config["model"]["max_tokens"],
        config["model"]["drop_thinking"],
    ) != (1.0, 0.95, None, None, "never"):
        raise ValueError("Inherited SWE model sampling configuration changed")
    if config["agent"]["agent_loop_timeout"] != 18000 or config["env"]["timeout"] != 1200:
        raise ValueError("Inherited native agent/environment deadlines changed")
    return config


class NativeSweRunner:
    def __init__(self, store, point_id, runtime):
        from miles.utils.chat_template_utils.tito_tokenizer import Qwen35TITOTokenizer, resolve_fixed_chat_template

        manifest = store.manifest(point_id)
        _verify_runtime(runtime, manifest["configuration"])
        if (
            _config_contract(native_config(runtime, request={"seed": manifest["seeds"][0]}, dataset_index=0))
            != manifest["configuration"]["native_config"]
        ):
            raise ValueError("Native harness configuration differs from the immutable point manifest")
        if list(benchmark_tasks(runtime["manifest_path"], runtime["dataset_path"])) != manifest["task_ids"]:
            raise ValueError("Evaluation tasks differ from the original manifest's first 100 tasks")
        reader = store.state(point_id)["readers"].get(runtime["server_reader_id"])
        if not reader or reader["status"] != "RUNNING":
            raise ValueError("Parent-owned server must have a live persistent HF reader")
        observed = runtime["server_identity"]
        if Path(observed["model_path"]).resolve() != Path(manifest["checkpoint_dir"]):
            raise ValueError("Serving model path is not this checkpoint")
        expected_version = (
            manifest["native_update"]["weight_version"] if manifest["owned"] else runtime["baseline_weight_version"]
        )
        if str(observed["weight_version"]) != str(expected_version):
            raise ValueError("Serving native weight-version readback differs")
        if (
            observed["tool_call_parser"],
            observed["reasoning_parser"],
            observed["context_length"],
            observed["preserve_thinking"],
            observed["enable_thinking"],
        ) != (Qwen35TITOTokenizer.tool_call_parser, Qwen35TITOTokenizer.reasoning_parser, 131072, True, True):
            raise ValueError("Need Qwen's registered parsers, full context, and preserved thinking")
        template_path, _ = resolve_fixed_chat_template("qwen35")
        if observed["chat_template_sha256"] != _sha(template_path):
            raise ValueError("Serving chat template differs from the existing fixed Qwen template")
        self.store, self.point_id, self.runtime = store, point_id, runtime
        if runtime["kill_grace_seconds"] <= 0:
            raise ValueError("Native child cleanup grace must be positive")

    async def __call__(self, request, deadline_at):
        recovered, trajectory_source = self._recover(request, deadline_at)
        if recovered is not None:
            return recovered
        destination = (
            self.store._point(self.point_id) / "native" / f"{request['task_id']}.{request['seed']}" / uuid.uuid4().hex
        )
        destination.mkdir(parents=True)
        invocation = {
            "request": request,
            "runtime": self.runtime,
            "deadline_at": deadline_at,
            "started_at": time.time(),
            "reference_root": str(self.store.reference_root),
            "point_manifest": str(self.store._point(self.point_id) / "manifest.json"),
            "trajectory_source": trajectory_source,
        }
        write_json(destination / "invocation.json", invocation)
        env = dict(
            os.environ,
            PYTHONPATH=os.pathsep.join(
                [
                    str(Path(__file__).resolve().parents[3]),
                    self.runtime["swe_source_root"] + "/src",
                    str(self.store.reference_root),
                    *self.runtime["python_paths"],
                    os.environ.get("PYTHONPATH", ""),
                ]
            ),
            CUDA_VISIBLE_DEVICES="",
            WORLD_SIZE="1",
        )
        with (destination / "child.log").open("w") as log:
            process = await asyncio.create_subprocess_exec(
                self.runtime["python"],
                "-B",
                "-m",
                "tests.manual.agent_opd.swe_native_evaluation",
                "--invocation",
                str(destination / "invocation.json"),
                env=env,
                stdout=log,
                stderr=asyncio.subprocess.STDOUT,
                start_new_session=True,
            )
            reader_id = "native-child-" + str(process.pid) + "-" + uuid.uuid4().hex
            registered = False
            try:
                self.store.reader_enter(
                    self.point_id,
                    reader_id,
                    {
                        "pid": process.pid,
                        "process_group": process.pid,
                        "request": request,
                        "destination": str(destination),
                    },
                )
                registered = True
                await process.wait()
            finally:
                # Reap the whole process group, including native grader descendants.
                await _stop_child_tree(process, self.runtime["kill_grace_seconds"])
                if registered:
                    self.store.reader_exit(
                        self.point_id,
                        reader_id,
                        {
                            "process_group": process.pid,
                            "all_live_group_members_exited": True,
                            "returncode": process.returncode,
                        },
                    )
        if process.returncode != 0:
            raise RuntimeError(f"Native SWE child exited {process.returncode}; evidence: {destination}")
        return self._validated_outcome(destination, request, deadline_at)

    def _invocation(self, destination, request, deadline_at):
        invocation = read_json(destination / "invocation.json")
        if invocation["request"] != request or invocation["deadline_at"] != deadline_at:
            raise ValueError("Saved native attempt has a different task/seed/deadline")
        if Path(invocation["reference_root"]).resolve() != self.store.reference_root:
            raise ValueError("Saved native reference root changed")
        _verify_runtime(invocation["runtime"], self.store.manifest(self.point_id)["configuration"])
        old, current = invocation["runtime"]["server_identity"], self.runtime["server_identity"]
        if old["model_path"] != current["model_path"] or old["weight_version"] != current["weight_version"]:
            raise ValueError("Saved native attempt was served by a different checkpoint/version")
        return invocation

    def _validated_outcome(self, destination, request, deadline_at):
        invocation = self._invocation(destination, request, deadline_at)
        row = read_json(destination / "outcome.json")
        if type(row["success"]) is not bool:
            raise ValueError("Saved native outcome is not boolean")
        raw = row["raw"]
        for artifact in raw["native_artifacts"].values():
            path = Path(artifact["path"]).resolve()
            if not path.is_relative_to(destination.resolve()) or _sha(path) != artifact["sha256"]:
                raise ValueError("Saved native artifact bytes changed or escaped the attempt")
        paths = {name: Path(raw["native_artifacts"][name]["path"]) for name in ("trajectory", "grader", "config")}
        if row["success"] != native_outcome(
            request["task_id"], paths["trajectory"], paths["grader"], self.store.reference_root
        ):
            raise ValueError("Saved native outcome disagrees with its grader/trajectory")
        _validate_config_and_requests(
            paths["config"],
            raw["request_paths"],
            request,
            self.store.manifest(self.point_id)["configuration"],
            destination,
        )
        if raw["request_sha256"] != {path: _sha(path) for path in raw["request_paths"]}:
            raise ValueError("Saved native request bytes changed")
        if raw["swe_commit"] != SWE_COMMIT or raw["server_identity"] != invocation["runtime"]["server_identity"]:
            raise ValueError("Saved native serving/source identity changed")
        return row

    def _recover(self, request, deadline_at):
        slot = self.store._point(self.point_id) / "native" / f"{request['task_id']}.{request['seed']}"
        attempts = sorted(slot.glob("*/invocation.json"))
        complete = [path.parent for path in attempts if (path.parent / "outcome.json").exists()]
        if len(complete) > 1:
            raise ValueError("Multiple completed native model attempts exist for the same slot")
        if complete:
            return self._validated_outcome(complete[0], request, deadline_at), None
        trajectory_source = None
        for path in attempts:
            destination = path.parent
            self._invocation(destination, request, deadline_at)
            trajectory = destination / "trajectories" / f"{request['task_id']}.json"
            if not trajectory.exists():
                continue
            data = read_json(trajectory)
            # A documented infrastructure failure may be regenerated after RCA;
            # a completed model trajectory must only be graded, never regenerated.
            try:
                meta = _model_trajectory(data)
            except NativeInfrastructureError:
                continue
            if not meta.get("exit_status") or not isinstance(meta.get("patch"), str):
                raise ValueError("Saved native trajectory is not a complete model attempt")
            wires = [str(path) for path in sorted((destination / "requests").glob("*.json"))]
            config_path = destination / "config.toml"
            _validate_config_and_requests(
                config_path, wires, request, self.store.manifest(self.point_id)["configuration"], destination
            )
            result = destination / "check_results" / f"{request['task_id']}.json"
            if result.exists() and read_json(result).get("status") in ("resolved", "unresolved", "apply_patch_fail"):
                saved_runtime = read_json(path)["runtime"]
                _publish_outcome(
                    destination,
                    request,
                    saved_runtime,
                    trajectory,
                    result,
                    config_path,
                    wires,
                    self.store.reference_root,
                )
                return self._validated_outcome(destination, request, deadline_at), None
            if trajectory_source is not None and _sha(trajectory_source["path"]) != _sha(trajectory):
                raise ValueError("Different completed native trajectories exist for the same slot")
            trajectory_source = {"path": str(trajectory), "sha256": _sha(trajectory), "request_paths": wires}
        return None, trajectory_source


def _validate_config_and_requests(config_path, wires, request, configuration, destination):
    # The native child uses Python3.10/toml; the outer coordinator uses Python3.12.
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        import toml as tomllib

    config = tomllib.loads(Path(config_path).read_text())
    if _config_contract(config) != configuration["native_config"]:
        raise ValueError("Saved native harness configuration differs from the immutable manifest")
    if config["model"]["inference_args"]["seed"] != request["seed"]:
        raise ValueError("Saved native config has a different seed")
    ids = [row["instance_id"] for row in read_json(config["dataset"]["name_or_path"])]
    if config["dataset"]["range_str"] != str(ids.index(request["task_id"])):
        raise ValueError("Saved native dataset range has a different task")
    if not wires:
        raise ValueError("Native agent did not issue an observed model request")
    for path in wires:
        if not Path(path).resolve().is_relative_to(destination.resolve()):
            raise ValueError("Saved native request escaped the attempt")
        row = read_json(path)
        body = row["body"]
        if (body["temperature"], body["top_p"], body["seed"], row["n"]) != (
            1.0,
            0.95,
            request["seed"],
            1,
        ) or "top_k" in body:
            raise ValueError("Actual request sampling differs from the frozen contract")
        if row["url"] != config["model"]["inference_args"]["custom_upstream_url"]:
            raise ValueError("Saved native request endpoint differs from its config")


def _publish_outcome(destination, request, runtime, trajectory, result, config_path, wires, reference_root):
    success = native_outcome(request["task_id"], trajectory, result, reference_root)
    raw = {
        "native_artifacts": {
            name: {"path": str(path), "sha256": _sha(path)}
            for name, path in (("trajectory", trajectory), ("grader", result), ("config", config_path))
        },
        "request_paths": wires,
        "request_sha256": {path: _sha(path) for path in wires},
        "swe_commit": SWE_COMMIT,
        "max_tokens_observed": [read_json(path)["max_tokens"] for path in wires],
        "max_tokens_override": False,
        "server_identity": runtime["server_identity"],
    }
    write_json(destination / "outcome.json", {"success": success, "raw": raw})


async def _stop_child_tree(process, grace):
    with contextlib.suppress(ProcessLookupError):
        os.killpg(process.pid, signal.SIGTERM)
    if process.returncode is None:
        try:
            await asyncio.wait_for(process.wait(), timeout=grace)
        except asyncio.TimeoutError:
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
            await process.wait()
    # A parent exit does not prove that a grader descendant has exited.
    with contextlib.suppress(ProcessLookupError):
        os.killpg(process.pid, signal.SIGKILL)
    deadline = time.monotonic() + grace
    while _live_group_members(process.pid):
        if time.monotonic() >= deadline:
            raise RuntimeError("Native child group has not exited; preserve its HF reader")
        await asyncio.sleep(0.05)


def _live_group_members(group_id):
    members = []
    for path in Path("/proc").glob("[0-9]*/stat"):
        try:
            fields = path.read_text().rsplit(")", 1)[1].split()
        except (FileNotFoundError, ProcessLookupError):
            continue
        if int(fields[2]) == group_id and fields[0] not in ("Z", "X"):
            members.append(int(path.parent.name))
    return members


@contextlib.contextmanager
def _capture_requests(destination, endpoint, deadline_at):
    """Capture actual HTTP JSON and bound native in-flight time by remaining deadlines."""
    import requests
    import swe_agents.cli.run as run_cli

    original_post = requests.post
    original_deadline = run_cli.agent_loop_retry_deadline
    local = threading.local()
    sequence = 0

    @contextlib.contextmanager
    def agent_deadline(seconds):
        local.deadline = time.time() + seconds
        try:
            with original_deadline(seconds):
                yield
        finally:
            local.deadline = None

    def post(url, *args, **kwargs):
        nonlocal sequence
        if url == endpoint:
            remaining = min(deadline_at, local.deadline or deadline_at) - time.time()
            if remaining <= 0:
                raise TimeoutError("Native request has exhausted the original deadline")
            # Native sync HTTP defaults to 3000s; only the remaining deadline may shorten it.
            kwargs["timeout"] = min(kwargs["timeout"], remaining)
            path = destination / "requests" / f"{sequence:06d}.json"
            sequence += 1
            payload = kwargs["json"]
            write_json(
                path,
                {
                    "url": url,
                    "body": payload,
                    "http_timeout_seconds": kwargs["timeout"],
                    "started_at": time.time(),
                    "deadline_at": deadline_at,
                    "max_tokens": payload.get("max_tokens"),
                    "n": payload.get("n", 1),
                },
            )
        return original_post(url, *args, **kwargs)

    requests.post = post
    run_cli.agent_loop_retry_deadline = agent_deadline
    try:
        yield
    finally:
        requests.post = original_post
        run_cli.agent_loop_retry_deadline = original_deadline


def native_child(invocation_path):
    import step_align.model.stepchat as stepchat
    import swe_agents.cli.run as run_cli
    import swe_agents.models.step_align as model_module
    import toml
    from playground.agenticeval.sweagents_swe import RunCheckPipeline

    invocation = read_json(invocation_path)
    # Both repositories have a top-level tests package. Load the pinned reference
    # by filename so Miles' tests package cannot shadow its scorer module.
    reference_swe = Path(invocation["reference_root"]) / "tests/e2e/mopd_step3p6_bounded_replay/swe_formal.py"
    if invocation["runtime"]["source_sha256"].get(str(reference_swe)) != _sha(reference_swe):
        raise ValueError("Reference scorer is not pinned by this invocation")
    runtime, request = invocation["runtime"], invocation["request"]
    manifest = read_json(invocation["point_manifest"])
    _verify_runtime(runtime, manifest["configuration"])
    # Check loaded modules, not just files that happen to be present on disk.
    for module in (run_cli, model_module, stepchat, sys.modules[RunCheckPipeline.__module__]):
        path = str(Path(module.__file__).resolve())
        if runtime["source_sha256"].get(path) != _sha(path):
            raise ValueError(f"Loaded native module is not pinned: {path}")
    destination = Path(invocation_path).parent
    rows = read_json(runtime["dataset_path"])
    ids = [row["instance_id"] for row in rows]
    config = native_config(runtime, request=request, dataset_index=ids.index(request["task_id"]))
    if _config_contract(config) != manifest["configuration"]["native_config"]:
        raise ValueError("Native harness configuration differs from the immutable point manifest")
    config_path = destination / "config.toml"
    config_path.write_text(toml.dumps(config))
    pipeline = RunCheckPipeline(eval_config_path=config_path, work_dir=destination)
    # The reference pipeline's grader subprocess otherwise uses its worktree submodule.
    pipeline._swe_agents_src = Path(runtime["swe_source_root"]) / "src"
    if len(pipeline.instances) != 1 or pipeline.instances[0]["instance_id"] != request["task_id"]:
        raise ValueError("Native dataset range returned a different slot")
    instance = pipeline.instances[0]
    trajectory_source = invocation["trajectory_source"]
    if trajectory_source is not None:
        source = Path(trajectory_source["path"])
        if (
            not source.resolve().is_relative_to(Path(invocation["point_manifest"]).parent.resolve())
            or _sha(source) != trajectory_source["sha256"]
        ):
            raise ValueError("Completed native trajectory changed before check-only recovery")
        _model_trajectory(read_json(source))
        target = pipeline._traj_path(request["task_id"], 0)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        # Retain the original observed requests byte-for-byte; check-only must
        # neither query the model nor fabricate new generation evidence.
        for index, path in enumerate(trajectory_source["request_paths"]):
            target = destination / "requests" / f"{index:06d}.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        original_config = toml.loads((source.parent.parent / "config.toml").read_text())
        config["model"]["inference_args"]["custom_upstream_url"] = original_config["model"]["inference_args"][
            "custom_upstream_url"
        ]
        config_path.write_text(toml.dumps(config))
    endpoint = config["model"]["inference_args"]["custom_upstream_url"]
    with _capture_requests(destination, endpoint, invocation["deadline_at"]):
        if trajectory_source is None:
            pipeline._run_instance(instance, 0)
        pipeline._check_instance_task(instance, 0)
    trajectory, result = pipeline._traj_path(request["task_id"], 0), pipeline._check_result_path(request["task_id"], 0)
    wires = [str(path) for path in sorted((destination / "requests").glob("*.json"))]
    _validate_config_and_requests(config_path, wires, request, manifest["configuration"], destination)
    _publish_outcome(
        destination, request, runtime, trajectory, result, config_path, wires, invocation["reference_root"]
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--invocation", required=True)
    args = parser.parse_args()

    def terminate(signum, frame):
        raise KeyboardInterrupt("Native evaluator termination; close the active environment")

    signal.signal(signal.SIGTERM, terminate)
    native_child(args.invocation)


if __name__ == "__main__":
    main()
