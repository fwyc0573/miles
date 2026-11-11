"""Dedicated H800 worker probe of native SWE teacher scoring; no generation.

The parent allocates one teacher node using the formal config's pinned image,
model mounts and CUDA environment. This probe never submits or stops RJobs and
never changes production payloads. Run from the configured repository:

    python3 -B -m tests.manual.agent_opd.probe_teacher_scoring \
        --config FORMAL_CONFIG --pair A --samples FIXED_SAMPLES.json \
        --output-dir NEW_OUTPUT_DIR --repeats 2 --request-timeout 3600

An isolated probe JSON may also be passed as --config; its formal_config keeps
the engine settings, and selected_fp32_snapshots selects source preparation.
Only true calls the qualified preparer before runtime inspection/server start.
Its retained receipt is source evidence, not measured CUDA snapshot behavior.
An opt-in mamba_runtime_metadata overlay follows selected-FP32 preparation and
reads the existing server-info endpoint once after all scoring requests. A
sample manifest may reference the original fixture and its first sample_count
entries without copying tokens or changing their source identities.
The opt-in kv_store_stream_witness preparer follows both source overlays and
uses the same metadata readback; preparation is not native stream validation.
The isolated kv_coherence_capture overlay requires a compiled production Rust
observer receipt. Its one post-loop drain returns compact numerical summaries,
not raw tensor archives, and remains uninterpreted until independent gates pass.
The cache_salt_full_input experiment namespaces only full-input requests by pair
and pre-send probe request ID; response-only requests remain unsalted controls.

Cold comparisons flush before each request. Separate warm passes flush once
before each mode's ordered sample stream. Mode order alternates by repetition
and, for cold comparisons, sample position. Numerical errors are observations,
not tolerance-based acceptance. Warm results also reference this run's matching
independent cold requests; warm-full is not a cold oracle. Worker-local raw
bodies/caches are not archived.
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
import tempfile
import time
from pathlib import Path
from urllib.parse import urlencode

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
    manifest = None
    if "source_fixture" in fixture:
        source = fixture["source_fixture"]
        count = fixture["sample_count"]
        if not isinstance(source, str) or not source:
            raise ValueError("Sample manifest source_fixture must be a nonempty path")
        if type(count) is not int or count <= 0:
            raise ValueError("Sample manifest sample_count must be a positive integer")
        source = (path.parent / source).resolve(strict=True)
        fixture = json.loads(source.read_text())
        if count > len(fixture["samples"]):
            raise ValueError("Sample manifest sample_count exceeds the original fixture")
        manifest = {"source_fixture": _file_identity(source), "sample_count": count,
                    "original_sample_count": len(fixture["samples"]), "selection": "Original fixture prefix, unchanged identities"}
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
    return {**fixture, "samples": fixture["samples"][:count], "sample_manifest": manifest} if manifest else fixture


def _config_input(path):
    # Resolve opt-in before runtime helpers transitively import SGLang.
    config = json.loads(path.read_text())
    selected_fp32 = config.get("selected_fp32_snapshots", False)
    if type(selected_fp32) is not bool:
        raise ValueError("selected_fp32_snapshots must be a JSON boolean")
    runtime_metadata = config.get("mamba_runtime_metadata", False)
    if type(runtime_metadata) is not bool:
        raise ValueError("mamba_runtime_metadata must be a JSON boolean")
    kv_store_stream_witness = config.get("kv_store_stream_witness", False)
    if type(kv_store_stream_witness) is not bool:
        raise ValueError("kv_store_stream_witness must be a JSON boolean")
    if kv_store_stream_witness and not (selected_fp32 and runtime_metadata):
        raise ValueError("kv_store_stream_witness requires selected_fp32_snapshots=true and mamba_runtime_metadata=true")
    coherence = config.get("kv_coherence_capture", False)
    if type(coherence) is not bool:
        raise ValueError("kv_coherence_capture must be a JSON boolean")
    if coherence and not (selected_fp32 and runtime_metadata and kv_store_stream_witness):
        raise ValueError("kv_coherence_capture requires selected_fp32_snapshots, mamba_runtime_metadata and kv_store_stream_witness=true")
    coherence_inputs = {}
    if coherence:
        for name in ("kv_coherence_build_receipt",):
            value = config.get(name)
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} must be a required nonempty string when kv_coherence_capture=true")
            coherence_inputs[name] = value
    if runtime_metadata and not selected_fp32:
        raise ValueError("mamba_runtime_metadata requires selected_fp32_snapshots=true")
    cache_salt_full_input = config.get("cache_salt_full_input", False)
    if type(cache_salt_full_input) is not bool:
        raise ValueError("cache_salt_full_input must be a JSON boolean")
    if coherence and cache_salt_full_input:
        raise ValueError("kv_coherence_capture requires the original unsalted scoring workload")
    config_paths = [path.resolve()]
    if "formal_config" in config:
        formal_path = (Path(__file__).resolve().parents[3] / config["formal_config"]).resolve(strict=True)
        config_paths.append(formal_path)
        config = json.loads(formal_path.read_text())
        # The probe input selects the experiment; formal engine parameters stay unchanged.
        config["selected_fp32_snapshots"] = selected_fp32
        if runtime_metadata:
            config["mamba_runtime_metadata"] = True
        config.pop("kv_store_stream_witness", None)
        if kv_store_stream_witness:
            config["kv_store_stream_witness"] = True
        # The wrapper owns opt-in; inherited formal true must not activate capture.
        for name in ("kv_coherence_capture", "kv_coherence_build_receipt"):
            config.pop(name, None)
        if coherence:
            config.update(kv_coherence_capture=True, **coherence_inputs)
        if cache_salt_full_input:
            config["cache_salt_full_input"] = True
    if coherence and config.get("cache_salt_full_input", False):
        raise ValueError("kv_coherence_capture requires the original unsalted scoring workload")
    return config, config_paths


def _load_config(path, pair, output):
    return _validate_config(*_config_input(path), pair, output)


def _validate_config(config, config_paths, pair, output):
    from tests.manual.agent_opd.run_qwen35_opd import _PERSONAL_ROOT, _READ_ONLY_MODELS

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
    for item in (*config_paths, Path(config["repo"]).resolve()):
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
                try:
                    response.raise_for_status()
                except aiohttp.ClientResponseError:
                    record["http_error_body"] = {
                        "response_text": raw.decode(errors="replace"), "encoding": "utf-8 with replacement",
                        "provenance": "aiohttp response.read(), before raise_for_status()"}
                    raise
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


async def _request(url, sample, mode, timeout, output, local, identity, cache_state, *, cache_salt_full_input=False):
    request_id = f"{identity['phase']}-r{identity['repetition']}-s{identity['sample_position']}-{mode}"
    payload = _payload(sample, mode)
    if cache_salt_full_input and mode == "full_input":
        payload["cache_salt"] = f"{identity['pair']}:{request_id}"
    record = {**identity, "request_id": request_id, "mode": mode, "source_uid": sample["source_uid"],
              "sample_index": sample["sample_index"], "input_count": len(sample["tokens"]),
              "prompt_count": len(sample["tokens"]) - sample["response_length"],
              "response_count": sample["response_length"], "logprob_start_len": payload["logprob_start_len"],
              "expected_input_token_logprobs_count": len(sample["tokens"]) - payload["logprob_start_len"],
              "first_requested_input_token_id": sample["tokens"][payload["logprob_start_len"]],
              "cache_state": cache_state, "cache_salt": payload.get("cache_salt"),
              "status": "failed", "started_at": time.time(),
              "token_ids_match": False, "finite_log_probs": False}
    record.update({key: None for key in ("http_time_to_headers_seconds", "http_elapsed_seconds", "body_read_seconds",
                                        "http_status", "body_bytes", "json_parse_seconds", "validation_seconds",
                                        "returned_completion_count", "input_token_logprobs_count",
                                        "first_input_token_logprob", "first_input_token_id", "native_request_id")})
    started = time.perf_counter()
    try:
        raw = await _http("POST", url + "/generate", payload, timeout, record)
        # Full response JSON stays worker-local, including invalid native responses.
        with (local / f"{request_id}.json").open("xb") as stream:
            stream.write(raw)
        body = _parse(raw, record)
        validating = time.perf_counter()
        try:
            meta = body.get("meta_info") if isinstance(body, dict) else None
            if isinstance(meta, dict):
                # This is the native req.rid used by ForwardBatch, not our filename identity.
                record["native_request_id"] = _meta_summary(meta.get("id"))
            vector = _scores(body, sample, record)
        finally:
            record["validation_seconds"] = time.perf_counter() - validating
        destination = output / "completion_scores" / f"{request_id}.json"
        _write(destination, {**identity, "request_id": request_id, "mode": mode,
                             "native_request_id": record["native_request_id"],
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


def _record_comparison(output, identity, results, sample, pair, cold_results=None):
    full, full_id = results["full_input"]
    response, response_id = results["response_only"]
    record = {**identity, "pair": pair, "source_uid": sample["source_uid"], "sample_index": sample["sample_index"],
              "full_request_id": full_id, "response_request_id": response_id,
              "full_vs_response_only": _comparison(full, response), "cold_reference": None, "historical_expected": None}
    if cold_results is not None:
        cold_full, cold_full_id = cold_results["full_input"]
        cold_response, cold_response_id = cold_results["response_only"]
        record["cold_reference"] = {
            "full_request_id": cold_full_id, "response_request_id": cold_response_id,
            "cold_full_vs_warm_full": _comparison(cold_full, full),
            "cold_full_vs_warm_response_only": _comparison(cold_full, response),
            "cold_response_only_vs_warm_full": _comparison(cold_response, full),
            "cold_response_only_vs_warm_response_only": _comparison(cold_response, response),
        }
    if pair == "A" and sample.get("expected_teacher_log_probs") is not None:
        expected = {"token_ids": sample["tokens"][-sample["response_length"]:],
                    "log_probs": sample["expected_teacher_log_probs"]}
        record["historical_expected"] = {
            "scope": "Caller-provided historical A teacher scores; not a B teacher reference",
            "full_input": _comparison(expected, full), "response_only": _comparison(expected, response),
        }
    _append(output / "comparisons.jsonl", record)


async def _benchmark(args, fixture, url, output, local, *, cache_salt_full_input=False):
    request_options = {"cache_salt_full_input": True} if cache_salt_full_input else {}
    server_request = {"endpoint": url + "/get_server_info"}
    info = _parse(await _http("GET", server_request["endpoint"], None, args.request_timeout, server_request), server_request)
    _write(output / "server_info.json", {"http": server_request, "get_server_info": info})
    cache_observations = {"cold_cache_verified": True, "warm_stream_initial_flush_verified": True}
    cold_results = {}
    for repetition in range(args.repeats):
        for position, sample in enumerate(fixture["samples"]):
            identity = {"pair": args.pair, "phase": "cold", "repetition": repetition, "sample_position": position}
            results = {}
            for mode in _mode_order(repetition, position):
                cache = await _flush(url, args.request_timeout, output / "cache.jsonl", {**identity, "mode": mode})
                cache_observations["cold_cache_verified"] &= cache == "flushed"
                results[mode] = await _request(url, sample, mode, args.request_timeout, output, local, identity,
                                               "cold_flushed" if cache == "flushed" else "cache_undefined", **request_options)
            _record_comparison(output, identity, results, sample, args.pair)
            cold_results[(args.pair, repetition, sample["source_uid"], sample["sample_index"])] = results
    for repetition in range(args.repeats):
        results = [{} for _ in fixture["samples"]]
        for mode in _mode_order(repetition):
            stream_id = {"phase": "warm_stream", "repetition": repetition, "mode": mode}
            cache = await _flush(url, args.request_timeout, output / "cache.jsonl", stream_id)
            cache_observations["warm_stream_initial_flush_verified"] &= cache == "flushed"
            for position, sample in enumerate(fixture["samples"]):
                identity = {"pair": args.pair, "phase": "warm_stream", "repetition": repetition, "sample_position": position}
                state = ("stream_first_after_flush" if position == 0 else "ordered_stream_after_flush") if cache == "flushed" else "cache_undefined"
                results[position][mode] = await _request(
                    url, sample, mode, args.request_timeout, output, local, identity, state, **request_options)
        for position, sample in enumerate(fixture["samples"]):
            identity = {"pair": args.pair, "phase": "warm_stream", "repetition": repetition, "sample_position": position}
            _record_comparison(output, identity, results[position], sample, args.pair,
                               cold_results[(args.pair, repetition, sample["source_uid"], sample["sample_index"])])
    return cache_observations


def _runtime_metadata_states(info):
    if not isinstance(info, dict):
        raise ValueError("Server-info response must be an object")
    for name in ("dp_size", "tp_size", "pp_size"):
        if type(info.get(name)) is not int or info[name] <= 0:
            raise ValueError(f"Server-info {name} must be a positive integer")
    states = info.get("internal_states")
    if not isinstance(states, list) or len(states) != info["dp_size"]:
        raise ValueError("Server-info internal_states must contain one response per DP, not per TP rank")
    ranks, observations = set(), []
    for index, state in enumerate(states):
        if not isinstance(state, dict) or "mamba_runtime_metadata" not in state:
            raise ValueError(f"DP response {index} is missing mamba_runtime_metadata")
        metadata = state["mamba_runtime_metadata"]
        if not isinstance(metadata, dict) or metadata.get("schema") != "mamba-runtime-metadata-v1":
            raise ValueError(f"DP response {index} has malformed mamba_runtime_metadata schema")
        if type(metadata.get("process_id")) is not int or metadata["process_id"] <= 0:
            raise ValueError(f"DP response {index} has malformed metadata process_id")
        rank = metadata.get("rank")
        if (not isinstance(rank, dict) or "dp_rank" not in rank
                or any(type(rank.get(name)) is not int or rank[name] < 0
                       for name in ("tp_rank", "pp_rank", "attn_dp_rank", "attn_tp_rank"))):
            raise ValueError(f"DP response {index} has malformed metadata rank")
        dp_rank = rank["dp_rank"]
        # Native DP1 without a controller retains dp_rank=None in the receipt.
        effective_dp_rank = 0 if dp_rank is None and info["dp_size"] == 1 else dp_rank
        if type(effective_dp_rank) is not int or effective_dp_rank < 0:
            raise ValueError(f"DP response {index} has malformed metadata rank")
        if effective_dp_rank >= info["dp_size"] or effective_dp_rank in ranks:
            raise ValueError(f"DP response {index} has duplicate or out-of-range dp_rank")
        ranks.add(effective_dp_rank)
        rows = metadata.get("rows")
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"DP response {index} has missing or empty runtime metadata rows")
        sequence = 0
        for row in rows:
            if (not isinstance(row, list) or len(row) != 3 or type(row[0]) is not int or row[0] <= sequence
                    or not isinstance(row[1], str) or not row[1] or not isinstance(row[2], list)
                    or any(not isinstance(field, list) or len(field) != 2 or not isinstance(field[0], str)
                           or not field[0] for field in row[2])):
                raise ValueError(f"DP response {index} has malformed runtime metadata row")
            sequence = row[0]
        observations.append({"state_index": index, "process_id": metadata["process_id"], "rank": rank,
                             "row_count": len(rows)})
    return observations


def _native_observer_errors(server_log):
    from tests.manual.agent_opd.sglang_rust_kv_observer import INVALIDATION_ERROR_MARKER as marker
    if server_log is None:
        raise ValueError("KV coherence requires the existing server log for independent native-error qualification")
    matches = []
    with server_log.open(errors="replace") as stream:
        for number, line in enumerate(stream, 1):
            if marker in line:
                matches.append({"line_number": number, "text": line.rstrip("\n")})
    return {"marker": marker, "server_log": str(server_log), "matches": matches,
            "status": "UNVERIFIED" if matches else "no_marker_observed",
            "qualification_limit": "Marker absence does not prove native alias/GIL/CUDA qualification"}


async def _collect_runtime_metadata(url, timeout, output, *, kv_coherence_capture=False, server_log=None):
    # The retained native /get_server_info alias delegates to /server_info.
    # Its internal_states list covers DP respondents, never all TP processes.
    endpoint = url + "/get_server_info"
    http = {"endpoint": endpoint}
    record = {"status": "failed", "http": http,
              "coverage": "One responding scheduler process per DP; no all-TP gather or independent TP-rank verification",
              "runtime_semantics": "UNVERIFIED; CPU host-enqueue receipts do not prove device completion or numerical parity"}
    raw = None
    try:
        if kv_coherence_capture:
            from tests.manual.agent_opd.sglang_kv_coherence import SCORING_REQUEST_COUNT

            rows = [json.loads(line) for line in (output / "requests.jsonl").read_text().splitlines()]
            rids = [row["native_request_id"] for row in rows]
            if (len(rows) != SCORING_REQUEST_COUNT or any(row["status"] != "scored" for row in rows)
                    or any(not isinstance(rid, str) or not rid for rid in rids) or len(set(rids)) != SCORING_REQUEST_COUNT):
                raise ValueError("KV coherence drain requires all16 distinct successfully scored native RIDs")
            record["native_observer_errors"] = _native_observer_errors(server_log)
            http["endpoint"] += "?" + urlencode({"kv_coherence_drain": "true"})
        raw = await _http("GET", http["endpoint"], None, timeout, http)
        info = _parse(raw, http)
        # Retain malformed readback as exact text if it cannot be strict JSON.
        json.dumps(info, allow_nan=False)
        record["server_info"] = info
        record["dp_responses"] = _runtime_metadata_states(info)
        if kv_coherence_capture:
            if record["native_observer_errors"]["matches"]:
                record["kv_coherence_status"] = "UNVERIFIED"
                raise ValueError(f"KV coherence UNVERIFIED: {record['native_observer_errors']['marker']} in native server output")
            record["kv_coherence"] = _coherence_states(info, output)
        record.update(status="collected", dp_size=info["dp_size"], tp_size=info["tp_size"], pp_size=info["pp_size"])
    except Exception as error:
        record.update(error_type=type(error).__name__, reason=str(error))
        if raw is not None:
            record["response_text"] = raw.decode(errors="replace")
    finally:
        _write(output / "runtime_metadata.json", record)
    return record


def _coherence_states(info, output):
    from tests.manual.agent_opd.sglang_kv_coherence import (
        BANK_COUNT, CANDIDATE_INPUT_COUNT, SCORING_REQUEST_COUNT, WINDOW_END, WINDOW_START, covered_once,
    )

    requests = [json.loads(line) for line in (output / "requests.jsonl").read_text().splitlines()]
    by_rid = {row["native_request_id"]: row for row in requests}
    candidates = [row for row in requests if row["mode"] == "full_input"
                  and row["input_count"] == CANDIDATE_INPUT_COUNT and row["logprob_start_len"] == 0]
    expected = {row["native_request_id"] for row in candidates}
    if (len(candidates) != BANK_COUNT or len(expected) != BANK_COUNT or {row["phase"] for row in candidates} != {"cold", "warm_stream"}
            or any(row["sample_index"] != 1695 or row["repetition"] != 0 or row["sample_position"] != 2
                   or row["meta_info"].get("num_retractions") != 0 for row in candidates)):
        raise ValueError("KV coherence response RID join does not contain the two original sample1695 full-input cases")
    summaries = []
    for state in info["internal_states"]:
        capture = state.get("kv_coherence")
        if not isinstance(capture, dict) or capture.get("schema") != "kv-coherence-v1":
            raise ValueError("Missing or malformed kv_coherence drain schema")
        if capture.get("status") != "captured":
            raise ValueError(f"KV coherence diagnostic unverified: {capture.get('reason', capture.get('errors'))}")
        if (not isinstance(capture.get("completed_rids"), list) or len(capture["completed_rids"]) != SCORING_REQUEST_COUNT
                or set(capture["completed_rids"]) != set(by_rid)):
            raise ValueError("KV coherence drain does not match all16 actual response RIDs")
        banks = capture.get("banks")
        if not isinstance(banks, list) or len(banks) != BANK_COUNT or {bank.get("rid") for bank in banks} != expected:
            raise ValueError("KV coherence opaque banks do not join the actual response RIDs")
        for bank in banks:
            case = by_rid[bank["rid"]]
            completion = json.loads(Path(case["completion_scores"]).read_text())
            if completion["native_request_id"] != case["native_request_id"] or case["meta_info"]["id"] != bank["rid"]:
                raise ValueError("KV coherence request/meta/completion RID identities differ")
            old_rows = bank.get("physical", {}).get("old_rows")
            if old_rows != (7955 if case["phase"] == "warm_stream" else 0):
                raise ValueError("KV coherence actual original OLD warm/cold coverage differs")
            physical = bank["physical"]
            if any(physical.get(name) is not True for name in ("writer_equals_FULL_insert_all_layers",
                       "original_OLD_equals_rebind", "rebind_suffix_equals_insert", "indices_in_bounds")):
                raise ValueError("KV coherence independent physical-index qualification missing or failed")
            insert, rebind = bank.get("insert"), bank.get("rebind")
            if (not isinstance(insert, dict) or not isinstance(rebind, dict)
                    or any(item.get("rid") != bank["rid"] or item.get("P") != WINDOW_START or item.get("E") != WINDOW_END
                           for item in (insert, rebind))
                    or rebind.get("Q") != WINDOW_START + old_rows or rebind.get("rotation_tail_declined") is not False):
                raise ValueError("KV coherence independent checkpoint RID/P/E/Q binding missing or changed")
            fragments = bank.get("fragments")
            if (not isinstance(fragments, list) or not covered_once([(f["lo"], f["hi"]) for f in fragments], WINDOW_START, rebind["Q"])
                    or any(f.get("rid") != bank["rid"] or f.get("P") != WINDOW_START or f.get("E") != WINDOW_END for f in fragments)):
                raise ValueError("KV coherence original pre-split OLD fragment coverage missing or changed")
            bank["logical_case"] = {key: case[key] for key in ("pair", "phase", "mode", "source_uid", "sample_index", "repetition")}
        capture["interpretation"] = "UNVERIFIED until independent all16/6804 baseline vectors and source/index gates pass"
        summaries.append(capture)
    return summaries


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
    config_input = _config_input(args.config.resolve(strict=True))
    private_temporary, package = None, None
    if config_input[0].get("kv_coherence_capture", False):
        from tests.manual.agent_opd import sglang_kv_coherence as coherence

        worker_root = Path(config_input[0]["worker_local_root"]).resolve()
        if not worker_root.is_absolute() or worker_root.is_relative_to("/mnt"):
            raise ValueError("Private SGLang package requires the configured worker-local temporary root")
        worker_root.mkdir(parents=True, exist_ok=True)
        private_temporary = tempfile.TemporaryDirectory(prefix="teacher-scoring-kv-", dir=worker_root)
        root = Path(importlib.util.find_spec("sglang").origin).parent
        package = coherence.prepare_package(root, worker_tmpdir=Path(private_temporary.name))
    from tests.manual.agent_opd import qwen35_pair_worker as paired
    from tests.manual.agent_opd.rjob_warmup import _worker_environment

    output = args.output_dir.resolve()
    config = _validate_config(*config_input, args.pair, output)
    fixture = _load_samples(args.samples, config["context_tokens"])
    if config.get("kv_coherence_capture", False) and (args.repeats != 1 or len(fixture["samples"]) != 4):
        raise ValueError("kv_coherence_capture requires the original first4/one-repetition 16-request workload")
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
                          "cold_reference": "Both independently flushed modes from this run, matched by pair/repetition/source_uid/sample_index; warm-full is descriptive, not a cold oracle",
                         "requests": "Sequential, same input IDs, native zero-generation payload; one aiohttp session per request",
                         "order_limit": "One repetition cannot balance both first-mode positions for each individual sample",
                         "timing": "perf_counter; headers include request serialization/server work; decoded body read, JSON parse and native tail validation measured separately",
                         "acceptance": "No performance PASS or numerical tolerance; primary judges observed differences"}}
    if "sample_manifest" in fixture:
        result["sample_manifest"] = fixture["sample_manifest"]
    if package is not None:
        result["kv_coherence_package"] = package
    try:
        _worker_environment(local)
        local_created = True
        (output / "completion_scores").mkdir()
        if config.get("selected_fp32_snapshots", False):
            from tests.manual.agent_opd import sglang_mamba_snapshots as snapshots

            root = Path(importlib.util.find_spec("sglang").origin).parent
            result["source_preflight"] = snapshots.prepare_source(
                root, image=config["image"], selected_fp32=True, archive_dir=output / "source_preflight")
        if config.get("mamba_runtime_metadata", False):
            from tests.manual.agent_opd import sglang_mamba_runtime_metadata as metadata

            result["runtime_metadata_source_preflight"] = metadata.prepare_runtime_metadata(
                root, image=config["image"], archive_dir=output / "runtime_metadata_source_preflight")
        if config.get("kv_store_stream_witness", False):
            from tests.manual.agent_opd import sglang_kv_streams as kv_streams

            result["kv_store_stream_source_preflight"] = kv_streams.prepare_source(
                root, image=config["image"], archive_dir=output / "kv_store_stream_source_preflight")
        if config.get("kv_coherence_capture", False):
            build = Path(config["kv_coherence_build_receipt"])
            if not build.is_absolute():
                build = Path(config["repo"]) / build
            result["kv_coherence_source_preflight"] = coherence.prepare_source(
                root, image=config["image"], archive_dir=output / "kv_coherence_source_preflight",
                build_receipt=build)
            if Path(importlib.util.find_spec("sglang").origin).parent.resolve() != root.resolve():
                raise ValueError("Prepared private SGLang package is not the selected runtime import root")
        result["runtime"] = _runtime(config, args.pair)
        result["native_scoring_sources"] = {name: _file_identity(Path(config["repo"]) / name) for name in (
            "miles/rollout/on_policy_distillation.py", "tests/manual/agent_opd/swe_replay.py",
            "tests/manual/agent_opd/qwen35_pair_worker.py", "tests/manual/agent_opd/probe_teacher_scoring.py")}
        if config.get("selected_fp32_snapshots", False):
            result["native_scoring_sources"]["tests/manual/agent_opd/sglang_mamba_snapshots.py"] = _file_identity(
                Path(snapshots.__file__))
        if config.get("mamba_runtime_metadata", False):
            result["native_scoring_sources"]["tests/manual/agent_opd/sglang_mamba_runtime_metadata.py"] = _file_identity(
                Path(metadata.__file__))
        if config.get("kv_store_stream_witness", False):
            result["native_scoring_sources"]["tests/manual/agent_opd/sglang_kv_streams.py"] = _file_identity(
                Path(kv_streams.__file__))
        if config.get("kv_coherence_capture", False):
            result["native_scoring_sources"]["tests/manual/agent_opd/sglang_kv_coherence.py"] = _file_identity(Path(coherence.__file__))
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
            request_options = {"cache_salt_full_input": True} if config.get("cache_salt_full_input", False) else {}
            result["cache_observations"] = asyncio.run(_benchmark(args, fixture, url, output, local, **request_options))
            paired._check_server(process)
            if config.get("mamba_runtime_metadata", False):
                result["native_measurements_completed"] = True
                options = {"kv_coherence_capture": True, "server_log": local / "server.log"} if config.get("kv_coherence_capture", False) else {}
                receipt = asyncio.run(_collect_runtime_metadata(url, args.request_timeout, output, **options))
                result["runtime_metadata"] = {"status": receipt["status"], "receipt": str(output / "runtime_metadata.json")}
                if config.get("kv_coherence_capture", False):
                    result["kv_coherence"] = {"status": receipt["status"],
                                              "interpretation": "PENDING independent baseline/source/physical validation",
                                              "summaries": receipt.get("kv_coherence", [])}
                if receipt["status"] != "collected":
                    raise RuntimeError(f"Scoring completed; independent runtime metadata readback failed: {receipt['reason']}")
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
                if private_temporary is not None:
                    private_temporary.cleanup()
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
