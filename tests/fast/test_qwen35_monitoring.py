"""Pure CPU fault/CP checks of task-scoped native monitoring acceptance.

All probabilities are deterministic fixtures, not measured model results.
"""

import copy
import json
import math

import pytest
import torch

from examples.agentic_opd.glm_turns import token_hash
from tests.ci.ci_register import register_cpu_ci
from tests.manual.agent_opd import inspect_qwen35 as inspector
from tests.manual.agent_opd.prepare_qwen35 import LENGTH_STRATA, MONITOR_PER_STRATUM

from miles.utils.audit_utils.event_logger.logger import EventLogger
from miles.utils.audit_utils.event_logger.models import (
    InferenceEngineWeightChecksumEvent,
    TrainGroupStepEndEvent,
    WeightUpdateResultEvent,
)
from miles.utils.audit_utils.process_identity import SimpleProcessIdentity, TrainerControllerProcessIdentity

# The complete file measured 34.57 seconds in the task's CPU environment.
register_cpu_ci(est_time=45, suite="stage-b-cpu", labels=["megatron"])


@pytest.fixture(scope="module")
def native_fixture():
    samples, rows = [], []
    kwargs = {"preserve_thinking": True, "enable_thinking": True}
    for name, lower, _ in LENGTH_STRATA:
        prefix = lower + 1
        # Shared immutable lists keep native pickle fixtures small despite real
        # accepted length boundaries. The production inspector never mutates them.
        tokens = [17] * prefix + [31, 32]
        digest = token_hash(tokens[:prefix])
        for position in range(MONITOR_PER_STRATUM):
            index = len(samples)
            uid = f"{name}-{position}"
            row = {"uid": uid, "group_id": f"task-{index}", "prompt_token_count": prefix,
                   "prompt_sha256": digest, "stratum": name, "split": "monitor", "exclusions": []}
            rows.append(row)
            sample = {"index": index, "tokens": tokens, "response_length": 2, "loss_mask": [1, 1],
                      "status": "completed", "rollout_log_probs": [-2.0, -2.0],
                      "metadata": {"source": {key: row[key] for key in ("uid", "group_id", "prompt_token_count", "prompt_sha256")},
                                   "completion": {"token_sha256": token_hash(tokens[prefix:])}, "chat_template_kwargs": kwargs,
                                   "probability_definition": {"decode": "full_vocabulary_log_softmax", "prefill": "full_vocabulary_log_softmax",
                                                              "sampling_distribution": "student_decode",
                                                              "sampling_params": {"temperature": 1, "top_p": 1, "top_k": -1}}},
                      "train_metadata": {"source_uid": uid, "prompt_sha256": digest,
                                         "completion_sha256": token_hash(tokens[prefix:]), "sample_index": index}}
            samples.append(sample)
    population = {"status": "passed", "length_strata": [
        {"name": name, "lower_exclusive": lower, "upper_inclusive": upper} for name, lower, upper in LENGTH_STRATA],
        "monitoring_per_stratum": MONITOR_PER_STRATUM, "population": rows,
        "split": {"monitoring_uids": [row["uid"] for row in rows], "checks": {"train_monitor_group_overlap": []}},
        "chat_template": {"kwargs": kwargs}}
    return population, samples


def _versions(sample, version):
    prefix = len(sample["tokens"]) - sample["response_length"]
    sample["weight_versions"] = [{"output_start": prefix, "prompt_tokens": prefix,
                                  "spans": [{"version": version, "abs_start": prefix, "abs_end": len(sample["tokens"])}],
                                  "prefill_spans": [{"version": version, "abs_start": 0, "abs_end": prefix}]}]
    sample["metadata"]["student_rescoring"] = {
        "status": "measured", "token_ids_match": True, "response_logprobs": list(sample["rollout_log_probs"]),
        "scored_weight_versions": [version], "sampled_weight_versions": [version], "versions_match": True,
        "cache_namespace": "independent", "training_logprobs_replaced": False,
        "probability_definition": "full_vocabulary_log_softmax"}


def _batch(samples, rollout_id, *, cp_rank=0, cp_size=1, qkv_format="thd", max_seq_len=None, weight_version=0):
    meta = {"rollout_id": rollout_id, "weight_version": weight_version, "cell_index": 0,
            "rank": cp_rank, "dp_rank": 0, "dp_size": 1, "tp_rank": 0, "tp_size": 2,
            "cp_rank": cp_rank, "cp_size": cp_size, "pp_rank": 0, "pp_size": 1,
            "qkv_format": qkv_format, "response_layout": "response" if cp_size == 1 else "zigzag",
            "allgather_cp": False, "rollout_temperature": 1, "log_probs_backend": "torch",
            "true_on_policy_mode": False, "use_rollout_sampling_mask": False}
    batch = {"metadata": meta, "sample_indices": [sample["index"] for sample in samples],
             "tokens": [sample["tokens"] for sample in samples],
             "loss_masks": [sample["loss_mask"] if sample["loss_mask"] is not None else [1] * sample["response_length"] for sample in samples],
             "total_lengths": [len(sample["tokens"]) for sample in samples],
             "response_lengths": [sample["response_length"] for sample in samples], "log_probs": []}
    if qkv_format == "bshd":
        batch["max_seq_lens"] = [max_seq_len] * len(samples)
    for sample in samples:
        positions = inspector._response_positions(meta, len(sample["tokens"]), sample["response_length"], max_seq_len)
        scores = torch.tensor(sample["rollout_log_probs"], dtype=torch.float64) + 0.01
        batch["log_probs"].append(scores[positions])
    return batch


def _write_checkpoint(root, samples, rollout_id, mutate=None, *, weight_version=0):
    samples = copy.deepcopy(samples)
    for sample in samples:
        _versions(sample, str(weight_version))
    dump = {"rollout_id": rollout_id, "samples": samples, "metadata": {"eval_dataset_names": ["monitor"] * len(samples)}}
    batch = _batch(samples, rollout_id, weight_version=weight_version)
    if mutate:
        mutate(dump, batch)
    torch.save(dump, root / "rollout_data" / f"eval_{rollout_id}.pt")
    torch.save({"rollout_id": f"eval_monitor_{rollout_id}", "rank": 0, "cp_rank": 0, "cp_size": 1,
                "qkv_format": "thd", "rollout_data": batch}, root / "train_data" / f"eval_monitor_{rollout_id}_0.pt")


def _write_native_events(root, *, skipped=(2, 19, 99), unchanged_engine_weights=False, positions=(None, *range(100))):
    """Use the actual typed native writer, fields and process filenames.

    Producers: train/group.py _log_step_end_event/update_weights and
    placement_group.py _log_inference_engine_weight_checksums. Model companion
    versions advance only at model.py's successful optimizer.step boundary.
    NORMAL is deliberately emitted for both successful and skipped updates.
    """
    controller_source = TrainerControllerProcessIdentity(trainer_id="actor")
    main_source = SimpleProcessIdentity(component="main")
    controller = EventLogger(log_dir=root / "events", source=controller_source, file_name=f"{controller_source.to_name()}.jsonl")
    main = EventLogger(log_dir=root / "events", source=main_source, file_name=f"{main_source.to_name()}.jsonl")
    version, versions = 17, {None: 17}
    for position in positions:
        if position is not None:
            controller.log(TrainGroupStepEndEvent,
                           {"rollout_id": position, "attempt": 0, "role": "actor", "cell_outcomes": {0: ["normal"]},
                            "cell_incarnations": {"actor-cell-0": "trainer-incarnation"}}, print_log=False)
            version += int(position not in skipped)
            versions[position] = version
        update_id = f"{0 if position is None else position + 1:032x}"
        controller.log(WeightUpdateResultEvent,
                       {"debug_weight_update_id": update_id, "debug_trainer_load_state_timestamp": 1234567.25,
                        "rollout_id": position, "candidate_version": version, "published_version": version,
                        "snapshot_cell_id_to_hashes": {"rollout-cell-0": "engine-incarnation"},
                        "updated_cell_ids": ["rollout-cell-0"], "failed_cell_ids": []}, print_log=False)
        main.log(InferenceEngineWeightChecksumEvent,
                 {"rollout_id": -1 if position is None else position, "trainer_model_id": None,
                  "weight_version": version, "debug_trainer_load_state_timestamp": 1234567.25, "debug_weight_update_id": update_id,
                  "engine_snapshots": [{"cell_id": "rollout-cell-0", "workers_hash": "engine-incarnation",
                                        "tensor_checksums": {"rank0/model.layers.0.weight": f"model-{17 if unchanged_engine_weights else version}"}}]},
                 print_log=False)
    return versions


@pytest.fixture(scope="module")
def native_run(tmp_path_factory, native_fixture):
    root = tmp_path_factory.mktemp("qwen-monitor-native-fixture")
    (root / "rollout_data").mkdir()
    (root / "train_data").mkdir()
    population, samples = native_fixture
    path = root / "population.json"
    path.write_text(json.dumps(population))
    versions = _write_native_events(root)
    for checkpoint in (0, 19, 39, 59, 79, 99):
        _write_checkpoint(root, samples, checkpoint, weight_version=versions[None if checkpoint == 0 else checkpoint])
    return root, path


def _fault_run(tmp_path, native_run, native_fixture, mutate, checkpoint=0, *, full=False):
    root, population = native_run
    for directory in ("rollout_data", "train_data"):
        (tmp_path / directory).mkdir()
        for path in (root / directory).glob("*.pt"):
            if path.stem not in (f"eval_{checkpoint}", f"eval_monitor_{checkpoint}_0"):
                (tmp_path / directory / path.name).symlink_to(path)
    version = torch.load(root / "train_data" / f"eval_monitor_{checkpoint}_0.pt", weights_only=False)["rollout_data"]["metadata"]["weight_version"]
    _write_checkpoint(tmp_path, native_fixture[1], checkpoint, mutate, weight_version=version)
    if full:
        (tmp_path / "events").symlink_to(root / "events", target_is_directory=True)
        return inspector.inspect(tmp_path, population)
    frozen = inspector._population(native_fixture[0])
    result, _ = inspector._checkpoint(tmp_path, native_fixture[0], frozen, checkpoint, "monitor", 0.03)
    return {"verdict": result["verdict"], "checkpoints": [result]}


def _codes(report, comparison="decode", checkpoint=0, stratum="overall"):
    row = next(row for row in report["checkpoints"] if row["rollout_id"] == checkpoint)
    return {issue["code"] for issue in row[comparison][stratum]["issues"]}


def test_complete_native_artifact_contract_passes_without_inventing_versions(native_run):
    report = inspector.inspect(*native_run)
    assert report["verdict"] == "PASS"
    assert report["checkpoint_verdict_counts"] == {"PASS": 6}
    assert len(report["monitoring_uids"]) == 24
    publication = report["weight_publication"]
    assert publication["verdict"] == "PASS"
    assert publication["baseline_weight_version"] == 17
    assert publication["final_published_weight_version"] == 114
    assert publication["successful_optimizer_updates"] == 97
    assert publication["skipped_optimizer_updates"] == 3
    assert publication["publications"][-1]["rollout_id"] == 99
    assert publication["publications"][-1]["optimizer_counter_delta"] == 0
    for checkpoint in report["checkpoints"]:
        version = publication["baseline_weight_version"] if checkpoint["rollout_id"] == 0 else next(
            row["published_version"] for row in publication["publications"] if row["rollout_id"] == checkpoint["rollout_id"])
        assert checkpoint["consumed_weight_versions"] == [str(version)]
        assert len(checkpoint["samples"]) == 24
        for name in ("decode", "prefill"):
            assert checkpoint[name]["overall"]["abs_mean"] == pytest.approx(0.01)
            assert checkpoint[name]["overall"]["expected_valid_tokens"] == 48
            for stratum, _, _ in LENGTH_STRATA:
                assert checkpoint[name][stratum]["compared_finite_tokens"] == 16
    # The report is strict JSON, including finite/missing diagnostics.
    json.dumps(report, allow_nan=False)
    assert "No convergence" in report["learning_conclusion"]


def test_all_baseline_monitoring_cannot_qualify_updated_weights(tmp_path, native_fixture):
    population, samples = native_fixture
    (tmp_path / "rollout_data").mkdir()
    (tmp_path / "train_data").mkdir()
    path = tmp_path / "population.json"
    path.write_text(json.dumps(population))

    versions = _write_native_events(tmp_path, skipped=range(100))
    for position in (0, 19, 39, 59, 79, 99):
        _write_checkpoint(tmp_path, samples, position, weight_version=versions[None])
    report = inspector.inspect(tmp_path, path)
    assert all(checkpoint["verdict"] == "PASS" for checkpoint in report["checkpoints"])
    assert report["verdict"] == "INCOMPLETE"
    assert report["weight_publication"]["issues"][0]["code"] == "successful_updated_version_missing"
    assert report["weight_publication"]["successful_optimizer_updates"] == 0


def test_final_monitor_stale_against_actual_publisher_is_incomplete(tmp_path, native_run, native_fixture):
    earlier = torch.load(native_run[0] / "train_data" / "eval_monitor_79_0.pt", weights_only=False)["rollout_data"]["metadata"]["weight_version"]

    def stale_final(dump, batch):
        batch["metadata"]["weight_version"] = earlier
        for sample in dump["samples"]:
            _versions(sample, str(earlier))

    report = _fault_run(tmp_path, native_run, native_fixture, stale_final, checkpoint=99, full=True)
    assert all(checkpoint["verdict"] == "PASS" for checkpoint in report["checkpoints"])
    assert report["verdict"] == "INCOMPLETE"
    publication = report["weight_publication"]
    assert publication["final_published_weight_version"] != earlier
    assert publication["issues"][0]["code"] == "final_monitor_publication_version_mismatch"


def test_counter_advance_without_updated_model_tensor_observation_is_incomplete(tmp_path):
    versions = _write_native_events(tmp_path, unchanged_engine_weights=True)
    checkpoints = [{"rollout_id": position, "consumed_weight_versions": [str(versions[None if position == 0 else position])]} for position in (0, 19, 39, 59, 79, 99)]
    publication = inspector._publication_checks(tmp_path, checkpoints)
    assert publication["successful_optimizer_updates"] == 97
    assert publication["verdict"] == "INCOMPLETE"
    assert publication["issues"][0]["code"] == "updated_engine_weights_unchanged"


def test_baseline_probe_keeps_checkpoint_zero_result_but_full_d8_is_incomplete(tmp_path, native_fixture):
    population, samples = native_fixture
    (tmp_path / "rollout_data").mkdir()
    (tmp_path / "train_data").mkdir()
    path = tmp_path / "population.json"
    path.write_text(json.dumps(population))
    versions = _write_native_events(tmp_path, positions=(None,))
    _write_checkpoint(tmp_path, samples, 0, weight_version=versions[None])
    report = inspector.inspect(tmp_path, path)
    assert report["checkpoints"][0]["verdict"] == "PASS"
    assert report["weight_publication"]["baseline_weight_version"] == 17
    assert report["weight_publication"]["verdict"] == report["verdict"] == "INCOMPLETE"


def test_missing_native_events_never_use_monitor_versions_as_update_proof(tmp_path):
    checkpoints = [{"rollout_id": position, "consumed_weight_versions": [str(17 + position)]} for position in (0, 19, 39, 59, 79, 99)]
    publication = inspector._publication_checks(tmp_path, checkpoints)
    assert publication["verdict"] == "INCOMPLETE"
    assert publication["successful_optimizer_updates"] is None
    assert publication["issues"][0]["code"] == "native_update_receipts_missing"


@pytest.mark.parametrize("corrupt", [False, True])
def test_final_native_checksum_missing_or_corrupt_is_incomplete(tmp_path, corrupt):
    versions = _write_native_events(tmp_path)
    path = tmp_path / "events" / "main.jsonl"
    lines = path.read_text().splitlines(keepends=True)
    if corrupt:
        event = json.loads(lines[-1])
        del event["weight_version"]
        lines[-1] = json.dumps(event) + "\n"
    else:
        lines = lines[:-1]
    path.write_text("".join(lines))
    checkpoints = [{"rollout_id": position, "consumed_weight_versions": [str(versions[None if position == 0 else position])]} for position in (0, 19, 39, 59, 79, 99)]
    publication = inspector._publication_checks(tmp_path, checkpoints)
    assert publication["verdict"] == "INCOMPLETE"
    assert publication["issues"][0]["code"] == ("native_event_artifacts_corrupt" if corrupt else "native_publication_checksum_incomplete")


def test_pre_tis_outlier_is_not_removed_from_acceptance(native_fixture):
    sample = copy.deepcopy(native_fixture[1][0])
    train = torch.tensor([-2.0 + math.log(3), -2.0], dtype=torch.float64)
    before = sample["loss_mask"].copy()
    metrics, tokens = inspector._token_metrics(train, torch.tensor([-2.0, -2.0]), sample=sample,
                                                mask=torch.tensor([True, True]), threshold=0.03)
    assert metrics["verdict"] == "FAIL"
    assert metrics["expected_valid_tokens"] == metrics["compared_finite_tokens"] == 2
    assert [token["tis_retained"] for token in tokens] == [False, True]
    assert metrics["abs_mean"] == pytest.approx(math.log(3) / 2)
    worst = metrics["worst_tokens"][0]
    assert (worst["source_uid"], worst["response_position"], worst["absolute_position"]) == ("short-0", 0, 1)
    assert sample["loss_mask"] == before
    ratio, delta = 3, math.log(3)
    assert metrics["k3_r_d_minus_r_plus_1"]["mean"] == pytest.approx((ratio * delta - ratio + 1) / 2)
    assert metrics["k3_r_minus_1_minus_d"]["mean"] == pytest.approx((ratio - 1 - delta) / 2)


@pytest.mark.parametrize("fault,code,comparison", [
    ("trainer_version", "trainer_decode_version_mismatch", "decode"),
    ("decode_version", "trainer_decode_version_mismatch", "decode"),
    ("generation_prefill_version", "mixed_consumed_versions", "decode"),
    ("prefill_version", "prefill_version_mismatch", "prefill"),
    ("trainer_tokens", "trainer_token_mismatch", "decode"),
    ("trainer_mask", "trainer_mask_mismatch", "decode"),
    ("missing_tokens", "trainer_input_tokens_missing", "decode"),
    ("missing_mask", "trainer_input_mask_missing", "decode"),
    ("completion_hash", "completion_token_mismatch", "decode"),
    ("source_prefix", "source_identity_mismatch", "decode"),
    ("probability", "probability_definition_missing", "decode"),
    ("prefill_probability", "prefill_probability_definition_missing", "prefill"),
])
def test_identity_version_mask_and_probability_faults_are_incomplete(tmp_path, native_run, native_fixture, fault, code, comparison):
    def mutate(dump, batch):
        sample = dump["samples"][0]
        if fault == "trainer_version":
            batch["metadata"]["weight_version"] = "different-actual-weights"
        elif fault == "decode_version":
            for span in sample["weight_versions"][0]["spans"] + sample["weight_versions"][0]["prefill_spans"]:
                span["version"] = "different-actual-weights"
        elif fault == "generation_prefill_version":
            sample["weight_versions"][0]["prefill_spans"][0]["version"] = "stale-kv"
        elif fault == "prefill_version":
            sample["metadata"]["student_rescoring"]["scored_weight_versions"] = ["stale-prefill"]
        elif fault == "trainer_tokens":
            batch["tokens"][0] = [*batch["tokens"][0][:-1], 99]
        elif fault == "trainer_mask":
            batch["loss_masks"][0] = [0, 1]
        elif fault == "missing_tokens":
            del batch["tokens"]
        elif fault == "missing_mask":
            del batch["loss_masks"]
        elif fault == "completion_hash":
            sample["metadata"]["completion"]["token_sha256"] = "different-completion"
        elif fault == "source_prefix":
            sample["metadata"]["source"]["prompt_sha256"] = "different-prefix"
        elif fault == "probability":
            del sample["metadata"]["probability_definition"]
        else:
            del sample["metadata"]["student_rescoring"]["probability_definition"]
    report = _fault_run(tmp_path, native_run, native_fixture, mutate)
    assert report["verdict"] == "INCOMPLETE"
    assert code in _codes(report, comparison)
    # One malformed sample cannot prevent inspection of healthy samples.
    if fault not in ("trainer_version", "missing_tokens", "missing_mask"):
        assert report["checkpoints"][0]["samples"][-1]["comparisons"]["decode"]["verdict"] == "PASS"


@pytest.mark.parametrize("missing", ["sample", "stratum", "final_checkpoint", "score_row", "corrupt_score", "duplicate_rank", "dp_rank"])
def test_missing_corrupt_duplicate_population_or_slices_are_incomplete(tmp_path, native_run, native_fixture, missing):
    def mutate(dump, batch):
        if missing in ("sample", "stratum"):
            keep = 23 if missing == "sample" else 16
            dump["samples"] = dump["samples"][:keep]
            dump["metadata"]["eval_dataset_names"] = dump["metadata"]["eval_dataset_names"][:keep]
            for name in ("sample_indices", "tokens", "loss_masks", "total_lengths", "response_lengths", "log_probs"):
                batch[name] = batch[name][:keep]
        elif missing == "score_row":
            for name in ("sample_indices", "tokens", "loss_masks", "total_lengths", "response_lengths", "log_probs"):
                batch[name] = batch[name][1:]
        elif missing == "corrupt_score":
            batch["log_probs"] = []
        elif missing == "dp_rank":
            batch["metadata"]["dp_size"] = 2
    if missing == "final_checkpoint":
        root, population = native_run
        for directory in ("rollout_data", "train_data"):
            (tmp_path / directory).mkdir()
            for path in (root / directory).glob("*.pt"):
                if "99" not in path.name:
                    (tmp_path / directory / path.name).symlink_to(path)
        report = inspector.inspect(tmp_path, population)
        assert report["checkpoints"][-1]["verdict"] == "INCOMPLETE"
    elif missing == "duplicate_rank":
        _fault_run(tmp_path, native_run, native_fixture, mutate)
        path = tmp_path / "train_data" / "eval_monitor_0_0.pt"
        (path.parent / "eval_monitor_0_9.pt").symlink_to(path)
        frozen = inspector._population(native_fixture[0])
        checkpoint, _ = inspector._checkpoint(tmp_path, native_fixture[0], frozen, 0, "monitor", 0.03)
        report = {"verdict": checkpoint["verdict"], "checkpoints": [checkpoint]}
        assert "duplicate_rank_slice" in _codes(report)
    else:
        report = _fault_run(tmp_path, native_run, native_fixture, mutate)
    assert report["verdict"] == "INCOMPLETE"
    if missing == "stratum":
        long = report["checkpoints"][0]["decode"]["long"]
        assert long["unknown_denominator_samples"] == 8
        assert long["expected_valid_tokens"] is None and long["abs_mean"] is None
    if missing == "dp_rank":
        assert "missing_rank_slice" in _codes(report)
    json.dumps(report, allow_nan=False)


def test_valid_nonfinite_is_incomplete_but_masked_nonfinite_is_excluded(native_fixture):
    sample = copy.deepcopy(native_fixture[1][0])
    train = torch.tensor([-2.0, float("nan")], dtype=torch.float64)
    infer = torch.tensor([-2.0, -2.0], dtype=torch.float64)
    metrics, _ = inspector._token_metrics(train, infer, sample=sample, mask=torch.tensor([True, True]), threshold=0.03)
    assert metrics["verdict"] == "INCOMPLETE"
    assert metrics["nonfinite_valid_tokens"] == metrics["missing_or_nonfinite_tokens"] == 1
    metrics, _ = inspector._token_metrics(train, infer, sample=sample, mask=torch.tensor([True, False]), threshold=0.03)
    assert metrics["verdict"] == "PASS" and metrics["expected_valid_tokens"] == 1
    assert metrics["nonfinite_masked_positions"] == 1


def test_teacher_student_divergence_is_separate_diagnostic_not_d8_failure(tmp_path, native_run, native_fixture):
    def mutate(dump, batch):
        for sample in dump["samples"]:
            sample["teacher_log_probs"] = [-1.8, -1.8]
            sample["metadata"]["probability_definition"]["teacher"] = "full_vocabulary_log_softmax"
            sample["metadata"]["teacher_scoring"] = {"token_ids_match": True, "scored_tokens": 2}
    report = _fault_run(tmp_path, native_run, native_fixture, mutate)
    checkpoint = report["checkpoints"][0]
    assert checkpoint["verdict"] == report["verdict"] == "PASS"
    teacher = checkpoint["teacher_student_sampled_divergence"]
    assert teacher["verdict"] == "DIAGNOSTIC"
    assert teacher["overall"]["abs_mean"] == pytest.approx(0.2)
    assert teacher["overall"]["delta_definition"] == "teacher_logprob - student_decode_logprob"
    assert "teacher_logprob" in teacher["overall"]["worst_tokens"][0]
    assert "tis_retained" not in teacher["overall"]["worst_tokens"][0]


def test_token_weighted_not_sample_weighted_and_each_stratum_is_gated(tmp_path, native_run, native_fixture):
    def mutate(dump, batch):
        sample = dump["samples"][16]
        prefix = sample["metadata"]["source"]["prompt_token_count"]
        sample["tokens"] = sample["tokens"][:prefix] + [31] * 100
        sample["response_length"], sample["loss_mask"], sample["rollout_log_probs"] = 100, [1] * 100, [-2.0] * 100
        digest = token_hash([31] * 100)
        sample["metadata"]["completion"]["token_sha256"] = digest
        sample["train_metadata"]["completion_sha256"] = digest
        version = batch["metadata"]["weight_version"]
        _versions(sample, str(version))
        batch.update(_batch(dump["samples"], 0, weight_version=version))
        batch["log_probs"] = [torch.tensor(sample["rollout_log_probs"], dtype=torch.float64) for sample in dump["samples"]]
        batch["log_probs"][16] += 0.08
    report = _fault_run(tmp_path, native_run, native_fixture, mutate, full=True)
    checkpoint = report["checkpoints"][0]
    assert checkpoint["decode"]["short"]["verdict"] == "PASS"
    assert checkpoint["decode"]["long"]["abs_mean"] == pytest.approx(8 / 114)
    assert checkpoint["decode"]["overall"]["abs_mean"] == pytest.approx(8 / 146)
    assert sum(row["comparisons"]["decode"]["abs_mean"] for row in checkpoint["samples"]) / 24 < 0.03
    assert checkpoint["decode"]["verdict"] == "FAIL" and report["verdict"] == "FAIL"
    # A mostly healthy cross-checkpoint average cannot override a single failure.
    assert report["aggregate"]["decode"]["overall"]["abs_mean"] < 0.03
    assert report["aggregate"]["verdict"] == "FAIL"


def test_inclusive_native_tis_boundaries_and_unclamped_k3(native_fixture):
    sample = native_fixture[1][0]
    train = torch.tensor([math.log(0.5), math.log(2)], dtype=torch.float64)
    metrics, records = inspector._token_metrics(train, torch.zeros(2), sample=sample, mask=torch.tensor([True, True]), threshold=0.03)
    assert [record["tis_retained"] for record in records] == [True, True]
    assert metrics["verdict"] == "FAIL"
    huge, records = inspector._token_metrics(torch.tensor([1000.0, 0.0]), torch.zeros(2), sample=sample,
                                             mask=torch.tensor([True, True]), threshold=0.03)
    assert huge["verdict"] == "INCOMPLETE"
    assert huge["nonfinite_unclamped_k3"] == 1
    assert records[0]["ratio"] is None
    json.dumps(huge, allow_nan=False)


@pytest.mark.parametrize("cp_size,qkv_format,maximum", [(2, "thd", None), (4, "thd", None), (2, "bshd", 32)])
def test_native_zigzag_cp_reassembles_token_positions_not_rank_order(cp_size, qkv_format, maximum):
    sample = {"index": 4, "tokens": list(range(16)), "response_length": 15, "loss_mask": [1] * 15,
              "rollout_log_probs": [float(position) - 20 for position in range(15)]}
    slices = []
    for rank in range(cp_size):
        batch = _batch([sample], 19, cp_rank=rank, cp_size=cp_size, qkv_format=qkv_format, max_seq_len=maximum)
        slices.append((batch, 0, f"native-rank-{rank}"))
    output, metadata = inspector._assemble_scores(slices, sample, torch.ones(15, dtype=torch.bool))
    assert metadata["cp_size"] == cp_size
    assert output.tolist() == pytest.approx([value + 0.01 for value in sample["rollout_log_probs"]])
    with pytest.raises(inspector.EvidenceError, match="Every CP rank") as error:
        inspector._assemble_scores(slices[:-1], sample, torch.ones(15, dtype=torch.bool))
    assert error.value.code == "missing_cp_slice"
    flattened = torch.cat([batch["log_probs"][0] for batch, _, _ in slices])
    if qkv_format == "thd":
        assert not torch.equal(flattened, output)


def test_unknown_cp_allgather_is_explicitly_incomplete(native_fixture):
    sample = native_fixture[1][0]
    batch = _batch([sample], 0, cp_size=2)
    batch["metadata"]["allgather_cp"] = True
    with pytest.raises(inspector.EvidenceError) as error:
        inspector._assemble_scores([(batch, 0, "native")], sample, torch.ones(2, dtype=torch.bool))
    assert error.value.code == "unsupported_response_layout"


def test_zero_target_denominator_is_named_not_synthetic_zero(native_fixture):
    sample = native_fixture[1][0]
    metrics, _ = inspector._token_metrics(torch.zeros(2), torch.zeros(2), sample=sample,
                                         mask=torch.zeros(2, dtype=torch.bool), threshold=0.03)
    assert metrics["verdict"] == "INCOMPLETE"
    assert metrics["abs_mean"] is None and metrics["zero_target_samples"] == 1
    assert metrics["expected_valid_tokens"] == 0
    assert metrics["issues"][0]["code"] == "zero_target_denominator"


def test_finite_native_values_with_overflowing_difference_are_incomplete(native_fixture):
    metrics, records = inspector._token_metrics(torch.tensor([1e308, 0], dtype=torch.float64),
                                               torch.tensor([-1e308, 0], dtype=torch.float64), sample=native_fixture[1][0],
                                               mask=torch.ones(2, dtype=torch.bool), threshold=0.03)
    assert metrics["verdict"] == "INCOMPLETE"
    assert metrics["nonfinite_logprob_differences"] == 1
    assert metrics["compared_finite_tokens"] == len(records) == 1
    json.dumps(metrics, allow_nan=False)


def test_incomplete_frozen_population_cannot_be_used(tmp_path, native_run, native_fixture):
    population = copy.deepcopy(native_fixture[0])
    population["split"]["monitoring_uids"] = population["split"]["monitoring_uids"][:-1]
    path = tmp_path / "population.json"
    path.write_text(json.dumps(population))
    report = inspector.inspect(native_run[0], path)
    assert report["verdict"] == "INCOMPLETE"
    assert report["issues"][0]["code"] == "monitoring_identity_mismatch"


def test_schedule_and_threshold_cannot_be_relaxed(native_run):
    with pytest.raises(inspector.EvidenceError) as error:
        inspector.inspect(*native_run, threshold=0.1)
    assert error.value.code == "acceptance_threshold_changed"
    with pytest.raises(inspector.EvidenceError) as error:
        inspector.inspect(*native_run, checkpoints=(0,))
    assert error.value.code == "monitoring_schedule_changed"
