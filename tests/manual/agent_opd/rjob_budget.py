"""Count personal or task-scoped GPU commitments before a new RJob submission.

Uses the native Python client's paginated RJob API. An admission lock belongs
to the caller and must cover this read and the subsequent backend submission.
"""

from datetime import datetime, timezone


_TERMINAL_PHASES = frozenset({"Succeeded", "Failed", "Stopped", "Terminated", "Deleted"})
_GPU_TAGS = frozenset({"H200", "H800", "B300"})
_CREATOR = "kubebrain.brainpp.cn/creator"
_PREEMPTIBLE = "quotagroup.brainpp.cn/preemptible"


def _pod_gpus(spec: dict) -> int:
    def requested(container):
        return int(container.get("resources", {}).get("requests", {}).get("nvidia.com/gpu", 0))

    running = sum(requested(container) for container in spec["containers"])
    initialization = max((requested(container) for container in spec.get("initContainers", [])), default=0)
    return max(running, initialization)


def committed_jobs(items: list[dict], *, creator: str, gpu_tag: str, task_annotation: tuple | None = None) -> list[dict]:
    if gpu_tag not in _GPU_TAGS:
        raise ValueError(f"Unclassified GPU tag: {gpu_tag}")
    result = []
    for job in items:
        labels = job["metadata"]["labels"]
        phase = job.get("status", {}).get("phase")
        if labels.get(_CREATOR) != creator or labels.get(_PREEMPTIBLE) == "yes" or phase in _TERMINAL_PHASES:
            continue
        if task_annotation is not None:
            key, value = task_annotation
            if job["metadata"].get("annotations", {}).get(key) != value:
                continue
        roles = {}
        for role, task in job["spec"]["taskSpecs"].items():
            count = _pod_gpus(task["template"]["spec"]) * task["replicas"]
            if count == 0:
                continue
            hardware = _GPU_TAGS.intersection(task.get("positiveTags") or [])
            if len(hardware) != 1:
                raise ValueError(f"Cannot classify GPU commitment for {job['metadata']['name']}/{role}")
            if gpu_tag in hardware:
                roles[role] = count
        if roles:
            result.append({"name": job["metadata"]["name"], "phase": phase, "roles": roles, "gpus": sum(roles.values())})
    return result


def admission_snapshot(
    client, *, creator: str, gpu_tag: str, requested_gpus: int, ceiling: int, timeout: float,
    task_annotation: tuple | None = None,
) -> dict:
    if requested_gpus < 0 or ceiling < 0 or timeout <= 0:
        raise ValueError("Invalid admission request, ceiling or API timeout")
    jobs, continuation = [], None
    while True:
        page = client.api.list_namespaced_custom_object(
            group=client.group, version=client.version, namespace=client.namespace, plural=client.plural,
            label_selector=f"{_CREATOR}={creator}", limit=100, _continue=continuation, _request_timeout=timeout,
        )
        jobs.extend(committed_jobs(page["items"], creator=creator, gpu_tag=gpu_tag, task_annotation=task_annotation))
        continuation = page["metadata"].get("continue")
        if not continuation:
            break
    committed = sum(job["gpus"] for job in jobs)
    return {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "creator": creator, "gpu_tag": gpu_tag, "nonterminal_jobs": jobs,
        "committed_gpus": committed, "requested_gpus": requested_gpus, "ceiling_gpus": ceiling,
        "admitted": committed + requested_gpus <= ceiling,
    }


def policy_admission_snapshot(client, *, policy: dict, creator: str, gpu_tag: str, requested_gpus: int,
                              timeout: float, now: datetime | None = None) -> dict:
    """Select task-window preemption or the personal limit from a fresh API view.

    The expiry controls new submissions only. Already admitted jobs continue;
    a job crossing the task ceiling is submitted wholly as preemptible.
    """
    fixed_time = now is not None
    now = datetime.now(timezone.utc) if now is None else now
    window = policy["temporary_task_allocation"]
    expires = datetime.fromisoformat(window["expires_at"])
    if now.utcoffset() is None or expires.utcoffset() is None:
        raise ValueError("GPU admission timestamps must include a timezone")
    task_scope = now < expires
    snapshot = admission_snapshot(
        client, creator=creator, gpu_tag=gpu_tag, requested_gpus=requested_gpus, timeout=timeout,
        ceiling=window["nonpreemptible_gpus"] if task_scope else policy["personal_nonpreemptible_gpus"],
        task_annotation=(policy["task_annotation"], policy["task_id"]) if task_scope else None,
    )
    now = now if fixed_time else datetime.fromisoformat(snapshot["observed_at"])
    if task_scope and now >= expires:
        task_scope = False
        snapshot = admission_snapshot(
            client, creator=creator, gpu_tag=gpu_tag, requested_gpus=requested_gpus, timeout=timeout,
            ceiling=policy["personal_nonpreemptible_gpus"],
        )
        now = datetime.fromisoformat(snapshot["observed_at"])
    snapshot.update(scope="task" if task_scope else "personal", policy=policy, evaluated_at=now.isoformat(),
                    preemptible=task_scope and not snapshot["admitted"])
    if task_scope:
        snapshot["admitted"] = True
    return snapshot


def validate_allocation(allocation: dict, *, requested_gpus: int, expected: dict) -> None:
    """Bind an evaluation reader to its actual, admitted RJob receipt."""
    admission = allocation.get("admission")
    if not isinstance(admission, dict):
        raise ValueError("Evaluation requires a submitted GPU admission receipt")
    if (requested_gpus <= 0 or admission.get("submitted") is not True or admission.get("admitted") is not True
            or not allocation.get("job_id") or admission.get("job") != allocation["job_id"]
            or type(admission.get("requested_gpus")) is not int or admission["requested_gpus"] < requested_gpus
            or type(admission.get("committed_gpus")) is not int or admission["committed_gpus"] < 0
            or type(admission.get("ceiling_gpus")) is not int or admission["ceiling_gpus"] < 0
            or type(admission.get("preemptible")) is not bool
            or admission.get("creator") != expected["creator"] or admission.get("gpu_tag") != expected["gpu_tag"]):
        raise ValueError("Evaluation requires a matching submitted GPU admission receipt")
    policy = admission["policy"]
    if policy.get("task_id") != expected["task_id"]:
        raise ValueError("GPU admission receipt belongs to a different task")
    window = policy["temporary_task_allocation"]
    observed = datetime.fromisoformat(admission["evaluated_at"])
    expires = datetime.fromisoformat(window["expires_at"])
    if observed.utcoffset() is None or expires.utcoffset() is None:
        raise ValueError("GPU admission timestamps must include a timezone")
    task_scope = observed < expires
    expected_scope = "task" if task_scope else "personal"
    ceiling = window["nonpreemptible_gpus"] if task_scope else policy["personal_nonpreemptible_gpus"]
    over_limit = admission["committed_gpus"] + admission["requested_gpus"] > ceiling
    if (admission.get("scope") != expected_scope or admission["ceiling_gpus"] != ceiling
            or admission["preemptible"] != (task_scope and over_limit) or (not task_scope and over_limit)):
        raise ValueError("GPU admission receipt violates its recorded allocation policy")
