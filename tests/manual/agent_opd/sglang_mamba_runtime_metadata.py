"""Prepare CPU-only receipts in the retained native SGLang diagnostic package.

Call after ``sglang_mamba_snapshots.prepare_source(selected_fp32=True)`` and
before attention imports/server startup. Formal launchers never import this
module. The recorder observes chosen locals, never tensor contents or decisions.
The existing internal-state response drains only its own process, not all TP
shards. Source qualification and CPU binding checks are not CUDA acceptance.
"""

import ast
import difflib
import hashlib
import importlib.metadata
import json
from pathlib import Path

from tests.manual.agent_opd import sglang_mamba_snapshots as snapshots


_SCHEDULE = "srt/managers/schedule_batch.py"
_GDN = "srt/layers/attention/linear/gdn_backend.py"
_HYBRID = "srt/layers/attention/hybrid_linear_attn_backend.py"
_MAMBA = "srt/mem_cache/unified_cache/components/mamba.py"
_RUNNER = "srt/model_executor/model_runner.py"
_TREE = "srt/mem_cache/unified_cache/unified_tree_core.py"
_CACHE = "srt/mem_cache/unified_radix_cache.py"
_INTERNAL = "srt/managers/scheduler_components/internal_state.py"
_RECORDER = "srt/mamba_runtime_metadata.py"
_ADDITIONAL = {
    _SCHEDULE: ("exp-1111-040603-422872", "455b597607f9ae753272666b4d3d07e9390d620d7ce400fda6f4686a74d84c0d"),
    _MAMBA: ("exp-1111-035902-035439", "22c0f2f5ec8c217c7b9bccd8753e8e5bf3914fd3c0d3ae52e64bfb7bd31df584"),
    _RUNNER: ("exp-1111-040603-422872", "0109f0d51947a646c643f1c56b55a7a0ef2638eaf20203159884588f8be7f4f3"),
    _TREE: ("exp-1111-042450-358109", "4948b7861488a51fce728a4ada6c40c875519b8cecc07aae4d9d6bec8b6a7e47"),
    _CACHE: ("exp-1111-040603-422872", "9c1a1116081c266301ecfeef4faf4178d18114a8996010765d9aa238cd83deb3"),
    _INTERNAL: ("exp-1111-040603-422872", "3879413625ca0991e3a64ca6a969a67afd1209aeb5c5760c4ab4ba7f46e98184"),
    "srt/layers/attention/mamba/prefill_track_metadata.py": (
        "exp-1111-042450-358109", "2ed82663640db555113b519efffa0f5ba8002129d44c92c2c2647b662be8a68a"
    ),
    "srt/model_executor/forward_batch_info.py": (
        "exp-1111-035902-035439", "5e01fa474ca1b838fd8fdca69b8ce9a13c3582cde22bda3f559df409c3016b56"
    ),
    "srt/runtime_context.py": (
        "exp-1111-042450-358109", "c36673ec3abb38e7f95c840fd6da8552de3b3f5e4ab5a498c22958e3988b4b1e"
    ),
}

# This code is installed only in a hash-qualified, disposable diagnostic package.
# No imports of torch/SGLang, tensor value reads, clocks, I/O, or synchronization.
_RECORDER_SOURCE = '''"""Process-local CPU receipts; device values and completion remain unmeasured."""

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
'''

_IMPORT = (
    "from sglang.srt.mamba_runtime_metadata import (\n"
    "    record as _mamba_record,\n"
    "    tensor_metadata as _mamba_tensor,\n"
    ")\n"
)


def _receipt(event: str, fields: tuple[tuple[str, str], ...], indent: int) -> str:
    """Emit one CPU tuple append, using expressions from the inspected scope."""
    pad = " " * indent
    lines = [f'{pad}_mamba_record("{event}", (\n']
    lines.extend(f'{pad}    ("{name}", {expression}),\n' for name, expression in fields)
    lines.append(f"{pad}))\n")
    return "".join(lines)


_RID = ("rids", "tuple(forward_batch.rids) if forward_batch.rids is not None else None")
_STATE = ("temporal", "_mamba_tensor(ssm_states)")
_REQ = (("rid", "req.rid"),)

# Anchors contain the original operation unchanged. Every edit only inserts a
# recorder import or CPU metadata append; no native algorithm is reproduced.
_EDITS = {
    _SCHEDULE: (
        ("import torch\n", "import torch\n\nfrom sglang.srt.mamba_runtime_metadata import record as _mamba_record\n"),
        (
            "        return _MambaRadixCacheV2TrackEntry(\n",
            _receipt("scheduler_track_boundary", _REQ + (
                ("prefix_len", "prefix_len"), ("seq_end", "seq_end"),
                ("extend_len", "req.extend_len"), ("cache_chunk_size", "cache_chunk_size"),
                ("state_chunk_size", "state_chunk_size"), ("checkpoint_grid", "checkpoint_grid"),
                ("mask", "mask"), ("track_position", "track_position"),
                ("track_seqlen", "mamba_track_seqlen"),
                ("aligned_seqlen", "mamba_track_seqlen_aligned"),
                ("last_track_idx", "req.kv.mamba_last_track_idx"),
                ("next_track_idx", "req.kv.mamba_next_track_idx"),
                ("branching_seqlen", "req.mamba_branching_seqlen"),
                ("last_track_seqlen", "req.kv.mamba_last_track_seqlen"),
            ), 8) + "        return _MambaRadixCacheV2TrackEntry(\n",
        ),
    ),
    _GDN: (
        ("from sglang.srt.layers.radix_linear_attention import RadixLinearAttention\n",
         _IMPORT + "from sglang.srt.layers.radix_linear_attention import RadixLinearAttention\n"),
        (
            "        return self.extend_kernel.extend(\n",
            _receipt("gdn_extend_dispatch", (
                ("kernel", "type(self.extend_kernel).__name__"),
                ("layer_id", 'kwargs.get("layer_id")'),
                ("track_state", '_mamba_tensor(kwargs.get("track_state"))'),
                ("track_chunk_idx", '_mamba_tensor(kwargs.get("track_chunk_idx"))'),
                _STATE, ("cache_indices", "_mamba_tensor(cache_indices)"),
                ("query_start_loc", "_mamba_tensor(query_start_loc)"),
            ), 8) + "        return self.extend_kernel.extend(\n",
        ),
        (
            "            core_attn_out, last_recurrent_state, h = self.kernel_dispatcher.extend(\n",
            _receipt("gdn_snapshot_allocation", (
                _RID, ("layer_id", "layer.layer_id"),
                ("has_mamba_track_mask", "forward_metadata.has_mamba_track_mask"),
                ("h_src", "_mamba_tensor(forward_metadata.track_ssm_h_src)"),
                ("snapshot_capability", "self.kernel_dispatcher.extend_kernel.supports_track_state_snapshot"),
                ("kernel", "type(self.kernel_dispatcher.extend_kernel).__name__"),
                ("allocated", "h_track_buf is not None"),
                ("track_state", "_mamba_tensor(h_track_buf)"),
                ("track_chunk_idx", "_mamba_tensor(forward_metadata.track_chunk_idx)"),
                _STATE, ("cache_indices", "_mamba_tensor(cache_indices)"),
                ("needs_state_gather", "needs_state_gather"),
                ("prefix_lens", "tuple(forward_batch.extend_prefix_lens_cpu) if forward_batch.extend_prefix_lens_cpu is not None else None"),
                ("extend_lens", "tuple(forward_batch.extend_seq_lens_cpu) if forward_batch.extend_seq_lens_cpu is not None else None"),
            ), 12) + "            core_attn_out, last_recurrent_state, h = self.kernel_dispatcher.extend(\n",
        ),
    ),
    _HYBRID: (
        ("from sglang.srt.environ import envs\n", "from sglang.srt.environ import envs\n" + _IMPORT),
        (
            "        # Resolve the tracked-row selection once per forward\n",
            _receipt("translated_track_metadata", (
                _RID, ("cache_indices", "_mamba_tensor(mamba_cache_indices)"),
                ("track_indices", "_mamba_tensor(forward_batch.mamba_track_indices)"),
            ), 8) + "        # Resolve the tracked-row selection once per forward\n",
        ),
        (
            "        to_device = self._track_indices_to_device\n",
            _receipt("prefill_track_plan", (
                _RID, ("chunk_size", "self.mamba_chunk_size"), ("mamba2", "is_mamba2"),
                ("mask", "tuple(forward_batch.mamba_prefill_track_mask_cpu)"),
                ("track_lens", "tuple(forward_batch.mamba_track_seqlens_cpu)"),
                ("extend_lens", "tuple(forward_batch.extend_seq_lens_cpu)"),
                ("prefix_lens", "tuple(forward_batch.extend_prefix_lens_cpu)"),
                *((name, f"tuple(plan.{name})") for name in (
                    "tracked_rows", "final_rows", "unaligned_rows", "h_rows", "h_src",
                    "recompute_rows", "recompute_end_locs", "chunk_indices"
                )),
                ("cache_indices", "_mamba_tensor(mamba_cache_indices)"),
                ("track_indices", "_mamba_tensor(forward_batch.mamba_track_indices)"),
            ), 8) + "        to_device = self._track_indices_to_device\n",
        ),
        (
            "                    ].to(ssm_states.dtype, copy=False)\n                else:\n",
            "                    ].to(ssm_states.dtype, copy=False)\n" + _receipt("snapshot_store_enqueued", (
                _RID, _STATE, ("source", '"h_track_buf"'),
                ("track_state", "_mamba_tensor(h_track_buf)"),
                ("source_rows", "_mamba_tensor(forward_metadata.track_ssm_h_batch_src)"),
                ("destination_slots", "_mamba_tensor(forward_metadata.track_ssm_h_dst)"),
            ), 20) + "                else:\n",
        ),
        (
            "                    ].to(ssm_states.dtype, copy=False)\n            if (\n",
            "                    ].to(ssm_states.dtype, copy=False)\n" + _receipt("snapshot_store_enqueued", (
                _RID, _STATE, ("source", '"per_chunk_h"'),
                ("h", "_mamba_tensor(h)"),
                ("source_rows", "_mamba_tensor(forward_metadata.track_ssm_h_src)"),
                ("destination_slots", "_mamba_tensor(forward_metadata.track_ssm_h_dst)"),
            ), 20) + "            if (\n",
        ),
        (
            "                    track_states.squeeze(0).to(ssm_states.dtype, copy=False)\n                )\n",
            "                    track_states.squeeze(0).to(ssm_states.dtype, copy=False)\n                )\n"
            + _receipt("snapshot_store_enqueued", (
                _RID, _STATE, ("source", '"recompute"'),
                ("track_states", "_mamba_tensor(track_states)"),
                ("destination_slots", "_mamba_tensor(forward_metadata.track_ssm_recompute_dst)"),
            ), 16),
        ),
        (
            "                    forward_metadata.track_ssm_final_src\n                ]\n",
            "                    forward_metadata.track_ssm_final_src\n                ]\n" + _receipt("snapshot_store_enqueued", (
                _RID, _STATE, ("source", '"final_state"'),
                ("source_slots", "_mamba_tensor(forward_metadata.track_ssm_final_src)"),
                ("destination_slots", "_mamba_tensor(forward_metadata.track_ssm_final_dst)"),
            ), 16),
        ),
    ),
    _MAMBA: (
        ("import torch\n", "import torch\n\n" + _IMPORT),
        (
            "        if not params.cow_mamba:\n            return result\n",
            "        if not params.cow_mamba:\n" + _receipt("cow_match_skipped", (
                ("reason", '"cow_not_requested"'), ("node_id", "result.best_match_node"),
            ), 12) + "            return result\n",
        ),
        (
            "        if src_index is None:\n            return result\n",
            "        if src_index is None:\n" + _receipt("cow_match_skipped", (
                ("reason", '"no_device_state"'), ("node_id", "result.best_match_node"),
            ), 12) + "            return result\n",
        ),
        (
            "        req.kv.mamba_needs_clear = False\n        return result\n",
            "        req.kv.mamba_needs_clear = False\n" + _receipt("cow_match_selected", _REQ + (
                ("node_id", "result.best_match_node"),
                ("source_slot", "_mamba_tensor(src_index)"),
                ("destination_slot", "_mamba_tensor(req.kv.mamba_pool_idx)"),
                ("needs_clear", "req.kv.mamba_needs_clear"),
            ), 8) + "        return result\n",
        ),
        (
            "            node.component_data[self.component_type].value = params.mamba_value\n",
            "            node.component_data[self.component_type].value = params.mamba_value\n"
            + _receipt("mamba_node_commit", (
                ("node_id", "node.id"), ("branch", '"new_leaf"'),
                ("value", "_mamba_tensor(params.mamba_value)"), ("mamba_exist", "result.mamba_exist"),
            ), 12),
        ),
        (
            "                node.id, self.component_type, params.mamba_value\n            )\n",
            "                node.id, self.component_type, params.mamba_value\n            )\n"
            + _receipt("mamba_node_commit", (
                ("node_id", "node.id"), ("branch", '"fill_absent_state"'),
                ("value", "_mamba_tensor(params.mamba_value)"), ("mamba_exist", "result.mamba_exist"),
            ), 12),
        ),
        (
            "        result.mamba_exist = True\n",
            "        result.mamba_exist = True\n" + _receipt("mamba_node_commit", (
                ("node_id", "node.id"), ("branch", '"retain_existing_state"'),
                ("existing_value", "_mamba_tensor(node.component_data[self.component_type].value)"),
                ("candidate_value", "_mamba_tensor(params.mamba_value)"),
                ("mamba_exist", "result.mamba_exist"),
            ), 8),
        ),
        (
            "                if checkpoint is None:\n                    return 0\n",
            "                if checkpoint is None:\n" + _receipt("mamba_donor_skipped", _REQ + (
                ("reason", '"no_finished_checkpoint"'), ("token_ids_len", "token_ids_len"),
                ("last_track_seqlen", "req.kv.mamba_last_track_seqlen"),
                ("previous_track_seqlen", "req.kv.mamba_prev_track_seqlen"),
            ), 20) + "                    return 0\n",
        ),
        (
            "                insert_params.mamba_value = active_value\n            return cache_len\n",
            "                insert_params.mamba_value = active_value\n" + _receipt("mamba_donor_prepared", _REQ + (
                ("is_finished", "is_finished"), ("cache_len", "cache_len"),
                ("token_ids_len", "token_ids_len"), ("keep_idx", "insert_params.mamba_keep_idx"),
                ("active_value", "_mamba_tensor(active_value)"),
                ("insert_value", "_mamba_tensor(insert_params.mamba_value)"),
            ), 12) + "            return cache_len\n",
        ),
        (
            "            insert_params.mamba_value = mamba_value_donated\n            return cache_len\n",
            "            insert_params.mamba_value = mamba_value_donated\n" + _receipt("mamba_donor_prepared", _REQ + (
                ("is_finished", "is_finished"), ("cache_len", "cache_len"),
                ("token_ids_len", "token_ids_len"),
                ("insert_value", "_mamba_tensor(mamba_value_donated)"),
                ("last_track_idx", "req.kv.mamba_last_track_idx"),
                ("next_track_idx", "req.kv.mamba_next_track_idx"),
            ), 12) + "            return cache_len\n",
        ),
    ),
    _RUNNER: (
        ("import torch\n", "import torch\n\n" + _IMPORT),
        (
            "                pool.translate_mamba_indices(forward_batch.mamba_clear_indices)\n            )\n",
            "                pool.translate_mamba_indices(forward_batch.mamba_clear_indices)\n            )\n"
            + _receipt("mamba_clear_enqueued", (
                _RID, ("clear_indices", "_mamba_tensor(forward_batch.mamba_clear_indices)"),
            ), 12),
        ),
        (
            "                    forward_batch.mamba_cow_dst_indices,\n                )\n",
            "                    forward_batch.mamba_cow_dst_indices,\n                )\n" + _receipt("mamba_cow_enqueued", (
                _RID, ("branch", '"int8_checkpoint"'),
                ("source_slots", "_mamba_tensor(forward_batch.mamba_cow_src_indices)"),
                ("destination_slots", "_mamba_tensor(forward_batch.mamba_cow_dst_indices)"),
            ), 16),
        ),
        (
            "                    pool.translate_mamba_indices(forward_batch.mamba_cow_dst_indices),\n                )\n",
            "                    pool.translate_mamba_indices(forward_batch.mamba_cow_dst_indices),\n                )\n"
            + _receipt("mamba_cow_enqueued", (
                _RID, ("branch", '"active_state_copy"'),
                ("source_slots", "_mamba_tensor(forward_batch.mamba_cow_src_indices)"),
                ("destination_slots", "_mamba_tensor(forward_batch.mamba_cow_dst_indices)"),
            ), 16),
        ),
    ),
    _TREE: (
        ("import torch\n", "import torch\n\n" + _IMPORT),
        (
            "                state.pending_actions.append(FreeDeviceKV([dup[swa_already_freed:]]))\n",
            "                state.pending_actions.append(FreeDeviceKV([dup[swa_already_freed:]]))\n"
            + _receipt("duplicate_kv_release_queued", (
                ("node_id", "node.id"), ("absolute_start", "abs_start"),
                ("absolute_end", "state.total_prefix_length + consumed_from"),
                ("full_only_end", "abs_start + swa_already_freed"),
                ("duplicate_indices", "_mamba_tensor(dup)"),
                ("mamba_exist", "state.result.mamba_exist"),
            ), 12),
        ),
    ),
    _CACHE: (
        ("import torch\n", "import torch\n\n" + _IMPORT),
        (
            "        result = self.insert(insert_params)\n",
            _receipt("checkpoint_insert_begin", _REQ + (
                ("page_aligned_len", "page_aligned_len"),
                ("protected_len", "req.kv.cache_protected_len"),
                ("insert_value", "_mamba_tensor(insert_params.mamba_value)"),
            ), 8) + "        result = self.insert(insert_params)\n" + _receipt("checkpoint_insert_returned", _REQ + (
                ("mamba_exist", "result.mamba_exist"),
                ("rotation_tail_declined", "result.rotation_tail_declined"),
                ("node_id", "result.last_device_node"), ("prefix_len", "result.prefix_len"),
            ), 8),
        ),
        (
            "            new_indices[req.kv.cache_protected_len :],\n        )\n",
            "            new_indices[req.kv.cache_protected_len :],\n        )\n"
            + _receipt("canonical_kv_rebind_enqueued", _REQ + (
                ("node_id", "new_last_node"), ("prefix_len", "new_prefix_len"),
                ("absolute_start", "req.kv.cache_protected_len"),
                ("absolute_end", "len(new_indices)"), ("page_aligned_len", "page_aligned_len"),
                ("canonical_indices", "_mamba_tensor(new_indices)"),
                ("mamba_exist", "result.mamba_exist"),
            ), 8),
        ),
        (
            "                self.token_to_kv_pool_allocator.free_segment(indices, start_pos=0)\n",
            "                self.token_to_kv_pool_allocator.free_segment(indices, start_pos=0)\n"
            + _receipt("kv_allocator_release_returned", (
                ("branch", '"full_and_swa"'), ("indices", "_mamba_tensor(indices)"),
            ), 16),
        ),
        (
            "                self.token_to_kv_pool_allocator.free_full_segment(indices, start_pos=0)\n",
            "                self.token_to_kv_pool_allocator.free_full_segment(indices, start_pos=0)\n"
            + _receipt("kv_allocator_release_returned", (
                ("branch", '"full_only"'), ("indices", "_mamba_tensor(indices)"),
            ), 16),
        ),
    ),
    _INTERNAL: (
        (
            "from sglang.srt.disaggregation.utils import DisaggregationMode\n",
            "from sglang.srt.disaggregation.utils import DisaggregationMode\n"
            "from sglang.srt.mamba_runtime_metadata import drain as _mamba_drain\n",
        ),
        (
            '        state.pop("custom_sigquit_handler", None)\n',
            '        state.pop("custom_sigquit_handler", None)\n'
            '        state["mamba_runtime_metadata"] = _mamba_drain(get_parallel())\n',
        ),
    ),
}


def source_manifest() -> dict:
    """Reuse the selected-FP32 owner's package identity and math-source hashes."""
    owner = snapshots.source_manifest()
    files = {
        relative: {"before_sha256": identity["after_sha256"], "native_source_job": owner["native_source_job"]}
        for relative, identity in owner["files"].items()
    }
    files.update({relative: {"before_sha256": digest, "native_source_job": job}
                  for relative, (job, digest) in _ADDITIONAL.items()})
    return {"image": owner["image"], "distribution_version": owner["distribution_version"], "files": files}


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _rewrite(relative: str, content: bytes, *, reverse: bool = False) -> bytes:
    text = content.decode()
    edits = _EDITS.get(relative, ())
    for before, after in reversed(edits) if reverse else edits:
        old, new = (after, before) if reverse else (before, after)
        old, new = "\n" + old, "\n" + new
        if text.count(old) != 1:
            raise ValueError(f"Runtime metadata source seam differs: {relative}")
        text = text.replace(old, new)
    return text.encode()


def _sources(root: Path, manifest: dict) -> tuple[dict, dict, dict]:
    current, original, candidate = {}, {}, {}
    for relative, identity in manifest["files"].items():
        path = root / relative
        if not path.is_file():
            raise ValueError(f"Required runtime metadata source absent: {path}; sha256={identity['before_sha256']}")
        content = path.read_bytes()
        baseline = content
        if _sha256(content) != identity["before_sha256"]:
            if relative not in _EDITS:
                raise ValueError(f"Unrecognized runtime metadata source: {path}; sha256={_sha256(content)}")
            try:
                baseline = _rewrite(relative, content, reverse=True)
            except ValueError as error:
                raise ValueError(f"Unrecognized runtime metadata source: {path}; sha256={_sha256(content)}") from error
        if _sha256(baseline) != identity["before_sha256"]:
            raise ValueError(f"Unrecognized runtime metadata source: {path}; sha256={_sha256(content)}")
        rewritten = _rewrite(relative, baseline)
        if content not in (baseline, rewritten):
            raise ValueError(f"Unrecognized runtime metadata source: {path}; sha256={_sha256(content)}")
        ast.parse(rewritten, filename=str(path))
        current[relative], original[relative], candidate[relative] = content, baseline, rewritten
    recorder = root / _RECORDER
    content = recorder.read_bytes() if recorder.exists() else b""
    expected = _RECORDER_SOURCE.encode()
    if content not in (b"", expected) or (recorder.exists() and not content):
        raise ValueError(f"Unrecognized runtime metadata recorder: {recorder}; sha256={_sha256(content)}")
    ast.parse(expected, filename=str(recorder))
    current[_RECORDER], original[_RECORDER], candidate[_RECORDER] = content, b"", expected
    return current, original, candidate


def _archive(archive: Path, original: dict, candidate: dict, manifest: dict) -> None:
    artifacts = {"source_manifest.json": (json.dumps(manifest, indent=2) + "\n").encode()}
    diff = []
    for relative in original:
        artifacts[f"before/{relative}"], artifacts[f"after/{relative}"] = original[relative], candidate[relative]
        diff.extend(difflib.unified_diff(
            original[relative].decode().splitlines(keepends=True),
            candidate[relative].decode().splitlines(keepends=True),
            fromfile=f"a/{relative}", tofile=f"b/{relative}",
        ))
    artifacts["runtime_metadata.diff"] = "".join(diff).encode()
    for relative, content in artifacts.items():
        path = archive / relative
        if path.exists() and path.read_bytes() != content:
            raise ValueError(f"Runtime metadata archive differs: {path}")
    for relative, content in artifacts.items():
        path = archive / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(content)


def prepare_runtime_metadata(native_sglang_package_root: Path, *, image: str, archive_dir: Path) -> dict:
    """Qualify every source before writes; archive exact diagnostic-only edits.

    Requires already-selected-FP32 sources. Repeating this function is idempotent;
    do not rerun the math preparer on an already instrumented diagnostic package.
    Missing/changed source, wrong image/version, or archive conflicts fail before
    source writes. No host SGLang import, model load, or GPU operation occurs.
    """
    manifest = source_manifest()
    if image != manifest["image"]:
        raise ValueError("Runtime metadata requires the qualified pinned image")
    version = importlib.metadata.version("sglang")
    if version != manifest["distribution_version"]:
        raise ValueError(f"Runtime metadata dependency identity differs: version={version}")
    root, archive = native_sglang_package_root.resolve(), archive_dir.resolve()
    current, original, candidate = _sources(root, manifest)
    manifest["files"] = {
        relative: {
            **manifest["files"].get(relative, {"created": True}),
            "before_sha256": _sha256(original[relative]), "after_sha256": _sha256(candidate[relative]),
        } for relative in candidate
    }
    _archive(archive, original, candidate, manifest)
    changed = [relative for relative in candidate if current[relative] != candidate[relative]]
    for relative in changed:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(candidate[relative])
    observed = {relative: _sha256((root / relative).read_bytes()) for relative in candidate}
    if observed != {relative: _sha256(content) for relative, content in candidate.items()}:
        raise ValueError("Runtime metadata dependency changed during preflight")
    receipt = {
        **manifest, "sglang_path": str(root), "archive_dir": str(archive),
        "observed_before_sha256": {relative: _sha256(content) for relative, content in current.items()},
        "observed_after_sha256": observed, "changed_files": changed, "patch_applied": bool(changed),
        "diagnostic_only": True, "selected_fp32_precondition": True,
        "readback_key": "mamba_runtime_metadata",
        "readback": "existing /server_info internal_state Dict; drains responding process only",
        "coverage": "no all-TP gather; DP responses retain individual process/rank receipts",
        "physical_slot_values": "UNMEASURED", "cuda_semantics": "UNVERIFIED",
        "runtime_semantics": "UNVERIFIED; host-enqueue receipts do not prove device completion or parity",
    }
    with (archive / "preflight.jsonl").open("a") as stream:
        stream.write(json.dumps(receipt, allow_nan=False) + "\n")
    return receipt
