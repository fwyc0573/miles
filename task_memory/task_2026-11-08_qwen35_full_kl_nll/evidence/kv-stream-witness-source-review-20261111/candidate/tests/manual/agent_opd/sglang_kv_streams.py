"""Prepare CPU-only KV stream receipts in the opted-in pinned CUDA diagnostic.

Call after selected-FP32 and Mamba CPU-metadata preparation, before any native
runtime/attention imports or teacher startup. Only CPP stores return an actual
in-call stream scalar; prefix-valid Triton terminals remain stream-UNVERIFIED.
No payload capture, device allocation/readback, synchronization, or policy edit
is installed. CPU source binding is not native compilation or runtime acceptance.
"""

import difflib
import importlib.metadata
import json
from pathlib import Path

from tests.manual.agent_opd import sglang_mamba_runtime_metadata as metadata


_CONTEXT = "srt/model_executor/forward_context.py"
_POOL = "srt/mem_cache/memory_pool.py"
_STORE = "kernels/ops/kvcache/kvcache.py"
_CPP = "kernels/jit/csrc/elementwise/kvcache.cuh"
_RUNNER = metadata._RUNNER
_RECORDER = metadata._RECORDER
_SOURCE_JOB = "exp-1111-102145-988437"
_FFI_VERSION = "0.1.11"

# Complete Source590, not the earlier collection that omitted Cython/allocators.
# Unedited dependencies qualify the publication, launcher, export and allocator
# paths; they are archived unchanged alongside the five actual source edits.
_NATIVE_FILES = {
    _CONTEXT: "e612cb6399e58a1c01d7ce72e5309148edbb4b0d28eccc053489c6cc5c6b3852",
    _POOL: "e077773e25c02be4dc597741e5f987375a221e595bccf92997dea684d5445a26",
    _STORE: "fe75ca2abad09ee4911f1049f1c054d93f0470578f2a3e234452d19980e0ad81",
    _CPP: "8b4cc36204b5623608c2467974bcd2a8daf283e96cdbd2f7ee268b07fa0f12e6",
    "kernels/jit/include/sgl_kernel/utils.cuh": "18b0bb2e27dccc20d7509e8b6b6c16e2b57a5ce98be648865fb75059be8a13db",
    "kernels/jit/utils/compile/spec.py": "f762d7d90adb2770988ab0d17b444496d9d611531ab136eb37b8c8707dd42b2f",
    "kernels/jit/utils/compile/loader.py": "f4437c88aae8ae55a315bef9f52e19b2dabd3ad8a2cf0ffaab2a6786dbb52993",
    "kernels/jit/utils/compile/cache.py": "3a9c277d676596e467d6a1e700e65ab2fb5ccf91b264ebe1c3cc06659fa470bf",
    "srt/model_executor/runner/eager_runner.py": "6ac59ed3d5758e52298054b822852e877a17c75de47c3e83709a00b92967d591",
    "srt/mem_cache/kv_cache_configurator.py": "1e31685151ea6ed110c2a659ea0ed975493d0eccf5295196567756bd5591887b",
    "srt/mem_cache/allocator/base.py": "17c07a9ab32c62932048d3579e620eaa2e2558b03b828df152b2ee953c4bfe32",
    "srt/mem_cache/allocator/token.py": "ee09d0021b69b111e3262811e2fdaf2f495ecfc2cf6ed142070a7f7e95a030ec",
    "srt/utils/custom_op.py": "16ce982c284ac85d437b9a6d3ccbe12e92b3ba59c9c1e3dbe0d54be48d8e0166",
    "tvm_ffi/cython/function.pxi": "40fba9880817d3b013e8978146491110434bd8b36d3a702ff4a93a230ff1c021",
    "tvm_ffi/cython/tvm_ffi_python_helpers.h": "a11be0560a2cc4b75845ab63fc7cb67f0dd890b8d89c32b58d7efb408172089f",
    "tvm_ffi/src/ffi/extra/env_context.cc": "941edd8415cca875c010f456f1f06f2f336b8978c64531f4953c1c4d848d490c",
    "tvm_ffi/_optional_torch_c_dlpack.py": "71fa7ff562ab5cb6a714200f31b5caa3d0a1c9cf949fd21c6a2a830580c60a18",
    "tvm_ffi/include/tvm/ffi/function.h": "42dd75a992d4fc9b5216709a5e115c6af91270843a7ab63cc3e9b6ba3d5a1236",
    "tvm_ffi/include/tvm/ffi/extra/c_env_api.h": "afca6fcd61cc385772c7bd0aef1d75b41195e40ed50075be9f7166dbeed6b0c9",
}

_IMPORT = metadata._IMPORT + (
    "from sglang.srt.model_executor.forward_context import (\n"
    "    get_forward_context, has_forward_context,\n"
    ")\n"
)
_BATCH_LOCAL = "_kv_batch = get_forward_context().forward_batch if has_forward_context() else None\n"
_BATCH_FIELDS = tuple(
    (name, f"tuple(_kv_batch.{attribute}) if _kv_batch is not None and _kv_batch.{attribute} is not None else None")
    for name, attribute in (
        ("rids", "rids"), ("prefix_lens", "extend_prefix_lens_cpu"),
        ("extend_lens", "extend_seq_lens_cpu"),
    )
)


def _descriptor(name: str, expression: str) -> tuple:
    return ((name, f"_mamba_tensor({expression})"), (f"{name}_data_ptr", f"{expression}.data_ptr()"))


def _terminal(kind: str, *, indent: int, prefix_valid: bool) -> str:
    """Emit only CPU fields at the class-owned, already-completed host call."""
    fields = (
        ("store_kind", repr(kind)),
        ("native_stream_scalar_observed", "False"),
        ("native_actual_stream", "None"),
        ("stream_qualification", repr("UNVERIFIED; CPP scalar is a separate in-call receipt")),
        ("pool_class", "(type(self).__module__, type(self).__qualname__)"),
        ("pool_object_id", "id(self)"),
        ("layer_id", "layer.layer_id if layer is not None else layer_id"),
        ("pool_layer_id", "layer_id"),
        ("buffer_layer_idx", "layer_id - self.start_layer"),
        *_BATCH_FIELDS,
        *_descriptor("k_cache", "self.k_buffer[layer_id - self.start_layer]"),
        *_descriptor("v_cache", "self.v_buffer[layer_id - self.start_layer]"),
        *_descriptor("writer_loc", "loc_2d" if prefix_valid else "loc"),
    )
    if prefix_valid:
        fields += _descriptor("commit_lens", "commit_lens")
    return " " * indent + _BATCH_LOCAL + metadata._receipt("kv_store_terminal", fields, indent)


_EDITS = {
    _CONTEXT: (
        (
            "    moe_num_token_non_padded: Optional[Callable[[], Optional[torch.Tensor]]] = None\n",
            "    moe_num_token_non_padded: Optional[Callable[[], Optional[torch.Tensor]]] = None\n"
            "    forward_batch: Optional[ForwardBatch] = None\n",
        ),
        (
            "            ctx, moe_num_token_non_padded=forward_batch.moe_num_token_non_padded\n",
            "            ctx, moe_num_token_non_padded=forward_batch.moe_num_token_non_padded,\n"
            "            forward_batch=forward_batch,\n",
        ),
    ),
    _CPP: (
        ("  static void\n  run(", "  static int64_t\n  run("),
        ("    if (batch_size == 0) return;\n", "    if (batch_size == 0) return -1;\n"),
        (
            "    LaunchKernel(num_blocks, {device::kWarpThreads, num_warps}, device)  //\n"
            "        .enable_pdl(kUsePDL)(kernel, params);\n",
            "    const auto stream = LaunchKernel::resolve_device(device);\n"
            "    LaunchKernel(num_blocks, {device::kWarpThreads, num_warps}, stream)  //\n"
            "        .enable_pdl(kUsePDL)(kernel, params);\n"
            "    return static_cast<int64_t>(reinterpret_cast<uintptr_t>(stream));\n",
        ),
    ),
    _STORE: (
        ("import torch\n", "import torch\n\n" + _IMPORT),
        (
            "    module.store_cache(\n",
            "    _kv_torch_stream = torch._C._cuda_getCurrentRawStream(k.device.index)\n"
            "    _kv_native_stream = module.store_cache(\n",
        ),
        (
            "        reserved_skip_index,\n    )\n",
            "        reserved_skip_index,\n    )\n"
            "    " + _BATCH_LOCAL + metadata._receipt("kv_store_stream", (
                ("store_kind", repr("cpp_store_cache")),
                ("native_stream_scalar_observed", "_kv_native_stream != -1"),
                ("native_actual_stream", "_kv_native_stream if _kv_native_stream != -1 else None"),
                ("torch_current_raw_stream", "_kv_torch_stream"),
                ("launch_enqueued", "_kv_native_stream != -1"),
                ("device_store_completion", repr("UNVERIFIED")),
                *_BATCH_FIELDS,
                *_descriptor("k_cache", "k_cache"), *_descriptor("v_cache", "v_cache"),
                *_descriptor("writer_loc", "indices"),
                ("row_bytes", "row_bytes"), ("v_row_bytes", "v_row_bytes"),
                ("size_limit", "size_limit"), ("reserved_skip_index", "reserved_skip_index"),
            ), 4),
        ),
    ),
    _POOL: (
        ("import torch\n", "import torch\n\n" + _IMPORT),
        (
            "        self._store_kv_layer(layer_id - self.start_layer, loc, cache_k, cache_v)\n",
            "        self._store_kv_layer(layer_id - self.start_layer, loc, cache_k, cache_v)\n"
            + _terminal("mha_set_kv_buffer_impl", indent=8, prefix_valid=False),
        ),
        (
            "                v_scale_is_tensor=isinstance(v_scale, torch.Tensor) and v_scale.is_cuda,\n"
            "            )\n            return\n",
            "                v_scale_is_tensor=isinstance(v_scale, torch.Tensor) and v_scale.is_cuda,\n"
            "            )\n" + _terminal("mha_prefix_valid_triton_fp8", indent=12, prefix_valid=True)
            + "            return\n",
        ),
        (
            "            store_dtype=self.store_dtype,\n        )\n",
            "            store_dtype=self.store_dtype,\n        )\n"
            + _terminal("mha_prefix_valid_triton", indent=8, prefix_valid=True),
        ),
    ),
    _RUNNER: (
        (
            "        self.token_to_kv_pool_allocator = result.token_to_kv_pool_allocator\n",
            "        self.token_to_kv_pool_allocator = result.token_to_kv_pool_allocator\n"
            + metadata._receipt("kv_allocator_created", (
                ("allocator_class", "(type(self.token_to_kv_pool_allocator).__module__, type(self.token_to_kv_pool_allocator).__qualname__)"),
                ("allocator_object_id", "id(self.token_to_kv_pool_allocator)"),
                ("pool_class", "(type(self.token_to_kv_pool).__module__, type(self.token_to_kv_pool).__qualname__)"),
                ("pool_object_id", "id(self.token_to_kv_pool)"),
                ("page_size", "self.token_to_kv_pool_allocator.page_size"),
                ("size", "self.token_to_kv_pool_allocator.size"),
                ("dtype", "str(self.token_to_kv_pool_allocator.dtype)"),
                ("device", "str(self.token_to_kv_pool_allocator.device)"),
            ), 8),
        ),
    ),
}


def source_manifest() -> dict:
    owner = metadata.source_manifest()
    files = {
        relative: {"metadata_base_sha256": identity["before_sha256"], "native_source_job": _SOURCE_JOB}
        for relative, identity in owner["files"].items()
    }
    files.update({relative: {"native_sha256": digest, "native_source_job": _SOURCE_JOB}
                  for relative, digest in _NATIVE_FILES.items()})
    files[_RECORDER] = {"metadata_recorder_sha256": metadata._sha256(metadata._RECORDER_SOURCE.encode())}
    return {"image": owner["image"], "distribution_version": owner["distribution_version"],
            "tvm_ffi_distribution_version": _FFI_VERSION, "native_source_job": _SOURCE_JOB, "files": files}


def _rewrite(relative: str, content: bytes, *, reverse: bool = False) -> bytes:
    text = content.decode()
    edits = _EDITS.get(relative, ())
    for before, after in reversed(edits) if reverse else edits:
        old, new = (after, before) if reverse else (before, after)
        old, new = "\n" + old, "\n" + new
        if text.count(old) != 1:
            raise ValueError(f"KV stream source seam differs: {relative}")
        text = text.replace(old, new)
    return text.encode()


def _qualified_baseline(relative: str, content: bytes, identity: dict) -> None:
    if "metadata_base_sha256" in identity:
        # Reuse the owner exactly: require its completed overlay, not its input.
        base = metadata._rewrite(relative, content, reverse=True)
        if metadata._sha256(base) != identity["metadata_base_sha256"] or metadata._rewrite(relative, base) != content:
            raise ValueError(f"KV stream metadata precondition differs: {relative}")
    else:
        expected = identity.get("native_sha256", identity.get("metadata_recorder_sha256"))
        if metadata._sha256(content) != expected:
            raise ValueError(f"KV stream source identity differs: {relative}; sha256={metadata._sha256(content)}")


def _sources(paths: dict, manifest: dict) -> tuple[dict, dict, dict]:
    current, original, candidate = {}, {}, {}
    for relative, identity in manifest["files"].items():
        path = paths[relative]
        if not path.is_file():
            raise ValueError(f"Required KV stream source absent: {path}; identity={identity}")
        content = path.read_bytes()
        baseline = content
        try:
            _qualified_baseline(relative, baseline, identity)
        except ValueError:
            if relative not in _EDITS:
                raise
            try:
                baseline = _rewrite(relative, content, reverse=True)
                _qualified_baseline(relative, baseline, identity)
            except ValueError as unsupported:
                raise ValueError(f"Unrecognized KV stream source: {path}; sha256={metadata._sha256(content)}") from unsupported
        rewritten = _rewrite(relative, baseline)
        if content not in (baseline, rewritten):
            raise ValueError(f"Unrecognized KV stream source: {path}")
        if relative in _EDITS and path.suffix == ".py":
            compile(rewritten, str(path), "exec")
        current[relative], original[relative], candidate[relative] = content, baseline, rewritten
    return current, original, candidate


def _archive(archive: Path, original: dict, candidate: dict, manifest: dict) -> None:
    artifacts = {"source_manifest.json": (json.dumps(manifest, indent=2) + "\n").encode()}
    diff = []
    for relative in original:
        artifacts[f"before/{relative}"], artifacts[f"after/{relative}"] = original[relative], candidate[relative]
        if original[relative] != candidate[relative]:
            diff.extend(difflib.unified_diff(original[relative].decode().splitlines(keepends=True),
                                             candidate[relative].decode().splitlines(keepends=True),
                                             fromfile=f"a/{relative}", tofile=f"b/{relative}"))
    artifacts["kv_streams.diff"] = "".join(diff).encode()
    for relative, content in artifacts.items():
        path = archive / relative
        if path.exists() and path.read_bytes() != content:
            raise ValueError(f"KV stream archive differs: {path}")
    for relative, content in artifacts.items():
        path = archive / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(content)


def prepare_source(native_sglang_package_root: Path, *, image: str, archive_dir: Path) -> dict:
    """Qualify both earlier overlays and every dependency before source writes.

    Idempotent only for this exact witness. TVM sources are located through the
    installed distribution, never substituted from a nested retained snapshot.
    No previous preparer, runtime import, compiler or GPU operation is invoked.
    """
    manifest = source_manifest()
    if image != manifest["image"]:
        raise ValueError("KV stream witness requires the qualified pinned image")
    for name, expected in (("sglang", manifest["distribution_version"]),
                           ("apache-tvm-ffi", manifest["tvm_ffi_distribution_version"])):
        version = importlib.metadata.version(name)
        if version != expected:
            raise ValueError(f"KV stream dependency identity differs: {name}={version}; expected={expected}")
    root, archive = native_sglang_package_root.resolve(), archive_dir.resolve()
    ffi = importlib.metadata.distribution("apache-tvm-ffi")
    paths = {relative: Path(ffi.locate_file(relative)).resolve() if relative.startswith("tvm_ffi/")
             else root / relative for relative in manifest["files"]}
    current, original, candidate = _sources(paths, manifest)
    manifest["files"] = {relative: {**identity, "before_sha256": metadata._sha256(original[relative]),
                                    "after_sha256": metadata._sha256(candidate[relative])}
                         for relative, identity in manifest["files"].items()}
    _archive(archive, original, candidate, manifest)
    changed = [relative for relative in candidate if current[relative] != candidate[relative]]
    for relative in changed:
        paths[relative].write_bytes(candidate[relative])
    observed = {relative: metadata._sha256(path.read_bytes()) for relative, path in paths.items()}
    if observed != {relative: metadata._sha256(content) for relative, content in candidate.items()}:
        raise ValueError("KV stream source changed during preflight")
    receipt = {
        **manifest, "sglang_path": str(root), "archive_dir": str(archive),
        "source_paths": {relative: str(path) for relative, path in paths.items()},
        "observed_before_sha256": {relative: metadata._sha256(content) for relative, content in current.items()},
        "observed_after_sha256": observed, "changed_files": changed, "patch_applied": bool(changed),
        "diagnostic_only": True, "selected_fp32_precondition": True, "cpu_metadata_precondition": True,
        "readback_key": "mamba_runtime_metadata", "readback": "existing process-local internal-state drain",
        "stream_witness_scope": "CPP calls only; CUDA prefix-valid Triton remains UNVERIFIED",
        "physical_slot_values": "UNMEASURED", "native_compilation": "UNVERIFIED",
        "actual_streams_allocator_class_vectors": "UNVERIFIED; CPU binding is not native execution",
    }
    with (archive / "preflight.jsonl").open("a") as stream:
        stream.write(json.dumps(receipt, allow_nan=False) + "\n")
    return receipt
