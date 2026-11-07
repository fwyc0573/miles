"""Real tiny package validation and CPU native API/lifecycle contracts.

Engine bytes/logprobs are explicit API fixtures, not measured GPU results.
No CUDA-only production kernel, library policy or loader is patched into CPU.
"""

import copy
import json
import sys
import asyncio
from types import SimpleNamespace

import pytest
import torch
from safetensors.torch import load_file, save_file

from examples.agentic_opd.glm_turns import token_hash
from tests.fast.test_qwen35_monitoring import _batch, _versions, _write_native_events, native_fixture
from tests.fast.test_qwen_text_export import _write_export
from tests.manual.agent_opd import inspect_qwen35 as inspector
from tests.manual.agent_opd import qwen_export
from tests.manual.agent_opd import qwen_reload
from miles.utils.audit_utils.event_logger.logger import EventLogger
from miles.utils.audit_utils.event_logger.models import EngineEnvReportEvent
from miles.utils.audit_utils.process_identity import SimpleProcessIdentity


@pytest.fixture(autouse=True)
def single_thread_cpu():
    threads = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(threads)


@pytest.fixture
def native_api(monkeypatch):
    state = SimpleNamespace(body=None, calls=[], scores=[-2.0, -2.0], init_error=False, cleanup_error=False,
                            version="cpu-boundary-fixture", score_version="0", generation_error=False, config_change=None)

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
            args = vars(self.server_args).copy()
            if state.config_change:
                args.update(state.config_change)
            return {"version": state.version, "server_args": args}

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

    fields = ("model_path", "tokenizer_path", "tp_size", "pp_size", "dp_size", "nnodes", "dtype", "quantization",
              "enable_lora", "context_length", "device", "attention_backend", "disable_cuda_graph")
    monkeypatch.setattr(qwen_reload, "_native_types", lambda: (
        Engine, SimpleNamespace, SimpleNamespace, lambda model: (NativeTextClass, "Qwen3_5ForCausalLM"),
        ("cos_sin_cache", "cos_cache", "sin_cache", "inv_freq", "freqs_cis", "expert_mask_gpu"), fields, lambda: 31234))
    return state


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
                "device": "cuda", "attention_backend": "triton", "disable_cuda_graph": True}
    logger = EventLogger(log_dir=run / "events", source=SimpleProcessIdentity(component="main"), file_name="main.jsonl")
    logger.log(EngineEnvReportEvent, {"cell_id": "rollout-cell-0", "workers_hash": "engine-incarnation",
               "server_url": "http://recorded-training-engine", "server_info": {"server_args": original, "version": native_api.version}},
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
