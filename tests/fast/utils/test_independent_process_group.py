"""Independent weight-transfer worlds must not split the trainer's default world."""

from types import SimpleNamespace

import pytest
import torch
import torch.distributed.distributed_c10d as c10d

from miles.utils.distributed_utils import init_process_group


class _ConstructorReached(Exception):
    pass


def test_independent_world_does_not_split_device_bound_parent(monkeypatch):
    parent = c10d.ProcessGroup(torch.distributed.HashStore(), 0, 8)
    device = torch.device("cuda:0")
    parent.bound_device_id = device
    split_source = object()
    monkeypatch.setattr(c10d._world, "default_pg", parent)
    monkeypatch.setattr(c10d, "_get_split_source", lambda group: split_source)

    class Nccl:
        class Options(SimpleNamespace):
            split_from = None

        def __new__(cls, store, rank, size, options):
            assert size == 5 and rank == 0
            assert options.split_from is None, "An independent world inherited the trainer's communicator"
            assert parent.bound_device_id is None
            raise _ConstructorReached

    monkeypatch.setattr(c10d, "ProcessGroupNCCL", Nccl)
    with pytest.raises(_ConstructorReached):
        init_process_group(
            backend="nccl", store=torch.distributed.HashStore(), world_size=5, rank=0, group_name="weights"
        )
    assert parent.bound_device_id == device
