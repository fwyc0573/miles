"""Run one seed of the original SWE agent/tools/grader against a GLM endpoint.

Use the existing native SWE Python environment and source paths in PYTHONPATH.
This adapter records input/version/outcome identity and keeps infrastructure or
invalid grader results separate from resolved/unresolved model outcomes.
"""

import argparse
import hashlib
import json
import time
from collections import Counter
from pathlib import Path

import toml
from playground.agenticeval.sweagents_configs import SweAgentACSEvalConfig
from playground.agenticeval.sweagents_swe import RunCheckPipeline
from tests.e2e.mopd_step3p6_bounded_replay.swe_formal import outcome


def _write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--membership", type=Path, required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--version", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--task-index", type=int)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--server-log", type=Path, required=True)
    args = parser.parse_args()
    args.output.relative_to("/mnt/codesign-exp/ycfeng")
    membership = json.loads(args.membership.read_text())
    if args.seed not in membership["seeds"]:
        raise ValueError("The benchmark seed is absent from the frozen membership")
    dataset = Path(membership["dataset"])
    if hashlib.sha256(dataset.read_bytes()).hexdigest() != membership["dataset_sha256"]:
        raise ValueError("Frozen benchmark questions changed")
    config = SweAgentACSEvalConfig().to_dict()
    config.update(repeat=1, concurrency=1, check_concurrency=1, save_stepeval_checkpoint=False, use_exit_code=False)
    config["check"]["concurrency"] = 1
    config["dataset"]["name_or_path"] = str(dataset)
    indices = list(range(len(membership["task_ids"]))) if args.task_index is None else [args.task_index]
    if any(index < 0 or index >= len(membership["task_ids"]) for index in indices):
        raise ValueError("Benchmark task index is outside the frozen membership")
    task_ids = [membership["task_ids"][index] for index in indices]
    config["dataset"]["range_str"] = ",".join(map(str, indices))
    config["model"].update(
        model_name=args.model,
        max_context_tokens=131072,
        inference_args={
            "custom_upstream_url": args.url + "/v1/chat/completions",
            "seed": args.seed,
            "chat_template_kwargs": {"clear_thinking": False},
        },
    )
    if (config["model"]["temperature"], config["model"]["top_p"]) != (1.0, 0.95):
        raise ValueError("The native evaluator sampling settings changed")
    args.output.mkdir(parents=True, exist_ok=False)
    config_path = args.output / "config.toml"
    config_path.write_text(toml.dumps(config))
    records = args.output / "outcomes"
    records.mkdir()

    class RecordedPipeline(RunCheckPipeline):
        def _record(self, instance: dict, stage: str, status: str, **fields):
            task_id = instance["instance_id"]
            _write(
                records / f"{task_id}.{stage}.json",
                {
                    "task_id": task_id,
                    "seed": args.seed,
                    "completed_updates": args.version,
                    "stage": stage,
                    "status": status,
                    "unix_time": time.time(),
                    **fields,
                },
            )

        def _run_instance(self, instance: dict, repeat_idx: int):
            self._record(instance, "generation", "running")
            started = time.monotonic()
            log_start = args.server_log.stat().st_size
            try:
                super()._run_instance(instance, repeat_idx)
            except Exception as error:
                self._record(
                    instance,
                    "generation",
                    "failed",
                    error_type=type(error).__name__,
                    elapsed_seconds=time.monotonic() - started,
                )
                raise
            with args.server_log.open("rb") as stream:
                stream.seek(log_start)
                raw = stream.read(args.server_log.stat().st_size - log_start)
            issued = []
            for line in raw.decode(errors="replace").splitlines():
                marker = line.find('{"timestamp":')
                if marker < 0:
                    continue
                entry = json.loads(line[marker:])
                if entry.get("event") != "request.received":
                    continue
                sampling = entry["obj"]["sampling_params"]
                if sampling.get("sampling_seed") == args.seed:
                    issued.append(
                        {
                            "rid": entry["rid"],
                            "n": sampling.get("n", 1),
                            "temperature": sampling["temperature"],
                            "top_p": sampling["top_p"],
                        }
                    )
            verified = bool(issued) and all(
                (row["n"], row["temperature"], row["top_p"]) == (1, 1.0, 0.95) for row in issued
            )
            self._record(
                instance,
                "generation",
                "returned",
                elapsed_seconds=time.monotonic() - started,
                seed_verified=verified,
                engine_requests=issued,
                log_interval_sha256=hashlib.sha256(raw).hexdigest(),
            )

        def _check_instance(self, instance: dict, repeat_idx: int) -> str:
            started = time.monotonic()
            self._record(instance, "grading", "running")
            try:
                status = super()._check_instance(instance, repeat_idx)
                trajectory_path = self._traj_path(instance["instance_id"], repeat_idx)
                resolved = outcome(
                    instance["instance_id"],
                    trajectory_path,
                    self._check_result_path(instance["instance_id"], repeat_idx),
                )
                trajectory = json.loads(trajectory_path.read_text())
                if trajectory.get("error_type") or trajectory.get("error_family"):
                    raise ValueError("Native trajectory contains a top-level execution error")
                messages = [message for dialog in trajectory["dialogs"] for message in dialog["messages"]]
                assistants = [message for message in messages if message["role"] == "assistant"]
                tools = Counter(
                    call["function"]["name"] for message in assistants for call in message.get("tool_calls", [])
                )
                signals = {
                    "assistant_turns": len(assistants),
                    "thinking_turns": sum(bool(message.get("reasoning_content")) for message in assistants),
                    "body_turns": sum(bool(message.get("content")) for message in assistants),
                    "tool_calls": dict(tools),
                    "tool_response_turns": sum(message["role"] == "tool" for message in messages),
                }
            except Exception as error:
                self._record(
                    instance,
                    "grading",
                    "invalid",
                    error_type=type(error).__name__,
                    elapsed_seconds=time.monotonic() - started,
                )
                raise
            self._record(
                instance,
                "grading",
                "resolved" if resolved else "unresolved",
                resolved=resolved,
                signals=signals,
                elapsed_seconds=time.monotonic() - started,
            )
            print("AGENT_OPD_BENCHMARK_ATTEMPT", args.version, args.seed, instance["instance_id"], status, flush=True)
            return status

    pipeline = RecordedPipeline(eval_config_path=config_path, work_dir=args.output)
    if [row["instance_id"] for row in pipeline.instances] != task_ids:
        raise ValueError("Native pipeline questions differ from the frozen ordered membership")
    pipeline.execute()
    print("AGENT_OPD_BENCHMARK_SEED_FINISHED", args.version, args.seed, flush=True)


if __name__ == "__main__":
    main()
