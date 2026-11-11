"""Dry source composition only: never a native builder or serving fallback.

Run with the host CPU test environment. Native preparation is explicitly injected
for this source/AST check; no .so is fabricated, imported, or declared qualified.
"""

import argparse
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tests.manual.agent_opd import sglang_kv_coherence as coherence
from tests.manual.agent_opd import sglang_kv_streams as streams
from tests.manual.agent_opd import sglang_mamba_runtime_metadata as metadata
from tests.manual.agent_opd import sglang_mamba_snapshots as snapshots
from tests.manual.agent_opd import sglang_rust_kv_observer as native


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    versions = {"sglang": streams.source_manifest()["distribution_version"], "apache-tvm-ffi": "0.1.11"}
    image = streams.source_manifest()["image"]
    with tempfile.TemporaryDirectory(prefix="kv-coherence-source-di-", dir="/data/ycfeng/tmp/opencode-v2-tmp/opencode") as temporary:
        root = Path(temporary) / "sglang"
        relatives = set(streams.source_manifest()["files"]) | set(coherence._EXTRA_PINS) | set(native._PYTHON_PINS)
        for relative in relatives:
            if relative == metadata._RECORDER:
                continue
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((args.source / relative).read_bytes())
        native_calls = []
        def native_source_di(root_arg: Path, *, image: str, archive_dir: Path, build_receipt: Path) -> dict:
            native_calls.append(str(root_arg))
            adapter = root_arg / native._ADAPTER
            adapter.write_bytes(native._adapter_candidate(adapter.read_bytes()))
            return {"scope": "EXPLICIT CPU SOURCE DI ONLY", "production_native_build": "PENDING",
                    "production_native_load": "NOT PERFORMED", "native_gpu_proof": "PENDING",
                    "adapter": str(adapter), "package_root": str(root_arg), "build_receipt_input": str(build_receipt),
                    "no_fake_binary": True}
        with patch.object(streams.importlib.metadata, "version", versions.__getitem__), \
             patch.object(streams.importlib.metadata, "distribution", lambda name: SimpleNamespace(locate_file=lambda relative: root / relative)), \
             patch.object(native, "prepare_source", native_source_di):
            snapshots.prepare_source(root, image=image, selected_fp32=True, archive_dir=Path(temporary) / "fp32")
            metadata.prepare_runtime_metadata(root, image=image, archive_dir=Path(temporary) / "metadata")
            streams.prepare_source(root, image=image, archive_dir=Path(temporary) / "wit")
            receipt = coherence.prepare_source(root, image=image, archive_dir=Path(temporary) / "coherence",
                                               build_receipt=Path("PENDING-production-observer-build.json"))
            assert len(native_calls) == 1
        for name in ("source_manifest.json", "coherence.diff", "preflight.jsonl"):
            (args.output / name).write_bytes((Path(temporary) / "coherence" / name).read_bytes())
        (args.output / "receipt.json").write_text(json.dumps({"task_id": "profile-kv-coherence-collector-implementation-20261111",
                                                             "scope": "CPU_SOURCE_DI_ONLY", "native_calls": len(native_calls),
                                                             "receipt": receipt}, indent=2) + "\n")
    print("CPU_SOURCE_DI_ONLY", args.output, "production native/GPU qualification PENDING")


if __name__ == "__main__":
    main()
