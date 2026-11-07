"""Real tiny package validation and CPU native API/lifecycle contracts.

Engine bytes/logprobs are explicit API fixtures, not measured GPU results.
No CUDA-only production kernel, library policy or loader is patched into CPU.
"""

import copy
import json
import sys
import asyncio
import shlex
import subprocess
import time
from contextlib import contextmanager
from types import SimpleNamespace

import pytest
import torch
from safetensors.torch import load_file, save_file

from tests.ci.ci_register import register_cpu_ci
from examples.agentic_opd.glm_turns import token_hash
from tests.fast.test_qwen35_monitoring import _batch, _versions, _write_native_events, native_fixture
from tests.fast.test_qwen_text_export import _write_export
from tests.manual.agent_opd import inspect_qwen35 as inspector
from tests.manual.agent_opd import qwen_export
from tests.manual.agent_opd import qwen_reload
from miles.utils.audit_utils.event_logger.logger import EventLogger
from miles.utils.audit_utils.event_logger.models import EngineEnvReportEvent
from miles.utils.audit_utils.process_identity import SimpleProcessIdentity

register_cpu_ci(est_time=60, suite="stage-b-cpu", labels=["megatron"])


@pytest.fixture(autouse=True)
def single_thread_cpu():
    threads = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(threads)


@pytest.fixture
def native_api(monkeypatch):
    import psutil

    state = SimpleNamespace(body=None, calls=[], scores=[-2.0, -2.0], init_error=False, cleanup_error=False,
                            version="cpu-boundary-fixture", score_version="0", generation_error=False, config_change=None,
                            process_tree=SimpleNamespace(children=lambda recursive: []))

    class NativeTextClass:
        pass

    NativeTextClass.__module__ = "sglang.srt.models.qwen3_5"
    NativeTextClass.__name__ = "Qwen3_5ForCausalLM"

    class Engine:
        def __init__(self, *, server_args):
            state.calls.append(("start", vars(server_args)))
            self.server_args = server_args
            self.loop = asyncio.new_event_loop()

            async def check_weights(request, context):
                state.calls.append(("checksum", vars(request)))
                body = copy.deepcopy(state.body)
                return body["success"], "CPU native API fixture", body["ranks"], "native-overall-fixture"

            self.tokenizer_manager = SimpleNamespace(check_weights=check_weights, model_config=SimpleNamespace(dtype=torch.float32))
            if state.init_error:
                raise RuntimeError("Injected native startup failure")

        def get_server_info(self):
            from sglang.srt.sampling.watermarking.core import redact_watermark_secrets

            args = vars(self.server_args).copy()
            # These fixed API-fixture values represent native resolved defaults;
            # tests do not run or monkeypatch a CUDA resolution pipeline.
            args.update(enable_lora=False, served_model_name=self.server_args.served_model_name or self.server_args.model_path)
            if state.config_change:
                args.update(state.config_change)
            return {"version": state.version, "server_args": redact_watermark_secrets(args)}

        def get_model_info(self):
            return {"model_path": self.server_args.model_path, "weight_version": "0", "load_format": "auto"}

        def flush_cache(self):
            state.calls.append(("flush", None))
            return True

        def generate(self, **payload):
            state.calls.append(("generate", payload))
            ids = payload["input_ids"]
            if payload["sampling_params"]["max_new_tokens"]:
                if state.generation_error:
                    raise RuntimeError("Injected generation failure")
                return {"text": "fixture text", "output_ids": [7],
                        "meta_info": {"prompt_tokens": len(ids), "weight_version": "0"}}
            start = payload["logprob_start_len"]
            return {"output_ids": [], "text": "", "meta_info": {
                "prompt_tokens": len(ids), "weight_version": state.score_version,
                "prefill_weight_versions": [{"version": state.score_version, "abs_start": 0, "abs_end": len(ids)}],
                "input_token_logprobs": [[None, ids[start], None],
                                          *[[score, token, None] for score, token in zip(state.scores, ids[start + 1:], strict=True)]]}}

        def shutdown(self):
            state.calls.append(("shutdown", None))
            if hasattr(self, "loop"):
                self.loop.close()
            if state.cleanup_error:
                raise RuntimeError("Injected cleanup failure")

    from sglang.srt.server_args import ServerArgs
    from miles.utils.workers.argv_utils import _record_field_names

    fields = _record_field_names(ServerArgs)
    monkeypatch.setattr(qwen_reload, "_native_types", lambda: (
        Engine, SimpleNamespace, SimpleNamespace, lambda model: (NativeTextClass, "Qwen3_5ForCausalLM"),
        ("cos_sin_cache", "cos_cache", "sin_cache", "inv_freq", "freqs_cis", "expert_mask_gpu"), fields, lambda: 31234))
    native_lifecycle = qwen_reload._fresh_engine

    @contextmanager
    def fake_process_scope(*args, **kwargs):
        # The fake Engine owns no OS children. A shared pytest interpreter may
        # retain a previous test's live ResourceTracker; it is not this Engine's
        # lifecycle. Real isolation tests explicitly disable this simulated view.
        with monkeypatch.context() as scope:
            if state.process_tree is not None:
                scope.setattr(psutil, "Process", lambda: state.process_tree)
            with native_lifecycle(*args, **kwargs) as result:
                yield result

    monkeypatch.setattr(qwen_reload, "_fresh_engine", fake_process_scope)
    return state


def _native_command(args):
    from miles.backends.sglang_utils.server_args_utils import server_args_to_argv
    from sglang.srt.sampling.watermarking.core import redact_watermark_command_line

    declared = {name: args[name] for name in (
        "model_path", "tokenizer_path", "tp_size", "dtype", "context_length", "device", "attention_backend",
        "disable_cuda_graph", "random_seed", "trust_remote_code", "host", "port",
    )}
    return redact_watermark_command_line(server_args_to_argv(declared))


def _decoder_fixture(tp, version):
    names = ["model.embed_tokens.weight", "model.norm.weight", "model.norm.gemma_weight",
             "model.layers.0.linear_attn.A_log", "model.layers.0.linear_attn.in_proj_qkvz.weight",
             "model.layers.0.input_layernorm.weight", "model.layers.0.input_layernorm.gemma_weight",
             "model.layers.1.qkv_proj.weight", "model.layers.1.q_norm.weight", "model.layers.1.q_norm.gemma_weight",
             "model.layers.1.mlp.gate_up_proj.weight"]
    return {f"rank{rank}/{name}": f"{index + version:016x}" for rank in range(tp) for index, name in enumerate(names)}


@pytest.fixture
def final_export(tmp_path, monkeypatch, native_fixture, native_api):
    source, export, _ = _write_export(tmp_path, monkeypatch)
    run = tmp_path / "student" / "B" / "job"
    (run / "hf").mkdir(parents=True)
    export = export.rename(run / "hf" / "step_99")
    package = qwen_export.export_text_checkpoint(source, export)
    package["rollout_id"] = 99
    (export / "qwen_text_export.json").write_text(json.dumps(package))
    (export / ".complete").touch()
    (run / "rollout_data").mkdir()
    (run / "train_data").mkdir()
    original = {"model_path": str(source), "tokenizer_path": str(source), "tp_size": 2, "pp_size": 1, "dp_size": 1,
                "nnodes": 1, "quantization": None, "enable_lora": False, "dtype": "float32", "context_length": 64,
                 "device": "cuda", "attention_backend": "triton", "disable_cuda_graph": True, "random_seed": 42,
                 "trust_remote_code": True, "host": "127.0.0.1", "port": 31000,
                 "served_model_name": str(source),
                "enable_watermark": False, "watermark_config": "<redacted>", "watermark_key": "<redacted>", "watermark_key_b": "<redacted>"}
    logger = EventLogger(log_dir=run / "events", source=SimpleProcessIdentity(component="main"), file_name="main.jsonl")
    logger.log(EngineEnvReportEvent, {"cell_id": "rollout-cell-0", "workers_hash": "engine-incarnation",
               "server_url": "http://recorded-training-engine", "server_info": {
                   "server_args": original, "version": native_api.version, "launch_command": _native_command(original)}},
               print_log=False)
    versions = _write_native_events(run)
    event_path = run / "events" / "main.jsonl"
    events = [json.loads(line) for line in event_path.read_text().splitlines()]
    for event in events:
        if event["type"] == "inference_engine_weight_checksum":
            hashes = _decoder_fixture(2, event["weight_version"])
            hashes.update({f"rank{rank}/visual.patch_embed.proj.weight": "00000000000000ff" for rank in range(2)})
            event["engine_snapshots"][0]["tensor_checksums"] = hashes
    event_path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    native_api.body = {"success": True, "ranks": [{
        "checksums": {key.split("/", 1)[1]: value for key, value in _decoder_fixture(2, versions[99]).items() if key.startswith(f"rank{rank}/")},
        "parallelism_info": [{"role": "target", "rank": rank, "size": 2, "tp_rank": rank, "tp_size": 2,
                              "pp_rank": 0, "pp_size": 1, "dp_rank": 0, "dp_size": 1}],
    } for rank in range(2)]}

    # Only the fixture's strata are shortened; production retains all 24 inputs
    # and the accepted 131072-token context boundaries without truncation.
    strata = (("short", 0, 3), ("medium", 3, 6), ("long", 6, 9))
    monkeypatch.setattr(inspector, "LENGTH_STRATA", strata)
    population, samples = copy.deepcopy(native_fixture)
    population["length_strata"] = [
        {"name": name, "lower_exclusive": lower, "upper_inclusive": upper} for name, lower, upper in strata
    ]
    for row, sample in zip(population["population"], samples, strict=True):
        prefix = next(lower + 1 for name, lower, _ in strata if name == row["stratum"])
        tokens = [1, 2, 3] * (prefix // 3) + [1, 2, 3][: prefix % 3] + [4, 5]
        row.update(prompt_token_count=prefix, prompt_sha256=token_hash(tokens[:prefix]))
        sample.update(tokens=tokens, loss_mask=[1, int(sample["index"] % 2 == 0)])
        sample["metadata"]["source"] = {key: row[key] for key in ("uid", "group_id", "prompt_token_count", "prompt_sha256")}
        sample["metadata"]["completion"]["token_sha256"] = token_hash(tokens[prefix:])
        sample["train_metadata"].update(prompt_sha256=row["prompt_sha256"], completion_sha256=token_hash(tokens[prefix:]))
        sample["rollout_log_probs"] = [-2.0, -2.0]
        _versions(sample, str(versions[99]))
    dump = {"rollout_id": 99, "samples": samples, "metadata": {"eval_dataset_names": ["monitor"] * len(samples)}}
    torch.save(dump, run / "rollout_data" / "eval_99.pt")
    batch = _batch(samples, 99, weight_version=versions[99])
    torch.save({"rollout_id": "eval_monitor_99", "rank": 0, "cp_rank": 0, "cp_size": 1,
                "qkv_format": "thd", "rollout_data": batch}, run / "train_data" / "eval_monitor_99_0.pt")
    population_path = tmp_path / "population.json"
    population_path.write_text(json.dumps(population))
    argv = []
    for flag, value in (("hf-checkpoint", source), ("dump-details", run), ("save-debug-event-data", run / "events"),
                        ("save-hf", run / "hf" / "step_{rollout_id}"), ("save-debug-rollout-data", run / "rollout_data" / "{rollout_id}.pt"),
                        ("save-debug-train-data", run / "train_data" / "{rollout_id}_{rank}.pt"),
                        ("num-rollout", 100), ("save-interval", 100), ("rollout-num-gpus-per-engine", 2),
                        ("sglang-dtype", "float32"), ("sglang-context-length", 64), ("sglang-attention-backend", "triton")):
        argv.extend(["--" + flag, str(value)])
    argv.append("--sglang-disable-cuda-graph")
    launch = tmp_path / "launch.json"
    launch.write_text(json.dumps({"student": str(source), "output_dir": str(run), "pair": "B",
                                 "population": {"path": str(population_path)}, "training_argv": argv}))
    runtime = tmp_path / "runtime.json"
    runtime.write_text(json.dumps({"image": "native-image-fixture@sha256:fixture", "pairs": {"B": {"student": {"path": str(source)}}}}))
    return {"export": export, "source": source, "run_dir": run, "population_report": population_path,
            "launch_receipt": launch, "runtime_config": runtime, "device": "cuda", "base_gpu_id": 0}


def test_native_boundary_forwards_all_fixed_inputs_and_generates(final_export, native_api):
    before = {path.name: path.read_bytes() for path in final_export["export"].iterdir()}
    report = qwen_reload.verify(**final_export)
    assert report["verdict"] == "PASS", report
    assert report["reload_verified"] is True
    assert report["weight_publication"]["final_published_weight_version"] == 114
    assert report["weight_publication"]["successful_optimizer_updates"] == 97
    assert len(report["samples"]) == 24
    assert report["probabilities"]["overall"]["expected_valid_tokens"] == 36
    for stratum in ("overall", "short", "medium", "long"):
        assert report["probabilities"][stratum]["abs_mean"] == pytest.approx(0.01)
        assert report["probabilities"][stratum]["missing_or_nonfinite_tokens"] == 0
    assert report["checksums"]["verdict"] == report["post_inference_checksums"]["verdict"] == "PASS"
    assert any("gemma_weight" in key for key in report["checksums"]["eligible_decoder_checksums"])
    assert report["runtime"]["native_model_info"]["weight_version"] == "0"
    assert len([call for call in native_api.calls if call[0] == "generate"]) == 25
    assert native_api.calls[-1][0] == "shutdown"
    requests = [value for name, value in native_api.calls if name == "checksum"]
    assert requests == [{"action": "checksum", "allow_quant_error": False, "selector": "all"}] * 2
    assert report["generation"]["verdict"] == "PASS"
    assert len(report["generation"]["output_token_ids"]) == 1
    assert "native SGLang D8" in report["verification_scope"]
    json.dumps(report, allow_nan=False)
    assert before == {path.name: path.read_bytes() for path in final_export["export"].iterdir()}


def test_stale_package_below_probability_threshold_cannot_pass(final_export, native_api):
    export = final_export["export"]
    index = json.loads((export / "model.safetensors.index.json").read_text())
    name = "model.layers.0.linear_attn.A_log"
    path = export / index["weight_map"][name]
    saved = load_file(path)
    saved[name] += 0.001
    save_file(saved, path)
    # Explicit stale-engine checksum fixture; no custom offline hash calculation.
    native_api.body["ranks"][0]["checksums"][name] = "0000000000000001"
    report = qwen_reload.verify(**final_export)
    assert report["reload_verified"] is False
    assert report["package"]["verdict"] == report["probabilities"]["verdict"] == "PASS"
    assert report["verdict"] == report["checksums"]["verdict"] == "FAIL"
    assert report["checksums"]["mismatches"][0]["key"] == "rank0/" + name
    assert len(report["samples"]) == 24 and all("forward" in row for row in report["samples"])
    assert report["generation"]["verdict"] == "PASS"
    json.dumps(report, allow_nan=False)


def test_saved_a_log_dtype_corruption_is_not_accepted(final_export):
    export = final_export["export"]
    index = json.loads((export / "model.safetensors.index.json").read_text())
    name = next(name for name in index["weight_map"] if name.endswith(".A_log"))
    path = export / index["weight_map"][name]
    saved = load_file(path)
    saved[name] = saved[name].bfloat16()
    save_file(saved, path)
    report = qwen_reload.verify(**final_export)
    assert not report["reload_verified"] and report["verdict"] == "INCOMPLETE"
    assert report["issues"][0]["code"] in ("packaged_dtype_mismatch", "a_log_not_fp32")


@pytest.mark.parametrize("fault,code", [
    ("missing_events", "native_update_receipts_missing"),
    ("stale_final_version", "final_monitor_publication_version_mismatch"),
    ("missing_final_sample", "monitoring_sample_missing"),
    ("missing_final_scores", "score_artifacts_missing"),
    ("trainer_tokens", "trainer_token_mismatch"),
    ("trainer_mask", "trainer_mask_mismatch"),
])
def test_missing_or_mismatched_final_evidence_cannot_pass(final_export, fault, code):
    run = final_export["run_dir"]
    raw_path, score_path = run / "rollout_data" / "eval_99.pt", run / "train_data" / "eval_monitor_99_0.pt"
    dump, score = (torch.load(path, weights_only=False) for path in (raw_path, score_path))
    batch = score["rollout_data"]
    if fault == "missing_events":
        (run / "events").rename(run / "omitted-events")
    elif fault == "stale_final_version":
        batch["metadata"]["weight_version"] -= 1
        for sample in dump["samples"]:
            _versions(sample, str(batch["metadata"]["weight_version"]))
    elif fault == "missing_final_sample":
        dump["samples"] = dump["samples"][1:]
        dump["metadata"]["eval_dataset_names"] = dump["metadata"]["eval_dataset_names"][1:]
        for field in ("sample_indices", "tokens", "loss_masks", "total_lengths", "response_lengths", "log_probs"):
            batch[field] = batch[field][1:]
    elif fault == "trainer_tokens":
        batch["tokens"][0][-1] += 1
    elif fault == "trainer_mask":
        batch["loss_masks"][0] = [0, 1]
    torch.save(dump, raw_path)
    torch.save(score, score_path)
    if fault == "missing_final_scores":
        score_path.unlink()
    report = qwen_reload.verify(**final_export)
    assert not report["reload_verified"] and report["verdict"] == "INCOMPLETE"
    issues = report["weight_publication"]["issues"] + report.get("probabilities", {}).get("overall", {}).get("issues", [])
    assert code in {issue["code"] for issue in issues}
    if fault in ("trainer_tokens", "trainer_mask", "missing_final_sample"):
        assert "forward" in report["samples"][-1]
        assert "forward" not in report["samples"][0]
    if fault == "missing_final_scores":
        assert report["probabilities"]["overall"]["missing_or_nonfinite_tokens"] == 36
        assert report["probabilities"]["overall"]["missing_valid_tokens"] is None
    json.dumps(report, allow_nan=False)


@pytest.mark.parametrize("fault", ["long_stratum", "nonfinite_valid", "nonfinite_masked"])
def test_probabilities_use_original_mask_and_each_stratum_gate(final_export, fault):
    path = final_export["run_dir"] / "train_data" / "eval_monitor_99_0.pt"
    score = torch.load(path, weights_only=False)
    values = score["rollout_data"]["log_probs"]
    if fault == "long_stratum":
        for row in values[16:]:
            row += 0.05
    else:
        values[1][0 if fault == "nonfinite_valid" else 1] = float("nan")
    torch.save(score, path)
    report = qwen_reload.verify(**final_export)
    metrics = report["probabilities"]
    assert metrics["overall"]["expected_valid_tokens"] == 36
    if fault == "long_stratum":
        assert metrics["overall"]["abs_mean"] < 0.03
        assert metrics["long"]["abs_mean"] > 0.03
        assert metrics["overall"]["verdict"] == "PASS"
        assert metrics["long"]["verdict"] == report["verdict"] == "FAIL"
    elif fault == "nonfinite_valid":
        assert metrics["overall"]["nonfinite_valid_tokens"] == metrics["overall"]["missing_or_nonfinite_tokens"] == 1
        assert report["verdict"] == "INCOMPLETE" and not report["reload_verified"]
    else:
        assert metrics["overall"]["nonfinite_masked_positions"] == 1
        assert metrics["overall"]["missing_or_nonfinite_tokens"] == 0
        assert report["verdict"] == "PASS"
    json.dumps(report, allow_nan=False)


@pytest.mark.parametrize("failed", [False, True])
def test_cli_writes_separate_report_without_touching_active_export(final_export, tmp_path, monkeypatch, failed):
    if failed:
        (final_export["run_dir"] / "events").rename(final_export["run_dir"] / "omitted-events")
    report_path = tmp_path / "reload-report.json"
    argv = ["qwen_reload", "--report", str(report_path)]
    for name, value in final_export.items():
        argv.extend(["--" + name.replace("_", "-"), str(value)])
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as result:
        qwen_reload.main()
    assert result.value.code == int(failed)
    report = json.loads(report_path.read_text())
    assert report["reload_verified"] is not failed
    assert json.loads((final_export["export"] / "qwen_text_export.json").read_text())["reload_verified"] is False


def test_cli_refuses_to_overwrite_package_report(final_export, monkeypatch):
    path = final_export["export"] / "qwen_text_export.json"
    before = path.read_bytes()
    argv = ["qwen_reload", "--report", str(path)]
    for name, value in final_export.items():
        argv.extend(["--" + name.replace("_", "-"), str(value)])
    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as result:
        qwen_reload.main()
    assert result.value.code == 2
    assert path.read_bytes() == before


@pytest.mark.parametrize("fault", ["missing_key", "unexpected_key", "derived_buffer", "partial_norm_only", "tp_mismatch"])
def test_full_native_decoder_checksum_contract(final_export, native_api, fault):
    rank = native_api.body["ranks"][0]
    key = "model.layers.0.input_layernorm.gemma_weight"
    if fault == "missing_key":
        rank["checksums"].pop(key)
    elif fault == "unexpected_key":
        rank["checksums"]["model.layers.0.unexpected.weight"] = "0000000000000001"
    elif fault == "derived_buffer":
        rank["checksums"][key] = "0000000000000001"
    elif fault == "partial_norm_only":
        for rank in native_api.body["ranks"]:
            rank["checksums"] = {name: value for name, value in rank["checksums"].items() if name.startswith("model.norm.")}
    else:
        rank["parallelism_info"][0]["tp_size"] = 4
    report = qwen_reload.verify(**final_export)
    assert not report["reload_verified"]
    if fault == "tp_mismatch":
        assert report["verdict"] == "INCOMPLETE"
        assert report["issues"][-1]["code"] == "reload_tp_mismatch"
    else:
        assert report["verdict"] == "FAIL"
        assert report["checksums"]["mismatches"]
        if fault in ("missing_key", "derived_buffer"):
            assert "rank0/" + key in {row["key"] for row in report["checksums"]["mismatches"]}
    assert native_api.calls[-1][0] == "shutdown"


@pytest.mark.parametrize("fault", ["missing_final", "stale_version", "wrong_incarnation", "missing_environment", "partial_reference"])
def test_final_native_origin_receipts_are_mandatory(final_export, native_api, fault):
    path = final_export["run_dir"] / "events" / "main.jsonl"
    events = [json.loads(line) for line in path.read_text().splitlines()]
    final = next(event for event in events if event["type"] == "inference_engine_weight_checksum" and event["rollout_id"] == 99)
    if fault == "missing_final":
        events.remove(final)
    elif fault == "stale_version":
        final["weight_version"] -= 1
    elif fault == "wrong_incarnation":
        final["engine_snapshots"][0]["workers_hash"] = "another-incarnation"
    elif fault == "missing_environment":
        events = [event for event in events if event["type"] != "engine_env_report"]
    else:
        for event in events:
            if event["type"] == "inference_engine_weight_checksum":
                event["engine_snapshots"][0]["tensor_checksums"] = {
                    key: value for key, value in event["engine_snapshots"][0]["tensor_checksums"].items()
                    if "embed_tokens" in key or "/model.norm." in key}
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    report = qwen_reload.verify(**final_export)
    assert report["verdict"] == "INCOMPLETE" and not report["reload_verified"]
    assert not native_api.calls
    if fault == "partial_reference":
        assert report["weight_publication"]["verdict"] == "PASS"
        assert report["issues"][-1]["code"] == "final_decoder_coverage_incomplete"


@pytest.mark.parametrize("fault", ["missing_launch", "wrong_output", "wrong_source", "launch_tp", "native_flag"])
def test_launch_and_actual_engine_origin_must_agree(final_export, native_api, fault):
    path = final_export["launch_receipt"]
    launch = json.loads(path.read_text())
    if fault == "missing_launch":
        path.unlink()
    else:
        if fault == "wrong_output":
            launch["output_dir"] += "-another-run"
        elif fault == "wrong_source":
            launch["student"] += "-another-source"
        else:
            flag = "--rollout-num-gpus-per-engine" if fault == "launch_tp" else "--sglang-dtype"
            launch["training_argv"][launch["training_argv"].index(flag) + 1] = "4" if fault == "launch_tp" else "bfloat16"
        path.write_text(json.dumps(launch))
    report = qwen_reload.verify(**final_export)
    assert report["verdict"] == "INCOMPLETE" and not report["reload_verified"]
    assert not native_api.calls


@pytest.mark.parametrize("fault", ["startup", "cleanup", "scoring_version", "generation", "server_version", "startup_flag"])
def test_native_failures_surface_and_cleanup_only_owned_engine(final_export, native_api, fault):
    if fault == "startup":
        native_api.init_error = True
    elif fault == "cleanup":
        native_api.cleanup_error = True
    elif fault == "scoring_version":
        native_api.score_version = "114"
    elif fault == "generation":
        native_api.generation_error = True
    elif fault == "server_version":
        native_api.version = "another-native-version"
    else:
        native_api.config_change = {"attention_backend": "another-backend"}
    report = qwen_reload.verify(**final_export)
    assert report["verdict"] == "INCOMPLETE" and not report["reload_verified"]
    assert native_api.calls[-1][0] == "shutdown"
    assert [name for name, _ in native_api.calls].count("shutdown") == 1


def test_tp4_comes_from_recorded_launch_not_pair_label(final_export, native_api):
    path = final_export["launch_receipt"]
    launch = json.loads(path.read_text())
    launch["training_argv"][launch["training_argv"].index("--rollout-num-gpus-per-engine") + 1] = "4"
    path.write_text(json.dumps(launch))
    path = final_export["run_dir"] / "events" / "main.jsonl"
    events = [json.loads(line) for line in path.read_text().splitlines()]
    for event in events:
        if event["type"] == "engine_env_report":
            event["server_info"]["server_args"]["tp_size"] = 4
            event["server_info"]["launch_command"] = _native_command(event["server_info"]["server_args"])
        elif event["type"] == "inference_engine_weight_checksum":
            event["engine_snapshots"][0]["tensor_checksums"] = _decoder_fixture(4, event["weight_version"])
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    native_api.body["ranks"] = [{
        "checksums": {key.split("/", 1)[1]: value for key, value in _decoder_fixture(4, 114).items() if key.startswith(f"rank{rank}/")},
        "parallelism_info": [{"rank": rank, "tp_size": 4, "pp_size": 1, "dp_size": 1}],
    } for rank in range(4)]
    report = qwen_reload.verify(**final_export)
    assert report["verdict"] == "PASS", report
    assert report["runtime"]["tp_size"] == 4
    assert report["checksums"]["eligible_tensor_count"] == 44


def test_native_bare_text_namespace_and_tied_head_are_not_offline_fusion():
    config = SimpleNamespace(num_hidden_layers=2, tie_word_embeddings=True)
    reference = _decoder_fixture(2, 114)
    reference.update({"rank0/visual.patch_embed.proj.weight": "00000000000000ff", "rank0/mtp.fc.weight": "00000000000000aa"})
    decoder, excluded = qwen_reload._decoder_checksums(reference, config, 2, reference=True)
    assert excluded == ["rank0/visual.patch_embed.proj.weight", "rank0/mtp.fc.weight"]
    bare = {key.replace("/model.", "/", 1): value for key, value in decoder.items()}
    actual, excluded = qwen_reload._decoder_checksums(bare, config, 2, reference=False)
    assert actual == decoder and not excluded
    assert any(key.endswith(".gemma_weight") for key in actual)
    with pytest.raises(inspector.EvidenceError):
        qwen_reload._decoder_checksums({**reference, "rank0/lm_head.weight": "00000000000000ff"}, config, 2, reference=True)


@pytest.mark.parametrize("missing", [False, True])
def test_native_raw_missing_and_nonfinite_scores_stay_visible(final_export, native_api, missing):
    native_api.scores[0] = None if missing else float("nan")
    report = qwen_reload.verify(**final_export)
    assert report["verdict"] == "INCOMPLETE" and not report["reload_verified"]
    raw = report["samples"][0]["raw_score_counts"]
    assert raw["expected_positions"] == raw["returned_positions"] == 2
    assert raw["finite_positions"] == 1
    assert raw["missing_positions"] == int(missing)
    assert raw["nonfinite_positions"] == int(not missing)
    assert report["probabilities"]["overall"]["expected_valid_tokens"] == 36
    assert native_api.calls[-1][0] == "shutdown"
    json.dumps(report, allow_nan=False)


def _cross_cell_origin(final_export, phase, *, changed_field=None, restore=False):
    """Exercise origin readers; publication consistency has its own native tests."""
    from tests.manual.agent_opd import probe_qwen35_text_reload

    path = final_export["run_dir"] / "events" / "main.jsonl"
    events = [json.loads(line) for line in path.read_text().splitlines()]
    environment = next(event for event in events if event["type"] == "engine_env_report")
    position = 99 if phase == "final" else -1
    checksum = next(event for event in events if event["type"] == "inference_engine_weight_checksum" and event["rollout_id"] == position)
    if phase == "baseline":
        initial_version = checksum["weight_version"]
        for item in events:
            if item["type"] == "inference_engine_weight_checksum":
                item["weight_version"] -= initial_version
    for index in range(1, 4):
        cell = copy.deepcopy(environment)
        cell["cell_id"], cell["workers_hash"] = f"rollout-cell-{index}", f"engine-incarnation-{index}"
        args = cell["server_info"]["server_args"]
        args.update(random_seed=42 + index, port=31000 + index, dist_init_addr=f"127.0.0.1:{32000 + index}",
                    nccl_port=33000 + index, gated_launch_port=34000 + index, engine_info_bootstrap_port=35000 + index)
        cell["server_info"].update(internal_states=[{"fixture": index}], startup_time=index, launch_command=_native_command(args))
        if index == 1 and changed_field:
            if changed_field == "version":
                cell["server_info"]["version"] = "another-native-version"
            elif changed_field == "missing_seed":
                args.pop("random_seed")
            else:
                args[changed_field] = "bfloat16" if changed_field == "dtype" else "another-backend"
        events.append(cell)
        snapshot = copy.deepcopy(checksum["engine_snapshots"][0])
        snapshot.update(cell_id=cell["cell_id"], workers_hash=cell["workers_hash"])
        checksum["engine_snapshots"].append(snapshot)
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    if phase == "baseline":
        publisher_path = final_export["run_dir"] / "events" / "trainer_controller_actor.jsonl"
        publishers = [json.loads(line) for line in publisher_path.read_text().splitlines()]
        for item in publishers:
            if item["type"] == "weight_update_result":
                item["candidate_version"] -= initial_version
                item["published_version"] -= initial_version
                if item["debug_weight_update_id"] == checksum["debug_weight_update_id"]:
                    item["snapshot_cell_id_to_hashes"] = {row["cell_id"]: row["workers_hash"] for row in checksum["engine_snapshots"]}
                    item["updated_cell_ids"] = list(item["snapshot_cell_id_to_hashes"])
        publisher_path.write_text("\n".join(json.dumps(item) for item in publishers) + "\n")
        if restore:
            _append_restoration(final_export["run_dir"], None)
        return probe_qwen35_text_reload._origin(qwen_reload, final_export["run_dir"], final_export["source"])
    publication = {"verdict": "PASS", "issues": [], "publications": [{
        "debug_weight_update_id": checksum["debug_weight_update_id"], "published_version": checksum["weight_version"]}]}
    launch = json.loads(final_export["launch_receipt"].read_text())
    return qwen_reload._final_origin(final_export["run_dir"], publication, launch, 2, final_export["source"])


def _append_restoration(run, position, *, wrong_tensor=False):
    from datetime import datetime, timedelta

    controller = run / "events" / "trainer_controller_actor.jsonl"
    main = run / "events" / "main.jsonl"
    rows = [json.loads(line) for line in controller.read_text().splitlines()]
    snapshots = [json.loads(line) for line in main.read_text().splitlines()]
    publication = next(row for row in rows if row["type"] == "weight_update_result" and row["rollout_id"] == position)
    checksum = next(row for row in snapshots if row["type"] == "inference_engine_weight_checksum"
                    and row["debug_weight_update_id"] == publication["debug_weight_update_id"])
    timestamp = datetime.fromisoformat(checksum["timestamp"])
    later = [datetime.fromisoformat(row["timestamp"]) for row in rows if datetime.fromisoformat(row["timestamp"]) > timestamp]
    interval = (min(later) - timestamp) / 3 if later else timedelta(seconds=1)
    assert interval > timedelta(microseconds=1)
    publication, checksum = copy.deepcopy(publication), copy.deepcopy(checksum)
    publication.update(rollout_id=None, debug_weight_update_id="f" * 32, timestamp=(timestamp + interval).isoformat())
    checksum.update(rollout_id=-1, debug_weight_update_id="f" * 32, timestamp=(timestamp + 2 * interval).isoformat())
    if wrong_tensor:
        for snapshot in checksum["engine_snapshots"]:
            key = next(key for key in snapshot["tensor_checksums"] if "gemma_weight" in key)
            snapshot["tensor_checksums"][key] = "badbadbadbadbadb"
    rows.append(publication)
    snapshots.append(checksum)
    controller.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    main.write_text("\n".join(json.dumps(row) for row in snapshots) + "\n")


def test_baseline_origin_binds_initial_publication_not_later_version_zero_restore(final_export):
    event, _, _ = _cross_cell_origin(final_export, "baseline", restore=True)
    assert event.weight_version == 0 and event.rollout_id == -1
    assert event.debug_weight_update_id == "0" * 32


@pytest.mark.parametrize("wrong_tensor", [False, True])
def test_final_reload_binds_planned_publication_before_final_restore(final_export, native_api, wrong_tensor):
    _append_restoration(final_export["run_dir"], 99, wrong_tensor=wrong_tensor)
    report = qwen_reload.verify(**final_export)
    if wrong_tensor:
        assert report["verdict"] == "INCOMPLETE" and not report["reload_verified"]
        assert not native_api.calls
    else:
        assert report["verdict"] == "PASS", report["issues"]
        assert report["final_origin"]["checksum_event"]["debug_weight_update_id"] != "f" * 32


def test_fake_native_process_tree_does_not_own_prior_pytest_children(final_export, native_api):
    live = subprocess.Popen([sys.executable, "-c", "print('ready', flush=True); input()"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    try:
        assert live.stdout.readline() == "ready\n"
        report = qwen_reload.verify(**final_export)
        assert report["verdict"] == "PASS", report["issues"]
        assert native_api.calls[-1][0] == "shutdown"
        assert report["cleanup"]["observed_owned_child_pids"] == []
        assert live.poll() is None
    finally:
        live.stdin.write("\n")
        live.stdin.flush()
        live.wait(timeout=5)
        live.stdout.close()
        live.stdin.close()


@pytest.mark.parametrize("phase", ["baseline", "final"])
def test_origin_accepts_per_cell_sampling_seeds(final_export, phase):
    event, chosen, _ = _cross_cell_origin(final_export, phase)
    assert len(event.engine_snapshots) == 4
    assert chosen["random_seed"] == 42
    assert "random_seed" not in qwen_reload._ALLOCATION_FIELDS


@pytest.mark.parametrize("phase", ["baseline", "final"])
@pytest.mark.parametrize("field", ["dtype", "attention_backend", "version", "missing_seed"])
def test_cross_cell_other_config_changes_remain_rejected(final_export, phase, field):
    with pytest.raises(inspector.EvidenceError):
        _cross_cell_origin(final_export, phase, changed_field=field)


@pytest.mark.parametrize("changed", [False, True])
def test_fresh_reference_seed_is_reproduced_exactly(final_export, native_api, changed):
    if changed:
        native_api.config_change = {"random_seed": 43}
    report = qwen_reload.verify(**final_export)
    startup = next(value for name, value in native_api.calls if name == "start")
    assert startup["random_seed"] == 42
    assert native_api.calls[-1][0] == "shutdown"
    if changed:
        assert report["verdict"] == "INCOMPLETE" and not report["reload_verified"]
        assert report["issues"][-1]["code"] == "reload_native_config_mismatch"
    else:
        assert report["verdict"] == "PASS" and report["reload_verified"]


def test_local_native_record_constructor_boundary(final_export):
    import ast
    import inspect
    from pathlib import Path
    import sglang
    from sglang.srt.server_args import ServerArgs
    from miles.utils.workers.argv_utils import _record_field_names

    path = final_export["run_dir"] / "events" / "main.jsonl"
    environment = next(json.loads(line) for line in path.read_text().splitlines() if json.loads(line)["type"] == "engine_env_report")
    declared = qwen_reload._recorded_server_args(environment["server_info"])
    config = {name: getattr(declared, name) for name in _record_field_names(ServerArgs)}
    assert set(_record_field_names(ServerArgs)) <= set(inspect.signature(ServerArgs).parameters)
    inspect.signature(ServerArgs).bind(**config)
    record = ServerArgs(**config)
    assert record.random_seed == 42 and record.tp_size == 2
    assert record.watermark_config is record.watermark_key is record.watermark_key_b is None
    assert not getattr(record, "_resolution_finished", False)
    # Read the actual constructor boundary without importing/launching CUDA Engine.
    source = Path(sglang.__file__).parent / "srt" / "entrypoints" / "engine.py"
    engine = next(node for node in ast.parse(source.read_text()).body if isinstance(node, ast.ClassDef) and node.name == "Engine")
    constructor = next(node for node in engine.body if isinstance(node, ast.FunctionDef) and node.name == "__init__")
    assert constructor.args.kwarg is not None
    assert any(isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == constructor.args.kwarg.arg
               and isinstance(node.slice, ast.Constant) and node.slice.value == "server_args" for node in ast.walk(constructor))


def test_redacted_report_is_not_native_constructor_input(final_export, native_api):
    report = qwen_reload.verify(**final_export)
    assert report["verdict"] == "PASS", report
    startup = next(value for name, value in native_api.calls if name == "start")
    assert startup["watermark_config"] is startup["watermark_key"] is startup["watermark_key_b"] is None
    assert startup["random_seed"] == 42 and startup["context_length"] == 64
    assert startup["dtype"] == "float32" and startup["disable_cuda_graph"] is True


@pytest.mark.parametrize("fault", ["missing", "malformed", "unknown_flag", "redacted", "model", "seed", "tp", "missing_context", "dtype"])
def test_native_cli_missing_or_inconsistent_evidence_cannot_pass(final_export, native_api, fault):
    path = final_export["run_dir"] / "events" / "main.jsonl"
    events = [json.loads(line) for line in path.read_text().splitlines()]
    info = next(event["server_info"] for event in events if event["type"] == "engine_env_report")
    if fault == "missing":
        info.pop("launch_command")
    elif fault == "malformed":
        info["launch_command"] = "--model-path 'unclosed"
    elif fault in ("unknown_flag", "redacted"):
        info["launch_command"] += " --unsupported-native-flag" if fault == "unknown_flag" else " --watermark-config '<redacted>'"
    else:
        argv = shlex.split(info["launch_command"])
        flag = {"model": "--model-path", "seed": "--random-seed", "tp": "--tp-size",
                "missing_context": "--context-length", "dtype": "--dtype"}[fault]
        index = argv.index(flag)
        if fault == "missing_context":
            del argv[index:index + 2]
        else:
            argv[index + 1] = {"model": "/another-model", "seed": "99", "tp": "4", "dtype": "float16"}[fault]
        info["launch_command"] = shlex.join(argv)
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    report = qwen_reload.verify(**final_export)
    assert report["verdict"] == "INCOMPLETE" and not report["reload_verified"]
    if fault in ("missing_context", "dtype"):
        assert report["issues"][-1]["code"] == "reload_native_config_mismatch"
        assert native_api.calls[-1][0] == "shutdown"
    else:
        assert report["issues"][-1]["code"].startswith("native_launch_command_")
        assert not native_api.calls


def test_nondefault_selected_native_cli_settings_are_reconstructed(final_export, native_api):
    path = final_export["run_dir"] / "events" / "main.jsonl"
    events = [json.loads(line) for line in path.read_text().splitlines()]
    info = next(event["server_info"] for event in events if event["type"] == "engine_env_report")
    info["server_args"].update(random_seed=97, context_length=96, max_running_requests=7)
    info["launch_command"] = _native_command(info["server_args"]) + " --max-running-requests 7"
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    path = final_export["launch_receipt"]
    launch = json.loads(path.read_text())
    index = launch["training_argv"].index("--sglang-context-length")
    launch["training_argv"][index + 1] = "96"
    path.write_text(json.dumps(launch))
    report = qwen_reload.verify(**final_export)
    assert report["verdict"] == "PASS", report
    startup = next(value for name, value in native_api.calls if name == "start")
    assert startup["random_seed"] == 97 and startup["context_length"] == 96 and startup["max_running_requests"] == 7
    assert report["checksums"]["verdict"] == report["post_inference_checksums"]["verdict"] == "PASS"


@pytest.mark.parametrize("phase", ["baseline", "final"])
def test_origin_refuses_absent_native_cli_before_copy_or_startup(final_export, native_api, phase):
    path = final_export["run_dir"] / "events" / "main.jsonl"
    events = [json.loads(line) for line in path.read_text().splitlines()]
    next(event["server_info"] for event in events if event["type"] == "engine_env_report").pop("launch_command")
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    with pytest.raises(inspector.EvidenceError) as error:
        _cross_cell_origin(final_export, phase)
    assert error.value.code == "native_launch_command_missing"
    assert not native_api.calls


def test_automatic_served_name_follows_relocated_model_only(final_export, native_api):
    path = final_export["run_dir"] / "events" / "main.jsonl"
    events = [json.loads(line) for line in path.read_text().splitlines()]
    info = next(event["server_info"] for event in events if event["type"] == "engine_env_report")
    info["server_args"]["served_model_name"] = str(final_export["source"])
    info["server_args"]["max_total_tokens"] = None
    info.update(max_total_num_tokens=1697128, startup_time={"fixture": 1}, frontend="python")
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    native_api.config_change = {"max_total_num_tokens": 1743657}
    report = qwen_reload.verify(**final_export)
    assert report["verdict"] == "PASS", report.get("issues")
    assert report["checksums"]["verdict"] == report["post_inference_checksums"]["verdict"] == "PASS"


@pytest.fixture
def baseline_input(final_export):
    run = final_export["run_dir"]
    dump = torch.load(run / "rollout_data" / "eval_99.pt", weights_only=False)
    dump["rollout_id"] = 0
    for sample in dump["samples"]:
        _versions(sample, "0")
    torch.save(dump, run / "rollout_data" / "eval_0.pt")
    batch = _batch(dump["samples"], 0, weight_version=0)
    torch.save({"rollout_id": "eval_monitor_0", "rank": 0, "cp_rank": 0, "cp_size": 1,
                "qkv_format": "thd", "rollout_data": batch}, run / "train_data" / "eval_monitor_0_0.pt")
    return run


def test_corrupted_selected_baseline_reference_is_rejected(baseline_input):
    from tests.manual.agent_opd import probe_qwen35_text_reload as probe

    path = baseline_input / "train_data" / "eval_monitor_0_0.pt"
    score = torch.load(path, weights_only=False)
    score["rollout_data"]["log_probs"] = [torch.full_like(value, -12.422473907470703)
                                           for value in score["rollout_data"]["log_probs"]]
    torch.save(score, path)
    with pytest.raises(inspector.EvidenceError, match="reference"):
        probe._input(qwen_reload, baseline_input)


@pytest.mark.parametrize("explicit,changed", [(False, True), (True, False), (True, True)])
def test_served_name_default_rule_never_hides_explicit_or_wrong_names(final_export, native_api, explicit, changed):
    path = final_export["run_dir"] / "events" / "main.jsonl"
    events = [json.loads(line) for line in path.read_text().splitlines()]
    info = next(event["server_info"] for event in events if event["type"] == "engine_env_report")
    if explicit:
        info["server_args"]["served_model_name"] = "chosen-api-name"
        info["launch_command"] += " --served-model-name chosen-api-name"
    if changed:
        native_api.config_change = {"served_model_name": "incorrect-api-name"}
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    report = qwen_reload.verify(**final_export)
    assert report["reload_verified"] is (not changed)
    if changed:
        assert report["issues"][-1]["code"] == "reload_native_config_mismatch"
        assert report["startup_settings"]["mismatches"][0]["field"] == "served_model_name"


@pytest.mark.parametrize("changed", [False, True])
def test_explicit_token_budget_remains_retained(final_export, native_api, changed):
    path = final_export["run_dir"] / "events" / "main.jsonl"
    events = [json.loads(line) for line in path.read_text().splitlines()]
    info = next(event["server_info"] for event in events if event["type"] == "engine_env_report")
    info["server_args"]["max_total_tokens"] = 100
    info["launch_command"] += " --max-total-tokens 100"
    path.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    if changed:
        native_api.config_change = {"max_total_tokens": 200}
    report = qwen_reload.verify(**final_export)
    assert report["reload_verified"] is (not changed)
    assert next(value for name, value in native_api.calls if name == "start")["max_total_tokens"] == 100


def test_valid_selected_baseline_is_qualified_with_existing_metric(baseline_input):
    from tests.manual.agent_opd import probe_qwen35_text_reload as probe

    sample, tokens, mask, train, artifacts = probe._input(qwen_reload, baseline_input)
    measured = artifacts["selected_reference_qualification"]
    assert measured["verdict"] == "PASS" and measured["threshold"] == 0.03
    assert measured["abs_mean"] == pytest.approx(0.01)
    assert measured["missing_valid_tokens"] == measured["nonfinite_valid_tokens"] == 0
    assert len(tokens) == len(sample["tokens"]) and len(train) == len(mask)


@pytest.mark.parametrize("fault", ["nan", "missing", "zero_target", "valid_alternative"])
def test_selected_baseline_invalid_evidence_never_switches_reference(baseline_input, fault):
    from tests.manual.agent_opd import probe_qwen35_text_reload as probe

    raw_path, score_path = baseline_input / "rollout_data" / "eval_0.pt", baseline_input / "train_data" / "eval_monitor_0_0.pt"
    dump, score = (torch.load(path, weights_only=False) for path in (raw_path, score_path))
    sample = min(dump["samples"], key=lambda item: (len(item["tokens"]), item["index"]))
    batch = score["rollout_data"]
    index = batch["sample_indices"].index(sample["index"])
    if fault == "missing":
        score_path.unlink()
    else:
        if fault == "zero_target":
            sample["loss_mask"] = [0] * sample["response_length"]
            batch["loss_masks"][index] = sample["loss_mask"]
        else:
            batch["log_probs"][index][:] = float("nan") if fault == "nan" else -12.422473907470703
        torch.save(dump, raw_path)
        torch.save(score, score_path)
    with pytest.raises(inspector.EvidenceError):
        probe._input(qwen_reload, baseline_input)


def test_real_terminal_children_are_reaped_without_touching_live_sibling():
    import psutil

    exited = subprocess.Popen([sys.executable, "-c", "print('exiting', flush=True)"], stdout=subprocess.PIPE, text=True)
    live = subprocess.Popen([sys.executable, "-c", "print('ready', flush=True); input()"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    try:
        child = psutil.Process(exited.pid)
        assert exited.stdout.read() == "exiting\n"
        assert live.stdout.readline() == "ready\n"
        deadline = time.monotonic() + 5
        while child.status() != psutil.STATUS_ZOMBIE:
            assert time.monotonic() < deadline
            time.sleep(0.001)
        assert child.is_running()  # This is the old probe's false-active predicate.
        report = qwen_reload._reap_terminal_children([child], [])
        assert report["verdict"] == "PASS" and report["remaining_owned_child_pids"] == []
        assert report["children"] == [{"pid": exited.pid, "reaped": True, "status": psutil.STATUS_ZOMBIE, "exit_code": 0}]
        assert not psutil.pid_exists(exited.pid)
        assert psutil.Process(live.pid).is_running()
        active = qwen_reload._reap_terminal_children([psutil.Process(live.pid)], [])
        assert active["verdict"] == "INCOMPLETE" and active["remaining_owned_child_pids"] == [live.pid]
        assert psutil.Process(live.pid).is_running()
    finally:
        live.stdin.write("\n")
        live.stdin.flush()
        live.wait(timeout=5)
        exited.wait(timeout=5)
        exited.stdout.close()
        live.stdout.close()
        live.stdin.close()


def test_native_shutdown_refuses_interpreter_with_preexisting_child(final_export, native_api):
    native_api.process_tree = None  # Exercise the unmodified real isolation guard.
    live = subprocess.Popen([sys.executable, "-c", "print('ready', flush=True); input()"],
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    try:
        assert live.stdout.readline() == "ready\n"
        report = qwen_reload.verify(**final_export)
        assert report["verdict"] == "INCOMPLETE" and report["issues"][-1]["code"] == "native_interpreter_not_isolated"
        assert not native_api.calls
        assert live.poll() is None
    finally:
        live.stdin.write("\n")
        live.stdin.flush()
        live.wait(timeout=5)
        live.stdout.close()
        live.stdin.close()


def test_real_multiprocessing_child_is_joined_with_its_own_handle():
    import multiprocessing
    import os
    import psutil

    process = multiprocessing.get_context("fork").Process(target=os._exit, args=(0,))
    process.start()
    try:
        child = psutil.Process(process.pid)
        deadline = time.monotonic() + 5
        while child.status() != psutil.STATUS_ZOMBIE:
            assert time.monotonic() < deadline
            time.sleep(0.001)
        report = qwen_reload._reap_terminal_children([child], [process])
        assert report["verdict"] == "PASS" and report["children"][0]["reaped"]
        assert process.exitcode == 0 and not process.is_alive()
        assert not psutil.pid_exists(process.pid)
    finally:
        process.join(timeout=5)
        process.close()


def test_probe_rejects_corrupt_reference_before_copy_or_engine(final_export, baseline_input, native_api, tmp_path, monkeypatch):
    from tests.manual.agent_opd import probe_qwen35_text_reload as probe

    _cross_cell_origin(final_export, "baseline")
    path = baseline_input / "train_data" / "eval_monitor_0_0.pt"
    score = torch.load(path, weights_only=False)
    score["rollout_data"]["log_probs"] = [torch.full_like(value, -12.422473907470703)
                                           for value in score["rollout_data"]["log_probs"]]
    torch.save(score, path)

    def forbidden_copy(*args):
        pytest.fail("Invalid reference reached expensive copy")

    monkeypatch.setattr(probe, "_copy", forbidden_copy)
    report = {"issues": [], "verdict": "INCOMPLETE"}
    args = SimpleNamespace(run_dir=baseline_input, source=final_export["source"], output=tmp_path / "new-copy")
    with pytest.raises(inspector.EvidenceError) as error:
        probe._run(args, report)
    assert error.value.code == "baseline_reference_unqualified"
    assert "copy" not in report and not args.output.exists() and not native_api.calls


@pytest.mark.parametrize("terminal", [False, True])
def test_resource_tracker_owner_and_whole_interpreter_exit(terminal):
    import textwrap

    script = textwrap.dedent("""
        import json
        import os
        import sys
        import time
        import psutil
        from multiprocessing import resource_tracker
        from tests.manual.agent_opd.qwen_reload import _reap_terminal_children

        owner = resource_tracker._resource_tracker
        owner.ensure_running()
        pid, fd = owner._pid, owner._fd
        child = psutil.Process(pid)
        terminal = sys.argv[1] == "terminal"
        if terminal:
            # Fault setup: EOF terminates the real tracker without a signal.
            # Keep the owner's fd valid, as after native child termination.
            with open(os.devnull, "wb") as sink:
                os.dup2(sink.fileno(), fd)
            deadline = time.monotonic() + 5
            while child.status() != psutil.STATUS_ZOMBIE:
                assert time.monotonic() < deadline
                time.sleep(0.001)
        report = _reap_terminal_children([child], [])
        print(json.dumps({"report": report, "pid": pid, "fd": fd,
                          "owner_pid": owner._pid, "owner_fd": owner._fd,
                          "pid_exists": psutil.pid_exists(pid)}), flush=True)
        # Normal interpreter exit must run the real ResourceTracker destructor.
    """)
    result = subprocess.run([sys.executable, "-B", "-c", script, "terminal" if terminal else "live"],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert "Exception ignored" not in result.stderr and "ChildProcessError" not in result.stderr, result.stderr
    evidence = json.loads(result.stdout)
    if terminal:
        assert evidence["report"]["verdict"] == "PASS"
        assert evidence["owner_pid"] is evidence["owner_fd"] is None
        assert evidence["report"]["children"][0]["owner"] == "multiprocessing.resource_tracker"
        assert evidence["pid_exists"] is False
    else:
        assert evidence["report"]["verdict"] == "INCOMPLETE"
        assert evidence["owner_pid"] == evidence["pid"] and evidence["owner_fd"] == evidence["fd"]
        assert evidence["report"]["remaining_owned_child_pids"] == [evidence["pid"]]
        assert evidence["pid_exists"] is True
