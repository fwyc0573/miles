"""CPU bindings of Source590; native streams, compilation and scores unverified.

MILES_PINNED_SGLANG_SOURCE supplies a complete pristine retained package. Missing
evidence skips explicitly; installed host SGLang is never a source substitute.
Only temporary clones are prepared, with the two earlier stages applied once.
"""

import ast
import copy
import dataclasses
import json
import os
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest

from tests.manual.agent_opd import sglang_kv_streams as witness
from tests.manual.agent_opd import sglang_mamba_runtime_metadata as metadata
from tests.manual.agent_opd import sglang_mamba_snapshots as snapshots


_EVIDENCE = (Path(__file__).resolve().parents[2]
             / "task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111"
             / witness._SOURCE_JOB / "source")


@pytest.fixture(scope="session")
def prepared_source(tmp_path_factory):
    retained = Path(os.environ["MILES_PINNED_SGLANG_SOURCE"]) if "MILES_PINNED_SGLANG_SOURCE" in os.environ else _EVIDENCE
    stage = tmp_path_factory.mktemp("kv-prior-stages")
    root = stage / "sglang"
    for relative, identity in witness.source_manifest()["files"].items():
        if relative == witness._RECORDER:
            continue
        path = retained / relative
        if not path.is_file():
            pytest.skip(f"Required retained Source590 evidence unavailable: {path}")
        content = path.read_bytes()
        expected = identity.get("native_sha256")
        if expected is None:
            expected = snapshots.source_manifest()["files"].get(relative, {}).get(
                "before_sha256", identity["metadata_base_sha256"]
            )
        assert metadata._sha256(content) == expected, path
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(witness.importlib.metadata, "version", lambda name: witness.source_manifest()["distribution_version"])
        snapshots.prepare_source(root, image=witness.source_manifest()["image"],
                                 selected_fp32=True, archive_dir=stage / "fp32")
        metadata.prepare_runtime_metadata(root, image=witness.source_manifest()["image"], archive_dir=stage / "metadata")
    return _contents(root)


@pytest.fixture
def native_root(prepared_source, tmp_path, monkeypatch):
    root = tmp_path / "sglang"
    for relative, content in prepared_source.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    versions = {"sglang": witness.source_manifest()["distribution_version"], "apache-tvm-ffi": "0.1.11"}
    monkeypatch.setattr(witness.importlib.metadata, "version", versions.__getitem__)
    monkeypatch.setattr(witness.importlib.metadata, "distribution",
                        lambda name: SimpleNamespace(locate_file=lambda relative: root / relative))
    return root


def _prepare(root, archive):
    return witness.prepare_source(root, image=witness.source_manifest()["image"], archive_dir=archive)


def _contents(root):
    return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*") if path.is_file()}


def _context(root, monkeypatch):
    module = ModuleType("qualified_kv_forward_context")
    monkeypatch.setitem(sys.modules, module.__name__, module)
    exec(compile((root / witness._CONTEXT).read_bytes(), witness._CONTEXT, "exec"), module.__dict__)
    return module


def _recorder(root):
    scope = {}
    exec(compile((root / witness._RECORDER).read_bytes(), witness._RECORDER, "exec"), scope)
    return scope


def _rows(recorder):
    parallel = SimpleNamespace(dp_rank=0, tp_rank=0, pp_rank=0, attn_dp_rank=0, attn_tp_rank=0)
    drained = recorder["drain"](parallel)
    assert drained["physical_slot_values"] == "UNMEASURED"
    json.dumps(drained, allow_nan=False)
    return [(event, dict(fields)) for _, event, fields in drained["rows"]]


def _method(root, relative, name, class_name=None):
    tree = ast.parse((root / relative).read_bytes())
    if class_name:
        tree = next(node for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name == class_name)
    return copy.deepcopy(next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name))


def _bind(root, relative, name, recorder, context, *, class_name=None, **namespace):
    node = _method(root, relative, name, class_name)
    node.decorator_list = []
    scope = {"_mamba_record": recorder["record"], "_mamba_tensor": recorder["tensor_metadata"],
             "get_forward_context": context.get_forward_context, "has_forward_context": context.has_forward_context,
             **namespace}
    module = ast.Module(body=ast.parse("from __future__ import annotations").body + [node], type_ignores=[])
    exec(compile(module, relative, "exec"), scope)
    return scope[name]


class _Batch:
    rids = ["rid-first", "rid-second"]
    extend_prefix_lens_cpu = [90112, 64]
    extend_seq_lens_cpu = [8192, 2]

    def moe_num_token_non_padded(self):
        return None


class _Tensor:
    """Only metadata and original native reshape/cast operations are available."""

    _next_ptr = 4096

    def __init__(self, shape=(2, 4), dtype="bfloat16", ptr=None):
        self.shape, self.dtype = tuple(shape), dtype
        self.device = SimpleNamespace(index=0)
        self.ndim = len(shape)
        self.ptr = ptr if ptr is not None else type(self)._next_ptr
        type(self)._next_ptr += 256

    def stride(self):
        result, product = [], 1
        for dim in reversed(self.shape):
            result.insert(0, product)
            product *= dim
        return tuple(result)

    def data_ptr(self):
        return self.ptr

    def numel(self):
        product = 1
        for dim in self.shape:
            product *= dim
        return product

    def element_size(self):
        return 2

    def view(self, *shape):
        if len(shape) == 1 and isinstance(shape[0], str):
            return _Tensor(self.shape, shape[0], self.ptr)
        shape = tuple(self.numel() // shape[-1] if dim == -1 else dim for dim in shape)
        return _Tensor(shape, self.dtype, self.ptr)

    def contiguous(self):
        return self

    def __getattr__(self, name):
        raise AssertionError(f"Forbidden tensor operation: {name}")

    def __getitem__(self, index):
        raise AssertionError("Device contents must not be indexed by witness")

    def __iter__(self):
        raise AssertionError("Device contents must not be iterated")

    def __bool__(self):
        raise AssertionError("Device values must not be tested")


def test_exact_stage_binding_archive_and_idempotence(native_root, tmp_path, monkeypatch):
    before = _contents(native_root)
    # The new stage must not call either earlier preparer, including on repeat.
    def forbidden(*args, **kwargs):
        raise AssertionError("Earlier source preparer rerun")
    monkeypatch.setattr(snapshots, "prepare_source", forbidden)
    monkeypatch.setattr(metadata, "prepare_runtime_metadata", forbidden)
    archive = tmp_path / "witness"
    receipt = _prepare(native_root, archive)
    after = _contents(native_root)
    assert set(receipt["changed_files"]) == set(witness._EDITS)
    assert receipt["native_compilation"] == "UNVERIFIED"
    assert receipt["readback_key"] == "mamba_runtime_metadata"
    assert receipt["stream_witness_scope"] == "CPP calls only; CUDA prefix-valid Triton remains UNVERIFIED"
    for relative, identity in receipt["files"].items():
        assert (archive / "before" / relative).read_bytes() == before[relative]
        assert (archive / "after" / relative).read_bytes() == after[relative]
        assert identity["before_sha256"] == metadata._sha256(before[relative])
        assert identity["after_sha256"] == metadata._sha256(after[relative])
        if relative not in witness._EDITS:
            assert after[relative] == before[relative]
    assert (archive / "kv_streams.diff").read_text().count("--- a/") == 5
    assert not _prepare(native_root, archive)["patch_applied"]
    assert not _prepare(native_root, tmp_path / "second-archive")["patch_applied"]
    assert _contents(native_root) == after
    assert len((archive / "preflight.jsonl").read_text().splitlines()) == 2


@pytest.mark.parametrize("relative", list(witness.source_manifest()["files"]))
def test_every_unknown_source_rejected_before_writes(native_root, tmp_path, relative):
    path = native_root / relative
    path.write_bytes(path.read_bytes() + b"\n// unsupported change\n")
    before = _contents(native_root)
    with pytest.raises(ValueError, match="KV stream|Runtime metadata"):
        _prepare(native_root, tmp_path / "witness")
    assert _contents(native_root) == before
    assert not (tmp_path / "witness").exists()


@pytest.mark.parametrize("precondition", ["image", "sglang", "ffi", "fp32", "metadata", "recorder", "missing", "archive"])
def test_wrong_precondition_rejected_before_writes(native_root, tmp_path, monkeypatch, precondition):
    image = witness.source_manifest()["image"]
    archive = tmp_path / "witness"
    if precondition == "image":
        image = "wrong-image"
    elif precondition in ("sglang", "ffi"):
        wrong = "sglang" if precondition == "sglang" else "apache-tvm-ffi"
        original = witness.importlib.metadata.version
        monkeypatch.setattr(witness.importlib.metadata, "version", lambda name: "wrong-version" if name == wrong else original(name))
    elif precondition == "fp32":
        path = native_root / snapshots._TRITON
        path.write_bytes(snapshots._rewrite(snapshots._TRITON, path.read_bytes(), reverse=True))
    elif precondition == "metadata":
        path = native_root / metadata._GDN
        path.write_bytes(metadata._rewrite(metadata._GDN, path.read_bytes(), reverse=True))
    elif precondition in ("missing", "recorder"):
        path = native_root / (witness._CONTEXT if precondition == "missing" else witness._RECORDER)
        path.rename(path.with_suffix(".absent"))
    else:
        archive.mkdir()
        (archive / "kv_streams.diff").write_text("other evidence\n")
    before = _contents(native_root)
    with pytest.raises(ValueError):
        witness.prepare_source(native_root, image=image, archive_dir=archive)
    assert _contents(native_root) == before
    assert not (archive / "source_manifest.json").exists()


def test_post_preparation_source_mutation_is_not_idempotence(native_root, tmp_path):
    _prepare(native_root, tmp_path / "witness")
    path = native_root / witness._CPP
    path.write_bytes(path.read_bytes() + b"\n// changed after preparation\n")
    before = _contents(native_root)
    with pytest.raises(ValueError, match="Unrecognized KV stream"):
        _prepare(native_root, tmp_path / "other")
    assert _contents(native_root) == before
    assert not (tmp_path / "other").exists()


def test_real_context_red_green_and_exact_restoration(native_root, tmp_path, monkeypatch):
    original = _context(native_root, monkeypatch)
    batch = _Batch()
    with original.forward_context(original.ForwardContext(attn_backend=object()), forward_batch=batch):
        with pytest.raises(AttributeError, match="forward_batch"):
            original.get_forward_context().forward_batch
    assert original._current is None
    _prepare(native_root, tmp_path / "witness")
    context = _context(native_root, monkeypatch)
    ctx = context.ForwardContext(attn_backend=object())
    assert ctx.forward_batch is None
    with context.forward_context(ctx, forward_batch=batch):
        active = context.get_forward_context()
        assert active.forward_batch is batch
        assert active.forward_batch.rids == _Batch.rids
        assert active.forward_batch.extend_prefix_lens_cpu == [90112, 64]
        assert active.forward_batch.extend_seq_lens_cpu == [8192, 2]
        assert active.moe_num_token_non_padded.__self__ is batch
        with pytest.raises(dataclasses.FrozenInstanceError):
            active.forward_batch = None
        with pytest.raises(RuntimeError, match="scope exit"):
            with context.forward_context(ctx, forward_batch=_Batch()):
                raise RuntimeError("scope exit")
        assert context.get_forward_context() is active
    assert context._current is None and ctx.forward_batch is None
    old_tail = ast.parse((tmp_path / "witness/before" / witness._CONTEXT).read_bytes()).body[-1].body[-2:]
    new_tail = ast.parse((native_root / witness._CONTEXT).read_bytes()).body[-1].body[-2:]
    assert ast.dump(ast.Module(body=old_tail, type_ignores=[])) == ast.dump(ast.Module(body=new_tail, type_ignores=[]))


@pytest.mark.parametrize("actual,torch_stream", [(0, 0), (96, 96), (128, 96), (-1, 96)])
@pytest.mark.parametrize("has_batch", [True, False])
def test_cpp_wrapper_keeps_none_and_observes_return_without_context_force(native_root, tmp_path, monkeypatch, actual, torch_stream, has_batch):
    _prepare(native_root, tmp_path / "witness")
    context, recorder = _context(native_root, monkeypatch), _recorder(native_root)
    calls, raw_calls = [], []
    def cpp(*args):
        calls.append(args)
        return actual
    def raw(index):
        raw_calls.append(index)
        return torch_stream
    store = _bind(native_root, witness._STORE, "store_cache", recorder, context,
                  torch=SimpleNamespace(_C=SimpleNamespace(_cuda_getCurrentRawStream=raw)),
                  _WARP_THREADS=32, _jit_kvcache_module=lambda *args: SimpleNamespace(store_cache=cpp))
    tensors = [_Tensor(), _Tensor(), _Tensor((4, 4)), _Tensor((4, 4)), _Tensor((2,))]
    def call():
        assert store(*tensors, row_bytes=8, v_row_bytes=8, num_split=2, size_limit=4, reserved_skip_index=-1) is None
    if has_batch:
        with context.forward_context(context.ForwardContext(attn_backend=object()), forward_batch=_Batch()):
            call()
    else:
        call()
    assert raw_calls == [0] and calls == [tuple(tensors) + (4, -1)]
    rows = _rows(recorder)
    assert len(rows) == 1 and rows[0][0] == "kv_store_stream"
    row = rows[0][1]
    assert row["store_kind"] == "cpp_store_cache"
    assert row["native_actual_stream"] == (actual if actual != -1 else None)
    assert row["native_stream_scalar_observed"] is (actual != -1)
    assert row["launch_enqueued"] is (actual != -1)
    assert row["torch_current_raw_stream"] == torch_stream
    assert row["rids"] == (tuple(_Batch.rids) if has_batch else None)
    assert row["k_cache_data_ptr"] == tensors[2].data_ptr()
    assert context._current is None


def test_real_torch_custom_op_schema_and_cpu_dispatch_still_return_none(native_root, tmp_path, monkeypatch):
    import torch
    _prepare(native_root, tmp_path / "witness")
    context, recorder = _context(native_root, monkeypatch), _recorder(native_root)
    monkeypatch.setattr(torch._C, "_cuda_getCurrentRawStream", lambda index: 96, raising=False)
    store = _bind(native_root, witness._STORE, "store_cache", recorder, context, torch=torch, _WARP_THREADS=32,
                  _jit_kvcache_module=lambda *args: SimpleNamespace(store_cache=lambda *args: 128))
    schema = torch.library.infer_schema(store, mutates_args={"k_cache", "v_cache"})
    assert schema.endswith(" -> ()")
    op = torch.library.custom_op("kv_stream_cpu_binding::store_cache", store,
                                 mutates_args={"k_cache", "v_cache"}, device_types="cpu")
    tensors = [torch.empty((2, 4)) for _ in range(4)] + [torch.empty((2,), dtype=torch.int64)]
    assert op(*tensors) is None
    row = _rows(recorder)[0][1]
    assert row["native_actual_stream"] == 128 and row["torch_current_raw_stream"] == 96


@pytest.mark.parametrize("kind", ["plain", "prefix", "prefix_fp8"])
def test_class_owned_terminals_preserve_layer_batch_and_unverified_triton(native_root, tmp_path, monkeypatch, kind):
    _prepare(native_root, tmp_path / "witness")
    context, recorder = _context(native_root, monkeypatch), _recorder(native_root)
    calls = []
    dtype = "fp8" if kind == "prefix_fp8" else "bfloat16"
    pool = SimpleNamespace(start_layer=1, dtype=dtype, store_dtype=dtype,
                           k_buffer=[_Tensor((4, 4)), _Tensor((4, 4))],
                           v_buffer=[_Tensor((4, 4)), _Tensor((4, 4))],
                           row_dim=4, v_row_dim=4, size=4, page_size=1, use_hnd=False,
                           is_quantized_kv_cache=False, _check_physical_write_loc=lambda *args: None,
                           _store_kv_layer=lambda *args: calls.append(("plain", args)))
    layer = SimpleNamespace(layer_id=9)
    inputs = [_Tensor((2, 4)), _Tensor((2, 4))]
    with context.forward_context(context.ForwardContext(attn_backend=object()), forward_batch=_Batch()):
        if kind == "plain":
            store = _bind(native_root, witness._POOL, "set_kv_buffer", recorder, context,
                          class_name="MHATokenToKVPool", unwrap_write_loc=lambda loc: (loc, None, None),
                          maybe_detect_oob=lambda *args: None)
            loc = _Tensor((2,))
            assert store(pool, layer, loc, *inputs, layer_id_override=2) is None
            assert calls == [("plain", (1, loc, *inputs))]
        else:
            store = _bind(native_root, witness._POOL, "set_kv_buffer_prefix_valid", recorder, context,
                          class_name="MHATokenToKVPool", _is_cuda=True, _is_hip=False, fp8_dtype="fp8",
                          torch=SimpleNamespace(Tensor=_Tensor, int64="bfloat16", int32="bfloat16"),
                          _resolve_fused_scale=lambda *args: 1.0,
                          _set_kv_buffer_prefix_valid_impl=lambda *args, **kwargs: calls.append(("prefix", args, kwargs)),
                          _set_kv_buffer_prefix_valid_impl_fp8=lambda *args, **kwargs: calls.append(("prefix_fp8", args, kwargs)))
            loc, commit = _Tensor((1, 2)), _Tensor((1,))
            assert store(pool, layer, loc, commit, *inputs, layer_id_override=2) is None
            assert len(calls) == 1 and calls[0][0] == kind
            assert calls[0][1][-2:] == (loc, commit)
    rows = _rows(recorder)
    assert len(rows) == 1 and rows[0][0] == "kv_store_terminal"
    row = rows[0][1]
    expected = {"plain": "mha_set_kv_buffer_impl", "prefix": "mha_prefix_valid_triton", "prefix_fp8": "mha_prefix_valid_triton_fp8"}
    assert row["store_kind"] == expected[kind]
    assert row["layer_id"] == 9 and row["pool_layer_id"] == 2 and row["buffer_layer_idx"] == 1
    assert row["rids"] == tuple(_Batch.rids) and row["extend_lens"] == (8192, 2)
    assert row["native_actual_stream"] is None and row["native_stream_scalar_observed"] is False
    assert "torch_current_raw_stream" not in row
    assert row["k_cache_data_ptr"] == pool.k_buffer[1].data_ptr()
    if kind != "plain":
        assert row["commit_lens_data_ptr"] == commit.data_ptr()


@pytest.mark.parametrize("class_name", ["TokenToKVPoolAllocator", "DifferentAllocator"])
def test_actual_runner_assignment_records_selected_class_not_model_inference(native_root, tmp_path, monkeypatch, class_name):
    before = _method(native_root, witness._RUNNER, "alloc_memory_pool")
    assert not any(isinstance(node, ast.Constant) and node.value == "kv_allocator_created" for node in ast.walk(before))
    _prepare(native_root, tmp_path / "witness")
    context, recorder = _context(native_root, monkeypatch), _recorder(native_root)
    allocator = type(class_name, (), {"page_size": 1, "size": 4, "dtype": "bfloat16", "device": "cuda:0"})()
    pool = object()
    result = SimpleNamespace(max_total_num_tokens=4, max_running_requests=2, req_to_token_pool=object(),
                             token_to_kv_pool=pool, token_to_kv_pool_allocator=allocator,
                             memory_pool_config=object(), unified_memory_pool=None)
    calls = []
    runner = SimpleNamespace(is_hybrid_swa=False, pre_model_load_memory=1,
                             init_kv_cache_configurator=lambda *args: calls.append("init"),
                             kv_cache_configurator=SimpleNamespace(configure=lambda **kwargs: result),
                             _init_post_memory_pool_components=lambda: calls.append("post"))
    allocate = _bind(native_root, witness._RUNNER, "alloc_memory_pool", recorder, context)
    assert allocate(runner) is None and calls == ["init", "post"]
    assert runner.token_to_kv_pool_allocator is allocator and runner.token_to_kv_pool is pool
    rows = _rows(recorder)
    assert len(rows) == 1 and rows[0][0] == "kv_allocator_created"
    row = rows[0][1]
    assert row["allocator_class"] == (type(allocator).__module__, class_name)
    assert row["allocator_object_id"] == id(allocator) and row["pool_object_id"] == id(pool)


def test_cpp_source_kernel_params_pdl_export_and_context_restoration_unchanged(native_root, tmp_path):
    before = _contents(native_root)
    cpp = before[witness._CPP].decode()
    assert "static void\n  run(" in cpp and "if (batch_size == 0) return;" in cpp
    assert "return static_cast<int64_t>" not in cpp
    _prepare(native_root, tmp_path / "witness")
    after = _contents(native_root)
    for relative in witness._EDITS:
        assert witness._rewrite(relative, after[relative], reverse=True) == before[relative]
    rewritten = after[witness._CPP].decode()
    assert rewritten.count("LaunchKernel::resolve_device(device)") == 1
    assert "LaunchKernel(num_blocks, {device::kWarpThreads, num_warps}, stream)" in rewritten
    assert "if (batch_size == 0) return -1;" in rewritten
    assert ".enable_pdl(kUsePDL)(kernel, params);" in rewritten
    assert cpp.split("  static void\n  run(")[0] == rewritten.split("  static int64_t\n  run(")[0]
    assert after["kernels/jit/include/sgl_kernel/utils.cuh"] == before["kernels/jit/include/sgl_kernel/utils.cuh"]
    assert after["kernels/jit/utils/compile/spec.py"] == before["kernels/jit/utils/compile/spec.py"]
    assert b"TVM_FFI_DLL_EXPORT_TYPED_FUNC({export_name}, ({kernel_name}))" in after["kernels/jit/utils/compile/spec.py"]


def test_removing_cpu_receipts_restores_original_python_algorithm_ast(native_root, tmp_path):
    before = _contents(native_root)
    _prepare(native_root, tmp_path / "witness")
    class RemoveReceipts(ast.NodeTransformer):
        def visit_ImportFrom(self, node):
            if node.module in ("sglang.srt.mamba_runtime_metadata", "sglang.srt.model_executor.forward_context"):
                return None
            return node
        def visit_Assign(self, node):
            if any(isinstance(target, ast.Name) and target.id.startswith("_kv_") for target in node.targets):
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "store_cache":
                    return ast.Expr(value=node.value)
                return None
            return self.generic_visit(node)
        def visit_Expr(self, node):
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "_mamba_record":
                return None
            return self.generic_visit(node)
    for relative in (witness._POOL, witness._STORE, witness._RUNNER):
        original = RemoveReceipts().visit(ast.parse(before[relative]))
        rewritten = RemoveReceipts().visit(ast.parse((native_root / relative).read_bytes()))
        assert ast.dump(original) == ast.dump(rewritten), relative
