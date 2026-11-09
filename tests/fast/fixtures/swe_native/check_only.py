"""Exercise the real pinned RunCheckPipeline check-only path with local grader injection.

The native trajectory parser, check request, result writer, and Miles adapter run
unchanged. ACS/model HTTP and the agent generation method are forbidden.
"""

import argparse
import json
import os
from pathlib import Path
from unittest.mock import patch

import playground.agenticeval.sweagents_swe as pipeline_module
import requests
import step_align.model.stepchat as stepchat
import swe_agents.cli.run as run_cli
import swe_agents.models.step_align as model_module
import toml

from tests.manual.agent_opd import swe_evaluation as swe
from tests.manual.agent_opd import swe_native_evaluation as native


def forbidden(*args, **kwargs):
    raise AssertionError("Check-only recovery must not generate or send any HTTP request")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--swe-source", required=True)
    args = parser.parse_args()
    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=False)
    fixtures = Path(__file__).parent
    task = "astropy__astropy-12907"
    request = {"point_id": "CPU-native-check-only", "task_id": task, "seed": 1729}
    runtime = {
        "swe_commit": swe.SWE_COMMIT,
        "dataset_path": args.dataset,
        "manifest_path": str(root / "benchmark.json"),
        "swe_source_root": args.swe_source,
        "model_name": "qwen35-4b",
        "url": "http://CPU-NO-NETWORK.invalid",
        "server_identity": {"model_path": "CPU-NO-MODEL", "weight_version": "CPU-FIXTURE"},
    }
    swe.write_json(runtime["manifest_path"], {"CPU_fixture": True})
    scorer = Path(args.reference) / "tests/e2e/mopd_step3p6_bounded_replay/swe_formal.py"
    sources = [
        scorer,
        *(Path(module.__file__).resolve() for module in (run_cli, model_module, stepchat, pipeline_module)),
    ]
    runtime["source_sha256"] = {str(path): native._sha(path) for path in sources}
    runtime["input_sha256"] = {
        str(path): native._sha(path) for path in (Path(args.dataset), Path(runtime["manifest_path"]))
    }
    config = native.native_config(runtime, request=request, dataset_index=0)
    original = root / "original"
    trajectory = original / "trajectories" / f"{task}.json"
    trajectory.parent.mkdir(parents=True)
    trajectory.write_bytes((fixtures / "submitted.json").read_bytes())
    config_path = original / "config.toml"
    config_path.write_text(toml.dumps(config))
    wire = original / "requests" / "000000.json"
    swe.write_json(
        wire,
        {
            "url": runtime["url"] + "/v1/chat/completions",
            "body": {"temperature": 1.0, "top_p": 0.95, "seed": 1729},
            "max_tokens": None,
            "n": 1,
            "CPU_fixture": True,
        },
    )
    manifest_path = root / "manifest.json"
    swe.write_json(manifest_path, {"configuration": native.evaluation_contract(runtime)})
    invocation_path = root / "recovery" / "invocation.json"
    swe.write_json(
        invocation_path,
        {
            "runtime": runtime,
            "request": request,
            "point_manifest": str(manifest_path),
            "reference_root": args.reference,
            "deadline_at": 4000000000,
            "trajectory_source": {
                "path": str(trajectory),
                "sha256": native._sha(trajectory),
                "request_paths": [str(wire)],
            },
        },
    )
    requests_seen = []

    def grader(pipeline, payload):
        requests_seen.append(payload)
        assert payload["patch"] == swe.read_json(trajectory)["meta"]["patch"]
        return swe.read_json(fixtures / "apply_patch_fail.json")

    with patch.dict(
        os.environ, {"SR_USER_TOKEN": "CPU-NO-NETWORK", "SESSION_ROUTER_USER_TOKEN": "CPU-NO-NETWORK"}
    ), patch.object(requests, "post", forbidden), patch.object(
        pipeline_module.RunCheckPipeline, "_run_instance", forbidden
    ), patch.object(
        pipeline_module.RunCheckPipeline, "_run_check_subprocess", grader
    ):
        native.native_child(str(invocation_path))
    outcome = swe.read_json(invocation_path.parent / "outcome.json")
    assert outcome["success"] is False and len(requests_seen) == 1
    archived = outcome["raw"]["native_artifacts"]
    assert archived["trajectory"]["sha256"] == native._sha(trajectory)
    assert native._sha(outcome["raw"]["request_paths"][0]) == native._sha(wire)
    assert swe.read_json(archived["grader"]["path"])["schema_version"] == 1
    print(
        json.dumps(
            {
                "status": "PASS",
                "kind": "native check-only CPU grader injection; no live ACS/model score",
                "native_check_requests": len(requests_seen),
                "trajectory_bytes_unchanged": True,
                "requests_bytes_unchanged": True,
                "success": False,
                "outcome": str(invocation_path.parent / "outcome.json"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
