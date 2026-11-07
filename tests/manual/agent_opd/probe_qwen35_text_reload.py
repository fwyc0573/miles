"""CUDA-only baseline native loader qualification; never accepts a final artifact.

Run in a dedicated pinned-worker interpreter from the repository root:
    python -B -m tests.manual.agent_opd.probe_qwen35_text_reload \
        --source SOURCE --run-dir QUALIFIED_BASELINE_RUN --output NEW_PERSONAL_CLOUD_DIR \
        --report NEW_REPORT_OUTSIDE_SOURCE_RUN_AND_OUTPUT.json
Only the new copy is converted; original assets and baseline evidence stay read-only.
"""

import argparse
import json
import os
import platform
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace


def _origin(reload, run_dir, source):
    native = reload.native
    events = native.EventReader(run_dir / "events", strict=True, event_types=(
        native.WeightUpdateResultEvent, native.TrainGroupStepEndEvent,
        native.InferenceEngineWeightChecksumEvent, native.InferenceEngineChecksumCollectionFailedEvent,
        reload.EngineEnvReportEvent,
    )).read()
    receipts = native._publication_receipts(events)
    baseline = receipts["baseline"]
    event, environments = receipts["checksums"][baseline.debug_weight_update_id], []
    native._require(event.rollout_id == -1 and event.weight_version == 0,
                    "baseline_initial_version_mismatch", "This probe requires the genuine fresh version-zero publication")
    for snapshot in event.engine_snapshots:
        records = [item for item in events if isinstance(item, reload.EngineEnvReportEvent)
                   and (item.cell_id, item.workers_hash) == (snapshot.cell_id, snapshot.workers_hash)
                   and item.timestamp <= event.timestamp]
        native._require(bool(records), "baseline_engine_environment_missing", snapshot.cell_id)
        environments.append(max(records, key=lambda item: item.timestamp))
    original = reload._server_config(environments[0].server_info)
    native._require(reload._cross_cell_configs_match(environments),
                    "baseline_engine_config_disagreement", "Baseline cells have different native ServerArgs")
    native._require(Path(original["model_path"]).resolve() == Path(original["tokenizer_path"]).resolve() == source and original["tp_size"] > 0
                    and original["pp_size"] == original["dp_size"] == original["nnodes"] == 1
                    and original["device"] == "cuda" and not original["quantization"] and not original["enable_lora"],
                    "baseline_source_or_topology_mismatch", "Need the original unquantized CUDA TP-only source")
    reload._recorded_server_args(environments[0].server_info)
    return event, original, environments


def _input(reload, run_dir):
    native = reload.native
    raw = run_dir / "rollout_data" / "eval_0.pt"
    dump = reload.torch.load(raw, map_location="cpu", weights_only=False)
    native._require(dump["rollout_id"] == 0, "baseline_checkpoint_mismatch", str(raw))
    samples = [sample for name, sample in zip(dump["metadata"]["eval_dataset_names"], dump["samples"], strict=True)
               if name == "monitor"]
    native._require(bool(samples), "baseline_monitor_missing", str(raw))
    sample = min(samples, key=lambda item: (len(item["tokens"]), item["index"]))
    tokens = native._vector(sample["tokens"], "tokens", dtype=reload.torch.int64)
    prefix = len(tokens) - sample["response_length"]
    source = sample["metadata"]["source"]
    native._require(prefix == source["prompt_token_count"] > 0 and sample["response_length"] > 0
                    and sample["status"] in ("completed", "truncated") and not sample.get("remove_sample", False)
                    and reload.token_hash(tokens[:prefix].tolist()) == source["prompt_sha256"]
                    and reload.token_hash(tokens[prefix:].tolist()) == sample["metadata"]["completion"]["token_sha256"],
                    "baseline_token_identity_mismatch", source["uid"])
    paths = sorted((run_dir / "train_data").glob("eval_monitor_0_*.pt"))
    slices, issues = native._score_slices(paths, 0, "eval_monitor_0")
    native._require(not issues, "baseline_score_evidence_incomplete", str(issues))
    mask = native._mask(sample)
    train, meta = native._assemble_scores(slices.get(sample["index"], []), sample, mask)
    native._require(str(meta["weight_version"]) == native._decode_version(sample, prefix) == "0",
                    "baseline_version_mismatch", "Baseline trainer and generation must consume version0")
    native._probability_check(sample, meta, "decode")
    decode = native._vector(sample["rollout_log_probs"], "baseline decode scores")
    qualification, _ = native._token_metrics(train, decode, sample=sample, mask=mask, threshold=reload._THRESHOLD)
    native._require(qualification["verdict"] == "PASS", "baseline_reference_unqualified",
                    f"Selected baseline reference failed the existing {reload._THRESHOLD} rule: {qualification}")
    return sample, tokens, mask, train, {"samples": str(raw), "scores": [str(path) for path in paths], "trainer_metadata": meta,
                                       "selected_reference_qualification": {"threshold": reload._THRESHOLD, **qualification},
                                       "qualification_scope": "Selected recorded sample: native trainer versus original decode; not whole-run D8 or final acceptance"}


def _copy(reload, source, output):
    shards = set(json.loads((source / reload.qwen_export._INDEX).read_text())["weight_map"].values())
    if any(Path(shard).name != shard for shard in shards):
        raise ValueError("Source shard names must be local filenames")
    assets = {"config.json", reload.qwen_export._INDEX, "tokenizer.json", "tokenizer_config.json"}
    assets.update(name for name in ("chat_template.jinja", "generation_config.json", "special_tokens_map.json",
                                  "added_tokens.json", "vocab.json", "merges.txt") if (source / name).is_file())
    output.mkdir(parents=True, exist_ok=False)
    for name in sorted(assets | shards):
        shutil.copyfile(source / name, output / name)
    return {"copied_files": sorted(assets | shards), "package": reload.qwen_export.export_text_checkpoint(source, output)}


def _checksums(reload, engine, request, baseline, config, tp):
    body = reload._native_checksums(engine, request)
    placements = [item for rank in body["ranks"] for item in rank["parallelism_info"]]
    reload.native._require(len(body["ranks"]) == tp and sorted({item["rank"] for item in placements}) == list(range(tp))
                           and all(item["tp_size"] == tp and item["pp_size"] == item["dp_size"] == 1 for item in placements),
                           "reload_tp_mismatch", str(placements))
    decoder, _ = reload._decoder_checksums(reload.merge_inference_engine_ranks(body), config, tp, reference=False)
    mismatches = [issue.model_dump() for issue in reload.compare_flat_dicts(baseline, decoder, "BASELINE", "fresh_text_reload")]
    return {"verdict": "FAIL" if mismatches else "PASS", "native_api": body, "mismatches": mismatches,
            "eligible_decoder_checksums": decoder, "coverage": "Complete native eligible decoder parameters/buffers, including gemma_weight"}


def _run(args, report):
    # Worker-only imports are deferred so controller-host --help has no CUDA dependency.
    import sglang
    from tests.manual.agent_opd import qwen_reload as reload

    event, original, environments = _origin(reload, args.run_dir, args.source)
    config, tp = reload.qwen_export._text_config(args.source), original["tp_size"]
    baseline, excluded = reload._decoder_checksums(event.engine_snapshots[0].tensor_checksums, config, tp, reference=True)
    reload.native._require(all(reload._decoder_checksums(item.tensor_checksums, config, tp, reference=True)[0] == baseline
                               for item in event.engine_snapshots), "baseline_cell_checksums_disagree", "Baseline decoder content differs")
    report["baseline_origin"] = {"reference": "BASELINE", "checksum_event": event.model_dump(mode="json"),
                                 "environments": [item.model_dump(mode="json") for item in environments], "excluded_vision_mtp_keys": excluded}
    sample, tokens, mask, train, report["raw_artifacts"] = _input(reload, args.run_dir)
    report["copy"] = _copy(reload, args.source, args.output)
    devices = [{"index": index, "name": reload.torch.cuda.get_device_name(index),
                "properties": str(reload.torch.cuda.get_device_properties(index))} for index in range(tp)]
    report["devices"] = devices
    reload.native._require(all("H800" in item["name"] for item in devices), "h800_device_mismatch", str(devices))
    report["cleanup"] = {"verdict": "INCOMPLETE", "issues": []}
    with reload._fresh_engine(original, args.output, "cuda", 0, reference_info=environments[0].server_info, cleanup=report["cleanup"]) as (engine, request, resolved):
        info, model_info = engine.get_server_info(), engine.get_model_info()
        actual = reload._server_config(info)
        report["runtime"] = {"python": platform.python_version(), "executable": sys.executable, "torch": reload.torch.__version__,
                             "sglang": sglang.__version__, "sglang_module": sglang.__file__, "tp_size": tp,
                             "server_info": info, "model_info": model_info, "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"), **resolved}
        report["startup_settings"] = reload._retained_config_comparison(environments[0].server_info, info)
        reload.native._require(info["version"] == environments[0].server_info["version"]
                               and Path(actual["model_path"]).resolve() == Path(model_info["model_path"]).resolve() == args.output
                               and report["startup_settings"]["verdict"] == "PASS",
                               "native_runtime_config_mismatch", f"Runtime version or retained settings changed: {report['startup_settings']['mismatches']}")
        reload.native._require(model_info["weight_version"] is not None, "fresh_engine_version_missing", str(model_info))
        version = str(model_info["weight_version"])
        report["before_checksums"] = _checksums(reload, engine, request, baseline, config, tp)
        meta, report["forward"] = reload._forward(engine, tokens, sample["response_length"], version)
        report["forward"]["native_api"] = {key: meta[key] for key in ("prompt_tokens", "weight_version", "prefill_weight_versions")}
        report["forward"]["native_api"]["input_token_logprobs"] = [
            [reload.native._json_number(item[0]) if item[0] is not None else None, *item[1:]]
            for item in meta.get("input_token_logprobs", [])]
        report["generation"] = reload._generate(engine, {sample["metadata"]["source"]["uid"]: (sample, tokens, mask, train)}, version)
        report["after_checksums"] = _checksums(reload, engine, request, baseline, config, tp)
        scores = reload.native._vector(reload._extract_response_logprobs(
            SimpleNamespace(tokens=tokens.tolist(), response_length=sample["response_length"]), meta), "native_prefill")
        report["scores"] = {"sample_index": sample["index"], "source_uid": sample["metadata"]["source"]["uid"],
                            "selection": "Shortest actual monitoring prefix plus completion; no truncation",
                            "original_loss_mask": mask.tolist(), "trainer": [reload.native._json_number(value) for value in train],
                            "reloaded_prefill": [reload.native._json_number(value) for value in scores]}
        report["probabilities"], report["token_metrics"] = reload.native._token_metrics(
            train, scores, sample=sample, mask=mask, threshold=reload._THRESHOLD)
        report["threshold"] = reload._THRESHOLD
    report["verdict"] = reload.native._verdict([report[key]["verdict"] for key in (
        "before_checksums", "after_checksums", "probabilities", "generation", "cleanup")])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "run-dir", "output", "report"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    args = parser.parse_args()
    args.source, args.run_dir, args.output, args.report = (path.resolve() for path in (args.source, args.run_dir, args.output, args.report))
    for destination in (args.output, args.report):
        if any(destination == path or destination.is_relative_to(path) or path.is_relative_to(destination)
               for path in (args.source, args.run_dir)):
            parser.error("--output and --report must be disjoint from the source and native run")
    if not args.output.is_relative_to(Path("/mnt/codesign-exp/ycfeng")) or args.output.exists() or args.report.exists():
        parser.error("--output must be a NEW personal-cloud directory; --report must be a new file")
    if args.report == args.output or args.report.is_relative_to(args.output) or args.output.is_relative_to(args.report):
        parser.error("--report must be outside --output")
    report = {"task_id": "QWEN-P3-TEXT-LOADER-PROBE", "scope": "baseline native loader qualification",
              "final_artifact_accepted": False, "verdict": "INCOMPLETE", "source": str(args.source),
              "run_dir": str(args.run_dir), "copied_artifact": str(args.output), "issues": []}
    try:
        _run(args, report)
    except Exception as error:
        report["issues"].append({"type": type(error).__name__, "detail": str(error)})
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open("x") as stream:
        json.dump(report, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print("QWEN35_BASELINE_TEXT_LOADER", report["verdict"], str(args.report), flush=True)
    raise SystemExit(0 if report["verdict"] == "PASS" else 1)


if __name__ == "__main__":
    main()
