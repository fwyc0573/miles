"""Wire existing selected FP32 GDN snapshots in one qualified native SGLang.

Run with the pinned worker's Python before importing SGLang attention modules
or launching engines. This standard-library preflight does not import SGLang,
run kernels, change tracking policy, or change the normal h/output/final state.

    python -m tests.manual.agent_opd.sglang_mamba_snapshots \
        --sglang-path "$SGLANG_PACKAGE" --image "$IMAGE" \
        --archive-dir "$ARCHIVE" --selected-fp32

Only the retained C3 source identity is supported. The older host CPU package
is not a substitute. CUDA and teacher warm-cache parity remain unverified.
"""

import argparse
import ast
import difflib
import hashlib
import importlib.metadata
import json
from pathlib import Path


_IMAGE = (
    "artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:"
    "165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805"
)
_VERSION = "0.5.24.dev80+g056f871"
_CHUNK = "kernels/ops/attention/fla/chunk.py"
_TRITON = "srt/layers/attention/linear/kernels/gdn_triton.py"
_FILES = {
    _CHUNK: {
        "before_sha256": "0fa7c1a0c1b9a9f1b5548dfeed58181df88ded8e4bbb36e27ce63e16c3d7fd85",
        "after_sha256": "b2c1cd76ab3558b893e082f07a8c587520e624e9988d19c0c1afa4f32a72e43c",
    },
    _TRITON: {
        "before_sha256": "ede52671dd880b4317c2308ad58d21d33544044b7bddda93d24bc08216fa812a",
        "after_sha256": "7060585d86347561a2caf36492163b584152e32efddea17b5b4cc8c33c5774bf",
    },
    "kernels/ops/attention/fla/chunk_delta_h.py": {
        "before_sha256": "e37fa6885dd50e945fb470ef3b858573f812c2d7590ed8decc627f15f4bea1c2",
    },
    "srt/layers/attention/linear/kernels/kernel_backend.py": {
        "before_sha256": "bb75a7e69b7c3fdc5274137f215a0118ef8f999db4c9175e871953db33bd8505",
    },
    "srt/layers/attention/linear/gdn_backend.py": {
        "before_sha256": "04f4d78226b0c91e97fe5b1768ccba2719bcf1996faffb32e37ef580d66fab13",
    },
    "srt/layers/attention/hybrid_linear_attn_backend.py": {
        "before_sha256": "e6f797a346bf7534026c963188e7383ec5eded10b94a75811ddb7867cc9980ef",
    },
}

# Small reversible source edits, not copies of the dependency's algorithms.
# Hash checks precede every edit; all candidate files are checked before writes.
_EDITS = {
    _TRITON: (
        (
            "    supports_strided_target_verify_qkv: bool = True\n",
            "    supports_strided_target_verify_qkv: bool = True\n"
            "    # Only the native CUDA chunk kernel honors selected FP32 snapshots.\n"
            "    supports_track_state_snapshot: bool = (\n"
            "        not is_cpu() and not is_npu() and not is_xpu()\n"
            "    )\n",
            1,
        ),
        (
            '        inplace_update_args = {"inplace_update": inplace_update}\n',
            '        inplace_update_args = {"inplace_update": inplace_update}\n'
            "        snapshot_args = {}\n"
            "        if self.supports_track_state_snapshot:\n"
            "            snapshot_args = {\n"
            '                "track_state": kwargs.get("track_state"),\n'
            '                "track_chunk_idx": kwargs.get("track_chunk_idx"),\n'
            "            }\n",
            1,
        ),
        (
            "            **inplace_update_args,\n",
            "            **inplace_update_args,\n            **snapshot_args,\n",
            1,
        ),
    ),
    _CHUNK: (
        (
            "    inplace_update: bool = True,\n",
            "    inplace_update: bool = True,\n"
            "    track_state: Optional[torch.Tensor] = None,\n"
            "    track_chunk_idx: Optional[torch.Tensor] = None,\n",
            2,
        ),
        (
            "        inplace_update: bool = True,\n",
            "        inplace_update: bool = True,\n"
            "        track_state: Optional[torch.Tensor] = None,\n"
            "        track_chunk_idx: Optional[torch.Tensor] = None,\n",
            1,
        ),
        (
            "        chunk_indices=chunk_indices,\n        inplace_update=inplace_update,\n    )",
            "        chunk_indices=chunk_indices,\n        inplace_update=inplace_update,\n"
            "        track_state=track_state,\n        track_chunk_idx=track_chunk_idx,\n    )",
            1,
        ),
        (
            "            chunk_indices=chunk_indices,\n            inplace_update=inplace_update,\n        )",
            "            chunk_indices=chunk_indices,\n            inplace_update=inplace_update,\n"
            "            track_state=track_state,\n            track_chunk_idx=track_chunk_idx,\n        )",
            1,
        ),
        (
            "        inplace_update,\n    )",
            "        inplace_update,\n        track_state,\n        track_chunk_idx,\n    )",
            1,
        ),
        (
            "            Whether to write final states back to `initial_state`. Default: `True`.\n",
            "            Whether to write final states back to `initial_state`. Default: `True`.\n"
            "        track_state (Optional[torch.Tensor]):\n"
            "            Selected FP32 state buffer of shape `[N, H, V, K]`; normal `h` is unchanged.\n"
            "        track_chunk_idx (Optional[torch.Tensor]):\n"
            "            Per-sequence chunk-entry index to snapshot; -1 skips that row.\n"
            "            Must be supplied together with `track_state`.\n",
            1,
        ),
    ),
}


def source_manifest() -> dict:
    """Return the qualified image/version and narrowly inspected file identities."""
    return {
        "image": _IMAGE,
        "distribution_version": _VERSION,
        "native_source_job": "exp-1111-042450-358109",
        "files": {
            relative: {"after_sha256": identity["before_sha256"], **identity} for relative, identity in _FILES.items()
        },
    }


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _rewrite(relative: str, content: bytes, *, reverse: bool = False) -> bytes:
    text = content.decode("utf-8")
    edits = _EDITS.get(relative, ())
    for before, after, count in reversed(edits) if reverse else edits:
        old, new = (after, before) if reverse else (before, after)
        # Match complete lines so a four-space pattern never hits eight spaces.
        old, new = "\n" + old, "\n" + new
        if text.count(old) != count:
            raise ValueError(f"Snapshot source seam differs: {relative}")
        text = text.replace(old, new)
    return text.encode("utf-8")


def _source_versions(root: Path, selected_fp32: bool) -> tuple[dict, dict, dict]:
    current, original, candidate = {}, {}, {}
    for relative, identity in source_manifest()["files"].items():
        content = (root / relative).read_bytes()
        digest = _sha256(content)
        allowed = {identity["before_sha256"]}
        if selected_fp32:
            allowed.add(identity["after_sha256"])
        if digest not in allowed:
            raise ValueError(f"Unrecognized SGLang snapshot source; refusing to alter {root / relative} ({digest})")
        current[relative] = content
        original[relative] = _rewrite(relative, content, reverse=True) if digest != identity["before_sha256"] else content
        candidate[relative] = _rewrite(relative, original[relative]) if selected_fp32 else original[relative]
        expected = identity["after_sha256" if selected_fp32 else "before_sha256"]
        if _sha256(original[relative]) != identity["before_sha256"] or _sha256(candidate[relative]) != expected:
            raise ValueError(f"Snapshot edit produced an unexpected source identity: {relative}")
        ast.parse(candidate[relative], filename=str(root / relative))
    return current, original, candidate


def _archive_sources(archive_dir: Path, original: dict, candidate: dict, manifest: dict) -> None:
    artifacts = {"source_manifest.json": (json.dumps(manifest, indent=2) + "\n").encode()}
    diff = []
    for relative in original:
        artifacts[f"before/{relative}"] = original[relative]
        artifacts[f"after/{relative}"] = candidate[relative]
        diff.extend(
            difflib.unified_diff(
                original[relative].decode().splitlines(keepends=True),
                candidate[relative].decode().splitlines(keepends=True),
                fromfile=f"a/{relative}",
                tofile=f"b/{relative}",
            )
        )
    artifacts["selected_fp32.diff"] = "".join(diff).encode()
    # A conflicting evidence directory is rejected before any source is touched.
    for relative, content in artifacts.items():
        path = archive_dir / relative
        if path.exists() and path.read_bytes() != content:
            raise ValueError(f"Snapshot source archive differs: {path}")
    for relative, content in artifacts.items():
        path = archive_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_bytes(content)


def prepare_source(root: Path, *, image: str, selected_fp32: bool, archive_dir: Path) -> dict:
    """Verify all six source files before applying the two-file wiring candidate.

    False verifies/archives the pristine baseline and never reverses a candidate.
    True accepts pristine or exactly prepared files and is idempotent. Invalid
    identity or conflicting archive fails before dependency source writes.
    """
    if type(selected_fp32) is not bool:
        raise ValueError("selected_fp32 must be a JSON boolean")
    manifest = source_manifest()
    if image != manifest["image"]:
        raise ValueError("Snapshot preflight requires the qualified pinned image")
    version = importlib.metadata.version("sglang")
    if version != manifest["distribution_version"]:
        raise ValueError(f"Snapshot dependency identity differs: version={version}")
    root, archive_dir = root.resolve(), archive_dir.resolve()
    current, original, candidate = _source_versions(root, selected_fp32)
    _archive_sources(archive_dir, original, candidate, manifest)
    changed = [relative for relative in current if current[relative] != candidate[relative]]
    for relative in changed:
        (root / relative).write_bytes(candidate[relative])
    observed_after = {relative: _sha256((root / relative).read_bytes()) for relative in candidate}
    if observed_after != {relative: _sha256(content) for relative, content in candidate.items()}:
        raise ValueError("Snapshot dependency changed during preflight")
    receipt = {
        **manifest,
        "sglang_path": str(root),
        "selected_fp32": selected_fp32,
        "snapshot_dtype": "float32" if selected_fp32 else None,
        "snapshot_capability": "native CUDA only" if selected_fp32 else "unchanged",
        "observed_before_sha256": {relative: _sha256(content) for relative, content in current.items()},
        "observed_after_sha256": observed_after,
        "changed_files": changed,
        "patch_applied": bool(changed),
        "archive_dir": str(archive_dir),
        "cuda_semantics": "UNVERIFIED",
    }
    with (archive_dir / "preflight.jsonl").open("a") as stream:
        stream.write(json.dumps(receipt, allow_nan=False) + "\n")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sglang-path", type=Path, required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--selected-fp32", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            prepare_source(
                args.sglang_path, image=args.image, selected_fp32=args.selected_fp32, archive_dir=args.archive_dir
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
