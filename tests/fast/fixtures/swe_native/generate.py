"""Regenerate CPU fault-injection artifacts with the pinned native SWE serializers.

Requires the existing native SWE Python environment and its source PYTHONPATH.
No model, ACS, GPU, or platform request is made.
"""

import argparse
import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import toml
from loguru import logger
from swe_agents.core import Dialog, TaskTrajectory, UserTextMessage
from swe_agents.core.exceptions import EnvInitError
from swe_agents.impl.sweagent.agents.default import DefaultAgent, StepOutput
from swe_agents.swe_evaluation.evaluation_helpers import handle_evaluation_exceptions
from swe_agents.swe_evaluation.harness.constants import END_TEST_OUTPUT, START_TEST_OUTPUT
from swe_agents.swe_evaluation.harness.grading import get_eval_report
from swe_agents.swe_evaluation.harness.test_spec.test_spec import make_test_spec
from swe_agents.swe_evaluation.harness.utils import PatchApplyFailedError
from tests.manual.agent_opd.swe_native_evaluation import native_config


class LocalEnvironment:
    def __init__(self, patch, dead):
        self.patch, self.dead = patch, dead

    def communicate(self, *args, **kwargs):
        return "/testbed"

    def execute_command(self, *args, **kwargs):
        if self.dead:
            raise EnvInitError("CPU fault injection: container/tmux died")

    def read_file(self, *args, **kwargs):
        return self.patch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--reference", required=True)
    args = parser.parse_args()
    root = Path(__file__).parent
    logger.disable("swe_agents.impl.sweagent.agents.default")
    config = native_config(
        {"dataset_path": args.dataset, "model_name": "qwen35-4b", "url": "http://evaluation-worker:31000"},
        request={"seed": 1729},
        dataset_index=0,
    )
    (root / "native_config.json").write_text(json.dumps(config, indent=2) + "\n")
    (root / "native_config.toml").write_text(toml.dumps(config))
    instance = next(
        row for row in json.loads(Path(args.dataset).read_text()) if row["instance_id"] == "astropy__astropy-12907"
    )
    spec = make_test_spec(instance, namespace="hub.i.basemind.com/swe-bench2512-tags", use_exit_code=False)
    patch = "diff --git a/fixture.py b/fixture.py\n--- a/fixture.py\n+++ b/fixture.py\n@@ -1 +1 @@\n-old\n+new\n"
    log = root / "test_output.txt"
    log.write_text(
        START_TEST_OUTPUT
        + "\n"
        + "\n".join(f"{name} FAILED" for name in spec.FAIL_TO_PASS)
        + "\n"
        + "\n".join(f"{name} PASSED" for name in spec.PASS_TO_PASS)
        + "\n"
        + END_TEST_OUTPUT
        + "\n"
    )
    detail = get_eval_report(spec, patch, str(log), include_tests_status=True)[spec.instance_id]
    assert detail["resolved"] is False and detail["tests_status_allcases"]
    grader = {"instance_id": spec.instance_id, "status": "unresolved", "detail": detail}
    (root / "unresolved.json").write_text(json.dumps(grader, indent=2) + "\n")
    try:
        raise PatchApplyFailedError("CPU fault injection: git apply rejected the model patch")
    except PatchApplyFailedError as error:
        message, status = handle_evaluation_exceptions()(error)
    (root / "apply_patch_fail.json").write_text(
        json.dumps({"instance_id": spec.instance_id, "status": status, "detail": message}, indent=2) + "\n"
    )
    for exit_status, dead in (
        ("submitted", False),
        ("exit_env_error", True),
        ("exit_context", False),
        ("exit_api", False),
        ("exit_error", False),
    ):
        agent = object.__new__(DefaultAgent)
        agent.env = LocalEnvironment(patch, dead)
        agent.tools = SimpleNamespace(check_for_submission_cmd=lambda observation: False)
        agent.logger = logger
        agent._problem_statement = None
        step = StepOutput(
            thought="CPU fault injection", output="CPU fault injection", exit_status=exit_status, done=True
        )
        if exit_status != "submitted":
            step = agent.attempt_autosubmission_after_error(step)
        meta = {"exit_status": step.exit_status, "patch": step.submission or patch}
        # This is the exact native final-state metadata projection in DefaultAgent.run.
        for key in (
            "error_type",
            "early_stop_reason",
            "format_error_code",
            "autosubmit",
            "autosubmit_reason",
            "autosubmit_exit_status",
        ):
            if key in (step.extra_info or {}):
                meta[key] = step.extra_info[key]
        trajectory = TaskTrajectory(
            status="success",
            dialogs=[Dialog(messages=[UserTextMessage(role="user", content=instance["problem_statement"])])],
            meta=meta,
        )
        (root / f"{exit_status}.json").write_text(trajectory.model_dump_json(indent=2) + "\n")
    files = [
        Path(__import__(module, fromlist=["__file__"]).__file__)
        for module in (
            "swe_agents.core.types",
            "swe_agents.impl.sweagent.agents.default",
            "swe_agents.swe_evaluation.evaluation_helpers",
            "swe_agents.swe_evaluation.harness.grading",
        )
    ]
    provenance = {
        "kind": "native-serialized CPU fault injection, not live ACS/model grading",
        "swe_commit": "1af09e5f90f55f6fbce5f71efe7da0030a2e126e",
        "instance_id": spec.instance_id,
        "source_sha256": {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
    }
    reference = Path(args.reference) / "tests/e2e/mopd_step3p6_bounded_replay/swe_formal.py"
    source = reference.read_text()
    # The portable test oracle consists of the exact original read/outcome
    # functions, not a mock or a production source fallback.
    functions = [
        ast.get_source_segment(source, node)
        for node in ast.parse(source).body
        if isinstance(node, ast.FunctionDef) and node.name in ("read", "outcome")
    ]
    assert len(functions) == 2
    oracle = root / "reference/tests/e2e/mopd_step3p6_bounded_replay/swe_formal.py"
    oracle.parent.mkdir(parents=True, exist_ok=True)
    oracle.write_text("import json\nfrom pathlib import Path\n\n\n" + "\n\n\n".join(functions) + "\n")
    provenance["reference_source_sha256"] = {str(reference): hashlib.sha256(reference.read_bytes()).hexdigest()}
    provenance["reference_oracle_sha256"] = hashlib.sha256(oracle.read_bytes()).hexdigest()
    (root / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")


if __name__ == "__main__":
    main()
