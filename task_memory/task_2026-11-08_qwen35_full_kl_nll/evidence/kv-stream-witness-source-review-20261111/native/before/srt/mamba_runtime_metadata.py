"""Process-local CPU receipts; device values and completion remain unmeasured."""

import os

_rows = []
_sequence = 0


def tensor_metadata(tensor):
    if tensor is None:
        return None
    return (id(tensor), str(tensor.dtype), tuple(tensor.shape),
            tuple(tensor.stride()), str(tensor.device))


def record(event, fields):
    global _sequence
    _sequence += 1
    _rows.append((_sequence, event, fields))


def drain(parallel):
    rows = tuple(_rows)
    _rows.clear()
    return {
        "schema": "mamba-runtime-metadata-v1",
        "process_id": os.getpid(),
        "rank": {name: getattr(parallel, name) for name in (
            "dp_rank", "tp_rank", "pp_rank", "attn_dp_rank", "attn_tp_rank")},
        "coverage": "responding scheduler process only; no all-TP gather",
        "physical_slot_values": "UNMEASURED",
        "tensor_metadata_fields": ("object_id", "dtype", "shape", "stride", "device"),
        "device_store_completion": "UNMEASURED; receipts follow host enqueue only",
        "rows": rows,
    }
