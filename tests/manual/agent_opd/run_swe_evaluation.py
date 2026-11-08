"""Run one admitted two-GPU SWE point, owning its server until safe release.

GPU worker command (pinned image Python3.12, no platform submission here):
    /opt/sglang/bin/python3 -B -m tests.manual.agent_opd.run_swe_evaluation \
        --configuration CONFIG.json --point POINT --allocation ADMISSION.json

The native role runs only in the configured repaired SWE Python3.10 environment.
Both roles reuse EvaluationStore/evaluate/NativeSweRunner; no alternative grader,
resubmission, automatic recovery, deadline renewal or completed-slot rescore exists.
For a small native qualification, use a separate root ending in /qualification-evaluations,
a qualification.<name> point, and explicit --qualification-attempt TASK#attempt-N.
Qualification retains the full manifest/missing ledger and never releases HF.
"""

import argparse
import asyncio
import copy
import json
import os
import signal
import socket
import sys
import time
import uuid
from pathlib import Path
from urllib.parse import urlsplit

import requests

from tests.manual.agent_opd import swe_native_evaluation as native
from tests.manual.agent_opd.rjob_budget import validate_allocation
from tests.manual.agent_opd.swe_evaluation import evaluate, read_json, store_from_config, write_json


def _server_command(config, manifest):
    runtime, server = config["runtime"], config["server"]
    identity = runtime["server_identity"]
    version = manifest["native_update"]["weight_version"] if manifest["owned"] else runtime["baseline_weight_version"]
    return [
        server["python"],
        "-B",
        "-m",
        "sglang.launch_server",
        "--model-path",
        manifest["checkpoint_dir"],
        "--tokenizer-path",
        manifest["checkpoint_dir"],
        "--host",
        "127.0.0.1",
        "--port",
        str(urlsplit(runtime["url"]).port),
        "--tp-size",
        "2",
        "--dtype",
        "bfloat16",
        "--context-length",
        str(identity["context_length"]),
        "--mem-fraction-static",
        str(server["mem_fraction_static"]),
        "--max-running-requests",
        str(server["max_running_requests"]),
        "--chunked-prefill-size",
        str(server["chunked_prefill_size"]),
        "--disable-cuda-graph",
        "--enable-deterministic-inference",
        "--attention-backend",
        "fa3",
        "--linear-attn-prefill-backend",
        "triton",
        "--weight-version",
        str(version),
        "--served-model-name",
        runtime["model_name"],
        "--tool-call-parser",
        identity["tool_call_parser"],
        "--reasoning-parser",
        identity["reasoning_parser"],
        "--chat-template",
        server["chat_template"],
        "--default-chat-template-kwargs",
        json.dumps({"preserve_thinking": True, "enable_thinking": True}),
    ]


def _native_environment(config):
    runtime = config["runtime"]
    env = dict(os.environ)
    env.pop("PYTHONHOME", None)
    env.update(
        PYTHONPATH=os.pathsep.join(
            [
                config["server"]["repo"],
                runtime["swe_source_root"] + "/src",
                config["reference_root"],
                *runtime["python_paths"],
            ]
        ),
        PYTHONNOUSERSITE="1",
        PYTHONDONTWRITEBYTECODE="1",
        CUDA_VISIBLE_DEVICES="",
        WORLD_SIZE="1",
        HF_HUB_OFFLINE="1",
        TRANSFORMERS_OFFLINE="1",
        LOGURU_DIAGNOSE="NO",
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
    )
    return env


def _owned_listener(process, port):
    """A foreign server on the port is not an identity/readiness observation."""
    inodes = set()
    for name in ("tcp", "tcp6"):
        for row in Path("/proc/net", name).read_text().splitlines()[1:]:
            fields = row.split()
            if int(fields[1].rsplit(":", 1)[1], 16) == port and fields[3] == "0A":
                inodes.add(fields[9])
    for pid in native._live_group_members(process.pid):
        for descriptor in Path(f"/proc/{pid}/fd").glob("*"):
            try:
                target = os.readlink(descriptor)
            except (FileNotFoundError, ProcessLookupError):
                continue
            if target.startswith("socket:[") and target[8:-1] in inodes:
                return True
    return False


def _check_port(url):
    with socket.socket() as port_check:
        port_check.bind(("127.0.0.1", urlsplit(url).port))


def _check_identity(config, manifest, model, info):
    args = info.get("server_args", info)
    runtime, server = config["runtime"], config["server"]
    expected = runtime["server_identity"]
    path = Path(manifest["checkpoint_dir"]).resolve()
    for value in (model["model_path"], model["tokenizer_path"], args["model_path"], args["tokenizer_path"]):
        if Path(value).resolve() != path:
            raise ValueError("Actual server model/tokenizer path differs from this point")
    version = manifest["native_update"]["weight_version"] if manifest["owned"] else runtime["baseline_weight_version"]
    if str(model["weight_version"]) != str(version):
        raise ValueError("Actual server weight-version label differs from this publication")
    if info["version"] != expected["sglang_version"]:
        raise ValueError("Actual SGLang runtime differs from the supplied pinned-image observation")
    values = {
        "tp_size": 2,
        "dtype": "bfloat16",
        "context_length": expected["context_length"],
        "reasoning_parser": expected["reasoning_parser"],
        "tool_call_parser": expected["tool_call_parser"],
        "chat_template": server["chat_template"],
        "default_chat_template_kwargs": {"preserve_thinking": True, "enable_thinking": True},
    }
    if any(args.get(name) != value for name, value in values.items()):
        raise ValueError("Resolved native server settings differ from the Qwen evaluation contract")
    if model["served_model_name"] != runtime["model_name"] or any(
        model[name] != expected[name] for name in ("reasoning_parser", "tool_call_parser")
    ):
        raise ValueError("Actual model endpoint label/parsers differ from this point")
    if manifest["owned"] and model["architectures"] != ["Qwen3_5ForCausalLM"]:
        raise ValueError("The generated HF did not load through the pure-text architecture")
    if native._sha(server["chat_template"]) != expected["chat_template_sha256"]:
        raise ValueError("The fixed Qwen template changed")
    return {**expected, "model_path": str(path), "weight_version": model["weight_version"]}


async def _wait_server(process, config, manifest, deadline):
    url, server = config["runtime"]["url"], config["server"]
    while time.time() < deadline:
        if process.returncode is not None:
            raise RuntimeError(f"Owned SGLang server exited during startup: {process.returncode}")
        if not _owned_listener(process, urlsplit(url).port):
            await asyncio.sleep(1)
            continue
        try:
            observed = []
            for endpoint in ("health", "model_info", "server_info"):
                response = await asyncio.to_thread(
                    requests.get, url + "/" + endpoint, timeout=min(server["request_timeout"], deadline - time.time())
                )
                response.raise_for_status()
                if endpoint != "health":
                    observed.append(response.json())
        except requests.RequestException:
            await asyncio.sleep(1)
            continue
        model, info = observed
        return _check_identity(config, manifest, model, info), {"model_info": model, "server_info": info}
    raise TimeoutError("Owned SGLang server did not become ready before the startup/original deadline")


def _validate_qwen_runtime(config):
    """GPU Python3.12 owns the actual Qwen registry/parser validation."""
    from miles.utils.chat_template_utils.tito_tokenizer import Qwen35TITOTokenizer, resolve_fixed_chat_template

    runtime, identity = config["runtime"], config["runtime"]["server_identity"]
    template, _ = resolve_fixed_chat_template("qwen35")
    expected = {
        "tool_call_parser": Qwen35TITOTokenizer.tool_call_parser,
        "reasoning_parser": Qwen35TITOTokenizer.reasoning_parser,
        "context_length": config["evaluation_contract"]["native_config"]["model"]["max_context_tokens"],
        "preserve_thinking": True,
        "enable_thinking": True,
        "chat_template_sha256": native._sha(template),
    }
    if any(identity[name] != value for name, value in expected.items()) or any(
        Path(path).resolve() != Path(template).resolve()
        for path in (runtime["chat_template"], config["server"]["chat_template"])
    ):
        raise ValueError("Need the registered Qwen parsers, fixed template, full context and preserved thinking")


def _qualification_requests(store, point_id, attempt_ids):
    namespace = store.root.name == "qualification-evaluations"
    qualification_point = point_id.startswith("qualification.")
    if attempt_ids is None:
        if namespace or qualification_point:
            raise ValueError("Qualification namespace requires explicit --qualification-attempt selection")
        return None
    if not namespace or not qualification_point:
        raise ValueError(
            "Qualification requires a separate /qualification-evaluations store and qualification.<name> point"
        )
    if not attempt_ids or len(set(attempt_ids)) != len(attempt_ids):
        raise ValueError("Qualification requires distinct explicit task#attempt-N identities")
    manifest = store.manifest(point_id)
    requests_by_uid = {
        request["uid"]: request
        for task in manifest["task_ids"]
        for attempt in range(4)
        for request in [store.request(point_id, task, attempt)]
    }
    if any(uid not in requests_by_uid for uid in attempt_ids):
        raise ValueError("Qualification attempt must be an exact slot from the frozen 100x4 manifest")
    missing = set(store.summary(point_id)["missing_attempt_ids"])
    if not missing.difference(attempt_ids):
        raise ValueError("Qualification must leave unexecuted slots missing, not complete a benchmark point")
    return tuple(requests_by_uid[uid] for uid in attempt_ids)


async def _qualification_run(store, point_id, *, runner, allocation, requests):
    """Execute only explicit missing slots through the reviewed native runner/scorer."""
    metadata = {
        "run_kind": "qualification",
        "point_id": point_id,
        "requested_attempt_ids": [request["uid"] for request in requests],
    }
    if not store.start(point_id, allocation=allocation):
        return {**metadata, "status": store.state(point_id)["status"], "summary": store.summary(point_id)}
    reader_id = "qualification-evaluator-" + uuid.uuid4().hex
    store.reader_enter(point_id, reader_id, {**metadata, "pid": os.getpid(), "allocation": allocation})
    deadline = store.state(point_id)["deadline_at"]
    missing = set(store.summary(point_id)["missing_attempt_ids"])
    executed = []
    try:
        for request in requests:
            if request["uid"] not in missing:
                continue
            remaining = deadline - time.time()
            if remaining <= 0:
                break
            executed.append(request["uid"])
            try:
                outcome = await asyncio.wait_for(runner(request, deadline), timeout=remaining)
                store.record(point_id, request, success=outcome["success"], raw=outcome["raw"])
            except Exception as error:
                store.infra_failure(point_id, request, {"type": type(error).__name__, "message": str(error)})
            await asyncio.sleep(0)
    finally:
        # NativeSweRunner joins each owned child before returning or raising.
        store.reader_exit(point_id, reader_id, {**metadata, "requests_finished": True, "at": time.time()})
        summary = store.settle(point_id)
        receipt = {
            **metadata,
            "executed_attempt_ids": executed,
            "deadline_at": deadline,
            "status": store.state(point_id)["status"],
            "summary": summary,
        }
        write_json(store._point(point_id) / "qualification_runs" / (reader_id + ".json"), receipt)
    return receipt


async def _native_run(config, point_id, *, qualification_attempts=None):
    task = asyncio.current_task()
    loop = asyncio.get_running_loop()
    # Graceful parent termination must join the four independently session-owned children.
    loop.add_signal_handler(signal.SIGTERM, task.cancel)
    store = store_from_config(config)
    requests = _qualification_requests(store, point_id, qualification_attempts)
    runner = native.NativeSweRunner(store, point_id, config["runtime"])
    if requests is not None:
        return await _qualification_run(
            store, point_id, runner=runner, allocation=config["allocation"], requests=requests
        )
    return await evaluate(store, point_id, runner=runner, allocation=config["allocation"])


async def run_point(config, point_id, allocation, *, qualification_attempts=None):
    store = store_from_config(config)
    requests = _qualification_requests(store, point_id, qualification_attempts)
    if allocation.get("eval_gpus") != 2 or allocation["admission"]["requested_gpus"] != 2:
        raise ValueError("This worker requires one admitted single-node two-GPU allocation")
    validate_allocation(allocation, requested_gpus=2, expected=store.allocation_identity)
    manifest, state = store.manifest(point_id), store.state(point_id)
    if requests is None and state["status"] in ("COMPLETE", "RELEASING", "RELEASED"):
        return {"summary": store.summary(point_id), "release": store.release(point_id)}
    if state["status"] != "QUEUED" or any(row["status"] != "EXITED" for row in state["readers"].values()):
        raise ValueError("Parent must diagnose/resume missing slots and prove old readers exited before launch")
    if manifest["configuration"] != config["evaluation_contract"]:
        raise ValueError("Worker configuration differs from the immutable queued point")
    _validate_qwen_runtime(config)
    config = copy.deepcopy(config)
    reader_id = "server-" + uuid.uuid4().hex
    config["runtime"]["server_reader_id"] = reader_id
    directory = store._point(point_id) / "workers" / reader_id
    directory.mkdir(parents=True)
    command = _server_command(config, manifest)
    evidence = {"worker_pid": os.getpid(), "allocation": allocation, "command": command, "at": time.time()}
    server_process = evaluator = None
    result = {"status": "FAILED", "server_reader_id": reader_id, "evidence": str(directory)}
    qualification = (
        {}
        if requests is None
        else {
            "run_kind": "qualification",
            "point_id": point_id,
            "requested_attempt_ids": [request["uid"] for request in requests],
        }
    )
    evidence.update(qualification)
    result.update(qualification)
    # Register BEFORE any server startup/model load, including partial startup failures.
    store.reader_enter(point_id, reader_id, evidence)
    try:
        write_json(directory / "start.json", evidence)
        deadline = time.time() + config["server"]["startup_timeout"]
        if state["deadline_at"] is not None:
            deadline = min(deadline, state["deadline_at"])
        if deadline <= time.time():
            raise TimeoutError("Original evaluation deadline expired; do not start or renew it")
        _check_port(config["runtime"]["url"])
        with (directory / "server.log").open("x") as log:
            server_process = await asyncio.create_subprocess_exec(
                *command,
                cwd=config["server"]["repo"],
                stdout=log,
                stderr=asyncio.subprocess.STDOUT,
                start_new_session=True,
            )
            identity, observed = await _wait_server(server_process, config, manifest, deadline)
            config["runtime"]["server_identity"] = identity
            config["allocation"] = allocation
            write_json(
                directory / "server.json",
                {
                    "pid": server_process.pid,
                    **observed,
                    "identity": identity,
                    **qualification,
                },
            )
            write_json(directory / "configuration.json", config)
            with (directory / "evaluator.log").open("x") as native_log:
                evaluator = await asyncio.create_subprocess_exec(
                    config["runtime"]["python"],
                    "-B",
                    "-m",
                    "tests.manual.agent_opd.run_swe_evaluation",
                    "--native",
                    "--configuration",
                    str(directory / "configuration.json"),
                    "--point",
                    point_id,
                    *[arg for request in requests or () for arg in ("--qualification-attempt", request["uid"])],
                    cwd=config["server"]["repo"],
                    env=_native_environment(config),
                    stdout=native_log,
                    stderr=asyncio.subprocess.STDOUT,
                    start_new_session=True,
                )
                watchers = [asyncio.create_task(child.wait()) for child in (evaluator, server_process)]
                try:
                    done, _ = await asyncio.wait(watchers, return_when=asyncio.FIRST_COMPLETED)
                    if watchers[1] in done:
                        raise RuntimeError("Owned SGLang server exited before native evaluation finished")
                    if evaluator.returncode != 0:
                        raise RuntimeError(f"Native evaluation exited {evaluator.returncode}; inspect {directory}")
                finally:
                    for watcher in watchers:
                        watcher.cancel()
                    await asyncio.gather(*watchers, return_exceptions=True)
        result["status"] = store.state(point_id)["status"]
    except BaseException as error:
        result["error"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        try:
            try:
                if evaluator is not None:
                    await native._stop_child_tree(evaluator, config["server"]["cleanup_grace_seconds"])
            finally:
                if server_process is not None:
                    await native._stop_child_tree(server_process, config["server"]["cleanup_grace_seconds"])
                cleanup = {
                    "pid": None if server_process is None else server_process.pid,
                    "returncode": None if server_process is None else server_process.returncode,
                    "all_live_group_members_exited": True,
                    "at": time.time(),
                    **qualification,
                }
                write_json(directory / "cleanup.json", cleanup)
                store.reader_exit(point_id, reader_id, cleanup)
        except BaseException as error:
            result.update(status="CLEANUP_FAILED", cleanup_error={"type": type(error).__name__, "message": str(error)})
            raise
        finally:
            write_json(directory / "worker.json", result)
    summary = store.summary(point_id)
    result["summary"] = summary
    if requests is None and store.state(point_id)["status"] == "COMPLETE":
        result["release"] = store.release(point_id)
    write_json(directory / "worker.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configuration", type=Path, required=True)
    parser.add_argument("--point", required=True)
    parser.add_argument("--allocation", type=Path)
    parser.add_argument("--native", action="store_true")
    parser.add_argument(
        "--qualification-attempt",
        action="append",
        dest="qualification_attempts",
        help="Explicit frozen TASK_ID#attempt-N slot; repeat for a short qualification list in its separate namespace.",
    )
    args = parser.parse_args()
    config = read_json(args.configuration)
    if args.native:
        if (
            sys.version_info[:2] != (3, 10)
            or Path(sys.executable).resolve() != Path(config["runtime"]["python"]).resolve()
        ):
            raise ValueError("Native agent/grader must use the configured repaired Python3.10 interpreter")
        result = asyncio.run(_native_run(config, args.point, qualification_attempts=args.qualification_attempts))
    else:
        if args.allocation is None:
            parser.error("--allocation requires the actual submitted admission receipt")
        allocation = read_json(args.allocation)
        if os.environ["KUBEBRAIN_RJOB_NAME"] != allocation["job_id"]:
            raise ValueError("Submitted receipt does not belong to this actual worker job")
        if (int(os.environ["KUBEBRAIN_REPLICA_TOTAL"]), int(os.environ["KUBEBRAIN_REPLICA"])) != (1, 0):
            raise ValueError("Evaluation requires one native single-node worker")
        if (
            sys.version_info[:2] != (3, 12)
            or Path(sys.executable).resolve() != Path(config["server"]["python"]).resolve()
        ):
            raise ValueError("GPU worker must use the pinned image's configured Python3.12")
        # CUDA-only environment preparation is deferred out of the native3.10 role.
        from tests.manual.agent_opd.rjob_warmup import _worker_environment
        from tests.manual.agent_opd.run_qwen35_opd import _gpu_devices

        _gpu_devices(config["allocation_identity"]["gpu_tag"], 2)
        _worker_environment(Path(config["server"]["local_root"]) / ("swe-" + uuid.uuid4().hex))

        async def worker():
            asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, asyncio.current_task().cancel)
            return await run_point(config, args.point, allocation, qualification_attempts=args.qualification_attempts)

        result = asyncio.run(worker())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
