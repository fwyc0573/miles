"""CPU contracts for the dedicated teacher probe; mock HTTP is not performance evidence."""

import asyncio
import json
import math
import os
import signal
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import aiohttp
import pytest
from tests.manual.agent_opd import probe_teacher_scoring as probe


@pytest.fixture
def sample():
    return {"source_uid": "conversation-1:turn-2", "sample_index": 7, "tokens": [10, 11, 12, 13, 14],
            "response_length": 2, "expected_teacher_log_probs": [-0.5, -0.25]}


def _body(sample, mode):
    start = probe._payload(sample, mode)["logprob_start_len"]
    entries = [[-0.5 if token == 13 else -0.25, token, None] for token in sample["tokens"]]
    entries[0][0] = None
    return {"text": "", "output_ids": [], "meta_info": {
        "input_token_logprobs": entries[start:], "output_token_logprobs": [],
        "cached_tokens": start, "e2e_latency": 12.5, "nested": {"observed_duration": 3.5}}}


@pytest.mark.parametrize("prompt,response", [(1, 1), (1, 3), (3, 1), (3, 2)])
def test_real_native_payload_and_placeholder_tail_boundaries(sample, prompt, response):
    from miles.rollout import on_policy_distillation as native

    sample.update(tokens=list(range(prompt + response)), response_length=response)
    full, short = (probe._payload(sample, mode) for mode in probe._MODES)
    assert full == native._score_payload(sample["tokens"])
    assert full["sampling_params"]["max_new_tokens"] == 0 and full["return_logprob"] is True
    assert full["logprob_start_len"] == 0
    assert {**short, "logprob_start_len": 0} == full
    assert short["logprob_start_len"] == prompt - 1
    for mode in probe._MODES:
        record = {}
        body = _body(sample, mode)
        actual = probe._scores(body, sample, record)
        assert actual["token_ids"] == sample["tokens"][-response:]
        assert actual["log_probs"] == [item[0] for item in native._trim_input_field(body["meta_info"], "input_token_logprobs", response)]
        assert record["token_ids_match"] and record["finite_log_probs"]
        assert record["meta_info"]["e2e_latency"] == 12.5
        assert record["meta_info"]["input_token_logprobs"] == {"omitted_array_length": len(body["meta_info"]["input_token_logprobs"])}


@pytest.mark.parametrize("failure", ["ids", "missing", "short", "nonfinite", "null", "generation"])
def test_native_invalid_responses_do_not_set_false_parity_flags(sample, failure):
    body = _body(sample, "response_only")
    if failure == "ids":
        body["meta_info"]["input_token_logprobs"][-1][1] = 999
    elif failure == "missing":
        del body["meta_info"]["input_token_logprobs"]
    elif failure == "short":
        body["meta_info"]["input_token_logprobs"] = body["meta_info"]["input_token_logprobs"][-2:]
    elif failure == "nonfinite":
        body["meta_info"]["input_token_logprobs"][-1][0] = float("nan")
    elif failure == "null":
        body["meta_info"]["input_token_logprobs"][-1][0] = None
    else:
        body["output_ids"] = [99]
    record = {}
    with pytest.raises((ValueError, TypeError)):
        probe._scores(body, sample, record)
    if failure == "ids":
        assert record["token_ids_match"] is False
        assert record["completion_token_id_mismatches"] == [{"position": 1, "expected": 14, "actual": 999}]
    elif failure in ("nonfinite", "null", "missing"):
        assert record["finite_log_probs"] is False
    if failure == "short":
        assert record["token_ids_match"] is False and record["returned_completion_count"] == 1


def test_comparison_reports_exact_errors_without_tolerance_or_acceptance():
    reference = {"token_ids": [1, 2], "log_probs": [0, -2]}
    candidate = {"token_ids": [1, 2], "log_probs": [0.25, -2.5]}
    result = probe._comparison(reference, candidate)
    assert result["values_exact"] is False and result["accepted"] is None
    assert result["max_absolute_error"] == 0.5 and result["max_relative_error"] == 0.25
    assert result["relative_error_undefined_count"] == 1
    assert probe._comparison(reference, reference)["values_exact"] is True
    assert probe._comparison({"token_ids": [1], "log_probs": [0]}, {"token_ids": [1], "log_probs": [0]})["max_relative_error"] is None
    for invalid in ({"token_ids": [1], "log_probs": [0]}, {"token_ids": [1, 2], "log_probs": [0, math.inf]}):
        assert probe._comparison(reference, invalid)["max_absolute_error"] is None


def test_fixture_keeps_order_and_rejects_duplicate_or_bad_input(sample, tmp_path):
    path = tmp_path / "samples.json"
    fixture = {"job": "historical-A-job", "samples": [sample, {**sample, "sample_index": 8}]}
    path.write_text(json.dumps(fixture))
    assert probe._load_samples(path, 10) == fixture
    fixture["samples"][1]["sample_index"] = sample["sample_index"]
    path.write_text(json.dumps(fixture))
    with pytest.raises(ValueError, match="Duplicate"):
        probe._load_samples(path, 10)
    for update in ({"response_length": 0}, {"response_length": 5}, {"tokens": [True, 2, 3]},
                   {"expected_teacher_log_probs": [0]}, {"expected_teacher_log_probs": [0, math.inf]}):
        path.write_text(json.dumps({"job": "historical-A-job", "samples": [{**sample, **update}]}))
        with pytest.raises(ValueError):
            probe._load_samples(path, 10)


class _Response:
    def __init__(self, raw, status, clock):
        self.raw, self.status, self.clock = raw, status, clock
        self.headers = {"Content-Length": str(len(raw))}

    async def __aenter__(self):
        self.clock.now += 2
        return self

    async def __aexit__(self, *args):
        return False

    async def read(self):
        self.clock.now += 3
        return self.raw

    def raise_for_status(self):
        if self.status >= 400:
            raise aiohttp.ClientResponseError(SimpleNamespace(real_url="mock://teacher"), (), status=self.status)


def _mock_http(monkeypatch, callback):
    clock, calls, timeouts = SimpleNamespace(now=0), [], []

    class Session:
        def __init__(self, *, timeout):
            timeouts.append(timeout.total)

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        def request(self, method, url, **kwargs):
            calls.append((method, url, kwargs))
            raw, status = callback(method, url, kwargs)
            return _Response(raw, status, clock)

    monkeypatch.setattr(aiohttp, "ClientSession", Session)
    monkeypatch.setattr(probe.time, "perf_counter", lambda: clock.now)
    return clock, calls, timeouts


def _output(tmp_path):
    output, local = tmp_path / "retained", tmp_path / "worker-local"
    output.mkdir()
    local.mkdir()
    (output / "completion_scores").mkdir()
    return output, local


def test_instrumented_mock_http_separates_headers_read_parse_validation(sample, tmp_path, monkeypatch):
    raw = json.dumps(_body(sample, "full_input")).encode()
    clock, calls, timeouts = _mock_http(monkeypatch, lambda *args: (raw, 200))
    original_parse, original_scores = probe.json.loads, probe._scores

    def loads(raw):
        clock.now += 7
        return original_parse(raw)

    def scores(*args):
        clock.now += 11
        return original_scores(*args)

    monkeypatch.setattr(probe.json, "loads", loads)
    monkeypatch.setattr(probe, "_scores", scores)
    output, local = _output(tmp_path)
    vector, request_id = asyncio.run(probe._request("mock://teacher", sample, "full_input", 19, output, local,
                                                  {"phase": "cold", "repetition": 0, "sample_position": 0}, "cold_flushed"))
    record = original_parse((output / "requests.jsonl").read_text())
    assert record["request_id"] == request_id == "cold-r0-s0-full_input"
    assert vector["token_ids"] == [13, 14] and record["status"] == "scored"
    assert record["http_time_to_headers_seconds"] == 2 and record["body_read_seconds"] == 3
    assert record["http_elapsed_seconds"] == 5 and record["json_parse_seconds"] == 7
    assert record["validation_seconds"] == 11 and record["body_bytes"] == len(raw)
    assert record["response_count"] == 2 and record["logprob_start_len"] == 0
    assert record["cache_state"] == "cold_flushed" and timeouts == [19]
    assert (local / f"{request_id}.json").read_bytes() == raw
    assert calls[0][2]["json"] == probe._payload(sample, "full_input")


@pytest.mark.parametrize("status", [400, 500])
def test_flush_real_http_failures_propagate_and_record_diagnostics(tmp_path, monkeypatch, status):
    _mock_http(monkeypatch, lambda *args: (b"native cache failure", status))
    path = tmp_path / "cache.jsonl"
    with pytest.raises(aiohttp.ClientResponseError) as error:
        asyncio.run(probe._flush("mock://teacher", 17, path, {"mode": "full_input"}))
    assert error.value.status == status
    record = json.loads(path.read_text())
    assert record["status"] == "failed" and record["http_status"] == status


@pytest.mark.parametrize("status", [404, 405, 501])
def test_flush_unsupported_is_explicitly_cache_undefined(tmp_path, monkeypatch, status):
    _mock_http(monkeypatch, lambda *args: (b"unsupported", status))
    path = tmp_path / "cache.jsonl"
    assert asyncio.run(probe._flush("mock://teacher", 17, path, {})) == "cache_undefined"
    assert json.loads(path.read_text())["http_status"] == status


@pytest.mark.parametrize("failure", ["timeout", "http", "json", "ids"])
def test_request_failures_remain_failures_and_are_not_parity_passes(sample, tmp_path, monkeypatch, failure):
    body = _body(sample, "full_input")
    if failure == "ids":
        body["meta_info"]["input_token_logprobs"][-1][1] = 999
    raw = b"{invalid JSON" if failure == "json" else json.dumps(body).encode()
    _mock_http(monkeypatch, lambda *args: (raw, 503 if failure == "http" else 200))
    if failure == "timeout":
        async def fail(*args):
            raise asyncio.TimeoutError("bounded HTTP timeout")
        monkeypatch.setattr(probe, "_http", fail)
    output, local = _output(tmp_path)
    with pytest.raises((asyncio.TimeoutError, aiohttp.ClientResponseError, ValueError)):
        asyncio.run(probe._request("mock://teacher", sample, "full_input", 17, output, local,
                                  {"phase": "cold", "repetition": 0, "sample_position": 0}, "cold_flushed"))
    record = json.loads((output / "requests.jsonl").read_text())
    assert record["status"] == "failed" and record["token_ids_match"] is False
    assert not list((output / "completion_scores").iterdir())
    if failure == "json":
        assert "json_parse_seconds" in record
    if failure == "ids":
        assert "validation_seconds" in record and (local / "cold-r0-s0-full_input.json").exists()


@pytest.mark.parametrize("cache_status", [200, 404])
def test_fixed_case_identities_cold_order_balance_warm_prefix_stream_and_historical_scope(sample, tmp_path, monkeypatch, cache_status):
    samples = [sample, {**sample, "source_uid": "conversation-1:turn-3", "sample_index": 8}]
    fixture = {"job": "historical-A-job", "samples": samples}

    def response(method, url, kwargs):
        if url.endswith("/get_server_info"):
            return b'{"version":"mock-not-native"}', 200
        if url.endswith("/flush_cache"):
            return b"Cache flushed" if cache_status == 200 else b"unsupported", cache_status
        payload = kwargs["json"]
        mode = "full_input" if payload["logprob_start_len"] == 0 else "response_only"
        return json.dumps(_body(sample, mode)).encode(), 200

    _, calls, timeouts = _mock_http(monkeypatch, response)
    output, local = _output(tmp_path)
    args = SimpleNamespace(repeats=2, request_timeout=17, pair="A")
    cache = asyncio.run(probe._benchmark(args, fixture, "mock://teacher", output, local))
    assert cache == {"cold_cache_verified": cache_status == 200, "warm_stream_initial_flush_verified": cache_status == 200}
    rows = [json.loads(line) for line in (output / "requests.jsonl").read_text().splitlines()]
    assert len(rows) == len({row["request_id"] for row in rows}) == 16
    assert [(row["repetition"], row["sample_position"], row["mode"]) for row in rows[:8]] == [
        (0, 0, "full_input"), (0, 0, "response_only"), (0, 1, "response_only"), (0, 1, "full_input"),
        (1, 0, "response_only"), (1, 0, "full_input"), (1, 1, "full_input"), (1, 1, "response_only")]
    assert [(row["sample_index"], row["mode"]) for row in rows[8:12]] == [
        (7, "full_input"), (8, "full_input"), (7, "response_only"), (8, "response_only")]
    if cache_status == 404:
        assert all(row["cache_state"] == "cache_undefined" for row in rows)
    else:
        assert rows[8]["cache_state"] == "stream_first_after_flush"
        assert rows[9]["cache_state"] == "ordered_stream_after_flush"
    assert len([call for call in calls if call[1].endswith("/flush_cache")]) == 12
    assert all(timeout == 17 for timeout in timeouts)
    comparisons = [json.loads(line) for line in (output / "comparisons.jsonl").read_text().splitlines()]
    assert len(comparisons) == 8 and all(row["full_vs_response_only"]["values_exact"] for row in comparisons)
    assert all(row["full_vs_response_only"]["accepted"] is None for row in comparisons)
    assert all(row["historical_expected"] is not None for row in comparisons)
    second = tmp_path / "b"
    second.mkdir()
    probe._record_comparison(second, {}, {mode: ({"token_ids": [13, 14], "log_probs": [-0.5, -0.25]}, mode) for mode in probe._MODES}, sample, "B")
    assert json.loads((second / "comparisons.jsonl").read_text())["historical_expected"] is None


def test_cli_requires_explicit_positive_budget_and_help_has_no_worker_imports():
    required = ["--config", "config.json", "--pair", "A", "--samples", "samples.json", "--output-dir", "new"]
    for extra in ([], ["--repeats", "1"], ["--repeats", "0", "--request-timeout", "1"],
                  ["--repeats", "1", "--request-timeout", "0"], ["--repeats", "1", "--request-timeout", "nan"]):
        with pytest.raises(SystemExit):
            probe._parser().parse_args(required + extra)
    args = probe._parser().parse_args(required + ["--repeats", "2", "--request-timeout", "17.5"])
    assert args.repeats == 2 and args.request_timeout == 17.5
    result = subprocess.run([sys.executable, "-B", "-m", "tests.manual.agent_opd.probe_teacher_scoring", "--help"],
                            capture_output=True, text=True, timeout=20)
    assert result.returncode == 0 and "--request-timeout" in result.stdout and "Traceback" not in result.stderr


@pytest.fixture
def worker_config(tmp_path, monkeypatch):
    from tests.manual.agent_opd import run_qwen35_opd as native

    personal = tmp_path / "personal"
    model = tmp_path / "approved-read-only" / "model"
    model.mkdir(parents=True)
    monkeypatch.setattr(native, "_PERSONAL_ROOT", personal)
    monkeypatch.setattr(native, "_READ_ONLY_MODELS", {model})
    config = {"gpu_tag": "H800", "charged_group": "codesign", "image": "parent-pinned-image-digest",
              "worker_python": sys.executable, "repo": str(Path.cwd()), "local_mount": str(tmp_path),
              "worker_local_root": str(tmp_path / "scratch"), "context_tokens": 10,
              "teacher_port": 30000, "teacher_dist_port": 29501,
              "pairs": {"A": {"startup_timeout": 17, "teacher": {
                  "path": str(model), "nodes": 1, "gpus_per_node": 4, "tp_size": 4,
                  "mem_fraction_static": 0.85, "max_running_requests": 1, "chunked_prefill_size": 8192}}}}
    # Both fixture files and the real repository are read from their common local ancestor.
    config["local_mount"] = str(Path(os.path.commonpath([str(tmp_path), str(Path.cwd())])))
    path = tmp_path / "config.json"
    path.write_text(json.dumps(config))
    return path, config, model


@pytest.mark.parametrize("field,value", [("gpu_tag", "H200"), ("charged_group", "step_main"), ("worker_python", "/other/python")])
def test_config_enforces_worker_hardware_and_reuses_model_whitelist(worker_config, tmp_path, field, value):
    path, config, model = worker_config
    output = tmp_path / "retained-new"
    assert probe._load_config(path, "A", output)["pairs"]["A"]["teacher"]["path"] == str(model)
    config[field] = value
    path.write_text(json.dumps(config))
    with pytest.raises(ValueError):
        probe._load_config(path, "A", output)


def test_preload_hashes_are_actual_required_files_and_not_native_gpu_evidence(worker_config, monkeypatch):
    path, config, model = worker_config
    config = probe._load_config(path, "A", path.parent / "output")
    for name in ("config.json", "model.safetensors.index.json"):
        (model / name).write_text('{}')
    monkeypatch.setattr(probe.subprocess, "check_output", lambda *args, **kwargs: "NVIDIA H800, 80000 MiB, mock-driver\n" * 4)
    runtime = probe._runtime(config, "A")
    assert set(probe._SGLANG_SOURCES).issubset(runtime["sglang_sources"])
    assert all(len(item["sha256"]) == 64 and item["bytes"] >= 0 for item in runtime["sglang_sources"].values())
    assert all(runtime["sglang_sources"][name]["bytes"] > 0 for name in probe._SGLANG_SOURCES)
    assert runtime["configured_image"] == config["image"] and "parent allocation input" in runtime["image_identity_limit"]
    monkeypatch.setattr(probe, "_SGLANG_SOURCES", ("missing-native-source.py",))
    with pytest.raises(FileNotFoundError):
        probe._runtime(config, "A")


@pytest.mark.parametrize("failure", ["startup", "benchmark", "archive"])
def test_worker_failure_stops_only_its_real_cpu_child_and_archives_local_log(worker_config, sample, tmp_path, monkeypatch, failure):
    from tests.manual.agent_opd import qwen35_pair_worker as paired

    path, config, model = worker_config
    monkeypatch.setattr(os, "environ", dict(os.environ))
    samples = tmp_path / "fixture.json"
    samples.write_text(json.dumps({"job": "historical-A-job", "samples": [sample]}))
    output = tmp_path / "retained"
    args = SimpleNamespace(config=path, pair="A", samples=samples, output_dir=output, repeats=1, request_timeout=17)
    monkeypatch.setenv("KUBEBRAIN_RJOB_NAME", "test-job")
    monkeypatch.setenv("KUBEBRAIN_REPLICA", "0")
    monkeypatch.setenv("KUBEBRAIN_REPLICA_TOTAL", "1")
    monkeypatch.setenv("NCCL_FROM_PLATFORM", "preserved")
    monkeypatch.setattr(probe, "_runtime", lambda *args: {"scope": "mock CPU, no GPU inspection"})
    monkeypatch.setattr(paired, "_teacher_command", lambda *args: [sys.executable, "-u", "-B", "-c",
                                                                 "print('owned CPU child'); import time; time.sleep(60)"])
    children = []
    original_popen = subprocess.Popen

    def launch(*args, **kwargs):
        assert (output / "preload.json").exists()
        assert os.environ["NCCL_FROM_PLATFORM"] == "preserved" and kwargs["start_new_session"] is True
        children.append(original_popen(*args, **kwargs))
        return children[-1]

    monkeypatch.setattr(probe.subprocess, "Popen", launch)

    def ready(*args):
        if failure == "startup":
            raise TimeoutError("native readiness deadline")
        return {"model_path": str(model)}

    async def benchmark(*args):
        if failure == "benchmark":
            raise ValueError("native score IDs differ")

    monkeypatch.setattr(paired, "_wait_teacher_ready", ready)
    monkeypatch.setattr(probe, "_benchmark", benchmark)
    if failure == "archive":
        def fail_archive(*args):
            raise OSError("archive storage failed")
        monkeypatch.setattr(probe.shutil, "copyfileobj", fail_archive)
    with pytest.raises((TimeoutError, ValueError, OSError)):
        probe._run(args)
    assert len(children) == 1 and children[0].poll() == -signal.SIGTERM
    record = json.loads((output / "result.json").read_text())
    assert record["status"] == "failed" and record["performance_accepted"] is False
    assert record["cleanup_completed"] is True and record["server_shutdown_returncode"] == -signal.SIGTERM
    if failure == "archive":
        assert record["archive_error_type"] == "OSError"
    else:
        assert (output / "server.log").exists()
    with pytest.raises(FileExistsError):
        probe._run(args)
    assert len(children) == 1 and json.loads((output / "result.json").read_text()) == record
