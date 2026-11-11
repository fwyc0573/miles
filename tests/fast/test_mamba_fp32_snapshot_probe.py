"""CPU preparation checks; NumPy tensors and recorded Triton launches are mocks, never native verdicts."""

import ast
import contextlib
import copy
import io
import json
import math
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from typing import Optional, Tuple

import numpy as np

from tests.manual.agent_opd import probe_mamba_fp32_snapshots as probe
from tests.manual.agent_opd import sglang_mamba_snapshots as snapshots


_TASK = Path(__file__).resolve().parents[2] / "task_memory/task_2026-11-08_qwen35_full_kl_nll"
_SOURCE = _TASK / "evidence/native-sglang-cache-source-20261111/exp-1111-042450-358109/source"
_CONFIG_NAMES = ("mamba_snapshot_semantics_config.json", "mamba_snapshot_packed_prefix_A_config.json",
                 "mamba_snapshot_packed_prefix_B_config.json")


class _MockTensor:
    def __init__(self, torch, values, dtype):
        self.torch, self.values, self.dtype = torch, np.asarray(values), dtype
        self.shape, self.device = self.values.shape, "cuda:0"

    def _new(self, values, dtype=None):
        return _MockTensor(self.torch, values, self.dtype if dtype is None else dtype)

    def __getitem__(self, index):
        if isinstance(index, _MockTensor):
            index = index.values
        return self._new(self.values[index])

    def __bool__(self):
        assert self.torch.inspection_allowed, "Producer attempted a host reduction"
        return bool(self.values)

    def __neg__(self):
        return self._new(-self.values)

    def __mul__(self, value):
        return self._new(self.values * value)

    def __sub__(self, value):
        return self._new(self.values - value.values)

    def __truediv__(self, value):
        return self._new(self.values / value.values)

    def __ne__(self, value):
        return self._new(self.values != (value.values if isinstance(value, _MockTensor) else value))

    def __invert__(self):
        return self._new(~self.values)

    def clone(self):
        return self._new(self.values.copy())

    def contiguous(self):
        return self._new(np.ascontiguousarray(self.values))

    def sigmoid(self):
        return self._new(1 / (1 + np.exp(-self.values)))

    def to(self, dtype):
        values = self.values.astype(np.float32)
        if dtype == self.torch.bfloat16:
            bits = values.view(np.uint32)
            values = ((bits + 0x7FFF + ((bits >> 16) & 1)) & 0xFFFF0000).astype(np.uint32).view(np.float32)
        return self._new(values, dtype)

    def double(self):
        return self._new(self.values.astype(np.float64), "torch.float64")

    def float(self):
        return self.to(self.torch.float32)

    def abs(self):
        return self._new(np.abs(self.values))

    def all(self):
        return self._new(self.values.all())

    def any(self):
        return self._new(self.values.any())

    def sum(self):
        return self._new(self.values.sum())

    def max(self):
        return self._new(self.values.max())

    def item(self):
        assert self.torch.inspection_allowed, "Producer attempted a host read"
        return self.values.item()

    def tolist(self):
        assert self.torch.inspection_allowed, "Producer attempted a host read"
        return self.values.tolist()

    def numel(self):
        return self.values.size

    def stride(self):
        return tuple(stride // self.values.itemsize for stride in self.values.strides)

    def detach(self):
        return self

    def cpu(self):
        assert self.torch.inspection_allowed, "Producer attempted a host copy"
        return self


class _MockTorch:
    Tensor = _MockTensor
    bfloat16, float32, int32 = "torch.bfloat16", "torch.float32", "torch.int32"

    def __init__(self):
        self.draws, self.saved = [], []
        self.inspection_allowed = False
        self.cuda = SimpleNamespace(synchronize=self._synchronize)

    def _synchronize(self):
        self.inspection_allowed = True

    def manual_seed(self, seed):
        self.rng = np.random.RandomState(seed)

    def randn(self, *shape, device, dtype):
        self.draws.append(("randn", shape, dtype))
        return _MockTensor(self, self.rng.standard_normal(shape).astype(np.float32), dtype).to(dtype)

    def rand(self, *shape, device, dtype):
        self.draws.append(("rand", shape, dtype))
        return _MockTensor(self, self.rng.random_sample(shape).astype(np.float32), dtype)

    def randn_like(self, tensor):
        return self.randn(*tensor.shape, device=tensor.device, dtype=tensor.dtype)

    def tensor(self, values, device, dtype):
        return _MockTensor(self, np.asarray(values, dtype=np.int32), dtype)

    def full(self, shape, value, device, dtype):
        return _MockTensor(self, np.full(shape, value, dtype=np.float32), dtype)

    def full_like(self, tensor, value):
        return self.full(tensor.shape, value, device=tensor.device, dtype=tensor.dtype)

    def zeros_like(self, tensor):
        return self.full_like(tensor, 0)

    def isfinite(self, tensor):
        return tensor._new(np.isfinite(tensor.values))

    def equal(self, actual, expected):
        assert self.inspection_allowed, "Producer attempted a host comparison"
        return np.array_equal(actual.values, expected.values)

    def save(self, raw, path):
        self.saved.append(path)


class _MockBackend:
    """Record caller inputs and return fixed artifacts, with no recurrence implementation."""

    def __init__(self, torch, config):
        self.torch, self.config, self.calls = torch, config, []

    def extend(self, **arguments):
        self.calls.append((arguments, arguments["ssm_states"].values.copy()))
        state, length = arguments["ssm_states"], arguments["q"].shape[1]
        rows = [state.values[slot] if slot >= 0 else np.zeros(state.shape[1:]) for slot in self.config["cache_indices"]]
        entry = _MockTensor(self.torch, np.asarray(rows), self.torch.float32)
        h = entry.to(self.torch.bfloat16)._new(np.repeat(entry.to(self.torch.bfloat16).values[:, None],
                                                       math.ceil(length / self.config["kernel_chunk_size"]), axis=1))
        if "track_state" in arguments:
            for row, chunk in enumerate(arguments["track_chunk_idx"].values):
                if chunk >= 0:
                    arguments["track_state"].values[row] = entry.values[row]
        return arguments["v"].clone(), None, h


class _MetadataTensor:
    def __init__(self, shape, dtype="bfloat16", values=None):
        self.shape, self.dtype, self.values = tuple(shape), dtype, values

    def __len__(self):
        return self.shape[0]

    def stride(self, axis):
        return math.prod(self.shape[axis + 1:])

    def new_empty(self, *shape):
        return _MetadataTensor(shape, self.dtype)

    def to(self, dtype):
        assert self.dtype == dtype
        return self


def _native_binding(config, length):
    """Execute retained candidate Python bindings with metadata tensors and a mock Triton launch."""
    _, _, candidate = snapshots._source_versions(_SOURCE, selected_fp32=True)
    definitions = []
    for relative, names in {
        "kernels/ops/attention/fla/chunk_delta_h.py": {"chunk_gated_delta_rule_fwd_h"},
        snapshots._CHUNK: {"chunk_gated_delta_rule_fwd", "ChunkGatedDeltaRuleFunction", "chunk_gated_delta_rule"},
        snapshots._TRITON: {"TritonGDNKernel"},
    }.items():
        for node in ast.parse(candidate[relative]).body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
                if node.name == "TritonGDNKernel":
                    node.body = [item for item in node.body if not isinstance(item, ast.FunctionDef) or item.name == "extend"]
                definitions.append(node)
    launch = {}

    class Launch:
        def __getitem__(self, grid):
            def record(**kwargs):
                launch.update(kwargs)
            return record

    class Function:
        @classmethod
        def apply(cls, *arguments):
            return cls.forward(None, *arguments)

    q = _MetadataTensor((1, length, config["qk_heads"], config["key_dim"]))
    v = _MetadataTensor((1, length, config["value_heads"], config["value_dim"]))
    namespace = {
        "torch": SimpleNamespace(Tensor=_MetadataTensor, LongTensor=_MetadataTensor, float32="float32",
                                 empty_like=lambda tensor: _MetadataTensor(tensor.shape),
                                 compiler=SimpleNamespace(disable=lambda f: f), autograd=SimpleNamespace(Function=Function)),
        "Optional": Optional, "Tuple": Tuple, "CHUNK_SIZE": config["kernel_chunk_size"], "SUPPRESS_LEVEL": 2,
        "LinearAttnKernelBase": type("LinearAttnKernelBase", (), {}),
        "is_cpu": lambda: False, "is_npu": lambda: False, "is_xpu": lambda: False,
        "input_guard": lambda f: f, "autocast_custom_fwd": lambda f: f, "l2norm_fwd": lambda tensor: tensor,
        "prepare_chunk_indices": lambda cu, size: _MetadataTensor((math.ceil(cu.values[-1] / size), 2), "int32"),
        "prepare_chunk_offsets": lambda cu, size: _MetadataTensor((2,), "int32"),
        "chunk_local_cumsum": lambda g, **kw: g,
        "chunk_gated_delta_rule_fwd_intra": lambda **kw: (
            _MetadataTensor((1, length, config["value_heads"], config["key_dim"])), v, object()),
        "chunk_fwd_o": lambda **kw: v, "triton": SimpleNamespace(cdiv=lambda a, b: math.ceil(a / b)),
        "chunk_gated_delta_rule_fwd_kernel_h_blockdim64": Launch(),
    }
    exec(compile(ast.Module(body=definitions, type_ignores=[]), "recorded-native-packed-bindings.py", "exec"), namespace)
    cu = _MetadataTensor((2,), "int32", [0, length])
    positions = _MetadataTensor((1,), "int32", config["track_chunk_indices"][-1])
    snapshot = _MetadataTensor((1, config["value_heads"], config["value_dim"], config["key_dim"]), "float32")
    output = namespace["TritonGDNKernel"]().extend(
        q=q, k=q, v=v, g=_MetadataTensor((1, length, config["value_heads"]), "float32"),
        beta=_MetadataTensor((1, length, config["value_heads"]), "float32"),
        ssm_states=_MetadataTensor((config["state_slots"], *snapshot.shape[1:]), "float32"),
        cache_indices=_MetadataTensor((1,), "int32", config["cache_indices"]), query_start_loc=cu,
        inplace_update=True, track_state=snapshot, track_chunk_idx=positions,
    )
    return launch, output, cu, snapshot, positions


class SnapshotProbePreparationTest(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((_TASK / "mamba_snapshot_packed_prefix_A_config.json").read_text())

    def _fixture_task(self, root):
        """Clone config bytes and relocate only formal mount/repo paths; no native allocation is tested."""
        root = root.resolve()
        repo = root / "repo"
        task = repo / "task_memory" / _TASK.name
        task.mkdir(parents=True)
        formal = json.loads((_TASK / "formal_config.json").read_text())
        formal.update(local_mount=str(root), repo=str(repo))
        (task / "formal_config.json").write_text(json.dumps(formal))
        for name in _CONFIG_NAMES:
            (task / name).write_bytes((_TASK / name).read_bytes())
        return task

    def _small_config(self, layout="packed"):
        config = copy.deepcopy(self.config)
        config.update(qk_heads=1, value_heads=2, key_dim=4, value_dim=3,
                      sequence_lengths=[133, 192], boundary_tokens=[64, 128], track_chunk_indices=[[1], [2]],
                      comparison_prefix_tokens=61)
        if layout == "equal_length":
            config.update(layout=layout, batch_size=3, cache_indices=[2, 0, -1],
                          track_chunk_indices=[[1, 2, -1], [2, 1, -1]])
        return config

    def _produced(self, config=None):
        config = self._small_config() if config is None else config
        torch = _MockTorch()
        backend = _MockBackend(torch, config)
        cases = probe._produce(torch, backend, config)
        return torch, backend, cases, config

    def test_actual_configs_and_cpu_only_cli(self):
        with tempfile.TemporaryDirectory(prefix="packed-cli-test-") as root:
            for location in ("initial_checkout", "relocated_checkout"):
                task = self._fixture_task(Path(root) / location)
                self.assertNotEqual(task, _TASK.resolve())
                for name in _CONFIG_NAMES:
                    with self.subTest(location=location, name=name), contextlib.redirect_stdout(io.StringIO()) as output:
                        self.assertEqual(probe.main(["--config", str(task / name), "--validate-config"]), 0)
                        verdict = json.loads(output.getvalue())
                        self.assertEqual(verdict["operator_inputs"], json.loads((_TASK / name).read_text()))
                        self.assertEqual(verdict["status"], "CPU_CONFIG_PASS")
                        self.assertEqual(verdict["cuda_semantics"], "UNVERIFIED")
                        self.assertEqual(verdict["failed_checks"], [])
        self.assertEqual(self.config["cache_indices"], [2])
        self.assertEqual(self.config["comparison_prefix_tokens"], 6519)

    def test_packed_rejections_and_old_live_row_constraint(self):
        mutations = [{"batch_size": 2, "cache_indices": [2, 1]}, {"cache_indices": [0]}, {"cache_indices": [-1]},
                     {"cache_indices": [4]}, {"sequence_lengths": [7253, 7253]}, {"sequence_lengths": [7232, 8192]},
                     {"comparison_prefix_tokens": 0}, {"comparison_prefix_tokens": 8192}, {"comparison_prefix_tokens": True},
                     {"boundary_tokens": [7168, 7231]}, {"track_chunk_indices": [[112]]},
                     {"qkv_dtype": "float32"}, {"index_dtype": "int64"}, {"layout": "equal_length"}]
        with tempfile.TemporaryDirectory(prefix="packed-config-test-") as root:
            task = self._fixture_task(Path(root))
            path = task / "config.json"
            path.write_text(json.dumps(self.config))
            self.assertEqual(probe._load_config(path)[0], self.config)
            for mutation in mutations:
                with self.subTest(mutation=mutation):
                    config = {**self.config, **mutation}
                    path.write_text(json.dumps(config))
                    with self.assertRaises(ValueError):
                        probe._load_config(path)

    def test_single_draw_shared_prefixes_and_one_pool_clone_per_forward_mock(self):
        torch, backend, cases, config = self._produced()
        self.assertEqual(len(torch.draws), 6)
        self.assertEqual(torch.draws[1][1][1], max(config["sequence_lengths"]))
        self.assertEqual(len(backend.calls), 10)
        states = [arguments["ssm_states"] for arguments, _ in backend.calls]
        self.assertEqual(len({id(state) for state in states}), 10)
        for arguments, initial_before in backend.calls:
            self.assertIsNotNone(arguments["query_start_loc"])
            self.assertEqual(arguments["query_start_loc"].dtype, torch.int32)
            self.assertEqual(arguments["query_start_loc"].values.tolist(), [0, arguments["q"].shape[1]])
            self.assertTrue(arguments["inplace_update"])
            np.testing.assert_array_equal(initial_before, cases[0]["initial"].values)
            self.assertFalse(np.shares_memory(arguments["ssm_states"].values, cases[0]["initial"].values))
        for name in cases[0]["inputs"]:
            self.assertTrue(np.shares_memory(cases[0]["inputs"][name].values, cases[1]["inputs"][name].values))
        self.assertFalse(torch.inspection_allowed)

    def test_equal_length_rng_order_remains_separate_mock(self):
        torch, backend, cases, config = self._produced(self._small_config("equal_length"))
        self.assertEqual(len(torch.draws), 11)
        self.assertEqual([draw[1][1] for draw in torch.draws[1::5]], config["sequence_lengths"])
        self.assertTrue(all(arguments["query_start_loc"] is None for arguments, _ in backend.calls))
        self.assertFalse(np.shares_memory(cases[0]["inputs"]["q"].values, cases[1]["inputs"]["q"].values))

    def test_all_numeric_comparisons_are_post_producer_and_remain_mock(self):
        torch, backend, cases, config = self._produced()
        report = {"checks": {}, "failed_checks": [], "cuda_semantics": "UNVERIFIED"}
        torch.cuda.synchronize()
        probe._inspect(torch, config, cases, Path("/worker-local/mock"), report)
        self.assertEqual(report["failed_checks"], [])
        self.assertEqual(report["cuda_semantics"], "UNVERIFIED")
        self.assertEqual(len(report["packed_native_calls"]), len(backend.calls))
        cross = report["cross_length"][0]
        self.assertEqual(cross["comparison_prefix_tokens"], config["comparison_prefix_tokens"])
        self.assertEqual(cross["comparisons"]["core_attn_out_common_prefix"]["elements"], 61 * 2 * 3)
        self.assertEqual(set(cross["comparisons"]), {"same_q_prefix", "same_k_prefix", "same_v_prefix", "same_g_prefix",
                                                     "same_beta_prefix", "same_initial_pool", "core_attn_out_common_prefix",
                                                     "common_h_rows", "selected_fp32_chunk_1", "selected_fp32_chunk_2"})
        self.assertTrue(any("native_prefix_128" in key for key in report["checks"]))
        self.assertEqual(torch.saved, [Path("/worker-local/mock/tensors.pt")])

    def test_cross_length_comparisons_detect_changed_values_mock(self):
        for target in ("output", "h", "snapshot", "input", "initial"):
            with self.subTest(target=target):
                torch, _, cases, config = self._produced()
                if target in ("output", "h"):
                    cases[1]["ordinary"][target].values.flat[1] += 1
                elif target == "snapshot":
                    cases[1]["tracked"][1]["snapshot"].values.flat[1] += 1
                elif target == "input":
                    cases[1]["inputs"]["q"] = cases[1]["inputs"]["q"].clone()
                    cases[1]["inputs"]["q"].values.flat[1] += 1
                else:
                    cases[1]["initial"] = cases[1]["initial"].clone()
                    cases[1]["initial"].values.flat[1] += 1
                torch.cuda.synchronize()
                report = {"checks": {}, "failed_checks": [], "cuda_semantics": "UNVERIFIED"}
                probe._inspect_packed(torch, config, cases, report)
                expected = {"output": "core_attn_out_common_prefix", "h": "common_h_rows",
                            "snapshot": "selected_fp32_chunk_2", "input": "same_q_prefix", "initial": "same_initial_pool"}[target]
                self.assertTrue(any(key.endswith("/" + expected) for key in report["failed_checks"]))
                self.assertEqual(report["cuda_semantics"], "UNVERIFIED")

    def test_actual_single_request_specialization_source_binding_only(self):
        if not _SOURCE.is_dir():
            self.skipTest("Retained C3 native source is unavailable; no substitute native claim")
        for variant in ("A", "B"):
            config = json.loads((_TASK / f"mamba_snapshot_packed_prefix_{variant}_config.json").read_text())
            for length in config["sequence_lengths"]:
                with self.subTest(variant=variant, length=length):
                    launch, output, cu, snapshot, positions = _native_binding(config, length)
                    self.assertIs(launch["cu_seqlens"], cu)
                    self.assertTrue(launch["IS_VARLEN"])
                    self.assertTrue(launch["INPLACE_UPDATE"])
                    self.assertTrue(launch["TRACK_STATE"])
                    self.assertIs(launch["track_state"], snapshot)
                    self.assertIs(launch["track_chunk_idx"], positions)
                    self.assertEqual(launch["initial_state_indices"].values, [2])
                    self.assertEqual(launch["h"].shape, (1, math.ceil(length / 64), config["value_heads"], 128, 128))
                    self.assertEqual((launch["Hg"], launch["H"], launch["K"], launch["V"]),
                                     (4, config["value_heads"], 128, 128))
                    self.assertEqual(output[1], None)


if __name__ == "__main__":
    unittest.main()
