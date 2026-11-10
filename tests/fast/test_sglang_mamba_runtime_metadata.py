"""CPU bindings of retained native source, with forbidden device reads trapped.

Source-dependent cases skip if retained evidence is unavailable, never replacing
it with host SGLang. Stand-ins check call/branch preservation, not CUDA math.
MILES_PINNED_SGLANG_SOURCE can supply one combined pristine native package.
"""

import ast
import copy
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.manual.agent_opd import sglang_mamba_runtime_metadata as metadata
from tests.manual.agent_opd import sglang_mamba_snapshots as snapshots


_EVIDENCE = (
    Path(__file__).resolve().parents[2]
    / "task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111"
)


@pytest.fixture
def native_root(tmp_path, monkeypatch):
    root = tmp_path / "sglang"
    source = os.environ.get("MILES_PINNED_SGLANG_SOURCE")
    for relative, identity in metadata.source_manifest()["files"].items():
        retained = Path(source) if source else _EVIDENCE / identity["native_source_job"] / "source"
        path = retained / relative
        if not path.is_file():
            pytest.skip(f"Required retained native source unavailable: {path}")
        content = path.read_bytes()
        expected = snapshots.source_manifest()["files"].get(relative, {}).get(
            "before_sha256", identity["before_sha256"]
        )
        assert metadata._sha256(content) == expected, path
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    monkeypatch.setattr(metadata.importlib.metadata, "version", lambda name: snapshots.source_manifest()["distribution_version"])
    snapshots.prepare_source(root, image=snapshots.source_manifest()["image"], selected_fp32=True,
                             archive_dir=tmp_path / "selected-fp32")
    return root


def _prepare(root, archive):
    return metadata.prepare_runtime_metadata(root, image=metadata.source_manifest()["image"], archive_dir=archive)


def _contents(root):
    return {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*.py")}


def _recorder(root=None):
    namespace = {}
    source = (root / metadata._RECORDER).read_bytes() if root is not None else metadata._RECORDER_SOURCE
    exec(compile(source, "qualified-runtime-metadata.py", "exec"), namespace)
    return namespace


def _drain(recorder):
    return recorder["drain"](SimpleNamespace(dp_rank=1, tp_rank=2, pp_rank=0, attn_dp_rank=1, attn_tp_rank=0))


def _events(recorder):
    return [(event, dict(fields)) for _, event, fields in _drain(recorder)["rows"]]


class _Tensor:
    """Metadata-only tensor; only native call sites may index/cast/mutate it."""

    def __init__(self, shape=(2,), dtype="int64", device="cuda:2"):
        self.shape, self.dtype, self.device = tuple(shape), dtype, device
        self.writes = []
        self.casts = []

    def __len__(self):
        return self.shape[0]

    def stride(self):
        strides, product = [], 1
        for dim in reversed(self.shape):
            strides.insert(0, product)
            product *= dim
        return tuple(strides)

    def numel(self):
        product = 1
        for dim in self.shape:
            product *= dim
        return product

    def __getitem__(self, index):
        if isinstance(index, _Tensor):
            shape = (index.shape[0], *self.shape[1:])
        elif isinstance(index, slice):
            shape = (len(range(*index.indices(self.shape[0]))), *self.shape[1:])
        elif isinstance(index, tuple):
            return self[index[-1]]
        else:
            shape = self.shape[1:]
        return _Tensor(shape, self.dtype, self.device)

    def __setitem__(self, index, value):
        self.writes.append((index, value))

    def to(self, dtype, copy=False):
        self.casts.append((dtype, copy))
        return _Tensor(self.shape, dtype, self.device)

    def squeeze(self, axis):
        return _Tensor(self.shape[:axis] + self.shape[axis + 1:], self.dtype, self.device)

    def unsqueeze(self, axis):
        return _Tensor(self.shape + (1,), self.dtype, self.device)

    def clone(self):
        return _Tensor(self.shape, self.dtype, self.device)

    def index_select(self, axis, indices):
        assert axis == 0
        return _Tensor((len(indices), *self.shape[1:]), self.dtype, self.device)

    def __iter__(self):
        raise AssertionError("Device tensor values must not be iterated")

    def item(self):
        raise AssertionError("Device scalar read is forbidden")

    def cpu(self):
        raise AssertionError("Device transfer is forbidden")

    def tolist(self):
        raise AssertionError("Device content conversion is forbidden")

    def __bool__(self):
        raise AssertionError("Device value-dependent bool is forbidden")


def _method(root, relative, name):
    tree = ast.parse((root / relative).read_bytes())
    return copy.deepcopy(next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name))


def _bind(root, relative, name, recorder, **namespace):
    node = _method(root, relative, name)
    node.decorator_list = []
    scope = {"_mamba_record": recorder["record"], "_mamba_tensor": recorder["tensor_metadata"], **namespace}
    future = ast.parse("from __future__ import annotations").body
    exec(compile(ast.Module(body=future + [node], type_ignores=[]), str(root / relative), "exec"), scope)
    return scope[name]


def _slice(root, relative, name, start, stop, recorder, **scope):
    """Execute exact retained statements, supplying unrelated upstream locals."""
    node = _method(root, relative, name)
    statements = node.body
    if name == "forward_extend":
        statements = next(node.orelse for node in statements if isinstance(node, ast.If)
                          and any(start(statement) for statement in node.orelse))
    a = next(i for i, statement in enumerate(statements) if start(statement))
    b = next(i for i, statement in enumerate(statements[a:], a) if stop(statement))
    node.name, node.args, node.decorator_list = "bound_slice", ast.arguments(
        posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[]
    ), []
    node.body, node.returns = statements[a:b + 1], None
    namespace = {"_mamba_record": recorder["record"], "_mamba_tensor": recorder["tensor_metadata"], **scope}
    future = ast.parse("from __future__ import annotations").body
    exec(compile(ast.fix_missing_locations(ast.Module(body=future + [node], type_ignores=[])), "native-chosen-locals.py", "exec"), namespace)
    return namespace["bound_slice"]


def test_exact_source_archive_and_idempotence(native_root, tmp_path):
    before = _contents(native_root)
    archive = tmp_path / "runtime"
    receipt = _prepare(native_root, archive)
    after = _contents(native_root)
    assert set(receipt["changed_files"]) == set(metadata._EDITS) | {metadata._RECORDER}
    assert receipt["diagnostic_only"] and receipt["cuda_semantics"] == "UNVERIFIED"
    assert receipt["physical_slot_values"] == "UNMEASURED"
    assert receipt["readback_key"] == "mamba_runtime_metadata"
    for relative in after:
        assert (archive / "before" / relative).read_bytes() == before.get(relative, b"")
        assert (archive / "after" / relative).read_bytes() == after[relative]
        assert receipt["files"][relative]["after_sha256"] == metadata._sha256(after[relative])
    for relative in snapshots.source_manifest()["files"]:
        if relative not in metadata._EDITS:
            assert after[relative] == before[relative], "diagnostics must not change the selected-FP32 math patch"
    assert (archive / "runtime_metadata.diff").read_text().count("--- a/") == 9
    assert not _prepare(native_root, archive)["patch_applied"]
    assert _contents(native_root) == after
    assert len((archive / "preflight.jsonl").read_text().splitlines()) == 2
    assert not _prepare(native_root, tmp_path / "fresh-archive")["patch_applied"]


@pytest.mark.parametrize("relative", list(metadata.source_manifest()["files"]) + [metadata._RECORDER])
def test_changed_sources_rejected_before_any_writes(native_root, tmp_path, relative):
    path = native_root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((path.read_bytes() if path.exists() else b"") + b"\n# unsupported source\n")
    before = _contents(native_root)
    with pytest.raises(ValueError, match="Unrecognized runtime metadata"):
        _prepare(native_root, tmp_path / "runtime")
    assert _contents(native_root) == before
    assert not (tmp_path / "runtime").exists()


def test_missing_required_source_names_path_and_hash(native_root, tmp_path):
    # A renamed test-local source makes the required path absent, not substituted.
    relative = "srt/runtime_context.py"
    path = native_root / relative
    path.rename(path.with_suffix(".absent"))
    before = _contents(native_root)
    with pytest.raises(ValueError, match=f"runtime_context.py; sha256={metadata._ADDITIONAL[relative][1]}"):
        _prepare(native_root, tmp_path / "runtime")
    assert _contents(native_root) == before
    assert not (tmp_path / "runtime").exists()


@pytest.mark.parametrize("identity", ["image", "version", "unprepared", "archive"])
def test_preflight_rejects_wrong_preconditions(native_root, tmp_path, monkeypatch, identity):
    image = metadata.source_manifest()["image"]
    archive = tmp_path / "runtime"
    if identity == "image":
        image = "unqualified"
    elif identity == "version":
        monkeypatch.setattr(metadata.importlib.metadata, "version", lambda name: "0.5.23")
    elif identity == "unprepared":
        path = native_root / snapshots._TRITON
        path.write_bytes(snapshots._rewrite(snapshots._TRITON, path.read_bytes(), reverse=True))
    else:
        archive.mkdir()
        (archive / "runtime_metadata.diff").write_text("other evidence\n")
    before = _contents(native_root)
    with pytest.raises(ValueError, match="qualified pinned image|identity differs|Unrecognized|archive differs"):
        metadata.prepare_runtime_metadata(native_root, image=image, archive_dir=archive)
    assert _contents(native_root) == before
    assert not (archive / "source_manifest.json").exists()


def test_diagnostic_ast_removal_restores_entire_native_ast(native_root, tmp_path):
    before = _contents(native_root)
    _prepare(native_root, tmp_path / "runtime")

    class RemoveDiagnostics(ast.NodeTransformer):
        def visit_ImportFrom(self, node):
            return None if node.module == "sglang.srt.mamba_runtime_metadata" else node

        def visit_Expr(self, node):
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "_mamba_record":
                return None
            return self.generic_visit(node)

        def visit_Assign(self, node):
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "_mamba_drain":
                return None
            return self.generic_visit(node)

    for relative in metadata._EDITS:
        original = ast.parse(before[relative])
        candidate = RemoveDiagnostics().visit(ast.parse((native_root / relative).read_bytes()))
        assert ast.dump(candidate) == ast.dump(original), relative
    recorder = ast.parse(metadata._RECORDER_SOURCE)
    calls = [node for node in ast.walk(recorder) if isinstance(node, ast.Call)]
    assert {node.func.attr for node in calls if isinstance(node.func, ast.Attribute)} == {"stride", "append", "clear", "getpid"}
    assert {node.module for node in ast.walk(recorder) if isinstance(node, ast.ImportFrom)} == set()


def test_recorder_is_cpu_only_and_drain_is_process_local():
    recorder = _recorder()
    tensor = _Tensor((2, 3, 4), "float32")
    observed = recorder["tensor_metadata"](tensor)
    assert observed == (id(tensor), "float32", (2, 3, 4), (12, 4, 1), "cuda:2")
    recorder["record"]("chosen", (("tensor", observed),))
    response = _drain(recorder)
    assert response["rank"]["tp_rank"] == 2
    assert response["coverage"] == "responding scheduler process only; no all-TP gather"
    assert response["physical_slot_values"] == "UNMEASURED"
    assert response["rows"] == ((1, "chosen", (("tensor", observed),)),)
    assert _drain(recorder)["rows"] == ()
    recorder["record"]("later", ())
    assert _drain(recorder)["rows"][0][0] == 2
    json.dumps(response, allow_nan=False)
    assert not tensor.writes and not tensor.casts


@pytest.mark.parametrize("mask,h_rows,capability", [(False, 0, True), (True, 0, True), (True, 1, False), (True, 1, True)])
@pytest.mark.parametrize("cpu_lens", [True, False])
def test_live_allocation_dispatch_and_selected_store_bindings(native_root, tmp_path, mask, h_rows, capability, cpu_lens):
    _prepare(native_root, tmp_path / "runtime")
    recorder, launches, allocations = _recorder(native_root), [], []

    class Kernel:
        supports_track_state_snapshot = capability

        def extend(self, *args, **kwargs):
            launches.append((args, kwargs))
            return object(), None, _Tensor((1, 3, 2, 4, 4), "bfloat16")

    kernel = Kernel()
    dispatch = _bind(native_root, metadata._GDN, "extend", recorder)
    dispatcher = SimpleNamespace(extend_kernel=kernel)
    dispatcher.extend = lambda **kwargs: dispatch(dispatcher, **kwargs)
    batch = SimpleNamespace(rids=["request-A"], extend_prefix_lens_cpu=[64], extend_seq_lens_cpu=[65], extend_prefix_lens=_Tensor())
    if not cpu_lens:
        batch.extend_prefix_lens_cpu = batch.extend_seq_lens_cpu = None
    forward = SimpleNamespace(
        has_mamba_track_mask=mask, track_ssm_h_src=_Tensor((h_rows,)), track_chunk_idx=_Tensor((1,), "int32"),
        state_checkpoint_cu_starts=None, num_state_checkpoints=0, state_checkpoint_every_n_tokens=None,
        track_ssm_h_dst=_Tensor((h_rows,)), track_ssm_h_batch_src=_Tensor((h_rows,)),
        track_ssm_recompute_dst=None, track_ssm_final_src=_Tensor((0,)),
    )
    temporal = _Tensor((4, 2, 4, 4), "bfloat16")

    def empty(shape, dtype, device):
        result = _Tensor(shape, dtype, device)
        allocations.append(result)
        return result

    scope = dict(
        self=SimpleNamespace(kernel_dispatcher=dispatcher), forward_batch=batch, forward_metadata=forward,
        layer=SimpleNamespace(layer_id=7), torch=SimpleNamespace(empty=empty, float32="float32"),
        cache_indices=_Tensor((1,)), ssm_states=temporal, ssm_states_contig=temporal,
        state_cache_indices=_Tensor((1,)), query_start_loc=_Tensor((2,)), needs_state_gather=False,
        query=_Tensor(), key=_Tensor(), value=_Tensor(), g=_Tensor(), beta=_Tensor(), kwargs={},
    )
    run = _slice(native_root, metadata._GDN, "forward_extend",
                 lambda node: isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "h_track_buf" for target in node.targets),
                 lambda node: isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "extend",
                 recorder, **scope)
    run()
    rows = _events(recorder)
    allocated = bool(mask and h_rows and capability)
    assert bool(allocations) == allocated
    assert [event for event, _ in rows] == ["gdn_snapshot_allocation", "gdn_extend_dispatch"]
    assert rows[0][1]["allocated"] is allocated and rows[0][1]["rids"] == ("request-A",)
    assert rows[0][1]["prefix_lens"] == ((64,) if cpu_lens else None)
    if allocated:
        assert rows[0][1]["track_state"][1] == "float32"
        assert rows[0][1]["track_state"][0] == rows[1][1]["track_state"][0]
    args, kwargs = launches[0]
    assert len(args) == 5 and kwargs["ssm_states"] is temporal
    assert kwargs["track_state"] is (allocations[0] if allocated else None)
    assert kwargs["track_chunk_idx"] is (forward.track_chunk_idx if allocated else None)
    assert kwargs["layer_id"] == 7
    assert kwargs["state_checkpoint_cu_starts"] is None
    assert not temporal.writes and not temporal.casts
    if mask and h_rows:
        store = _bind(native_root, metadata._HYBRID, "_track_mamba_state_extend", recorder)
        store(None, batch, _Tensor((1, 3, 2, 4, 4), "bfloat16"), temporal, forward,
              h_track_buf=allocations[0] if allocated else None)
        events = _events(recorder)
        assert events[0][0] == "snapshot_store_enqueued"
        assert events[0][1]["source"] == ("h_track_buf" if allocated else "per_chunk_h")
        assert events[0][1]["temporal"][1] == "bfloat16"
        assert len(temporal.writes) == 1 and temporal.writes[0][1].dtype == "bfloat16"


@pytest.mark.parametrize("mamba2", [False, True])
def test_actual_cpu_plan_mapping_does_not_read_slots(native_root, tmp_path, mamba2):
    _prepare(native_root, tmp_path / "runtime")
    recorder = _recorder(native_root)
    plan_module = {}
    exec(compile((native_root / "srt/layers/attention/mamba/prefill_track_metadata.py").read_bytes(), "native-prefill-plan.py", "exec"), plan_module)
    mamba2_type = type("Mamba2AttnBackend", (), {})
    backend = mamba2_type() if mamba2 else SimpleNamespace()
    backend.mamba_chunk_size = 64
    transfers = []

    def to_device(values, dtype="int64"):
        transfers.append((tuple(values), dtype))
        return _Tensor((len(values),), dtype)

    backend._track_indices_to_device = to_device
    batch = SimpleNamespace(
        rids=["a", "b", "c"], mamba_prefill_track_mask_cpu=[True, True, False],
        mamba_track_seqlens_cpu=[129, 64, -1], extend_seq_lens_cpu=[130, 64, 2],
        extend_prefix_lens_cpu=[0, 0, 0], mamba_track_indices=_Tensor((3,)),
    )
    mapping = _bind(native_root, metadata._HYBRID, "_init_track_ssm_indices_from_cpu", recorder,
                    Mamba2AttnBackend=mamba2_type, build_prefill_track_plan=plan_module["build_prefill_track_plan"],
                    torch=SimpleNamespace(int32="int32"))
    result = mapping(backend, _Tensor((3,)), batch)
    rows = _events(recorder)
    assert len(rows) == 1 and rows[0][0] == "prefill_track_plan"
    observed = rows[0][1]
    assert observed["tracked_rows"] == (0, 1) and observed["final_rows"] == (1,)
    assert observed["h_src"] == (2,) and observed["chunk_indices"] == (2, -1, -1)
    assert observed["mask"] == (True, True, False) and observed["mamba2"] is mamba2
    assert len(result) == 9 and result[0].dtype == "int32"
    assert observed["track_indices"][0] == id(batch.mamba_track_indices)
    assert transfers.count(((2, -1, -1), "int32")) == 1


@pytest.mark.parametrize("extend_len,branch", [(65, None), (130, None), (130, 64)])
def test_actual_boundary_and_pingpong_choices(native_root, tmp_path, extend_len, branch):
    _prepare(native_root, tmp_path / "runtime")
    recorder = _recorder(native_root)
    kv = SimpleNamespace(mamba_next_track_idx=0, mamba_last_track_idx=1, mamba_last_track_seqlen=None)
    req = SimpleNamespace(rid="boundary", prefix_len=0, extend_len=extend_len, extend_end=extend_len, kv=kv,
                          mamba_branching_seqlen=branch)
    swaps = []

    def other(index):
        swaps.append(index)
        return 1 - index

    backend = SimpleNamespace(model_config=SimpleNamespace(hf_text_config=SimpleNamespace(mamba_chunk_size=64)),
                              tree_cache=SimpleNamespace(page_size=1), req_to_token_pool=SimpleNamespace(get_mamba_ping_pong_other_idx=other))
    boundary = _bind(native_root, metadata._SCHEDULE, "_mamba_radix_cache_v2_req_prepare_for_extend", recorder,
                     mamba_cache_chunk_size=lambda: 64, mamba_checkpoint_grid=lambda page_size: 128,
                     get_parallel=lambda: SimpleNamespace(dcp_enabled=False),
                     get_exec=lambda: SimpleNamespace(mamba=SimpleNamespace(enable_mamba_extra_buffer_lazy=False)),
                     _MambaRadixCacheV2TrackEntry=lambda **kwargs: kwargs)
    result = boundary(backend, req)
    row = _events(recorder)[0][1]
    assert result["track_mask"] is (extend_len >= 128)
    assert row["mask"] == result["track_mask"] and row["track_seqlen"] == result["track_seqlen"]
    assert row["track_position"] == result["track_position"] == 0
    assert len(swaps) == int(result["track_mask"]), "recorder must not recompute the ping-pong resolver"
    assert row["last_track_idx"] == kv.mamba_last_track_idx and row["next_track_idx"] == kv.mamba_next_track_idx
    if branch is not None:
        assert row["aligned_seqlen"] == branch and row["track_seqlen"] == branch + 1


def test_actual_cow_match_and_existing_node_retention(native_root, tmp_path):
    _prepare(native_root, tmp_path / "runtime")
    recorder = _recorder(native_root)
    source, candidate = _Tensor((1,)), _Tensor((1,))
    req = SimpleNamespace(rid="cow", kv=SimpleNamespace(holds_mamba=True, mamba_pool_idx=_Tensor(())))
    result = SimpleNamespace(best_match_node=42, mamba_exist=False)
    backend = SimpleNamespace(component_type=0, tree_core=SimpleNamespace(get_component_device_value=lambda node, component: source))
    match = _bind(native_root, metadata._MAMBA, "finalize_match_result_in_cache", recorder)
    assert match(backend, SimpleNamespace(cow_mamba=True, req=req), result) is result
    assert req.kv.mamba_cow_src_index is source and req.kv.mamba_needs_clear is False
    assert _events(recorder)[0][1]["node_id"] == 42
    existing = _Tensor((1,))
    node = SimpleNamespace(id=43, component_data=[SimpleNamespace(value=existing)])
    backend.tree_core = SimpleNamespace(lru_lists=[SimpleNamespace(reset_node_mru=lambda node: None)])
    commit = _bind(native_root, metadata._MAMBA, "commit_insert_component_data", recorder, get_and_increase_time_counter=lambda: 8)
    commit(backend, node, False, SimpleNamespace(mamba_value=candidate), result, [])
    assert node.component_data[0].value is existing and result.mamba_exist is True
    row = _events(recorder)[0][1]
    assert row["branch"] == "retain_existing_state" and row["mamba_exist"] is True
    assert row["existing_value"][0] == id(existing) and row["candidate_value"][0] == id(candidate)


@pytest.mark.parametrize("clear,cow,int8", [(True, False, False), (False, True, False), (False, True, True), (True, True, False)])
def test_actual_deferred_clear_and_cow_calls_unchanged(native_root, tmp_path, clear, cow, int8):
    _prepare(native_root, tmp_path / "runtime")
    recorder, calls, translations = _recorder(native_root), [], []
    pool_type = type("HybridReqToTokenPool", (), {})
    pool = pool_type()

    def translate(indices):
        translations.append(indices)
        return indices

    pool.translate_mamba_indices = translate
    pool.mamba_pool = SimpleNamespace(clear_slots=lambda indices: calls.append(("clear", indices)))
    pool.copy_mamba_state = lambda src, dst: calls.append(("copy", src, dst))
    pool.mamba_ckpt_pool = SimpleNamespace(load_to_active=lambda *args: calls.append(("load_int8", *args))) if int8 else None
    batch = SimpleNamespace(rids=["cow-batch"], forward_mode=SimpleNamespace(is_extend=lambda: True, is_target_verify=lambda: False, is_draft_extend_v2=lambda: False),
                            mamba_clear_indices=_Tensor((1,)) if clear else None,
                            mamba_cow_src_indices=_Tensor((1,)) if cow else None,
                            mamba_cow_dst_indices=_Tensor((1,)) if cow else None)
    run = _bind(native_root, metadata._RUNNER, "_maybe_execute_deferred_mamba_cow_and_clear", recorder, HybridReqToTokenPool=pool_type)
    run(SimpleNamespace(req_to_token_pool=pool, is_draft_worker=False), batch)
    assert [call[0] for call in calls] == (["clear"] if clear else []) + (["load_int8" if int8 else "copy"] if cow else [])
    assert len(translations) == int(clear) + (2 if cow and not int8 else 0)
    rows = _events(recorder)
    assert len(rows) == int(clear) + int(cow)
    assert all(row[1]["rids"] == ("cow-batch",) for row in rows)
    assert batch.mamba_clear_indices is batch.mamba_cow_src_indices is batch.mamba_cow_dst_indices is None


def test_finished_donor_uses_already_chosen_checkpoint_once(native_root, tmp_path):
    _prepare(native_root, tmp_path / "runtime")
    recorder, selections = _recorder(native_root), []
    backend_type = type("Backend", (), {"int8_ckpt_pool": None})
    backend = backend_type()
    backend.cache = SimpleNamespace(enable_mamba_extra_buffer=True)

    def checkpoint(req, length):
        selections.append((req, length))
        return 128, 1

    backend._select_finished_checkpoint = checkpoint
    req = SimpleNamespace(rid="donor", kv=SimpleNamespace(mamba_last_track_seqlen=256,
                          mamba_prev_track_seqlen=128, mamba_ping_pong_track_buffer=_Tensor((2,))))
    params = SimpleNamespace(mamba_keep_idx=None, mamba_value=None)
    prepare = _bind(native_root, metadata._MAMBA, "prepare_for_caching_req", recorder)
    assert prepare(backend, req, params, 200, True) == 128
    assert len(selections) == 1 and params.mamba_keep_idx == 1
    row = _events(recorder)[0][1]
    assert row["keep_idx"] == 1 and row["cache_len"] == 128 and row["token_ids_len"] == 200
    assert row["insert_value"][0] == id(params.mamba_value)


def test_live_tracking_slot_donation_return_is_observed_without_resolving_it_again(native_root, tmp_path):
    _prepare(native_root, tmp_path / "runtime")
    recorder, donations, allocations = _recorder(native_root), [], []
    backend_type = type("Backend", (), {"int8_ckpt_pool": None})
    backend = backend_type()
    donated, replacement = _Tensor((1,)), _Tensor((1,))

    def donate(req, new_slot):
        donations.append((req, new_slot))
        return donated

    def allocate(req):
        allocations.append(req)
        return replacement

    backend.cache = SimpleNamespace(enable_mamba_extra_buffer=True,
                                    req_to_token_pool=SimpleNamespace(donate_mamba_ping_pong_slot=donate))
    backend._alloc_mamba_slot = allocate
    req = SimpleNamespace(rid="live-donor", kv=SimpleNamespace(mamba_last_track_seqlen=128,
                          mamba_last_track_idx=0, mamba_next_track_idx=1))
    params = SimpleNamespace(mamba_value=None)
    prepare = _bind(native_root, metadata._MAMBA, "prepare_for_caching_req", recorder)
    assert prepare(backend, req, params, 130, False) == 128
    assert donations == [(req, replacement)] and allocations == [req]
    assert params.mamba_value is donated
    row = _events(recorder)[0][1]
    assert row["insert_value"][0] == id(donated) and row["cache_len"] == 128
    assert (row["last_track_idx"], row["next_track_idx"]) == (0, 1)


@pytest.mark.parametrize("branch", ["final", "recompute"])
def test_other_actual_store_branches_only_append_metadata(native_root, tmp_path, branch):
    _prepare(native_root, tmp_path / "runtime")
    recorder = _recorder(native_root)
    store = _bind(native_root, metadata._HYBRID, "_track_mamba_state_extend", recorder)
    state = _Tensor((4, 2, 4, 4), "float32")
    forward = SimpleNamespace(has_mamba_track_mask=True, track_ssm_h_src=_Tensor((0,)),
                              track_ssm_recompute_dst=_Tensor((1,)) if branch == "recompute" else None,
                              track_ssm_final_src=_Tensor((1,)) if branch == "final" else _Tensor((0,)),
                              track_ssm_final_dst=_Tensor((1,)))
    store(None, SimpleNamespace(rids=["other-store"]), None, state, forward,
          track_states=_Tensor((1, 1, 2, 4, 4), "bfloat16") if branch == "recompute" else None)
    row = _events(recorder)[0][1]
    assert row["source"] == ("final_state" if branch == "final" else "recompute")
    assert row["temporal"][1] == "float32" and len(state.writes) == 1


def test_already_instrumented_source_change_is_rejected(native_root, tmp_path):
    _prepare(native_root, tmp_path / "runtime")
    path = native_root / metadata._GDN
    path.write_bytes(path.read_bytes() + b"\n# unexpected post-preparation edit\n")
    before = _contents(native_root)
    with pytest.raises(ValueError, match="Unrecognized runtime metadata source"):
        _prepare(native_root, tmp_path / "different-archive")
    assert _contents(native_root) == before
    assert not (tmp_path / "different-archive").exists()


@pytest.mark.parametrize("swa_floor", [0, 12])
def test_duplicate_release_intervals_and_canonical_rebind(native_root, tmp_path, swa_floor):
    _prepare(native_root, tmp_path / "runtime")
    recorder, frees = _recorder(native_root), []
    full = type("FreeDeviceKV", (), {"__init__": lambda self, indices: setattr(self, "indices", indices)})
    full_only = type("FreeDeviceKVFullOnly", (), {"__init__": lambda self, indices: setattr(self, "indices", indices)})
    component = SimpleNamespace(update_component_on_insert_overlap=lambda **kwargs: kwargs["prefix_len"])
    state = SimpleNamespace(overlap_node=SimpleNamespace(id=42), overlap_prefix_len=8, value=_Tensor((8,)),
                            total_prefix_length=4, params=SimpleNamespace(prev_prefix_len=6, get_evicted_seqlen=lambda component: swa_floor),
                            result=SimpleNamespace(mamba_exist=True), pending_actions=[])
    tree = SimpleNamespace(components=[component], _finish_insert_walk_node=lambda *args: None)
    overlap = _bind(native_root, metadata._TREE, "_insert_overlap_step", recorder, FreeDeviceKV=full,
                    FreeDeviceKVFullOnly=full_only, ComponentType=SimpleNamespace(SWA=1))
    overlap(tree, state)
    queued = _events(recorder)[0][1]
    assert (queued["absolute_start"], queued["absolute_end"]) == (6, 12)
    assert queued["full_only_end"] == (12 if swa_floor else 6)
    allocator = SimpleNamespace(free_segment=lambda indices, start_pos: frees.append(("all", len(indices), start_pos)),
                                free_full_segment=lambda indices, start_pos: frees.append(("full", len(indices), start_pos)))
    apply = _bind(native_root, metadata._CACHE, "_apply_cache_action", recorder, ComponentAction=type("ComponentAction", (), {}),
                  FreeDeviceKV=full, FreeDeviceKVFullOnly=full_only)
    for action in state.pending_actions:
        apply(SimpleNamespace(token_to_kv_pool_allocator=allocator), action)
    assert frees == [("full" if swa_floor else "all", 6, 0)]
    assert _events(recorder)[0][0] == "kv_allocator_release_returned"
    writes, resolutions = [], []
    canonical = _Tensor((12,))

    def path_indices(node_id):
        resolutions.append(node_id)
        return canonical

    cache = SimpleNamespace(page_size=1, path_device_indices=path_indices,
                            req_to_token_pool=SimpleNamespace(write=lambda target, values: writes.append((target, values))))
    req = SimpleNamespace(rid="rebind", kv=SimpleNamespace(req_pool_idx=3, cache_protected_len=6))
    run = _slice(native_root, metadata._CACHE, "checkpoint_into_tree",
                 lambda node: isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "new_last_node",
                 lambda node: isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "_mamba_record"
                 and node.value.args[0].value == "canonical_kv_rebind_enqueued",
                 recorder, self=cache, req=req, result=SimpleNamespace(last_device_node=42, prefix_len=12, mamba_exist=True), page_aligned_len=12)
    run()
    assert resolutions == [42] and len(writes) == 1
    assert writes[0][0] == (3, slice(6, 12)) and len(writes[0][1]) == 6
    row = _events(recorder)[0][1]
    assert row["node_id"] == 42 and row["mamba_exist"] is True
    assert (row["absolute_start"], row["absolute_end"]) == (6, 12)


def test_existing_internal_state_dict_drains_only_responding_process(native_root, tmp_path):
    _prepare(native_root, tmp_path / "runtime")
    recorder = _recorder(native_root)
    recorder["record"]("selected", (("rids", ("a",)),))
    parallel = SimpleNamespace(dp_rank=0, tp_rank=0, pp_rank=0, attn_dp_rank=0, attn_tp_rank=0)
    controller = SimpleNamespace(**{name: lambda state: None for name in (
        "_add_topology", "_add_memory_usage", "_add_disaggregation", "_add_elastic_ep", "_add_speculative",
        "_add_step_times", "_add_rust_server", "_add_env_vars"
    )})
    get_state = _bind(native_root, metadata._INTERNAL, "get_internal_state", recorder,
                      get_context=lambda: SimpleNamespace(resolved_server_args_dict=lambda: {"unchanged": 7, "custom_sigquit_handler": object()}),
                      get_parallel=lambda: parallel, _mamba_drain=recorder["drain"], msgspec_to_builtins=lambda state: state,
                      GetInternalStateReqOutput=lambda **kwargs: kwargs)
    response = get_state(controller, object())["internal_state"]
    assert response["unchanged"] == 7 and "custom_sigquit_handler" not in response
    assert response["mamba_runtime_metadata"]["rows"][0][1] == "selected"
    assert response["mamba_runtime_metadata"]["rank"]["tp_rank"] == 0
    assert get_state(controller, object())["internal_state"]["mamba_runtime_metadata"]["rows"] == ()
    json.dumps(response, allow_nan=False)
