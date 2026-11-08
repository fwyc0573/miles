"""Construct the existing SWE contract in the native Python3.10 environment.

No platform clients, credentials, model servers or graders are created here.
The caller supplies deployment observations; source/input identities come from
the accepted T03 evidence, and native_config remains the sole harness owner.
"""

import argparse
import copy
import hashlib
from pathlib import Path
from urllib.parse import urlsplit

from tests.manual.agent_opd import swe_native_evaluation as native
from tests.manual.agent_opd.swe_evaluation import SEEDS, benchmark_tasks, read_json, write_json
from tests.manual.agent_opd.watch_swe_evaluations import validate_dispatch


def build_configuration(inputs):
    """Build once before enqueue; do not reconstruct an existing point's contract.

    Required inputs are explicit rather than fabricated runtime/job identities.
    Run this function with the repaired SWE interpreter and its source PYTHONPATH.
    The outer worker may run in the pinned GPU image's Python3.12 independently.
    """
    pins = read_json(inputs["source_pins"])
    integration = read_json(inputs["integration_config"])
    source = integration["pairs"]["A"]["student"]["path"]
    if integration["pairs"]["B"]["student"]["path"] != source:
        raise ValueError("The four cells must share the original 4B source")
    protected = [str(Path(path).resolve()) for path in inputs["protected_sources"]]
    if str(Path(source).resolve()) not in protected:
        raise ValueError("The original 4B source must be explicitly protected")
    identity = copy.deepcopy(inputs["server_identity"])
    if identity["weight_version"] is None or inputs["baseline_weight_version"] is None:
        raise ValueError("Supply the original-source and endpoint weight-version identities")
    if not identity["sglang_version"]:
        raise ValueError("Supply the SGLang version observed in the pinned image")
    endpoint = urlsplit(inputs["url"])
    if endpoint.scheme != "http" or endpoint.hostname != "127.0.0.1" or not endpoint.port or endpoint.path:
        raise ValueError("The owned single-node server requires an explicit loopback HTTP port")
    runtime = {
        "python": inputs["native_python"],
        "python_paths": inputs["python_paths"],
        "swe_source_root": pins["snapshot_path"],
        "swe_commit": pins["swe_commit"],
        "source_sha256": pins["source_sha256"],
        "input_sha256": {
            inputs["dataset_path"]: pins["benchmark_library_sha256"],
            pins["benchmark_manifest"]: inputs["manifest_sha256"],
        },
        "dataset_path": inputs["dataset_path"],
        "manifest_path": pins["benchmark_manifest"],
        "model_name": pins["configuration_payloads"][0]["model"]["model_name"],
        "url": inputs["url"],
        "server_reader_id": inputs["server_reader_id"],
        "server_identity": identity,
        "chat_template": pins["qwen_template"]["path"],
        "baseline_weight_version": inputs["baseline_weight_version"],
        "kill_grace_seconds": inputs["kill_grace_seconds"],
    }
    native._verify_sources(runtime)
    tasks = benchmark_tasks(runtime["manifest_path"], runtime["dataset_path"])
    if list(tasks) != pins["task_ids"]:
        raise ValueError("Selected IDs must match the accepted manifest-ordered 100 tasks")
    _validate_identity(identity, pins["qwen_template"])
    contract = native.evaluation_contract(runtime)
    # Existing evidence must still agree with the actual native constructor.
    for seed, recorded in zip(SEEDS, pins["configuration_payloads"], strict=True):
        actual = native.native_config(runtime, request={"seed": seed}, dataset_index=0)
        if native._config_contract(actual) != native._config_contract(recorded):
            raise ValueError("The inherited native harness differs from the reviewed source evidence")
    server = {
        "python": integration["worker_python"],
        "image": integration["image"],
        "repo": integration["repo"],
        "local_root": integration["worker_local_root"],
        "startup_timeout": integration["pairs"]["A"]["startup_timeout"],
        "request_timeout": inputs["server_request_timeout"],
        "cleanup_grace_seconds": inputs["server_cleanup_grace_seconds"],
        "chat_template": pins["qwen_template"]["path"],
        **{
            name: integration["pairs"]["A"]["student"][name]
            for name in ("mem_fraction_static", "max_running_requests", "chunked_prefill_size")
        },
    }
    if min(runtime["kill_grace_seconds"], server["request_timeout"], server["startup_timeout"]) <= 0:
        raise ValueError("Native cleanup and server startup/request timeouts must be positive")
    if server["cleanup_grace_seconds"] <= runtime["kill_grace_seconds"]:
        raise ValueError("Coordinator cleanup must allow the native children to finish their cleanup")
    configuration = {
        "root": inputs["root"],
        "owned_root": inputs["owned_root"],
        "protected_sources": protected,
        "original_source": source,
        "reference_root": inputs["reference_root"],
        "allocation_identity": {
            "task_id": read_json(integration["gpu_policy"])["task_id"],
            "creator": integration["creator"],
            "gpu_tag": integration["gpu_tag"],
        },
        "task_ids": list(tasks),
        "evaluation_contract": contract,
        "runtime": runtime,
        "server": server,
    }
    if "dispatch" in inputs:
        configuration["dispatch"] = copy.deepcopy(inputs["dispatch"])
        validate_dispatch(inputs["integration_config"], configuration)
    return configuration


def _validate_identity(identity, template):
    # Registry imports belong to the GPU Python3.12 worker. Native3.10 owns
    # the frozen source/template bytes and the inherited scientific contract.
    expected = {
        "context_length": 131072,
        "preserve_thinking": True,
        "enable_thinking": True,
        "chat_template_sha256": template["sha256"],
    }
    if any(identity[name] != value for name, value in expected.items()):
        raise ValueError("Endpoint identity must use the pinned Qwen template and complete 128K context with thinking")
    if hashlib.sha256(Path(template["path"]).read_bytes()).hexdigest() != template["sha256"]:
        raise ValueError("The accepted fixed Qwen template changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Configuration already exists; do not replace an immutable point contract")
    configuration = build_configuration(read_json(args.inputs))
    if "dispatch" in configuration:
        validate_dispatch(args.output, configuration)
    write_json(args.output, configuration)


if __name__ == "__main__":
    main()
