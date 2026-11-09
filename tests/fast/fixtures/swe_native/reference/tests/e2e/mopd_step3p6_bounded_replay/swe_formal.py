import json
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text())


def outcome(task, trajectory_path, result_path):
    trajectory, result = read(trajectory_path), read(result_path)
    if not isinstance(trajectory, dict) or not isinstance(result, dict):
        raise ValueError("native artifacts must be JSON objects")
    meta = trajectory.get("meta") or trajectory.get("metadata") or {}
    detail = result.get("detail")
    if (
        not isinstance(meta, dict)
        or meta.get("error_type")
        or result.get("instance_id") != task
        or not isinstance(detail, dict)
    ):
        raise ValueError("native trajectory or grader identity is unverified")
    if (
        result.get("status") not in ("resolved", "unresolved")
        or type(detail.get("resolved")) is not bool
    ):
        raise ValueError("native grader did not return a model outcome")
    if detail["resolved"] != (result["status"] == "resolved"):
        raise ValueError("native grader status and resolved disagree")
    if not isinstance(detail.get("tests_status"), dict) or not detail["tests_status"]:
        raise ValueError("native grader has no test summary")
    if (
        not isinstance(detail.get("tests_status_allcases"), dict)
        or not detail["tests_status_allcases"]
    ):
        raise ValueError("native grader has no individual test outcomes")
    return detail["resolved"]
