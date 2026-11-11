"""Replay retained CPU metadata at the actual context/callback seam; no GPU claim."""

import argparse
import json
import resource
import runpy
import time
import traceback
from pathlib import Path
from types import SimpleNamespace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair", choices=("A", "B"), default="A")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
    started = time.monotonic()
    task = Path(__file__).resolve().parents[2]
    attempt = task / "evidence/teacher-scoring-kv-coherence-probe-20261111/native" / args.pair / f"admission-{args.pair}-r2"
    startup = json.loads((attempt / "server_info.json").read_text())["get_server_info"]["internal_states"][0]
    rows = startup["mamba_runtime_metadata"]["rows"]
    null_row = next(row for row in rows if row[1] == "kv_store_stream"
                    and any(dict(row[2])[key] is None for key in ("rids", "prefix_lens", "extend_lens")))
    business = json.loads((attempt / "runtime_metadata.json").read_text())["server_info"]["internal_states"][0]
    valid_row = next(row for row in business["mamba_runtime_metadata"]["rows"] if row[1] == "kv_store_stream"
                     and all(dict(row[2])[key] is not None for key in ("rids", "prefix_lens", "extend_lens")))
    runtime = runpy.run_path(str(attempt / "kv_coherence_source_preflight/after/srt/kv_coherence.py"))
    context = runpy.run_path(str(attempt / "kv_store_stream_source_preflight/after/srt/model_executor/forward_context.py"))
    store = (attempt / "kv_coherence_source_preflight/after/kernels/ops/kvcache/kvcache.py").read_text()
    binding = next(line.strip() for line in store.splitlines() if line.strip().startswith("_kv_batch = "))
    observe = runtime["observe"]
    collector = runtime["Collector"].__new__(runtime["Collector"])
    collector.start, collector.end = runtime["WINDOW_START"], runtime["WINDOW_END"]
    collector.by_rid, collector.errors, collector.pending_cpp = {}, [], {}
    observe.__globals__["_collector"] = collector

    def invoke(row):
        fields = dict(row[2])
        batch = SimpleNamespace(rids=fields["rids"], extend_prefix_lens_cpu=fields["prefix_lens"],
                                extend_seq_lens_cpu=fields["extend_lens"], moe_num_token_non_padded=lambda: None)
        control = context["ForwardContext"](attn_backend=None)
        with context["forward_context"](control, forward_batch=batch):
            scope = {name: context[name] for name in ("get_forward_context", "has_forward_context")}
            exec(binding, scope)
            assert scope["_kv_batch"] is batch
            observe("note_cpp", scope["_kv_batch"], None, None, None,
                    fields["native_actual_stream"], fields["torch_current_raw_stream"])
            observe("fresh", None, 0, None, scope["_kv_batch"], "cpp")
        assert not context["has_forward_context"]()
        return batch

    assert not context["has_forward_context"]()
    absent = {name: context[name] for name in ("get_forward_context", "has_forward_context")}
    exec(binding, absent)
    assert absent["_kv_batch"] is None
    observe("note_cpp", absent["_kv_batch"], None, None, None, None, None)
    observe("fresh", None, 0, None, absent["_kv_batch"], "cpp")
    invoke(valid_row)
    assert collector.errors == [], collector.errors
    batch = invoke(null_row)
    try:
        collector._targets(batch)
    except TypeError as error:
        null_site = [{"function": frame.name, "line": frame.lineno, "code": frame.line}
                     for frame in traceback.extract_tb(error.__traceback__)]
    else:
        null_site = []
    print(json.dumps({"task_id": "profile-kv-coherence-batch-metadata-rca-20261111",
                      "scope": "CPU_METADATA_REPLAY_ONLY", "pair": args.pair,
                      "process_id": startup["kv_coherence"]["process_id"],
                      "null_wit_seq": null_row[0], "valid_wit_seq": valid_row[0],
                      "recorded_null_fields": {key: dict(null_row[2])[key]
                                               for key in ("rids", "prefix_lens", "extend_lens")},
                      "absent_context_and_valid_metadata_pass": True,
                      "errors": collector.errors, "null_site": null_site,
                      "elapsed_seconds": round(time.monotonic() - started, 3)}, indent=2))
    assert collector.errors == [], "RED: valid published native batch with missing host lens poisons global diagnostic errors"


if __name__ == "__main__":
    main()
