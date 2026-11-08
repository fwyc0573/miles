"""Compare the frozen SWE benchmark with ordered GLM-5.2 conversations.

Example (use a memory-limited systemd scope when available):
    timeout 180s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python \
        tests/manual/agent_opd/check_swe_benchmark_overlap.py \
        --benchmark /data/ycfeng/tmp/qwen35-swe-full-r256/swe_bench2512_all_sorted.json \
        --manifest /path/to/domain_manifests_1009/swe/domain_manifest.json \
        --benchmark-copy-receipt /data/ycfeng/tmp/qwen35-swe-full-r256/benchmark-COPY_COMPLETE.json \
        --sources /data/ycfeng/tmp/qwen35-swe-full-r256/swe-sources-20261023 \
        --output task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/benchmark-training-overlap.json

This is a source-text audit, not a tokenizer eligibility or contamination certificate.
"""

import argparse
import hashlib
import json
import platform
import re
import shlex
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path


IDENTITY_KEYS = {
    "instance_id": "instance_id",
    "task_id": "instance_id",
    "repo": "repo",
    "repository": "repo",
    "repo_name": "repo",
    "base_commit": "base_commit",
    "problem_statement": "problem_statement",
}
PR_DESCRIPTION = re.compile(r"<pr_description>(.*?)</pr_description>", re.DOTALL)
INSTANCE_ID = re.compile(r"\b[A-Za-z0-9_.-]+__[A-Za-z0-9_.-]+-\d+\b")
REPO_URL = re.compile(r"https?://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)")
FIELD_LINE = re.compile(
    r"^\s*(instance_id|task_id|repo|repository|repo_name|base_commit)\s*[:=]\s*"
    r"[\"']?([^\s\"'<>]+)",
    re.MULTILINE,
)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def text_sha256(text):
    """Collapse Unicode whitespace, preserving case, punctuation, and word order."""
    return hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()


def file_identity(path):
    return {
        "path": str(Path(path).resolve()),
        "sha256": sha256(path),
        "bytes": Path(path).stat().st_size,
    }


def identity_values(value, path):
    """Read explicit identity keys recursively without interpreting request IDs."""
    if isinstance(value, dict):
        for key, item in value.items():
            location = f"{path}.{key}"
            if key in IDENTITY_KEYS and isinstance(item, str) and item.strip():
                yield IDENTITY_KEYS[key], item.strip(), location
            yield from identity_values(item, location)
    elif isinstance(value, list):
        for item in value:
            yield from identity_values(item, path + "[]")


def conversation_identity(conversation, metadata_counts, field_counts, role_counts):
    values = defaultdict(set)
    locations = defaultdict(set)
    context = []
    initial = True
    tools = 0
    for message in conversation:
        role = message["role"]
        role_counts[role] += 1
        metadata = message.get("meta", {})
        metadata_counts.update(metadata.keys())
        tools += int("tools" in message)
        for name, value, location in identity_values(message, "message"):
            values[name].add(value)
            locations[name].add(location)
            field_counts[location] += 1
        if role == "assistant":
            initial = False
        if initial and role in ("user", "system"):
            text = message["content"]
            if not isinstance(text, str):
                raise ValueError("Initial task context must be text")
            context.append(text)
            for key, value in FIELD_LINE.findall(text):
                name = IDENTITY_KEYS[key]
                values[name].add(value)
                locations[name].add("initial_context.label." + key)
                field_counts["initial_context.label." + key] += 1
    statements = [
        body.strip()
        for text in context
        for body in PR_DESCRIPTION.findall(text)
        if body.strip()
    ]
    task_descriptions = [
        text.split("Task Description:", 1)[1].strip()
        for text in context
        if "Task Description:" in text
    ]
    values["problem_statement"].update(statements + task_descriptions)
    text = "\n".join(context)
    return {
        "instance_ids": sorted(values["instance_id"]),
        "repos": sorted(values["repo"]),
        "base_commits": sorted(values["base_commit"]),
        "problem_statement_sha256": sorted(
            {text_sha256(value) for value in values["problem_statement"]}
        ),
        "identity_locations": {name: sorted(paths) for name, paths in locations.items()},
        "pr_description_count": len(statements),
        "task_description_count": len(task_descriptions),
        "initial_context_instance_id_literals": sorted(set(INSTANCE_ID.findall(text))),
        "task_context_github_repo_mentions": sorted(
            {repo.removesuffix(".git") for repo in REPO_URL.findall(text)}
        ),
        "messages_with_tools": tools,
    }


def scan_sources(directory):
    receipt_path = directory / "COPY_COMPLETE.json"
    receipt = json.loads(receipt_path.read_text())
    expected = {Path(row["path"]).name: row for row in receipt["files"]}
    files = [
        directory / f"glm5.2_distill_{series}_include_unresolved_part{part:04d}.json"
        for series, parts in ((0, 5), (1, 6))
        for part in range(parts)
    ]
    conversations = []
    inputs = []
    metadata_counts, field_counts, role_counts = Counter(), Counter(), Counter()
    turn_offset = 0
    for path in files:
        identity = file_identity(path)
        if identity["sha256"] != expected[path.name]["sha256"]:
            raise ValueError(f"Source differs from verified copy receipt: {path}")
        identity.update(
            original_path=expected[path.name]["path"], copy_receipt_sha256_match=True
        )
        rows = json.loads(path.read_text())
        file_turns = 0
        for index, conversation in enumerate(rows):
            turns = sum(message["role"] == "assistant" for message in conversation)
            row = conversation_identity(
                conversation, metadata_counts, field_counts, role_counts
            )
            row.update(
                file_name=path.name,
                conversation_index=index,
                assistant_turn_count=turns,
                first_assistant_stream_index=turn_offset,
                assistant_stream_end_exclusive=turn_offset + turns,
            )
            conversations.append(row)
            turn_offset += turns
            file_turns += turns
        if (
            len(rows) != expected[path.name]["conversations"]
            or file_turns != expected[path.name]["assistant_turns"]
        ):
            raise ValueError(f"Source counts differ from copy receipt: {path}")
        identity.update(conversations=len(rows), assistant_turns=file_turns)
        inputs.append(identity)
        del rows
    return inputs, conversations, {
        "conversation_count": len(conversations),
        "assistant_turn_count": turn_offset,
        "message_role_counts": dict(role_counts),
        "message_meta_top_level_key_occurrences": dict(metadata_counts),
        "explicit_identity_field_occurrences": dict(field_counts),
        "conversations_with_identity": {
            key: sum(bool(row[key]) for row in conversations)
            for key in (
                "instance_ids", "repos", "base_commits", "problem_statement_sha256",
                "initial_context_instance_id_literals", "task_context_github_repo_mentions",
            )
        },
        "pr_description_count": sum(row["pr_description_count"] for row in conversations),
        "task_description_count": sum(row["task_description_count"] for row in conversations),
        "messages_with_tools": sum(row["messages_with_tools"] for row in conversations),
        "copy_receipt": file_identity(receipt_path),
    }


def benchmark_tasks(library, manifest):
    rows = json.loads(library.read_text())
    ids = json.loads(manifest.read_text())["benchmark"]["task_ids"]
    by_id = {row["instance_id"]: row for row in rows}
    if (
        len(ids) != 500 or len(set(ids)) != 500
        or len(rows) != 500 or set(ids) != set(by_id)
    ):
        raise ValueError("Manifest and library must contain the same 500 distinct task IDs")
    tasks = []
    for task_id in ids[:100]:
        row = by_id[task_id]
        task = {
            key: row[key]
            for key in ("instance_id", "repo", "base_commit", "problem_statement")
        }
        task["problem_statement_sha256"] = text_sha256(task["problem_statement"])
        task["library_row_index"] = next(
            index for index, item in enumerate(rows) if item["instance_id"] == task_id
        )
        tasks.append(task)
    return tasks, {
        "selected_task_count": len(tasks),
        "selected_repo_counts": dict(Counter(task["repo"] for task in tasks)),
        "manifest_order_equals_library_row_order": ids == [row["instance_id"] for row in rows],
        "library_first_100_intersection_with_selected_tasks": len(
            set(ids[:100]) & {row["instance_id"] for row in rows[:100]}
        ),
        "selected_order_sha256": hashlib.sha256(
            json.dumps(ids[:100], separators=(",", ":")).encode()
        ).hexdigest(),
    }


def comparison(rows, tasks):
    methods = {
        name: [] for name in (
            "exact_instance_id", "repo_and_base_commit", "normalized_problem_statement_sha256"
        )
    }
    for row in rows:
        for task in tasks:
            conditions = {
                "exact_instance_id": task["instance_id"] in row["instance_ids"],
                "repo_and_base_commit": (
                    task["repo"] in row["repos"]
                    and task["base_commit"] in row["base_commits"]
                ),
                "normalized_problem_statement_sha256": (
                    task["problem_statement_sha256"] in row["problem_statement_sha256"]
                ),
            }
            for method, matches in conditions.items():
                if matches:
                    methods[method].append({
                        "instance_id": task["instance_id"],
                        "file_name": row["file_name"],
                        "conversation_index": row["conversation_index"],
                    })
    available = {
        "exact_instance_id": sum(bool(row["instance_ids"]) for row in rows),
        "repo_and_base_commit": sum(bool(row["repos"] and row["base_commits"]) for row in rows),
        "normalized_problem_statement_sha256": sum(
            bool(row["problem_statement_sha256"]) for row in rows
        ),
    }
    result = {}
    for method, matches in methods.items():
        result[method] = {
            "status": (
                "COMPLETE" if available[method] == len(rows)
                else "IDENTITY_COVERAGE_INCOMPLETE"
            ),
            "conversations_with_comparable_identity": available[method],
            "matching_benchmark_task_count": len({match["instance_id"] for match in matches}),
            "matching_conversation_count": len({
                (match["file_name"], match["conversation_index"]) for match in matches
            }),
            "matching_pair_count": len(matches),
            "matches": matches,
        }
    benchmark_repos = {task["repo"] for task in tasks}
    for name, key in (
        ("explicit_repository_overlap", "repos"),
        ("task_context_repository_mentions_overlap", "task_context_github_repo_mentions"),
    ):
        source_repos = {repo for row in rows for repo in row[key]}
        shared = benchmark_repos & source_repos
        result[name] = {
            "repo_names": sorted(shared),
            "repo_count": len(shared),
            "source_repo_count": len(source_repos),
            "conversations_with_shared_repo": sum(bool(shared & set(row[key])) for row in rows),
            "interpretation": (
                "Explicit labelled repository values, without URL normalization"
                if key == "repos"
                else "GitHub URL mentions in initial task context; not verified task repository identity"
            ),
        }
    return result


def reference_evidence(task_directory):
    return {
        "prior_exact_text_comparison": {
            "report": file_identity(task_directory / "test_report_2026-10-02_source_inventory.md"),
            "recorded_result": "0/4992 SWE conversations matched 500 fixed benchmark instructions; historical normalization and benchmark archive differ from this audit's native-library comparison",
        },
        "prior_fragment_comparison": {
            "report": file_identity(task_directory / "test_report_2026-10-03_task_benchmark_overlap.md"),
            "recorded_result": "5/1603 question-based SWE groups shared 1-4 normalized 13-word fragments with the 500-task index; no frozen train/monitoring input was affected",
            "benchmark_ids": ["sphinx-doc__sphinx-8265", "scikit-learn__scikit-learn-13142", "pydata__xarray-4629"],
        },
        "prior_input_rule": {
            "report": file_identity(task_directory / "test_report_2026-10-03_swe_tb_freeze.md"),
            "scope": "The old task used question-based grouping, rendered-prompt deduplication, and a train/monitoring split. This source audit applies none of those transforms.",
        },
    }


def main():
    started_at = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", required=True, type=Path)
    parser.add_argument("--benchmark-copy-receipt", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--sources", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    benchmark_input = file_identity(args.benchmark)
    copy_receipt = json.loads(args.benchmark_copy_receipt.read_text())
    if benchmark_input["sha256"] != copy_receipt["sha256"]:
        raise ValueError("Benchmark library differs from the original-source copy receipt")
    benchmark_input.update(
        original_path=copy_receipt["source"],
        personal_cloud_copy=copy_receipt["destination"],
        copy_receipt=file_identity(args.benchmark_copy_receipt),
        copy_receipt_sha256_match=True,
    )
    tasks, benchmark_counts = benchmark_tasks(args.benchmark, args.manifest)
    inputs, conversations, training_counts = scan_sources(args.sources)
    scopes = {}
    for name, budget in (
        ("all_conversations", None),
        ("first_51200_assistant_turns", 51200),
        ("first_1024_assistant_turns", 1024),
    ):
        rows = conversations if budget is None else [
            row for row in conversations
            if row["assistant_turn_count"] and row["first_assistant_stream_index"] < budget
        ]
        scopes[name] = {
            "conversation_count": len(rows),
            "assistant_turn_budget": budget,
            "assistant_turns_in_included_whole_conversations": sum(
                row["assistant_turn_count"] for row in rows
            ),
            "last_conversation": {
                key: rows[-1][key] for key in (
                    "file_name", "conversation_index", "first_assistant_stream_index",
                    "assistant_stream_end_exclusive",
                )
            },
            "overlap": comparison(rows, tasks),
        }
    report = {
        "task_id": "T01-overlap",
        "status": "FACTUAL_SOURCE_COMPARISON_COMPLETE_WITH_IDENTITY_LIMITS",
        "inputs": {
            "benchmark_library": benchmark_input,
            "ordered_manifest": file_identity(args.manifest),
            "training_sources_in_consumption_order": inputs,
        },
        "method": {
            "benchmark_selection": "benchmark.task_ids[:100] from the existing 500-task domain manifest; map by instance_id into the library, not library[:100]",
            "selection_source": "/data/ycfeng/steptron/.worktrees/step3p6-replay-v1/tests/e2e/mopd_step3p6_bounded_replay/swe_formal.py:112-127,163-170,202-206",
            "training_order": "distill_0 parts 0000..0004, then distill_1 parts 0000..0005; conversation order, then every role=assistant position",
            "identity_extraction": "Recursive explicit message/meta keys and labelled initial-context fields; no request/tool-call IDs used as task identities",
            "problem_statement_extraction": "Nonempty <pr_description> bodies and text after Task Description: in system/user context before the first assistant",
            "problem_statement_normalization": "SHA256 of UTF-8 encoded ' '.join(text.split()); case and punctuation preserved",
            "repo_commit_comparison": "Exact explicit repository and base_commit strings, without alias inference",
            "prefix_eligibility": "Native source assistant positions before Qwen prompt encoding; actual <131072-token eligibility was not evaluated",
            "repository_context": "GitHub owner/repository URL mentions are reported separately, not promoted to authoritative task repo fields",
        },
        "benchmark_counts": benchmark_counts,
        "benchmark_tasks": tasks,
        "training_identity_counts": training_counts,
        "scopes": scopes,
        "training_conversation_identities": conversations,
        "reference_evidence": reference_evidence(args.manifest.parents[4]),
        "limitations": [
            "Missing structured instance_id/repo/base_commit fields leave identity-based overlap unverified; seven initial-context repo labels do not restore complete task identity. Zero observed matches is not proof of non-overlap.",
            "Exact problem text matching does not detect paraphrases, aliases, translations, or edited copies.",
            "The two prefix memberships are native pre-tokenization assistant prefixes, not a verified post-Qwen-length-filter eligible stream. An all-source zero exact-text intersection also implies zero for any subset of these source conversations.",
            "Repository mentions can reference dependencies, comparisons, or screenshots, rather than the task repository.",
            "No exclusion, data rewrite, GPU run, cloud write, or overlap-handling decision is made.",
        ],
        "execution": {
            "python": sys.executable,
            "python_version": platform.python_version(),
            "argv": shlex.join([sys.executable, *sys.argv]),
            "script": file_identity(__file__),
            "elapsed_seconds_before_write": time.monotonic() - started_at,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({
        "output": str(args.output),
        "training_identity_counts": training_counts,
        "benchmark_counts": benchmark_counts,
        "scopes": scopes,
    }, indent=2))


if __name__ == "__main__":
    main()
