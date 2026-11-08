"""Retain the 2026-11-08 SWE-1003 fixture and hand-computed audit checks.

Adapted from /data/ycfeng/tmp/agent-opd-image/make_and_check_swe1003_synthetic.py;
the original is preserved. Native filenames and pins come from source_audit_config.json.
Run from the repository root with python -m tests.manual.agent_opd.make_and_check_swe1003_synthetic:
  make <fresh-source-directory> [--config <source_audit_config.json>]
  audit-command <source-directory> <output-directory> [--config <source_audit_config.json>]
  check <output-directory>
  prompt-adjacency

audit-command only prints a command; this script never launches the audit workflow.
The fixture adds different instance_id values for identical first-user text. Missing
first-user messages are checked separately by the pure prompt-adjacency regression.
"""

import argparse
import json
import shlex
from pathlib import Path

from tests.manual.agent_opd.audit_swe1003_sources import (
    SOURCE_MANIFEST, SourceConversation, prompt_adjacency, prompt_key,
)
from tests.manual.agent_opd.submit_swe1003_audit import _commands
from tests.manual.agent_opd.swe_inputs import load_pinned_modules

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "task_memory/task_2026-11-08_qwen35_full_kl_nll/source_audit_config.json"
TOOLS = [{"type": "function", "function": {
    "name": "bash", "description": "Run a command",
    "parameters": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
}}]


def system(tools_key="tool_schemas", **extra):
    return {"role": "system", "content": "You are a coding agent.", tools_key: TOOLS, "loss_mask": 0,
            "meta": {"instance_id": extra.pop("instance")}, **extra}


def user(text):
    return {"role": "user", "content": text, "loss_mask": 0}


def assistant(mask, call=None):
    message = {"role": "assistant", "content": "Done." if call is None else "", "reasoning_content": "Think.",
               "loss_mask": mask}
    if call is not None:
        message["tool_calls"] = [{"id": call, "type": "function",
                                  "function": {"name": "bash", "arguments": json.dumps({"command": "ls"})}}]
    return message


def tool(call, text="file.py"):
    return {"role": "tool", "content": text, "tool_call_id": call, "loss_mask": 0}


def files():
    f0 = [
        # c0: prompt A, eligible 2 of 3 assistants.
        [system(instance="A"), user("Fix task A"), assistant(1, "c1"), tool("c1"), assistant(0, "c2"), tool("c2"),
         assistant(1)],
        # c1: visual (image part in user content), eligible 1.
        [system(instance="V"), {"role": "user", "loss_mask": 0, "content": [
            {"type": "image_url", "image_url": {"url": "data:image/png;base64,AAAA"}}]}, assistant(1)],
        # c2: identical prompt A, different instance metadata; third training prefix is over-length.
        [system(instance="A-other"), user("Fix task A"), assistant(1, "c1"), tool("c1"), assistant(1, "c2"),
         tool("c2", "word " * 6000), assistant(1)],
    ]
    f1 = [[system(instance="N"), user("Fix task N"), assistant(0, "c1"), tool("c1"), assistant(0)]]
    rest = []
    for index, name in enumerate("BCDEFG"):
        first = system("tools", instance=name, reasoning_effort="high") if index == 0 else system(instance=name)
        rest.append([[first, user(f"Fix task {name}"), assistant(1), user("continue"), assistant(1)]])
    return [f0, f1, *rest]


def make(directory: Path, config: dict) -> None:
    modules = load_pinned_modules(Path(config["steptron_root"]), {
        SOURCE_MANIFEST: config["module_sha256"][SOURCE_MANIFEST],
    })
    paths = modules[SOURCE_MANIFEST].SWE_DATA_FILES
    rows_by_file = list(zip(paths, files(), strict=True))
    directory.mkdir(parents=True, exist_ok=False)
    for path, rows in rows_by_file:
        with (directory / Path(path).name).open("x") as stream:
            stream.write(json.dumps(rows) + "\n")
    print(json.dumps({"status": "PASS", "source_root": str(directory.resolve()), "files": len(rows_by_file)}))


def check_prompt_adjacency() -> dict:
    first, second = files()[0][0], files()[0][2]
    assert first[0]["meta"]["instance_id"] != second[0]["meta"]["instance_id"]
    first_key, second_key = prompt_key(first), prompt_key(second)
    assert first_key is not None and first_key == second_key
    missing = [[system(instance="missing-1"), assistant(1)], [system(instance="missing-2"), assistant(1)]]
    assert [prompt_key(messages) for messages in missing] == [None, None]
    rows = [SourceConversation(0, index, 2, 1, 1, False, key)
            for index, key in enumerate((first_key, second_key, None, None, first_key))]
    adjacency = prompt_adjacency(rows, 2)
    assert adjacency["distinct_prompt_groups"] == 1
    assert adjacency["conversations_without_key"] == 2
    assert adjacency["conversations_per_prompt_group"] == {
        "count": 1, "min": 3, "median": 3, "p90": 3, "max": 3, "mean": 3.0,
    }
    assert adjacency["same_prompt_runs_in_file_order"] == {
        "count": 2, "min": 1, "median": 1.5, "p90": 2, "max": 2, "mean": 1.5,
    }
    assert adjacency["distinct_prompt_groups_in_2_consecutive_conversations"] == {
        "count": 4, "min": 0, "median": 1.0, "p90": 1, "max": 1, "mean": 0.75,
    }
    assert "distinct_tasks" not in adjacency
    return {"status": "PASS", "different_instance_ids_same_prompt_group": True,
            "missing_first_user_is_not_a_prompt_group": True, "no_task_count_claimed": True,
            "prompt_adjacency": adjacency}


def check(output_root: Path) -> dict:
    audit = json.loads((output_root / "swe1003-source-audit.json").read_text())
    manifest = json.loads((output_root / "swe1003-source-manifest.json").read_text())
    expected_totals = {
        "files": 8, "conversations": 10, "assistant_turns": 21, "eligible_turns": 18, "masked_assistant_turns": 3,
        "visual_conversations": 1, "eligible_turns_excluded_as_visual": 1, "conversations_without_eligible_turns": 1,
        "trainable_conversations": 8, "trainable_eligible_turns": 17, "overlength_conversations": 1,
        "overlength_turns": 1,
    }
    checks = {f"totals.{key}": (audit["totals"][key], value) for key, value in expected_totals.items()}
    checks.update({
        "file0 visual indices": (audit["files"][0]["visual_source_item_indices"], [1]),
        "file0 eligible per conversation": (audit["eligible_turns_per_conversation"][0], [2, 1, 3]),
        "file1 without eligible": (audit["files"][1]["conversations_without_eligible_turns"], 1),
        "distinct prompt groups": (audit["prompt_adjacency"]["distinct_prompt_groups"], 7),
        "longest same-prompt run": (audit["prompt_adjacency"]["same_prompt_runs_in_file_order"]["max"], 2),
        "task identity unverified": (audit["task_identity"]["status"], "UNVERIFIED"),
        "task count unknown": (audit["task_identity"]["distinct_tasks"], None),
        "reasoning_effort values": (audit["schema"]["first_message_option_values"], {"reasoning_effort": {"'high'": 1}}),
        "meta instance_id": (audit["schema"]["meta_keys"]["instance_id"], {"messages": 10, "distinct_values": 10}),
        "manifest status": (manifest["status"], "COMPLETE"),
        "manifest files": (len(manifest["files"]), 8),
    })
    streaming = next(simulation for simulation in audit["simulations"] if simulation["active_conversations"] == 1)
    checks.update({
        "M=1 draws": (streaming["draws"], 7), "M=1 accepted": (streaming["accepted"], 6),
        "M=1 rejected": (streaming["rejected_overlength"], 1), "M=1 repeated": (streaming["repeated_turns"], 0),
        "M=1 trained": (streaming["conversations_trained"], 3), "M=1 finished": (streaming["conversations_finished"], 3),
        "M=1 span max": (streaming["update_span"]["max"], 2), "M=1 span min": (streaming["update_span"]["min"], 1),
    })
    interleaved = next(simulation for simulation in audit["simulations"] if simulation["active_conversations"] == 2)
    checks.update({"M=2 accepted": (interleaved["accepted"], 6),
                   "M=2 draws = accepted + rejected": (interleaved["draws"],
                                                       interleaved["accepted"] + interleaved["rejected_overlength"])})
    for index, simulation in enumerate(audit["simulations"]):
        checks[f"simulation {index} task count unknown"] = (simulation["tasks_per_update"], None)
        checks[f"simulation {index} prompt groups recorded"] = ("prompt_groups_per_update" in simulation, True)
    failures = [f"{name}: {actual!r} != {expected!r}"
                for name, (actual, expected) in checks.items() if actual != expected]
    check_prompt_adjacency()
    return {"status": "FAIL" if failures else "PASS", "failures": failures,
            "longest_prompt_tokens": audit["trainable_distributions"]["longest_prompt_tokens"],
            "task_identity": audit["task_identity"],
            "M=2": {key: interleaved[key] for key in ("draws", "rejected_overlength", "update_span",
                                                      "conversations_trained", "tasks_per_update",
                                                      "prompt_groups_per_update")}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    make_parser = commands.add_parser("make")
    make_parser.add_argument("directory", type=Path)
    make_parser.add_argument("--config", type=Path, default=CONFIG)
    audit_parser = commands.add_parser("audit-command")
    audit_parser.add_argument("source_root", type=Path)
    audit_parser.add_argument("output_root", type=Path)
    audit_parser.add_argument("--config", type=Path, default=CONFIG)
    commands.add_parser("check").add_argument("output_root", type=Path)
    commands.add_parser("prompt-adjacency")
    args = parser.parse_args()
    if args.command == "make":
        make(args.directory, json.loads(args.config.read_text()))
    elif args.command == "audit-command":
        config = json.loads(args.config.read_text())
        # Fixture dimensions replace formal-run dimensions, not native module pins.
        config.update(repo=str(REPO_ROOT), source_root=str(args.source_root.resolve()),
                      output_root=str(args.output_root.resolve()), simulate=["1x2", "2x2"],
                      updates=2, turns_per_update=3, trend_window=1, rollout_max_context_len=2000)
        print(shlex.join(_commands(config)[0]))
    else:
        result = check(args.output_root) if args.command == "check" else check_prompt_adjacency()
        print(json.dumps(result))
        raise SystemExit(result["status"] != "PASS")


if __name__ == "__main__":
    main()
