"""Test-only local smoke launcher: reject HF2 before admission, dispatch HF3 normally.

Parent-operated command, using the existing training submitter's CLI:

    python -B -m tests.manual.agent_opd.check_swe_native_async \
        --config "$INTEGRATION" --pair A --protocol r256 --receipt "$NEW_RECEIPT"

Only smoke3/8/2/save2 with one explicit qualification slot is allowed. The first
HF2 evaluator subprocess gets an empty AK_BASEMIND in its child environment only.
HF3 inherits the actual unchanged private environment. No fake platform, scorer,
production fault flag, extra admission path or cleanup is supplied here. The
parent must inspect the real native receipts, ledger and reader cleanup afterwards.
"""

import argparse
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tests.manual.agent_opd import submit_swe_opd
from tests.manual.agent_opd import watch_swe_evaluations as watch
from tests.manual.agent_opd.swe_evaluation import read_json, write_json


class _QualificationWatcher(watch.EvaluationWatcher):
    def __init__(self, *args):
        super().__init__(*args)
        self.injected = False

    def _launch(self, point, row):
        popen = watch.subprocess.Popen

        def launch(argv, **kwargs):
            target = (
                not self.injected
                and point.startswith("qualification.")
                and point.endswith(f".{self.job_id}.HF2")
                and argv[:5] == [sys.executable, "-u", "-B", "-m", "tests.manual.agent_opd.submit_swe_evaluation"]
                and argv[argv.index("--point") + 1] == point
            )
            if target:
                env = dict(os.environ if kwargs.get("env") is None else kwargs["env"])
                env["AK_BASEMIND"] = ""
                kwargs["env"] = env
            child = popen(argv, **kwargs)
            if target:
                self.injected = True
                evidence = {"point_id": point, "field": "AK_BASEMIND", "at": time.time()}
                try:
                    write_json(self.directory / "fault.json", evidence)
                except Exception:
                    # Recording is an auxiliary soft gate, never a reason to discard a live launcher.
                    print("SWE_NATIVE_ASYNC_FAULT_EVIDENCE_UNVERIFIED", evidence, flush=True)
            return child

        # Intercept only this exact evaluator argv in this dedicated test process.
        with patch.object(watch, "subprocess", SimpleNamespace(Popen=launch, STDOUT=watch.subprocess.STDOUT)):
            super()._launch(point, row)


def _validate(config, path):
    if "KUBEBRAIN_RJOB_NAME" in os.environ:
        raise ValueError("The native async check is local only, never an RJob worker")
    submit_swe_opd._validate_paths(config, path)
    if Path.cwd().resolve() != Path(config["local_mount"]).resolve():
        raise ValueError("Run the native async check from the integration local_mount")
    train = config["training"]
    expected = {"run_kind": "smoke", "successful_updates": 3, "bank_slots": 8, "bank_uses": 2, "save_interval": 2}
    if any(train[field] != value for field, value in expected.items()):
        raise ValueError("The native async check allows only smoke3/8/2/save2, never a formal run")
    checkpoint = config["checkpoint"]
    if checkpoint["post_save_hook"] != "tests.manual.agent_opd.swe_hf_export.post_save":
        raise ValueError("The native async check requires the existing public HF publication callback")
    configuration = watch._local_path(
        checkpoint["hook_args"]["swe_evaluation_configuration"], Path(config["local_mount"]).resolve()
    )
    evaluation = read_json(configuration)
    mount, _, _ = watch.validate_dispatch(configuration, evaluation)
    if mount != Path(config["local_mount"]).resolve() or len(watch.qualification_attempt_ids(evaluation)) != 1:
        raise ValueError("The native async check requires the same local mount and exactly one explicit slot")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--pair", choices=("A", "B"), required=True)
    parser.add_argument("--protocol", choices=("full", "r256"), required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    path = args.config.resolve(strict=True)
    config = read_json(path)
    _validate(config, path)
    watch._local_path(args.receipt, Path(config["local_mount"]).resolve())
    with patch.object(watch, "EvaluationWatcher", _QualificationWatcher):
        return submit_swe_opd.main()


if __name__ == "__main__":
    raise SystemExit(main())
