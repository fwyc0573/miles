"""CPU tensor/source/RPC contracts, never production-native or CUDA acceptance."""

import ast
import copy
import json
import os
import sys
import subprocess
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


def _prepare_di(root, archive, monkeypatch):
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
                                       build_receipt=archive.parent / "not-a-real-build.json")
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


def _capture_bank(collector, pool, rid, q, *, fresh_delta=0):
    req = _req(rid)
    collector.register(req)
    loc = torch.tensor([0, 1, 2, 3], dtype=torch.int64)
    batch = SimpleNamespace(rids=[rid], extend_prefix_lens_cpu=[2], extend_seq_lens_cpu=[4])
    for dense, (k, v) in enumerate(zip(pool.k_buffer, pool.v_buffer)):
        collector.note_cpp(batch, k, v, loc, 17, 17)
        collector.fresh(pool, dense, loc, batch, "cpp")
    params = SimpleNamespace(prev_prefix_len=2, value=torch.tensor([6, 7, 0, 1, 2, 3], dtype=torch.int64))
    collector.insert(req, params, 6, type("RustUnifiedTreeCore", (), {})())
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
        batch = SimpleNamespace(rids=["rid"], extend_prefix_lens_cpu=[2], extend_seq_lens_cpu=[4])
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
        "kv_coherence_build_receipt": "PENDING", "worker_local_root": str(tmp_path / "worker-local")}))
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
