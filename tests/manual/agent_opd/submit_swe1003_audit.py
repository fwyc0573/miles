"""Run the in-place SWE-1003 audit and input checks on one CPU RJob.

Initialize personal StepMind authentication on the local host, then run with
--config pointing to the task's source_audit_config.json. The submitter remains
alive until the worker exits. --dry-run prints the exact commands without a job.
"""

import argparse
import json
import os
import shlex
import subprocess
from pathlib import Path


def _commands(config: dict) -> list[list[str]]:
    python = [config["worker_python"], "-u", "-B", "-m"]
    common = []
    for name in ("steptron_root", "source_root", "tokenizer", "chat_template", "rollout_max_context_len"):
        common.extend(["--" + name.replace("_", "-"), str(config[name])])
    output = Path(config["repo"]) / config["output_root"]
    audit = python + ["tests.manual.agent_opd.audit_swe1003_sources"] + common
    for flag, module in (
        ("base-loader", "playground.baseline_new.mopd.online_turn_loader"),
        ("source-manifest", "playground.users.cj.opd.s4_swe_source_manifest_1001"),
        ("turn-data", "playground.users.cj.opd.s4_swe_turn_data_1001"),
        ("visual-audit", "playground.users.cj.opd.s4_swe_visual_audit_1001"),
    ):
        audit.extend([f"--{flag}-sha256", config["module_sha256"][module]])
    audit.extend(["--chat-template-kwargs", json.dumps(config["chat_template_kwargs"]),
                  "--simulate", *config["simulate"], "--output-root", str(output)])
    for name in ("updates", "turns_per_update", "trend_window"):
        audit.extend(["--" + name.replace("_", "-"), str(config[name])])
    check = python + ["tests.manual.agent_opd.check_swe_inputs"] + common
    check.extend(["--source-manifest", str(output / "swe1003-source-manifest.json"),
                  "--module-sha256", json.dumps(config["module_sha256"]),
                  "--turn-source", "loss_masked", "--output-root", str(output / "parity")])
    for name in ("temporary_root", "active_conversations", "block_turns", "order_draws", "parity_draws"):
        check.extend(["--" + name.replace("_", "-"), str(config[name])])
    return [audit, check]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--worker", action="store_true")
    args = parser.parse_args()
    path = args.config.resolve(strict=True)
    config = json.loads(path.read_text())
    commands = _commands(config)
    if args.dry_run:
        print(json.dumps({"submitted": False, "configuration": str(path), "commands": commands,
                          "cpu": config["cpu"], "gpu": config["gpu"], "mem_gb": config["mem_gb"],
                          "mounts": config["mounts"], "image": config["image"]}, indent=2))
        return
    if args.worker:
        import platform

        import torch
        import transformers

        os.chdir(config["repo"])
        print(json.dumps({"python": platform.python_version(), "torch": torch.__version__,
                          "transformers": transformers.__version__, "configuration": str(path)}), flush=True)
        for command in commands:
            print("COMMAND", shlex.join(command), flush=True)
            subprocess.run(command, check=True)
        print("SWE1003_IN_PLACE_AUDIT_AND_PARITY_PASS", flush=True)
        return
    if config["gpu"] != 0:
        raise ValueError("The source audit is CPU-only")
    if os.environ.get("STEPMIND_BACKEND") != "rjob":
        raise ValueError("Initialize STEPMIND_BACKEND=rjob using the personal-auth runbook")
    if not all(os.environ.get(key) for key in ("BRAINPP_ACCESS_KEY", "BRAINPP_SECRET_KEY")):
        raise ValueError("Initialize personal credentials before constructing the backend")
    from steptron.exp.base_exp import ResourceConfig
    from steptron.utils.stepmind import spawn_tasks

    os.chdir(config["local_mount"])
    resource = ResourceConfig(
        cpu=config["cpu"], gpu=0, mem_gb=config["mem_gb"], replica=1,
        image=config["image"], positive_tags=[], extra_requirements=[],
        mounts=list(config["mounts"]), custom_resources=[], envs={},
        command="{COMMAND}", preemptible=False,
        task_specs={"audit": {"is_critical": True, "gang_start": False}},
    )
    resource.exp_name = "qwen35-profile-source-audit"
    os.environ["EXP_ID"] = resource.exp_name
    worker = [config["worker_python"], "-u", "-B", str(Path(__file__).resolve()),
              "--config", str(path), "--worker"]
    script = f"export PYTHONPATH={shlex.quote(config['repo'])}\nexec {shlex.join(worker)}"
    workers = spawn_tasks(resource, command="bash -lc " + shlex.quote(script),
                          charged_group=config["charged_group"], use_image=True,
                          code_mount_point=config["local_mount"])
    print("SWE1003_AUDIT_TERMINAL", workers.rjob.meta.name, workers.poll(), flush=True)


if __name__ == "__main__":
    main()
