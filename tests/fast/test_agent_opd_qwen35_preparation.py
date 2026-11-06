"""Regress Qwen population selection without weights, cloud reads or GPUs."""

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest
from examples.agentic_opd.glm_turns import encode_glm_turn, token_hash
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import WhitespaceSplit
from transformers import PreTrainedTokenizerFast

from tests.manual.agent_opd import prepare_glm5_2 as glm
from tests.manual.agent_opd import prepare_qwen35 as qwen


@pytest.fixture
def tokenizer():
    backend = Tokenizer(WordLevel({"[UNK]": 0, "x": 1}, unk_token="[UNK]"))
    backend.pre_tokenizer = WhitespaceSplit()
    return PreTrainedTokenizerFast(tokenizer_object=backend, unk_token="[UNK]")


def _history():
    return [
        {"role": "user", "content": "first task"},
        {
            "role": "assistant",
            "content": "test it",
            "reasoning_content": "EARLY_REASONING",
            "tool_calls": [{"type": "function", "function": {"name": "test", "arguments": '{"path":"parser.py"}'}}],
        },
        {"role": "tool", "content": "test failed"},
        {"role": "user", "content": "next task"},
        {"role": "assistant", "content": "test again", "reasoning_content": "LATE_REASONING"},
        {"role": "tool", "content": "new failure"},
    ]


def _dataset_row():
    return {
        "prompt": "GLM prompt is never used by Qwen",
        "metadata": {
            "source": {
                "uid": "file-sha:1:6",
                "category": "neither",
                "group_id": "task-a",
                "prompt_token_count": 200000,
                "conversation_sha256": "conversation-sha",
                "file_sha256": "file-sha",
            },
            "history": _history(),
            "tools": [{"type": "function", "function": {"name": "test", "parameters": {"type": "object", "properties": {}}}}],
            "original_completion": {"message": {"role": "assistant", "content": "OLD_TARGET"}, "has_thinking": False},
        },
    }


@pytest.mark.parametrize("kwargs,early,thinking", [({}, True, True), ({"preserve_thinking": False}, False, True), ({"enable_thinking": False}, True, False)])
def test_actual_template_preserves_user_control_and_original_history(tokenizer, kwargs, early, thinking):
    _, template, settings = qwen._template_settings(None, kwargs)
    original = _dataset_row()
    untouched = copy.deepcopy(original)
    row, evidence = qwen._render_row(original, tokenizer, template, settings)
    assert ("EARLY_REASONING" in row["prompt"]) == early
    assert "LATE_REASONING" in row["prompt"]
    assert "OLD_TARGET" not in row["prompt"]
    assert row["metadata"]["thinking_enabled"] == thinking
    suffix = "<|im_start|>assistant\n<think>\n" if thinking else "<|im_start|>assistant\n<think>\n\n</think>\n\n"
    assert row["prompt"].endswith(suffix)
    ids = tokenizer.encode(row["prompt"], add_special_tokens=False)
    assert ids == tokenizer.apply_chat_template(
        qwen.normalize_tool_arguments(original["metadata"]["history"]),
        chat_template=template,
        tools=original["metadata"]["tools"],
        add_generation_prompt=True,
        return_dict=False,
        **settings,
    )
    assert evidence["prompt_token_count"] == len(ids)
    assert evidence["prompt_sha256"] == row["metadata"]["source"]["prompt_sha256"] == token_hash(ids)
    assert original == untouched
    assert row["metadata"]["original_completion"] == original["metadata"]["original_completion"]


def test_custom_template_path_and_kwargs_reach_renderer(tokenizer, tmp_path):
    path = tmp_path / "custom.jinja"
    path.write_text("{{ custom_label }} {{ messages[0]['content'] }} {{ preserve_thinking }} {{ enable_thinking }}")
    actual_path, template, settings = qwen._template_settings(path, {"custom_label": "chosen", "preserve_thinking": False})
    row, _ = qwen._render_row(_dataset_row(), tokenizer, template, settings)
    assert actual_path == path
    assert row["prompt"] == "chosen first task False True"


def _evidence(uid, group, length):
    return {
        "uid": uid,
        "group_id": group,
        "prompt_token_count": length,
        "prompt_sha256": uid,
        "stratum": qwen._stratum(length),
        "exclusions": [],
    }


def _population():
    # Two groups supply each entire bank; eight DISTINCT groups are not needed.
    rows = [
        _evidence(f"{name}-{i}", f"task-{name}-{i // 8}", upper)
        for name, _, upper in qwen.LENGTH_STRATA
        for i in range(16)
    ]
    rows.extend([_evidence("over", "task-short-0", 122881), _evidence("benchmark", "eval-task", 100)])
    return rows


def test_split_uses_exact_strata_and_excludes_entire_monitor_groups_globally():
    population = _population()
    training, monitoring, report = qwen._partition_population(population, {"eval-task"})
    assert len(monitoring) == 24
    assert report["monitoring_stratum_counts"] == {"short": 8, "medium": 8, "long": 8}
    assert all(count <= 2 for count in report["monitoring_stratum_group_counts"].values())
    monitor_groups = set(report["monitoring_groups"])
    for row in population:
        if row["group_id"] in monitor_groups:
            assert row["uid"] not in training
            if row["uid"] not in monitoring:
                assert "monitoring_task_group" in row["exclusions"]
    assert not any(report["checks"].values())
    assert population[-2]["exclusions"][0] == "qwen_prefix_over_budget"
    assert population[-1]["exclusions"] == ["inherited_evaluation_task_group"]
    second = qwen._partition_population(_population(), {"eval-task"})
    assert (training, monitoring, report) == second
    assert training == [row["uid"] for row in population if row["split"] == "train"]


@pytest.mark.parametrize("length,expected", [(0, None), (1, "short"), (32768, "short"), (32769, "medium"), (65536, "medium"), (65537, "long"), (122880, "long"), (122881, None)])
def test_length_boundaries_are_not_adjusted(length, expected):
    assert qwen._stratum(length) == expected


def test_shortfall_is_actual_qwen_coverage_and_does_not_mutate_lengths():
    population = [row for row in _population() if not row["uid"].startswith("medium-") or int(row["uid"].split("-")[1]) < 7]
    original_lengths = [row["prompt_token_count"] for row in population]
    with pytest.raises(ValueError, match="INCOMPLETE.*medium.*7"):
        qwen._partition_population(population, {"eval-task"})
    assert [row["prompt_token_count"] for row in population] == original_lengths


def test_monitoring_must_leave_a_training_group_and_can_share_groups_across_strata():
    rows = [_evidence(f"{name}-{i}", "monitor-task", upper) for name, _, upper in qwen.LENGTH_STRATA for i in range(8)]
    with pytest.raises(ValueError, match="no whole task group can remain"):
        qwen._select_monitoring(rows)
    rows.append(_evidence("training-only", "train-task", 20))
    training, monitoring, report = qwen._partition_population(rows, set())
    assert training == ["training-only"]
    assert len(monitoring) == 24
    assert report["monitoring_groups"] == ["monitor-task"]


class _GLMTokenizer:
    """Only the GLM provenance renderer is simulated; Qwen uses real tokenization."""

    def apply_chat_template(self, messages, *, add_generation_prompt, **kwargs):
        if add_generation_prompt:
            return " ".join(message.get("content", "") for message in messages) + " <|assistant|><think>"
        return " ".join(message.get("content", "") for message in messages[:-1]) + " <|assistant|>" + messages[-1]["content"]

    def encode(self, text, **kwargs):
        # Deliberately very different token lengths from the Qwen tokenizer.
        return list(text.encode())

    def decode(self, ids, **kwargs):
        return bytes(ids).decode()


def _manifest_fixture(tmp_path):
    glm_tokenizer = _GLMTokenizer()
    conversations, entries = [], []
    lengths = [100] * 10 + [32769] * 10 + [65537] * 10 + [122881]
    for index, length in enumerate(lengths):
        conversation = [{"role": "user", "content": "x " * (length - 2)}, {"role": "assistant", "content": " old target"}]
        conversations.append(json.dumps(conversation).encode())
        turn = encode_glm_turn(glm_tokenizer, conversation, None)
        entries.append({
            "file": 0,
            "parent_row": index,
            "source_item_index": index,
            "assistant_turn_index": 1,
            "group_id": f"task-{index}",
            "prompt_token_count": len(turn.prompt_ids),
            "prompt_sha256": token_hash(turn.prompt_ids),
            "completion_token_count": len(turn.completion_ids),
            "completion_sha256": token_hash(turn.completion_ids),
            "conversation_sha256": hashlib.sha256(conversations[-1]).hexdigest(),
        })
    source = tmp_path / "source.json"
    offset = 1
    for entry, raw in zip(entries, conversations, strict=True):
        entry.update(item_start=offset, item_end=offset + len(raw))
        offset += len(raw) + 1
    source.write_bytes(b"[" + b",".join(conversations) + b"]")
    file = {"path": str(source), "size": source.stat().st_size, "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
    manifest = {"files": [file], "categories": {"neither": {"train": entries}}}
    return manifest, glm_tokenizer, lengths


def test_full_population_counts_actual_qwen_ids_without_glm_length_prefilter(tokenizer, tmp_path):
    manifest, glm_tokenizer, lengths = _manifest_fixture(tmp_path)
    # Simple fixture template retains the complete history and generation marker.
    template = "{{ messages[0]['content'] }} assistant think"
    rows, population = qwen._prepare_population(manifest, glm_tokenizer, tokenizer, template, {"enable_thinking": True}, tmp_path)
    assert len(rows) == len(population) == len(lengths) == 31
    assert [row["prompt_token_count"] for row in population] == lengths
    assert all(row["glm_prompt_token_count"] > row["prompt_token_count"] for row in population)
    # Long Qwen-eligible prefixes have GLM provenance lengths beyond the limit.
    assert all(row["glm_prompt_token_count"] > qwen.PREFIX_TOKENS for row in population[20:30])
    training, monitoring, split = qwen._partition_population(population, set())
    assert split["exclusion_counts"]["qwen_prefix_over_budget"] == 1
    assert len(training) == 6 and len(monitoring) == 24
    for uid in training + monitoring:
        row = rows[uid]
        ids = tokenizer.encode(row["prompt"], add_special_tokens=False)
        assert len(ids) == row["metadata"]["source"]["prompt_token_count"]
        assert token_hash(ids) == row["metadata"]["source"]["prompt_sha256"]
        assert row["metadata"]["thinking_enabled"] is True


def test_original_glm_hash_and_scoped_source_bytes_are_still_verified(tokenizer, tmp_path):
    manifest, glm_tokenizer, _ = _manifest_fixture(tmp_path)
    file, entry = manifest["files"][0], manifest["categories"]["neither"]["train"][0]
    with pytest.raises(ValueError):
        glm._read_conversation(file, entry)
    conversation = glm._read_conversation(file, entry, source_root=tmp_path)
    entry["prompt_sha256"] = "changed"
    with pytest.raises(ValueError, match="GLM prompt differs"):
        glm._make_row(glm_tokenizer, conversation, file, entry, "neither")
    source = Path(file["path"])
    source.write_bytes(source.read_bytes().replace(b'"user"', b'"tool"', 1))
    with pytest.raises(ValueError, match="conversation bytes changed"):
        glm._read_conversation(file, entry, source_root=tmp_path)


def _reference(path, value):
    path.write_text(json.dumps(value))
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def _cli_fixture(tmp_path, tokenizer, monkeypatch):
    manifest, glm_tokenizer, _ = _manifest_fixture(tmp_path)
    entries = manifest["categories"]["neither"]["train"]
    membership = _reference(tmp_path / "membership.json", {"task_ids": ["held-out-benchmark"]})
    pool = {"files": manifest["files"], "train": entries, "probe": [entries[0]]}
    selection = {
        "membership": membership,
        "selected_conversations": [{key: row[key] for key in ("file", "source_item_index", "group_id")} for row in entries],
    }
    manifest.update(
        membership=membership,
        parents={"neither": {
            "pool": _reference(tmp_path / "pool.json", pool),
            "selection": _reference(tmp_path / "selection.json", selection),
        }},
        isolation="Pinned parent evaluation exclusions",
    )
    glm_path, qwen_path = tmp_path / "glm-tokenizer", tmp_path / "qwen-tokenizer"
    glm_path.mkdir()
    (glm_path / "tokenizer.json").write_text("pinned simulated GLM asset")
    manifest["tokenizer"] = {"assets": {"tokenizer.json": hashlib.sha256((glm_path / "tokenizer.json").read_bytes()).hexdigest()}}
    tokenizer.save_pretrained(qwen_path)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest))
    template = tmp_path / "fixture.jinja"
    template.write_text("{{ messages[0]['content'] }} assistant think")
    output = tmp_path / "prepared"
    argv = ["prepare_qwen35", "--manifest", str(manifest_path), "--glm-tokenizer", str(glm_path), "--qwen-tokenizer", str(qwen_path), "--source-root", str(tmp_path), "--chat-template-path", str(template), "--output-root", str(output)]
    monkeypatch.setattr(sys, "argv", argv)

    def load(path, *, local_files_only):
        assert local_files_only is True
        return glm_tokenizer if path == glm_path else tokenizer

    monkeypatch.setattr(qwen.AutoTokenizer, "from_pretrained", load)
    return manifest_path, output


def test_cli_freezes_reusable_split_and_generation_contract(tokenizer, tmp_path, monkeypatch):
    _, output = _cli_fixture(tmp_path, tokenizer, monkeypatch)
    qwen.main()
    report = json.loads((output / "population.json").read_text())
    assert report["status"] == "passed" and report["population_count"] == 31
    assert report["limits"] == {"context_tokens": 131072, "response_tokens": 8192, "prefix_tokens": 122880}
    assert report["chat_template"]["kwargs"] == {"preserve_thinking": True, "enable_thinking": True}
    assert report["split"]["exclusion_counts"]["inherited_evaluation_task_group"] == 1
    assert report["training_order"]["seed"] == 42
    assert not any(report["split"]["checks"].values())
    for split in ("train", "monitor"):
        path = output / f"{split}.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        identity_key = "monitoring_uids" if split == "monitor" else "training_uids"
        assert [row["metadata"]["source"]["uid"] for row in rows] == report["split"][identity_key]
        assert report["datasets"][split]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
        for row in rows:
            metadata = row["metadata"]
            ids = tokenizer.encode(row["prompt"], add_special_tokens=False)
            assert metadata["source"]["prompt_token_count"] == len(ids)
            assert metadata["source"]["prompt_sha256"] == token_hash(ids)
            assert metadata["thinking_enabled"] is True
            assert metadata["original_completion"]["message"]["content"] == " old target"
            assert all(key in metadata for key in ("history", "tools", "original_completion"))
    with pytest.raises(FileExistsError, match="new population directory"):
        qwen.main()


def test_cli_missing_coverage_writes_incomplete_population_without_partial_datasets(tokenizer, tmp_path, monkeypatch):
    manifest_path, output = _cli_fixture(tmp_path, tokenizer, monkeypatch)
    manifest = json.loads(manifest_path.read_text())
    manifest["categories"]["neither"]["train"] = [row for row in manifest["categories"]["neither"]["train"] if row["source_item_index"] < 20]
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="INCOMPLETE.*long.*0"):
        qwen.main()
    report = json.loads((output / "population.json").read_text())
    assert report["status"] == "incomplete"
    assert len(report["population"]) == 20
    assert not (output / "train.jsonl").exists() and not (output / "monitor.jsonl").exists()


def test_inherited_pins_and_parent_group_membership_cannot_change(tokenizer, tmp_path, monkeypatch):
    manifest_path, _ = _cli_fixture(tmp_path, tokenizer, monkeypatch)
    manifest = json.loads(manifest_path.read_text())
    references = glm._verify_manifest_references(manifest)
    assert qwen._verify_population_membership(manifest, references) == {"task-0"}
    manifest["categories"]["neither"]["train"][1]["group_id"] = "different-task"
    with pytest.raises(ValueError, match="source turn/group differs"):
        qwen._verify_population_membership(manifest, references)
    Path(manifest["membership"]["path"]).write_text("changed")
    with pytest.raises(ValueError, match="inherited source selection/exclusion evidence changed"):
        glm._verify_manifest_references(manifest)


def test_legacy_glm_cli_keeps_shortest_selection_and_original_output(tokenizer, tmp_path, monkeypatch):
    manifest_path, _ = _cli_fixture(tmp_path, tokenizer, monkeypatch)
    output, report = tmp_path / "legacy.jsonl", tmp_path / "legacy-report.json"
    read_conversation = glm._read_conversation
    monkeypatch.setattr(glm, "_read_conversation", lambda file, row: read_conversation(file, row, source_root=tmp_path))
    monkeypatch.setattr(sys, "argv", [
        "prepare_glm5_2", "--manifest", str(manifest_path), "--tokenizer", str(tmp_path / "glm-tokenizer"),
        "--output", str(output), "--report", str(report), "--turns-per-category", "1", "--max-prompt-tokens", "1000",
    ])
    glm.main()
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    assert len(rows) == 1
    assert rows[0]["metadata"]["source"]["source_item_index"] == 0
    assert rows[0]["prompt"].endswith("<|assistant|>")
    evidence = json.loads(report.read_text())
    assert evidence["status"] == "passed"
    assert evidence["turns_per_category"] == 1 and evidence["max_prompt_tokens"] == 1000
    assert evidence["turns"][0]["prefix_and_completion_match"] is True
