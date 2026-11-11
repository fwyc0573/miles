"""CPU tensor/source/RPC contracts, never production-native or CUDA acceptance."""

import ast
import copy
import hashlib
import json
import os
import sys
import subprocess
from contextlib import nullcontext
from enum import IntEnum, auto
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
import torch

from tests.manual.agent_opd import sglang_kv_coherence as coherence
from tests.manual.agent_opd import sglang_kv_streams as streams
from tests.manual.agent_opd import sglang_mamba_runtime_metadata as metadata
from tests.manual.agent_opd import sglang_mamba_snapshots as snapshots


_SOURCE = Path(__file__).resolve().parents[2] / (
    "task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111/"
    "exp-1111-102145-988437/source")


@pytest.fixture
def composed(tmp_path, monkeypatch):
    root = tmp_path / "sglang"
    retained = Path(os.environ.get("MILES_PINNED_SGLANG_SOURCE", _SOURCE))
    for relative in set(streams.source_manifest()["files"]) | set(coherence._EXTRA_PINS):
        if relative == metadata._RECORDER:
            continue
        source = retained / relative
        assert source.is_file(), f"Required pinned coherence source unavailable: {source}"
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    versions = {"sglang": streams.source_manifest()["distribution_version"], "apache-tvm-ffi": "0.1.11"}
    monkeypatch.setattr(streams.importlib.metadata, "version", versions.__getitem__)
    monkeypatch.setattr(streams.importlib.metadata, "distribution",
                        lambda name: SimpleNamespace(locate_file=lambda relative: root / relative))
    image = streams.source_manifest()["image"]
    snapshots.prepare_source(root, image=image, selected_fp32=True, archive_dir=tmp_path / "fp32")
    metadata.prepare_runtime_metadata(root, image=image, archive_dir=tmp_path / "metadata")
    streams.prepare_source(root, image=image, archive_dir=tmp_path / "wit")
    return root


def _prepare_di(root, archive, monkeypatch, **selection):
    from tests.manual.agent_opd import sglang_rust_kv_observer as native
    calls = []
    nested = {"scope": "DI only: compiled production-native qualification PENDING", "package_root": str(root),
              "fixture": ["exact", {"nested": True}]}

    def prepare(root_arg: Path, *, image: str, archive_dir: Path, build_receipt: Path) -> dict:
        assert root_arg == root and build_receipt == archive.parent / "not-a-real-build.json"
        assert not (root / coherence._RUNTIME).exists() or calls
        calls.append((root_arg, image, archive_dir, build_receipt))
        return nested

    monkeypatch.setattr(native, "prepare_source", prepare)
    receipt = coherence.prepare_source(root, image=coherence.source_manifest()["image"], archive_dir=archive,
                                       build_receipt=archive.parent / "not-a-real-build.json", **selection)
    return receipt, nested, calls


def test_source_composition_all_seams_receipt_and_original_attention(composed, tmp_path, monkeypatch):
    before = {str(p.relative_to(composed)): p.read_bytes() for p in composed.rglob("*") if p.is_file()}
    receipt, nested, calls = _prepare_di(composed, tmp_path / "coherence", monkeypatch)
    assert len(calls) == 1 and receipt["native_observer"] is nested
    assert set(receipt["changed_files"]) == set(coherence._edits()) | {coherence._RUNTIME}
    for relative, original in before.items():
        current = (composed / relative).read_bytes()
        assert (tmp_path / "coherence/before" / relative).read_bytes() == original
        assert (tmp_path / "coherence/after" / relative).read_bytes() == current
        if relative not in coherence._edits():
            assert current == original
    for relative in coherence._edits():
        ast.parse((composed / relative).read_bytes(), feature_version=(3, 10))
    cache = (composed / metadata._CACHE).read_text()
    start = cache.index("    def checkpoint_into_tree(")
    body = cache[start:cache.index("    def ", start + 5)]
    assert body.index("insert_params.value = values") < body.index('_kv_observe("insert"') < body.index("result = self.insert(insert_params)")
    assert body.index("self.req_to_token_pool.write(") < body.index('_kv_observe("rebind"')
    pool = (composed / streams._POOL).read_text()
    seam = "self._store_kv_layer(layer_id - self.start_layer, loc, cache_k, cache_v)"
    assert pool.index(seam) < pool.index('_kv_observe("fresh", self, layer_id - self.start_layer, loc, _kv_batch, "cpp")')
    runtime = ast.parse((composed / coherence._RUNTIME).read_bytes())
    capture_methods = {"fresh", "insert", "rebind", "__call__", "note_cpp"}
    for node in ast.walk(runtime):
        if isinstance(node, ast.FunctionDef) and node.name in capture_methods:
            attrs = {n.attr for n in ast.walk(node) if isinstance(n, ast.Attribute)}
            assert not attrs & {"cpu", "item", "tolist", "synchronize", "record_stream", "wait_stream", "get_kv_buffer", "node_by_id"}
    assert "torch.save" not in (composed / coherence._RUNTIME).read_text()
    assert "kv_coherence_artifact_dir" not in (composed / coherence._RUNTIME).read_text()


@pytest.mark.parametrize("failure", ["missing_build", "math", "rpc", "wit_absent"])
def test_preparation_rejects_missing_build_or_unknown_sources(composed, tmp_path, monkeypatch, failure):
    archive = tmp_path / "invalid"
    if failure == "missing_build":
        with pytest.raises((FileNotFoundError, ValueError)):
            coherence.prepare_source(composed, image=coherence.source_manifest()["image"], archive_dir=archive,
                                     build_receipt=tmp_path / "nonexistent-production-build.json")
        assert not (composed / coherence._RUNTIME).exists()
        return
    relative = snapshots._TRITON if failure == "math" else coherence._HTTP if failure == "rpc" else streams._CONTEXT
    path = composed / relative
    if failure == "wit_absent":
        path.write_bytes(streams._rewrite(relative, path.read_bytes(), reverse=True))
    else:
        path.write_bytes(path.read_bytes() + b"\n# unsupported\n")
    before = {p: p.read_bytes() for p in composed.rglob("*") if p.is_file()}
    with pytest.raises(ValueError):
        _prepare_di(composed, archive, monkeypatch)
    assert {p: p.read_bytes() for p in before} == before
    assert not (composed / coherence._RUNTIME).exists()


def _toy(monkeypatch, layers=2):
    monkeypatch.setattr(coherence, "WINDOW_START", 2)
    monkeypatch.setattr(coherence, "WINDOW_END", 6)
    pool = type("MHATokenToKVPool", (), {})()
    pool.post_capture_active = False
    pool.model_layer_ids = tuple(3 + 4 * n for n in range(layers))
    pool.k_buffer = [torch.arange(32).reshape(8, 1, 4).to(torch.bfloat16) + n for n in range(layers)]
    pool.v_buffer = [k + 100 for k in pool.k_buffer]
    root = type("HybridLinearKVPool", (), {})()
    root.post_capture_active, root.full_kv_pool = False, pool
    root.full_attention_layer_id_mapping = {layer: dense for dense, layer in enumerate(pool.model_layer_ids)}
    allocator = type("TokenToKVPoolAllocator", (), {})()
    allocator.page_size, allocator.size = 1, 8
    allocator.get_kvcache = lambda: root
    collector = coherence.Collector(torch, allocator, root, stream_scalar=lambda device: 17)
    return collector, pool


def _req(rid, *, eligible=True):
    return SimpleNamespace(rid=rid, return_logprob=True, logprob_start_len=0 if eligible else 100,
                           origin_input_ids=range(98942), kv=SimpleNamespace(cache_protected_len=2),
                            finished=lambda: True)


def _tree_core(module_file):
    # CPU fixture: exported object identity, not a loaded Rust ABI claim.
    bindings = ModuleType("cpu_fixture.mem_cache")
    bindings.__file__ = str(module_file)
    binding_class = type("RustUnifiedTreeCoreBinding", (), {"__module__": "builtins"})
    bindings.RustUnifiedTreeCoreBinding = binding_class
    core = type("RustUnifiedTreeCore", (), {"_bindings": bindings,
                "_binding_class": lambda self: bindings.RustUnifiedTreeCoreBinding})()
    core._binding = binding_class()
    return core


def _capture_bank(collector, pool, rid, q, *, fresh_delta=0):
    req = _req(rid)
    collector.register(req)
    loc = torch.tensor([0, 1, 2, 3], dtype=torch.int64)
    batch = SimpleNamespace(rids=[rid], extend_prefix_lens_cpu=[2], extend_seq_lens_cpu=[4],
                            forward_mode=SimpleNamespace(is_extend=lambda: True))
    for dense, (k, v) in enumerate(zip(pool.k_buffer, pool.v_buffer)):
        collector.note_cpp(batch, k, v, loc, 17, 17)
        collector.fresh(pool, dense, loc, batch, "cpp")
    params = SimpleNamespace(prev_prefix_len=2, value=torch.tensor([6, 7, 0, 1, 2, 3], dtype=torch.int64))
    collector.insert(req, params, 6, _tree_core(__file__))
    if q > 2:
        # A different original tensor owns the matching physical indices.
        original = torch.tensor([6, 7, 0, 1, 2, 3, 5], dtype=torch.int64)
        for k in pool.k_buffer:
            k[:q - 2] += fresh_delta
        collector(rid, 2, 6, 71, 0, q, original)
    result = SimpleNamespace(prefix_len=q, last_device_node=99, rotation_tail_declined=False)
    collector.rebind(req, params.value.clone(), 6, result)
    return params


@pytest.mark.parametrize("order", [("opaque-a", "opaque-b"), ("opaque-b", "opaque-a")])
def test_two_opaque_banks_full_capture_indices_metrics_only_after_all16(monkeypatch, order):
    collector, pool = _toy(monkeypatch)
    collector.register(_req("response-only", eligible=False))
    assert not collector.by_rid
    _capture_bank(collector, pool, order[0], 2)
    params = _capture_bank(collector, pool, order[1], 5, fresh_delta=1)
    assert params.old_full_observer == (collector, order[1], 2, 6)
    rids = [*order, *(f"other-{n}" for n in range(14))]
    for rid in rids[:-1]:
        collector.finish(_req(rid))
    original_cpu = torch.Tensor.cpu
    def forbidden_cpu(*args, **kwargs):
        raise AssertionError("Early/default drain must not read tensor contents")
    monkeypatch.setattr(torch.Tensor, "cpu", forbidden_cpu)
    assert collector.drain(False)['status'] == "metadata_only"
    assert collector.drain(True)['status'] == "unverified"
    collector.finish(_req(rids[-1]))
    monkeypatch.setattr(torch.Tensor, "cpu", original_cpu)
    receipt = collector.drain(True)
    assert receipt["status"] == "captured"
    assert receipt["banks"][0]["metrics"] is None and receipt["banks"][0]["physical"]["old_rows"] == 0
    warm = receipt["banks"][1]
    assert warm["physical"]["old_rows"] == 3
    assert all(warm["physical"][name] for name in ("writer_equals_FULL_insert_all_layers",
                                                   "original_OLD_equals_rebind", "rebind_suffix_equals_insert", "indices_in_bounds"))
    assert len(warm["metrics"]) == 4 and warm["metrics"][0]["max_absolute_error"] == 1
    assert len(json.dumps(receipt, allow_nan=False)) < 20000
    assert collector.drain(False) is receipt
    assert all("payload" not in bank and "indices" not in bank for bank in collector.banks)


@pytest.mark.parametrize("fault", ["none", "duplicate", "stream", "triton", "bank_exhaustion", "rebind"])
def test_capture_faults_are_observable_and_do_not_throw_serving(monkeypatch, fault):
    collector, pool = _toy(monkeypatch)
    params = _capture_bank(collector, pool, "rid", 2)
    if fault == "none":
        collector("rid", 2, 6, 71, 0, 5, None)
    elif fault == "duplicate":
        source = params.value
        collector("rid", 2, 6, 71, 0, 4, source)
        collector("rid", 2, 6, 71, 0, 4, source)
    elif fault == "bank_exhaustion":
        collector.register(_req("two"))
        collector.register(_req("three"))
    elif fault == "rebind":
        collector.rebind(_req("rid"), params.value, 6, SimpleNamespace(prefix_len=2, rotation_tail_declined=False))
    else:
        collector.banks[0]["fresh_layers"].clear()
        loc = torch.tensor([0, 1, 2, 3], dtype=torch.int64)
        batch = SimpleNamespace(rids=["rid"], extend_prefix_lens_cpu=[2], extend_seq_lens_cpu=[4],
                                forward_mode=SimpleNamespace(is_extend=lambda: True))
        if fault == "stream":
            collector.note_cpp(batch, pool.k_buffer[0], pool.v_buffer[0], loc, 18, 17)
        collector.fresh(pool, 0, loc, batch, "triton" if fault == "triton" else "cpp")
    assert collector.errors and collector.errors[-1]["message"]


@pytest.mark.parametrize("layers,payload,indices,total", [(16, 512, 2.375, 514.375), (10, 320, 1.625, 321.625)])
def test_real_descriptor_budget_not_fixed_model_name(layers, payload, indices, total):
    descriptor = SimpleNamespace(shape=(200000, 1, 256), element_size=lambda: 2)
    budget = coherence.capture_budget([(descriptor, descriptor)] * layers, 8192, 2)
    assert [budget[name] / 2**20 for name in ("payload_bytes", "index_bytes", "allocated_bytes")] == [payload, indices, total]


def test_flattened_writer_offsets_native_fragment_math_and_coverage():
    rows = coherence.writer_windows(["first", "target", "tail"], [0, 90112, 98304], [7, 8192, 3], 90112, 98304)
    assert rows == [("target", 90112, 8192, 90112, 98304, 7, 8199)]
    assert coherence.fragment_window(81920, 16147, 90112, 98304) == (90112, 98067, 8192, 16147)
    assert coherence.covered_once([(90112, 95000), (95000, 98067)], 90112, 98067)
    assert not coherence.covered_once([(90112, 95000), (94999, 98067)], 90112, 98067)
    assert coherence.covered_once([], 90112, 90112)


def _bind(root, relative, name, namespace):
    tree = ast.parse((root / relative).read_bytes())
    node = copy.deepcopy(next(n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name))
    node.decorator_list = []
    module = ast.Module(body=ast.parse("from __future__ import annotations").body + [node], type_ignores=[])
    exec(compile(module, relative, "exec"), namespace)
    return namespace[name]


@pytest.fixture
def forward_mode():
    relative = "srt/model_executor/forward_batch_info.py"
    tree = ast.parse((_SOURCE / relative).read_bytes())
    node = copy.deepcopy(next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "ForwardMode"))
    namespace = {"IntEnum": IntEnum, "auto": auto}
    module = ast.Module(body=ast.parse("from __future__ import annotations").body + [node], type_ignores=[])
    exec(compile(module, relative, "exec"), namespace)
    return namespace["ForwardMode"]


@pytest.fixture
def generated_callbacks(composed, tmp_path, monkeypatch):
    _prepare_di(composed, tmp_path / "coherence", monkeypatch)
    runtime = ModuleType("cpu_generated_kv_callbacks")
    exec(compile((composed / coherence._RUNTIME).read_bytes(), coherence._RUNTIME, "exec"), vars(runtime))
    toy, pool = _toy(monkeypatch)
    collector = runtime.Collector.__new__(runtime.Collector)
    vars(collector).update(vars(toy))
    runtime._collector = collector
    context = ModuleType("cpu_generated_forward_context")
    monkeypatch.setitem(sys.modules, context.__name__, context)
    exec(compile((composed / streams._CONTEXT).read_bytes(), streams._CONTEXT, "exec"), vars(context))
    source = (composed / streams._STORE).read_text()
    binding = next(line.strip() for line in source.splitlines() if line.strip().startswith("_kv_batch = "))

    def capture(batch, loc=None):
        assert not context.has_forward_context()
        scope = (context.forward_context(context.ForwardContext(attn_backend=None), forward_batch=batch)
                 if batch is not None else nullcontext())
        with scope:
            names = {"get_forward_context": context.get_forward_context, "has_forward_context": context.has_forward_context}
            exec(binding, names)
            assert names["_kv_batch"] is batch
            k, v = pool.k_buffer[0], pool.v_buffer[0]
            runtime.observe("note_cpp", names["_kv_batch"], k, v, loc, 17, 17)
            pending = dict(collector.pending_cpp)
            runtime.observe("fresh", pool, 0, loc, names["_kv_batch"], "cpp")
        assert not context.has_forward_context()
        return pending

    return collector, pool, capture


@pytest.mark.parametrize("mode,prefix,extend", [("DECODE", None, None), ("EXTEND", [0], [1])])
def test_generated_callbacks_use_actual_mode_scope_and_restore_context(generated_callbacks, forward_mode, mode, prefix, extend):
    collector, _, capture = generated_callbacks
    assert not forward_mode.DECODE.is_extend() and forward_mode.EXTEND.is_extend()
    batch = SimpleNamespace(rids=["ordinary-native-request"], extend_prefix_lens_cpu=prefix,
                            extend_seq_lens_cpu=extend, forward_mode=forward_mode[mode],
                            moe_num_token_non_padded=lambda: None)
    capture(None)
    capture(batch)
    assert collector.errors == [], collector.errors
    assert not collector.pending_cpp and not collector.by_rid


def test_generated_extend_missing_or_malformed_metadata_still_invalidates_unselected_rid(
        generated_callbacks, forward_mode):
    collector, _, capture = generated_callbacks
    for field, value in [("rids", None), ("extend_prefix_lens_cpu", None), ("extend_seq_lens_cpu", None),
                         ("extend_prefix_lens_cpu", [None]), ("extend_seq_lens_cpu", [-1]), ("extend_seq_lens_cpu", [])]:
        batch = SimpleNamespace(rids=["unselected-scoring-rid"], extend_prefix_lens_cpu=[0],
                                extend_seq_lens_cpu=[1], forward_mode=forward_mode.EXTEND,
                                moe_num_token_non_padded=lambda: None)
        setattr(batch, field, value)
        count = len(collector.errors)
        capture(batch)
        errors = collector.errors[count:]
        assert [error["stage"] for error in errors] == ["note_cpp", "fresh"], (field, value, errors)
        assert all(error["rid"] is None and error["message"] for error in errors)
        assert not collector.by_rid and not collector.pending_cpp
    assert len(collector.errors) == 12


def test_generated_extend_target_consumes_unchanged_cpp_key(generated_callbacks, forward_mode):
    collector, pool, capture = generated_callbacks
    collector.register(_req("target"))
    batch = SimpleNamespace(rids=["target"], extend_prefix_lens_cpu=[2], extend_seq_lens_cpu=[4],
                            forward_mode=forward_mode.EXTEND, moe_num_token_non_padded=lambda: None)
    loc = torch.tensor([0, 1, 2, 3], dtype=torch.int64)
    key = collector._key(batch, pool.k_buffer[0], pool.v_buffer[0], loc)
    assert capture(batch, loc) == {key: (17, 17)}
    assert not collector.pending_cpp and not collector.errors
    bank = collector.by_rid["target"]
    assert bank["fresh_layers"] == {0} and torch.equal(bank["indices"]["writer"][0], loc)


def test_generated_binding_identity_before_selection_and_one_shot(generated_callbacks, tmp_path, monkeypatch):
    collector, _, _ = generated_callbacks
    module_file = tmp_path / "cpu-binding-file"
    data = b"CPU disk bytes; not an actual native library"
    module_file.write_bytes(data)
    alias = tmp_path / "module-file-alias"
    alias.symlink_to(module_file)
    core = _tree_core(alias)
    reads, read_bytes = [], Path.read_bytes
    def read(path):
        reads.append(path)
        return read_bytes(path)
    monkeypatch.setattr(Path, "read_bytes", read)
    collector.insert(_req("ordinary-request", eligible=False), None, 0, core)
    assert not collector.by_rid and reads == [module_file.resolve()]
    identity = collector.native_binding
    assert identity == {"module": "cpu_fixture.mem_cache", "module_file": str(module_file.resolve()),
                        "module_sha256": hashlib.sha256(data).hexdigest(), "module_bytes": len(data),
                        "class": "RustUnifiedTreeCoreBinding", "class_module": "builtins",
                        "class_is_module_attribute": True, "factory_class_matches": True,
                        "process_id": os.getpid()}
    assert identity["class_module"] != identity["module"] and collector.binding_error is None
    def forbidden_read(path):
        raise AssertionError("Serving binding identity must not reread after its first attempt")
    monkeypatch.setattr(Path, "read_bytes", forbidden_read)
    collector.insert(_req("second-request", eligible=False), None, 0, object())
    receipt = collector.drain(False)
    assert receipt["native_binding"] is identity and receipt["binding_error"] is None
    assert not collector.errors and reads == [module_file.resolve()]


@pytest.mark.parametrize("fault,message", [("export", "differs from module export"),
    ("factory", "differs from adapter factory class"), ("missing_file", "FileNotFoundError")])
def test_binding_failure_isolated_once_and_blocks_complete_bank_metrics(monkeypatch, tmp_path, fault, message):
    collector, pool = _toy(monkeypatch)
    module_file = tmp_path / "cpu-binding-file"
    module_file.write_bytes(b"CPU binding failure fixture")
    core = _tree_core(module_file)
    if fault == "export":
        core._bindings.RustUnifiedTreeCoreBinding = type("RustUnifiedTreeCoreBinding", (), {})
    elif fault == "factory":
        core._binding_class = lambda: type("DifferentFactoryBinding", (), {})
    else:
        core._bindings.__file__ = str(tmp_path / "missing-binding-file")
    collector.insert(_req("ordinary-request", eligible=False), None, 0, core)
    error = collector.binding_error
    assert message in error and collector.errors[0]["stage"] == "native_binding"
    assert collector.drain(False)["status"] == "unverified"
    if fault != "missing_file":
        field = "class_is_module_attribute" if fault == "export" else "factory_class_matches"
        assert collector.native_binding[field] is False
    def forbidden(*args, **kwargs):
        raise AssertionError("Invalid/missing identity must not reread or compute tensor metrics")
    monkeypatch.setattr(Path, "read_bytes", forbidden)
    _capture_bank(collector, pool, "cold", 2)
    _capture_bank(collector, pool, "warm", 5)
    for rid in ("cold", "warm", *(f"scoring-{n}" for n in range(14))):
        collector.finish(_req(rid))
    monkeypatch.setattr(collector, "_physical", forbidden)
    monkeypatch.setattr(collector, "_metrics", forbidden)
    receipt = collector.drain(True)
    assert receipt["status"] == "unverified" and "binding identity" in receipt["reason"]
    assert receipt["binding_error"] == error and len(receipt["completed_rids"]) == 16
    assert len(collector.errors) == 1 and all(bank["fresh_layers"] == {0, 1} for bank in collector.banks)
    assert all("metrics" not in bank for bank in receipt["banks"])


def test_missing_serving_identity_and_unavailable_collector_receipts(monkeypatch):
    collector, _ = _toy(monkeypatch)
    for rid in range(16):
        collector.finish(_req(str(rid)))
    def forbidden(*args):
        raise AssertionError("Missing serving binding must disqualify before tensor metrics")
    monkeypatch.setattr(collector, "_metrics", forbidden)
    receipt = collector.drain(True)
    assert receipt["status"] == "unverified" and "binding identity" in receipt["reason"]
    assert receipt["native_binding"] is None and receipt["binding_error"] is None
    monkeypatch.setattr(coherence, "_collector", None)
    assert coherence.drain()["native_binding"] is None and coherence.drain()["binding_error"] is None


def test_real_rpc_source_bindings_default_false_and_true_forwarding(composed, tmp_path, monkeypatch):
    import asyncio
    _prepare_di(composed, tmp_path / "coherence", monkeypatch)
    calls = []
    async def get_state(**kwargs):
        calls.append(kwargs)
        return [{"kv_coherence": {"schema": "kv-coherence-v1", "status": "metadata_only"}}]
    namespace = {"json": json, "logger": SimpleNamespace(warning=lambda *args: None),
                 "_global_state": SimpleNamespace(tokenizer_manager=SimpleNamespace(
                     get_internal_state=get_state, server_args=object(), startup_time=0), scheduler_info=object()),
                 "build_server_info": lambda *args: {}, "msgspec_to_builtins": lambda x: x,
                 "redact_watermark_secrets": lambda x: x, "__version__": "CPU-source-binding"}
    namespace["server_info"] = _bind(composed, coherence._HTTP, "server_info", namespace)
    alias = _bind(composed, coherence._HTTP, "get_server_info", namespace)
    asyncio.run(alias())
    asyncio.run(alias(True))
    assert calls == [{"kv_coherence_drain": False}, {"kv_coherence_drain": True}]
    captured = []
    async def communicate(req):
        captured.append(req)
        return [SimpleNamespace(internal_state={"schema": "CPU-source-binding"})]
    get_internal = _bind(composed, coherence._CONTROL, "get_internal_state", {"GetInternalStateReq": SimpleNamespace})
    owner = SimpleNamespace(auto_create_handle_loop=lambda: None, get_internal_state_communicator=communicate)
    asyncio.run(get_internal(owner))
    asyncio.run(get_internal(owner, kv_coherence_drain=True))
    assert captured[0].kv_coherence_drain is False and captured[1].kv_coherence_drain is True
    import msgspec
    io_tree = ast.parse((composed / coherence._IO).read_bytes())
    cls = copy.deepcopy(next(n for n in io_tree.body if isinstance(n, ast.ClassDef) and n.name == "GetInternalStateReq"))
    io_namespace = {"BaseReq": msgspec.Struct}
    exec(compile(ast.Module(body=[cls], type_ignores=[]), coherence._IO, "exec"), io_namespace)
    req_type = io_namespace["GetInternalStateReq"]
    assert req_type().kv_coherence_drain is False
    assert msgspec.json.decode(msgspec.json.encode(req_type(kv_coherence_drain=True)), type=req_type).kv_coherence_drain is True
    dispatch = []
    runtime_module = ModuleType("sglang.srt.kv_coherence")
    runtime_module.drain = lambda requested=False: dispatch.append(requested) or {"schema": "CPU-only"}
    monkeypatch.setitem(sys.modules, runtime_module.__name__, runtime_module)
    names = ("_add_topology", "_add_memory_usage", "_add_disaggregation", "_add_elastic_ep",
             "_add_speculative", "_add_step_times", "_add_rust_server", "_add_env_vars")
    owner = SimpleNamespace(**{name: lambda state: None for name in names})
    method = _bind(composed, metadata._INTERNAL, "get_internal_state", {
        "get_context": lambda: SimpleNamespace(resolved_server_args_dict=lambda: {"custom_sigquit_handler": object()}),
        "get_parallel": lambda: object(), "_mamba_drain": lambda parallel: {"schema": "CPU-metadata"},
        "GetInternalStateReqOutput": SimpleNamespace, "msgspec_to_builtins": lambda value: value})
    assert method(owner, req_type()).internal_state["kv_coherence"] == {"schema": "CPU-only"}
    assert method(owner, req_type(kv_coherence_drain=True)).internal_state["mamba_runtime_metadata"] == {"schema": "CPU-metadata"}
    assert dispatch == [False, True]


@pytest.mark.parametrize("tp_rank", [0, 1])
def test_preallocation_fault_isolated_and_other_tp_inactive(monkeypatch, tp_rank):
    collector, pool = _toy(monkeypatch)
    module = ModuleType("sglang.srt.runtime_context")
    module.get_parallel = lambda: SimpleNamespace(tp_rank=tp_rank, pp_size=1, attn_cp_size=1)
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setattr(coherence, "_collector", None)
    monkeypatch.setattr(coherence, "_startup_error", None)
    config = SimpleNamespace(disable_cuda_graph=True, page_size=1, enable_memory_saver=False,
                             enable_unified_memory=False, enable_hierarchical_cache=False,
                             enable_unified_cache_external_linker=False)
    config.resolved_dict = lambda: {name: value for name, value in vars(config).items() if name != "resolved_dict"}
    allocator = type("TokenToKVPoolAllocator", (), {})()
    allocator.get_kvcache = lambda: collector.root
    allocator.page_size, allocator.size = 1, 8
    runner = SimpleNamespace(server_args=config, token_to_kv_pool_allocator=allocator, token_to_kv_pool=collector.root)
    allocations = []
    def fail(*args, **kwargs):
        allocations.append(kwargs)
        raise RuntimeError("CPU injected preallocation exhaustion; not actual GPU allocation")
    monkeypatch.setattr(torch, "empty", fail)
    coherence.initialize_runner(runner)
    assert coherence._collector is None
    assert bool(allocations) == (tp_rank == 0)
    assert bool(coherence._startup_error) == (tp_rank == 0)
    assert coherence.drain(True)["status"] == "unverified"


def _initializer_case(monkeypatch):
    collector, _ = _toy(monkeypatch)
    runtime = ModuleType("cpu_generated_kv_coherence")
    exec(compile(coherence._runtime_source(), "generated/srt/kv_coherence.py", "exec"), vars(runtime))
    runtime.WINDOW_START, runtime.WINDOW_END = 2, 6
    context = ModuleType("sglang.srt.runtime_context")
    context.get_parallel = lambda: SimpleNamespace(tp_rank=0, pp_size=1, attn_cp_size=1)
    monkeypatch.setitem(sys.modules, context.__name__, context)
    resolved = {"disable_cuda_graph": True, "page_size": 1, "enable_memory_saver": False,
                "enable_unified_memory": False, "enable_hierarchical_cache": False,
                "enable_unified_cache_external_linker": False}
    config = SimpleNamespace(**{**resolved, "page_size": None})
    reads = []
    def resolved_dict():
        reads.append("resolved_dict")
        return dict(resolved)
    config.resolved_dict = resolved_dict
    allocator = type("TokenToKVPoolAllocator", (), {})()
    allocator.page_size, allocator.size = 1, 8
    allocator.get_kvcache = lambda: collector.root
    runner = SimpleNamespace(server_args=config, token_to_kv_pool_allocator=allocator, token_to_kv_pool=collector.root)
    allocations, empty = [], torch.empty
    def allocate(*args, **kwargs):
        allocations.append((args, kwargs))
        return empty(*args, **kwargs)
    monkeypatch.setattr(torch, "empty", allocate)
    return runtime, runner, resolved, reads, allocations


def test_generated_initializer_uses_resolved_page_and_preserves_raw_input(monkeypatch):
    runtime, runner, resolved, reads, allocations = _initializer_case(monkeypatch)
    raw = {name: getattr(runner.server_args, name) for name in resolved}
    runtime.initialize_runner(runner)
    assert runner.server_args.page_size is None
    assert {name: getattr(runner.server_args, name) for name in resolved} == raw
    assert runtime._startup_error is None, runtime._startup_error
    assert runtime._collector is not None and len(runtime._collector.banks) == 2
    assert reads == ["resolved_dict"] and allocations


@pytest.mark.parametrize("field,value", [("disable_cuda_graph", False), ("page_size", 64),
    ("enable_memory_saver", True), ("enable_unified_memory", True), ("enable_hierarchical_cache", True),
    ("enable_unified_cache_external_linker", True)])
def test_generated_initializer_rejects_resolved_config_difference_before_allocation(monkeypatch, field, value):
    runtime, runner, resolved, reads, allocations = _initializer_case(monkeypatch)
    resolved[field] = value
    runtime.initialize_runner(runner)
    assert runtime._collector is None and not allocations
    assert reads == ["resolved_dict"] and runner.server_args.page_size is None
    assert runtime._startup_error["message"] == "Collector actual graph/page/memory/cache config differs from qualified WIT"


@pytest.mark.parametrize("fault,message", [
    ("allocator_page", "live allocator root and page1"), ("allocator_class", "TokenToKVPoolAllocator"),
    ("root_class", "HybridLinearKVPool/MHATokenToKVPool"), ("full_class", "HybridLinearKVPool/MHATokenToKVPool"),
    ("pp", "PP1/CP1"), ("cp", "PP1/CP1"), ("missing_interface", "resolved_dict")])
def test_generated_initializer_retains_independent_guards_before_allocation(monkeypatch, fault, message):
    runtime, runner, _, reads, allocations = _initializer_case(monkeypatch)
    allocator, root = runner.token_to_kv_pool_allocator, runner.token_to_kv_pool
    if fault == "allocator_page":
        allocator.page_size = 64
    elif fault == "allocator_class":
        runner.token_to_kv_pool_allocator = SimpleNamespace(**vars(allocator))
    elif fault == "root_class":
        runner.token_to_kv_pool = SimpleNamespace(**vars(root))
        allocator.get_kvcache = lambda: runner.token_to_kv_pool
    elif fault == "full_class":
        root.full_kv_pool = SimpleNamespace(**vars(root.full_kv_pool))
    elif fault in ("pp", "cp"):
        sys.modules["sglang.srt.runtime_context"].get_parallel = lambda: SimpleNamespace(
            tp_rank=0, pp_size=2 if fault == "pp" else 1, attn_cp_size=2 if fault == "cp" else 1)
    else:
        del runner.server_args.resolved_dict
    runtime.initialize_runner(runner)
    assert runtime._collector is None and not allocations
    assert reads == ([] if fault == "missing_interface" else ["resolved_dict"])
    assert message in runtime._startup_error["message"]
    assert runner.server_args.page_size is None


def test_retained_page_resolution_declares_without_mutating_raw_record():
    schedule = ast.parse((_SOURCE / "srt/arg_groups/fields/schedule.py").read_bytes())
    page = next(node for node in ast.walk(schedule) if isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name) and node.target.id == "page_size")
    assert isinstance(page.value, ast.Constant) and page.value.value is None
    assert any(isinstance(node, ast.keyword) and node.arg == "resolvable"
               and isinstance(node.value, ast.Constant) and node.value.value is True for node in ast.walk(page.annotation))
    relative = "srt/arg_groups/overrides.py"
    default = _bind(_SOURCE, relative, "_page_size_default", {
        "get_platform": lambda: SimpleNamespace(is_hip=False, is_musa=False)})
    declare = _bind(_SOURCE, relative, "declare_resolution", {
        "is_record": lambda cfg: False, "get_context": lambda: SimpleNamespace(server_args=None)})
    def unexpected_fallback(*args):
        raise AssertionError("Declared page_size must be resolved before any fallback")
    result = _bind(_SOURCE, relative, "resolution_result", {"with_fallback": unexpected_fallback})
    # Exact retained functions, but plain CPU inputs/platform predicates, not full ServerArgs bootstrap.
    config = SimpleNamespace(page_size=None, _raw_input={"page_size": None})
    decision = default(config)
    assert decision == {"page_size": 1} and config.page_size is None
    declare(config, "_page_size_default", **decision)
    assert config._resolved_overrides == [("_page_size_default", {"page_size": 1})]
    assert result(config, "page_size") == 1
    assert config.page_size is None and config._raw_input == {"page_size": None}
    setter = _bind(_SOURCE, "srt/server_args.py", "__setattr__", {})
    config._resolution_finished = True
    with pytest.raises(AttributeError, match="read-only"):
        setter(config, "page_size", 1)
    assert config.page_size is None


def test_metrics_zero_reference_and_nonfinite_never_manufacture_equality(monkeypatch):
    collector, pool = _toy(monkeypatch, layers=1)
    _capture_bank(collector, pool, "warm", 5)
    bank = collector.by_rid["warm"]
    old_k, old_v = bank["payload"]["old"][0]
    fresh_k, fresh_v = bank["payload"]["fresh"][0]
    old_k[:3].zero_()
    fresh_k[:3].fill_(0.25)
    old_v[:3].fill_(float("inf"))
    fresh_v[:3].fill_(float("inf"))
    metrics = collector._metrics(bank)
    assert metrics[0]["max_absolute_error"] == 0.25 and metrics[0]["max_relative_error"] is None
    assert metrics[0]["relative_error_undefined_count"] == 12
    assert metrics[1]["old_nonfinite_count"] == metrics[1]["fresh_nonfinite_count"] == 12
    assert metrics[1]["values_exact"] is False and metrics[1]["max_absolute_error"] is None
    json.dumps(metrics, allow_nan=False)


@pytest.mark.parametrize("fault", [None, "values", "tokens", "count"])
def test_independent_all16_6804_completion_gate_uses_existing_comparison(tmp_path, fault):
    for directory in (tmp_path / "baseline", tmp_path / "candidate"):
        (directory / "completion_scores").mkdir(parents=True)
        rows = []
        for n in range(16):
            count = 425 if n < 15 else 429
            vector = {"token_ids": list(range(count)), "log_probs": [0.0, *([-2.0] * (count - 1))]}
            if directory.name == "candidate" and n == 15:
                if fault == "values":
                    vector["log_probs"][-1] = -2.5
                elif fault == "tokens":
                    vector["token_ids"][-1] = 99999
                elif fault == "count":
                    vector["log_probs"].pop()
                    vector["token_ids"].pop()
            row = {"pair": "A", "phase": "cold" if n < 8 else "warm_stream", "mode": "full_input" if n % 2 == 0 else "response_only",
                   "source_uid": f"sample-{n % 8}", "sample_index": n % 8, "repetition": 0,
                   "request_id": str(n), "status": "scored"}
            rows.append(row)
            (directory / "completion_scores" / f"{n}.json").write_text(json.dumps(vector))
        (directory / "requests.jsonl").write_text("".join(json.dumps(row) + "\n" for row in rows))
    result = coherence.compare_completion_vectors(tmp_path / "candidate", tmp_path / "baseline")
    assert result["all16_6804_exact"] == (fault is None)
    assert result["baseline_values"] == 6804 and result["vectors"] == 16
    assert result["comparisons"][0]["relative_error_undefined_count"] == 1
    if fault == "values":
        assert result["comparisons"][-1]["max_absolute_error"] == 0.5
        assert result["comparisons"][-1]["max_relative_error"] == 0.25
    assert result["interpretation"].startswith("PENDING independent source")


def _binding_in_fresh_process(name, tmp_path, *, composed=False):
    # The repository conftest imports SGLang; test a clean worker, never purge it.
    root = Path(__file__).resolve().parents[2]
    arguments = "module.composed.__wrapped__(directory, patch), directory, patch" if composed else "directory, patch"
    code = ("import pytest\nfrom pathlib import Path\nfrom tests.fast import test_sglang_kv_coherence as module\n"
            f"directory = Path({str(tmp_path)!r})\n"
            "with pytest.MonkeyPatch.context() as patch:\n"
            f"    module.{name}({arguments})\n"
            f"print('CPU_PRIVATE_BINDING_TEST_PASS', {name!r})\n")
    stdout = subprocess.check_output([sys.executable, "-B", "-c", code], cwd=root, text=True, timeout=30)
    assert f"CPU_PRIVATE_BINDING_TEST_PASS {name}" in stdout


def test_whole_private_package_binding_and_real_child_import_leave_baseline_unchanged(tmp_path):
    _binding_in_fresh_process("_whole_private_package_binding", tmp_path)


def _whole_private_package_binding(tmp_path, monkeypatch):
    baseline, temporary = tmp_path / "installed" / "sglang", tmp_path / "worker-tmp"
    baseline.mkdir(parents=True)
    temporary.mkdir()
    (baseline / "__init__.py").write_text('VALUE = "ordinary private import"\n')
    (baseline / "srt").mkdir()
    (baseline / "srt/__init__.py").write_text("")
    # Not in any collector manifest: the runtime copy must not select a verifier subset.
    (baseline / "srt/not_a_manifest_member.py").write_text("VALUE = 73\n")
    external = tmp_path / "original-library-bytes"
    external.write_bytes(b"CPU copy fixture; not a native binary")
    (baseline / "library-link").symlink_to(external)
    (baseline / "launch_server.py").write_text(
        "import json,sglang\nfrom sglang.srt import not_a_manifest_member as module\n"
        "print(json.dumps({'origin':sglang.__file__,'module_origin':module.__file__,'value':module.VALUE}))\n")
    before = {path: path.read_bytes() for path in baseline.rglob("*") if path.is_file()}
    monkeypatch.syspath_prepend(str(baseline.parent))
    monkeypatch.setenv("PYTHONPATH", "preserved-repository-path")
    assert Path(coherence.importlib.util.find_spec("sglang").origin).parent == baseline
    receipt = coherence.prepare_package(baseline, worker_tmpdir=temporary)
    private = Path(receipt["package_root"])
    assert Path(coherence.importlib.util.find_spec("sglang").origin).parent == private
    assert "sglang" not in sys.modules and private != baseline
    assert not (private / "library-link").is_symlink()
    (private / "library-link").write_bytes(b"changed only private fixture")
    command = [sys.executable, "-B", "-m", "sglang.launch_server"]
    result = json.loads(subprocess.check_output(command, cwd=tmp_path, env=dict(os.environ), text=True, timeout=10))
    assert Path(result["origin"]).parent == private
    assert Path(result["module_origin"]) == private / "srt/not_a_manifest_member.py" and result["value"] == 73
    assert {path: path.read_bytes() for path in before} == before
    assert receipt["child_pythonpath"].endswith(os.pathsep + "preserved-repository-path")
    assert receipt["serving_native_origin_sha"].startswith("PENDING")


@pytest.mark.parametrize("loaded", ["sglang", "sglang.srt.layers.attention", "sglang.srt.mem_cache.rust_tree_core.mem_cache"])
def test_private_binding_rejects_prior_import_without_purge_copy_or_path_change(tmp_path, monkeypatch, loaded):
    baseline, temporary = tmp_path / "sglang", tmp_path / "worker-tmp"
    baseline.mkdir()
    temporary.mkdir()
    (baseline / "__init__.py").write_text("")
    module = ModuleType(loaded)
    monkeypatch.setitem(sys.modules, loaded, module)
    paths, environment = list(sys.path), dict(os.environ)
    with pytest.raises(ValueError, match="precede all SGLang imports"):
        coherence.prepare_package(baseline, worker_tmpdir=temporary)
    assert sys.modules[loaded] is module and sys.path == paths and dict(os.environ) == environment
    assert not (temporary / "kv-coherence-runtime").exists()


def test_real_native_preparer_join_is_blocked_on_pending_build_in_selected_private_root(tmp_path):
    _binding_in_fresh_process("_real_native_pending_binding", tmp_path, composed=True)


def _real_native_pending_binding(composed, tmp_path, monkeypatch):
    from tests.manual.agent_opd import sglang_rust_kv_observer as native
    (composed / "__init__.py").write_bytes((_SOURCE / "__init__.py").read_bytes())
    before = {p: p.read_bytes() for p in composed.rglob("*") if p.is_file()}
    temporary = tmp_path / "worker-tmp"
    temporary.mkdir()
    monkeypatch.setattr(sys, "path", list(sys.path))
    monkeypatch.setenv("PYTHONPATH", os.environ.get("PYTHONPATH", ""))
    package = coherence.prepare_package(composed, worker_tmpdir=temporary)
    private = Path(package["package_root"])
    build = tmp_path / "pending-real-production-build.json"
    build.write_text(json.dumps({"status": "PENDING", "image": native.IMAGE, "module": native.MODULE}))
    actual, calls = native.prepare_source, []
    def called(root: Path, *, image: str, archive_dir: Path, build_receipt: Path) -> dict:
        calls.append((root, image, archive_dir, build_receipt))
        return actual(root, image=image, archive_dir=archive_dir, build_receipt=build_receipt)
    monkeypatch.setattr(native, "prepare_source", called)
    with pytest.raises(ValueError, match="passing pinned CPU observer build receipt"):
        coherence.prepare_source(private, image=native.IMAGE, archive_dir=tmp_path / "coherence",
                                 build_receipt=build)
    assert len(calls) == 1 and calls[0][0] == private != composed
    assert Path(coherence.importlib.util.find_spec("sglang").origin).parent == private
    assert not (private / coherence._RUNTIME).exists()
    assert native.MODULE not in sys.modules and {p: p.read_bytes() for p in before} == before


def test_worker_private_binding_precedes_real_transitive_sglang_import(tmp_path):
    _binding_in_fresh_process("_worker_private_before_first_sglang_import", tmp_path)


def _worker_private_before_first_sglang_import(tmp_path, monkeypatch):
    import builtins
    from tests.manual.agent_opd import probe_teacher_scoring as probe
    baseline = tmp_path / "installed/sglang"
    baseline.mkdir(parents=True)
    (baseline / "__init__.py").write_text("# CPU import-order fixture\n")
    monkeypatch.syspath_prepend(str(baseline.parent))
    monkeypatch.setenv("PYTHONPATH", os.environ.get("PYTHONPATH", ""))
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"kv_coherence_capture": True, "selected_fp32_snapshots": True,
        "mamba_runtime_metadata": True, "kv_store_stream_witness": True,
        "kv_coherence_build_receipt": "PENDING", "recurrent_sample_original_indices": [1693, 1695],
        "worker_local_root": str(tmp_path / "worker-local")}))
    owner, seen = builtins.__import__, []
    def importing(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "sglang" or name.startswith("sglang."):
            private = Path(probe.importlib.util.find_spec("sglang").origin).parent
            assert private != baseline and private.is_relative_to(tmp_path / "worker-local")
            assert Path(os.environ["PYTHONPATH"].split(os.pathsep)[0]) == private.parent
            assert (private / "__init__.py").read_bytes() == (baseline / "__init__.py").read_bytes()
            seen.append(name)
            raise RuntimeError("CPU test stopped before first actual SGLang import")
        return owner(name, globals, locals, fromlist, level)
    monkeypatch.setattr(builtins, "__import__", importing)
    with pytest.raises(RuntimeError, match="before first actual SGLang import"):
        probe._run(SimpleNamespace(config=config))
    assert seen == ["sglang.srt.environ"]  # Real qwen worker -> training script import.
    assert "sglang" not in sys.modules


def test_recurrent_selected_real_source_anchors_hashes_and_once_only_preparer(composed, tmp_path, monkeypatch):
    selection = {"recurrent_input_counts": (97365, 98942), "recurrent_common_rows": 6519}
    receipt, _, calls = _prepare_di(composed, tmp_path / "recurrent", monkeypatch, **selection)
    assert len(calls) == 1
    assert receipt["manifest"]["recurrent_selection"] == {
        "input_counts": (97365, 98942), "common_rows": 6519, "status": "configured"}
    runner = (composed / metadata._RUNNER).read_text()
    assert "initialize_runner(self, recurrent_input_counts=(97365, 98942), recurrent_common_rows=6519)" in runner
    source = (composed / metadata._GDN).read_text()
    begin, inputs, end = (source.index(f'_kv_observe("recurrent_{name}"') for name in ("begin", "inputs", "end"))
    assert source.index("needs_state_gather = (") < begin < source.index("conv_states_contig = conv_states[cache_indices]")
    assert begin < source.index("conv_states[forward_metadata.conv_states_mask_indices] =")
    assert source.index("mixed_qkv = self._convolve_prefill(") < inputs
    assert source.index("g, beta = self._prefill_gates(layer, a, b)") < inputs
    assert inputs < source.index("core_attn_out, last_recurrent_state, h = self.kernel_dispatcher.extend(") < end
    assert end < source.index("if is_npu() and last_recurrent_state is not None:")
    assert "_kv_batch = get_forward_context().forward_batch if has_forward_context() else None" in source
    assert coherence._rewrite(metadata._GDN, (composed / metadata._GDN).read_bytes(), reverse=True, **selection) == (
        tmp_path / "recurrent/before" / metadata._GDN).read_bytes()
    for relative, digest in receipt["observed_after_sha256"].items():
        assert hashlib.sha256((composed / relative).read_bytes()).hexdigest() == digest
    assert receipt["manifest"]["runtime_sha256"] == receipt["observed_after_sha256"][coherence._RUNTIME]
    # Changing the bound selection is tampering, not an idempotent second mode.
    with pytest.raises(ValueError):
        coherence._rewrite(metadata._RUNNER, (composed / metadata._RUNNER).read_bytes(), reverse=True)
    runtime = ast.parse((composed / coherence._RUNTIME).read_text())
    capture = {"recurrent_begin", "recurrent_inputs", "recurrent_end", "_recurrent_copy", "_recurrent_state_copy",
               "_recurrent_publication", "_recurrent_rebind", "_recurrent_target"}
    for node in ast.walk(runtime):
        if isinstance(node, ast.FunctionDef) and node.name in capture:
            attrs = {part.attr for part in ast.walk(node) if isinstance(part, ast.Attribute)}
            assert not attrs & {"cpu", "item", "tolist", "synchronize", "wait_stream", "record_stream", "node_by_id"}
    assert not any(isinstance(node, ast.Attribute) and node.attr in (
        "synchronize", "wait_stream", "record_stream", "reset_peak_memory_stats", "empty_cache", "save")
                   for node in ast.walk(runtime))


@pytest.mark.parametrize("counts,common", [(None, 1), ((97365,), 1), ((97365, 97365), 1),
    ((97365, 98942), 7254), ((97365, 98942), 0)])
def test_recurrent_selection_rejects_unbound_or_noncommon_input(counts, common):
    with pytest.raises(ValueError):
        coherence.recurrent_selection(counts, common)


def _recurrent_toy(monkeypatch):
    collector, pool = _toy(monkeypatch, layers=1)
    # CPU pinning and allocator-stat DI; no CUDA or real native implementation.
    class CpuCopies:
        def __getattr__(self, name):
            return getattr(torch, name)

        def empty(self, *args, **kwargs):
            kwargs.pop("pin_memory", None)
            return torch.empty(*args, **kwargs)

        cuda = SimpleNamespace(**{name: lambda device: 123 for name in (
            "memory_allocated", "memory_reserved", "max_memory_allocated", "max_memory_reserved")})
    collector.torch = CpuCopies()
    conv = torch.arange(24).reshape(4, 2, 3).to(torch.bfloat16)
    temporal = torch.arange(16).reshape(4, 1, 2, 2).float()
    req_pool = SimpleNamespace(layer_transfer_counter=None, mamba_map={0: 0},
        mamba_pool=SimpleNamespace(mamba2_layer_cache=lambda layer: SimpleNamespace(conv=[conv], temporal=temporal)),
        translate_mamba_indices=lambda indices: indices)
    collector.initialize_recurrent(req_pool, (5, 8), 2)
    assert not collector.recurrent["errors"]
    return collector, pool, conv, temporal


def _recurrent_capture(collector, conv, temporal, rid, input_count, *, delta=0, track=False):
    req = _req(rid)
    req.origin_input_ids = range(input_count)
    collector.register(req)
    rows = min(collector.rows, input_count - collector.start)
    batch = SimpleNamespace(rids=[rid], extend_prefix_lens_cpu=[collector.start], extend_seq_lens_cpu=[rows],
        extend_prefix_lens=torch.tensor([collector.start], dtype=torch.int32),
        forward_mode=SimpleNamespace(is_extend=lambda: True))
    indices = torch.tensor([1], dtype=torch.int32)
    query = torch.tensor([0, rows], dtype=torch.int32)
    layer = SimpleNamespace(layer_id=0, conv_weights=torch.ones(2, 4, dtype=torch.bfloat16),
                            bias=None, activation="silu", head_k_dim=2)
    calls = []
    def conv_call(x, weight, bias, **kwargs):
        calls.append(("conv", tuple(x.stride()), kwargs["seq_lens_cpu"], kwargs["cache_indices"].clone()))
        assert x.stride() == (1, 3)
        kwargs["conv_states"][kwargs["cache_indices"].long()] += 2
        return x * 2
    class Dispatcher:
        extend_kernel = SimpleNamespace()
        def extend(self, **kwargs):
            calls.append(("temporal", kwargs["track_state"] is not None, kwargs["track_chunk_idx"]))
            states, slots = kwargs["ssm_states"], kwargs["cache_indices"].long()
            output = kwargs["v"] + states[slots[0], 0, 0, 0]
            states[slots] += 3
            if kwargs["track_state"] is not None:
                kwargs["track_state"].copy_(states[slots])
            return output, None, torch.empty(0)
    forward = SimpleNamespace(query_start_loc=query, conv_block_table=None,
        has_mamba_track_mask=track, num_state_checkpoints=None, state_checkpoint_every_n_tokens=None,
        state_checkpoint_cu_starts=None, track_conv_indices=torch.tensor([[rows - 3, rows - 2, rows - 1]]),
        conv_states_mask_indices=torch.tensor([2], dtype=torch.int64))
    backend = SimpleNamespace(forward_metadata=forward, kernel_dispatcher=Dispatcher())
    mixed = torch.empty_strided((rows, 2), (3, 1), dtype=torch.bfloat16)
    mixed.copy_(torch.arange(rows * 2).reshape(rows, 2) + delta)
    collector.recurrent_begin(backend, layer, batch, indices, conv, temporal, mixed,
                              conv_fn=conv_call, needs_state_gather=False)
    if track:
        conv[forward.conv_states_mask_indices] = mixed[forward.track_conv_indices].transpose(1, 2)
    post = conv_call(mixed.transpose(0, 1), layer.conv_weights, None, conv_states=conv,
                     cache_indices=indices, seq_lens_cpu=[rows]).transpose(0, 1)
    q, k, v = (post.reshape(1, rows, 1, 2).contiguous().clone() for _ in range(3))
    g = torch.ones(1, rows, 1)
    beta = torch.ones(1, rows, 1)
    track_state = torch.empty((1, *temporal.shape[1:])) if track else None
    track_idx = torch.tensor([0], dtype=torch.int32) if track else None
    collector.recurrent_inputs(layer, batch, post, q, k, v, g, beta, query,
                               track_state=track_state, track_chunk_idx=track_idx, output=None)
    output, _, _ = backend.kernel_dispatcher.extend(q=q, k=k, v=v, g=g, beta=beta,
        ssm_states=temporal, cache_indices=indices, track_state=track_state, track_chunk_idx=track_idx)
    collector.recurrent_end(layer, batch, indices, conv, temporal, output)
    return req, calls


def test_recurrent_four_independent_candidates_copy_before_mutation_and_private_controls(monkeypatch):
    collector, full, conv, temporal = _recurrent_toy(monkeypatch)
    requests, calls = [], []
    for rid, count in (("opaque-z", 8), ("opaque-a", 5), ("opaque-c", 8), ("opaque-b", 5)):
        initial_conv, initial_temporal = conv[1:2].clone(), temporal[1:2].clone()
        req, native_calls = _recurrent_capture(collector, conv, temporal, rid, count, track=True)
        requests.append(req)
        calls.append(native_calls)
        bank = collector.recurrent["by_rid"][rid]
        assert torch.equal(bank["host"]["initial_conv"], initial_conv)
        assert torch.equal(bank["host"]["initial_temporal"], initial_temporal)
        assert not torch.equal(bank["host"]["initial_temporal"], temporal[1:2])
        assert bank["descriptors"]["conv_input"]["stride"] == (3, 1)
    assert not collector.by_rid and len(collector.recurrent["by_rid"]) == 4
    # Prove existing FULL selection remains two opaque 98942-input banks.
    _capture_bank(collector, full, "full-one", 2)
    _capture_bank(collector, full, "full-two", 5)
    for req in requests:
        collector.finish(req)
    for rid in ("full-one", "full-two", *(f"ordinary-{i}" for i in range(10))):
        collector.finish(_req(rid))
    saved_conv, saved_temporal = conv.clone(), temporal.clone()
    def forbidden(*args, **kwargs):
        raise AssertionError("Metadata-only drain must not inspect host captures or replay")
    original = collector._recurrent_value
    monkeypatch.setattr(collector, "_recurrent_value", forbidden)
    assert collector.drain(False)["recurrent_state"]["status"] == "metadata_only"
    monkeypatch.setattr(collector, "_recurrent_value", original)
    receipt = collector.drain(True)
    recurrent = receipt["recurrent_state"]
    assert receipt["status"] == recurrent["status"] == "captured", recurrent
    assert len(recurrent["records"]) == 4 and len(recurrent["comparisons"]) == 6
    controls = [r for r in recurrent["replays"] if r["kind"] == "control"]
    assert len(controls) == 8 and all(row["values_exact"] for row in controls)
    shapes = [r for r in recurrent["replays"] if r["kind"] == "shape"]
    assert len(shapes) == 4 and all(row["common_rows"] == 2 for row in shapes)
    assert any(r["kind"] == "state-sensitivity" for r in recurrent["replays"])
    assert torch.equal(conv, saved_conv) and torch.equal(temporal, saved_temporal)
    assert all(record["publication"]["canonical_value_status"] == "unverified" for record in recurrent["records"])
    assert all("host" not in bank and "dispatcher" not in bank for bank in collector.recurrent["banks"])
    call_count = sum(map(len, calls))
    assert collector.drain(True) is receipt and collector.drain(False) is receipt
    assert sum(map(len, calls)) == call_count
    assert recurrent["memory"]["after_replay"]["peak_allocated_bytes"] == 123
    assert len(json.dumps(receipt, allow_nan=False)) < 100000


def test_recurrent_error_isolation_mode_scope_publication_join_and_incomplete_drain(monkeypatch):
    collector, _, conv, temporal = _recurrent_toy(monkeypatch)
    monkeypatch.setattr(coherence, "_collector", collector)
    # DECODE's missing CPU lens is not an error or a reason to touch it.
    coherence.observe("recurrent_begin", None, SimpleNamespace(layer_id=0), SimpleNamespace(
        forward_mode=SimpleNamespace(is_extend=lambda: False)), None, None, None, None,
        conv_fn=None, needs_state_gather=False)
    assert not collector.recurrent["errors"] and not collector.errors
    req, _ = _recurrent_capture(collector, conv, temporal, "writer", 5)
    bank = collector.recurrent["by_rid"][req.rid]
    donor = SimpleNamespace(mamba_value=torch.tensor([1], dtype=torch.int32))
    collector._recurrent_publication(req, donor, collector.start)
    publication = bank["host"]["publication_temporal"].clone()
    temporal[1].zero_()
    assert torch.equal(bank["host"]["publication_temporal"], publication)
    collector._recurrent_rebind(req, collector.start, SimpleNamespace(last_device_node=7,
        prefix_len=collector.start, mamba_exist=True, rotation_tail_declined=False))
    assert bank["publication"]["canonical_value_status"] == "unverified"
    def error(*args, **kwargs):
        raise RuntimeError("Injected observation error before native mutation")
    monkeypatch.setattr(collector, "recurrent_inputs", error)
    assert coherence.observe("recurrent_inputs") is None
    assert collector.recurrent["errors"][-1]["stage"] == "recurrent_inputs" and not collector.errors
    monkeypatch.setattr(collector, "_recurrent_value", error)
    assert collector.drain(True)["recurrent_state"]["status"] == "unverified"
    assert "host" in bank


def test_recurrent_new_canonical_publication_is_field_level_and_compared_by_rid(monkeypatch):
    collector, _, conv, temporal = _recurrent_toy(monkeypatch)
    req, _ = _recurrent_capture(collector, conv, temporal, "opaque-writer", 5)
    collector._recurrent_publication(req, SimpleNamespace(mamba_value=torch.tensor([1])), collector.start)
    collector._recurrent_rebind(req, collector.start, SimpleNamespace(last_device_node=19,
        prefix_len=collector.start, mamba_exist=False, rotation_tail_declined=False))
    bank = collector.recurrent["by_rid"][req.rid]
    assert bank["publication"]["canonical_value_status"] == "captured"
    comparisons = collector._recurrent_publication_comparisons([bank])
    assert comparisons[0]["left_rid"] == comparisons[0]["right_rid"] == "opaque-writer"
    assert comparisons[0]["publication_node_id"] == 19
    assert comparisons[0]["source_key_join"].startswith("unverified")
    assert comparisons[0]["components"]["temporal"]["mismatch_count"] > 0


def test_generated_recurrent_observation_error_does_not_suppress_native_exception(
        composed, tmp_path, monkeypatch):
    _prepare_di(composed, tmp_path / "recurrent-native-error", monkeypatch)
    calls = []
    def observe(method, *args, **kwargs):
        calls.append(method)
        # The installed observation wrapper isolates its own failures.
        if method == "recurrent_inputs":
            coherence.observe(method, *args, **kwargs)
    collector, _, conv, temporal = _recurrent_toy(monkeypatch)
    monkeypatch.setattr(coherence, "_collector", collector)
    def observation_error(*args, **kwargs):
        raise ValueError("Injected copy failure; no native operator executed")
    monkeypatch.setattr(collector, "recurrent_inputs", observation_error)
    def native_error(**kwargs):
        raise RuntimeError("Injected native dispatcher failure remains visible")
    batch = SimpleNamespace(forward_mode=SimpleNamespace(is_extend=lambda: True, is_target_verify=lambda: False),
        rids=["opaque"], batch_size=1, extend_prefix_lens_cpu=[2], extend_seq_lens_cpu=[3],
        extend_prefix_lens=torch.tensor([2]))
    query = torch.tensor([0, 3], dtype=torch.int32)
    forward_metadata = SimpleNamespace(query_start_loc=query, mamba_cache_indices=torch.tensor([1]),
        retrieve_next_token=None, retrieve_next_sibling=None, retrieve_parent_token=None,
        has_mamba_track_mask=False, track_ssm_h_src=None, track_chunk_idx=None,
        state_checkpoint_cu_starts=None, num_state_checkpoints=None, state_checkpoint_every_n_tokens=None)
    namespace = {"torch": torch, "_is_hip": False, "_kv_observe": observe,
        "get_forward_context": lambda: SimpleNamespace(forward_batch=batch), "has_forward_context": lambda: True,
        "causal_conv1d_fn": object(), "is_cpu": lambda: False, "is_cuda": lambda: True,
        "is_hip": lambda: False, "is_xpu": lambda: False, "MAX_FUSED_QKV_SPLIT_DIM": 6,
        "_mamba_record": lambda *args: None, "_mamba_tensor": lambda value: None,
        "fused_qkv_split_gdn_prefill": lambda x, *args: tuple(torch.zeros(1, 3, 1, 2) for _ in range(3))}
    forward = _bind(composed, metadata._GDN, "forward_extend", namespace)
    backend = SimpleNamespace(forward_metadata=forward_metadata, mis_metadata=None, requires_contiguous_prefill_state=False,
        _use_strided_target_verify_qkv=False, req_to_token_pool=SimpleNamespace(
            mamba2_layer_cache=lambda layer: SimpleNamespace(conv=[conv], temporal=temporal)),
        _convolve_prefill=lambda *args: args[2],
        _prefill_gates=lambda *args: (torch.ones(1, 3, 1), torch.ones(1, 3, 1)),
        kernel_dispatcher=SimpleNamespace(extend=native_error, extend_kernel=SimpleNamespace(
            supports_track_state_snapshot=True)))
    layer = SimpleNamespace(layer_id=0, q_dim=2, k_dim=2, v_dim=2, num_q_heads=1, num_k_heads=1,
                            num_v_heads=1, head_q_dim=2, head_k_dim=2, head_v_dim=2)
    with pytest.raises(RuntimeError, match="native dispatcher failure remains visible"):
        forward(backend, layer, batch, torch.zeros(3, 6), torch.zeros(3, 1), torch.zeros(3, 1))
    assert calls == ["recurrent_begin", "recurrent_inputs"]
    assert not collector.errors and collector.recurrent["errors"][-1]["stage"] == "recurrent_inputs"


def test_recurrent_allocation_error_preserves_full_and_unconfigured_default(monkeypatch):
    collector, _ = _toy(monkeypatch)
    assert collector.drain(False)["recurrent_state"]["coverage"]["configured"] is False
    def fail(*args, **kwargs):
        raise RuntimeError("Injected pinned allocation failure")
    pool = SimpleNamespace(layer_transfer_counter=None, mamba_map={0: 0},
        mamba_pool=SimpleNamespace(mamba2_layer_cache=fail))
    collector.initialize_recurrent(pool, (5, 8), 2)
    assert not collector.errors and collector.recurrent["errors"][0]["stage"] == "allocation"
    collector.register(_req("full"))
    assert len(collector.by_rid) == 1 and len(collector.banks) == 2


def test_recurrent_requires_successful_existing_full_readback_and_never_substitutes_sync(monkeypatch):
    collector, full, conv, temporal = _recurrent_toy(monkeypatch)
    _recurrent_capture(collector, conv, temporal, "recurrent", 5)
    _capture_bank(collector, full, "full-one", 2)
    _capture_bank(collector, full, "full-two", 5)
    for rid in ("full-one", "full-two", "recurrent", *(f"ordinary-{i}" for i in range(13))):
        collector.finish(_req(rid))
    def failure(*args, **kwargs):
        raise RuntimeError("Injected failure of the existing FULL readback boundary")
    def forbidden(*args, **kwargs):
        raise AssertionError("Unfinished pinned captures must not be read or replayed")
    monkeypatch.setattr(collector, "_physical", failure)
    monkeypatch.setattr(collector, "_recurrent_value", forbidden)
    monkeypatch.setattr(collector, "_recurrent_conv_replay", forbidden)
    receipt = collector.drain(True)
    assert receipt["status"] == receipt["recurrent_state"]["status"] == "unverified"
    assert "FULL completion/readback" in receipt["recurrent_state"]["reason"]
    assert not receipt["recurrent_state"]["replays"]
    assert collector.drain(True) is receipt
    # Without a known completion boundary, retain destinations rather than free
    # potentially in-flight DMA memory or invent a synchronize/event fallback.
    assert "host" in collector.recurrent["by_rid"]["recurrent"]


def test_recurrent_metrics_common_rows_first_absolute_coordinate_and_nonfinite():
    a = torch.zeros(1, 3, 1, 2, dtype=torch.bfloat16)
    b = a.clone()
    b[0, 1, 0, 1] = 2
    b[0, 2, 0, 0] = float("inf")
    metric = coherence.recurrent_metrics(torch, a[:, :2], b[:, :2], token_axis=1, start=90112)
    assert metric["mismatch_count"] == 1 and metric["first_mismatch"] == {
        "coordinate": [0, 1, 0, 1], "absolute_token": 90113}
    assert metric["max_absolute_error"] == 2 and metric["rms_error"] == 1.0
    full = coherence.recurrent_metrics(torch, a, b, token_axis=1, start=90112)
    assert full["right_nonfinite_count"] == 1 and not full["values_exact"]
    json.dumps(full, allow_nan=False)
    state = torch.zeros(1, 2, 2, 2)
    other = state.clone()
    other[0, 1, 0, 1] = 3
    metric = coherence.recurrent_metrics(torch, state, other)
    assert metric["first_mismatch"] == {"coordinate": [0, 1, 0, 1], "absolute_token": None}
    assert metric["mismatch_count"] == 1 and metric["max_absolute_error"] == 3
