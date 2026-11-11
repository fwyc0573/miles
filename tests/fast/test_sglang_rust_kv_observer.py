"""CPU source/preparation tests, not production-native compile qualification."""

import ast
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tests.manual.agent_opd import sglang_rust_kv_observer as observer
from tests.manual.agent_opd import probe_rust_kv_observer as probe


_TASK = Path(__file__).resolve().parents[2] / "task_memory/task_2026-11-08_qwen35_full_kl_nll"
_RUST = _TASK / "evidence/native-rust-source-20261111/exp-1111-124522-553024/checkout/rust/sglang-radix-tree"
_PYTHON = _TASK / "evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437/source"


class ObserverPrerequisites(unittest.TestCase):
    def test_incomplete_receipt_fails_without_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / "receipt.json"
            receipt.write_text(json.dumps({"status": "PENDING", "image": observer.IMAGE}))
            archive = root / "must-not-exist"
            with self.assertRaisesRegex(ValueError, "passing pinned"):
                observer.prepare_source(root / "package", image=observer.IMAGE,
                                        archive_dir=archive, build_receipt=receipt)
            self.assertFalse(archive.exists())

    def test_alternate_module_is_rejected_before_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / "receipt.json"
            receipt.write_text(json.dumps({"status": "PASS", "image": observer.IMAGE,
                                          "module": observer.MODULE + "_inspection"}))
            with self.assertRaisesRegex(ValueError, "same production"):
                observer.prepare_source(root, image=observer.IMAGE, archive_dir=root / "archive",
                                        build_receipt=receipt)
            self.assertFalse((root / "archive").exists())

    def test_shared_baseline_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / "receipt.json"
            receipt.write_text(json.dumps({"status": "PASS", "image": observer.IMAGE,
                "module": observer.MODULE, "features": ["python-extension"],
                "qualification": {"status": "PASS"}, "original": {"package_root": str(root)}}))
            with self.assertRaisesRegex(ValueError, "shared baseline"):
                observer.prepare_source(root, image=observer.IMAGE, archive_dir=root / "archive",
                                        build_receipt=receipt)
            self.assertFalse((root / "archive").exists())

    def test_loaded_module_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            receipt = root / "receipt.json"
            receipt.write_text(json.dumps({"status": "PASS", "image": observer.IMAGE,
                "module": observer.MODULE, "features": ["python-extension"],
                "qualification": {"status": "PASS"}}))
            with patch.dict(sys.modules, {observer.MODULE: SimpleNamespace()}):
                with self.assertRaisesRegex(ValueError, "after native import"):
                    observer.prepare_source(root, image=observer.IMAGE, archive_dir=root / "archive",
                                            build_receipt=receipt)
            self.assertFalse((root / "archive").exists())

    @unittest.skipUnless(_PYTHON.is_dir(), "Retained pinned Python source is not available")
    def test_bad_actual_library_hash_fails_before_any_staging_write(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "private-package"
            for relative in observer._PYTHON_PINS:
                destination = package / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((_PYTHON / relative).read_bytes())
            library = root / "candidate.so"
            library.write_bytes(b"\x7fELFnot-a-qualified-native-library")
            environment = {"python": "3.12.16", "torch": "2.14.1+cu130", "cxx11_abi": True, "cuda_initialized": False}
            built = {"module": observer.MODULE, "module_runtime_name": observer.MODULE, "features": ["python-extension"], "loader_mode": "force",
                     "rustc": "rustc 1.99.1 test", "environment": environment, "path": str(library), "sha256": "wrong"}
            receipt = root / "receipt.json"
            receipt.write_text(json.dumps({"status": "PASS", "image": observer.IMAGE, "module": observer.MODULE,
                "features": ["python-extension"], "original": {"package_root": str(root / "baseline")},
                "baseline": built, "observer": built,
                "qualification": {"status": "PASS", "variants": ["original", "rebuilt", "observer-none", "observer-enabled"],
                     "cases": ["ordinary", "partial_split", "missing_full", "end_abort", "mamba_barrier"],
                     "exact_actions_results_topology_indices": True, "native_fixtures": {"status": "PASS"}, "dependency_files": 6,
                     "invalidation_failure_marker": observer.INVALIDATION_ERROR_MARKER,
                     "invalidation_failure_marker_verified": True}}))
            # These mocks only reach a fail-closed preflight branch. They cannot
            # produce a passing native receipt or bypass a compilation gate.
            versions = {"torch": "2.14.1+cu130", "sglang": "0.5.24.dev80+g056f871", "apache-tvm-ffi": "0.1.11"}
            with patch.object(observer.sys, "version_info", (3, 12, 16)), patch.object(
                    observer.importlib.metadata, "version", side_effect=versions.__getitem__), patch.object(
                    observer, "_composed_sources", return_value={}):
                with self.assertRaisesRegex(ValueError, "binary identity differs"):
                    observer.prepare_source(package, image=observer.IMAGE, archive_dir=root / "archive", build_receipt=receipt)
            self.assertFalse((root / "archive").exists())
            self.assertEqual((package / observer._ADAPTER).read_bytes(), (_PYTHON / observer._ADAPTER).read_bytes())

    def test_no_new_builder_or_native_import_at_module_scope(self):
        source = Path(observer.__file__).read_text()
        tree = ast.parse(source)
        imports = [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertFalse(any("torch" in ast.unparse(node) or "sglang.srt" in ast.unparse(node) for node in imports))
        self.assertNotIn("cargo build", source)
        probe = Path(observer.__file__).with_name("probe_rust_kv_observer.py").read_text()
        self.assertIn('load_rust_extension(observer.MODULE, mode="force"', probe)
        self.assertIn('load_rust_extension(observer.MODULE, mode="never")', probe)
        self.assertNotIn("_load_extension_from_path", probe)
        self.assertNotIn("mem_cache_inspection", probe)


class ObserverCPUWorkflow(unittest.TestCase):
    """Mock orchestration boundaries only; no compiler or native runtime proof."""

    def test_insert_fixture_exports_actual_contiguous_int64_key_buffer(self):
        keys = [1, 2, 3, 4]
        module = SimpleNamespace(InsertParamsBinding=lambda **kwargs: kwargs)
        torch = SimpleNamespace(int64="int64", tensor=lambda values, **kwargs: values)
        params = probe._params(module, torch, keys, [10, 11, 12, 13])
        view = memoryview(params["key"])
        self.assertEqual((view.format, view.itemsize, view.ndim, view.c_contiguous), ("q", 8, 1, True))
        self.assertEqual(view.tolist(), keys)
        self.assertEqual(params["value"], [10, 11, 12, 13])
        with self.assertRaises(TypeError):
            memoryview(keys)

    def test_every_native_match_constructor_uses_the_same_int64_buffer(self):
        tree = ast.parse(Path(probe.__file__).read_text())
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Attribute) and node.func.attr == "MatchParamsBinding"]
        self.assertEqual(len(calls), 4)
        for call in calls:
            self.assertIsInstance(call.args[0], ast.Call)
            self.assertEqual(ast.unparse(call.args[0].func), "array")
            self.assertEqual(ast.literal_eval(call.args[0].args[0]), "q")

    @unittest.skipUnless(_RUST.is_dir(), "Retained pinned native ABI source is not available")
    def test_fixture_fields_and_used_methods_match_the_pinned_native_abi(self):
        binding = (_RUST / "src/python_bindings.rs").read_text()

        def fields(name):
            body = re.search(r"pub struct " + name + r" \{(.*?)\n\}", binding, re.S).group(1)
            return set(re.findall(r"^\s*(?:pub )?(\w+):", body, re.M))

        self.assertEqual(set(probe._RESULT_FIELDS), fields("InsertResultBinding"))
        self.assertEqual(set(probe._MATCH_FIELDS), fields("MatchResultBinding"))
        tree = ast.parse(Path(probe.__file__).read_text())
        methods = {node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Attribute) and ast.unparse(node.func.value) == "core"}
        self.assertEqual(methods, {"begin_insert", "resume_insert", "end_insert", "has_ongoing_insert", "match_prefix",
                                  "collect_path_info", "get_component_device_value", "commit_backup", "demote", "evict_excess_path_states"})
        for method in methods:
            self.assertIn("fn " + method + "(", binding)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "TreeCoreInitParamsBinding":
                self.assertLessEqual({keyword.arg for keyword in node.keywords}, fields("TreeCoreInitParamsBinding"))
        self.assertIn("key.extract::<PyBuffer<i64>>()?", binding)
        self.assertIn("buffer.is_c_contiguous()", binding)
        self.assertIn("type TreePathNodeInfoTuple = (NodeId, NodeId, usize, usize, Option<usize>, usize)", binding)

    def test_resume_rejects_existing_output_without_native_execution(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "old-attempt"
            archive.mkdir()
            (archive / "qualification-command.json").write_text('{"returncode": 1}')
            output = Path(temporary) / "existing-output"
            output.mkdir()
            with patch.object(observer, "_retained_build", return_value={}), patch.object(observer, "_run") as run:
                with self.assertRaisesRegex(ValueError, "separate new"):
                    observer.resume_source(Path(temporary), image=observer.IMAGE, archive_dir=archive, output_dir=output)
                run.assert_not_called()
            self.assertEqual(list(output.iterdir()), [])

    def test_resume_runs_only_qualification_and_does_not_finalize_a_failure(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "old-attempt"
            archive.mkdir()
            failure = archive / "qualification-command.json"
            failure.write_text('{"returncode": 1}')
            failed_log = archive / "qualify-original.stderr"
            failed_log.write_text("original retained failure")
            output = Path(temporary) / "new-qualification"
            # Negative orchestration test only: no successful qualification is
            # fabricated, no native call runs, and the sole finalizer is skipped.
            receipt = {"input_receipts": {}, "baseline": {"path": "/retained/baseline.so", "sha256": "baseline"},
                       "observer": {"path": "/retained/observer.so", "sha256": "observer"}}
            with patch.object(observer, "_retained_build", return_value=receipt), patch.object(
                    observer, "_run", side_effect=RuntimeError("native qualification pending")) as run, patch.object(
                    observer, "finalize_build") as finalize:
                with self.assertRaisesRegex(RuntimeError, "native qualification pending"):
                    observer.resume_source(Path(temporary), image=observer.IMAGE, archive_dir=archive, output_dir=output)
                command = run.call_args.args[2]
                self.assertEqual(command[0], "qualify")
                self.assertIn(str(archive), command)
                self.assertIn(str(output), command)
                finalize.assert_not_called()
            self.assertEqual(failure.read_text(), '{"returncode": 1}')
            self.assertEqual(failed_log.read_text(), "original retained failure")
            self.assertFalse((archive / "observer-build.json").exists())
            self.assertEqual([path.name for path in output.iterdir()], ["resume-inputs.json"])

    @unittest.skipUnless(_RUST.is_dir() and (_TASK / "evidence/native-rust-kv-observer-build-20261111/build-observer.json").is_file(),
                         "Actual completed CPU build artifacts are not available")
    def test_actual_completed_build_artifacts_and_native_source_remain_unchanged(self):
        archive = _TASK / "evidence/native-rust-kv-observer-build-20261111"
        expected = {"baseline": "fbe6ea7c5e48216daa34f13b792b38ecf39090a99a3f9a72f776a388d67124aa",
                    "observer": "0dc763cc3b53bae4b62116407cdd5e0a30d3a9353bab9fe15424c30ce41b49ba"}
        for variant, sha in expected.items():
            built = json.loads((archive / f"build-{variant}.json").read_text())
            if not Path(built["path"]).is_file():
                self.skipTest("Retained compiled libraries are NFS-only references unavailable on this host")
            observer._verify_compiled_build(built, variant)
            self.assertEqual(built["sha256"], sha)
            self.assertEqual(observer._sha(Path(built["path"]).read_bytes()), sha)
        before = observer._qualified_files(_RUST, observer._RUST_PINS)
        after = {relative: observer._rust_candidate(relative, content) for relative, content in before.items()}
        self.assertEqual(json.loads((archive / "source-manifest.json").read_text())["after"], observer._identities(after))

    def test_worker_tmpdir_matches_existing_formal_local_root(self):
        config = json.loads((_TASK / "rust_kv_observer_cpu_config.json").read_text())
        formal = json.loads((_TASK / "formal_config.json").read_text())
        self.assertEqual(config["environment"]["TMPDIR"], formal["worker_local_root"])
        self.assertEqual(config["environment"]["SGLANG_RUST_BUILD_MODE"], "never")

    def test_loader_cache_is_temporary_and_only_library_is_retained(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            local = root / "worker-local"
            local.mkdir()
            args = SimpleNamespace(root=root / "package", archive_dir=root / "archive",
                                   workspace=root / "archive/sources/observer", variant="observer")
            recorded = []

            def load(name, *, mode, cache_dir, **kwargs):
                self.assertEqual((name, mode), (observer.MODULE, "force"))
                self.assertEqual(cache_dir.parent.parent, local)
                self.assertFalse(cache_dir.is_relative_to(args.archive_dir))
                cache_dir.mkdir()
                library = cache_dir / "mem_cache.mock-source-only.so"
                library.write_bytes(b"source-only placement fixture, not an ELF library")
                recorded.append(cache_dir)
                return SimpleNamespace(__file__=str(library), __name__=observer.MODULE,
                                       __spec__=SimpleNamespace(name=observer.MODULE))

            modules = {"torch": SimpleNamespace(), "sglang": SimpleNamespace(__file__=str(args.root / "__init__.py")),
                       "sglang.srt.rust_extensions.loader": SimpleNamespace(load_rust_extension=load),
                       "sglang.srt.rust_extensions.torch_build": SimpleNamespace(
                           torch_build_configuration=lambda **kwargs: SimpleNamespace(environment={}, fingerprint="source-only"))}
            with patch.dict(sys.modules, modules), patch.dict(probe.os.environ, {"TMPDIR": str(local)}), patch.object(
                    probe, "_environment", return_value={}), patch.object(probe.subprocess, "run",
                    return_value=SimpleNamespace(stdout="rustc 1.99.1 source-only")):
                probe._build(args)
            self.assertEqual(len(recorded), 1)
            self.assertFalse(recorded[0].exists())
            files = sorted(str(path.relative_to(args.archive_dir)) for path in args.archive_dir.rglob("*") if path.is_file())
            self.assertEqual(files, ["build-observer.json", "libraries/observer/mem_cache.mock-source-only.so"])
            receipt = json.loads((args.archive_dir / "build-observer.json").read_text())
            library = Path(receipt["path"])
            self.assertEqual(receipt["sha256"], observer._sha(library.read_bytes()))
            self.assertFalse(receipt["loader_cache_retained"])

    def test_native_fixture_target_is_temporary_and_logs_are_retained(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            local, archive = root / "worker-local", root / "archive"
            local.mkdir()
            archive.mkdir()
            recorded = []

            def run(command, *, stdout, stderr, **kwargs):
                target = Path(command[command.index("--target-dir") + 1])
                self.assertEqual(target.parent.parent, local)
                self.assertFalse(target.is_relative_to(archive))
                target.mkdir()
                (target / "mock-object").write_bytes(b"source-only placement fixture")
                recorded.append(target)
                stdout.write(b"source-only orchestration fixture: 2 passed\n")
                return SimpleNamespace(returncode=0)

            modules = {"torch": SimpleNamespace(), "sglang.srt.rust_extensions.torch_build": SimpleNamespace(
                torch_build_configuration=lambda **kwargs: SimpleNamespace(environment={}))}
            with patch.dict(sys.modules, modules), patch.dict(probe.os.environ, {"TMPDIR": str(local)}), patch.object(
                    probe.subprocess, "run", side_effect=run):
                record = probe._rust_tests(SimpleNamespace(archive_dir=archive, output=None))
            self.assertFalse(recorded[0].exists())
            self.assertFalse(record["target_retained"])
            self.assertEqual(sorted(path.name for path in archive.iterdir()),
                             ["native-fixtures.json", "native-fixtures.stderr", "native-fixtures.stdout"])

    def test_injected_failure_requires_native_marker_and_both_errors(self):
        marker = f"{observer.INVALIDATION_ERROR_MARKER} rid=cpu-rid P=0 E=32 stage=capture"
        errors = [marker, "injected OLD capture failure", "injected invalidation failure"]
        probe._injected_invalidation_failure("\n".join(errors))
        for missing in range(3):
            with self.subTest(missing=missing), self.assertRaises(AssertionError):
                probe._injected_invalidation_failure("\n".join(error for index, error in enumerate(errors) if index != missing))
        with self.assertRaises(AssertionError):
            probe._injected_invalidation_failure("\n".join(errors + [marker]))


class ObserverReceiptLocation(unittest.TestCase):
    """Receipt routing/preflight only; never new native qualification evidence."""

    def test_existing_final_receipt_does_not_mask_source_identity_gate(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive, root = Path(temporary) / "archive", Path(temporary) / "package"
            archive.mkdir()
            old = archive / "observer-build.json"
            old.write_bytes(b"old retained receipt; source-only location fixture")
            original = old.read_bytes()
            pending = {"status": "PENDING", "task_id": observer.TASK_ID, "image": observer.IMAGE,
                       "module": observer.MODULE, "features": ["python-extension"],
                       "original": {"package_root": str(root)}}
            (archive / "observer-build-pending.json").write_text(json.dumps(pending))
            with patch.object(observer, "_qualified_files", side_effect=ValueError("source identity differs")) as validate:
                with self.assertRaisesRegex(ValueError, "source identity differs"):
                    observer._retained_build(root, image=observer.IMAGE, archive_dir=archive)
                validate.assert_called_once_with(root.parents[1] / "rust/sglang-radix-tree", observer._RUST_PINS)
            self.assertEqual(old.read_bytes(), original)

    @unittest.skipUnless((_TASK / "evidence/native-rust-kv-observer-qualification-20261111-r2/qualification.json").is_file(),
                         "Actual R2 receipt inputs are not available")
    def test_finalizer_routes_only_to_new_qualification_receipt(self):
        actual = _TASK / "evidence/native-rust-kv-observer-build-20261111/observer-build.json"
        if not actual.is_file():
            self.skipTest("Actual retained root receipt is not available")
        r2 = _TASK / "evidence/native-rust-kv-observer-qualification-20261111-r2"
        with tempfile.TemporaryDirectory() as temporary:
            archive, output = Path(temporary) / "archive", Path(temporary) / "qualification"
            archive.mkdir()
            output.mkdir()
            old = archive / "observer-build.json"
            old.write_bytes(actual.read_bytes())
            original = old.read_bytes()
            for name in ["qualification.json", "qualification-command.json", *(
                    f"qualify-{variant}.json" for variant in ("original", "rebuilt", "observer-none", "observer-enabled"))]:
                (output / name).write_bytes((r2 / name).read_bytes())
            paths = []

            def write_destination(path, receipt):
                paths.append(path)
                # Real R2 JSON supplies validation inputs, but this source-only
                # writer cannot manufacture a new PASS/native proof artifact.
                observer._write_new(path, b"source-only receipt destination; not native qualification")

            with patch.object(observer, "_retained_build", return_value=json.loads(original)), patch.object(
                    observer, "_json_new", side_effect=write_destination):
                observer.finalize_build(Path(temporary), image=observer.IMAGE,
                                        archive_dir=archive, qualification_dir=output)
            self.assertEqual(paths, [output / "observer-build.json"])
            self.assertTrue((output / "observer-build.json").is_file())
            self.assertEqual(old.read_bytes(), original)

    def test_failed_qualification_never_writes_either_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive, output = Path(temporary) / "archive", Path(temporary) / "qualification"
            archive.mkdir()
            output.mkdir()
            old = archive / "observer-build.json"
            old.write_bytes(b"old receipt bytes, not a new qualification")
            original = old.read_bytes()
            (output / "qualification.json").write_text('{"status":"FAIL"}')
            with patch.object(observer, "_retained_build", return_value={}), patch.object(observer, "_json_new") as write:
                with self.assertRaisesRegex(ValueError, "required production scenarios"):
                    observer.finalize_build(Path(temporary), image=observer.IMAGE,
                                            archive_dir=archive, qualification_dir=output)
                write.assert_not_called()
            self.assertFalse((output / "observer-build.json").exists())
            self.assertEqual(old.read_bytes(), original)


class ObserverContendedGetter(unittest.TestCase):
    """Real harness oracle with deterministic scheduling, not native/GIL proof."""

    def _contended_getter(self, scenario):
        events, threads, captures, completed_getters = [], [], [], []

        class Event:
            def __init__(self):
                self.set_value = False
                events.append(self)

            def set(self):
                self.set_value = True
                if self is events[0] and scenario == "premature_getter":
                    threads[0].join(0)

            def is_set(self):
                return self.set_value

            def wait(self, timeout):
                return self.is_set()

        class Thread:
            def __init__(self, *, target, daemon):
                self.target = target
                self.finished = False
                threads.append(self)

            def start(self):
                pass

            def join(self, timeout):
                if not self.finished:
                    self.finished = True
                    self.target()

            def is_alive(self):
                return False

        indices = SimpleNamespace(tolist=lambda: [10, 11, 12, 13])

        def get_value(node, component):
            if events:
                if scenario == "getter_failure":
                    raise RuntimeError("injected outside getter failure")
                completed_getters.append(node)
            return indices

        core = SimpleNamespace(match_prefix=lambda params: SimpleNamespace(last_device_node_id=1),
                               get_component_device_value=get_value)
        module = SimpleNamespace(TreeCoreInitParamsBinding=lambda **kwargs: kwargs,
                                 RustUnifiedTreeCoreBinding=lambda *args: core,
                                 MatchParamsBinding=lambda key: key,
                                 InsertParamsBinding=lambda **kwargs: SimpleNamespace(**kwargs))
        torch = SimpleNamespace(int64="int64", tensor=lambda values, **kwargs: values)

        def walk(core, params, torch):
            if not hasattr(params, "old_full_observer"):
                return
            capture, rid, start, end = params.old_full_observer
            captures.append(capture)
            if scenario == "missing_callback":
                return
            # Model only the existing native error route: callback exceptions
            # invalidate rather than escape _walk. No native PASS is fabricated.
            try:
                capture(rid, start, end, 1, 0, 2, indices)
            except Exception as error:
                capture.invalidate(rid, start, end, "capture", f"{type(error).__name__}: {error}")

        with patch.object(probe.threading, "Event", Event), patch.object(probe.threading, "Thread", Thread), patch.object(
                probe.time, "sleep"), patch.object(probe, "_metadata", return_value={}), patch.object(
                probe, "_walk", side_effect=walk):
            try:
                probe._contended_getter(torch, module)
            except AssertionError as error:
                return error, captures[0], completed_getters
        return None, captures[0], completed_getters

    def test_rejects_invalidated_callback_when_outside_getter_completes(self):
        for scenario in ("attempt_timeout", "premature_getter"):
            with self.subTest(scenario=scenario):
                error, capture, completed_getters = self._contended_getter(scenario)
                self.assertTrue(capture.rows)
                self.assertEqual(completed_getters, [1])
                self.assertEqual(capture.invalidations[0][:4], ["cpu-rid", 0, 32, "capture"])
                self.assertIn("AssertionError", capture.invalidations[0][4])
                self.assertIsNotNone(error, "Old oracle falsely accepted an invalidated callback after getter completion")
                self.assertIn("capture", str(error))

    def test_outside_getter_failure_still_rejects(self):
        error, capture, completed_getters = self._contended_getter("getter_failure")
        self.assertIsNotNone(error)
        self.assertIn("injected outside getter failure", str(error))
        self.assertTrue(capture.invalidations)
        self.assertEqual(completed_getters, [])

    def test_missing_callback_rejects_without_real_timeout(self):
        error, capture, completed_getters = self._contended_getter("missing_callback")
        self.assertIsNotNone(error)
        self.assertEqual((capture.rows, capture.invalidations, completed_getters), ([], [], []))


@unittest.skipUnless(_RUST.is_dir() and _PYTHON.is_dir(), "Retained pinned production sources are not available")
class ObserverPinnedSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before = observer._qualified_files(_RUST, observer._RUST_PINS)
        cls.after = {relative: observer._rust_candidate(relative, content) for relative, content in cls.before.items()}

    def test_full_crate_identity_and_exact_patch_scope(self):
        self.assertEqual(len(self.before), 22)
        self.assertEqual(sum(relative.endswith(".rs") for relative in self.before), 19)
        self.assertEqual({relative for relative in self.before if self.before[relative] != self.after[relative]}, {
            "src/unified_tree_core.rs", "src/python_bindings.rs", "src/tests/unified_tree_core.rs",
            "src/tests/components/base.rs", "src/tests/components/full.rs",
            "src/tests/components/mamba.rs", "src/tests/components/swa.rs"})
        for relative in ("Cargo.toml", "Cargo.lock", "torch_compat.h", "src/node.rs", "src/components/full.rs"):
            self.assertEqual(self.before[relative], self.after[relative])

    def test_partial_split_observer_is_original_and_immediate(self):
        old = self.before["src/unified_tree_core.rs"].decode()
        new = self.after["src/unified_tree_core.rs"].decode()
        self.assertNotIn("old_full_observer", old)  # RED: no native baseline seam.
        start = new.index("    fn insert_walk_step_(")
        stop = new.index("    pub(crate) fn insert_overlap_step_(", start)
        walk = new[start:stop]
        seam = "let prefix_len = state.key.match_len(cursor, &node.key, self.page_size);"
        self.assertIn(seam + "\n        if let Some(observer) = &state.old_full_observer", walk)
        self.assertLess(walk.index("observer(node.id, cursor, prefix_len, node.try_device_value(FULL))"),
                        walk.index("self.split_node_"))
        callback = walk[walk.index("if let Some(observer)"):walk.index("if prefix_len <")]
        self.assertNotIn("state.value", callback)
        for token in ("narrow", "copy", "cat", "Mutex", "lock", "stream", "wait"):
            self.assertNotIn(token, callback)

    def test_native_state_retains_context_but_component_params_do_not(self):
        new = self.after["src/unified_tree_core.rs"].decode()
        self.assertIn("old_full_observer: params.old_full_observer.clone(),", new)
        self.assertEqual(new.count("old_full_observer: None,"), 3)
        self.assertIn("pub type OldFullObserver = Arc<dyn Fn(NodeId, usize, usize, Option<&Tensor>) + Send + Sync>", new)
        self.assertEqual(new.count("observer(node.id, cursor, prefix_len, node.try_device_value(FULL))"), 1)

    def test_python_bridge_errors_are_observable(self):
        new = self.after["src/python_bindings.rs"].decode()
        begin = new.index("fn old_full_observer(")
        bridge = new[begin:new.index("/// Convert a Python int64 sequence", begin)]
        self.assertLess(bridge.index("cursor >= end"), bridge.index("Python::attach"))
        self.assertIn("tensor_to_py(py, tensor.shallow_clone())", bridge)
        self.assertIn("None => Ok(py.None())", bridge)
        self.assertIn('getattr("invalidate")', bridge)
        self.assertIn("invalidate.bind(py).call1", bridge)
        self.assertEqual(bridge.count("write_unraisable"), 2)
        self.assertEqual(bridge.count(observer.INVALIDATION_ERROR_MARKER), 1)
        self.assertIn('rid={} P={} E={} stage={}', bridge)
        marker = bridge.index('eprintln!')
        self.assertGreater(marker, bridge.index("if let Err(invalidation_error)"))
        self.assertLess(marker, bridge.index("error.write_unraisable"))
        self.assertNotIn("let _ =", bridge)
        self.assertNotIn("catch_unwind", bridge)
        self.assertEqual(new.count("old_full_observer: old_full_observer(py, params.old_full_observer.as_ref())?"), 2)

    def test_fixture_defaults_and_real_native_tests(self):
        fixtures = [relative for relative in self.after if relative.startswith("src/tests/")
                    and self.after[relative] != self.before[relative]]
        self.assertEqual(len(fixtures), 5)
        for relative in fixtures:
            new = self.after[relative].decode()
            self.assertEqual(new.count("track_adopted_ranges: false,"), new.count("old_full_observer: None,"))
        native = self.after["src/tests/unified_tree_core.rs"].decode()
        self.assertIn("fn old_full_observer_precedes_partial_split_and_borrows_original_storage", native)
        self.assertIn("fn old_full_observer_sees_none_before_fresh_restoration", native)
        self.assertIn("assert_eq!(value.data_ptr() as usize, pointer)", native)

    def test_each_source_tamper_is_rejected(self):
        for relative, content in self.before.items():
            with self.subTest(relative=relative):
                with self.assertRaisesRegex(ValueError, "identity differs"):
                    observer._rust_candidate(relative, content + b"\n")

    def test_actual_adapter_constructor_forwards_optional_tuple(self):
        content = (_PYTHON / observer._ADAPTER).read_bytes()
        candidate = observer._adapter_candidate(content)
        before = ast.parse(content)
        after = ast.parse(candidate)
        original = next(node for node in ast.walk(before) if isinstance(node, ast.FunctionDef) and node.name == "begin_insert")
        changed = next(node for node in ast.walk(after) if isinstance(node, ast.FunctionDef) and node.name == "begin_insert")
        self.assertNotIn("old_full_observer", ast.unparse(original))
        changed.returns = None
        for argument in changed.args.args:
            argument.annotation = None
        compiled = ast.fix_missing_locations(ast.Module(body=[changed], type_ignores=[]))
        captured = []
        namespace = {"_radix_key_buffer": lambda key: key}
        exec(compile(compiled, str(_PYTHON / observer._ADAPTER), "exec"), namespace)
        binding = SimpleNamespace(begin_insert=lambda params: params)
        bindings = SimpleNamespace(InsertParamsBinding=lambda **kwargs: captured.append(kwargs) or kwargs)
        adapter = SimpleNamespace(_binding=binding, _bindings=bindings, _insert_step_from_binding=lambda step: step)
        params = SimpleNamespace(key=SimpleNamespace(extra_key=None, cache_salt=None), value=[1], session_id=None,
                                 mamba_value=None, prev_prefix_len=0, get_evicted_seqlen=lambda component: 0,
                                 swa_branching_seqlen=None, inserted_len=0, priority=None, track_adopted_ranges=False,
                                 rotation_base=None)
        namespace["ComponentType"] = SimpleNamespace(SWA=1)
        namespace["begin_insert"](adapter, params)
        self.assertIsNone(captured[-1]["old_full_observer"])
        context = (object(), "rid", 3, 7)
        params.old_full_observer = context
        namespace["begin_insert"](adapter, params)
        self.assertIs(captured[-1]["old_full_observer"], context)
        del captured[-1]["old_full_observer"]
        self.assertEqual(captured[0], {**captured[-1], "old_full_observer": None})


if __name__ == "__main__":
    unittest.main()
