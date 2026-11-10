"""Execute retained native Python call bindings; never import host SGLang/CUDA.

MILES_PINNED_SGLANG_SOURCE may point to another copy of the retained C3 package.
The untracked local evidence is used when present; CI without that evidence skips
these source-dependent tests rather than substituting the host's older SGLang.
The Triton launch is a recorder, not a recurrence implementation.
"""

import ast
import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Optional, Tuple

import pytest

from tests.manual.agent_opd import sglang_mamba_snapshots as snapshots


_RETAINED = (
    Path(__file__).resolve().parents[2]
    / "task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/native-sglang-cache-source-20261111"
    / "exp-1111-042450-358109/source"
)


@pytest.fixture
def native_root(tmp_path):
    source = Path(os.environ.get("MILES_PINNED_SGLANG_SOURCE", _RETAINED))
    if not source.is_dir():
        pytest.skip("Actual retained native SGLang C3 source is not available")
    root = tmp_path / "sglang"
    for relative, identity in snapshots.source_manifest()["files"].items():
        content = (source / relative).read_bytes()
        assert snapshots._sha256(content) == identity["before_sha256"]
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    return root


@pytest.fixture
def qualified_version(monkeypatch):
    monkeypatch.setattr(
        snapshots.importlib.metadata, "version", lambda name: snapshots.source_manifest()["distribution_version"]
    )


def _prepare(root, archive, *, selected_fp32=True):
    return snapshots.prepare_source(
        root, image=snapshots.source_manifest()["image"], selected_fp32=selected_fp32, archive_dir=archive
    )


def _contents(root):
    return {relative: (root / relative).read_bytes() for relative in snapshots.source_manifest()["files"]}


class _Tensor:
    def __init__(self, shape, dtype="bfloat16", slot_stride=None):
        self.shape = shape
        self.dtype = dtype
        self.slot_stride = slot_stride

    def __len__(self):
        return self.shape[0]

    def stride(self, axis):
        assert axis == 0
        if self.slot_stride is not None:
            return self.slot_stride
        result = 1
        for dimension in self.shape[1:]:
            result *= dimension
        return result

    def new_empty(self, *shape):
        return _Tensor(shape, self.dtype)

    def to(self, dtype):
        assert dtype == self.dtype
        return self


class _AutogradFunction:
    @classmethod
    def apply(cls, *args):
        return cls.forward(None, *args)


def _identity(function):
    return function


def _definitions(path, names):
    tree = ast.parse(path.read_bytes())
    definitions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names]
    assert {node.name for node in definitions} == set(names)
    return definitions


def _native_call(root, *, snapshot=None, positions=None, varlen=True, inplace_update=True):
    """Run real extend -> public chunk -> apply/forward -> fwd -> fwd_h bindings."""
    launch = {}

    class Launch:
        def __getitem__(self, grid):
            def record(**kwargs):
                launch.update(kwargs)
                launch["grid"] = grid({"BV": 32})

            return record

    torch = SimpleNamespace(
        Tensor=_Tensor,
        LongTensor=_Tensor,
        float32="float32",
        empty_like=lambda tensor: _Tensor(tensor.shape, tensor.dtype),
        compiler=SimpleNamespace(disable=_identity),
        autograd=SimpleNamespace(Function=_AutogradFunction),
    )
    tensors = {name: _Tensor((1, 130, 2, 128)) for name in ("q", "k", "w")}
    tensors.update(v=_Tensor((1, 130, 2, 64)), u=_Tensor((1, 130, 2, 64)))
    namespace = {
        "torch": torch,
        "Optional": Optional,
        "Tuple": Tuple,
        "CHUNK_SIZE": 64,
        "SUPPRESS_LEVEL": 2,
        "LinearAttnKernelBase": type("LinearAttnKernelBase", (), {"supports_track_state_snapshot": False}),
        "is_cpu": lambda: False,
        "is_npu": lambda: False,
        "is_xpu": lambda: False,
        "input_guard": _identity,
        "autocast_custom_fwd": _identity,
        "l2norm_fwd": lambda tensor: tensor,
        "prepare_chunk_indices": lambda *args: _Tensor((3,), "int64"),
        "prepare_chunk_offsets": lambda *args: _Tensor((3,), "int64"),
        "chunk_local_cumsum": lambda g, **kwargs: g,
        "chunk_gated_delta_rule_fwd_intra": lambda **kwargs: (tensors["w"], tensors["u"], object()),
        "chunk_fwd_o": lambda **kwargs: tensors["v"],
        "triton": SimpleNamespace(cdiv=lambda a, b: (a + b - 1) // b),
        "chunk_gated_delta_rule_fwd_kernel_h_blockdim64": Launch(),
    }
    definitions = _definitions(root / "kernels/ops/attention/fla/chunk_delta_h.py", ["chunk_gated_delta_rule_fwd_h"])
    definitions += _definitions(
        root / "kernels/ops/attention/fla/chunk.py",
        ["chunk_gated_delta_rule_fwd", "ChunkGatedDeltaRuleFunction", "chunk_gated_delta_rule"],
    )
    kernel_class = _definitions(root / "srt/layers/attention/linear/kernels/gdn_triton.py", ["TritonGDNKernel"])[0]
    # Only extend and capability declarations are reached; unrelated methods
    # have annotations for dependencies that this CPU binding test does not load.
    kernel_class.body = [
        node for node in kernel_class.body if not isinstance(node, ast.FunctionDef) or node.name == "extend"
    ]
    module = ast.Module(body=definitions + [kernel_class], type_ignores=[])
    exec(compile(module, "retained-native-SGLang-bindings.py", "exec"), namespace)
    state = _Tensor((4, 2, 64, 128), "float32", slot_stride=65536)
    cache_indices = _Tensor((2,), "int64")
    query_start_loc = _Tensor((3,), "int64") if varlen else None
    output = namespace["TritonGDNKernel"]().extend(
        q=tensors["q"],
        k=tensors["k"],
        v=tensors["v"],
        g=_Tensor((1, 130, 2)),
        beta=_Tensor((1, 130, 2)),
        ssm_states=state,
        cache_indices=cache_indices,
        query_start_loc=query_start_loc,
        inplace_update=inplace_update,
        track_state=snapshot,
        track_chunk_idx=positions,
    )
    return SimpleNamespace(
        launch=launch,
        output=output,
        tensors=tensors,
        state=state,
        cache_indices=cache_indices,
        query_start_loc=query_start_loc,
        capability=namespace["TritonGDNKernel"].supports_track_state_snapshot,
    )


@pytest.mark.parametrize("varlen", [False, True])
@pytest.mark.parametrize("inplace_update", [False, True])
def test_selected_snapshot_call_chain(native_root, qualified_version, tmp_path, varlen, inplace_update):
    snapshot = _Tensor((2, 2, 64, 128), "float32")
    positions = _Tensor((2,), "int32")
    red = _native_call(native_root, snapshot=snapshot, positions=positions, varlen=varlen, inplace_update=inplace_update)
    assert not red.capability and not red.launch["TRACK_STATE"]
    assert red.launch["track_state"] is None and red.launch["track_chunk_idx"] is None
    _prepare(native_root, tmp_path / "archive")
    observed = _native_call(
        native_root, snapshot=snapshot, positions=positions, varlen=varlen, inplace_update=inplace_update
    )
    assert observed.capability and observed.launch["TRACK_STATE"]
    assert observed.launch["track_state"] is snapshot, "native extend silently dropped the selected FP32 snapshot"
    assert observed.launch["track_chunk_idx"] is positions
    assert observed.launch["stride_track_state"] == snapshot.stride(0)
    assert observed.launch["initial_state"] is observed.state
    assert observed.launch["initial_state_indices"] is observed.cache_indices
    assert observed.launch["stride_init_state"] == 65536
    assert observed.launch["cu_seqlens"] is observed.query_start_loc
    assert observed.launch["INPLACE_UPDATE"] is inplace_update
    assert observed.output[0] is observed.tensors["v"]
    assert observed.output[1] is None
    assert observed.output[2] is observed.launch["h"]
    assert observed.launch["h"].dtype == observed.tensors["k"].dtype == "bfloat16"
    assert observed.launch["h"].shape == red.launch["h"].shape
    for key in (
        "grid", "BT", "T", "H", "Hg", "K", "V", "USE_G", "USE_GK", "USE_INITIAL_STATE",
        "SAVE_NEW_VALUE", "IS_VARLEN", "NT_BUCKET", "USE_EXP2",
    ):
        assert observed.launch[key] == red.launch[key]


def test_preparer_archives_exact_sources_and_is_idempotent(native_root, qualified_version, tmp_path):
    original = _contents(native_root)
    red = _prepare(native_root, tmp_path / "baseline", selected_fp32=False)
    assert not red["patch_applied"] and _contents(native_root) == original
    green = _prepare(native_root, tmp_path / "candidate")
    candidate = _contents(native_root)
    assert set(green["changed_files"]) == {snapshots._CHUNK, snapshots._TRITON}
    assert green["patch_applied"] and green["cuda_semantics"] == "UNVERIFIED"
    for relative, identity in snapshots.source_manifest()["files"].items():
        assert snapshots._sha256(candidate[relative]) == identity["after_sha256"]
        assert (tmp_path / "candidate/before" / relative).read_bytes() == original[relative]
        assert (tmp_path / "candidate/after" / relative).read_bytes() == candidate[relative]
    again = _prepare(native_root, tmp_path / "candidate")
    assert not again["patch_applied"] and again["changed_files"] == []
    assert _contents(native_root) == candidate
    assert len((tmp_path / "candidate/preflight.jsonl").read_text().splitlines()) == 2
    fresh = _prepare(native_root, tmp_path / "idempotent-new-archive")
    assert not fresh["patch_applied"]
    for relative in original:
        assert (tmp_path / "idempotent-new-archive/before" / relative).read_bytes() == original[relative]
    diff = (tmp_path / "candidate/selected_fp32.diff").read_text()
    assert diff.count("--- a/") == 2
    with pytest.raises(ValueError, match="Unrecognized SGLang snapshot source"):
        _prepare(native_root, tmp_path / "no-implicit-revert", selected_fp32=False)
    assert _contents(native_root) == candidate
    assert not (tmp_path / "no-implicit-revert").exists()


@pytest.mark.parametrize("relative", list(snapshots.source_manifest()["files"]))
def test_unsupported_source_has_no_partial_writes(native_root, qualified_version, tmp_path, relative):
    target = native_root / relative
    target.write_bytes(target.read_bytes() + b"\n# unsupported fixture change\n")
    before = _contents(native_root)
    with pytest.raises(ValueError, match="Unrecognized SGLang snapshot source"):
        _prepare(native_root, tmp_path / "archive")
    assert _contents(native_root) == before
    assert not (tmp_path / "archive").exists()


@pytest.mark.parametrize("field", ["image", "version", "boolean"])
def test_unsupported_identity_has_no_partial_writes(native_root, tmp_path, monkeypatch, field):
    manifest = snapshots.source_manifest()
    image = manifest["image"] if field != "image" else "unqualified-image"
    selected = True if field != "boolean" else "true"
    version = manifest["distribution_version"] if field != "version" else "0.5.23"
    monkeypatch.setattr(snapshots.importlib.metadata, "version", lambda name: version)
    before = _contents(native_root)
    with pytest.raises(ValueError, match="qualified pinned image|identity differs|JSON boolean"):
        snapshots.prepare_source(native_root, image=image, selected_fp32=selected, archive_dir=tmp_path / "archive")
    assert _contents(native_root) == before
    assert not (tmp_path / "archive").exists()


def test_conflicting_archive_has_no_partial_writes(native_root, qualified_version, tmp_path):
    before = _contents(native_root)
    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / "selected_fp32.diff").write_text("unrelated evidence\n")
    with pytest.raises(ValueError, match="archive differs"):
        _prepare(native_root, archive)
    assert _contents(native_root) == before
    assert sorted(path.name for path in archive.iterdir()) == ["selected_fp32.diff"]


@pytest.mark.parametrize("failure", ["missing_positions", "missing_buffer", "rounded_buffer"])
def test_existing_native_snapshot_contract_is_reached(native_root, qualified_version, tmp_path, failure):
    _prepare(native_root, tmp_path / "archive")
    snapshot = (
        None
        if failure == "missing_buffer"
        else _Tensor((2, 2, 64, 128), "bfloat16" if failure == "rounded_buffer" else "float32")
    )
    positions = None if failure == "missing_positions" else _Tensor((2,), "int32")
    with pytest.raises(AssertionError, match="passed together|must be fp32"):
        _native_call(native_root, snapshot=snapshot, positions=positions)


def test_cold_cuda_binding_is_unchanged(native_root, qualified_version, tmp_path):
    red = _native_call(native_root)
    _prepare(native_root, tmp_path / "archive")
    green = _native_call(native_root)
    assert green.capability
    assert green.launch["TRACK_STATE"] is False
    assert green.launch["track_state"] is green.launch["track_chunk_idx"] is None
    assert green.launch["stride_track_state"] == 0
    assert green.output[0].dtype == red.output[0].dtype
    assert green.launch["h"].shape == red.launch["h"].shape
    assert green.launch["h"].dtype == red.launch["h"].dtype


@pytest.mark.parametrize("platform", ["cuda", "cpu", "npu", "xpu"])
def test_snapshot_capability_is_native_cuda_only(native_root, qualified_version, tmp_path, platform):
    _prepare(native_root, tmp_path / "archive")
    definitions = _definitions(native_root / snapshots._TRITON, ["TritonGDNKernel"])
    namespace = {
        "LinearAttnKernelBase": type("LinearAttnKernelBase", (), {}),
        "is_cpu": lambda: platform == "cpu",
        "is_npu": lambda: platform == "npu",
        "is_xpu": lambda: platform == "xpu",
    }
    future = ast.parse("from __future__ import annotations").body
    exec(compile(ast.Module(body=future + definitions, type_ignores=[]), "native-GDN-capability.py", "exec"), namespace)
    assert namespace["TritonGDNKernel"].supports_track_state_snapshot is (platform == "cuda")


def test_kernel_recurrence_positions_allocation_copy_and_cold_output_are_unchanged(native_root, qualified_version, tmp_path):
    original = _contents(native_root)
    _prepare(native_root, tmp_path / "archive")
    candidate = _contents(native_root)
    for relative in original.keys() - {snapshots._CHUNK, snapshots._TRITON}:
        assert candidate[relative] == original[relative]
    before = ast.parse(original[snapshots._CHUNK])
    after = ast.parse(candidate[snapshots._CHUNK])
    unchanged_calls = {"chunk_local_cumsum", "chunk_gated_delta_rule_fwd_intra", "chunk_fwd_o", "l2norm_fwd"}

    def unchanged(tree):
        return [
            ast.dump(node)
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in unchanged_calls
        ]

    assert unchanged(before) == unchanged(after)
    assert [ast.dump(node) for node in ast.walk(before) if isinstance(node, ast.Return)] == [
        ast.dump(node) for node in ast.walk(after) if isinstance(node, ast.Return)
    ]
    for method in ("packed_decode", "decode", "target_verify"):
        before_method = next(
            node for node in ast.walk(ast.parse(original[snapshots._TRITON]))
            if isinstance(node, ast.FunctionDef) and node.name == method
        )
        after_method = next(
            node for node in ast.walk(ast.parse(candidate[snapshots._TRITON]))
            if isinstance(node, ast.FunctionDef) and node.name == method
        )
        assert ast.dump(before_method) == ast.dump(after_method)


def test_cli_returns_preflight_receipt(native_root, qualified_version, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        [
            "sglang_mamba_snapshots",
            "--sglang-path", str(native_root),
            "--image", snapshots.source_manifest()["image"],
            "--archive-dir", str(tmp_path / "archive"),
            "--selected-fp32",
        ],
    )
    snapshots.main()
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["selected_fp32"] is True and receipt["patch_applied"] is True
    assert receipt["sglang_path"] == str(native_root)
