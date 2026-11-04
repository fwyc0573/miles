"""Check CUDA weight broadcasts across independent trainer and inference worlds.

Run on the warmup's external two-node Ray cluster before loading model weights.
The default NCCL worlds bind eagerly to their devices, matching the failure that
an independent weight-transfer world must avoid. Probe actors are then released.
"""

import argparse
import json
import os
import traceback
from datetime import timedelta
from pathlib import Path

import ray
import torch
import torch.distributed as dist
from ray.util.scheduling_strategies import NodeAffinitySchedulingStrategy
from sglang.srt.environ import envs

from miles.utils.distributed_utils import init_process_group
from miles.utils.misc import get_free_port
from miles.utils.port_range import service_port_range


@ray.remote(num_gpus=1, num_cpus=1)
class _WeightSyncRank:
    def __init__(self, role: str, rank: int, size: int, timeout: int, channels: int | None):
        if channels is not None:
            os.environ["NCCL_MIN_NCHANNELS"] = str(channels)
            os.environ["NCCL_MAX_NCHANNELS"] = str(channels)
        self.role = role
        self.rank = rank
        self.size = size
        self.timeout = timedelta(seconds=timeout)
        self.device = torch.device("cuda", 0)
        torch.cuda.set_device(self.device)
        self.weights = None

    def address(self, port_count: int) -> tuple[str, int]:
        ports = service_port_range()
        port = get_free_port(start_port=ports[0], consecutive=port_count, port_range=ports)
        return ray._private.services.get_node_ip_address(), port

    def initialize(self, address: str, port: int) -> dict:
        dist.init_process_group(
            backend="nccl",
            init_method=f"tcp://{address}:{port}",
            rank=self.rank,
            world_size=self.size,
            device_id=self.device,
            timeout=self.timeout,
        )
        if dist.group.WORLD.bound_device_id != self.device:
            raise ValueError("The probe default world did not bind eagerly to its device")
        return self._default_sum()

    def _default_sum(self) -> dict:
        value = torch.tensor(self.rank + 1, device=self.device, dtype=torch.float32)
        dist.all_reduce(value)
        expected = self.size * (self.size + 1) / 2
        if value.item() != expected:
            raise ValueError(f"{self.role} default-world reduction differs: {value.item()} != {expected}")
        return {
            "role": self.role,
            "rank": self.rank,
            "world_size": self.size,
            "sum": value.item(),
            "nccl_channel_bounds": {key: os.environ.get(key) for key in ("NCCL_MIN_NCHANNELS", "NCCL_MAX_NCHANNELS")},
        }

    def connect_weights(self, address: str, port: int, rank: int, size: int) -> None:
        if self.role == "trainer":
            create = init_process_group
        else:
            # Use the receiver's native factory, rather than another Miles sender.
            from sglang.srt.utils import init_custom_process_group

            create = init_custom_process_group
        self.weights = create(
            backend="nccl",
            init_method=f"tcp://{address}:{port}",
            rank=rank,
            world_size=size,
            group_name="agent-opd-weight-probe",
            timeout=self.timeout,
        )
        if dist.group.WORLD.bound_device_id != self.device:
            raise ValueError("Creating the weight world changed the default device binding")

    def broadcast(self, elements: int, version: int) -> dict:
        expected = torch.arange(elements, device=self.device, dtype=torch.bfloat16) + version
        tensor = expected.clone() if self.role == "trainer" else torch.empty_like(expected)
        dist.broadcast(tensor, src=0, group=self.weights, async_op=True).wait()
        if not torch.equal(tensor, expected):
            raise ValueError("An inference rank received different weight tensor values")
        return {"role": self.role, "rank": self.rank, "version": version, "sum": tensor.float().sum().item()}

    def finish(self) -> dict:
        if self.weights is not None:
            dist.destroy_process_group(self.weights)
        result = self._default_sum()
        dist.destroy_process_group()
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--address", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--trainer-gpus", type=int, default=8)
    parser.add_argument("--inference-gpus", type=int, default=4)
    parser.add_argument("--tensor-elements", type=int, default=32)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--sender-channels", type=int)
    args = parser.parse_args()
    ray.init(address=args.address, log_to_driver=False)
    actors = []
    initialized = []
    stage = "discover_nodes"
    try:
        nodes = [node for node in ray.nodes() if node["Alive"]]
        head_ip = ray._private.services.get_node_ip_address()
        trainer_node = next(node for node in nodes if node["NodeManagerAddress"] == head_ip)
        inference_node = next(node for node in nodes if node["NodeID"] != trainer_node["NodeID"])
        stage = "create_actors"
        trainer, inference = [], []
        for role, node, count, ranks in (
            ("trainer", trainer_node, args.trainer_gpus, trainer),
            ("inference", inference_node, args.inference_gpus, inference),
        ):
            for rank in range(count):
                actor = _WeightSyncRank.options(
                    scheduling_strategy=NodeAffinitySchedulingStrategy(node["NodeID"], soft=False)
                ).remote(
                    role,
                    rank,
                    count,
                    args.timeout,
                    args.sender_channels if role == "trainer" else envs.SGLANG_DETERMINISTIC_NCCL_NCHANNELS.get(),
                )
                actors.append(actor)
                ranks.append(actor)
        stage = "allocate_ports"
        trainer_ip, trainer_port = ray.get(trainer[0].address.remote(2), timeout=args.timeout)
        inference_ip, inference_port = ray.get(inference[0].address.remote(1), timeout=args.timeout)
        stage = "initialize_default_worlds"
        initialized = ray.get(
            [actor.initialize.remote(trainer_ip, trainer_port) for actor in trainer]
            + [actor.initialize.remote(inference_ip, inference_port) for actor in inference],
            timeout=args.timeout,
        )
        stage = "connect_weight_world"
        participants = [trainer[0], *inference]
        ray.get(
            [
                actor.connect_weights.remote(trainer_ip, trainer_port + 1, rank, len(participants))
                for rank, actor in enumerate(participants)
            ],
            timeout=args.timeout,
        )
        stage = "broadcast_weights"
        broadcasts = []
        for version in (0, 1):
            broadcasts.extend(
                ray.get(
                    [actor.broadcast.remote(args.tensor_elements, version) for actor in participants],
                    timeout=args.timeout,
                )
            )
        stage = "restore_default_worlds"
        restored = ray.get([actor.finish.remote() for actor in actors], timeout=args.timeout)
        result = {
            "status": "passed",
            "nodes": [trainer_ip, inference_ip],
            "default_worlds": initialized,
            "weight_world_size": len(participants),
            "tensor_elements": args.tensor_elements,
            "dtype": "bfloat16",
            "sender_channels": args.sender_channels,
            "receiver_channels": envs.SGLANG_DETERMINISTIC_NCCL_NCHANNELS.get(),
            "broadcasts": broadcasts,
            "default_worlds_after_weight_transfer": restored,
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n")
        print("AGENT_OPD_WEIGHT_SYNC_PROBE_PASSED", json.dumps(result), flush=True)
    except Exception as error:
        result = {
            "status": "failed",
            "stage": stage,
            "error_type": type(error).__name__,
            "default_worlds": initialized,
            "traceback": traceback.format_exc(),
        }
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n")
        print("AGENT_OPD_WEIGHT_SYNC_PROBE_FAILED", json.dumps(result), flush=True)
        raise
    finally:
        for actor in actors:
            ray.kill(actor, no_restart=True)
        ray.shutdown()


if __name__ == "__main__":
    main()
