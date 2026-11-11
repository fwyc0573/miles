"""Isolated FULL KV and layer-0 recurrent diagnostic; CPU is not CUDA proof.

The installed runtime observes original CPP stores and the production Rust
insert callback. It never walks the tree, changes a cache decision, or waits.
Only the explicit after-all internal-state drain reads device contents.
"""

import ast
import difflib
import hashlib
import importlib.metadata
import importlib.util
import json
import math
import os
import shutil
import sys
import threading
from pathlib import Path

from tests.manual.agent_opd import sglang_kv_streams as streams


# BEGIN INSTALLED RUNTIME
WINDOW_START = 90112
WINDOW_END = 98304
CANDIDATE_INPUT_COUNT = 98942
BANK_COUNT = 2
RECURRENT_BANK_COUNT = 4
SCORING_REQUEST_COUNT = 16
_collector = None
_startup_error = None


def tensor_descriptor(tensor):
    return {"data_ptr": tensor.data_ptr(), "shape": tuple(tensor.shape),
            "stride": tuple(tensor.stride()), "dtype": str(tensor.dtype),
            "device": str(tensor.device)}


def capture_budget(buffers, rows, banks):
    payload = sum(math.prod(k.shape[1:]) * k.element_size()
                  + math.prod(v.shape[1:]) * v.element_size() for k, v in buffers)
    return {"payload_bytes": banks * 2 * rows * payload,
            "index_bytes": banks * (len(buffers) + 3) * rows * 8,
            "allocated_bytes": banks * rows * (2 * payload + (len(buffers) + 3) * 8)}


def fragment_window(cursor, prefix_len, start, end):
    lo, hi = max(start, cursor), min(end, cursor + prefix_len)
    return (lo, hi, lo - cursor, hi - cursor) if lo < hi else None


def writer_windows(rids, prefixes, extends, start, end):
    if not (len(rids) == len(prefixes) == len(extends)):
        raise ValueError("ForwardBatch CPU RID/lens arrays differ")
    offset, windows = 0, []
    for rid, prefix, extend in zip(rids, prefixes, extends):
        if type(prefix) is not int or type(extend) is not int or min(prefix, extend) < 0:
            raise ValueError("ForwardBatch CPU lens must be nonnegative integers")
        lo, hi = max(start, prefix), min(end, prefix + extend)
        if lo < hi:
            windows.append((rid, prefix, extend, lo, hi, offset + lo - prefix, offset + hi - prefix))
        offset += extend
    return windows


def covered_once(intervals, start, end):
    cursor = start
    for lo, hi in sorted(intervals):
        if lo != cursor or hi <= lo or hi > end:
            return False
        cursor = hi
    return cursor == end


def recurrent_selection(input_counts, common_rows):
    if input_counts is None and common_rows is None:
        return (), None
    counts = tuple(input_counts) if input_counts is not None else ()
    if (len(counts) != 2 or len(set(counts)) != 2
            or any(type(n) is not int or n <= WINDOW_START for n in counts)
            or type(common_rows) is not int
            or not 0 < common_rows <= min(WINDOW_END - WINDOW_START, min(counts) - WINDOW_START)):
        raise ValueError("Recurrent selection requires two input counts within the native window and actual common rows")
    return tuple(sorted(counts)), common_rows


def recurrent_metrics(torch, left, right, *, token_axis=None, start=None, readback_right=None):
    """Compare small CPU slices, without tolerances or full-size FP64 copies."""
    receipt = {"left_shape": tuple(left.shape), "right_shape": tuple(right.shape),
               "left_dtype": str(left.dtype), "right_dtype": str(right.dtype),
               "status": "unverified"}
    if left.shape != right.shape or left.dtype != right.dtype:
        receipt["reason"] = "Component shape/dtype differs"
        return receipt
    # Indexed temporal state is [1, H, V, K]; inspect one head, not a full FP64 state.
    axis = token_axis if token_axis is not None else (1 if len(left.shape) == 4 else 0)
    mismatch_count = nonfinite_left = nonfinite_right = finite_count = 0
    maximum = squared = 0.0
    first = None
    for row in range(left.shape[axis]):
        right_row = right.select(axis, row)
        if readback_right is not None:
            right_row = readback_right(right_row)
        a, b = left.select(axis, row).double(), right_row.double()
        fa, fb = torch.isfinite(a), torch.isfinite(b)
        finite = fa & fb
        mismatch = a != b
        count = int(mismatch.sum())
        mismatch_count += count
        nonfinite_left += int((~fa).sum())
        nonfinite_right += int((~fb).sum())
        finite_count += int(finite.sum())
        if count and first is None:
            coordinate = list(mismatch.nonzero()[0].tolist())
            coordinate.insert(axis, row)
            first = {"coordinate": coordinate,
                     "absolute_token": start + row if token_axis is not None else None}
        differences = (a - b)[finite]
        if differences.numel():
            maximum = max(maximum, float(differences.abs().max()))
            squared += float((differences * differences).sum())
    receipt.update(status="captured", mismatch_count=mismatch_count,
                   left_nonfinite_count=nonfinite_left, right_nonfinite_count=nonfinite_right,
                   finite_pair_count=finite_count, first_mismatch=first,
                   max_absolute_error=maximum if finite_count else None,
                   rms_error=math.sqrt(squared / finite_count) if finite_count else None,
                   values_exact=not (mismatch_count or nonfinite_left or nonfinite_right))
    return receipt


class Collector:
    """Own preallocated receipts; errors disqualify evidence, never serving."""

    def __init__(self, torch, allocator, root, *, stream_scalar):
        self.torch, self.stream_scalar = torch, stream_scalar
        self.start, self.end = WINDOW_START, WINDOW_END
        self.rows = self.end - self.start
        self.banks, self.by_rid, self.completed = [], {}, set()
        self.errors, self.pending_cpp, self.summary = [], {}, None
        self.native_binding, self.binding_error = None, None
        self.recurrent = {"configured": False, "banks": [], "by_rid": {}, "errors": [],
                          "summary": None, "staging": {}, "memory": {}}
        self.root, self.pool = root, root.full_kv_pool
        if allocator.get_kvcache() is not root or allocator.page_size != 1:
            raise ValueError("Collector requires the live allocator root and page1")
        if type(allocator).__name__ != "TokenToKVPoolAllocator":
            raise ValueError("Collector requires the qualified TokenToKVPoolAllocator")
        if type(root).__name__ != "HybridLinearKVPool" or type(self.pool).__name__ != "MHATokenToKVPool":
            raise ValueError("Collector requires the actual HybridLinearKVPool/MHATokenToKVPool topology")
        if root.post_capture_active or self.pool.post_capture_active:
            raise ValueError("Collector initialization requires finalized non-post-capture backing")
        self.mapping = dict(root.full_attention_layer_id_mapping)
        if sorted(self.mapping.values()) != list(range(len(self.mapping))):
            raise ValueError("FULL global-to-dense mapping is not complete")
        self.layers = tuple(sorted(self.mapping, key=self.mapping.get))
        if tuple(self.pool.model_layer_ids) != self.layers:
            raise ValueError("FULL child global-layer declaration differs from root")
        self.buffers = tuple(zip(self.pool.k_buffer, self.pool.v_buffer))
        if len(self.buffers) != len(self.layers) or not self.layers:
            raise ValueError("FULL backing does not match the dense layer mapping")
        for k, v in self.buffers:
            if (len(k.shape) != 3 or k.shape != v.shape or k.dtype != v.dtype
                    or k.device != v.device or k.dtype != torch.bfloat16
                    or not k.is_contiguous() or not v.is_contiguous()):
                raise ValueError("Collector requires finalized contiguous BF16 NHD K/V buffers")
        self.topology = {"root_object_id": id(root), "writer_object_id": id(self.pool),
                         "allocator_object_id": id(allocator), "allocator_class": type(allocator).__name__,
                         "root_class": type(root).__name__, "writer_class": type(self.pool).__name__,
                         "page_size": allocator.page_size, "capacity": allocator.size,
                         "mapping": tuple(self.mapping.items()),
                         "buffers": tuple({"layer_id": layer, "K": tensor_descriptor(k), "V": tensor_descriptor(v)}
                                          for layer, (k, v) in zip(self.layers, self.buffers)),
                         "budget": capture_budget(self.buffers, self.rows, BANK_COUNT)}
        for _ in range(BANK_COUNT):
            payload = {}
            for side in ("fresh", "old"):
                payload[side] = tuple((torch.empty((self.rows, *k.shape[1:]), dtype=k.dtype, device=k.device),
                                       torch.empty((self.rows, *v.shape[1:]), dtype=v.dtype, device=v.device))
                                      for k, v in self.buffers)
            device = self.buffers[0][0].device
            indices = {name: torch.empty((self.rows,), dtype=torch.int64, device=device)
                       for name in ("old", "insert", "rebind")}
            indices["writer"] = tuple(torch.empty((self.rows,), dtype=torch.int64, device=device)
                                      for _ in self.layers)
            self.banks.append({"rid": None, "payload": payload, "indices": indices,
                               "fresh_layers": set(), "fragments": [], "insert": None,
                               "rebind": None, "errors": [], "scheduler": None})

    def invalidate(self, rid, start, end, stage, message):
        error = {"rid": rid, "P": start, "E": end, "stage": stage, "message": str(message)}
        self.errors.append(error)
        bank = self.by_rid.get(rid)
        if bank is not None:
            bank["errors"].append(error)

    def register(self, req):
        try:
            self._recurrent_register(req)
        except Exception as error:
            self._recurrent_error("selection", error, req.rid)
        if not (req.return_logprob and req.logprob_start_len == 0
                and len(req.origin_input_ids) == CANDIDATE_INPUT_COUNT):
            return
        if req.rid in self.by_rid:
            return
        free = next((bank for bank in self.banks if bank["rid"] is None), None)
        if free is None:
            self.invalidate(req.rid, self.start, self.end, "selection", "More than two distinct candidate RIDs")
            return
        free["rid"] = req.rid
        self.by_rid[req.rid] = free

    def _key(self, batch, k, v, loc):
        return (tuple(batch.rids), tuple(batch.extend_prefix_lens_cpu), tuple(batch.extend_seq_lens_cpu),
                k.data_ptr(), v.data_ptr(), loc.data_ptr())

    def _targets(self, batch):
        if not batch.forward_mode.is_extend():
            return []
        return [row for row in writer_windows(batch.rids, batch.extend_prefix_lens_cpu,
                                              batch.extend_seq_lens_cpu, self.start, self.end)
                if row[0] in self.by_rid]

    def note_cpp(self, batch, k, v, loc, native_stream, torch_stream):
        if batch is None or not self._targets(batch):
            return
        key = self._key(batch, k, v, loc)
        if key in self.pending_cpp:
            raise ValueError("Duplicate target CPP store key")
        self.pending_cpp[key] = (native_stream, torch_stream)

    def fresh(self, pool, dense, loc, batch, kind):
        if batch is None:
            return
        for rid, prefix, extend, lo, hi, src_lo, src_hi in self._targets(batch):
            bank = self.by_rid[rid]
            try:
                if kind != "cpp":
                    raise ValueError("CUDA prefix-valid Triton terminal unsupported; commit_lens/stream UNVERIFIED")
                if (pool is not self.pool or prefix != self.start or extend != self.rows
                        or (lo, hi) != (self.start, self.end)):
                    raise ValueError("Target writer is not the exact RID/P/8192 chunk and live FULL child")
                if dense in bank["fresh_layers"]:
                    raise ValueError("Duplicate target FULL writer layer")
                k, v = self.buffers[dense]
                witness = self.pending_cpp.pop(self._key(batch, k, v, loc), None)
                current = self.stream_scalar(k.device)
                if witness is None or witness[0] == -1 or witness[0] != witness[1] or witness[0] != current:
                    raise ValueError("Missing/mismatched target in-call CPP/F stream witness")
                selected = loc[src_lo:src_hi]
                self._validate_indices(selected, self.rows)
                bank["indices"]["writer"][dense].copy_(selected)
                out_k, out_v = bank["payload"]["fresh"][dense]
                self.torch.index_select(k, 0, selected, out=out_k)
                self.torch.index_select(v, 0, selected, out=out_v)
                bank["fresh_layers"].add(dense)
            except Exception as error:
                self.invalidate(rid, self.start, self.end, "fresh", error)

    def _validate_indices(self, indices, count):
        if (indices.dtype != self.torch.int64 or tuple(indices.shape) != (count,)
                or indices.device != self.buffers[0][0].device):
            raise ValueError("Physical indices require device-local int64 vector of exact length")

    def _capture_native_binding(self, tree_core):
        if self.native_binding is not None or self.binding_error is not None:
            return
        try:
            bindings = type(tree_core)._bindings
            actual_class = type(tree_core._binding)
            factory_class = tree_core._binding_class()
            module_file = Path(bindings.__file__).resolve(strict=True)
            module_data = module_file.read_bytes()
            self.native_binding = {"module": bindings.__name__, "module_file": str(module_file),
                                   "module_sha256": hashlib.sha256(module_data).hexdigest(),
                                   "module_bytes": len(module_data), "class": actual_class.__name__,
                                   "class_module": actual_class.__module__,
                                   "class_is_module_attribute": getattr(bindings, actual_class.__name__) is actual_class,
                                   "factory_class_matches": factory_class is actual_class,
                                   "process_id": os.getpid()}
            if not self.native_binding["class_is_module_attribute"]:
                raise ValueError("Actual native binding class differs from module export")
            if not self.native_binding["factory_class_matches"]:
                raise ValueError("Actual native binding class differs from adapter factory class")
        except Exception as error:
            self.binding_error = f"{type(error).__name__}: {error}"
            self.invalidate(None, self.start, self.end, "native_binding", self.binding_error)

    def insert(self, req, params, page_aligned_len, tree_core):
        self._recurrent_publication(req, params, page_aligned_len)
        self._capture_native_binding(tree_core)
        bank = self.by_rid.get(req.rid)
        if bank is None or page_aligned_len != self.end or req.kv.cache_protected_len != self.start:
            return
        try:
            if bank["insert"] is not None:
                raise ValueError("Repeated target RID/P/E insert invocation")
            if type(tree_core).__name__ != "RustUnifiedTreeCore":
                raise ValueError("Original OLD observer requires the actual RustUnifiedTreeCore")
            if params.prev_prefix_len != self.start or len(params.value) != self.end:
                raise ValueError("FULL InsertParams protected range differs")
            original = params.value[self.start:self.end]
            self._validate_indices(original, self.rows)
            bank["indices"]["insert"].copy_(original)
            scheduler = {"thread_id": threading.get_native_id(),
                         "torch_current_raw_stream": self.stream_scalar(original.device)}
            bank["scheduler"] = scheduler
            bank["insert"] = {"rid": req.rid, "P": self.start, "E": self.end,
                              "protected_len": req.kv.cache_protected_len,
                              "page_aligned_len": page_aligned_len,
                              "FULL_value": tensor_descriptor(params.value), **scheduler}
            params.old_full_observer = (self, req.rid, self.start, self.end)
        except Exception as error:
            self.invalidate(req.rid, self.start, self.end, "insert", error)

    def __call__(self, rid, start, end, node_id, cursor, prefix_len, original_indices):
        try:
            bank = self.by_rid[rid]
            if (start, end) != (self.start, self.end) or bank["insert"] is None:
                raise ValueError("Native observer RID/P/E is not the armed invocation")
            window = fragment_window(cursor, prefix_len, start, end)
            if window is None:
                return
            lo, hi, src_lo, src_hi = window
            if original_indices is None:
                raise ValueError("Matched original node has no live FULL value; fresh restoration is not OLD")
            if len(original_indices) < prefix_len:
                raise ValueError("Original FULL tensor is shorter than matched fragment")
            scheduler = bank["scheduler"]
            observed = {"thread_id": threading.get_native_id(),
                        "torch_current_raw_stream": self.stream_scalar(original_indices.device)}
            if observed != scheduler:
                raise ValueError("Inline original FULL callback does not match scheduler S thread/stream")
            if any(lo < b and a < hi for a, b in ((f["lo"], f["hi"]) for f in bank["fragments"])):
                raise ValueError("Original OLD fragments overlap")
            selected = original_indices[src_lo:src_hi]
            self._validate_indices(selected, hi - lo)
            out = slice(lo - start, hi - start)
            bank["indices"]["old"][out].copy_(selected)
            for dense, (k, v) in enumerate(self.buffers):
                out_k, out_v = bank["payload"]["old"][dense]
                self.torch.index_select(k, 0, selected, out=out_k[out])
                self.torch.index_select(v, 0, selected, out=out_v[out])
            bank["fragments"].append({"rid": rid, "P": start, "E": end, "node_id": node_id,
                                      "cursor": cursor, "prefix_len": prefix_len, "lo": lo, "hi": hi,
                                      "original_FULL": tensor_descriptor(original_indices), **observed})
        except Exception as error:
            self.invalidate(rid, start, end, "old", error)

    def rebind(self, req, new_indices, page_aligned_len, result):
        self._recurrent_rebind(req, page_aligned_len, result)
        bank = self.by_rid.get(req.rid)
        if bank is None or page_aligned_len != self.end or req.kv.cache_protected_len != self.start:
            return
        try:
            if bank["insert"] is None or bank["rebind"] is not None or result.rotation_tail_declined:
                raise ValueError("Missing/repeated/declined target checkpoint rebind")
            if not self.start <= result.prefix_len <= self.end or len(new_indices) != self.end:
                raise ValueError("Target rebind Q/end differs from captured window")
            selected = new_indices[self.start:self.end]
            self._validate_indices(selected, self.rows)
            bank["indices"]["rebind"].copy_(selected)
            bank["rebind"] = {"rid": req.rid, "P": self.start, "E": self.end, "Q": result.prefix_len,
                              "node_id": result.last_device_node,
                              "rotation_tail_declined": result.rotation_tail_declined,
                              "canonical_indices": tensor_descriptor(new_indices)}
        except Exception as error:
            self.invalidate(req.rid, self.start, self.end, "rebind", error)

    def _recurrent_error(self, stage, error, rid=None):
        row = {"rid": rid, "stage": stage, "error_type": type(error).__name__, "message": str(error)}
        self.recurrent["errors"].append(row)
        bank = self.recurrent["by_rid"].get(rid)
        if bank is not None:
            bank["errors"].append(row)

    def _recurrent_memory(self, stage):
        device = self.recurrent["conv"].device
        self.recurrent["memory"][stage] = {
            "allocated_bytes": self.torch.cuda.memory_allocated(device),
            "reserved_bytes": self.torch.cuda.memory_reserved(device),
            "peak_allocated_bytes": self.torch.cuda.max_memory_allocated(device),
            "peak_reserved_bytes": self.torch.cuda.max_memory_reserved(device),
            "owned_capture_host_bytes": sum(t.numel() * t.element_size()
                for bank in self.recurrent["banks"] for t in bank["host"].values()),
            "owned_serving_staging_bytes": sum(t.numel() * t.element_size()
                for t in self.recurrent["staging"].values()),
            "peak_scope": "process lifetime; no peak reset"}

    def initialize_recurrent(self, req_pool, input_counts=None, common_rows=None):
        """Separate optional evidence allocation from the accepted FULL banks."""
        state = self.recurrent
        try:
            counts, common = recurrent_selection(input_counts, common_rows)
            if not counts:
                return
            state.update(configured=True, input_counts=counts, common_rows=common,
                         max_rows=min(self.rows, max(counts) - self.start), req_pool=req_pool)
            if req_pool.layer_transfer_counter is not None:
                raise ValueError("Recurrent observation requires the existing no-transfer pool")
            cache = req_pool.mamba_pool.mamba2_layer_cache(req_pool.mamba_map[0])
            conv, temporal = cache.conv[0], cache.temporal
            if (len(cache.conv) != 1 or not conv.is_contiguous() or not temporal.is_contiguous()
                    or temporal.dtype != self.torch.float32 or conv.device != temporal.device):
                raise ValueError("Recurrent observation requires the retained contiguous conv/FP32 temporal layout")
            state.update(conv=conv, temporal=temporal)
            self._recurrent_memory("before_allocation")
            for _ in range(RECURRENT_BANK_COUNT):
                state["banks"].append({"rid": None, "host": {}, "descriptors": {}, "errors": [],
                                       "stages": [], "publication": None, "call": {}})
            for name, tensor in (("conv", conv), ("temporal", temporal)):
                for phase in ("initial", "final", "publication"):
                    for bank in state["banks"]:
                        bank["host"][phase + "_" + name] = self.torch.empty(
                            (1, *tensor.shape[1:]), dtype=tensor.dtype, device="cpu", pin_memory=True)
                for stream in ("forward", "scheduler"):
                    state["staging"][stream + "_" + name] = self.torch.empty(
                        (1, *tensor.shape[1:]), dtype=tensor.dtype, device=tensor.device)
            self._recurrent_memory("after_state_allocation")
        except Exception as error:
            self._recurrent_error("allocation", error)
            state["allocation_failed"] = True

    def _recurrent_register(self, req):
        state = self.recurrent
        if (not state["configured"] or state.get("allocation_failed")
                or not req.return_logprob or req.logprob_start_len != 0
                or len(req.origin_input_ids) not in state["input_counts"] or req.rid in state["by_rid"]):
            return
        free = next((b for b in state["banks"] if b["rid"] is None), None)
        if free is None:
            self._recurrent_error("selection", ValueError("More than four recurrent candidate RIDs"), req.rid)
            return
        free.update(rid=req.rid, input_count=len(req.origin_input_ids))
        state["by_rid"][req.rid] = free

    def _recurrent_target(self, layer, batch):
        state = self.recurrent
        # ForwardMode is authoritative: DECODE/verify fields may have no CPU lens.
        if (not state["configured"] or state.get("allocation_failed") or layer.layer_id != 0
                or batch is None or not batch.forward_mode.is_extend()):
            return None
        rids, prefixes, extends = batch.rids, batch.extend_prefix_lens_cpu, batch.extend_seq_lens_cpu
        if len(rids) != 1:
            if any(rid in state["by_rid"] for rid in rids):
                raise ValueError("Recurrent capture supports only the retained single-sequence call")
            return None
        bank = state["by_rid"].get(rids[0])
        if bank is None:
            return None
        if (tuple(prefixes) == (self.start,)
                and tuple(extends) == (min(self.rows, bank["input_count"] - self.start),)):
            return bank
        return None

    def _recurrent_copy(self, bank, name, tensor, token_axis=None):
        shape = list(tensor.shape)
        if token_axis is not None:
            shape[token_axis] = self.recurrent["max_rows"]
        if name not in bank["host"]:
            # Allocate four max-length banks from actual native tensor descriptors.
            for candidate in self.recurrent["banks"]:
                candidate["host"][name] = self.torch.empty(
                    tuple(shape), dtype=tensor.dtype, device="cpu", pin_memory=True)
        destination = bank["host"][name]
        if token_axis is not None:
            destination = destination.narrow(token_axis, 0, tensor.shape[token_axis])
        if destination.shape != tensor.shape or destination.dtype != tensor.dtype:
            raise ValueError("Recurrent component allocation differs from its actual descriptor")
        destination.copy_(tensor, non_blocking=True)
        bank["descriptors"][name] = tensor_descriptor(tensor)

    def _recurrent_state_copy(self, bank, phase, conv, temporal, indices, stream):
        if indices.numel() != 1 or indices.device != conv.device:
            raise ValueError("Recurrent capture requires one device-local active/donor index")
        current = self.stream_scalar(conv.device)
        key = stream + "_stream"
        if key in self.recurrent and self.recurrent[key] != current:
            raise ValueError("Private recurrent staging cannot be reused across different streams")
        self.recurrent[key] = current
        selected = indices.reshape(1).to(dtype=self.torch.int64)
        for name, source in (("conv", conv), ("temporal", temporal)):
            staging = self.recurrent["staging"][stream + "_" + name]
            self.torch.index_select(source, 0, selected, out=staging)
            self._recurrent_copy(bank, phase + "_" + name, staging)

    def recurrent_begin(self, backend, layer, forward_batch, cache_indices, conv_states,
                        ssm_states, mixed_qkv, *, conv_fn, needs_state_gather):
        bank = self._recurrent_target(layer, forward_batch)
        if bank is None:
            return
        if bank["stages"] or needs_state_gather:
            raise ValueError("Repeated recurrent begin or unsupported gathered-state call")
        if conv_states is not self.recurrent["conv"] or ssm_states is not self.recurrent["temporal"]:
            # at_layer_idx creates views; compare the actual backing identity, not Python view identity.
            if (tensor_descriptor(conv_states) != tensor_descriptor(self.recurrent["conv"])
                    or tensor_descriptor(ssm_states) != tensor_descriptor(self.recurrent["temporal"])):
                raise ValueError("Observed recurrent state is not the initialized layer-0 pool")
        metadata = backend.forward_metadata
        if metadata.conv_block_table is not None:
            raise ValueError("Retained single-sequence conv control requires its actual None block table")
        bank.update(P=self.start, extend=forward_batch.extend_seq_lens_cpu[0],
                    dispatcher=backend.kernel_dispatcher, conv_fn=conv_fn,
                    weights=layer.conv_weights, bias=layer.bias)
        bank["call"] = {"activation": layer.activation, "bias_present": layer.bias is not None,
                        "conv_function": {"module": conv_fn.__module__, "name": conv_fn.__qualname__},
                        "weights": tensor_descriptor(layer.conv_weights),
                        "bias": tensor_descriptor(layer.bias) if layer.bias is not None else None,
                        "dispatcher": type(backend.kernel_dispatcher).__name__,
                        "extend_kernel": type(backend.kernel_dispatcher.extend_kernel).__name__,
                        "conv_states": tensor_descriptor(conv_states),
                        "ssm_states": tensor_descriptor(ssm_states),
                        "state_capture": "one indexed row through private same-stream staging, not a retained pool view",
                        "head_first": False, "use_qk_l2norm_in_kernel": True,
                        "scale": layer.head_k_dim ** -0.5, "inplace_update": True,
                        "block_table": None, "seq_lens_cpu": tuple(forward_batch.extend_seq_lens_cpu),
                        "has_mamba_track_mask": metadata.has_mamba_track_mask,
                        "num_state_checkpoints": metadata.num_state_checkpoints,
                        "state_checkpoint_every_n_tokens": metadata.state_checkpoint_every_n_tokens,
                        "forward_stream": self.stream_scalar(conv_states.device)}
        self._recurrent_state_copy(bank, "initial", conv_states, ssm_states, cache_indices, "forward")
        self._recurrent_copy(bank, "cache_indices", cache_indices)
        self._recurrent_copy(bank, "has_initial_state", forward_batch.extend_prefix_lens > 0)
        self._recurrent_copy(bank, "extend_prefix_lens", forward_batch.extend_prefix_lens)
        for name in ("query_start_loc", "state_checkpoint_cu_starts"):
            tensor = getattr(metadata, name)
            if tensor is not None:
                self._recurrent_copy(bank, name, tensor)
            else:
                bank["call"][name] = None
        if metadata.has_mamba_track_mask:
            for name in ("track_conv_indices", "conv_states_mask_indices"):
                self._recurrent_copy(bank, name, getattr(metadata, name))
        bank["descriptors"]["conv_input"] = tensor_descriptor(mixed_qkv)
        if "conv_input" not in self.recurrent["staging"]:
            self.recurrent["staging"]["conv_input"] = self.torch.empty(
                (self.recurrent["max_rows"], mixed_qkv.shape[1]), dtype=mixed_qkv.dtype, device=mixed_qkv.device)
        staging = self.recurrent["staging"]["conv_input"][:mixed_qkv.shape[0]]
        staging.copy_(mixed_qkv)
        self._recurrent_copy(bank, "conv_input", staging, 0)
        # Dense host storage is not the native strided projection view.
        bank["descriptors"]["conv_input"] = tensor_descriptor(mixed_qkv)
        bank["stages"].append("begin")

    def recurrent_inputs(self, layer, forward_batch, mixed_qkv, q, k, v, g, beta,
                         query_start_loc, *, track_state, track_chunk_idx, output):
        bank = self._recurrent_target(layer, forward_batch)
        if bank is None:
            return
        if bank["stages"] != ["begin"]:
            raise ValueError("Recurrent inputs lacks a unique pre-mutation begin")
        self._recurrent_copy(bank, "conv_output", mixed_qkv, 0)
        for name, tensor in (("q", q), ("k", k), ("v", v), ("g", g), ("beta", beta)):
            self._recurrent_copy(bank, name, tensor, 1)
        bank["call"]["track_state"] = tensor_descriptor(track_state) if track_state is not None else None
        bank["call"]["output"] = tensor_descriptor(output) if output is not None else None
        bank["output_dtype"] = output.dtype if output is not None else None
        if track_chunk_idx is not None:
            self._recurrent_copy(bank, "track_chunk_idx", track_chunk_idx)
        else:
            bank["call"]["track_chunk_idx"] = None
        if tensor_descriptor(query_start_loc) != bank["descriptors"]["query_start_loc"]:
            raise ValueError("Recurrence cu-seqlens differs from the saved native call")
        bank["stages"].append("inputs")

    def recurrent_end(self, layer, forward_batch, cache_indices, conv_states, ssm_states, core_attn_out):
        bank = self._recurrent_target(layer, forward_batch)
        if bank is None:
            return
        if bank["stages"] != ["begin", "inputs"]:
            raise ValueError("Recurrent end lacks unique saved inputs")
        self._recurrent_copy(bank, "output", core_attn_out, 1)
        self._recurrent_state_copy(bank, "final", conv_states, ssm_states, cache_indices, "forward")
        bank["stages"].append("end")
        self._recurrent_memory("after_capture")

    def _recurrent_publication(self, req, params, page_aligned_len):
        bank = self.recurrent["by_rid"].get(req.rid)
        if bank is None or page_aligned_len != self.start:
            return
        try:
            if bank["publication"] is not None or params.mamba_value is None:
                raise ValueError("Repeated/missing same-P incoming donor publication")
            indices = self.recurrent["req_pool"].translate_mamba_indices(params.mamba_value)
            self._recurrent_state_copy(bank, "publication", self.recurrent["conv"],
                                       self.recurrent["temporal"], indices, "scheduler")
            self._recurrent_copy(bank, "publication_indices", indices)
            bank["publication"] = {"P": page_aligned_len, "incoming_donor": tensor_descriptor(indices),
                                   "canonical_value_status": "unverified",
                                   "reason": "Publication result join unavailable"}
        except Exception as error:
            self._recurrent_error("publication", error, req.rid)

    def _recurrent_rebind(self, req, page_aligned_len, result):
        bank = self.recurrent["by_rid"].get(req.rid)
        if bank is None or page_aligned_len != self.start:
            return
        try:
            publication = bank["publication"]
            if publication is None:
                return
            if "node_id" in publication:
                raise ValueError("Repeated same-P publication rebind")
            publication.update(node_id=result.last_device_node, prefix_len=result.prefix_len,
                               mamba_exist=result.mamba_exist, rotation_tail_declined=result.rotation_tail_declined)
            canonical = (not result.mamba_exist and not result.rotation_tail_declined
                         and result.prefix_len == self.start and result.last_device_node is not None)
            publication["canonical_value_status"] = "captured" if canonical else "unverified"
            publication["reason"] = None if canonical else "Incoming donor is not a joined new canonical-P publication"
        except Exception as error:
            self._recurrent_error("publication_join", error, req.rid)

    def finish(self, req):
        if req.return_logprob and req.finished():
            self.completed.add(req.rid)

    def _physical(self, bank):
        q = bank["rebind"]["Q"]
        n = q - self.start
        frozen = {name: bank["indices"][name].cpu() for name in ("insert", "rebind")}
        writer_equal = all(self.torch.equal(value.cpu(), frozen["insert"])
                           for value in bank["indices"]["writer"])
        old_equal = n == 0 or self.torch.equal(bank["indices"]["old"][:n].cpu(), frozen["rebind"][:n])
        suffix_equal = self.torch.equal(frozen["rebind"][n:], frozen["insert"][n:])
        capacity = self.buffers[0][0].shape[0]
        bounds = all(bool(((value >= 0) & (value < capacity)).all()) for value in frozen.values())
        if n:
            old = bank["indices"]["old"][:n].cpu()
            bounds = bounds and bool(((old >= 0) & (old < capacity)).all())
        return {"writer_equals_FULL_insert_all_layers": writer_equal,
                "original_OLD_equals_rebind": old_equal, "rebind_suffix_equals_insert": suffix_equal,
                "indices_in_bounds": bounds, "old_rows": n}

    def _metrics(self, bank):
        n = bank["rebind"]["Q"] - self.start
        if not n:
            return None
        metrics = []
        for layer, fresh, old in zip(self.layers, bank["payload"]["fresh"], bank["payload"]["old"]):
            for name, candidate, reference in zip(("K", "V"), fresh, old):
                a, b = reference[:n].cpu().float(), candidate[:n].cpu().float()
                finite_a, finite_b = self.torch.isfinite(a), self.torch.isfinite(b)
                finite = finite_a & finite_b
                mismatch = a != b
                errors = (a - b).abs()
                relative_mask = finite & (a != 0)
                absolute = errors[finite]
                relative = errors[relative_mask] / a[relative_mask].abs()
                row = {"layer_id": layer, "side": name, "old_rows": n,
                       "values_exact": bool(finite.all()) and bool(self.torch.equal(a, b)),
                       "mismatch_count": int(mismatch.sum()),
                       "max_absolute_error": float(absolute.max()) if absolute.numel() else None,
                       "max_relative_error": float(relative.max()) if relative.numel() else None,
                       "relative_error_undefined_count": int((a == 0).sum()),
                       "old_nonfinite_count": int((~finite_a).sum()),
                       "fresh_nonfinite_count": int((~finite_b).sum())}
                for label, values, mask in (("absolute", errors, finite),
                                            ("relative", errors / a.abs(), relative_mask)):
                    if bool(mask.any()):
                        position = int(values.masked_fill(~mask, -1).flatten().argmax())
                        dim = a.shape[2]
                        token, head, dimension = position // (a.shape[1] * dim), (position // dim) % a.shape[1], position % dim
                        row[label + "_extremum"] = {"token": self.start + token, "head": head,
                                                     "dimension": dimension, "OLD": float(a.flatten()[position]),
                                                     "FRESH": float(b.flatten()[position])}
                metrics.append(row)
        return metrics

    def _recurrent_receipt(self, requested):
        state = self.recurrent
        if state["summary"] is not None:
            return state["summary"]
        return {"schema": "recurrent-state-v1", "process_id": os.getpid(),
                "status": "unverified" if requested or not state["configured"] else "metadata_only",
                "reason": ("Existing FULL completion/readback is required" if state["configured"]
                           else "Recurrent selection is unconfigured; no values captured or replayed"),
                "records": [{"rid": b["rid"], "input_count": b["input_count"],
                             "P": b.get("P"), "extend": b.get("extend"),
                             "descriptors": b["descriptors"], "call": b["call"],
                             "publication": b["publication"] or {
                                 "canonical_value_status": "unverified", "reason": "Canonical-P publication join unavailable"},
                             "stages": tuple(b["stages"]), "errors": tuple(b["errors"])}
                            for b in state["banks"] if b["rid"] is not None],
                "comparisons": [], "replays": [], "errors": tuple(state["errors"]),
                "coverage": {"scope": "responding scheduler process, TP0, layer0 only; no all-TP gather",
                             "configured": state["configured"], "expected_records": RECURRENT_BANK_COUNT,
                             "registered_records": len(state["by_rid"]),
                             "common_rows": state.get("common_rows")},
                "memory": state["memory"], "numeric_acceptance": None}

    def _recurrent_value(self, bank, name, rows=None):
        value = bank["host"][name]
        axis = 0 if name in ("conv_input", "conv_output") else 1
        if name in ("conv_input", "conv_output", "q", "k", "v", "g", "beta", "output"):
            value = value.narrow(axis, 0, bank["extend"] if rows is None else rows)
        return value

    def _recurrent_components(self, left, right, rows, names):
        result = {}
        for name in names:
            token_axis = (0 if name in ("conv_input", "conv_output") else 1) if name in (
                "conv_input", "conv_output", "q", "k", "v", "g", "beta", "output") else None
            result[name] = recurrent_metrics(
                self.torch, self._recurrent_value(left, name, rows), self._recurrent_value(right, name, rows),
                token_axis=token_axis, start=self.start)
        return result

    def _recurrent_publication_comparisons(self, banks):
        comparisons = []
        for left in banks:
            for right in banks:
                publication = right["publication"]
                if publication is None or publication["canonical_value_status"] != "captured":
                    continue
                comparisons.append({"left_rid": left["rid"], "right_rid": right["rid"],
                    "common_rows": None, "kind": "active-initial/canonical-publication",
                    "publication_node_id": publication["node_id"],
                    "source_key_join": "unverified; consumer must join original source/cache-event identity",
                    "components": {name: recurrent_metrics(self.torch, left["host"]["initial_" + name],
                                                            right["host"]["publication_" + name])
                                   for name in ("conv", "temporal")}})
        return comparisons

    def _recurrent_upload(self, bank, name, rows=None):
        source = self._recurrent_value(bank, name, rows)
        descriptor = bank["descriptors"][name]
        value = self.torch.empty_strided(source.shape, descriptor["stride"],
                                         dtype=source.dtype, device=self.recurrent["conv"].device)
        value.copy_(source)
        return value

    def _recurrent_readback(self, value):
        host = self.torch.empty(value.shape, dtype=value.dtype, device="cpu", pin_memory=True)
        host.copy_(value, non_blocking=False)
        return host

    def _recurrent_conv_replay(self, bank, rows, state_bank, *, readback=True):
        torch, call = self.torch, bank["call"]
        x = self._recurrent_upload(bank, "conv_input", rows)
        initial = self._recurrent_value(state_bank, "initial_conv")
        indices = self._recurrent_value(bank, "cache_indices")
        active = int(indices.reshape(-1)[0])
        original_slots = [active]
        if call["has_mamba_track_mask"]:
            original_slots.extend(int(n) for n in bank["host"]["conv_states_mask_indices"].reshape(-1))
        slots = tuple(dict.fromkeys(original_slots))
        pool = torch.empty((len(slots), *initial.shape[1:]), dtype=initial.dtype, device=x.device)
        pool[0:1].copy_(initial)
        cache_indices = torch.zeros(indices.shape, dtype=indices.dtype, device=x.device)
        if call["has_mamba_track_mask"]:
            track = self._recurrent_upload(bank, "track_conv_indices")
            destinations = torch.tensor([slots.index(int(n)) for n in
                                         bank["host"]["conv_states_mask_indices"].reshape(-1)],
                                        dtype=bank["host"]["conv_states_mask_indices"].dtype, device=x.device)
            if rows == bank["extend"]:
                pool[destinations] = x[track].transpose(1, 2)
            else:
                if active in original_slots[1:]:
                    raise ValueError("Shortened conv call has an active/tracking alias; shape comparison unavailable")
                # These original tracking writes target independent scratch slots.
                # They are not the truncated kernel's active initial state or input.
                tracked = bank["host"]["conv_input"][bank["host"]["track_conv_indices"].long()]
                pool[destinations] = tracked.to(x.device).transpose(1, 2)
        query = self._recurrent_upload(bank, "query_start_loc")
        if rows != bank["extend"]:
            query = torch.tensor([0, rows], dtype=query.dtype, device=x.device)
        output = bank["conv_fn"](
            x.transpose(0, 1), bank["weights"], bank["bias"], activation=call["activation"],
            conv_states=pool, has_initial_state=self._recurrent_upload(bank, "has_initial_state"),
            cache_indices=cache_indices, query_start_loc=query, seq_lens_cpu=[rows])
        output = output.transpose(0, 1)[:rows]
        if readback:
            return self._recurrent_readback(output), self._recurrent_readback(pool[:1])
        return output, pool[:1]

    def _recurrent_gdn_replay(self, bank, rows, state_bank, *, readback=True):
        torch, call = self.torch, bank["call"]
        tensors = {name: self._recurrent_upload(bank, name, rows) for name in ("q", "k", "v", "g", "beta")}
        temporal = self._recurrent_value(state_bank, "initial_temporal").to(self.recurrent["temporal"].device)
        # A new owned copy is required even in CPU DI, where .to(device) may alias.
        temporal = temporal.clone()
        original_indices = bank["host"]["cache_indices"]
        indices = torch.zeros(original_indices.shape, dtype=original_indices.dtype, device=temporal.device)
        query = self._recurrent_upload(bank, "query_start_loc")
        if rows != bank["extend"]:
            query = torch.tensor([0, rows], dtype=query.dtype, device=temporal.device)
        track = None
        track_idx = None
        if call["track_state"] is not None:
            descriptor = call["track_state"]
            track = torch.empty_strided(descriptor["shape"], descriptor["stride"],
                                        dtype=temporal.dtype, device=temporal.device)
            track_idx = self._recurrent_upload(bank, "track_chunk_idx")
        output = None
        if call["output"] is not None:
            descriptor = call["output"]
            shape = list(descriptor["shape"])
            shape[1] = rows
            output = torch.empty_strided(shape, descriptor["stride"], dtype=bank["output_dtype"], device=temporal.device)
        checkpoint_starts = (self._recurrent_upload(bank, "state_checkpoint_cu_starts")
                             if "state_checkpoint_cu_starts" in bank["host"] else None)
        if rows != bank["extend"] and checkpoint_starts is not None:
            raise ValueError("Shortened state-checkpoint ABI is unavailable for this retained call")
        result, _, h = bank["dispatcher"].extend(
            **tensors, ssm_states=temporal, cache_indices=indices, query_start_loc=query,
            state_checkpoint_cu_starts=checkpoint_starts, num_state_checkpoints=call["num_state_checkpoints"],
            state_checkpoint_every_n_tokens=call["state_checkpoint_every_n_tokens"],
            output=output, layer_id=0, extend_prefix_lens=self._recurrent_upload(bank, "extend_prefix_lens"),
            track_state=track, track_chunk_idx=track_idx)
        if readback:
            return self._recurrent_readback(result), self._recurrent_readback(temporal)
        return result, temporal

    def _recurrent_replay(self, bank, component, rows, state_bank, kind, *, compared_rids=()):
        row = {"rid": bank["rid"], "kind": kind, "component": component, "rows": rows,
               "common_rows": self.recurrent["common_rows"], "compared_rids": tuple(compared_rids),
               "initial_state_rid": state_bank["rid"], "status": "unverified", "metrics": {}}
        try:
            method = self._recurrent_conv_replay if component == "conv" else self._recurrent_gdn_replay
            output_name = "conv_output" if component == "conv" else "output"
            count = rows if kind == "control" else self.recurrent["common_rows"]
            axis = 0 if component == "conv" else 1
            if kind == "state-sensitivity":
                baseline, _ = method(bank, rows, bank)
                output, state = method(bank, rows, state_bank, readback=False)
                reference = baseline.narrow(axis, 0, count)
                readback = self._recurrent_readback
            else:
                output, state = method(bank, rows, state_bank)
                reference = self._recurrent_value(bank, output_name, count)
                readback = None
            row["metrics"]["output"] = recurrent_metrics(
                self.torch, reference, output.narrow(axis, 0, count),
                token_axis=axis, start=self.start, readback_right=readback)
            if kind == "control":
                row["metrics"]["final_state"] = recurrent_metrics(
                    self.torch, bank["host"]["final_" + ("conv" if component == "conv" else "temporal")], state)
            row["status"] = "captured"
            row["values_exact"] = all(metric["values_exact"] for metric in row["metrics"].values())
            row["comparison_reference"] = ("own-state scratch versus alternate actual-state scratch; same captured input"
                                           if kind == "state-sensitivity" else "captured own call; see independent scratch control")
        except Exception as error:
            self._recurrent_error("replay_" + kind + "_" + component, error, bank["rid"])
            row.update(reason=str(error), error_type=type(error).__name__)
        return row

    def _recurrent_drain(self, full_completed):
        state = self.recurrent
        receipt = self._recurrent_receipt(True)
        if not full_completed:
            return receipt
        if not state["configured"] or state.get("allocation_failed"):
            state["summary"] = receipt
            self._recurrent_release()
            return receipt
        try:
            self._recurrent_memory("before_drain")
            banks = [bank for bank in state["banks"] if bank["stages"] == ["begin", "inputs", "end"]]
            receipt["coverage"]["captured_records"] = len(banks)
            receipt["coverage"]["input_count_records"] = {
                str(count): sum(bank["input_count"] == count for bank in banks) for count in state["input_counts"]}
            for record in receipt["records"]:
                bank = state["by_rid"][record["rid"]]
                complete = bank["stages"] == ["begin", "inputs", "end"]
                record["status"] = "captured" if complete else "unverified"
                if complete:
                    record["native_indices"] = {name: bank["host"][name].tolist() for name in (
                        "cache_indices", "query_start_loc", "track_chunk_idx", "conv_states_mask_indices")
                                                if name in bank["host"]}
                if complete and record["publication"]["canonical_value_status"] == "captured":
                    record["publication"]["active_initial_comparison"] = {
                        name: recurrent_metrics(self.torch, bank["host"]["initial_" + name],
                                                bank["host"]["publication_" + name])
                        for name in ("conv", "temporal")}
            names = ("initial_conv", "initial_temporal", "final_conv", "final_temporal",
                     "conv_input", "conv_output", "q", "k", "v", "g", "beta", "output")
            for index, left in enumerate(banks):
                for right in banks[index + 1:]:
                    receipt["comparisons"].append({"left_rid": left["rid"], "right_rid": right["rid"],
                        "common_rows": state["common_rows"], "components": self._recurrent_components(
                            left, right, state["common_rows"], names)})
            publication_comparisons = self._recurrent_publication_comparisons(banks)
            receipt["comparisons"].extend(publication_comparisons)
            shorter = min(min(self.rows, n - self.start) for n in state["input_counts"])
            controls = {}
            for bank in banks:
                for component in ("conv", "temporal"):
                    control = self._recurrent_replay(bank, component, bank["extend"], bank, "control")
                    receipt["replays"].append(control)
                    controls[bank["rid"], component] = control
                    if bank["extend"] > shorter:
                        shape = self._recurrent_replay(bank, component, shorter, bank, "shape")
                        shape["control_status"] = control["status"]
                        shape["control_values_exact"] = control.get("values_exact")
                        receipt["replays"].append(shape)
            for pair in receipt["comparisons"]:
                if pair.get("kind") == "active-initial/canonical-publication":
                    continue
                for component in ("conv", "temporal"):
                    initial = pair["components"]["initial_" + component]
                    if (initial["status"] == "captured" and initial["left_nonfinite_count"] == 0
                            and initial["right_nonfinite_count"] == 0 and initial["mismatch_count"]):
                        left, right = state["by_rid"][pair["left_rid"]], state["by_rid"][pair["right_rid"]]
                        sensitivity = self._recurrent_replay(left, component, left["extend"], right,
                                                            "state-sensitivity", compared_rids=(left["rid"], right["rid"]))
                        control = controls[left["rid"], component]
                        sensitivity.update(control_status=control["status"], control_values_exact=control.get("values_exact"))
                        receipt["replays"].append(sensitivity)
            # Missing canonical publication is field-level unavailable, not lost active/input evidence.
            capture_errors = [error for error in state["errors"] if error["stage"] not in ("publication", "publication_join")]
            complete = (len(banks) == RECURRENT_BANK_COUNT and not capture_errors
                        and all(n == RECURRENT_BANK_COUNT // len(state["input_counts"])
                                for n in receipt["coverage"]["input_count_records"].values()))
            receipt.update(status="captured" if complete else "unverified",
                           reason=None if complete else "Incomplete recurrent capture/replay coverage")
            self._recurrent_memory("after_replay")
        except Exception as error:
            self._recurrent_error("drain", error)
            receipt.update(status="unverified", reason=str(error))
        receipt["errors"] = tuple(state["errors"])
        state["summary"] = receipt
        self._recurrent_release()
        return receipt

    def _recurrent_release(self):
        state = self.recurrent
        for bank in state["banks"]:
            for name in ("host", "dispatcher", "conv_fn", "weights", "bias", "output_dtype"):
                bank.pop(name, None)
        state["staging"].clear()

    def drain(self, requested):
        if self.summary is not None:
            return self.summary
        receipt = {"schema": "kv-coherence-v1", "process_id": os.getpid(),
                   "status": "unverified" if self.binding_error is not None else "metadata_only",
                   "topology": self.topology, "errors": tuple(self.errors),
                   "native_binding": self.native_binding, "binding_error": self.binding_error,
                   "completed_rids": tuple(sorted(self.completed)),
                   "banks": [{"rid": bank["rid"], "insert": bank["insert"], "rebind": bank["rebind"],
                              "fragments": tuple(bank["fragments"]), "fresh_layers": tuple(sorted(bank["fresh_layers"])),
                              "errors": tuple(bank["errors"])} for bank in self.banks],
                    "coverage": "responding TP0 only; no all-TP gather", "numeric_acceptance": None}
        receipt["recurrent_state"] = self._recurrent_receipt(requested)
        if not requested:
            return receipt
        if len(self.completed) != SCORING_REQUEST_COUNT:
            receipt.update(status="unverified", reason="Drain requires all16 distinct completed native scoring RIDs")
            return receipt
        if self.native_binding is None or self.binding_error is not None:
            receipt.update(status="unverified", reason="Missing/errored serving native binding identity")
            return receipt
        if len(self.by_rid) != BANK_COUNT or self.errors or self.pending_cpp:
            receipt.update(status="unverified", reason="Candidate cardinality/capture errors/unconsumed CPP witness")
            return receipt
        for bank in self.banks:
            q = bank["rebind"]["Q"] if bank["rebind"] else None
            intervals = [(f["lo"], f["hi"]) for f in bank["fragments"]]
            if (bank["insert"] is None or q is None or bank["errors"]
                    or bank["fresh_layers"] != set(range(len(self.layers)))
                    or not covered_once(intervals, self.start, q)):
                receipt.update(status="unverified", reason="Incomplete FULL writer/insert/rebind/original OLD coverage")
                return receipt
        try:
            receipt["banks"] = []
            for bank in self.banks:
                physical = self._physical(bank)
                qualified = all(physical[name] for name in ("writer_equals_FULL_insert_all_layers",
                                                           "original_OLD_equals_rebind",
                                                           "rebind_suffix_equals_insert", "indices_in_bounds"))
                receipt["banks"].append({"rid": bank["rid"], "insert": bank["insert"], "rebind": bank["rebind"],
                                         "fragments": bank["fragments"], "physical": physical,
                                         "metrics": self._metrics(bank) if qualified else None,
                                         "status": "captured" if qualified else "unverified"})
            receipt["status"] = "captured" if all(b["status"] == "captured" for b in receipt["banks"]) else "unverified"
        except Exception as error:
            receipt.update(status="unverified", reason=str(error), error_type=type(error).__name__)
        self.summary = receipt
        for bank in self.banks:
            bank.pop("payload", None)
            bank.pop("indices", None)
        receipt["recurrent_state"] = self._recurrent_drain(receipt["status"] == "captured")
        return receipt


def initialize_runner(runner, *, recurrent_input_counts=None, recurrent_common_rows=None):
    global _collector, _startup_error
    from sglang.srt.runtime_context import get_parallel
    if get_parallel().tp_rank != 0:
        return
    try:
        if _collector is not None:
            raise ValueError("Collector initialized more than once")
        config = runner.server_args.resolved_dict()
        required = {"disable_cuda_graph": True, "page_size": 1, "enable_memory_saver": False,
                    "enable_unified_memory": False, "enable_hierarchical_cache": False,
                    "enable_unified_cache_external_linker": False}
        if any(config[name] != value for name, value in required.items()):
            raise ValueError("Collector actual graph/page/memory/cache config differs from qualified WIT")
        if get_parallel().pp_size != 1 or get_parallel().attn_cp_size != 1:
            raise ValueError("Collector requires qualified PP1/CP1")
        import torch
        _collector = Collector(torch, runner.token_to_kv_pool_allocator, runner.token_to_kv_pool,
                                stream_scalar=lambda device: torch._C._cuda_getCurrentRawStream(device.index))
        if recurrent_input_counts is not None or recurrent_common_rows is not None:
            try:
                _collector.initialize_recurrent(runner.req_to_token_pool, recurrent_input_counts, recurrent_common_rows)
            except Exception as error:
                _collector._recurrent_error("allocation", error)
    except Exception as error:
        _startup_error = {"stage": "preallocation", "error_type": type(error).__name__, "message": str(error)}


def observe(method, *args, **kwargs):
    if _collector is None:
        return
    try:
        getattr(_collector, method)(*args, **kwargs)
    except Exception as error:
        if method.startswith("recurrent_"):
            rid = None
            _collector._recurrent_error(method, error, rid)
        else:
            _collector.invalidate(None, WINDOW_START, WINDOW_END, method, error)


def drain(requested=False):
    if _collector is None:
        return {"schema": "kv-coherence-v1", "process_id": os.getpid(), "status": "unverified",
                "native_binding": None, "binding_error": None,
                "errors": (_startup_error,) if _startup_error else (), "numeric_acceptance": None,
                "reason": "Responding collector unavailable; no device readback",
                "recurrent_state": {"schema": "recurrent-state-v1", "process_id": os.getpid(),
                                    "status": "unverified", "records": [], "comparisons": [], "replays": [],
                                    "coverage": {"scope": "Responding collector unavailable"},
                                    "errors": (), "reason": "No collector; no capture or replay"}}
    return _collector.drain(requested)
# END INSTALLED RUNTIME


_RUNTIME = "srt/kv_coherence.py"
_HTTP = "srt/entrypoints/http_server.py"
_CONTROL = "srt/managers/tokenizer_control_mixin.py"
_IO = "srt/managers/io_struct.py"
_OUTPUT = "srt/managers/scheduler_components/output_streamer.py"
_IMPORT = "from sglang.srt.kv_coherence import observe as _kv_observe\n"
_EXTRA_PINS = {
    _HTTP: "329e4e1552b176f0753303a17df65dc49c0a59f1e642979a3537ad3a0d953b0a",
    _CONTROL: "aadd92f9f77cc59c4a7496f24890b7e9c6361897408a8330e1141f6ece5ace46",
    _IO: "1f94aca08ed27f74280e87ec80999df32df3088be987ec1377ff2f572e13739b",
    _OUTPUT: "77c07830c2e2e9529d7490a515898848d2f844eff46782ac9dab6e675bf15287",
}


def _runtime_source():
    source = Path(__file__).read_text().split("# BEGIN INSTALLED RUNTIME\n", 1)[1].split("# END INSTALLED RUNTIME", 1)[0]
    return ('"""CUDA-only opt-in FULL KV observer; no cache decisions or new waits."""\n'
            "import hashlib\nimport math\nimport os\nimport threading\nfrom pathlib import Path\n\n" + source).encode()


def _edits(*, recurrent_input_counts=None, recurrent_common_rows=None):
    metadata = streams.metadata
    counts, common = recurrent_selection(recurrent_input_counts, recurrent_common_rows)
    initialization = ("        initialize_runner(self, recurrent_input_counts=" + repr(counts)
                      + ", recurrent_common_rows=" + repr(common) + ")\n") if counts else "        initialize_runner(self)\n"
    return {
        metadata._RUNNER: (("        self._init_post_memory_pool_components()\n",
                            "        self._init_post_memory_pool_components()\n"
                             "        from sglang.srt.kv_coherence import initialize_runner\n"
                             + initialization),),
        metadata._GDN: (("import torch\n", "import torch\n\n" + _IMPORT
                         + "from sglang.srt.model_executor.forward_context import get_forward_context, has_forward_context\n"),
                        ("        if needs_state_gather:\n            conv_states_contig = conv_states[cache_indices].contiguous()\n",
                         "        _kv_batch = get_forward_context().forward_batch if has_forward_context() else None\n"
                         '        _kv_observe("recurrent_begin", self, layer, _kv_batch, cache_indices,\n'
                         "                    conv_states, ssm_states, mixed_qkv, conv_fn=causal_conv1d_fn,\n"
                         "                    needs_state_gather=needs_state_gather)\n"
                         "        if needs_state_gather:\n            conv_states_contig = conv_states[cache_indices].contiguous()\n"),
                        ("            core_attn_out, last_recurrent_state, h = self.kernel_dispatcher.extend(\n",
                         '            _kv_observe("recurrent_inputs", layer, _kv_batch, mixed_qkv, query, key, value,\n'
                         "                        g, beta, query_start_loc, track_state=h_track_buf,\n"
                         "                        track_chunk_idx=forward_metadata.track_chunk_idx if h_track_buf is not None else None,\n"
                         '                        output=kwargs.get("linear_attn_output"))\n'
                         "            core_attn_out, last_recurrent_state, h = self.kernel_dispatcher.extend(\n"),
                        ("            if is_npu() and last_recurrent_state is not None:\n",
                         '            _kv_observe("recurrent_end", layer, _kv_batch, state_cache_indices,\n'
                         "                        conv_states_contig, ssm_states_contig, core_attn_out)\n"
                         "            if is_npu() and last_recurrent_state is not None:\n")),
        metadata._SCHEDULE: (("import torch\n", "import torch\n\n" + _IMPORT),
                             ('        _mamba_record("scheduler_track_boundary", (\n',
                              '        _kv_observe("register", req)\n        _mamba_record("scheduler_track_boundary", (\n')),
        streams._STORE: (("import torch\n", "import torch\n\n" + _IMPORT),
                         ('    _mamba_record("kv_store_stream", (\n',
                          '    _kv_observe("note_cpp", _kv_batch, k_cache, v_cache, indices,\n'
                          '                _kv_native_stream, _kv_torch_stream)\n'
                          '    _mamba_record("kv_store_stream", (\n')),
        streams._POOL: (("import torch\n", "import torch\n\n" + _IMPORT),
                        (streams._terminal("mha_set_kv_buffer_impl", indent=8, prefix_valid=False),
                         streams._terminal("mha_set_kv_buffer_impl", indent=8, prefix_valid=False)
                         + '        _kv_observe("fresh", self, layer_id - self.start_layer, loc, _kv_batch, "cpp")\n'),
                        (streams._terminal("mha_prefix_valid_triton_fp8", indent=12, prefix_valid=True),
                         streams._terminal("mha_prefix_valid_triton_fp8", indent=12, prefix_valid=True)
                         + '            _kv_observe("fresh", self, layer_id - self.start_layer, loc_2d, _kv_batch, "triton")\n'),
                        (streams._terminal("mha_prefix_valid_triton", indent=8, prefix_valid=True),
                         streams._terminal("mha_prefix_valid_triton", indent=8, prefix_valid=True)
                         + '        _kv_observe("fresh", self, layer_id - self.start_layer, loc_2d, _kv_batch, "triton")\n')),
        metadata._CACHE: (("import torch\n", "import torch\n\n" + _IMPORT),
                         ('        _mamba_record("checkpoint_insert_begin", (\n',
                          '        _kv_observe("insert", req, insert_params, page_aligned_len, self.tree_core)\n'
                          '        _mamba_record("checkpoint_insert_begin", (\n'),
                         ('        _mamba_record("canonical_kv_rebind_enqueued", (\n',
                          '        _kv_observe("rebind", req, new_indices, page_aligned_len, result)\n'
                          '        _mamba_record("canonical_kv_rebind_enqueued", (\n')),
        _OUTPUT: (("            acc.accept(req=req)\n", "            acc.accept(req=req)\n"
                    "            from sglang.srt.kv_coherence import observe as _kv_observe\n"
                    '            _kv_observe("finish", req)\n'),),
        _IO: (("class GetInternalStateReq(BaseReq, kw_only=True):\n    pass\n",
               "class GetInternalStateReq(BaseReq, kw_only=True):\n"
               "    kv_coherence_drain: bool = False\n"),),
        _CONTROL: (("    async def get_internal_state(self: TokenizerManager) -> List[Dict[Any, Any]]:\n",
                    "    async def get_internal_state(self: TokenizerManager, *, kv_coherence_drain=False) -> List[Dict[Any, Any]]:\n"),
                   ("        req = GetInternalStateReq()\n",
                    "        req = GetInternalStateReq(kv_coherence_drain=kv_coherence_drain)\n")),
        _HTTP: (("async def get_server_info():\n", "async def get_server_info(kv_coherence_drain: bool = False):\n"),
                ("    return await server_info()\n", "    return await server_info(kv_coherence_drain=kv_coherence_drain)\n"),
                ("async def server_info():\n", "async def server_info(kv_coherence_drain: bool = False):\n"),
                ("    ] = await _global_state.tokenizer_manager.get_internal_state()\n",
                 "    ] = await _global_state.tokenizer_manager.get_internal_state(\n"
                 "        kv_coherence_drain=kv_coherence_drain,\n"
                 "    )\n")),
        metadata._INTERNAL: ((metadata._EDITS[metadata._INTERNAL][1][1],
                             metadata._EDITS[metadata._INTERNAL][1][1]
                             + "        from sglang.srt.kv_coherence import drain as _kv_drain\n"
                             '        state["kv_coherence"] = _kv_drain(recv_req.kv_coherence_drain)\n'),),
    }


def _rewrite(relative, content, *, reverse=False, recurrent_input_counts=None, recurrent_common_rows=None):
    text = content.decode()
    edits = _edits(recurrent_input_counts=recurrent_input_counts, recurrent_common_rows=recurrent_common_rows).get(relative, ())
    for before, after in reversed(edits) if reverse else edits:
        old, new = (after, before) if reverse else (before, after)
        if text.count("\n" + old) != 1:
            raise ValueError(f"KV coherence source seam differs: {relative}")
        text = text.replace("\n" + old, "\n" + new)
    return text.encode()


def source_manifest(*, recurrent_input_counts=None, recurrent_common_rows=None):
    owner = streams.source_manifest()
    counts, common = recurrent_selection(recurrent_input_counts, recurrent_common_rows)
    return {"image": owner["image"], "distribution_version": owner["distribution_version"],
            "tvm_ffi_distribution_version": owner["tvm_ffi_distribution_version"],
            "composition": "selected-FP32 -> CPU metadata -> KV WIT -> production Rust observer -> coherence",
            "files": owner["files"], "additional_native_sha256": dict(_EXTRA_PINS),
            "runtime_sha256": streams.metadata._sha256(_runtime_source()),
            "recurrent_selection": {"input_counts": counts, "common_rows": common,
                                    "status": "configured" if counts else "unconfigured"}}


def compare_completion_vectors(output: Path, baseline: Path) -> dict:
    """Independent offline vector gate; never declares the KV metrics interpreted."""
    from tests.manual.agent_opd.probe_teacher_scoring import _comparison

    keys = ("pair", "phase", "mode", "source_uid", "sample_index", "repetition")
    def vectors(directory):
        rows = [json.loads(line) for line in (directory / "requests.jsonl").read_text().splitlines()]
        result = {}
        for row in rows:
            key = tuple(row[name] for name in keys)
            if key in result or row["status"] != "scored":
                raise ValueError("Completion gate requires unique successful logical request cases")
            result[key] = json.loads((directory / "completion_scores" / f"{row['request_id']}.json").read_text())
        if len(result) != SCORING_REQUEST_COUNT:
            raise ValueError("Completion gate requires exactly16 completion vectors")
        return result
    current, reference = vectors(output), vectors(baseline)
    if set(current) != set(reference):
        raise ValueError("Completion gate logical cases differ from the accepted baseline")
    rows = [{"case": dict(zip(keys, key)), **_comparison(reference[key], current[key])} for key in reference]
    counts = {"baseline_values": sum(len(value["log_probs"]) for value in reference.values()),
              "candidate_values": sum(len(value["log_probs"]) for value in current.values())}
    exact = all(row["token_ids_match"] and row["finite_log_probs"] and row["values_exact"] for row in rows)
    return {"schema": "kv-coherence-completion-gate-v1", "baseline": str(baseline), "output": str(output),
            "vectors": len(rows), **counts, "all16_6804_exact": exact and all(n == 6804 for n in counts.values()),
            "comparisons": rows, "interpretation": "PENDING independent source/thread/stream/physical OLD qualification"}


def prepare_package(root: Path, *, worker_tmpdir: Path) -> dict:
    """Copy the whole runtime package once and bind ordinary parent/child imports."""
    loaded = [name for name in sys.modules if name == "sglang" or name.startswith("sglang.")]
    if loaded:
        raise ValueError(f"Private diagnostic binding must precede all SGLang imports; already loaded {min(loaded)} ({len(loaded)} modules)")
    root, temporary = root.resolve(strict=True), worker_tmpdir.resolve(strict=True)
    if not (root / "__init__.py").is_file() or not temporary.is_dir() or temporary.is_relative_to(root):
        raise ValueError("Private runtime copy requires a regular SGLang package and separate existing worker TMPDIR")
    private = temporary / "kv-coherence-runtime" / "sglang"
    private.parent.mkdir(exist_ok=False)
    # Dereference source symlinks; a staged library must not write through to baseline.
    shutil.copytree(root, private, symlinks=False)
    search_path = str(private.parent)
    sys.path.insert(0, search_path)
    inherited = os.environ.get("PYTHONPATH")
    os.environ["PYTHONPATH"] = search_path + (os.pathsep + inherited if inherited else "")
    spec = importlib.util.find_spec("sglang")
    if spec is None or Path(spec.origin).resolve() != private / "__init__.py":
        raise ValueError("Ordinary SGLang import does not resolve to the private diagnostic package")
    return {"schema": "kv-coherence-package-v1", "source_package_root": str(root),
            "package_root": str(private), "worker_tmpdir": str(temporary),
            "import_origin": str(spec.origin), "child_pythonpath": os.environ["PYTHONPATH"],
            "copy_scope": "whole runtime SGLang package; no subset verifier clone",
            "serving_native_origin_sha": "PENDING actual server/runtime attestation"}


def prepare_source(root: Path, *, image: str, archive_dir: Path, build_receipt: Path,
                   recurrent_input_counts=None, recurrent_common_rows=None) -> dict:
    """Require a real production build receipt; no builder or missing-module fallback."""
    from tests.manual.agent_opd import sglang_rust_kv_observer as native

    selection = {"recurrent_input_counts": recurrent_input_counts, "recurrent_common_rows": recurrent_common_rows}
    manifest = source_manifest(**selection)
    if image != manifest["image"]:
        raise ValueError("KV coherence requires the qualified pinned image")
    for name, version in (("sglang", manifest["distribution_version"]),
                          ("apache-tvm-ffi", manifest["tvm_ffi_distribution_version"])):
        if importlib.metadata.version(name) != version:
            raise ValueError(f"KV coherence dependency version differs: {name}")
    root, archive_dir = root.resolve(), archive_dir.resolve()
    # The native owner validates/stages the compiled production artifact and adapter.
    native_receipt = native.prepare_source(root, image=image, archive_dir=archive_dir / "native_observer",
                                            build_receipt=build_receipt)
    if Path(native_receipt["package_root"]).resolve() != root:
        raise ValueError("Native observer receipt does not identify the selected private runtime package")
    current, before, after = {}, {}, {}
    relatives = set(manifest["files"]) | set(_EXTRA_PINS)
    ffi = importlib.metadata.distribution("apache-tvm-ffi")
    paths = {rel: Path(ffi.locate_file(rel)).resolve() if rel.startswith("tvm_ffi/") else root / rel
             for rel in sorted(relatives)}
    for relative, path in paths.items():
        content = path.read_bytes()
        baseline = content
        if relative in _edits(**selection):
            try:
                baseline = _rewrite(relative, content, reverse=True, **selection)
            except ValueError:
                pass
        before[relative], current[relative] = baseline, content
    # Qualify completed WIT bytes, not a substituted source snapshot.
    for relative, identity in manifest["files"].items():
        baseline = before[relative]
        unpatched = streams._rewrite(relative, baseline, reverse=True) if relative in streams._EDITS else baseline
        streams._qualified_baseline(relative, unpatched, identity)
        if streams._rewrite(relative, unpatched) != baseline:
            raise ValueError(f"KV coherence requires completed KV WIT composition: {relative}")
    for relative, digest in _EXTRA_PINS.items():
        if streams.metadata._sha256(before[relative]) != digest:
            raise ValueError(f"KV coherence additional native source differs: {relative}")
    for relative, baseline in before.items():
        candidate = _rewrite(relative, baseline, **selection)
        if current[relative] not in (baseline, candidate):
            raise ValueError(f"Unrecognized KV coherence source: {relative}")
        if relative.endswith(".py"):
            ast.parse(candidate, feature_version=(3, 10))
        after[relative] = candidate
    runtime = root / _RUNTIME
    installed = runtime.read_bytes() if runtime.exists() else b""
    if installed not in (b"", _runtime_source()):
        raise ValueError("Unrecognized KV coherence installed runtime")
    current[_RUNTIME], before[_RUNTIME], after[_RUNTIME] = installed, b"", _runtime_source()
    paths[_RUNTIME] = runtime
    artifacts = {"source_manifest.json": (json.dumps(manifest, indent=2) + "\n").encode()}
    diff = []
    for relative in before:
        artifacts[f"before/{relative}"], artifacts[f"after/{relative}"] = before[relative], after[relative]
        if before[relative] != after[relative]:
            diff.extend(difflib.unified_diff(before[relative].decode().splitlines(True),
                                             after[relative].decode().splitlines(True),
                                             fromfile=f"a/{relative}", tofile=f"b/{relative}"))
    artifacts["coherence.diff"] = "".join(diff).encode()
    for relative, content in artifacts.items():
        path = archive_dir / relative
        if path.exists() and path.read_bytes() != content:
            raise ValueError(f"KV coherence archive differs: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(content)
    changed = [relative for relative in after if current[relative] != after[relative]]
    for relative in changed:
        paths[relative].write_bytes(after[relative])
    observed = {rel: streams.metadata._sha256(path.read_bytes()) for rel, path in paths.items()}
    if observed != {rel: streams.metadata._sha256(value) for rel, value in after.items()}:
        raise ValueError("KV coherence source changed during preflight")
    receipt = {"schema": "kv-coherence-preparation-v1", "native_observer": native_receipt, "package_root": str(root),
               "manifest": manifest, "archive_dir": str(archive_dir), "changed_files": changed,
               "observed_after_sha256": observed, "readback_key": "kv_coherence",
                "preallocation": "two opaque RID banks after finalized backing; TP0 only",
                "recurrent_state": {"schema": "recurrent-state-v1", **manifest["recurrent_selection"],
                                    "preallocation": "four independent recurrent banks, descriptor-derived capped native rows",
                                    "native_capture_replay": "UNVERIFIED; CPU preparation only"},
               "native_gpu_capture": "PENDING; CPU preparation is not original OLD/FRESH/CUDA proof"}
    with (archive_dir / "preflight.jsonl").open("a") as stream:
        stream.write(json.dumps(receipt, allow_nan=False) + "\n")
    return receipt
