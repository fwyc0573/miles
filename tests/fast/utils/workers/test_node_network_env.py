"""Replay heterogeneous H800 platform environments through the native launch path."""

import argparse
import asyncio
import json
import os
import shlex
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from ray._private.runtime_env.context import RuntimeEnvContext
from ray.core.generated.common_pb2 import Language
from ray.runtime_env.runtime_env import _merge_runtime_env
from tests.fast.fixtures.args_fixtures import parser_defaults
from tests.fast.ray.rollout.conftest import make_args
from tests.fast.test_qwen35_pair_worker import student_node
from tests.fast.utils.workers.conftest import worker_manager_args
from tests.manual.agent_opd import run_qwen35_opd as native
from tests.manual.agent_opd import run_swe_opd as swe

from miles.ray.specs.inference import InferenceEngineSpec
from miles.utils.args.runtime import AllConfig
from miles.utils.external_utils.command_utils.base_backend import BaseCommandBackend
from miles.utils.external_utils.command_utils.ray_backend import backend as ray_backend
from miles.utils.workers import command_actor, process_utils
from miles.utils.workers.command_actor import CommandActor
from miles.utils.workers.ray_worker_manager import RayWorkerManager
from miles.utils.workers.types import WorkerCommBackend

__all__ = ["student_node"]

# Selected platform values captured for exp-1109-181120-274261 on 2026-11-09.
_HEAD_HCAS = "=mlx5_0,mlx5_1,mlx5_2,mlx5_3,mlx5_4,mlx5_6,mlx5_7,mlx5_8"
_RANK_TWO_HCAS = "=mlx5_2,mlx5_3,mlx5_1,mlx5_0,mlx5_4,mlx5_6,mlx5_8,mlx5_7"
_NETWORK_ENV = {
    "NCCL_SOCKET_IFNAME": "ens20np0",
    "NCCL_IB_HCA": _HEAD_HCAS,
    "NCCL_IB_GID_INDEX": "3",
    "NVSHMEM_BOOTSTRAP_UID_SOCK_IFNAME": "ens20np0",
    "NVSHMEM_HCA_PE_MAPPING": "mlx5_0:1:1,mlx5_1:1:1,mlx5_2:1:1,mlx5_3:1:1,mlx5_4:1:1,mlx5_6:1:1,mlx5_7:1:1,mlx5_8:1:1",
}
_RANK_TWO_ENV = {
    **_NETWORK_ENV,
    "NCCL_SOCKET_IFNAME": "ens22np0",
    "NCCL_IB_HCA": _RANK_TWO_HCAS,
    "NVSHMEM_BOOTSTRAP_UID_SOCK_IFNAME": "ens22np0",
    "NVSHMEM_HCA_PE_MAPPING": "mlx5_2:1:1,mlx5_3:1:1,mlx5_1:1:1,mlx5_0:1:1,mlx5_4:1:1,mlx5_6:1:1,mlx5_8:1:1,mlx5_7:1:1",
}
_NCCL_CONTROLS = {
    "NCCL_NVLS_ENABLE": "0",
    "NCCL_IB_TC": "186",
    "NCCL_IB_FIFO_TC": "192",
    "NCCL_IB_PCI_RELAXED_ORDERING": "1",
    "NCCL_IB_DISABLE": "0",
    "NCCL_IB_QPS_PER_CONNECTION": "8",
    "NCCL_IB_TIMEOUT": "21",
    "NCCL_IB_RETRY_CNT": "7",
    "NCCL_MIN_NCHANNELS": "8",
    "NCCL_MAX_NCHANNELS": "8",
    "SGLANG_DETERMINISTIC_NCCL_NCHANNELS": "8",
}
_DETERMINISM = {
    "NCCL_MIN_NCHANNELS": "8",
    "NCCL_MAX_NCHANNELS": "8",
    "SGLANG_DETERMINISTIC_NCCL_NCHANNELS": "8",
    "NVTE_ALLOW_NONDETERMINISTIC_ALGO": "0",
    "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
}


@pytest.mark.parametrize("student_node", [(4, "H800")], indirect=True)
@pytest.mark.parametrize("network", ["heterogeneous", "uniform", "single"])
def test_native_submission_to_engine_subprocess_keeps_node_network(
    student_node, fake_ray_cluster, monkeypatch, network
):
    node = student_node
    # The shared fixture caches parser defaults; do not initialize it from this
    # run's SWE hook argv or leave those custom fields in unrelated later tests.
    with monkeypatch.context() as defaults:
        defaults.setattr(sys, "argv", ["test"])
        parser_defaults()
    if network == "single":
        node.args.student_nodes = 1
        monkeypatch.setenv("KUBEBRAIN_REPLICA_TOTAL", "1")
    for key in tuple(os.environ):
        if key.startswith(("NCCL_", "NVSHMEM_", "SGLANG_DETERMINISTIC_")):
            monkeypatch.delenv(key)
    for key, value in {**_NETWORK_ENV, **_NCCL_CONTROLS}.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("MILES_SCRIPT_ENABLE_RAY_SUBMIT", "1")
    monkeypatch.setattr(
        native.U.ExecuteTrainConfig, "create_backend", lambda config: ray_backend.RayCommandBackend(config)
    )
    monkeypatch.setattr(BaseCommandBackend, "exec_command_cpu", lambda *args, **kwargs: None)
    submissions = []
    monkeypatch.setattr(ray_backend, "run_ray_job", lambda **kwargs: submissions.append(kwargs))

    recipe = (
        Path(__file__).resolve().parents[4]
        / "task_memory/task_2026-11-08_qwen35_swe_full_r256/integration_config.json"
    )
    config = json.loads(recipe.read_text())
    config.update(
        context_tokens=131072,
        prompt_tokens=114688,
        response_tokens=16384,
        protocol="r256",
        run_root=str(node.args.output_root),
        shared_dir=str(node.args.shared_dir),
        worker_local_root=str(node.args.local_root),
        startup_timeout=node.args.startup_timeout,
        gpu_tag=node.args.gpu_type,
        megatron_path=node.args.megatron_path,
    )
    config["rollout_num_gpus"] = node.args.student_nodes * node.args.gpus_per_node
    config["pairs"]["A"]["student"].update(nodes=node.args.student_nodes, tp_size=4, engine_gpus=4)
    pool_gpus = [8] if network == "single" else [8, 24]
    config["sglang_config"] = native.U.encode_pseudo_file(
        json.dumps(
            {
                "sglang": [
                    {
                        "name": "default",
                        "server_groups": [
                            {"worker_type": "regular", "num_gpus": gpus, "num_gpus_per_engine": 4}
                            for gpus in pool_gpus
                        ],
                    }
                ]
            }
        )
    )
    swe._train(config, "A", "http://teacher:30000/generate")
    assert len(submissions) == 1
    submission = submissions[0]
    submitted = submission["runtime_env"]["env_vars"]
    assert {key: submitted[key] for key in _DETERMINISM} == _DETERMINISM

    parser = argparse.ArgumentParser(add_help=False)
    argv = shlex.split(submission["entrypoint"])[1:]
    monkeypatch.setattr(sys, "argv", argv)
    AllConfig.add_arguments(parser)
    parsed, _ = parser.parse_known_args(argv[1:])
    args = make_args(**vars(parsed))
    specs = InferenceEngineSpec.create(args)
    slots = args.rollout_num_gpus
    pg = SimpleNamespace(
        pg=object(), pg_reordered_bundle_indices=list(range(slots)), pg_reordered_gpu_ids=[i % 8 for i in range(slots)]
    )
    # Ray merges the job env into the manager, and into each actor's node-local
    # raylet env before applying the actor's explicit runtime env.
    for key, value in submitted.items():
        monkeypatch.setenv(key, value)
    manager = RayWorkerManager()

    async def launch():
        try:
            await manager.init(
                worker_manager_args(sglang_scaling=args.sglang_scaling),
                specs,
                {"rollout": pg},
                comm_backend=WorkerCommBackend.RAY,
            )
        finally:
            await manager.shutdown()

    fake_ray_cluster.use_node_ips(*(f"10.0.0.{rank + 7}" for rank in range(node.args.student_nodes) for _ in range(2)))
    asyncio.run(launch())
    calls = fake_ray_cluster.calls_of("run")
    assert len(calls) == slots // args.rollout_num_gpus_per_engine
    assert {handle.actor_class for handle in fake_ray_cluster.handles} == {CommandActor}

    subprocesses = []
    monkeypatch.setattr(
        process_utils.subprocess, "Popen", lambda *args, **kwargs: subprocesses.append(kwargs) or object()
    )
    monkeypatch.setattr(process_utils.atexit, "register", lambda *args: None)
    monkeypatch.setattr(command_actor.fault_hook_controller, "configure", lambda **kwargs: None)
    monkeypatch.setattr(command_actor.threading, "Thread", lambda **kwargs: SimpleNamespace(start=lambda: None))
    monkeypatch.setattr(os, "execvp", lambda *args, **kwargs: None)
    for call in calls:
        rank = int(call.handle.node_ip.rsplit(".", 1)[1]) - 7
        platform = _RANK_TWO_ENV if network == "heterogeneous" and rank == 2 else _NETWORK_ENV
        actor_runtime = _merge_runtime_env(
            submission["runtime_env"], call.handle.options["runtime_env"], override=True
        )
        assert actor_runtime is not None
        with monkeypatch.context() as local:
            local.setattr(os, "environ", {**platform, **_NCCL_CONTROLS})
            RuntimeEnvContext(env_vars=actor_runtime["env_vars"]).exec_worker(["-c", "pass"], Language.PYTHON)
            CommandActor().run(**call.kwargs)
        effective = subprocesses[-1]["env"]
        assert {
            key: effective[key] for key in platform
        } == platform, f"rank {rank} inherited the head's NIC/HCA selection"
        assert {key: effective[key] for key in _NCCL_CONTROLS} == _NCCL_CONTROLS
        assert {key: effective[key] for key in _DETERMINISM} == _DETERMINISM
        assert call.kwargs["envs"] == {}
        assert "NCCL_SOCKET_IFNAME=" not in call.kwargs["cmd"]
        assert "NCCL_IB_HCA=" not in call.kwargs["cmd"]
