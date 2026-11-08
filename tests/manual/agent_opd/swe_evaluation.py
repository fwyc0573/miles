"""Durable, trainer-independent SWE evaluation and owned HF release.

The trainer calls ``enqueue_checkpoint`` after the existing Qwen packaging hook,
passing the observed native successful-update/publication record. An independent
worker calls ``evaluate`` with an admitted allocation and an async native runner.
No GPU is submitted here. Never feed this queue into EvalDispatcher's snapshot GC.
"""

import argparse
import asyncio
import contextlib
import fcntl
import hashlib
import json
import os
import re
import time
import uuid
from pathlib import Path

from tests.manual.agent_opd.rjob_budget import validate_allocation

SEEDS = (1729, 1730, 1731, 1732)
HF_UPDATES = (50, 100, 150, 200)
EVALUATION_SECONDS = 72 * 3600
SWE_COMMIT = "1af09e5f90f55f6fbce5f71efe7da0030a2e126e"


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    """Publish atomically, including directory durability before returning."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".partial")
    with temporary.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    descriptor = os.open(path.parent, os.O_DIRECTORY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@contextlib.contextmanager
def _locked(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def _label(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", value):
        raise ValueError("Identity must be a nonempty artifact filename")
    return value


def _file_inventory(path):
    files = []
    for file in sorted(path.rglob("*")):
        if file.is_symlink():
            raise ValueError("Owned HF must not contain symlinks")
        if file.is_file():
            stat = file.stat()
            files.append({"path": str(file.relative_to(path)), "bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns})
    return files


def benchmark_tasks(manifest_path, library_path):
    """Use manifest order, NOT the physical library's first 100 rows."""
    manifest = read_json(manifest_path)
    tasks = manifest["benchmark"]["task_ids"]
    if manifest["source_group"] != "swe" or len(tasks) != 500 or len(set(tasks)) != 500:
        raise ValueError("Need the original ordered 500-task SWE manifest")
    library = read_json(library_path)
    by_id = {row["instance_id"]: row for row in library}
    if len(library) != 500 or len(by_id) != 500 or set(by_id) != set(tasks):
        raise ValueError("Benchmark library must match the entire manifest")
    return tuple(_label(task) for task in tasks[:100])


class EvaluationStore:
    """One immutable point manifest, atomic slot results, and explicit reader leases."""

    def __init__(self, root, *, owned_root, protected_sources, reference_root, allocation_identity):
        self.root = Path(root).resolve()
        self.owned_root = Path(owned_root).resolve()
        self.protected_sources = tuple(Path(path).resolve() for path in protected_sources)
        self.reference_root = Path(reference_root).resolve()
        self.allocation_identity = dict(allocation_identity)

    def _point(self, point_id):
        return self.root / "points" / _label(point_id)

    def manifest(self, point_id):
        return read_json(self._point(point_id) / "manifest.json")

    def state(self, point_id):
        return read_json(self._point(point_id) / "state.json")

    def _owned_path(self, path, native_update):
        path = Path(path)
        resolved = path.resolve()
        if path.is_symlink() or not resolved.is_relative_to(self.owned_root) or resolved == self.owned_root:
            raise ValueError("HF deletion scope must be inside this task's owned root")
        if any(resolved.is_relative_to(source) or source.is_relative_to(resolved) for source in self.protected_sources):
            raise ValueError("Original and historical source weights are protected")
        checkpoint_index = native_update["checkpoint_index"]
        if type(checkpoint_index) is not int or checkpoint_index != native_update["successful_update"] - 1:
            raise ValueError("HF checkpoint index must match the native successful update")
        if resolved.parts[-2:] != ("hf", f"step_{checkpoint_index}"):
            raise ValueError("HF path must match the observed native successful-index save")
        return resolved

    def enqueue_checkpoint(self, *, point_id, checkpoint_dir, native_update, source, task_ids, configuration):
        """Return only after durable enqueue; no queue cap, GPU wait, or benchmark wait."""
        if type(native_update["successful_update"]) is not int or native_update["successful_update"] not in HF_UPDATES:
            raise ValueError("Native successful update is not an HF evaluation point")
        if type(native_update["rollout_id"]) is not int or native_update["rollout_id"] < 0:
            raise ValueError("Need the observed native rollout ID, not update minus one")
        if native_update["weight_version"] is None or not native_update["native_counters"]:
            raise ValueError("Native counters and published weight version are required")
        checkpoint = self._owned_path(checkpoint_dir, native_update)
        package = read_json(checkpoint / "qwen_text_export.json")
        if not (checkpoint / ".complete").is_file() or package.get("status") != "packaged":
            raise ValueError("Partial export cannot be enqueued")
        if package.get("run_kind") != "formal":
            raise ValueError("Only formal HF packages may enter a 400-attempt evaluation point")
        if (
            package.get("rollout_id") != native_update["rollout_id"]
            or package.get("checkpoint_index") != native_update["checkpoint_index"]
            or package.get("successful_update") != native_update["successful_update"]
            or package.get("weight_version") != native_update["weight_version"]
            or Path(package["source"]).resolve() != Path(source).resolve()
        ):
            raise ValueError("Packaging source/update/rollout/version identity disagrees with native publication")
        index = read_json(checkpoint / "model.safetensors.index.json")
        shards = set(index["weight_map"].values())
        if not shards or any(Path(name).name != name or not (checkpoint / name).is_file() for name in shards):
            raise ValueError("Exported shard index is incomplete")
        for name in ("config.json", "tokenizer.json", "tokenizer_config.json"):
            if not (checkpoint / name).is_file():
                raise ValueError(f"Export is missing {name}")
        return self._enqueue(point_id, checkpoint, native_update, task_ids, configuration, owned=True)

    def enqueue_baseline(self, *, point_id, source, task_ids, configuration):
        source = Path(source).resolve()
        if source not in self.protected_sources or not source.is_dir():
            raise ValueError("Baseline must use a registered, protected original model")
        return self._enqueue(point_id, source, None, task_ids, configuration, owned=False)

    def _enqueue(self, point_id, checkpoint, native_update, task_ids, configuration, *, owned):
        tasks = tuple(_label(task) for task in task_ids)
        if len(tasks) != 100 or len(set(tasks)) != 100:
            raise ValueError("Formal SWE evaluation requires 100 distinct manifest tasks")
        point = self._point(point_id)
        manifest = {
            "point_id": point_id,
            "checkpoint_dir": str(checkpoint),
            "owned": owned,
            "native_update": native_update,
            "task_ids": list(tasks),
            "seeds": list(SEEDS),
            "configuration": configuration,
            "files": _file_inventory(checkpoint) if owned else [],
        }
        with _locked(self.root / "queue.lock"), _locked(point / "lock"):
            for other in (self.root / "points").glob("*/manifest.json"):
                previous = read_json(other)
                if (
                    owned
                    and previous["owned"]
                    and previous["checkpoint_dir"] == str(checkpoint)
                    and previous["point_id"] != point_id
                ):
                    raise ValueError("An owned HF already belongs to another immutable evaluation point")
            target = point / "manifest.json"
            if target.exists():
                if read_json(target) != manifest:
                    raise ValueError("Evaluation identity is immutable")
            else:
                write_json(target, manifest)
            # A crash between manifest and state publication remains recoverable.
            if not (point / "state.json").exists():
                write_json(
                    point / "state.json",
                    {
                        "status": "QUEUED",
                        "first_started_at": None,
                        "deadline_at": None,
                        "readers": {},
                        "recoveries": [],
                    },
                )
        return point_id

    def queued(self):
        queued = []
        for path in sorted((self.root / "points").glob("*/manifest.json")):
            point_id = path.parent.name
            with _locked(path.parent / "lock"):
                if not (path.parent / "state.json").exists():
                    # Enqueue crashed between its two atomic publications; no reader started.
                    write_json(
                        path.parent / "state.json",
                        {
                            "status": "QUEUED",
                            "first_started_at": None,
                            "deadline_at": None,
                            "readers": {},
                            "recoveries": [],
                        },
                    )
                if self.state(point_id)["status"] == "QUEUED":
                    queued.append(point_id)
        return tuple(queued)

    def request(self, point_id, task_id, attempt):
        manifest = self.manifest(point_id)
        if task_id not in manifest["task_ids"] or type(attempt) is not int or attempt not in range(4):
            raise ValueError("Foreign SWE slot")
        return {
            "point_id": point_id,
            "task_id": task_id,
            "attempt": attempt,
            "seed": SEEDS[attempt],
            "uid": f"{task_id}#attempt-{attempt}",
            "scope": "formal_subset",
            "domain": "swe",
            "benchmark": "SWE-bench Verified",
        }

    def _ledger(self, point_id):
        # Reuse the source-backed four-attempt scorer, without importing the GPU runner.
        import sys

        if str(self.reference_root) not in sys.path:
            sys.path.insert(0, str(self.reference_root))
        from playground.users.ycfeng.MOPD.bounded_replay_evaluation import FourAttempts

        manifest = self.manifest(point_id)
        ledger = FourAttempts(manifest["task_ids"], seeds=SEEDS, scope="formal_subset", domain="swe")
        for path in sorted((self._point(point_id) / "results").glob("*.json")):
            row = read_json(path)
            request = row["request"]
            if request != self.request(point_id, request["task_id"], request["attempt"]):
                raise ValueError("Persisted result identity changed")
            ledger.record(request["task_id"], request["attempt"], success=row["success"], raw=row)
        return ledger

    def summary(self, point_id):
        return self._ledger(point_id).summarize()

    def record(self, point_id, request, *, success, raw):
        if request != self.request(point_id, request["task_id"], request["attempt"]) or type(success) is not bool:
            raise ValueError("Result identity or native boolean outcome is invalid")
        point = self._point(point_id)
        path = point / "results" / f"{request['task_id']}.{request['seed']}.json"
        with _locked(point / "lock"):
            if self.state(point_id)["status"] != "RUNNING":
                raise ValueError("Late completion after evaluation settlement")
            if path.exists():
                previous = read_json(path)
                if previous["request"] != request or previous["success"] != success or previous["raw"] != raw:
                    raise ValueError("Completed model outcomes cannot be rerolled or overwritten")
            else:
                write_json(
                    path,
                    {
                        "request": request,
                        "success": success,
                        "raw": raw,
                        "persisted_at": time.time(),
                        "deadline_at": self.state(point_id)["deadline_at"],
                    },
                )

    def infra_failure(self, point_id, request, error):
        point = self._point(point_id)
        with _locked(point / "lock"):
            write_json(
                point / "failures" / f"{request['task_id']}.{request['seed']}.{uuid.uuid4().hex}.json",
                {"request": request, "observed_at": time.time(), "error": error},
            )

    def reader_enter(self, point_id, reader_id, evidence):
        point = self._point(point_id)
        with _locked(point / "lock"):
            state = self.state(point_id)
            if state["status"] not in ("QUEUED", "RUNNING", "INCOMPLETE"):
                raise ValueError("Evaluation no longer admits HF readers")
            if reader_id in state["readers"]:
                raise ValueError("Reader identities cannot be reused")
            state["readers"][reader_id] = {"status": "RUNNING", "started_at": time.time(), "start": evidence}
            write_json(point / "state.json", state)

    def reader_exit(self, point_id, reader_id, evidence):
        if not evidence:
            raise ValueError("Reader exit requires actual process/platform evidence")
        point = self._point(point_id)
        with _locked(point / "lock"):
            state = self.state(point_id)
            state["readers"][reader_id].update(status="EXITED", exit=evidence)
            write_json(point / "state.json", state)

    def start(self, point_id, *, allocation, now=None):
        """Called when the independently admitted worker actually begins evaluation."""
        if type(allocation.get("eval_gpus")) is not int:
            raise ValueError("Evaluation requires a positive integer GPU allocation")
        validate_allocation(allocation, requested_gpus=allocation["eval_gpus"], expected=self.allocation_identity)
        point = self._point(point_id)
        now = time.time() if now is None else now
        with _locked(point / "lock"):
            state = self.state(point_id)
            if state["status"] != "QUEUED":
                raise ValueError("Evaluation needs enqueue or diagnosed missing-slot recovery")
            if state["first_started_at"] is None:
                state.update(first_started_at=now, deadline_at=now + EVALUATION_SECONDS)
            if now >= state["deadline_at"]:
                state["status"] = "EXPIRED"
                write_json(point / "state.json", state)
                return False
            state.update(status="RUNNING", allocation=allocation)
            write_json(point / "state.json", state)
        return True

    def resume(self, point_id, *, diagnosis, remedy, now=None):
        if not diagnosis or not remedy:
            raise ValueError("Missing slots may resume only after infrastructure RCA and repair")
        point = self._point(point_id)
        now = time.time() if now is None else now
        with _locked(point / "lock"):
            state = self.state(point_id)
            if state["status"] not in ("RUNNING", "INCOMPLETE"):
                raise ValueError("Only interrupted/incomplete evaluations may resume")
            if any(reader["status"] != "EXITED" for reader in state["readers"].values()):
                raise ValueError("Interrupted readers must be proven exited before recovery")
            state["recoveries"].append({"at": now, "diagnosis": diagnosis, "remedy": remedy})
            state["status"] = "EXPIRED" if now >= state["deadline_at"] else "QUEUED"
            write_json(point / "state.json", state)
        return state["status"]

    def settle(self, point_id, *, now=None):
        point = self._point(point_id)
        now = time.time() if now is None else now
        with _locked(point / "lock"):
            summary = self.summary(point_id)
            # The complete archive is durable before any release decision.
            write_json(point / "evaluation.json", summary)
            state = self.state(point_id)
            state["status"] = (
                "COMPLETE"
                if summary["status"] == "COMPLETE"
                else "EXPIRED" if now >= state["deadline_at"] else "INCOMPLETE"
            )
            write_json(point / "state.json", state)
        return summary

    def _validate_native_archive(self, point_id):
        point = self._point(point_id)
        for path in (point / "results").glob("*.json"):
            raw = read_json(path)["raw"]
            for artifact in raw.get("native_artifacts", {}).values():
                artifact_path = Path(artifact["path"]).resolve()
                if (
                    not artifact_path.is_relative_to(point)
                    or hashlib.sha256(artifact_path.read_bytes()).hexdigest() != artifact["sha256"]
                ):
                    raise ValueError("Archived native grader/trajectory/config bytes changed")

    def release(self, point_id):
        """Delete only inventoried new HF files after archive and every reader exit."""
        point = self._point(point_id)
        with _locked(point / "lock"):
            manifest, state = self.manifest(point_id), self.state(point_id)
            if not manifest["owned"]:
                return {"status": "PROTECTED_SOURCE", "deleted_bytes": 0}
            if state["status"] == "RELEASED":
                return read_json(point / "release.json")
            if state["status"] not in ("COMPLETE", "RELEASING") or self.summary(point_id)["status"] != "COMPLETE":
                raise ValueError("Incomplete HF must be retained")
            if read_json(point / "evaluation.json") != json.loads(json.dumps(self.summary(point_id))):
                raise ValueError("Complete result archive must match the slot ledger")
            if any(reader["status"] != "EXITED" for reader in state["readers"].values()):
                raise ValueError("All HF readers must exit before deletion")
            self._validate_native_archive(point_id)
            hf = self._owned_path(manifest["checkpoint_dir"], manifest["native_update"])
            receipt_path = point / "release.json"
            receipt = (
                read_json(receipt_path)
                if receipt_path.exists()
                else {
                    "status": "RELEASING",
                    "checkpoint_dir": str(hf),
                    "files": manifest["files"],
                    "deleted_files": [],
                    "deleted_bytes": 0,
                    "unlinking": None,
                }
            )
            if receipt["checkpoint_dir"] != str(hf) or receipt["files"] != manifest["files"]:
                raise ValueError("Release receipt must retain the original owned-file inventory")
            for item in receipt["files"]:
                relative = Path(item["path"])
                if relative.is_absolute() or ".." in relative.parts or not (hf / relative).resolve().is_relative_to(hf):
                    raise ValueError("Release file escaped its owned HF directory")
            current = {item["path"]: item for item in _file_inventory(hf)}
            expected = {item["path"]: item for item in receipt["files"] if item["path"] not in receipt["deleted_files"]}
            if any(item != expected.get(name) for name, item in current.items()):
                raise ValueError("Owned HF changed or contains unowned files; do not delete")
            if state["status"] == "COMPLETE" and current != expected:
                raise ValueError("Owned HF disappeared before release")
            missing = set(expected) - set(current)
            if missing and missing != {receipt["unlinking"]}:
                raise ValueError("Unexplained missing HF files cannot be counted as our deleted bytes")
            state["status"] = "RELEASING"
            write_json(point / "state.json", state)
            write_json(receipt_path, receipt)
            for item in receipt["files"]:
                if item["path"] in receipt["deleted_files"]:
                    continue
                # Persist one unlink intent so recovery cannot count unrelated
                # missing files as this release's deleted bytes.
                receipt["unlinking"] = item["path"]
                write_json(receipt_path, receipt)
                (hf / item["path"]).unlink(missing_ok=True)
                receipt["deleted_files"].append(item["path"])
                receipt["deleted_bytes"] += item["bytes"]
                receipt["unlinking"] = None
                write_json(receipt_path, receipt)
            for directory in sorted((path for path in hf.rglob("*") if path.is_dir()), reverse=True):
                directory.rmdir()
            if hf.exists():
                hf.rmdir()
            receipt["status"] = "RELEASED"
            write_json(receipt_path, receipt)
            state["status"] = "RELEASED"
            write_json(point / "state.json", state)
            return receipt


async def evaluate(store, point_id, *, runner, allocation):
    """Four independent seed workers, each with native concurrency one.

    ``runner(request, deadline_at)`` returns {success: bool, raw: native evidence}.
    It MUST reap all owned children on cancellation before returning/raising.
    Infrastructure errors stay missing; a completed native model failure is False.
    """
    if not store.start(point_id, allocation=allocation):
        return store.summary(point_id)
    reader = "evaluator-" + uuid.uuid4().hex
    store.reader_enter(point_id, reader, {"pid": os.getpid(), "allocation": allocation})
    deadline = store.state(point_id)["deadline_at"]
    missing = set(store.summary(point_id)["missing_attempt_ids"])
    tasks = store.manifest(point_id)["task_ids"]

    async def seed_worker(attempt):
        for task in tasks:
            request = store.request(point_id, task, attempt)
            if request["uid"] not in missing:
                continue
            remaining = deadline - time.time()
            if remaining <= 0:
                return
            try:
                outcome = await asyncio.wait_for(runner(request, deadline), timeout=remaining)
                store.record(point_id, request, success=outcome["success"], raw=outcome["raw"])
            except Exception as error:
                store.infra_failure(point_id, request, {"type": type(error).__name__, "message": str(error)})
            await asyncio.sleep(0)

    workers = [asyncio.create_task(seed_worker(attempt)) for attempt in range(4)]
    completion = asyncio.gather(*workers, return_exceptions=True)
    try:
        results = await asyncio.shield(completion)
        for result in results:
            if isinstance(result, BaseException):
                raise result
    finally:
        # Shield prevents parent cancellation from cancelling workers through
        # gather. Cancel each worker once, then join its native child cleanup.
        for worker in workers:
            if not worker.done():
                worker.cancel()
        await completion
        store.reader_exit(point_id, reader, {"workers_finished": True, "at": time.time()})
        store.settle(point_id)
    return store.summary(point_id)


def store_from_config(configuration):
    return EvaluationStore(
        configuration["root"],
        owned_root=configuration["owned_root"],
        protected_sources=configuration["protected_sources"],
        reference_root=configuration["reference_root"],
        allocation_identity=configuration["allocation_identity"],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configuration", required=True)
    parser.add_argument("--point")
    parser.add_argument("--action", choices=("queue", "summary", "release", "run"), required=True)
    args = parser.parse_args()
    configuration = read_json(args.configuration)
    store = store_from_config(configuration)
    if args.action == "queue":
        result = store.queued()
    elif args.action == "summary":
        result = store.summary(args.point)
    elif args.action == "release":
        result = store.release(args.point)
    else:
        from tests.manual.agent_opd.swe_native_evaluation import NativeSweRunner

        runner = NativeSweRunner(store, args.point, configuration["runtime"])
        result = asyncio.run(evaluate(store, args.point, runner=runner, allocation=configuration["allocation"]))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
