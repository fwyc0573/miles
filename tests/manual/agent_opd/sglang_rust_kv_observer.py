"""Pinned production-native OLD observer preparation; no payload collection.

Builds use SGLang's existing loader in fresh CPU processes. Preparation requires
a passing four-way native qualification receipt and a private package copy.
Neither entrypoint mutates the baseline installation or enables formal builds.
"""

from __future__ import annotations

import difflib
import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


MODULE = "sglang.srt.mem_cache.rust_tree_core.mem_cache"
TASK_ID = "profile-native-rust-kv-observer-implementation-20261111"
IMAGE = "artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805"
ORIGINAL_BINARY_SHA256 = "2c1e54965c8139358df1ef2a7751620c339ad1ff4988cee54cc35467a8b90f6c"
INVALIDATION_ERROR_MARKER = "old_full_observer_invalidation_failed"
_ADAPTER = "srt/mem_cache/rust_tree_core/adapter.py"
_PYTHON_PINS = {
    _ADAPTER: "4caf80d2d909e548b04cc44a664b7dd7adb6c919d7d1d56f9c9d7c25e5f92635",
    "srt/rust_extensions/loader.py": "0c25123a7e1c051a7f285abdb0b4ac6f4591bcf2cefe07b100bb55bc24137c6d",
    "srt/rust_extensions/torch_build.py": "36fce352fe9b3aa1b699f50f0a2ed09fa0d8a612d061384e7e177faf92b4126e",
}
_RUST_PINS = {
    "Cargo.lock": "361d0a6948c2a3c178fc6b07eb9a2321a44b21d41fc14929e672a0bd1ae9e4da",
    "Cargo.toml": "3b69d62195db3c1e1d9c0da0e4c355f444e68cebfb11354dde9ca6f0b9ddb2f3",
    "src/cache_action.rs": "ec60c4daa878d3ee345b14a4ba13e18e41d6ce1a73e1def5b2d2266dda37c5c4",
    "src/components/full.rs": "fc7f8302390743626d94f4756f68ecba4340a5a53aaafb5d1cb7a6f496125510",
    "src/components/mamba.rs": "e49a2e4d654427a72ce667e8cf3015862673e1306d8f4908a8e006d13232634d",
    "src/components/mod.rs": "c6f7a9126fd54613c94ac898be3a7891e5110a6d4f05cd3089f5327adaec8fdc",
    "src/components/swa.rs": "5f209168ae589c449ea47484112823095a93773e262f1fa8b9f324238bd4e52f",
    "src/lib.rs": "2a607d116c44d1ed045b70bd675b537c94724275c9eec386b68daafbae4ddd0a",
    "src/node.rs": "826ef0bed6c15a53e67fff3b7dd0797dc945de73fb97d2af6df3588507ce111f",
    "src/python_bindings/cache_action.rs": "28bf650a12426df6c20a75f9f6b5bb58564be80cb16d92bcaca99e6292c33fac",
    "src/python_bindings.rs": "d6f55c307b99195902f6e2c24f8c013b6a1aace0edd51982fedac17bb67adf61",
    "src/tests/components/base.rs": "061f6eede709b2b97280681dff4264c9a84e436761c3711d273cc72b69649ab6",
    "src/tests/components/full.rs": "1416c7c35c77aa912a6639542bb658ba983dac757a50bc006aecbdc26b542199",
    "src/tests/components/mamba.rs": "69c83d0c712003bef3275ed82cf0250349722025dbeaa36025fe5d2a6ca9d422",
    "src/tests/components/swa.rs": "837c98eeb431d127431347bccd58e3d177d20817fd53eca95ad37ec233a0df92",
    "src/tests/node.rs": "e8d37e7eb647ab9b49f98c4eed4157640560252557a360871323f49ffe58f360",
    "src/tests/test_utils.rs": "ca576b74d1aca874a3a6f3705b808a97610cd978798f20187ad3d15965d543eb",
    "src/tests/unified_lru_list.rs": "500d68b6ce132461ac254ff2e4af8d76c336bab2d4de3ea962b9cfaa3172dde6",
    "src/tests/unified_tree_core.rs": "4a189155528655c017674e59f7bfd057c898514efa382990aa44dba376f578d7",
    "src/unified_lru_list.rs": "c8f1e4a22fbe9683caac3f5ebb45d6a9bc42a9f165b535a0584cc483a106ee5b",
    "src/unified_tree_core.rs": "e0af738c0fadcaa5a471e17d1d618a2f4aa0a20e336751b6da3b534111a837c6",
    "torch_compat.h": "f619ac5d2a4b279a1808d6588118872de0800c954a8e0a97888460bd80cfdc71",
}

_BRIDGE = '''/// Invocation-owned diagnostic bridge. Errors never become cache decisions.
fn old_full_observer(
    py: Python<'_>,
    context: Option<&Py<PyAny>>,
) -> PyResult<Option<OldFullObserver>> {
    let Some(context) = context else { return Ok(None) };
    let (capture, rid, start, end): (Py<PyAny>, String, usize, usize) =
        context.bind(py).extract()?;
    let invalidate = capture.bind(py).getattr("invalidate")?.unbind();
    if !capture.bind(py).is_callable() || !invalidate.bind(py).is_callable() || start >= end {
        return Err(PyValueError::new_err("invalid old_full_observer context"));
    }
    Ok(Some(Arc::new(move |node_id, cursor, prefix_len, original| {
        // Filter before Python attachment and before creating a Tensor owner.
        if cursor >= end || cursor + prefix_len <= start { return; }
        Python::attach(|py| {
            let indices = match original {
                Some(tensor) => tensor_to_py(py, tensor.shallow_clone()),
                None => Ok(py.None()),
            };
            let (stage, result) = match indices {
                Ok(indices) => ("capture", capture.bind(py).call1(
                    (&rid, start, end, node_id, cursor, prefix_len, indices)
                ).map(|_| ())),
                Err(error) => ("tensor_wrap", Err(error)),
            };
            if let Err(error) = result {
                let message = error.to_string();
                if let Err(invalidation_error) = invalidate.bind(py).call1(
                    (&rid, start, end, stage, &message)
                ) {
                    // Both errors remain observable in the retained process stderr.
                    eprintln!("{invalidation_error_marker} rid={} P={} E={} stage={}", rid, start, end, stage);
                    error.write_unraisable(py, Some(capture.bind(py)));
                    invalidation_error.write_unraisable(py, Some(invalidate.bind(py)));
                }
            }
        });
    })))
}

'''.replace("{invalidation_error_marker}", INVALIDATION_ERROR_MARKER)

_NATIVE_TESTS = '''
#[test]
fn old_full_observer_precedes_partial_split_and_borrows_original_storage() {
    use std::sync::atomic::{AtomicUsize, Ordering};
    let mut tc = core();
    let key = vec![1, 2, 3, 4];
    tc.insert(&insert_params(&key, &[10, 11, 12, 13]));
    let id = tc.match_prefix(&match_params(&key)).last_device_node_id;
    let original = tc.get_component_device_value(id, FULL).unwrap().unwrap().shallow_clone();
    let pointer = original.data_ptr() as usize;
    let seen = Arc::new(AtomicUsize::new(0));
    let observed = Arc::clone(&seen);
    let partial = vec![1, 2, 8];
    let mut params = insert_params(&partial, &[20, 21, 28]);
    params.old_full_observer = Some(Arc::new(move |node_id, cursor, prefix_len, value| {
        let value = value.expect("FULL present before split");
        assert_eq!((node_id, cursor, prefix_len), (id, 0, 2));
        assert_eq!(value.size(), vec![4]);
        assert_eq!(value.data_ptr() as usize, pointer);
        observed.fetch_add(1, Ordering::SeqCst);
    }));
    let result = tc.insert(&params);
    assert_eq!(result.prefix_len, 2);
    assert_eq!(seen.load(Ordering::SeqCst), 1);
    assert!(original.equal(&Tensor::from_slice(&[10i64, 11, 12, 13])));
    tc.sanity_check(&[], &[]);
}

#[test]
fn old_full_observer_sees_none_before_fresh_restoration() {
    use std::sync::atomic::{AtomicUsize, Ordering};
    let mut tc = core();
    let root = tc.arena.root();
    let node = add_leaf(&mut tc, root, vec![1, 2, 3]);
    let _ = tc.arena.take_device_value(node, FULL);
    tc.dec_evictable_size(FULL, 3);
    let seen = Arc::new(AtomicUsize::new(0));
    let observed = Arc::clone(&seen);
    let key = vec![1, 2, 3];
    let mut params = insert_params(&key, &[20, 21, 22]);
    params.old_full_observer = Some(Arc::new(move |_, cursor, prefix_len, value| {
        assert_eq!((cursor, prefix_len), (0, 3));
        assert!(value.is_none());
        observed.fetch_add(1, Ordering::SeqCst);
    }));
    tc.insert(&params);
    assert_eq!(seen.load(Ordering::SeqCst), 1);
    assert!(tc.arena.device_value(node, FULL).equal(&Tensor::from_slice(&[20i64, 21, 22])));
}
'''


def _sha(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _replace(text: str, before: str, after: str, *, count: int = 1) -> str:
    if text.count(before) != count:
        raise ValueError(f"Pinned Rust observer seam differs: {before!r}")
    return text.replace(before, after)


def _rust_candidate(relative: str, content: bytes) -> bytes:
    if _sha(content) != _RUST_PINS[relative]:
        raise ValueError(f"Rust source identity differs: {relative}")
    text = content.decode()
    if relative == "src/unified_tree_core.rs":
        text = _replace(text, "/// Params for an insert; the key is borrowed from the caller.\n",
                        "/// Inline observer of original FULL storage; never returns a cache decision.\n"
                        "pub type OldFullObserver = Arc<dyn Fn(NodeId, usize, usize, Option<&Tensor>) + Send + Sync>;\n\n"
                        "/// Params for an insert; the key is borrowed from the caller.\n")
        text = _replace(text, "    pub track_adopted_ranges: bool,\n", "    pub track_adopted_ranges: bool,\n    pub old_full_observer: Option<OldFullObserver>,\n")
        text = _replace(text, "    track_adopted_ranges: bool,\n", "    track_adopted_ranges: bool,\n    old_full_observer: Option<OldFullObserver>,\n")
        text = _replace(text, "            track_adopted_ranges: params.track_adopted_ranges,\n", "            track_adopted_ranges: params.track_adopted_ranges,\n            old_full_observer: params.old_full_observer.clone(),\n")
        text = _replace(text, "            track_adopted_ranges: state.track_adopted_ranges,\n", "            track_adopted_ranges: state.track_adopted_ranges,\n            old_full_observer: None,\n", count=3)
        seam = "        let prefix_len = state.key.match_len(cursor, &node.key, self.page_size);\n"
        text = _replace(text, seam, seam + "        if let Some(observer) = &state.old_full_observer {\n            observer(node.id, cursor, prefix_len, node.try_device_value(FULL));\n        }\n")
    elif relative == "src/python_bindings.rs":
        text = _replace(text, "use std::sync::Mutex;", "use std::sync::{Arc, Mutex};")
        text = _replace(text, "    InsertResult, InsertStepResult, MatchPrefixParams, MatchResult, PoolHitPolicy, PoolName,", "    InsertResult, InsertStepResult, MatchPrefixParams, MatchResult, OldFullObserver, PoolHitPolicy, PoolName,")
        text = _replace(text, "/// Convert a Python int64 sequence to an owned `Vec<i64>`.\n", _BRIDGE + "/// Convert a Python int64 sequence to an owned `Vec<i64>`.\n")
        text = _replace(text, "    pub track_adopted_ranges: bool,\n", "    pub track_adopted_ranges: bool,\n    pub old_full_observer: Option<Py<PyAny>>,\n")
        text = _replace(text, "track_adopted_ranges = false, rotation_base = None))]", "track_adopted_ranges = false, rotation_base = None, old_full_observer = None))]")
        text = _replace(text, "        rotation_base: Option<i64>,\n    ) -> PyResult<Self> {", "        rotation_base: Option<i64>,\n        old_full_observer: Option<Py<PyAny>>,\n    ) -> PyResult<Self> {")
        text = _replace(text, "            track_adopted_ranges,\n", "            track_adopted_ranges,\n            old_full_observer,\n")
        text = _replace(text, "                    track_adopted_ranges: params.track_adopted_ranges,\n", "                    track_adopted_ranges: params.track_adopted_ranges,\n                    old_full_observer: old_full_observer(py, params.old_full_observer.as_ref())?,\n", count=2)
    elif relative.startswith("src/tests/") and "track_adopted_ranges: false," in text:
        text = re.sub(r"(?m)^(\s*)track_adopted_ranges: false,$", r"\1track_adopted_ranges: false,\n\1old_full_observer: None,", text)
        if relative == "src/tests/unified_tree_core.rs":
            text += _NATIVE_TESTS
    return text.encode()


def _adapter_candidate(content: bytes) -> bytes:
    if _sha(content) != _PYTHON_PINS[_ADAPTER]:
        raise ValueError("Rust adapter source identity differs")
    seam = "                rotation_base=params.rotation_base,\n"
    text = _replace(content.decode(), seam, seam + "                old_full_observer=getattr(params, \"old_full_observer\", None),\n")
    compile(text, _ADAPTER, "exec")
    return text.encode()


def _qualified_files(root: Path, pins: dict[str, str]) -> dict[str, bytes]:
    files = {relative: (root / relative).read_bytes() for relative in pins}
    for relative, content in files.items():
        if _sha(content) != pins[relative]:
            raise ValueError(f"Pinned source identity differs: {root / relative}")
    return files


def _identities(files: dict[str, bytes]) -> dict:
    return {relative: {"bytes": len(content), "sha256": _sha(content)} for relative, content in files.items()}


def _write_new(path: Path, content: bytes) -> None:
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError(f"Existing observer artifact differs: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def _json_new(path: Path, content: dict) -> None:
    _write_new(path, (json.dumps(content, indent=2, allow_nan=False) + "\n").encode())


def _diff(before: dict[str, bytes], after: dict[str, bytes]) -> bytes:
    return "".join(line for relative in before if before[relative] != after[relative]
                   for line in difflib.unified_diff(before[relative].decode().splitlines(keepends=True),
                                                   after[relative].decode().splitlines(keepends=True),
                                                   fromfile=f"a/{relative}", tofile=f"b/{relative}")).encode()


def _binary(root: Path) -> Path:
    binaries = list((root / "srt/mem_cache/rust_tree_core").glob("mem_cache*.so"))
    binaries = [p for p in binaries if "inspection" not in p.name]
    if len(binaries) != 1:
        raise ValueError(f"Expected exactly one production mem_cache binary: {binaries}")
    return binaries[0].resolve()


def _run(archive: Path, name: str, args: list[str]) -> dict:
    script = Path(__file__).with_name("probe_rust_kv_observer.py")
    command = [sys.executable, "-B", str(script), *args]
    env = {**os.environ, "CUDA_VISIBLE_DEVICES": "", "PYTHONDONTWRITEBYTECODE": "1"}
    # Existing registry cache is read-only/offline; no dependency installation.
    env["CARGO_NET_OFFLINE"] = "true"
    with (archive / f"{name}.stdout").open("xb") as stdout, (archive / f"{name}.stderr").open("xb") as stderr:
        result = subprocess.run(command, stdout=stdout, stderr=stderr, env=env, check=False)
    _json_new(archive / f"{name}-command.json", {"command": command, "returncode": result.returncode})
    if result.returncode:
        raise RuntimeError(f"CPU observer {name} failed ({result.returncode}); see {archive / (name + '.stderr')}")
    return json.loads((archive / f"{name}.json").read_text())


def build_source(root: Path, *, image: str, archive_dir: Path) -> dict:
    """Retain/build/qualify baseline and observer without changing ``root``.

    Run only in the pinned GPU0 image. All compiler and native-module execution
    happens in isolated child processes, through the production loader API.
    """
    root, archive = root.resolve(), archive_dir.resolve()
    if image != IMAGE:
        raise ValueError("Rust observer requires the pinned image")
    crate = root.parents[1] / "rust/sglang-radix-tree"
    before = _qualified_files(crate, _RUST_PINS)
    python = _qualified_files(root, _PYTHON_PINS)
    bundled = _binary(root)
    if _sha(bundled.read_bytes()) != ORIGINAL_BINARY_SHA256:
        raise ValueError("Original production binary identity differs")
    after = {relative: _rust_candidate(relative, content) for relative, content in before.items()}
    adapter = _adapter_candidate(python[_ADAPTER])
    if archive.exists():
        raise ValueError("CPU build archive must be new; preserve failed attempts separately")
    archive.mkdir(parents=True)
    manifest = {"task_id": TASK_ID, "image": image, "module": MODULE, "features": ["python-extension"],
                "before": _identities(before), "after": _identities(after),
                "adapter_before_sha256": _sha(python[_ADAPTER]), "adapter_after_sha256": _sha(adapter),
                "binary_source_commit": "UNVERIFIED"}
    _json_new(archive / "source-manifest.json", manifest)
    _write_new(archive / "observer.patch", _diff(before, after))
    _write_new(archive / "adapter.patch", _diff({_ADAPTER: python[_ADAPTER]}, {_ADAPTER: adapter}))
    receipt = {"task_id": TASK_ID, "image": image, "module": MODULE, "features": ["python-extension"],
               "status": "PENDING", "source_manifest": manifest,
               "original": {"package_root": str(root), "path": str(bundled), "sha256": ORIGINAL_BINARY_SHA256,
                            "binary_source_commit": "UNVERIFIED"}}
    _json_new(archive / "observer-build-pending.json", receipt)
    for variant, files in (("baseline", before), ("observer", after)):
        workspace = archive / "sources" / variant
        for relative, content in files.items():
            _write_new(workspace / relative, content)
        receipt[variant] = _run(archive, f"build-{variant}", ["_build", "--root", str(root),
                                "--workspace", str(workspace), "--archive-dir", str(archive), "--variant", variant])
    _run(archive, "qualification", ["qualify", "--archive-dir", str(archive), "--root", str(root)])
    return finalize_build(root, image=image, archive_dir=archive, qualification_dir=archive)


def _verify_compiled_build(built: dict, variant: str) -> None:
    environment = built["environment"]
    if (built.get("module") != MODULE or built.get("features") != ["python-extension"]
            or built.get("module_runtime_name") != MODULE or built.get("loader_mode") != "force"
            or not built.get("rustc", "").startswith("rustc 1.99.1 ")
            or (environment.get("python"), environment.get("torch"), environment.get("cxx11_abi"),
                environment.get("cuda_initialized")) != ("3.12.16", "2.14.1+cu130", True, False)):
        raise ValueError(f"Compiled observer ABI/build environment differs: {variant}")


def _verify_qualification(qualification: dict) -> None:
    if (qualification.get("status") != "PASS"
            or qualification.get("variants") != ["original", "rebuilt", "observer-none", "observer-enabled"]
            or qualification.get("cases") != ["ordinary", "partial_split", "missing_full", "end_abort", "mamba_barrier"]
            or qualification.get("exact_actions_results_topology_indices") is not True
            or qualification.get("native_fixtures", {}).get("status") != "PASS"
            or qualification.get("dependency_files") != 6
            or qualification.get("invalidation_failure_marker") != INVALIDATION_ERROR_MARKER
            or qualification.get("invalidation_failure_marker_verified") is not True):
        raise ValueError("Native qualification receipt does not cover the required production scenarios")


def _receipt_identity(path: Path) -> dict:
    content = path.read_bytes()
    return {"path": str(path.resolve()), "sha256": _sha(content), "bytes": len(content)}


def _retained_build(root: Path, *, image: str, archive_dir: Path) -> dict:
    """Verify completed source/libraries independently of prior qualifications."""
    root, archive = root.resolve(), archive_dir.resolve()
    if image != IMAGE:
        raise ValueError("A pinned CPU build image is required")
    pending = archive / "observer-build-pending.json"
    receipt = json.loads(pending.read_text())
    if (receipt.get("status") != "PENDING" or receipt.get("task_id") != TASK_ID
            or receipt.get("image") != IMAGE or receipt.get("module") != MODULE
            or receipt.get("features") != ["python-extension"]
            or Path(receipt["original"]["package_root"]).resolve() != root):
        raise ValueError("Retained build header/original package root differs")
    before = _qualified_files(root.parents[1] / "rust/sglang-radix-tree", _RUST_PINS)
    after = {relative: _rust_candidate(relative, content) for relative, content in before.items()}
    python = _qualified_files(root, _PYTHON_PINS)
    manifest = json.loads((archive / "source-manifest.json").read_text())
    if (manifest != receipt["source_manifest"] or manifest["before"] != _identities(before)
            or manifest["after"] != _identities(after) or manifest["image"] != IMAGE
            or manifest["module"] != MODULE or manifest["features"] != ["python-extension"]
            or manifest["adapter_before_sha256"] != _sha(python[_ADAPTER])
            or manifest["adapter_after_sha256"] != _sha(_adapter_candidate(python[_ADAPTER]))):
        raise ValueError("Retained compiled source composition differs")
    original = _binary(root)
    if (original != Path(receipt["original"]["path"]).resolve()
            or receipt["original"]["sha256"] != ORIGINAL_BINARY_SHA256
            or _sha(original.read_bytes()) != ORIGINAL_BINARY_SHA256):
        raise ValueError("Original bundled production binary changed")
    identities = {"pending": _receipt_identity(pending), "source_manifest": _receipt_identity(archive / "source-manifest.json")}
    for variant, files in (("baseline", before), ("observer", after)):
        workspace = archive / "sources" / variant
        _qualified_files(workspace, {relative: _sha(content) for relative, content in files.items()})
        path = archive / f"build-{variant}.json"
        built = json.loads(path.read_text())
        _verify_compiled_build(built, variant)
        library = Path(built["path"]).resolve()
        content = library.read_bytes()
        command = json.loads((archive / f"build-{variant}-command.json").read_text())
        if (Path(built["workspace"]).resolve() != workspace
                or not library.is_relative_to((archive / "libraries" / variant).resolve())
                or not content.startswith(b"\x7fELF") or _sha(content) != built["sha256"]
                or command["returncode"] != 0):
            raise ValueError(f"Retained actual compiled library/build evidence differs: {variant}")
        receipt[variant] = built
        identities[variant] = _receipt_identity(path)
    receipt["input_receipts"] = identities
    return receipt


def finalize_build(root: Path, *, image: str, archive_dir: Path, qualification_dir: Path) -> dict:
    """Finalize beside this qualification, preserving all earlier receipts."""
    archive, qualification_dir = archive_dir.resolve(), qualification_dir.resolve()
    receipt = _retained_build(root, image=image, archive_dir=archive)
    path = qualification_dir / "qualification.json"
    qualification = json.loads(path.read_text())
    _verify_qualification(qualification)
    command = json.loads((qualification_dir / "qualification-command.json").read_text())
    if command["returncode"] != 0:
        raise ValueError("Actual qualification command did not succeed")
    libraries = {"original": receipt["original"], "rebuilt": receipt["baseline"],
                 "observer-none": receipt["observer"], "observer-enabled": receipt["observer"]}
    for variant, library in libraries.items():
        output = json.loads((qualification_dir / f"qualify-{variant}.json").read_text())
        if (output["status"] != "PASS" or output["production_module"] != MODULE
                or Path(output["library_path"]).resolve() != Path(library["path"]).resolve()
                or output["library_sha256"] != library["sha256"]):
            raise ValueError(f"Actual native qualification/library binding differs: {variant}")
    receipt.update(status="PASS", qualification=qualification,
                   qualification_receipt=_receipt_identity(path))
    _json_new(qualification_dir / "observer-build.json", receipt)
    return receipt


def resume_source(root: Path, *, image: str, archive_dir: Path, output_dir: Path) -> dict:
    """Resume only a completed-build, failed-qualification CPU attempt once."""
    archive, output = archive_dir.resolve(), output_dir.resolve()
    receipt = _retained_build(root, image=image, archive_dir=archive)
    failure = json.loads((archive / "qualification-command.json").read_text())
    if failure["returncode"] == 0:
        raise ValueError("Resume requires a retained failed qualification command")
    if output.exists() or output == archive or output.is_relative_to(archive):
        raise ValueError("Resume output must be a separate new qualification directory")
    output.mkdir(parents=True)
    _json_new(output / "resume-inputs.json", {"task_id": TASK_ID, "image": IMAGE,
              "input_receipts": receipt["input_receipts"], "failed_qualification": _receipt_identity(archive / "qualification-command.json"),
              "libraries": {variant: {key: receipt[variant][key] for key in ("path", "sha256")}
                            for variant in ("baseline", "observer")},
              "fixture_source": _receipt_identity(Path(__file__).with_name("probe_rust_kv_observer.py"))})
    _run(output, "qualification", ["qualify", "--root", str(root.resolve()), "--archive-dir", str(archive), "--output", str(output)])
    return finalize_build(root, image=image, archive_dir=archive, qualification_dir=output)


def _composed_sources(root: Path) -> dict:
    # The existing WIT owner alone knows FP32/metadata/FFI composition. Require
    # its exact completed output; reverse only through that owner's guards.
    from tests.manual.agent_opd import sglang_kv_streams as streams

    manifest = streams.source_manifest()
    ffi = importlib.metadata.distribution("apache-tvm-ffi")
    paths = {relative: Path(ffi.locate_file(relative)).resolve() if relative.startswith("tvm_ffi/")
             else root / relative for relative in manifest["files"]}
    current, _, candidate = streams._sources(paths, manifest)
    if current != candidate:
        raise ValueError("Rust observer requires completed selected-FP32 -> CPU metadata -> KV WIT source")
    return _identities(current)


def prepare_source(root: Path, *, image: str, archive_dir: Path, build_receipt: Path) -> dict:
    """Stage the qualified same-name binary and adapter in a private overlay.

    Every source, composition, build-receipt and actual library prerequisite is
    checked before any write. The caller preserves this returned receipt as-is.
    """
    root, archive = root.resolve(), archive_dir.resolve()
    receipt_bytes = build_receipt.read_bytes()
    receipt = json.loads(receipt_bytes)
    if image != IMAGE or receipt.get("image") != IMAGE or receipt.get("status") != "PASS":
        raise ValueError("A passing pinned CPU observer build receipt is required")
    if receipt.get("module") != MODULE or receipt.get("features") != ["python-extension"]:
        raise ValueError("Only the same production module/features are supported")
    if receipt.get("qualification", {}).get("status") != "PASS":
        raise ValueError("Production-native CPU qualification is required")
    if observer_module := sys.modules.get(MODULE):
        raise ValueError(f"Cannot stage after native import: {observer_module}")
    if root == Path(receipt["original"]["package_root"]).resolve():
        raise ValueError("Cannot stage into the shared baseline; provide a private diagnostic package copy")
    if "source" in root.parts and any(part.startswith("native-") for part in root.parts):
        raise ValueError("Retained raw source archives are read-only")
    if sys.version_info[:3] != (3, 12, 16):
        raise ValueError("Prepared native observer requires Python 3.12.16")
    if importlib.metadata.version("torch") != "2.14.1+cu130":
        raise ValueError("Prepared native observer requires Torch 2.14.1+cu130")
    for package, expected in (("sglang", "0.5.24.dev80+g056f871"), ("apache-tvm-ffi", "0.1.11")):
        if importlib.metadata.version(package) != expected:
            raise ValueError(f"Prepared native observer dependency differs: {package}")
    composition = _composed_sources(root)
    before = _qualified_files(root, _PYTHON_PINS)
    adapter = _adapter_candidate(before[_ADAPTER])
    _verify_qualification(receipt["qualification"])
    for variant in ("baseline", "observer"):
        _verify_compiled_build(receipt[variant], variant)
    artifact = Path(receipt["observer"]["path"]).resolve()
    content = artifact.read_bytes()
    if not content.startswith(b"\x7fELF") or _sha(content) != receipt["observer"]["sha256"]:
        raise ValueError("Compiled observer binary identity differs")
    manifest = receipt["source_manifest"]
    original_crate = Path(receipt["original"]["package_root"]).parents[1] / "rust/sglang-radix-tree"
    expected_before = _qualified_files(original_crate, _RUST_PINS)
    expected_after = {relative: _rust_candidate(relative, content) for relative, content in expected_before.items()}
    if (manifest["before"] != _identities(expected_before) or manifest["after"] != _identities(expected_after)
            or manifest["adapter_after_sha256"] != _sha(adapter)
            or manifest["features"] != ["python-extension"] or manifest["module"] != MODULE):
        raise ValueError("Compiled source composition differs from this observer implementation")
    target = _binary(root)
    if _sha(target.read_bytes()) != ORIGINAL_BINARY_SHA256:
        raise ValueError("Private package does not contain the original pinned binary")
    if artifact == target:
        raise ValueError("Build artifact must remain separate from the staged copy")
    result = {"task_id": TASK_ID, "image": image, "module": MODULE, "features": ["python-extension"],
              "diagnostic_only": True, "package_root": str(root), "compiled_sha256": _sha(content),
              "binary_target": str(target),
              "build_receipt": str(build_receipt.resolve()), "build_receipt_sha256": _sha(receipt_bytes),
              "original_binary_source_commit": "UNVERIFIED", "native_cpu_qualification": "PASS",
              "invalidation_failure_marker": INVALIDATION_ERROR_MARKER,
              "cuda_thread_stream_payload_qualification": "PENDING", "composition": composition,
              "adapter_before_sha256": _sha(before[_ADAPTER]), "adapter_after_sha256": _sha(adapter),
              "changed_files": [_ADAPTER, str(target.relative_to(root))]}
    _json_new(archive / "preflight.json", result)
    _write_new(archive / "adapter.patch", _diff({_ADAPTER: before[_ADAPTER]}, {_ADAPTER: adapter}))
    (root / _ADAPTER).write_bytes(adapter)
    shutil.copyfile(artifact, target)
    if _sha(target.read_bytes()) != result["compiled_sha256"]:
        raise RuntimeError("Staged production binary differs after copy")
    return result
