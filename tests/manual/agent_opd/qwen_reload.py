"""Verify an existing final Qwen3.5 text-HF export without changing it or training.

Example (run after final export and monitoring artifacts have settled):
    python -m tests.manual.agent_opd.qwen_reload --export RUN/hf/step_99 \
        --source SOURCE_MODEL --run-dir RUN --population-report POPULATION/population.json \
        --launch-receipt LAUNCH.json --runtime-config RUNTIME.json \
        --device cuda --base-gpu-id 0 --report RELOAD_REPORT.json

The sole reload path is a fresh native SGLang Engine. Its complete eligible
decoder checksums must equal the final native publisher's checksums, including
derived buffers. Numerical proximity alone cannot establish final identity.
Original final monitoring inputs/masks use the existing 0.03 summary. Scores
are native input-token prefill logprobs, not original decode observations.
Run in a dedicated interpreter: native Engine.shutdown reaps its child tree.
No checkpoint, package report, optimizer or training state is written.
"""

import argparse
import inspect
import json
import math
import platform
import re
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import quote

import torch
from transformers import AutoConfig

from examples.agentic_opd.glm_turns import token_hash
from miles.rollout.generate_utils.prefill_logprobs import _build_prefill_scoring_payload, _extract_response_logprobs
from miles.utils.audit_utils.checksum_utils import merge_inference_engine_ranks
from miles.utils.audit_utils.event_analyzer.rules.checksum_compare import compare_flat_dicts
from miles.utils.audit_utils.event_logger.models import EngineEnvReportEvent
from tests.manual.agent_opd import inspect_qwen35 as native
from tests.manual.agent_opd import qwen_export

_ACCEPTANCE = inspect.signature(native.inspect).parameters
_FINAL_ROLLOUT = _ACCEPTANCE["checkpoints"].default[-1]
_THRESHOLD = _ACCEPTANCE["threshold"].default
_COMPARISON = "hf_reload"
_ALLOCATION_FIELDS = {
    "model_path", "tokenizer_path", "host", "port", "base_gpu_id", "node_rank", "nnodes", "dist_init_addr", "nccl_port",
    "gated_launch_port", "engine_info_bootstrap_port", "disaggregation_bootstrap_port",
}


def _unavailable(row, error):
    issue = native._issue(error)
    row["issues"].append(issue)
    row["comparisons"][_COMPARISON] = {
        "verdict": "INCOMPLETE", "issues": [issue], "nonfinite_valid_tokens": None, "missing_valid_tokens": None,
        "nonfinite_masked_positions": None, "missing_masked_positions": None,
    }


def _package(export, source, run_dir):
    native._require(export == run_dir / "hf" / f"step_{_FINAL_ROLLOUT}", "final_export_path_mismatch",
                    "The export must be this run's final HF directory")
    package = json.loads((export / "qwen_text_export.json").read_text())
    native._require(package["status"] == "packaged" and package["rollout_id"] == _FINAL_ROLLOUT,
                    "final_packaging_incomplete", "Need completed final text packaging, not just a directory or marker")
    native._require(Path(package["source"]).resolve() == source, "export_source_mismatch", "Packaging names a different source")
    native._require((export / ".complete").is_file(), "native_export_incomplete", "Native export completion is absent")
    qwen_export._validate_tokenizer(source, export)
    config = AutoConfig.from_pretrained(export, local_files_only=True)
    expected_config = qwen_export._text_config(source)
    # Only file identity, library version and the export-selected weight dtype
    # differ legitimately from the source text schema.
    excluded = {"_name_or_path", "transformers_version", "dtype"}
    actual = {key: value for key, value in config.to_dict().items() if key not in excluded}
    expected = {key: value for key, value in expected_config.to_dict().items() if key not in excluded}
    native._require(actual == expected, "text_config_mismatch",
                    f"Source/export text configuration differs: {sorted(key for key in actual.keys() | expected.keys() if actual.get(key) != expected.get(key))}")
    tensors = qwen_export._read_tensors(export)
    shapes = qwen_export._expected_shapes(config)
    required = set(shapes) - ({"lm_head.weight"} if config.tie_word_embeddings else set())
    native._require(set(tensors) == required, "packaged_tensor_coverage_mismatch", "Packaged names differ from the text-loader schema")
    embedding_dtype = tensors["model.embed_tokens.weight"].dtype
    native._require(embedding_dtype in qwen_export._DTYPES and str(config.dtype) == str(qwen_export._DTYPES[embedding_dtype]),
                    "packaged_dtype_mismatch", "Declared dtype differs from the saved embedding")
    for name, tensor in tensors.items():
        native._require(tensor.shape == shapes[name], "packaged_shape_mismatch", name)
        native._require(tensor.dtype in {embedding_dtype, "F32"}, "packaged_dtype_mismatch", name)
        if name.endswith(".linear_attn.A_log"):
            native._require(tensor.dtype == "F32", "a_log_not_fp32", f"{name}: saved {tensor.dtype}, expected FP32")
    native._require(package["tensor_dtypes"] == dict(Counter(tensor.dtype for tensor in tensors.values()))
                    and package["saved_tensor_count"] == len(tensors),
                    "packaging_receipt_mismatch", "Saved tensors disagree with packaging evidence")
    return config, tensors, {"verdict": "PASS", "rollout_id": package["rollout_id"],
                            "model_type": config.model_type, "architecture": config.architectures[0],
                            "tokenizer_assets_equal": True, "saved_tensor_count": len(tensors)}


def _launch(launch_receipt, runtime_config, source, run_dir, population_report):
    launch = json.loads(launch_receipt.read_text())
    runtime = json.loads(runtime_config.read_text())
    argv = launch["training_argv"]
    native._require(Path(launch["output_dir"]).resolve() == run_dir and Path(launch["student"]).resolve() == source,
                    "launch_origin_mismatch", "Launch output/source differs from the requested run")
    native._require(Path(launch["population"]["path"]).resolve() == population_report,
                    "launch_population_mismatch", "Launch names a different frozen population")
    native._require(runtime["pairs"][launch["pair"]]["student"]["path"] == str(source),
                    "runtime_source_mismatch", "Runtime configuration names another student")
    expected = {"--hf-checkpoint": str(source), "--dump-details": str(run_dir),
                "--save-debug-event-data": str(run_dir / "events"),
                "--save-hf": str(run_dir / "hf" / "step_{rollout_id}"),
                "--save-debug-rollout-data": str(run_dir / "rollout_data" / "{rollout_id}.pt"),
                "--save-debug-train-data": str(run_dir / "train_data" / "{rollout_id}_{rank}.pt"),
                "--num-rollout": str(_FINAL_ROLLOUT + 1), "--save-interval": str(_FINAL_ROLLOUT + 1)}
    for flag, value in expected.items():
        native._require(argv.count(flag) == 1 and argv[argv.index(flag) + 1] == value,
                        "launch_argv_mismatch", flag)
    flag = "--rollout-num-gpus-per-engine"
    native._require(argv.count(flag) == 1, "launch_topology_missing", flag)
    tp = int(argv[argv.index(flag) + 1])
    native._require(tp > 0, "launch_topology_invalid", str(tp))
    return launch, tp, runtime["image"]


def _server_config(info):
    # Native releases publish either a server_args record or the flat resolved record.
    from sglang.srt.server_args import ServerArgs
    from miles.utils.workers.argv_utils import _record_field_names

    record = info["server_args"] if "server_args" in info else info
    return {name: record[name] for name in _record_field_names(ServerArgs) if name in record}


def _final_origin(run_dir, publication, launch, tp, source):
    native._require(publication["verdict"] == "PASS", "final_publication_unverified", str(publication["issues"]))
    final = publication["publications"][-1]
    events = native.EventReader(run_dir / "events", strict=True, event_types=(
        native.InferenceEngineWeightChecksumEvent, EngineEnvReportEvent,
    )).read()
    matches = [event for event in events if isinstance(event, native.InferenceEngineWeightChecksumEvent)
               and event.debug_weight_update_id == final["debug_weight_update_id"]]
    native._require(len(matches) == 1, "final_checksum_missing_or_duplicate", str(len(matches)))
    event = matches[0]
    native._require(event.rollout_id == _FINAL_ROLLOUT and event.weight_version == final["published_version"]
                    and event.trainer_model_id is None, "final_checksum_origin_mismatch", event.debug_weight_update_id)
    environments = []
    for snapshot in event.engine_snapshots:
        records = [item for item in events if isinstance(item, EngineEnvReportEvent)
                   and item.cell_id == snapshot.cell_id and item.workers_hash == snapshot.workers_hash
                   and item.timestamp <= event.timestamp]
        native._require(bool(records), "final_engine_environment_missing", snapshot.cell_id)
        environments.append(max(records, key=lambda item: item.timestamp))
    original = _server_config(environments[0].server_info)
    native._require(all({key: value for key, value in _server_config(item.server_info).items() if key not in _ALLOCATION_FIELDS}
                        == {key: value for key, value in original.items() if key not in _ALLOCATION_FIELDS} for item in environments),
                    "final_engine_config_disagreement", "Publisher engine configurations disagree")
    native._require(Path(original["model_path"]).resolve() == source and original["tp_size"] == tp,
                    "final_engine_launch_mismatch", "Actual source/TP disagrees with launch")
    native._require(original["pp_size"] == original["dp_size"] == original["nnodes"] == 1,
                    "reload_topology_unsupported", "This task's local reload requires TP-only single-node serving")
    native._require(not original["quantization"] and not original["enable_lora"],
                    "reload_weight_mode_unsupported", "D13 requires the native unquantized full decoder")
    # Verify explicit engine flags against native resolved values/types; router flags
    # belong to the router, not this fresh local Engine.
    from miles.backends.sglang_utils.sglang_config import _add_prefixed_primary_server_args

    parser = argparse.ArgumentParser(add_help=False)
    _add_prefixed_primary_server_args(parser)
    parsed, unknown = parser.parse_known_args(launch["training_argv"])
    native._require(not any(arg.startswith("--sglang-") and not arg.startswith("--sglang-router-") for arg in unknown),
                    "launch_engine_flag_unsupported", str(unknown))
    for action in parser._actions:
        if any(flag in launch["training_argv"] for flag in action.option_strings):
            name = action.dest.removeprefix("sglang_")
            native._require(name in original and original[name] == getattr(parsed, action.dest),
                            "launch_engine_flag_mismatch", name)
    return event, original, environments[0].server_info["version"]


def _decoder_checksums(checksums, config, tp, *, reference):
    decoder, excluded = {}, []
    for key, value in checksums.items():
        match = re.fullmatch(r"rank(\d+)/(.+)", key)
        native._require(match is not None and int(match[1]) in range(tp), "checksum_rank_invalid", key)
        rank, name = match.groups()
        native._require(isinstance(value, str) and re.fullmatch(r"[0-9a-f]{16}", value) is not None,
                        "native_checksum_invalid", key)
        if name.startswith(("visual.", "mtp.")):
            native._require(reference, "text_reload_excluded_tensor_present", key)
            excluded.append(key)
            continue
        # The native bare text backbone owns layers/embed_tokens/norm directly;
        # the source ConditionalGeneration owns that same backbone as model.
        if name.startswith(("layers.", "embed_tokens.", "norm.")):
            name = "model." + name
        layer = re.fullmatch(r"model.layers.(\d+)\.(.+)", name)
        native._require(name in ("model.embed_tokens.weight", "model.norm.weight", "model.norm.gemma_weight", "lm_head.weight")
                        or layer is not None and int(layer[1]) in range(config.num_hidden_layers),
                        "unexpected_decoder_namespace", key)
        canonical = f"rank{rank}/{name}"
        native._require(canonical not in decoder, "duplicate_decoder_checksum", canonical)
        decoder[canonical] = value
    if reference:
        for rank in range(tp):
            prefix = f"rank{rank}/model."
            native._require(prefix + "embed_tokens.weight" in decoder and prefix + "norm.weight" in decoder,
                            "final_decoder_coverage_incomplete", prefix)
            for layer_id in range(config.num_hidden_layers):
                native._require(any(key.startswith(prefix + f"layers.{layer_id}.") for key in decoder),
                                "final_decoder_coverage_incomplete", f"{prefix}layers.{layer_id}")
            head = f"rank{rank}/lm_head.weight"
            # WeightChecker.named_parameters() deduplicates the tied head, whose
            # canonical source name is model.embed_tokens.weight (Qwen3VL init).
            native._require((head not in decoder) == config.tie_word_embeddings,
                            "final_tied_head_coverage_mismatch", head)
    return decoder, excluded


def _checksum_comparison(body, final_decoder, config, tp):
    ranks = body["ranks"]
    native._require(len(ranks) == tp, "reload_tp_mismatch", str(len(ranks)))
    seen = []
    for rank in ranks:
        placements = rank["parallelism_info"]
        native._require(placements and all(item["tp_size"] == tp and item["pp_size"] == item["dp_size"] == 1
                                          for item in placements), "reload_tp_mismatch", str(placements))
        seen.extend({item["rank"] for item in placements})
    native._require(sorted(seen) == list(range(tp)), "reload_rank_coverage_mismatch", str(seen))
    reloaded, _ = _decoder_checksums(merge_inference_engine_ranks(body), config, tp, reference=False)
    mismatches = [issue.model_dump() for issue in compare_flat_dicts(final_decoder, reloaded, "final_publisher", "fresh_reload")]
    return {"verdict": "FAIL" if mismatches else "PASS", "mismatches": mismatches,
            "missing_decoder_keys": sorted(final_decoder.keys() - reloaded.keys()),
            "unexpected_decoder_keys": sorted(reloaded.keys() - final_decoder.keys()),
            "eligible_decoder_checksums": reloaded, "eligible_tensor_count": len(reloaded),
            "coverage": "Full native eligible parameter/buffer bytes, including gemma_weight; no agent skip list",
            "identity_proof": "Native engine-space content equality, not arbitrary direct-HF-space dtype equality"}


def _native_types():
    # CUDA-only native engine imports are deferred; CPU tests replace this API boundary,
    # never CUDA kernels or production dtype/loader policy.
    from sglang.srt.entrypoints.engine import Engine
    from sglang.srt.managers.io_struct import CheckWeightsReqInput
    from sglang.srt.model_loader.utils import get_model_architecture
    from sglang.srt.server_args import ServerArgs
    from sglang.srt.utils.weight_checker import _NON_PERSISTENT_BUFFER_PATTERNS
    from sglang.srt.utils.network import get_free_port
    from miles.utils.workers.argv_utils import _record_field_names

    return Engine, ServerArgs, CheckWeightsReqInput, get_model_architecture, _NON_PERSISTENT_BUFFER_PATTERNS, _record_field_names(ServerArgs), get_free_port


@contextmanager
def _fresh_engine(original, export, device, base_gpu_id):
    Engine, ServerArgs, request_type, architecture, excluded, fields, free_port = _native_types()
    config = {name: original[name] for name in fields if name in original}
    # Only fresh allocation/address identities change. Model and weight-affecting
    # settings remain the recorded native settings, including dtype and TP.
    config.update(model_path=str(export), tokenizer_path=str(export), device=device, base_gpu_id=base_gpu_id,
                  host="127.0.0.1", port=free_port(), node_rank=0, nnodes=1, dist_init_addr=None, nccl_port=None)
    for name in ("gated_launch_port", "engine_info_bootstrap_port", "disaggregation_bootstrap_port"):
        if name in config:
            config[name] = None
    engine = Engine.__new__(Engine)
    # Native shutdown supports partial startup through tokenizer_manager=None.
    engine.tokenizer_manager = None
    try:
        Engine.__init__(engine, server_args=ServerArgs(**config))
        selected, resolved_arch = architecture(engine.tokenizer_manager.model_config)
        native._require(selected.__module__.startswith("sglang.srt.models.") and resolved_arch == "Qwen3_5ForCausalLM",
                        "native_text_loader_unsupported", f"{selected.__module__}.{selected.__name__}/{resolved_arch}")
        yield engine, request_type, {"model_class": f"{selected.__module__}.{selected.__name__}",
                                    "resolved_architecture": resolved_arch, "position_buffer_exclusions": list(excluded),
                                    "model_dtype": str(engine.tokenizer_manager.model_config.dtype)}
    finally:
        engine.shutdown()


def _native_checksums(engine, request_type):
    success, message, ranks, checksum = engine.loop.run_until_complete(engine.tokenizer_manager.check_weights(
        request_type(action="checksum", allow_quant_error=False, selector="all"), None))
    return {"success": success, "message": message, "ranks": ranks, "per_engine_checksum": checksum}


def _monitoring_inputs(run_dir, population):
    frozen = native._population(population)
    raw_path = run_dir / "rollout_data" / f"eval_{_FINAL_ROLLOUT}.pt"
    stem = f"eval_{quote('monitor', safe='')}_{_FINAL_ROLLOUT}"
    paths = sorted((run_dir / "train_data").glob(f"{stem}_*.pt"))
    slices, issues = native._score_slices(paths, _FINAL_ROLLOUT, stem)
    samples, indices = {}, set()
    try:
        dump = torch.load(raw_path, map_location="cpu", weights_only=False)
        native._require(dump["rollout_id"] == _FINAL_ROLLOUT, "checkpoint_mismatch", str(raw_path))
        names = dump["metadata"]["eval_dataset_names"]
        native._require(len(names) == len(dump["samples"]), "dataset_row_count_mismatch", str(raw_path))
        for name, sample in zip(names, dump["samples"], strict=True):
            if name != "monitor":
                continue
            uid = sample["metadata"]["source"]["uid"]
            native._require(uid in frozen, "unexpected_monitoring_identity", uid)
            native._require(uid not in samples and sample["index"] not in indices, "duplicate_monitoring_sample", uid)
            samples[uid] = sample
            indices.add(sample["index"])
        native._require(not (set(slices) - indices), "unexpected_score_sample", str(set(slices) - indices))
    except Exception as error:
        issues.append({"path": str(raw_path), **native._issue(error)})
    rows, inputs = [], {}
    for uid, frozen_row in frozen.items():
        row = {"source_uid": uid, "stratum": frozen_row["stratum"], "sample_index": None,
               "expected_valid_tokens": None, "zero_target": None, "issues": [], "comparisons": {}}
        rows.append(row)
        try:
            native._require(uid in samples, "monitoring_sample_missing", uid)
            sample = samples[uid]
            mask = native._mask(sample)
            row.update(sample_index=sample["index"], expected_valid_tokens=int(mask.sum()), zero_target=not bool(mask.any()))
            tokens = native._source_check(sample, frozen_row, population)
            version = native._decode_version(sample, frozen_row["prompt_token_count"])
            train, meta = native._assemble_scores(slices.get(sample["index"], []), sample, mask)
            native._require(str(meta["weight_version"]) == version, "trainer_decode_version_mismatch",
                            f"Trainer {meta['weight_version']} versus sampled {version}")
            native._probability_check(sample, meta, "decode")
            row.update(consumed_weight_version=version, input_token_sha256=token_hash(tokens.tolist()),
                       prompt_sha256=frozen_row["prompt_sha256"], prompt_token_count=frozen_row["prompt_token_count"],
                       completion_sha256=sample["metadata"]["completion"]["token_sha256"],
                       response_length=sample["response_length"], original_loss_mask=mask.tolist(),
                       trainer_score_metadata=meta)
            inputs[uid] = (sample, tokens, mask, train)
        except Exception as error:
            _unavailable(row, error)
    checkpoint = {"rollout_id": _FINAL_ROLLOUT,
                  "consumed_weight_versions": sorted({row["consumed_weight_version"] for row in rows if "consumed_weight_version" in row})}
    publication = native._publication_checks(run_dir, [checkpoint])
    return rows, inputs, issues, publication, {"samples": str(raw_path), "scores": [str(path) for path in paths]}


def _forward(engine, tokens, response_length, fresh_version):
    prefix = len(tokens) - response_length
    native._require(prefix > 0 and response_length > 0, "empty_forward_input", "Need a recorded prefix and completion")
    sample = SimpleNamespace(tokens=tokens.tolist(), response_length=response_length, multimodal_inputs=None)
    args = SimpleNamespace(lora_rank=0, lora_adapter_path=None)
    payload = _build_prefill_scoring_payload(args, sample, {"top_p": 1, "top_k": -1})
    native._require(engine.flush_cache(), "fresh_cache_flush_failed", "Native cache flush was not confirmed")
    output = engine.generate(**payload)
    meta = output["meta_info"]
    native._require(meta["prompt_tokens"] == len(tokens), "reload_input_truncated", str(meta["prompt_tokens"]))
    native._require(str(meta["weight_version"]) == fresh_version, "reload_scoring_version_mismatch", str(meta["weight_version"]))
    spans = meta["prefill_weight_versions"]
    native._require(bool(spans) and all(str(span["version"]) == fresh_version for span in spans),
                    "reload_prefill_version_mismatch", str(spans))
    return meta, {"logprob_start_len": payload["logprob_start_len"], "input_truncated": False,
                    "fresh_engine_weight_version": fresh_version, "prefill_weight_versions": spans,
                    "source": "Native SGLang generate input_token_logprobs; max_new_tokens=0; full vocabulary normalizer"}


def _generate(engine, inputs, fresh_version):
    uid, (sample, tokens, _, _) = min(inputs.items(), key=lambda item: len(item[1][1]) - item[1][0]["response_length"])
    prefix = tokens[: len(tokens) - sample["response_length"]].tolist()
    output = engine.generate(input_ids=prefix, sampling_params={"temperature": 0, "max_new_tokens": 1})
    meta, generated = output["meta_info"], output["output_ids"]
    native._require(meta["prompt_tokens"] == len(prefix) and len(generated) == 1,
                    "native_generation_boundary_mismatch", "Need the complete recorded prefix and one generated token")
    native._require(str(meta["weight_version"]) == fresh_version, "reload_generation_version_mismatch", str(meta["weight_version"]))
    return {"verdict": "PASS", "source_uid": uid, "prompt_sha256": token_hash(prefix),
            "prompt_token_count": len(prefix), "max_new_tokens": 1, "temperature": 0,
            "output_token_ids": generated, "output_text": output["text"], "fresh_engine_weight_version": fresh_version,
            "acceptance": "Actual text generation only; no equality requirement against temperature-1 sampled completions"}


def verify(*, export, source, run_dir, population_report, launch_receipt, runtime_config, device, base_gpu_id):
    """Return authoritative reload evidence; every failure leaves reload_verified false."""
    export, source, run_dir, population_report = (Path(path).resolve() for path in (export, source, run_dir, population_report))
    launch_receipt, runtime_config = Path(launch_receipt).resolve(), Path(runtime_config).resolve()
    report = {"schema_version": 2, "task_id": "QWEN-P3-HF-RELOAD-IMPLEMENT", "verdict": "INCOMPLETE", "reload_verified": False,
              "export": str(export), "source": str(source), "run_dir": str(run_dir), "population_report": str(population_report),
              "rollout_id": _FINAL_ROLLOUT, "threshold": _THRESHOLD, "issues": [], "samples": [],
              "verification_scope": "Final text-HF reload validation, distinct from native SGLang D8; no training control",
              "probability_definition": "Native SGLang input-token prefill logprobs on original sampled IDs; train_logprob - reload_prefill_logprob; original pre-TIS masks",
              "launch_receipt": str(launch_receipt), "runtime_config": str(runtime_config)}
    try:
        launch, tp, image = _launch(launch_receipt, runtime_config, source, run_dir, population_report)
        config, tensors, report["package"] = _package(export, source, run_dir)
        report["package"].update(saved_dtypes=dict(Counter(tensor.dtype for tensor in tensors.values())),
                                fp32_a_log_names=sorted(name for name in tensors if name.endswith(".linear_attn.A_log")))
        population = json.loads(population_report.read_text())
        rows, inputs, issues, publication, artifacts = _monitoring_inputs(run_dir, population)
        report.update(samples=rows, weight_publication=publication, raw_artifacts=artifacts)
        report["issues"].extend(issues)
        report["probabilities"] = native._comparison_summary(rows, {}, _COMPARISON, _THRESHOLD, issues)
        final, original, version = _final_origin(run_dir, publication, launch, tp, source)
        decoder, excluded = _decoder_checksums(final.engine_snapshots[0].tensor_checksums, config, tp, reference=True)
        report["final_origin"] = {"checksum_event": final.model_dump(mode="json"), "tp_size": tp,
                                  "excluded_vision_mtp_keys": excluded, "eligible_decoder_tensor_count": len(decoder)}
        with _fresh_engine(original, export, device, base_gpu_id) as (engine, request_type, resolved):
            info, model_info = engine.get_server_info(), engine.get_model_info()
            actual = _server_config(info)
            native._require(info["version"] == version, "native_runtime_version_mismatch", f"{info['version']} versus {version}")
            native._require(Path(actual["model_path"]).resolve() == export and Path(model_info["model_path"]).resolve() == export
                            and actual["tp_size"] == tp and actual["device"] == device,
                            "reload_startup_mismatch", "Native engine resolved a different model, TP or device")
            # Startup records must confirm every retained weight-affecting setting.
            native._require(all(name in actual and actual[name] == value for name, value in original.items()
                                if name not in _ALLOCATION_FIELDS),
                            "reload_native_config_mismatch", "Native settings changed from the publisher engine")
            native._require(model_info["weight_version"] is not None, "fresh_engine_version_missing", "Need an actual fresh-engine receipt")
            fresh_version = str(model_info["weight_version"])
            report["runtime"] = {"backend": "sglang", "python": platform.python_version(), "torch": torch.__version__,
                                 "native_server_info": info, "native_model_info": model_info, "tp_size": tp, **resolved,
                                 "image": image, "image_verification": "Parent-owned worker/container evidence; no platform query by this validator"}
            report["checksums"] = _checksum_comparison(_native_checksums(engine, request_type), decoder, config, tp)
            records = {}
            for row in rows:
                uid = row["source_uid"]
                if uid not in inputs:
                    continue
                sample, tokens, mask, train = inputs[uid]
                try:
                    meta, row["forward"] = _forward(engine, tokens, sample["response_length"], fresh_version)
                    tail = meta.get("input_token_logprobs", [])[-sample["response_length"]:]
                    row["raw_score_counts"] = {
                        "expected_positions": sample["response_length"], "returned_positions": len(tail),
                        "finite_positions": sum(item[0] is not None and math.isfinite(item[0]) for item in tail),
                        "nonfinite_positions": sum(item[0] is not None and not math.isfinite(item[0]) for item in tail),
                        "missing_positions": sample["response_length"] - len(tail) + sum(item[0] is None for item in tail),
                    }
                    row["raw_prefill_tail"] = [[native._json_number(item[0]) if item[0] is not None else None, item[1]] for item in tail]
                    scoring_sample = SimpleNamespace(tokens=tokens.tolist(), response_length=sample["response_length"])
                    scores = native._vector(_extract_response_logprobs(scoring_sample, meta), "sglang_input_token_logprobs")
                    row["trainer_logprobs"] = [native._json_number(value) for value in train]
                    row["reload_prefill_logprobs"] = [native._json_number(value) for value in scores]
                    row["comparisons"][_COMPARISON], measured = native._token_metrics(train, scores, sample=sample, mask=mask, threshold=_THRESHOLD)
                    records[uid] = {_COMPARISON: measured}
                except Exception as error:
                    _unavailable(row, error)
            report["probabilities"] = native._comparison_summary(rows, records, _COMPARISON, _THRESHOLD, issues)
            try:
                native._require(bool(inputs), "generation_prefix_missing", "No verified recorded prefix is available")
                report["generation"] = _generate(engine, inputs, fresh_version)
            except Exception as error:
                report["generation"] = {"verdict": "INCOMPLETE", "issues": [native._issue(error)]}
            report["post_inference_checksums"] = _checksum_comparison(_native_checksums(engine, request_type), decoder, config, tp)
        report["cleanup"] = {"verdict": "PASS", "scope": "Only this standalone validator's fresh native Engine child tree"}
        report["verdict"] = native._verdict([publication["verdict"], report["checksums"]["verdict"], report["post_inference_checksums"]["verdict"],
                                             report["probabilities"]["verdict"], report["generation"]["verdict"]])
        report["reload_verified"] = report["verdict"] == "PASS"
    except Exception as error:
        report["issues"].append(native._issue(error))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ("export", "source", "run-dir", "population-report", "launch-receipt", "runtime-config", "report"):
        parser.add_argument(f"--{option}", type=Path, required=True)
    parser.add_argument("--device", required=True, help="Explicit native device; parent validates the pinned GPU runtime")
    parser.add_argument("--base-gpu-id", type=int, required=True, help="First local visible GPU for this fresh Engine")
    args = parser.parse_args()
    output = args.report.resolve()
    # A misplaced output must not overwrite checkpoint assets or native evidence.
    for path in (args.export, args.source, args.run_dir, args.population_report, args.launch_receipt, args.runtime_config):
        path = path.resolve()
        if output == path or output.is_relative_to(path):
            parser.error("--report must be outside the export, source, native run and population report")
    report = verify(export=args.export, source=args.source, run_dir=args.run_dir,
                    population_report=args.population_report, launch_receipt=args.launch_receipt,
                    runtime_config=args.runtime_config, device=args.device, base_gpu_id=args.base_gpu_id)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print("QWEN35_HF_RELOAD", report["verdict"], str(output), flush=True)
    raise SystemExit(0 if report["reload_verified"] else 1)


if __name__ == "__main__":
    main()
