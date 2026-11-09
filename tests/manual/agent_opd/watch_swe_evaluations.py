"""Dispatch trainer-enqueued SWE points from the local mounted workspace only.

The local training submitter prepares the dispatch base before native submission
and starts one observer after obtaining the actual job name. Its native
workers.wait() return or failure signals drain; admitted evaluation
submitter subprocesses remain alive until they exit. Standalone observation uses
the same dispatcher and an actual training terminal receipt:

    python -B -m tests.manual.agent_opd.watch_swe_evaluations \
        --config "$INTEGRATION" --configuration "$EVALUATION" \
        --job "$TRAINING_JOB" --trainer-receipt "$TRAINING_RECEIPT"

Evaluation JSON requires dispatch.local_mount, dispatch.directory and positive
dispatch.poll_seconds. Only a proven admission denial is rechecked while training
is alive. After training finishes, drain admitted children and report remaining
queued points. Unknown, failed and incomplete evaluations require operator RCA;
this observer never reads the cloud store, resumes a scorer or submits on a GPU.
"""

import argparse
import fcntl
import logging
import math
import os
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from tests.manual.agent_opd.rjob_budget import _TERMINAL_PHASES
from tests.manual.agent_opd.swe_evaluation import HF_UPDATES, SEEDS, _label, _locked, read_json, write_json

logger = logging.getLogger(__name__)


def _local_path(path, mount):
    path = Path(path)
    if not path.is_absolute() or ".." in path.parts or path.is_relative_to("/mnt"):
        raise ValueError("Dispatch paths must be absolute local workspace paths, not cloud paths")
    resolved = path.resolve()
    if resolved.is_relative_to("/mnt") or not resolved.is_relative_to(mount):
        raise ValueError("Dispatch paths must resolve under dispatch.local_mount")
    return resolved


def validate_dispatch(configuration, evaluation):
    """Validate the existing local dispatch contract without fabricating a job ID."""
    dispatch = evaluation["dispatch"]
    mount = Path(dispatch["local_mount"])
    if (
        not mount.is_absolute()
        or ".." in mount.parts
        or mount.is_relative_to("/mnt")
        or mount.resolve().is_relative_to("/mnt")
    ):
        raise ValueError("dispatch.local_mount must identify a local workspace")
    mount = mount.resolve()
    _local_path(configuration, mount)
    seconds = dispatch["poll_seconds"]
    if (
        isinstance(seconds, bool)
        or not isinstance(seconds, (int, float))
        or not math.isfinite(seconds)
        or seconds <= 0
    ):
        raise ValueError("dispatch.poll_seconds must be finite and positive")
    directory = _local_path(dispatch["directory"], mount)
    qualification_attempt_ids(evaluation)
    return mount, directory, seconds


def qualification_attempt_ids(evaluation):
    """Return only explicitly selected qualification slots from the frozen ledger."""
    dispatch = evaluation.get("dispatch", {})
    if "qualification_attempt_ids" not in dispatch:
        return ()
    attempts = dispatch["qualification_attempt_ids"]
    if Path(evaluation["root"]).name != "qualification-evaluations":
        raise ValueError("Explicit qualification dispatch requires /qualification-evaluations")
    if not isinstance(attempts, list) or not attempts or any(not isinstance(uid, str) for uid in attempts):
        raise ValueError("Qualification dispatch requires a nonempty explicit list of attempt IDs")
    slots = {f"{task}#attempt-{attempt}" for task in evaluation["task_ids"] for attempt in range(len(SEEDS))}
    if len(set(attempts)) != len(attempts) or not set(attempts) < slots:
        raise ValueError("Qualification dispatch must select distinct slots from, but not all of, the frozen ledger")
    return tuple(attempts)


def _dispatch_scope(configuration, evaluation, job_id):
    mount, directory, seconds = validate_dispatch(configuration, evaluation)
    job_directory = _local_path(directory / _label(job_id), mount)
    if job_directory != directory / job_id:
        raise ValueError("Dispatch job directory must not redirect to another job")
    return mount, job_directory, seconds


def _publish_once(directory, path, row):
    # The same small identity lock covers worker notifications and local freezing.
    with _locked(_local_path(directory / "identity.lock", directory)):
        if path.exists():
            if read_json(path) != row:
                raise ValueError(f"Frozen dispatch identity cannot be overwritten: {path}")
        else:
            write_json(path, row)


def notify_ready(configuration, evaluation, *, job_id, point_id, checkpoint_dir):
    """Write only point/job/HF/config identity after durable cloud enqueue."""
    _, directory, _ = _dispatch_scope(configuration, evaluation, job_id)
    frozen = _local_path(directory / "evaluation.json", directory)
    _publish_once(directory, frozen, evaluation)
    notification = {
        "point_id": _label(point_id),
        "job_id": _label(job_id),
        "checkpoint_dir": str(checkpoint_dir),
        "configuration": str(frozen),
    }
    _validate_notification(notification, evaluation, job_id, frozen)
    path = _local_path(directory / "ready" / f"{point_id}.json", directory)
    _publish_once(directory, path, notification)
    return path


def _validate_notification(row, evaluation, job_id, configuration):
    if set(row) != {"point_id", "job_id", "checkpoint_dir", "configuration"}:
        raise ValueError("Ready notifications may contain only point/job/HF/config identity")
    if row["job_id"] != job_id:
        return False
    point = _label(row["point_id"])
    if row["configuration"] != str(configuration):
        raise ValueError("Ready notification must identify the frozen evaluation configuration")
    checkpoint, owned = Path(row["checkpoint_dir"]), Path(evaluation["owned_root"])
    # These are cloud identities, not paths to inspect on the local machine.
    if not checkpoint.is_absolute() or ".." in checkpoint.parts or not checkpoint.is_relative_to(owned):
        raise ValueError("Ready notification HF identity escapes the configured owned namespace")
    if checkpoint.parent.name != "hf" or not checkpoint.name.startswith("step_"):
        raise ValueError("Ready notification must identify a native HF save directory")
    update = int(checkpoint.name.removeprefix("step_")) + 1
    attempts = qualification_attempt_ids(evaluation)
    if point.startswith("qualification."):
        if not attempts or update <= 0 or not point.endswith(f".{job_id}.HF{update}"):
            raise ValueError("Ready qualification must identify this job's explicitly enabled native HF point")
    elif attempts or update not in HF_UPDATES or not point.endswith(f".{job_id}.HF{update}"):
        raise ValueError("Ready notification must identify this job's frozen formal HF point")
    return True


class EvaluationWatcher:
    """Own local process handles and conservative per-point admission journals."""

    def __init__(self, config_path, configuration, job_id):
        if "KUBEBRAIN_RJOB_NAME" in os.environ:
            raise ValueError("Evaluation dispatch must run locally, never on an RJob worker")
        evaluation, config = read_json(configuration), read_json(config_path)
        self.mount, self.directory, self.poll_seconds = _dispatch_scope(configuration, evaluation, job_id)
        if Path(config["local_mount"]).resolve() != self.mount or Path.cwd().resolve() != self.mount:
            raise ValueError("Evaluation observer must run from the integration local_mount")
        _local_path(config_path, self.mount)
        self.job_id, self.evaluation = _label(job_id), evaluation
        self.configuration = _local_path(self.directory / "evaluation.json", self.directory)
        self.config_path = _local_path(self.directory / "integration.json", self.directory)
        _publish_once(self.directory, self.configuration, evaluation)
        _publish_once(self.directory, self.config_path, config)
        self.children, self.rows, self.invalid_paths, self.checked_points = {}, {}, set(), set()

    def _record(self, point, row):
        self.rows[point] = row
        try:
            write_json(_local_path(self.directory / "dispatch" / f"{_label(point)}.json", self.directory), row)
        except Exception:
            self.invalid_paths.add(self.directory / "dispatch" / f"{point}.json")
            logger.exception("SWE dispatch journal is unverified for %s; training continues", point)

    def _receipt(self, path, point):
        _local_path(path, self.directory)
        if not path.exists():
            return None
        row = read_json(path)
        if (
            row["point"] != point
            or row["configuration"] != str(self.configuration)
            or row["config"] != str(self.config_path)
        ):
            raise ValueError("Evaluation receipt belongs to another point or frozen configuration")
        return row

    def _launch(self, point, row):
        sequence = row.get("admission_check", 0) + 1
        receipt = _local_path(self.directory / "receipts" / f"{point}.admission-{sequence}.json", self.directory)
        if receipt.exists() or receipt.with_name(receipt.name + ".pending").exists():
            raise ValueError("An existing receipt or pending submission is not a safe retry")
        row = {"point_id": point, "status": "STARTING", "receipt": str(receipt), "admission_check": sequence}
        # Persist intent before Popen; a crash in the handoff is deliberately not retried.
        journal = _local_path(self.directory / "dispatch" / f"{point}.json", self.directory)
        write_json(journal, row)
        self.rows[point] = row
        self.checked_points.add(point)
        argv = [
            sys.executable,
            "-u",
            "-B",
            "-m",
            "tests.manual.agent_opd.submit_swe_evaluation",
            "--config",
            str(self.config_path),
            "--configuration",
            str(self.configuration),
            "--point",
            point,
            "--receipt",
            str(receipt),
            *[arg for uid in qualification_attempt_ids(self.evaluation) for arg in ("--qualification-attempt", uid)],
        ]
        log = _local_path(self.directory / "logs" / f"{point}.admission-{sequence}.log", self.directory)
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("x") as stream:
            child = subprocess.Popen(argv, cwd=self.mount, stdout=stream, stderr=subprocess.STDOUT)
        self.children[point] = (child, receipt)
        self._record(point, {**row, "pid": child.pid})

    def _scan(self, training_finished):
        for path in sorted((self.directory / "ready").glob("*.json")):
            if path in self.invalid_paths:
                continue
            point = None
            try:
                _local_path(path, self.directory)
                notification = read_json(path)
                if not _validate_notification(notification, self.evaluation, self.job_id, self.configuration):
                    continue
                point = notification["point_id"]
                if path.name != f"{point}.json":
                    raise ValueError("Notification filename disagrees with its point identity")
                if point in self.children:
                    continue
                if point not in self.rows:
                    journal = _local_path(self.directory / "dispatch" / f"{point}.json", self.directory)
                    self.rows[point] = read_json(journal) if journal.exists() else {}
                row = self.rows[point]
                if row.get("status") == "ADMISSION_DENIED" and (
                    not training_finished or point not in self.checked_points
                ):
                    receipt = Path(row["receipt"])
                    proof = self._receipt(receipt, point)
                    if not self._denied(proof, receipt, row["exit_code"]):
                        raise ValueError("Admission denial no longer proves no submission")
                elif row:
                    if row["status"] in ("STARTING", "ADMITTED"):
                        raise ValueError(
                            "Prior launcher handoff has no owned process handle; inspect, do not resubmit"
                        )
                    continue
                self._launch(point, row)
            except Exception as error:
                self.invalid_paths.add(path)
                if point is not None:
                    self._record(point, {**self.rows.get(point, {}), "status": "UNVERIFIED", "error": str(error)})
                logger.exception(
                    "SWE ready notification is unverified at %s; other points and training continue", path
                )

    @staticmethod
    def _denied(proof, receipt, exit_code):
        return (
            exit_code == 2
            and proof is not None
            and proof["job_id"] is None
            and proof["admission"]["submitted"] is False
            and proof["admission"]["admitted"] is False
            and not receipt.with_name(receipt.name + ".pending").exists()
        )

    def _poll_children(self):
        for point, (child, receipt) in list(self.children.items()):
            exit_code = child.poll()
            try:
                proof = self._receipt(receipt, point)
                row = self.rows[point]
                if exit_code is None:
                    if proof is not None and proof["admission"]["submitted"] is True and proof["job_id"]:
                        if row["status"] != "ADMITTED":
                            self._record(point, {**row, "status": "ADMITTED", "evaluation_job_id": proof["job_id"]})
                    continue
                if self._denied(proof, receipt, exit_code):
                    self._record(point, {**row, "status": "ADMISSION_DENIED", "exit_code": exit_code})
                elif proof is not None and proof["admission"]["submitted"] is True and proof["job_id"]:
                    self._record(
                        point,
                        {
                            **row,
                            "status": "EVALUATOR_EXITED",
                            "exit_code": exit_code,
                            "evaluation_job_id": proof["job_id"],
                        },
                    )
                else:
                    raise ValueError("Exited evaluator has no authoritative admission outcome; no automatic retry")
            except Exception as error:
                if self.rows[point].get("error") != str(error):
                    self._record(point, {**self.rows[point], "status": "UNVERIFIED", "error": str(error)})
                    logger.exception(
                        "SWE evaluator observation failed for %s; preserve its launcher while live", point
                    )
            finally:
                if exit_code is not None:
                    child.wait()
                    del self.children[point]

    def run(self, training_finished):
        lock = _local_path(self.directory / "watcher.lock", self.directory)
        with lock.open("a") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                while True:
                    finished = training_finished()
                    self._poll_children()
                    self._scan(finished)
                    if finished and not self.children:
                        break
                    time.sleep(self.poll_seconds)
            finally:
                # An observer error must not drop already-admitted local launchers.
                while self.children:
                    self._poll_children()
                    if self.children:
                        time.sleep(self.poll_seconds)
            summary = {
                "job_id": self.job_id,
                "training_terminal_observed": True,
                "points": self.rows,
                "unverified_paths": sorted(str(path) for path in self.invalid_paths),
            }
            write_json(_local_path(self.directory / "observer.json", self.directory), summary)
            if self.invalid_paths or any(
                row["status"] == "UNVERIFIED" or (row["status"] == "EVALUATOR_EXITED" and row["exit_code"] != 0)
                for row in self.rows.values()
            ):
                return 1
            return 2 if any(row["status"] == "ADMISSION_DENIED" for row in self.rows.values()) else 0


@dataclass
class _LocalObserver:
    thread: threading.Thread
    training_finished: threading.Event


def prepare_dispatch(config_path, config):
    """Create the base locally before a worker can create it; failures are soft gates."""
    try:
        configuration = config["checkpoint"]["hook_args"].get("swe_evaluation_configuration")
        if configuration is None:
            return
        if "KUBEBRAIN_RJOB_NAME" in os.environ:
            raise ValueError("Evaluation dispatch must run locally, never on an RJob worker")
        evaluation = read_json(configuration)
        mount, directory, _ = validate_dispatch(configuration, evaluation)
        if Path(config["local_mount"]).resolve() != mount or Path.cwd().resolve() != mount:
            raise ValueError("Evaluation observer must run from the integration local_mount")
        _local_path(config_path, mount)
        directory.mkdir(parents=True, exist_ok=True)
    except Exception:
        logger.exception("SWE evaluation dispatch directory could not be prepared; training continues")


def start_dispatch(config_path, config, job_id):
    """Start after actual job creation; failures are training soft gates."""
    try:
        configuration = config["checkpoint"]["hook_args"].get("swe_evaluation_configuration")
        if configuration is None:
            return None
        if read_json(config_path) != config:
            raise ValueError("Training integration configuration changed after submission")
        watcher = EvaluationWatcher(config_path, configuration, job_id)
        finished = threading.Event()

        def observe():
            try:
                result = watcher.run(finished.is_set)
                print("SWE_EVALUATION_OBSERVER_FINISHED", job_id, result, flush=True)
            except Exception:
                logger.exception("SWE evaluation observer failed for %s; training continues", job_id)

        thread = threading.Thread(target=observe, name=f"swe-evaluations-{job_id}", daemon=True)
        thread.start()
        return _LocalObserver(thread, finished)
    except Exception:
        logger.exception("SWE evaluation observer could not start for %s; training continues", job_id)
        return None


def finish_dispatch(observer):
    """Drain after native workers.wait() returns or raises, preserving child handles."""
    if observer is not None:
        observer.training_finished.set()
        observer.thread.join()


def _terminal_receipt(path, job_id):
    if not path.exists():
        return False
    row = read_json(path)
    if row["job"] != job_id or row["status"]["phase"] not in _TERMINAL_PHASES:
        raise ValueError("Training terminal receipt must identify this actual terminated job")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--configuration", type=Path, required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--trainer-receipt", type=Path, required=True)
    args = parser.parse_args()
    watcher = EvaluationWatcher(args.config, args.configuration, args.job)
    terminal = _local_path(args.trainer_receipt.with_suffix(".terminal.json"), watcher.mount)
    return watcher.run(lambda: _terminal_receipt(terminal, args.job))


if __name__ == "__main__":
    raise SystemExit(main())
