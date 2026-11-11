"""Isolated two-bank FULL KV diagnostic; CPU preparation is not CUDA proof.

The installed runtime observes original CPP stores and the production Rust
insert callback. It never walks the tree, changes a cache decision, or waits.
Only the explicit after-all internal-state drain reads device contents.
"""

import ast
import difflib
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


class Collector:
    """Own preallocated receipts; errors disqualify evidence, never serving."""

    def __init__(self, torch, allocator, root, *, stream_scalar):
        self.torch, self.stream_scalar = torch, stream_scalar
        self.start, self.end = WINDOW_START, WINDOW_END
        self.rows = self.end - self.start
        self.banks, self.by_rid, self.completed = [], {}, set()
        self.errors, self.pending_cpp, self.summary = [], {}, None
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

    def insert(self, req, params, page_aligned_len, tree_core):
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

    def drain(self, requested):
        if self.summary is not None:
            return self.summary
        receipt = {"schema": "kv-coherence-v1", "process_id": os.getpid(),
                   "status": "metadata_only", "topology": self.topology, "errors": tuple(self.errors),
                   "completed_rids": tuple(sorted(self.completed)),
                   "banks": [{"rid": bank["rid"], "insert": bank["insert"], "rebind": bank["rebind"],
                              "fragments": tuple(bank["fragments"]), "fresh_layers": tuple(sorted(bank["fresh_layers"])),
                              "errors": tuple(bank["errors"])} for bank in self.banks],
                   "coverage": "responding TP0 only; no all-TP gather", "numeric_acceptance": None}
        if not requested:
            return receipt
        if len(self.completed) != SCORING_REQUEST_COUNT:
            receipt.update(status="unverified", reason="Drain requires all16 distinct completed native scoring RIDs")
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
        return receipt


def initialize_runner(runner):
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
    except Exception as error:
        _startup_error = {"stage": "preallocation", "error_type": type(error).__name__, "message": str(error)}


def observe(method, *args):
    if _collector is None:
        return
    try:
        getattr(_collector, method)(*args)
    except Exception as error:
        _collector.invalidate(None, WINDOW_START, WINDOW_END, method, error)


def drain(requested=False):
    if _collector is None:
        return {"schema": "kv-coherence-v1", "process_id": os.getpid(), "status": "unverified",
                "errors": (_startup_error,) if _startup_error else (), "numeric_acceptance": None,
                "reason": "Responding collector unavailable; no device readback"}
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
            "import math\nimport os\nimport threading\n\n" + source).encode()


def _edits():
    metadata = streams.metadata
    return {
        metadata._RUNNER: (("        self._init_post_memory_pool_components()\n",
                            "        self._init_post_memory_pool_components()\n"
                            "        from sglang.srt.kv_coherence import initialize_runner\n"
                            "        initialize_runner(self)\n"),),
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


def _rewrite(relative, content, *, reverse=False):
    text = content.decode()
    edits = _edits().get(relative, ())
    for before, after in reversed(edits) if reverse else edits:
        old, new = (after, before) if reverse else (before, after)
        if text.count("\n" + old) != 1:
            raise ValueError(f"KV coherence source seam differs: {relative}")
        text = text.replace("\n" + old, "\n" + new)
    return text.encode()


def source_manifest():
    owner = streams.source_manifest()
    return {"image": owner["image"], "distribution_version": owner["distribution_version"],
            "tvm_ffi_distribution_version": owner["tvm_ffi_distribution_version"],
            "composition": "selected-FP32 -> CPU metadata -> KV WIT -> production Rust observer -> coherence",
            "files": owner["files"], "additional_native_sha256": dict(_EXTRA_PINS),
            "runtime_sha256": streams.metadata._sha256(_runtime_source())}


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


def prepare_source(root: Path, *, image: str, archive_dir: Path, build_receipt: Path) -> dict:
    """Require a real production build receipt; no builder or missing-module fallback."""
    from tests.manual.agent_opd import sglang_rust_kv_observer as native

    manifest = source_manifest()
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
        if relative in _edits():
            try:
                baseline = _rewrite(relative, content, reverse=True)
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
        candidate = _rewrite(relative, baseline)
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
               "native_gpu_capture": "PENDING; CPU preparation is not original OLD/FRESH/CUDA proof"}
    with (archive_dir / "preflight.jsonl").open("a") as stream:
        stream.write(json.dumps(receipt, allow_nan=False) + "\n")
    return receipt
