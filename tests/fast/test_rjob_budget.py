"""Admission regressions for pending roles, pagination and hardware identity."""

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from tests.manual.agent_opd.rjob_budget import (
    admission_snapshot,
    committed_jobs,
    policy_admission_snapshot,
    validate_allocation,
)


def _job(name, phase, *, roles=(8, 2), replicas=1, hardware="H200", owner="owner", preemptible="no"):
    return {
        "metadata": {"name": name, "labels": {
            "kubebrain.brainpp.cn/creator": owner,
            "quotagroup.brainpp.cn/preemptible": preemptible,
        }},
        "status": {"phase": phase},
        "spec": {"taskSpecs": {
            str(i): {"replicas": replicas, "positiveTags": [hardware], "template": {"spec": {
                "containers": [{"resources": {"requests": {"nvidia.com/gpu": str(gpus)}}}],
            }}} for i, gpus in enumerate(roles)
        }},
    }


def test_pending_starting_and_stopping_keep_every_role_committed():
    jobs = [_job(phase, phase) for phase in ("Pending", "Starting", "Running", "Stopping")]
    jobs += [_job(phase, phase) for phase in ("Succeeded", "Failed", "Stopped", "Terminated", "Deleted")]
    jobs += [_job("other-owner", "Running", owner="other"), _job("preemptible", "Running", preemptible="yes")]
    jobs += [_job("other-hardware", "Running", hardware="H800")]
    rows = committed_jobs(jobs, creator="owner", gpu_tag="H200")
    assert {r["name"] for r in rows} == {"Pending", "Starting", "Running", "Stopping"}
    assert sum(r["gpus"] for r in rows) == 40
    assert all(r["roles"] == {"0": 8, "1": 2} for r in rows)


def test_native_replica_and_init_gpu_requests_are_counted():
    job = _job("replicated", "Pending", roles=(2,), replicas=3)
    pod = job["spec"]["taskSpecs"]["0"]["template"]["spec"]
    pod["initContainers"] = [{"resources": {"requests": {"nvidia.com/gpu": "4"}}}]
    assert committed_jobs([job], creator="owner", gpu_tag="H200")[0]["gpus"] == 12
    with pytest.raises(ValueError, match="Cannot classify"):
        committed_jobs([_job("unknown", "Running", hardware="generic")], creator="owner", gpu_tag="H200")
    assert committed_jobs([_job("cpu", "Pending", roles=(0,), hardware="generic")], creator="owner", gpu_tag="H200") == []


@pytest.mark.parametrize("requested,admitted", [(16, True), (17, False)])
def test_all_pages_contribute_to_the_ceiling(requested, admitted):
    calls = []

    def listing(**kwargs):
        calls.append(kwargs)
        if kwargs["_continue"] is None:
            return {"items": [_job("first", "Running", replicas=3)], "metadata": {"continue": "next-page"}}
        assert kwargs["_continue"] == "next-page"
        return {"items": [_job("second", "Pending")], "metadata": {}}

    client = SimpleNamespace(api=SimpleNamespace(list_namespaced_custom_object=listing),
                             group="native", version="v1", namespace="test", plural="rjobs")
    result = admission_snapshot(client, creator="owner", gpu_tag="H200", requested_gpus=requested, ceiling=56, timeout=20)
    assert result["committed_gpus"] == 40
    assert result["admitted"] is admitted
    assert len(calls) == 2 and all(call["_request_timeout"] == 20 for call in calls)


POLICY = {
    "task_id": "swe-task", "task_annotation": "miles.ycfeng/task", "personal_nonpreemptible_gpus": 56,
    "temporary_task_allocation": {"expires_at": "2026-11-08T21:00:00+00:00", "nonpreemptible_gpus": 64},
}
BEFORE_EXPIRY = datetime(2026, 11, 8, 20, 59, 59, tzinfo=timezone.utc)
AT_EXPIRY = datetime(2026, 11, 8, 21, 0, 0, tzinfo=timezone.utc)
IDENTITY = {"task_id": POLICY["task_id"], "creator": "owner", "gpu_tag": "H200"}


def _client(items):
    def listing(**kwargs):
        return {"items": items, "metadata": {}}
    return SimpleNamespace(api=SimpleNamespace(list_namespaced_custom_object=listing),
                           group="native", version="v1", namespace="test", plural="rjobs")


def _owned(job):
    job["metadata"]["annotations"] = {POLICY["task_annotation"]: POLICY["task_id"]}
    return job


@pytest.mark.parametrize("requested,preemptible", [(16, False), (17, True)])
def test_task_window_ignores_other_tasks_and_selects_overflow_preemption(requested, preemptible):
    jobs = [_job("other-task", "Running", roles=(72,)), _owned(_job("training", "Running", roles=(40,))),
            _owned(_job("queued-eval", "Pending", roles=(8,))),
            _owned(_job("preemptible-eval", "Running", roles=(20,), preemptible="yes")),
            _owned(_job("done", "Succeeded", roles=(10,)))]
    receipt = policy_admission_snapshot(_client(jobs), policy=POLICY, creator="owner", gpu_tag="H200",
                                        requested_gpus=requested, timeout=20, now=BEFORE_EXPIRY)
    assert receipt["admitted"] and receipt["scope"] == "task"
    assert receipt["committed_gpus"] == 48 and receipt["ceiling_gpus"] == 64
    assert receipt["preemptible"] is preemptible
    receipt.update(submitted=True, job="new-eval")
    validate_allocation({"job_id": "new-eval", "admission": receipt}, requested_gpus=requested, expected=IDENTITY)


@pytest.mark.parametrize("other_gpus,admitted", [(40, True), (72, False)])
def test_exact_expiry_restores_personal_admission(other_gpus, admitted):
    jobs = [_job("other-task", "Running", roles=(other_gpus,)), _owned(_job("swe", "Running"))]
    receipt = policy_admission_snapshot(_client(jobs), policy=POLICY, creator="owner", gpu_tag="H200",
                                        requested_gpus=1, timeout=20, now=AT_EXPIRY)
    assert receipt["scope"] == "personal" and receipt["ceiling_gpus"] == 56
    assert receipt["admitted"] is admitted and receipt["preemptible"] is False
    assert receipt["committed_gpus"] == other_gpus + 10


def test_inventory_read_crossing_expiry_rechecks_personal_jobs(monkeypatch):
    from tests.manual.agent_opd import rjob_budget

    class Clock(datetime):
        current = BEFORE_EXPIRY

        @classmethod
        def now(cls, tz=None):
            return cls.current

    calls = []

    def listing(**kwargs):
        calls.append(kwargs)
        Clock.current = AT_EXPIRY
        return {"items": [_job("other-task", "Running", roles=(72,))], "metadata": {}}

    monkeypatch.setattr(rjob_budget, "datetime", Clock)
    client = _client([])
    client.api.list_namespaced_custom_object = listing
    receipt = policy_admission_snapshot(client, policy=POLICY, creator="owner", gpu_tag="H200",
                                        requested_gpus=1, timeout=20)
    assert receipt["scope"] == "personal" and not receipt["admitted"]
    assert receipt["committed_gpus"] == 72 and len(calls) == 2


def test_allocation_validates_job_resources_policy_and_preemption():
    receipt = policy_admission_snapshot(_client([]), policy=POLICY, creator="owner", gpu_tag="H200",
                                        requested_gpus=2, timeout=20, now=BEFORE_EXPIRY)
    receipt.update(submitted=True, job="gpu-eval")
    allocation = {"job_id": "gpu-eval", "admission": receipt}
    validate_allocation(allocation, requested_gpus=2, expected=IDENTITY)
    for changes in ({"job": "other-job"}, {"submitted": False}, {"requested_gpus": 1},
                    {"preemptible": True}, {"ceiling_gpus": 65}, {"scope": "personal"},
                    {"creator": "other-owner"}, {"gpu_tag": "H800"}, {"policy": POLICY | {"task_id": "other"}}):
        with pytest.raises(ValueError):
            validate_allocation(allocation | {"admission": receipt | changes}, requested_gpus=2, expected=IDENTITY)
    # No current-clock expiry check: the user's admitted jobs may finish later.
    expired_receipt = receipt | {"evaluated_at": AT_EXPIRY.isoformat(), "ceiling_gpus": 56, "scope": "personal"}
    validate_allocation(allocation | {"admission": expired_receipt}, requested_gpus=2, expected=IDENTITY)
