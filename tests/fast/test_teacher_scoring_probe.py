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
    entries[start][0] = None
    return {"text": "", "output_ids": [], "meta_info": {
        "input_token_logprobs": entries[start:], "output_token_logprobs": [],
        "cached_tokens": start, "e2e_latency": 12.5, "nested": {"observed_duration": 3.5}}}


@pytest.mark.parametrize("prompt,response", [(1, 1), (1, 3), (3, 1), (3, 2)])
def test_real_native_payload_and_placeholder_tail_boundaries(sample, prompt, response, monkeypatch):
    from miles.rollout import on_policy_distillation as native

    owner, calls = native._score_payload, []

    def score_payload(tokens, **kwargs):
        calls.append((tokens, kwargs))
        return owner(tokens, **kwargs)

    monkeypatch.setattr(native, "_score_payload", score_payload)
    sample.update(tokens=list(range(prompt + response)), response_length=response)
    full, short = (probe._payload(sample, mode) for mode in probe._MODES)
    assert calls == [(sample["tokens"], {}), (sample["tokens"], {"response_length": response})]
    assert full == owner(sample["tokens"])
    assert short == owner(sample["tokens"], response_length=response)
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
        start = probe._payload(sample, mode)["logprob_start_len"]
        assert record["input_token_logprobs_count"] == prompt + response - start
        assert record["first_input_token_logprob"] is None
        assert record["first_input_token_id"] == sample["tokens"][start]


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


@pytest.mark.parametrize("mode", probe._MODES)
def test_instrumented_mock_http_separates_headers_read_parse_validation(sample, tmp_path, monkeypatch, mode):
    raw = json.dumps(_body(sample, mode)).encode()
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
    vector, request_id = asyncio.run(probe._request("mock://teacher", sample, mode, 19, output, local,
                                                  {"phase": "cold", "repetition": 0, "sample_position": 0}, "cold_flushed"))
    record = original_parse((output / "requests.jsonl").read_text())
    assert record["request_id"] == request_id == f"cold-r0-s0-{mode}"
    assert vector["token_ids"] == [13, 14] and record["status"] == "scored"
    assert record["http_time_to_headers_seconds"] == 2 and record["body_read_seconds"] == 3
    assert record["http_elapsed_seconds"] == 5 and record["json_parse_seconds"] == 7
    assert record["validation_seconds"] == 11 and record["body_bytes"] == len(raw)
    start = probe._payload(sample, mode)["logprob_start_len"]
    assert record["response_count"] == 2 and record["logprob_start_len"] == start
    assert record["input_token_logprobs_count"] == record["expected_input_token_logprobs_count"] == len(sample["tokens"]) - start
    assert record["first_input_token_id"] == record["first_requested_input_token_id"] == sample["tokens"][start]
    assert record["first_input_token_logprob"] is None
    assert record["cache_state"] == "cold_flushed" and timeouts == [19]
    assert (local / f"{request_id}.json").read_bytes() == raw
    assert calls[0][2]["json"] == probe._payload(sample, mode)


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
        body["meta_info"]["input_token_logprobs"][0][:2] = [float("nan"), float("inf")]
        body["meta_info"]["input_token_logprobs"][-1][1] = float("nan")
    raw = b"{invalid JSON" if failure == "json" else json.dumps(body).encode()
    _mock_http(monkeypatch, lambda *args: (raw, 503 if failure == "http" else 200))
    if failure == "timeout":
        async def fail(*args):
            raise asyncio.TimeoutError("bounded HTTP timeout")
        monkeypatch.setattr(probe, "_http", fail)
    output, local = _output(tmp_path)
    with pytest.raises((asyncio.TimeoutError, aiohttp.ClientResponseError, ValueError)) as error:
        asyncio.run(probe._request("mock://teacher", sample, "full_input", 17, output, local,
                                  {"phase": "cold", "repetition": 0, "sample_position": 0}, "cold_flushed"))
    record = json.loads((output / "requests.jsonl").read_text())
    assert record["status"] == "failed" and record["token_ids_match"] is False
    assert not list((output / "completion_scores").iterdir())
    if failure == "json":
        assert "json_parse_seconds" in record
    if failure == "ids":
        assert "validation_seconds" in record and (local / "cold-r0-s0-full_input.json").exists()
        assert str(error.value) == "Teacher completion IDs differ from fixed tokens or scores are nonfinite"
        assert record["first_input_token_logprob"] == {"nonfinite": "nan"}
        assert record["first_input_token_id"] == {"nonfinite": "inf"}
        assert record["completion_token_id_mismatches"][-1]["actual"] == {"nonfinite": "nan"}
        assert record["input_token_logprobs_count"] == len(sample["tokens"])


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


@pytest.mark.parametrize("pair", ["A", "B"])
def test_warm_scores_use_same_run_cold_references_not_contaminated_warm_full(sample, tmp_path, monkeypatch, pair):
    samples = [{**sample, "source_uid": f"conversation-{position // 2}", "sample_index": position % 2,
                "tokens": [10, 11, 12, 100 + position, 200 + position]} for position in range(7)]
    fixture = {"job": "historical-A-job", "samples": samples}
    references = {
        (repetition, item["source_uid"], item["sample_index"], mode): [
            -1.0 - position - (0.125 if position == 2 and mode == "response_only" else 0), -0.25 - repetition]
        for repetition in range(2) for position, item in enumerate(samples) for mode in probe._MODES
    }
    current = {}
    original_request = probe._request

    async def request(url, item, mode, timeout, output, local, identity, cache_state):
        current.update(sample=item, mode=mode, identity=identity)
        return await original_request(url, item, mode, timeout, output, local, identity, cache_state)

    def response(method, url, kwargs):
        if url.endswith("/get_server_info"):
            return b'{"version":"mock-not-native"}', 200
        if url.endswith("/flush_cache"):
            return b"Cache flushed", 200
        item, mode, identity = current["sample"], current["mode"], current["identity"]
        values = references[(identity["repetition"], item["source_uid"], item["sample_index"], mode)]
        body = _body(item, mode)
        # Case 0: warm response agrees with both cold modes, but not warm full.
        # Case 1: both warm modes drift together, so warm parity is misleading.
        drift = identity["phase"] == "warm_stream" and (
            (identity["sample_position"] == 0 and mode == "full_input") or identity["sample_position"] == 1)
        for entry, value in zip(body["meta_info"]["input_token_logprobs"][-2:], values):
            entry[0] = value - (0.5 if drift else 0)
        return json.dumps(body).encode(), 200

    monkeypatch.setattr(probe, "_request", request)
    _, calls, _ = _mock_http(monkeypatch, response)
    output, local = _output(tmp_path)
    args = SimpleNamespace(repeats=2, request_timeout=17, pair=pair)
    asyncio.run(probe._benchmark(args, fixture, "mock://teacher", output, local))
    rows = [json.loads(line) for line in (output / "requests.jsonl").read_text().splitlines()]
    assert len(rows) == len({row["request_id"] for row in rows}) == 56
    assert sum(url.endswith("/generate") for _, url, _ in calls) == 56
    assert sum(url.endswith("/flush_cache") for _, url, _ in calls) == 32
    by_id = {row["request_id"]: row for row in rows}
    comparisons = [json.loads(line) for line in (output / "comparisons.jsonl").read_text().splitlines()]
    assert len(comparisons) == 28
    for row in comparisons:
        assert row["pair"] == pair
        assert (row["historical_expected"] is None) == (pair == "B")
        if row["phase"] == "cold":
            assert row["full_vs_response_only"]["values_exact"] == (row["sample_position"] != 2)
            if row["sample_position"] == 2:
                assert row["full_vs_response_only"]["max_absolute_error"] == 0.125
            assert row["cold_reference"] is None
            continue
        cold = row["cold_reference"]
        for mode, key in (("full_input", "full_request_id"), ("response_only", "response_request_id")):
            reference = by_id[cold[key]]
            assert reference["phase"] == "cold" and reference["mode"] == mode
            assert all(reference[key] == row[key] for key in ("repetition", "source_uid", "sample_index"))
            vector = json.loads(Path(reference["completion_scores"]).read_text())
            assert vector["log_probs"] == references[(row["repetition"], row["source_uid"], row["sample_index"], mode)]
        errors = [cold[key] for key in (
            "cold_full_vs_warm_full", "cold_full_vs_warm_response_only",
            "cold_response_only_vs_warm_full", "cold_response_only_vs_warm_response_only")]
        assert all(error["accepted"] is None and error["finite_log_probs"] and error["token_ids_match"]
                   for error in errors)
        if row["sample_position"] == 0:
            assert row["full_vs_response_only"]["values_exact"] is False
            assert cold["cold_full_vs_warm_full"]["max_absolute_error"] == 0.5
            assert cold["cold_response_only_vs_warm_full"]["values_exact"] is False
            assert cold["cold_full_vs_warm_response_only"]["values_exact"] is True
            assert cold["cold_response_only_vs_warm_response_only"]["values_exact"] is True
        elif row["sample_position"] == 1:
            assert row["full_vs_response_only"]["values_exact"] is True
            assert all(error["values_exact"] is False and error["max_absolute_error"] == 0.5 for error in errors)
        elif row["sample_position"] == 2:
            assert row["full_vs_response_only"]["values_exact"] is False
            assert cold["cold_full_vs_warm_full"]["values_exact"] is True
            assert cold["cold_response_only_vs_warm_response_only"]["values_exact"] is True
            assert cold["cold_full_vs_warm_response_only"]["max_absolute_error"] == 0.125
            assert cold["cold_response_only_vs_warm_full"]["max_absolute_error"] == 0.125
        else:
            assert all(error["values_exact"] is True for error in errors)


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


@pytest.fixture
def snapshot_source(tmp_path, monkeypatch):
    from tests.manual.agent_opd import sglang_mamba_snapshots as snapshots

    retained = Path(os.environ.get("MILES_PINNED_SGLANG_SOURCE", Path(__file__).resolve().parents[2]
                    / "task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111"
                    / "exp-1111-042450-358109/source"))
    if not retained.is_dir():
        pytest.skip("Actual retained native SGLang C3 source is not available")
    root = tmp_path / "native-sglang"
    manifest = snapshots.source_manifest()
    for relative in manifest["files"]:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((retained / relative).read_bytes())
    monkeypatch.setattr(snapshots.importlib.metadata, "version", lambda name: manifest["distribution_version"])
    return root, snapshots


@pytest.mark.parametrize("selected", [0, 1, "true", None, {}, []])
@pytest.mark.parametrize("probe_input", [False, True])
def test_snapshot_selection_rejects_non_boolean_json_before_worker_start(worker_config, tmp_path, selected, probe_input):
    path, config, _ = worker_config
    value = {"formal_config": str(path)} if probe_input else config
    value["selected_fp32_snapshots"] = selected
    input_path = tmp_path / "invalid-selection.json"
    input_path.write_text(json.dumps(value))
    with pytest.raises(ValueError, match="selected_fp32_snapshots must be a JSON boolean"):
        probe._load_config(input_path, "A", tmp_path / "new-output")
    assert json.loads(path.read_text()).get("selected_fp32_snapshots") is None


@pytest.mark.parametrize("selected", [None, False, True])
def test_selected_source_preparation_precedes_runtime_and_teacher_and_retains_real_receipt(
        worker_config, sample, tmp_path, monkeypatch, snapshot_source, selected):
    from tests.manual.agent_opd import qwen35_pair_worker as paired, rjob_warmup as warmup

    path, config, model = worker_config
    root, snapshots = snapshot_source
    config["image"] = snapshots.source_manifest()["image"]
    path.write_text(json.dumps(config))
    wrapper = {"formal_config": str(path)}
    if selected is not None:
        wrapper["selected_fp32_snapshots"] = selected
    wrapper_path = tmp_path / "probe.json"
    wrapper_path.write_text(json.dumps(wrapper))
    samples = tmp_path / "samples.json"
    samples.write_text(json.dumps({"job": "historical-A-job", "samples": [sample]}))
    output = tmp_path / "retained-new"
    args = probe._parser().parse_args(["--config", str(wrapper_path if selected is not None else path),
                                      "--pair", "A", "--samples", str(samples), "--output-dir", str(output),
                                      "--repeats", "2", "--request-timeout", "17"])
    monkeypatch.setattr(os, "environ", dict(os.environ))
    for key, value in {"KUBEBRAIN_RJOB_NAME": "cpu-test-job", "KUBEBRAIN_REPLICA": "0",
                       "KUBEBRAIN_REPLICA_TOTAL": "1", "NCCL_FROM_PLATFORM": "preserved",
                       "CUDA_VISIBLE_DEVICES": "0,1,2,3", "SGLANG_FORCE_COARSE_WAR_BARRIER": "0"}.items():
        monkeypatch.setenv(key, value)
    events, receipts = [], []
    original_prepare = snapshots.prepare_source
    before = {relative: (root / relative).read_bytes() for relative in snapshots.source_manifest()["files"]}
    # Other CPU tests may already import host attention; this worker path must not add imports before preparation.
    attention_before = {name for name in sys.modules if name.startswith("sglang.srt.layers.attention")}

    def prepare(root_arg, **kwargs):
        assert root_arg == root and kwargs == {"image": config["image"], "selected_fp32": True,
                                               "archive_dir": output / "source_preflight"}
        assert {name for name in sys.modules if name.startswith("sglang.srt.layers.attention")} == attention_before
        receipts.append(original_prepare(root_arg, **kwargs))
        events.append("prepared")
        return receipts[-1]

    monkeypatch.setattr(snapshots, "prepare_source", prepare)

    def find_spec(name):
        assert name == "sglang" and selected is True
        return SimpleNamespace(origin=str(root / "__init__.py"))

    monkeypatch.setattr(probe.importlib.util, "find_spec", find_spec)

    def environment(local):
        local.mkdir(parents=True)
        monkeypatch.setenv("MILES_NODE_EXTERNAL_IP", "192.0.2.10")

    monkeypatch.setattr(warmup, "_worker_environment", environment)

    def runtime(*args):
        assert events == (["prepared"] if selected is True else [])
        events.append("runtime")
        return {"scope": "CPU mock; native CUDA unverified"}

    monkeypatch.setattr(probe, "_runtime", runtime)
    native_command = paired._teacher_command(config, "A", 0, {"ip": "192.0.2.10"})

    def launch(command, **kwargs):
        assert command == native_command and kwargs["start_new_session"] is True
        assert events[-1] == "runtime"
        preload = json.loads((output / "preload.json").read_text())
        source = "tests/manual/agent_opd/sglang_mamba_snapshots.py"
        assert (source in preload["native_scoring_sources"]) == (selected is True)
        if selected is True:
            assert preload["source_preflight"] == receipts[0]
            assert preload["source_preflight"]["cuda_semantics"] == "UNVERIFIED"
            assert preload["native_scoring_sources"][source] == probe._file_identity(Path(snapshots.__file__))
        else:
            assert "source_preflight" not in preload
        assert all(os.environ[key] == value for key, value in {
            "NCCL_FROM_PLATFORM": "preserved", "CUDA_VISIBLE_DEVICES": "0,1,2,3",
            "SGLANG_FORCE_COARSE_WAR_BARRIER": "0"}.items())
        events.append("teacher")
        return SimpleNamespace(poll=lambda: None)

    monkeypatch.setattr(probe.subprocess, "Popen", launch)
    monkeypatch.setattr(paired, "_wait_teacher_ready", lambda *args: {"model_path": str(model)})
    monkeypatch.setattr(paired, "_check_server", lambda *args: None)
    monkeypatch.setattr(paired, "_stop_child", lambda *args: None)

    async def benchmark(*args):
        events.append("benchmark")
        return {"scope": "CPU mock; no requests made"}

    monkeypatch.setattr(probe, "_benchmark", benchmark)
    probe._run(args)
    result = json.loads((output / "result.json").read_text())
    assert result["status"] == "measurements_completed"
    assert events == (["prepared"] if selected is True else []) + ["runtime", "teacher", "benchmark"]
    if selected is True:
        assert result["source_preflight"] == receipts[0]
        assert receipts[0]["changed_files"] == ["kernels/ops/attention/fla/chunk.py",
                                               "srt/layers/attention/linear/kernels/gdn_triton.py"]
        assert json.loads((output / "source_preflight/preflight.jsonl").read_text()) == receipts[0]
    else:
        assert not receipts and not (output / "source_preflight").exists()
        assert {relative: (root / relative).read_bytes() for relative in before} == before
    assert json.loads(path.read_text()) == config and json.loads(wrapper_path.read_text()) == wrapper


@pytest.mark.parametrize("failure", ["image", "source"])
def test_snapshot_source_error_stops_before_runtime_or_teacher_without_fallback(
        worker_config, sample, tmp_path, monkeypatch, snapshot_source, failure):
    from tests.manual.agent_opd import rjob_warmup as warmup

    path, config, _ = worker_config
    root, snapshots = snapshot_source
    config["selected_fp32_snapshots"] = True
    if failure == "source":
        config["image"] = snapshots.source_manifest()["image"]
        (root / "kernels/ops/attention/fla/chunk.py").write_bytes(b"unqualified source\n")
    path.write_text(json.dumps(config))
    samples = tmp_path / "samples.json"
    samples.write_text(json.dumps({"job": "historical-A-job", "samples": [sample]}))
    output = tmp_path / "failure-output"
    args = SimpleNamespace(config=path, pair="A", samples=samples, output_dir=output, repeats=2, request_timeout=17)
    monkeypatch.setattr(os, "environ", dict(os.environ))
    for key, value in {"KUBEBRAIN_RJOB_NAME": "cpu-test-job", "KUBEBRAIN_REPLICA": "0",
                       "KUBEBRAIN_REPLICA_TOTAL": "1"}.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setattr(warmup, "_worker_environment", lambda local: local.mkdir(parents=True))
    monkeypatch.setattr(probe.importlib.util, "find_spec", lambda name: SimpleNamespace(origin=str(root / "__init__.py")))

    def unexpected(*args, **kwargs):
        pytest.fail("Source preflight failure must not reach runtime or teacher startup")

    monkeypatch.setattr(probe, "_runtime", unexpected)
    monkeypatch.setattr(probe.subprocess, "Popen", unexpected)
    before = {relative: (root / relative).read_bytes() for relative in snapshots.source_manifest()["files"]}
    message = "qualified pinned image" if failure == "image" else "Unrecognized SGLang snapshot source"
    with pytest.raises(ValueError, match=message):
        probe._run(args)
    result = json.loads((output / "result.json").read_text())
    assert result["status"] == "failed" and result["error_type"] == "ValueError"
    assert result["native_measurements_completed"] is False and result["cleanup_completed"] is True
    assert "source_preflight" not in result and "runtime" not in result
    assert not (output / "preload.json").exists() and not (output / "source_preflight").exists()
    assert {relative: (root / relative).read_bytes() for relative in before} == before


def test_fp32_variant_changes_only_selection_and_isolated_output():
    repo = Path(__file__).resolve().parents[2]
    task = repo / "task_memory/task_2026-11-08_qwen35_full_kl_nll"
    base_text = (task / "teacher_scoring_probe_config.json").read_text()
    variant_text = (task / "teacher_scoring_fp32_probe_config.json").read_text()
    base, variant = json.loads(base_text), json.loads(variant_text)
    assert "selected_fp32_snapshots" not in base and variant["selected_fp32_snapshots"] is True
    assert variant["output_parent"] != base["output_parent"]
    assert {key: value for key, value in variant.items() if key != "selected_fp32_snapshots"} == {
        **base, "output_parent": variant["output_parent"]}
    restored = variant_text.replace('  "selected_fp32_snapshots": true,\n', "", 1)
    assert restored.replace(json.dumps(variant["output_parent"]), json.dumps(base["output_parent"]), 1) == base_text
    assert variant.get("envs", {}) == {}
    formal = json.loads((repo / variant["formal_config"]).read_text())
    fixture = json.loads((repo / variant["samples"]).read_text())
    assert len(fixture["samples"]) == 7 and variant["repeats"] == 2 and variant["pairs"] == ["A", "B"]
    assert formal["gpu_tag"] == "H800" and formal["charged_group"] == "codesign"
    for pair in variant["pairs"]:
        assert formal["pairs"][pair]["teacher"]["max_running_requests"] == 1
        assert formal["pairs"][pair]["teacher"]["chunked_prefill_size"] == 8192


@pytest.mark.parametrize("war_barrier", [None, "0", "1"])
def test_preload_hashes_and_actual_war_barrier_env_are_not_native_gpu_evidence(worker_config, monkeypatch, war_barrier):
    path, config, model = worker_config
    config = probe._load_config(path, "A", path.parent / "output")
    config["envs"] = {"SGLANG_FORCE_COARSE_WAR_BARRIER": "not-the-runtime-value"}
    if war_barrier is None:
        monkeypatch.delenv("SGLANG_FORCE_COARSE_WAR_BARRIER", raising=False)
    else:
        monkeypatch.setenv("SGLANG_FORCE_COARSE_WAR_BARRIER", war_barrier)
    monkeypatch.setenv("PROBE_TEST_SECRET", "do-not-record-this-secret")
    for name in ("config.json", "model.safetensors.index.json"):
        (model / name).write_text('{}')
    monkeypatch.setattr(probe.subprocess, "check_output", lambda *args, **kwargs: "NVIDIA H800, 80000 MiB, mock-driver\n" * 4)
    runtime = probe._runtime(config, "A")
    serialized = json.loads(json.dumps(runtime))
    assert serialized["sglang_environment"] == {"SGLANG_FORCE_COARSE_WAR_BARRIER": war_barrier}
    assert "do-not-record-this-secret" not in json.dumps(runtime)
    assert set(probe._SGLANG_SOURCES).issubset(runtime["sglang_sources"])
    assert all(len(item["sha256"]) == 64 and item["bytes"] >= 0 for item in runtime["sglang_sources"].values())
    assert all(runtime["sglang_sources"][name]["bytes"] > 0 for name in probe._SGLANG_SOURCES)
    assert runtime["configured_image"] == config["image"] and "parent allocation input" in runtime["image_identity_limit"]
    monkeypatch.setattr(probe.subprocess, "check_output", lambda *args, **kwargs: "NVIDIA H200, 140000 MiB, mock-driver\n" * 4)
    with pytest.raises(ValueError, match="configured H800 teacher"):
        probe._runtime(config, "A")
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
