"""Dedicated H800 worker probe of native SWE teacher scoring; no generation.

The parent allocates one teacher node using the formal config's pinned image,
model mounts and CUDA environment. This probe never submits or stops RJobs and
never changes production payloads. Run from the configured repository:

    python3 -B -m tests.manual.agent_opd.probe_teacher_scoring \
        --config FORMAL_CONFIG --pair A --samples FIXED_SAMPLES.json \
        --output-dir NEW_OUTPUT_DIR --repeats 2 --request-timeout 3600

Cold comparisons flush before each request. Separate warm passes flush once
before each mode's ordered sample stream. Mode order alternates by repetition
and, for cold comparisons, sample position. Numerical errors are observations,
not tolerance-based acceptance. Worker-local raw bodies/caches are not archived.
"""

import argparse
import asyncio
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

_TASK_ID = "profile-teacher-scoring-probe-20261111"
_MODES = ("full_input", "response_only")
_SGLANG_SOURCES = (
    "srt/entrypoints/http_server.py",
    "srt/managers/io_struct.py",
    "srt/managers/tokenizer_manager.py",
    "srt/managers/scheduler.py",
    "srt/managers/schedule_batch.py",
    "srt/layers/logits_processor.py",
    "srt/model_executor/model_runner.py",
    "srt/mem_cache/radix_cache.py",
    "srt/models/qwen3_5.py",
)


def _positive_float(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("must be finite and positive")
    return number


def _positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be positive")
    return number


def _parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--pair", choices=("A", "B"), required=True)
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--repeats", type=_positive_int, required=True)
    parser.add_argument("--request-timeout", type=_positive_float, required=True)
    return parser


def _write(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def _append(path, value):
    with path.open("a") as stream:
        stream.write(json.dumps(value, allow_nan=False) + "\n")


def _file_identity(path):
    return {"path": str(path), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def _load_samples(path, context_tokens):
    fixture = json.loads(path.read_text())
    if not isinstance(fixture["job"], str) or not fixture["job"] or not fixture["samples"]:
        raise ValueError("Fixture requires a historical job and nonempty samples")
    identities = set()
    for sample in fixture["samples"]:
        uid, index, tokens, response = (sample[key] for key in (
            "source_uid", "sample_index", "tokens", "response_length"))
        if not isinstance(uid, str) or not uid or type(index) is not int or index < 0:
            raise ValueError("Sample requires a nonempty source_uid and nonnegative integer sample_index")
        identity = (uid, index)
        if identity in identities:
            raise ValueError(f"Duplicate sample identity: {identity}")
        identities.add(identity)
        if not isinstance(tokens, list) or any(type(token) is not int or token < 0 for token in tokens):
            raise ValueError(f"Sample {identity} tokens must be nonnegative integer IDs")
        if type(response) is not int or not 0 < response < len(tokens) <= context_tokens:
            raise ValueError(f"Sample {identity} must contain a prompt and completion within context_tokens")
        expected = sample.get("expected_teacher_log_probs")
        if expected is not None and (not isinstance(expected, list) or len(expected) != response
                                    or any(type(x) not in (int, float) or not math.isfinite(x) for x in expected)):
            raise ValueError(f"Sample {identity} historical log probabilities must be finite and completion-aligned")
    return fixture


def _load_config(path, pair, output):
    # Worker-only imports keep Python 3.10 controller --help dependency-free.
    from tests.manual.agent_opd.run_qwen35_opd import _PERSONAL_ROOT, _READ_ONLY_MODELS

    config = json.loads(path.read_text())
    teacher = config["pairs"][pair]["teacher"]
    if config["gpu_tag"] != "H800" or config["charged_group"] != "codesign":
        raise ValueError("This dedicated probe requires H800/codesign")
    if not config["image"] or not config["worker_python"]:
        raise ValueError("The pinned image and worker_python must be explicit")
    if Path(sys.executable).resolve() != Path(config["worker_python"]).resolve():
        raise ValueError("Run the probe with the configured worker_python")
    if teacher["nodes"] != 1 or teacher["tp_size"] != teacher["gpus_per_node"]:
        raise ValueError("Probe requires one teacher node with the formal TP and GPU allocation")
    for key in ("gpus_per_node", "tp_size", "max_running_requests", "chunked_prefill_size"):
        if type(teacher[key]) is not int or teacher[key] <= 0:
            raise ValueError(f"Teacher {key} must be a positive integer")
    if not 0 < teacher["mem_fraction_static"] < 1:
        raise ValueError("Teacher mem_fraction_static must be in (0, 1)")
    config["startup_timeout"] = _positive_float(config["pairs"][pair]["startup_timeout"])
    if type(config["context_tokens"]) is not int or config["context_tokens"] <= 0:
        raise ValueError("context_tokens must be an explicit positive integer")
    for key in ("teacher_port", "teacher_dist_port"):
        if type(config[key]) is not int or not 0 < config[key] < 65536:
            raise ValueError(f"{key} must be a TCP port")
    source = Path(teacher["path"])
    if (not source.is_absolute() or ".." in source.parts
            or (not source.is_relative_to(_PERSONAL_ROOT) and source not in _READ_ONLY_MODELS)
            or (not source.resolve().is_relative_to(_PERSONAL_ROOT) and source.resolve() not in _READ_ONLY_MODELS)):
        raise ValueError("Teacher source must be personal or an exactly approved read-only model")
    mount, local = Path(config["local_mount"]).resolve(), Path(config["worker_local_root"]).resolve()
    if not mount.is_absolute() or mount.is_relative_to("/mnt") or local.is_relative_to("/mnt"):
        raise ValueError("Workspace and worker_local_root must be local, not cloud paths")
    for item in (path.resolve(), Path(config["repo"]).resolve()):
        if not item.is_relative_to(mount):
            raise ValueError("Config and repo must resolve under local_mount")
    if output.is_relative_to("/mnt"):
        if not output.is_relative_to(_PERSONAL_ROOT):
            raise ValueError("Cloud outputs must stay in the personal namespace")
    elif not output.is_relative_to(mount):
        raise ValueError("Retained local output must resolve under local_mount")
    if output == source.resolve() or output.is_relative_to(source.resolve()) or source.resolve().is_relative_to(output):
        raise ValueError("Output must be disjoint from the read-only model source")
    return config


def _payload(sample, mode):
    from miles.rollout.on_policy_distillation import _score_payload

    if mode not in _MODES:
        raise ValueError(f"Unknown probe mode: {mode}")
    if mode == "response_only":
        return _score_payload(sample["tokens"], response_length=sample["response_length"])
    return _score_payload(sample["tokens"])


def _meta_summary(value):
    if isinstance(value, dict):
        return {key: _meta_summary(item) for key, item in value.items()}
    if isinstance(value, list):
        return {"omitted_array_length": len(value)}
    if isinstance(value, float) and not math.isfinite(value):
        return {"nonfinite": str(value)}
    return value


def _scores(body, sample, record):
    from miles.rollout.on_policy_distillation import _trim_input_field

    record.update(token_ids_match=False, finite_log_probs=False)
    meta = body["meta_info"]
    record["meta_info"] = _meta_summary(meta)
    raw_scores = meta.get("input_token_logprobs")
    record["input_token_logprobs_count"] = len(raw_scores) if isinstance(raw_scores, list) else None
    record.update(first_input_token_logprob=None, first_input_token_id=None)
    if isinstance(raw_scores, list) and raw_scores and isinstance(raw_scores[0], list) and len(raw_scores[0]) >= 2:
        record["first_input_token_logprob"] = _meta_summary(raw_scores[0][0])
        record["first_input_token_id"] = _meta_summary(raw_scores[0][1])
    scores = _trim_input_field(meta, "input_token_logprobs", sample["response_length"])
    ids = [item[1] for item in scores]
    values = [float(item[0]) for item in scores]
    record["returned_completion_count"] = len(scores)
    record["token_ids_match"] = ids == sample["tokens"][-sample["response_length"]:]
    record["finite_log_probs"] = all(math.isfinite(value) for value in values)
    record["completion_token_id_mismatches"] = [
        {"position": position, "expected": expected, "actual": _meta_summary(actual)}
        for position, (expected, actual) in enumerate(zip(sample["tokens"][-sample["response_length"]:], ids))
        if expected != actual
    ]
    record["nonfinite_log_prob_positions"] = [position for position, value in enumerate(values) if not math.isfinite(value)]
    if not record["token_ids_match"] or not record["finite_log_probs"]:
        raise ValueError("Teacher completion IDs differ from fixed tokens or scores are nonfinite")
    if meta.get("output_token_logprobs") or body.get("output_ids"):
        raise ValueError("Scoring-only request unexpectedly generated tokens")
    return {"token_ids": ids, "log_probs": values}


def _comparison(reference, candidate):
    ids_match = reference["token_ids"] == candidate["token_ids"]
    left, right = reference["log_probs"], candidate["log_probs"]
    finite = all(math.isfinite(x) for x in left + right)
    result = {"token_ids_match": ids_match, "finite_log_probs": finite,
              "values_exact": False, "max_absolute_error": None, "max_relative_error": None,
              "relative_error_undefined_count": None, "accepted": None}
    if not ids_match or not finite or len(left) != len(right) or not left:
        return result
    errors = [abs(a - b) for a, b in zip(left, right)]
    relative = [error / abs(a) for a, error in zip(left, errors) if a != 0]
    result.update(values_exact=left == right, max_absolute_error=max(errors),
                  max_relative_error=max(relative) if relative else None,
                  relative_error_undefined_count=sum(a == 0 for a in left))
    return result


async def _http(method, url, payload, timeout, record):
    # Native _post_json hides read/parse boundaries; use its existing aiohttp dependency directly.
    import aiohttp

    started = time.perf_counter()
    record.update({key: None for key in ("http_time_to_headers_seconds", "http_status", "body_read_seconds",
                                        "body_bytes", "content_length_header", "content_encoding_header")})
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.request(method, url, **({"json": payload} if payload is not None else {})) as response:
                record["http_time_to_headers_seconds"] = time.perf_counter() - started
                record["http_status"] = response.status
                record["content_length_header"] = response.headers.get("Content-Length")
                record["content_encoding_header"] = response.headers.get("Content-Encoding")
                reading = time.perf_counter()
                try:
                    raw = await response.read()
                finally:
                    record["body_read_seconds"] = time.perf_counter() - reading
                record["body_bytes"] = len(raw)
                response.raise_for_status()
                return raw
    finally:
        record["http_elapsed_seconds"] = time.perf_counter() - started


def _parse(raw, record):
    started = time.perf_counter()
    try:
        return json.loads(raw)
    finally:
        record["json_parse_seconds"] = time.perf_counter() - started


async def _flush(url, timeout, path, identity):
    import aiohttp

    record = {**identity, "endpoint": url + "/flush_cache", "status": "failed"}
    try:
        raw = await _http("POST", record["endpoint"], None, timeout, record)
        record.update(status="flushed", response_text=raw.decode(errors="replace"))
    except aiohttp.ClientResponseError as error:
        if error.status not in (404, 405, 501):
            record.update(error_type=type(error).__name__, reason=str(error))
            raise
        record.update(status="cache_undefined", error_type=type(error).__name__, reason=str(error))
    except BaseException as error:
        record.update(error_type=type(error).__name__, reason=str(error))
        raise
    finally:
        _append(path, record)
    return record["status"]


async def _request(url, sample, mode, timeout, output, local, identity, cache_state):
    payload = _payload(sample, mode)
    request_id = f"{identity['phase']}-r{identity['repetition']}-s{identity['sample_position']}-{mode}"
    record = {**identity, "request_id": request_id, "mode": mode, "source_uid": sample["source_uid"],
              "sample_index": sample["sample_index"], "input_count": len(sample["tokens"]),
              "prompt_count": len(sample["tokens"]) - sample["response_length"],
              "response_count": sample["response_length"], "logprob_start_len": payload["logprob_start_len"],
              "expected_input_token_logprobs_count": len(sample["tokens"]) - payload["logprob_start_len"],
              "first_requested_input_token_id": sample["tokens"][payload["logprob_start_len"]],
              "cache_state": cache_state, "status": "failed", "started_at": time.time(),
              "token_ids_match": False, "finite_log_probs": False}
    record.update({key: None for key in ("http_time_to_headers_seconds", "http_elapsed_seconds", "body_read_seconds",
                                        "http_status", "body_bytes", "json_parse_seconds", "validation_seconds",
                                        "returned_completion_count", "input_token_logprobs_count",
                                        "first_input_token_logprob", "first_input_token_id")})
    started = time.perf_counter()
    try:
        raw = await _http("POST", url + "/generate", payload, timeout, record)
        # Full response JSON stays worker-local, including invalid native responses.
        with (local / f"{request_id}.json").open("xb") as stream:
            stream.write(raw)
        body = _parse(raw, record)
        validating = time.perf_counter()
        try:
            vector = _scores(body, sample, record)
        finally:
            record["validation_seconds"] = time.perf_counter() - validating
        destination = output / "completion_scores" / f"{request_id}.json"
        _write(destination, {**identity, "request_id": request_id, "mode": mode,
                             "source_uid": sample["source_uid"], "sample_index": sample["sample_index"], **vector})
        record.update(status="scored", completion_scores=str(destination))
        return vector, request_id
    except BaseException as error:
        record.update(error_type=type(error).__name__, reason=str(error))
        raise
    finally:
        record["elapsed_seconds"] = time.perf_counter() - started
        _append(output / "requests.jsonl", record)


def _mode_order(repetition, sample_position=0):
    return _MODES if (repetition + sample_position) % 2 == 0 else tuple(reversed(_MODES))


def _record_comparison(output, identity, results, sample, pair):
    full, full_id = results["full_input"]
    response, response_id = results["response_only"]
    record = {**identity, "source_uid": sample["source_uid"], "sample_index": sample["sample_index"],
              "full_request_id": full_id, "response_request_id": response_id,
              "full_vs_response_only": _comparison(full, response), "historical_expected": None}
    if pair == "A" and sample.get("expected_teacher_log_probs") is not None:
        expected = {"token_ids": sample["tokens"][-sample["response_length"]:],
                    "log_probs": sample["expected_teacher_log_probs"]}
        record["historical_expected"] = {
            "scope": "Caller-provided historical A teacher scores; not a B teacher reference",
            "full_input": _comparison(expected, full), "response_only": _comparison(expected, response),
        }
    _append(output / "comparisons.jsonl", record)


async def _benchmark(args, fixture, url, output, local):
    server_request = {"endpoint": url + "/get_server_info"}
    info = _parse(await _http("GET", server_request["endpoint"], None, args.request_timeout, server_request), server_request)
    _write(output / "server_info.json", {"http": server_request, "get_server_info": info})
    cache_observations = {"cold_cache_verified": True, "warm_stream_initial_flush_verified": True}
    for repetition in range(args.repeats):
        for position, sample in enumerate(fixture["samples"]):
            identity = {"phase": "cold", "repetition": repetition, "sample_position": position}
            results = {}
            for mode in _mode_order(repetition, position):
                cache = await _flush(url, args.request_timeout, output / "cache.jsonl", {**identity, "mode": mode})
                cache_observations["cold_cache_verified"] &= cache == "flushed"
                results[mode] = await _request(url, sample, mode, args.request_timeout, output, local, identity,
                                               "cold_flushed" if cache == "flushed" else "cache_undefined")
            _record_comparison(output, identity, results, sample, args.pair)
    for repetition in range(args.repeats):
        results = [{} for _ in fixture["samples"]]
        for mode in _mode_order(repetition):
            stream_id = {"phase": "warm_stream", "repetition": repetition, "mode": mode}
            cache = await _flush(url, args.request_timeout, output / "cache.jsonl", stream_id)
            cache_observations["warm_stream_initial_flush_verified"] &= cache == "flushed"
            for position, sample in enumerate(fixture["samples"]):
                identity = {"phase": "warm_stream", "repetition": repetition, "sample_position": position}
                state = ("stream_first_after_flush" if position == 0 else "ordered_stream_after_flush") if cache == "flushed" else "cache_undefined"
                results[position][mode] = await _request(url, sample, mode, args.request_timeout, output, local, identity, state)
        for position, sample in enumerate(fixture["samples"]):
            identity = {"phase": "warm_stream", "repetition": repetition, "sample_position": position}
            _record_comparison(output, identity, results[position], sample, args.pair)
    return cache_observations


def _runtime(config, pair):
    root = Path(importlib.util.find_spec("sglang").origin).parent
    sources = {name: _file_identity(root / name) for name in _SGLANG_SOURCES}
    # Capture the actual scheduler/cache/model decomposition, including worker fork changes.
    for pattern in ("srt/managers/scheduler*.py", "srt/managers/scheduler_components/*.py",
                    "srt/mem_cache/*radix*.py", "srt/models/qwen3_5*.py"):
        for path in sorted(root.glob(pattern)):
            sources[str(path.relative_to(root))] = _file_identity(path)
    gpu = subprocess.check_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                                   "--format=csv,noheader"], text=True, timeout=config["startup_timeout"]).strip().splitlines()
    if len(gpu) != config["pairs"][pair]["teacher"]["gpus_per_node"] or any("H800" not in row for row in gpu):
        raise ValueError(f"Worker GPU allocation differs from the configured H800 teacher: {gpu}")
    model = Path(config["pairs"][pair]["teacher"]["path"])
    return {"python": platform.python_version(), "executable": sys.executable,
            "sglang": importlib.metadata.version("sglang"), "torch": importlib.metadata.version("torch"),
            "sglang_sources": sources, "configured_image": config["image"],
            "image_identity_limit": "Image digest is the parent allocation input, not independently inspected container metadata",
            "gpu_devices": gpu, "model_path": str(model),
            "model_manifest_identity": {name: _file_identity(model / name) for name in ("config.json", "model.safetensors.index.json")},
            "checkpoint_identity_limit": "Mounted source path and manifest hashes; no whole-weight checksum",
            "sglang_environment": {"SGLANG_FORCE_COARSE_WAR_BARRIER": os.environ.get("SGLANG_FORCE_COARSE_WAR_BARRIER")},
            "nccl_environment": {key: value for key, value in os.environ.items() if key.startswith("NCCL_")},
            "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES")}


def _run(args):
    from tests.manual.agent_opd import qwen35_pair_worker as paired
    from tests.manual.agent_opd.rjob_warmup import _worker_environment

    output = args.output_dir.resolve()
    config = _load_config(args.config.resolve(strict=True), args.pair, output)
    fixture = _load_samples(args.samples, config["context_tokens"])
    job = os.environ["KUBEBRAIN_RJOB_NAME"]
    if Path(job).name != job or job in ("", ".", ".."):
        raise ValueError("Platform job name must be a single directory component")
    if (int(os.environ["KUBEBRAIN_REPLICA"]), int(os.environ["KUBEBRAIN_REPLICA_TOTAL"])) != (0, 1):
        raise ValueError("Probe must run only on a new, dedicated single-node teacher task")
    local = Path(config["worker_local_root"]) / f"teacher-scoring-{job}-{args.pair}"
    output.mkdir(parents=True, exist_ok=False)
    process, local_created = None, False
    result = {"task_id": _TASK_ID, "job": job, "pair": args.pair, "historical_job": fixture["job"],
              "status": "failed", "native_measurements_completed": False,
              "cleanup_completed": False,
              "performance_accepted": False, "numerical_acceptance": None, "request_timeout": args.request_timeout,
              "repeats": args.repeats, "sample_count": len(fixture["samples"]), "worker_local_directory": str(local),
              "fixture": _file_identity(args.samples), "config": _file_identity(args.config),
              "expected_scoring_requests": 4 * len(fixture["samples"]) * args.repeats,
              "method": {"cold": "Flush before each mode/sample request; alternate order by repetition+sample position",
                         "warm_stream": "Flush once per mode stream; fixed sample order; alternate mode order by repetition",
                         "requests": "Sequential, same input IDs, native zero-generation payload; one aiohttp session per request",
                         "order_limit": "One repetition cannot balance both first-mode positions for each individual sample",
                         "timing": "perf_counter; headers include request serialization/server work; decoded body read, JSON parse and native tail validation measured separately",
                         "acceptance": "No performance PASS or numerical tolerance; primary judges observed differences"}}
    try:
        _worker_environment(local)
        local_created = True
        (output / "completion_scores").mkdir()
        result["runtime"] = _runtime(config, args.pair)
        result["native_scoring_sources"] = {name: _file_identity(Path(config["repo"]) / name) for name in (
            "miles/rollout/on_policy_distillation.py", "tests/manual/agent_opd/swe_replay.py",
            "tests/manual/agent_opd/qwen35_pair_worker.py", "tests/manual/agent_opd/probe_teacher_scoring.py")}
        command = paired._teacher_command(config, args.pair, 0, {"ip": os.environ["MILES_NODE_EXTERNAL_IP"]})
        result["argv"] = command
        _write(output / "preload.json", result)
        with (local / "server.log").open("x") as log:
            process = subprocess.Popen(command, cwd=config["repo"], stdout=log,
                                       stderr=subprocess.STDOUT, start_new_session=True)
            url = f"http://{os.environ['MILES_NODE_EXTERNAL_IP']}:{config['teacher_port']}"
            result["model_info"] = paired._wait_teacher_ready(
                process, url, config["pairs"][args.pair]["teacher"]["path"], local / "never-finished.json",
                config["startup_timeout"])
            if result["model_info"] is None:
                raise RuntimeError("Dedicated teacher readiness was interrupted")
            result["cache_observations"] = asyncio.run(_benchmark(args, fixture, url, output, local))
            paired._check_server(process)
        result.update(status="measurements_completed", native_measurements_completed=True)
    except BaseException as error:
        result.update(error_type=type(error).__name__, reason=str(error))
        raise
    finally:
        try:
            if process is not None:
                result["server_returncode_before_cleanup"] = process.poll()
                paired._stop_child(process)
                result["server_shutdown_returncode"] = process.poll()
            result["cleanup_completed"] = True
        except BaseException as error:
            result.update(status="failed", cleanup_error_type=type(error).__name__, cleanup_error=str(error))
            raise
        finally:
            try:
                if local_created and (local / "server.log").exists():
                    with (local / "server.log").open("rb") as source, (output / "server.log").open("xb") as destination:
                        shutil.copyfileobj(source, destination)
            except BaseException as error:
                result.update(status="failed", archive_error_type=type(error).__name__, archive_error=str(error))
                raise
            finally:
                _write(output / "result.json", result)
                print("TEACHER_SCORING_PROBE", result["status"], str(output), flush=True)


def _terminate(signum, frame):
    raise SystemExit(128 + signum)


def main():
    args = _parser().parse_args()
    previous = signal.signal(signal.SIGTERM, _terminate)
    try:
        _run(args)
    finally:
        signal.signal(signal.SIGTERM, previous)


if __name__ == "__main__":
    main()
