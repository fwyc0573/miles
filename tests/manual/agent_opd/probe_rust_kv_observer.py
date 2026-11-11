"""GPU0 production-native observer build and CPU semantic qualification.

Example (inside the pinned production image, never on the host):
    python3 -B tests/manual/agent_opd/probe_rust_kv_observer.py build \
        --root /sgl-workspace/sglang/python/sglang --image IMAGE \
        --archive-dir PRIVATE_ARCHIVE

The existing SGLang loader is the sole builder. Each library/observer variant
loads in its own fresh process; no inspection module or Python walker is used.
For completed builds whose qualification failed, `resume` reuses retained
libraries and sources; --output names a separate new qualification directory.
"""

from __future__ import annotations

import argparse
import ast
import gc
import importlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import threading
import time
import weakref
from array import array
from pathlib import Path


# Direct script invocation does not otherwise expose the repository's tests.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tests.manual.agent_opd import sglang_rust_kv_observer as observer


_CASES = ("ordinary", "partial_split", "missing_full", "end_abort", "mamba_barrier")
_CPU_VARIANT_TIMEOUT_SECONDS = 60
_RESULT_FIELDS = ("rotation_tail_declined", "prefix_len", "total_len", "last_device_node",
                  "inserted_host_node", "host_insert_dropped", "mamba_exist", "swa_branch_inserted",
                  "adopted_ranges", "cache_actions")
_MATCH_FIELDS = ("device_prefix_len", "last_device_node_id", "last_host_node_id", "best_match_node_id",
                 "last_visited_node_id", "full_device_match_len", "host_hit_length", "swa_host_hit_length",
                 "swa_branching_seqlen", "mamba_host_hit_length",
                 "mamba_branching_seqlen", "full_kv_hit_length", "cache_actions")


def _environment(torch) -> dict:
    result = {"python": platform.python_version(), "executable": sys.executable,
              "torch": str(torch.__version__), "cxx11_abi": torch.compiled_with_cxx11_abi(),
              "cuda_initialized": torch.cuda.is_initialized(), "pid": os.getpid()}
    if (result["python"], result["torch"], result["cxx11_abi"], result["cuda_initialized"]) != (
            "3.12.16", "2.14.1+cu130", True, False):
        raise RuntimeError(f"Pinned CPU runtime prerequisites differ: {result}")
    return result


def _build(args) -> None:
    if observer.MODULE in sys.modules:
        raise RuntimeError("Production native module imported before explicit build")
    import torch
    import sglang
    from sglang.srt.rust_extensions.loader import load_rust_extension
    from sglang.srt.rust_extensions.torch_build import torch_build_configuration

    environment = _environment(torch)
    if Path(sglang.__file__).resolve().parent != args.root.resolve():
        raise RuntimeError("Imported SGLang package differs from the verified build root")
    build = torch_build_configuration(compat_header=args.workspace / "torch_compat.h",
                                     python_module=observer.MODULE, torch_module=torch)
    compiler = subprocess.run(["rustc", "--version"], check=True, capture_output=True, text=True).stdout.strip()
    if not compiler.startswith("rustc 1.99.1 "):
        raise RuntimeError(f"Installed rustc identity differs: {compiler}")
    with tempfile.TemporaryDirectory(prefix="rust-kv-build-", dir=os.environ["TMPDIR"]) as temporary:
        cache = Path(temporary) / "loader-cache"
        module = load_rust_extension(observer.MODULE, mode="force", cache_dir=cache,
                                     workspace=args.workspace, build_environment=build.environment,
                                     build_fingerprint=build.fingerprint)
        if module.__spec__.name != observer.MODULE:
            raise RuntimeError("Production loader module specification differs")
        environment = _environment(torch)
        path = Path(module.__file__).resolve()
        if not path.is_relative_to(cache.resolve()):
            raise RuntimeError("Production loader selected a non-isolated artifact")
        destination = args.archive_dir / "libraries" / args.variant / path.name
        observer._write_new(destination, path.read_bytes())
    result = {"path": str(destination.resolve()), "sha256": observer._sha(destination.read_bytes()),
              "module": module.__spec__.name, "module_runtime_name": module.__name__,
              "features": ["python-extension"], "loader_mode": "force",
              "loader_artifact": str(path), "loader_cache": str(cache), "loader_cache_retained": False,
              "workspace": str(args.workspace.resolve()),
              "environment": environment, "build_fingerprint": build.fingerprint,
              "build_environment": {key: build.environment.get(key) for key in (
                  "LIBTORCH", "LIBTORCH_CXX11_ABI", "LIBTORCH_BYPASS_VERSION_CHECK", "PYO3_PYTHON",
                  "CXXFLAGS", "RUSTFLAGS", "CARGO_NET_OFFLINE")}, "rustc": compiler}
    observer._json_new(args.archive_dir / f"build-{args.variant}.json", result)


def _dependency_sources(archive: Path) -> dict:
    registry = Path(os.environ.get("CARGO_HOME", str(Path.home() / ".cargo"))) / "registry/src"
    selections = {
        "tch-0.24.0": ("src/wrappers/tensor.rs", "src/wrappers/python.rs"),
        "torch-sys-0.24.0": ("libtch/torch_api.cpp", "libtch/torch_python.cpp"),
        "pyo3-0.29.2": ("src/marker.rs", "src/internal/state.rs"),
    }
    patterns = ("shallow_clone", "at_shallow_clone", "pyobject_wrap", "pyobject_unpack",
                "THPVariable_Wrap", "THPVariable_Unpack", "attach", "detach", "SuspendGIL")
    result = {}
    for package, relatives in selections.items():
        candidates = sorted(registry.glob(f"*/{package}"))
        if len(candidates) != 1:
            raise RuntimeError(f"Expected one installed locked Cargo source for {package}: {candidates}")
        for relative in relatives:
            source = candidates[0] / relative
            content = source.read_bytes()
            lines = content.decode().splitlines()
            hits = [(index, line) for index, line in enumerate(lines) if any(p in line for p in patterns)]
            if not hits:
                raise RuntimeError(f"No decisive bridge/attachment source in {source}")
            intervals = sorted({i for index, _ in hits for i in range(max(0, index - 5), min(len(lines), index + 24))})
            key = f"{package}/{relative}"
            observer._write_new(archive / "dependencies" / key, content)
            result[key] = {"source": str(source), "bytes": len(content), "sha256": observer._sha(content),
                           "decisive_lines": [[i + 1, lines[i]] for i in intervals]}
    observer._json_new(archive / "dependency-source-manifest.json", result)
    return result


def _source_topology(root: Path, archive: Path, *, source_archive: Path | None = None) -> dict:
    scheduler = root / "srt/managers/scheduler.py"
    content = scheduler.read_bytes()
    if observer._sha(content) != "54bbde812b4af9e01a00b62e12e95015fdb1c325b9e153706616ba59ea52b2a6":
        raise RuntimeError("Scheduler call-topology source identity differs")
    tree = ast.parse(content)
    selected = {node.name: ast.get_source_segment(content.decode(), node) for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and node.name in (
                    "dispatch_event_loop", "_dispatch_event_loop_once", "event_loop_normal", "event_loop_overlap")}
    assert set(selected) == {"dispatch_event_loop", "_dispatch_event_loop_once", "event_loop_normal", "event_loop_overlap"}
    assert "self.process_batch_result(batch, result)" in selected["event_loop_normal"]
    assert "pop_and_process()" in selected["event_loop_overlap"]
    assert not any("Thread(" in source or "threading." in source for source in selected.values())
    source_archive = archive if source_archive is None else source_archive
    native = (source_archive / "sources/baseline/src/python_bindings.rs").read_text()
    start = native.index("macro_rules! tree_core_methods")
    stop = native.index("macro_rules!", start + len("macro_rules!"))
    body = native[start:stop]
    starts = list(re.finditer(r"\n\s+fn (\w+)\(", body))
    calls = []
    for index, match in enumerate(starts):
        function = body[match.start():starts[index + 1].start() if index + 1 < len(starts) else len(body)]
        if "self.core()" in function:
            assert ".detach" in function, f"Core method takes native Mutex while attached: {match.group(1)}"
            calls.append(match.group(1))
    assert len(calls) == 130
    result = {"scheduler_sha256": observer._sha(content), "scheduler_functions": selected,
              "binding_sha256": observer._sha(native.encode()), "core_call_methods_with_detach": calls,
              "count": len(calls), "scope": "Source call topology; runtime CUDA S thread remains pending"}
    observer._json_new(archive / "source-topology.json", result)
    return result


def _load(path: Path | None):
    import torch
    from sglang.srt.rust_extensions.loader import load_rust_extension

    _environment(torch)
    if observer.MODULE in sys.modules:
        raise RuntimeError("Variant already imported before qualification")
    if path is None:
        module = load_rust_extension(observer.MODULE, mode="never")
        if observer._sha(Path(module.__file__).read_bytes()) != observer.ORIGINAL_BINARY_SHA256:
            raise RuntimeError("Original bundled production binary identity differs")
    else:
        # Select the retained probe copy as a bundled production module through
        # the public loader's unchanged never mode. No global path is edited.
        package = importlib.import_module("sglang.srt.mem_cache.rust_tree_core")
        package.__path__ = [str(path.resolve().parent)]
        module = load_rust_extension(observer.MODULE, mode="never")
        if Path(module.__file__).resolve() != path.resolve():
            raise RuntimeError("Production never-mode import did not select the probe copy")
    return torch, module


def _serialize(value, torch):
    if isinstance(value, torch.Tensor):
        assert value.device.type == "cpu", "CPU qualification cannot read CUDA content"
        return {"tensor": value.tolist(), "dtype": str(value.dtype), "shape": list(value.shape)}
    if isinstance(value, dict):
        return {str(k): _serialize(v, torch) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_serialize(v, torch) for v in value]
    return value


def _metadata(tensor) -> dict | None:
    if tensor is None:
        return None
    return {"data_ptr": tensor.data_ptr(), "storage_ptr": tensor.untyped_storage().data_ptr(),
            "shape": list(tensor.shape), "stride": list(tensor.stride()), "dtype": str(tensor.dtype),
            "device": str(tensor.device), "storage_offset": tensor.storage_offset()}


class _Capture:
    """CPU qualification only; never calls a tree method inside a callback."""

    def __init__(self, expected: dict, *, fail: bool = False, invalidate_fail: bool = False):
        self.expected = expected
        self.fail = fail
        self.invalidate_fail = invalidate_fail
        self.rows = []
        self.invalidations = []
        self.thread = threading.get_native_id()

    def __call__(self, rid, start, end, node_id, cursor, prefix_len, indices):
        assert threading.get_native_id() == self.thread
        assert (rid, start, end) == ("cpu-rid", 0, 32)
        assert _metadata(indices) == self.expected[node_id]
        row = {"node_id": node_id, "cursor": cursor, "prefix_len": prefix_len,
               "metadata": _metadata(indices), "thread": threading.get_native_id()}
        # CPU-only byte evidence, never a CUDA capture-time operation.
        row["indices"] = None if indices is None else indices.tolist()
        self.rows.append(row)
        if self.fail:
            raise ValueError("injected OLD capture failure")

    def invalidate(self, rid, start, end, stage, message):
        self.invalidations.append([rid, start, end, stage, message])
        if self.invalidate_fail:
            raise ValueError("injected invalidation failure")


def _params(module, torch, key, indices, *, capture=None, mamba=False, explicit_none=False):
    kwargs = {"key": array("q", key), "value": torch.tensor(indices, dtype=torch.int64), "track_adopted_ranges": True}
    if mamba:
        kwargs["mamba_value"] = torch.tensor([100 + len(key)], dtype=torch.int64)
    if capture is not None or explicit_none:
        kwargs["old_full_observer"] = None if capture is None else (capture, "cpu-rid", 0, 32)
    return module.InsertParamsBinding(**kwargs)


def _walk(core, params, torch, *, abort=False):
    steps = []
    step = core.begin_insert(params)
    while True:
        steps.append({"actions": _serialize(step.actions, torch),
                      "result": None if step.result is None else _serialize(
                          {name: getattr(step.result, name) for name in _RESULT_FIELDS}, torch)})
        for action in step.actions:
            if action[0] == "mamba_evict_excess_path_states":
                evicted = core.evict_excess_path_states(action[1])
                steps[-1].setdefault("mamba_evictions", []).append(_serialize(
                    {field: getattr(evicted, field) for field in (
                        "tracker", "new_device_frees", "new_host_frees", "cache_actions")}, torch))
        if step.result is not None:
            break
        assert core.has_ongoing_insert()
        if abort:
            steps.append({"end_actions": _serialize(core.end_insert(), torch)})
            break
        step = core.resume_insert()
    assert not core.has_ongoing_insert()
    assert core.end_insert() == []
    return steps


def _snapshot(core, module, keys, torch, *, mamba=False):
    matches, ends = [], []
    for key in keys:
        match = core.match_prefix(module.MatchParamsBinding(array("q", key)))
        matches.append(_serialize({name: getattr(match, name) for name in _MATCH_FIELDS}, torch))
        ends.append(match.last_device_node_id)
    paths = core.collect_path_info(ends)
    nodes = sorted({row[0] for path in paths for row in path})
    values = {node: {component: _serialize(core.get_component_device_value(node, component), torch)
                     for component in ((0, 2) if mamba else (0,))} for node in nodes}
    return {"matches": matches, "paths": _serialize(paths, torch), "full_values": _serialize(values, torch)}


def _case(torch, module, name, enabled, explicit_none, *, fail=False, invalidate_fail=False):
    mamba = name == "mamba_barrier"
    hicache = name in ("end_abort", "missing_full")
    init = module.TreeCoreInitParamsBinding(device="cpu", page_size=1, enable_hicache=hicache,
                                           write_through_threshold=2 if hicache else 256,
                                           mamba_cache_chunk_size=1 if mamba else None,
                                           mamba_max_states_per_path=1 if mamba else None)
    core = module.RustUnifiedTreeCoreBinding(init, [0, 2] if mamba else [0])
    key = [1, 2, 3, 4] if name == "partial_split" else [1, 2, 3]
    seed = _walk(core, _params(module, torch, key, list(range(10, 10 + len(key))), mamba=mamba), torch)
    match = core.match_prefix(module.MatchParamsBinding(array("q", key)))
    node = match.last_device_node_id
    if name == "missing_full":
        core.commit_backup(node, torch.tensor([110, 111, 112], dtype=torch.int64), {})
        core.demote(node)
        assert core.get_component_device_value(node, 0) is None
    expected = {node: _metadata(core.get_component_device_value(node, 0))}
    capture = _Capture(expected, fail=fail, invalidate_fail=invalidate_fail) if enabled else None
    capture_ref = None if capture is None else weakref.ref(capture)
    inserted = [1, 2, 8] if name == "partial_split" else key + [5, 6]
    params = _params(module, torch, inserted, list(range(20, 20 + len(inserted))),
                     capture=capture, mamba=mamba, explicit_none=explicit_none)
    steps = _walk(core, params, torch, abort=name == "end_abort")
    if name == "partial_split" and enabled:
        assert len(capture.rows) == 1 and capture.rows[0]["prefix_len"] == 2
        assert capture.rows[0]["metadata"]["shape"] == [4]
    if name == "missing_full" and enabled:
        assert len(capture.rows) == 1 and capture.rows[0]["indices"] is None
    if enabled and not fail:
        assert capture.rows and not capture.invalidations, capture.invalidations
    if name == "mamba_barrier":
        assert len(steps) >= 2 and steps[0]["result"] is None
        assert any(action[0] == "mamba_evict_excess_path_states" for step in steps for action in step.get("actions", []))
    if name == "end_abort":
        assert steps[0]["result"] is None and "end_actions" in steps[-1]
        try:
            core.resume_insert()
        except RuntimeError as error:
            steps.append({"resume_after_abort_error": str(error)})
        else:
            raise AssertionError("Native resume accepted a missing walk")
        steps.extend(_walk(core, _params(module, torch, [9], [90]), torch))
    keys = [key, inserted] + ([[9]] if name == "end_abort" else [])
    snapshot = _snapshot(core, module, keys, torch, mamba=mamba)
    evidence = None if capture is None else {"rows": capture.rows, "invalidations": capture.invalidations}
    if fail:
        assert capture.invalidations and capture.invalidations[0][3] == "capture"
        assert "injected OLD capture failure" in capture.invalidations[0][4]
    del params, capture
    gc.collect()
    if capture_ref is not None:
        assert capture_ref() is None, "Native observer survives finish/end"
    return {"semantic": {"seed": seed, "steps": steps, "snapshot": snapshot}, "observer": evidence}


def _exercise(args) -> None:
    torch, module = _load(args.library)
    result = {name: _case(torch, module, name, args.enabled, args.explicit_none) for name in _CASES}
    if args.enabled:
        for failure, invalidation_failure in ((True, False), (True, True)):
            case = _case(torch, module, "partial_split", True, False,
                         fail=failure, invalidate_fail=invalidation_failure)
            assert case["semantic"] == result["partial_split"]["semantic"]
        # A concurrent caller is permitted only through the scheduler's serial
        # dispatch. Exercise that topology, not an invented native/cache lock.
        serial = []
        for _ in range(8):
            thread = threading.Thread(target=lambda: serial.append(_case(torch, module, "partial_split", True, False)["semantic"]))
            thread.start()
            thread.join()
        assert len(serial) == 8 and all(value == result["partial_split"]["semantic"] for value in serial)
        _contended_getter(torch, module)
        _suspended_observer_lifetime(torch, module, abort=False)
        _suspended_observer_lifetime(torch, module, abort=True)
        _outside_window(torch, module)
    observer._json_new(args.output, {"status": "PASS", "module": module.__name__,
                                    "production_module": module.__spec__.name,
                                    "library_path": str(Path(module.__file__).resolve()),
                                    "library_sha256": observer._sha(Path(module.__file__).read_bytes()),
                                    "environment": _environment(torch), "cases": result})


def _contended_getter(torch, module) -> None:
    """Force GIL release inside capture while an outside getter takes the core.

    Events/sleep belong only to this CPU qualification harness. Production
    observer/cache code gets no event, wait, new Mutex, or Mutex release.
    """
    core = module.RustUnifiedTreeCoreBinding(module.TreeCoreInitParamsBinding(device="cpu"), [0])
    _walk(core, _params(module, torch, [1, 2, 3, 4], [10, 11, 12, 13]), torch)
    node = core.match_prefix(module.MatchParamsBinding(array("q", [1, 2, 3, 4]))).last_device_node_id
    expected = {node: _metadata(core.get_component_device_value(node, 0))}
    entered, attempted, completed = threading.Event(), threading.Event(), threading.Event()
    failures = []

    def read_outside_callback():
        try:
            assert entered.wait(10)
            attempted.set()
            core.get_component_device_value(node, 0)
            completed.set()
        except BaseException as error:
            failures.append(str(error))

    class Capture(_Capture):
        def __call__(self, *arguments):
            super().__call__(*arguments)
            entered.set()
            assert attempted.wait(10)
            time.sleep(0.02)
            assert not completed.is_set(), "Getter unexpectedly entered while native Mutex is held"

    thread = threading.Thread(target=read_outside_callback, daemon=True)
    thread.start()
    capture = Capture(expected)
    _walk(core, _params(module, torch, [1, 2, 8], [20, 21, 28], capture=capture), torch)
    thread.join(10)
    assert completed.is_set() and not thread.is_alive() and not failures, failures
    assert capture.rows and not capture.invalidations, capture.invalidations


def _suspended_observer_lifetime(torch, module, *, abort: bool) -> None:
    init = module.TreeCoreInitParamsBinding(device="cpu", mamba_cache_chunk_size=1, mamba_max_states_per_path=1)
    core = module.RustUnifiedTreeCoreBinding(init, [0, 2])
    _walk(core, _params(module, torch, [1, 2, 3], [10, 11, 12], mamba=True), torch)
    node = core.match_prefix(module.MatchParamsBinding(array("q", [1, 2, 3]))).last_device_node_id
    capture = _Capture({node: _metadata(core.get_component_device_value(node, 0))})
    reference = weakref.ref(capture)
    params = _params(module, torch, [1, 2, 3, 4], [20, 21, 22, 23], mamba=True, capture=capture)
    step = core.begin_insert(params)
    assert step.result is None and core.has_ongoing_insert()
    del params, capture
    gc.collect()
    assert reference() is not None, "Walk does not own observer across native barrier"
    for action in step.actions:
        if action[0] == "mamba_evict_excess_path_states":
            core.evict_excess_path_states(action[1])
    if abort:
        core.end_insert()
    else:
        done = core.resume_insert()
        assert done.result is not None
    assert not core.has_ongoing_insert()
    gc.collect()
    assert reference() is None, "Finished native walk retains observer"


def _outside_window(torch, module) -> None:
    core = module.RustUnifiedTreeCoreBinding(module.TreeCoreInitParamsBinding(device="cpu"), [0])
    _walk(core, _params(module, torch, [1, 2, 3, 4], [10, 11, 12, 13]), torch)
    capture = _Capture({})
    params = _params(module, torch, [1, 2, 8], [20, 21, 28])
    params.old_full_observer = (capture, "cpu-rid", 10, 20)
    result = _walk(core, params, torch)
    assert result[-1]["result"]["prefix_len"] == 2
    assert not capture.rows and not capture.invalidations


def _rust_tests(args) -> dict:
    """Native core fixtures, using the production loader's Torch environment."""
    import torch
    from sglang.srt.rust_extensions.torch_build import torch_build_configuration

    output = args.archive_dir if args.output is None else args.output
    build = torch_build_configuration(compat_header=args.archive_dir / "sources/observer/torch_compat.h",
                                     python_module=observer.MODULE, torch_module=torch)
    with tempfile.TemporaryDirectory(prefix="rust-kv-tests-", dir=os.environ["TMPDIR"]) as temporary:
        target = Path(temporary) / "target"
        command = ["cargo", "test", "--locked", "--offline", "--manifest-path",
                   str(args.archive_dir / "sources/observer/Cargo.toml"), "--target-dir",
                   str(target), "old_full_observer", "--", "--nocapture"]
        with (output / "native-fixtures.stdout").open("xb") as stdout, (output / "native-fixtures.stderr").open("xb") as stderr:
            result = subprocess.run(command, env=build.environment, stdout=stdout, stderr=stderr, check=False)
    record = {"command": command, "returncode": result.returncode,
              "status": "PASS" if result.returncode == 0 else "FAIL", "target_retained": False}
    observer._json_new(output / "native-fixtures.json", record)
    if result.returncode:
        raise RuntimeError("Actual Rust observer fixtures failed; see native-fixtures.stderr")
    log = (output / "native-fixtures.stdout").read_text()
    if "2 passed" not in log:
        raise RuntimeError("Native fixture execution did not report both observer tests")
    return record


def _injected_invalidation_failure(stderr: str) -> None:
    marker = f"{observer.INVALIDATION_ERROR_MARKER} rid=cpu-rid P=0 E=32 stage=capture"
    assert stderr.count(observer.INVALIDATION_ERROR_MARKER) == 1 and marker in stderr, "Native invalidation-failure marker missing or duplicated"
    assert "injected OLD capture failure" in stderr and "injected invalidation failure" in stderr


def _qualify(args) -> None:
    observer._retained_build(args.root, image=observer.IMAGE, archive_dir=args.archive_dir)
    output_dir = args.archive_dir if args.output is None else args.output
    variants = (("original", None, False, False),
                ("rebuilt", Path(json.loads((args.archive_dir / "build-baseline.json").read_text())["path"]), False, False),
                ("observer-none", Path(json.loads((args.archive_dir / "build-observer.json").read_text())["path"]), False, True),
                ("observer-enabled", Path(json.loads((args.archive_dir / "build-observer.json").read_text())["path"]), True, False))
    outputs = {}
    for name, library, enabled, explicit_none in variants:
        args_list = ["_exercise", "--output", str(output_dir / f"qualify-{name}.json")]
        if library is not None:
            args_list += ["--library", str(library)]
        if enabled:
            args_list += ["--enabled"]
        if explicit_none:
            args_list += ["--explicit-none"]
        # Child output path differs from _run's build convention by intent.
        command = [sys.executable, "-B", str(Path(__file__).resolve()), *args_list]
        with (output_dir / f"qualify-{name}.stdout").open("xb") as stdout, (output_dir / f"qualify-{name}.stderr").open("xb") as stderr:
            completed = subprocess.run(command, stdout=stdout, stderr=stderr, check=False,
                                       timeout=_CPU_VARIANT_TIMEOUT_SECONDS)
        observer._json_new(output_dir / f"qualify-{name}-command.json", {"command": command, "returncode": completed.returncode})
        if completed.returncode:
            raise RuntimeError(f"Native CPU variant {name} failed; inspect retained stderr")
        outputs[name] = json.loads((output_dir / f"qualify-{name}.json").read_text())
    reference = {name: outputs["original"]["cases"][name]["semantic"] for name in _CASES}
    for variant, output in outputs.items():
        assert {name: output["cases"][name]["semantic"] for name in _CASES} == reference, variant
    errors = (output_dir / "qualify-observer-enabled.stderr").read_text()
    _injected_invalidation_failure(errors)
    for name in ("original", "rebuilt", "observer-none"):
        assert observer.INVALIDATION_ERROR_MARKER not in (output_dir / f"qualify-{name}.stderr").read_text(), name
    dependencies = _dependency_sources(output_dir)
    topology = _source_topology(args.root, output_dir, source_archive=args.archive_dir)
    fixtures = _rust_tests(args)
    result = {"status": "PASS", "variants": list(outputs), "cases": list(_CASES),
              "exact_actions_results_topology_indices": True, "native_fixtures": fixtures,
              "dependency_manifest": str(output_dir / "dependency-source-manifest.json"),
              "dependency_files": len(dependencies), "thread_topology": "serial scheduler calls only",
              "core_call_methods_with_detach": topology["count"], "contended_outside_getter": "PASS",
              "invalidation_failure_marker": observer.INVALIDATION_ERROR_MARKER,
              "invalidation_failure_marker_verified": True,
              "concurrent_unscheduled_mutex_reentry": "UNSUPPORTED; no new lock or release added",
              "cuda_thread_stream_witness": "PENDING", "original_binary_source_commit": "UNVERIFIED"}
    observer._json_new(output_dir / "qualification.json", result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "_build", "qualify", "_exercise", "resume"))
    parser.add_argument("--root", type=Path)
    parser.add_argument("--image")
    parser.add_argument("--archive-dir", type=Path)
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--variant", choices=("baseline", "observer"))
    parser.add_argument("--library", type=Path)
    parser.add_argument("--output", type=Path, help="New qualification directory for resume/qualify; JSON file for _exercise")
    parser.add_argument("--enabled", action="store_true")
    parser.add_argument("--explicit-none", action="store_true")
    args = parser.parse_args()
    if args.action == "build":
        observer.build_source(args.root, image=args.image, archive_dir=args.archive_dir)
    elif args.action == "resume":
        observer.resume_source(args.root, image=args.image, archive_dir=args.archive_dir, output_dir=args.output)
    elif args.action == "_build":
        _build(args)
    elif args.action == "qualify":
        _qualify(args)
    else:
        _exercise(args)


if __name__ == "__main__":
    main()
