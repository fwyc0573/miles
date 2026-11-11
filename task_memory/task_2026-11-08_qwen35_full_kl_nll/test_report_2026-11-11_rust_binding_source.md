## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Primary replay accepted retained-source/provenance verification only; archive the source evidence while keeping the original Rust observer and numeric acceptance pending. |
| 2026-11-11 | Verify retained Rust candidates, production binding identity and zero-GPU terminal evidence; preserve unresolved binary source commit and formal hold. |

# Rust binding source verification

TaskID: `profile-rust-cache-source-provenance-20261111`. Primary accepts the retained-source/provenance result after replaying the report and reconciling every input hash. Scope: source verification and archival only; no engine source edits, compilation, numeric capture or original pre-split observer acceptance. The verification agent made no platform calls; the primary separately collected the filtered platform receipt.
Source root: `evidence/native-rust-source-20261111/`; archive: `exp-1111-124522-553024/`. Machine results: [source-verification.json](evidence/native-rust-source-20261111/source-verification.json).

## Observed results

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| New retained files | 621 distinct paths; every SHA-256 and size matches | 621/621; 13,491,926 bytes; 567 `.rs` rows | PASS |
| Original Python/Cython/source archive | 5501 paths; unchanged hashes, size and image/version | 5501/5501; 79,478,292 bytes; zero `.rs` rows | PASS |
| Checkout versus both Git candidates | Same selected Rust paths and bytes | 206 paths / 189 `.rs` / 4,494,866 bytes each; missing/extra/changed = 0 | PASS |
| Selected radix crate inputs | Cargo manifests/locks/header and referenced Rust files available | 22 files / 19 `.rs`; 8 explicit Rust path references resolve | PASS |
| Distribution identity | Original version, editable origin and generated `_version.py` agree | `0.5.24.dev80+g056f871`; editable `/sgl-workspace/sglang/python` | PASS |
| Production binding load | Bundled production module; CUDA remains uninitialized | `mem_cache`, bundled=true; Python 3.12.16 / Torch 2.14.1+cu130 / CXX11=true / CUDA initialized=false | PASS, load only |
| Resource and terminal evidence | Personal creator; pinned image/local NFS; GPU=0; successful business/container termination | cpu2 / 8000Mi / GPU0; one replica Succeeded / Completed / exit0 / restart0 / matching owner UID | PASS |
| Native binary source commit | Direct evidence tying binary to one source commit | No direct stamp; module version=null | UNVERIFIED |

The loaded module is `sglang.srt.mem_cache.rust_tree_core.mem_cache`, at `/sgl-workspace/sglang/python/sglang/srt/mem_cache/rust_tree_core/mem_cache.cpython-312-x86_64-linux-gnu.so`.
The worker recorded 3,399,272 bytes, SHA-256 `2c1e54965c8139358df1ef2a7751620c339ad1ff4988cee54cc35467a8b90f6c`, GNU build ID `849599cc340045a6ed34eb52de0fdc2a3ff9a236`; the `.so` was not copied or rehashed locally.
Checkout HEAD `056f871a7ee8b4573832049011f0fdf52589cfd8` and environment label `297e54fd105e974cdf401e5b4d20253a22c16f90` are available candidate Git objects in the worker receipt. Scoped Git status is empty; the last recorded Rust change is `297e54fd`. All three selected source maps have SHA-256 `1062188e9d6414a7d4921dfdda1b0b55747fd25ebc06037a9d07d3fea0da3229`.
Crate `Cargo.toml:1-17,19-21,34-40` declares `sglang-radix-tree` 0.1.0, library `mem_cache`, cdylib, production module and `python-extension` feature. Root `rust/Cargo.toml:12-17` excludes and separately registers this isolated workspace. Its own `Cargo.lock` and `torch_compat.h` are retained; lock declarations include pyo3 0.29.2 and tch/torch-sys 0.24.0, not measured compiled dependency versions.
Primary-owned [platform-verification.json](evidence/native-rust-source-20261111/platform-verification.json) reconciles submission and terminal receipts: UID `b85fb8fd-6418-4a0b-97d0-876abf864315`, creator `i-fengyicheng`, image165 and mount `100.96.128.195:/data/ycfeng:/data/ycfeng`; container finished `2026-11-11T04:46:41Z`, job finished `04:46:43Z`. This agent read only the filtered artifact, without SDK/API/auth/SSH access.

## Interpretation and limits

- Python/base labels differ, but the selected Rust sources do not. Paths, compiler strings, environment and build IDs cannot identify the binary's source commit; absence of embedded paths is neutral. The previous proposed path-based inference is withdrawn.
- `.comment` reports rustc 1.99.1 / `58cf8f9c3`, matching the directly inspected installed compiler. `rust/rust-toolchain.toml` declares 1.92; the worker queried installed cargo/rustc binaries directly, without rustup downloads. Neither fact attests source commit, build features or reproducible binary equivalence.
- Worker selection was `.rs/.toml/.lock/.h/.hpp/.cpp/.cc` plus rust-toolchain names (`worker.py:32-34,57-71,94-107`). Original 5501 selection excluded `.rs` and searched only the Python package. Its missing Rust files did not mean worker absence.
- The actual radix workspace has no retained `build.rs`, explicit `build=`/build dependencies, literal include macros, path dependencies or metadata `source-inputs`; all referenced Rust paths and the declared compatibility header are retained. No concrete missing input was found for this isolated crate's source inspection.
- The wider selected Rust tree lacks five JSON fixtures referenced by other crates: `sglang-api-types/testdata/json_parity.json` and `sglang-server/testdata/{frame_metadata,tokenizer_metrics,load_snapshot,prometheus_multiprocess}.json`. These are not selected radix dependencies. Equality of the 206 selected files is not equality of the loader's all-file source digest, nor a hermetic dependency/vendor/build archive; do not turn unrelated Markdown/fixtures into a radix observer gate.
- Production module loading and the declared source ABI permit the separately owned walker analysis, not native pre-split/FULL tensor/stream-readiness acceptance. No KV capture, runtime parity experiment or new Cargo build was performed. Existing bounded CPP/WIT acceptance and warm FAIL remain unchanged; formal04/05 HOLD.

## Commands and reproducible local check

Local: `python3 -B` (Python 3.10.6, GCC 11.3.0), standard library only, no Torch import or conda change. Worker: pinned `/opt/sglang/bin/python3 -B` (3.12.16), `timeout 600`, exact inline collector/arguments retained in `submission.json.command`; collector source is `worker.py` (SHA in machine results). Native git/readelf/direct-toolchain commands are retained verbatim in `source.json`.
From the repository root, replay the following block with `python3 -B -`; it reads artifacts and prints results without writing files:

```python
import ast, hashlib, json, re
from pathlib import Path
task = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
root = task / 'evidence/native-rust-source-20261111'
base = root / 'exp-1111-124522-553024'
d = json.loads((base / 'source.json').read_text())
old = task / 'evidence/native-sglang-cache-source-20261111/exp-1111-102145-988437'
o = json.loads((old / 'source.json').read_text())
def sha(content):
    return hashlib.sha256(content).hexdigest()
def verify(rows, directory):
    result = {}
    for row in rows:
        content = (directory / row['path']).read_bytes()
        value = {'bytes': len(content), 'sha256': sha(content)}
        assert row['path'] not in result
        assert value == {key: row[key] for key in value}, row['path']
        result[row['path']] = value
    return result
def fingerprint(rows):
    return sha(json.dumps(rows, sort_keys=True, separators=(',', ':')).encode())
files = verify(d['files'], base)
original = verify(o['files'], old / 'source')
assert len(files) == 621 and len(original) == 5501
assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()} == set(files) | {'source.json'}
revisions = [candidate['revision'] for candidate in d['git_source_candidates']]
assert len(revisions) == 2 and all(c['available'] for c in d['git_source_candidates'])
sets = [{p[len(prefix):]: value for p, value in files.items() if p.startswith(prefix)}
        for prefix in ['checkout/rust/'] + ['git/' + rev + '/rust/' for rev in revisions]]
assert sets[0] == sets[1] == sets[2] and len(sets[0]) == 206
for c in d['git_source_candidates']:
    assert set(c['files']) == {p for p in files if p.startswith('git/' + c['revision'] + '/')}
assert d['git_head']['returncode'] == d['git_rust_status']['returncode'] == d['git_rust_last_change']['returncode'] == 0
assert d['git_head']['stdout'].strip() == revisions[0] and d['git_rust_status']['stdout'] == ''
assert d['git_rust_last_change']['stdout'].splitlines()[0] == revisions[1]
assert d['environment']['SGLANG_BUILD_COMMIT'] == revisions[1]
radix = {p[len('sglang-radix-tree/'):]: v for p, v in sets[0].items() if p.startswith('sglang-radix-tree/')}
crate = base / 'checkout/rust/sglang-radix-tree'
manifest = (crate / 'Cargo.toml').read_text()
assert len(radix) == 22 and (crate / 'Cargo.lock').is_file() and (crate / 'torch_compat.h').is_file()
assert 'python-module = "' + d['loaded_binding']['module'] + '"' in manifest
assert '[workspace]' in manifest and not re.search(r'(?m)^\s*(build\s*=|source-inputs\s*=|\[build-dependencies\])', manifest)
assert not (crate / 'build.rs').exists()
missing = []
for path in (base / 'checkout/rust').rglob('*.rs'):
    text = path.read_text()
    references = re.findall(r'include(?:_str|_bytes)?!\s*\(\s*"([^"]+)"', text)
    if path.is_relative_to(crate):
        assert not references
        assert all((path.parent / ref).is_file() for ref in re.findall(r'#\[path\s*=\s*"([^"]+)"\]', text))
    for ref in references:
        target = (path.parent / ref).resolve()
        if not target.is_file(): missing.append(target.relative_to((base / 'checkout/rust').resolve()).as_posix())
assert len(missing) == 5 and all(not p.startswith('sglang-radix-tree/') for p in missing)
metadata = (base / 'distribution/METADATA').read_text()
url = json.loads((base / 'distribution/direct_url.json').read_text())
assert 'Version: ' + d['sglang_version'] in metadata and url == {'dir_info': {'editable': True}, 'url': 'file://' + d['checkout'] + '/python'}
values = {target.id: node.value.value for node in ast.parse((old / 'source/_version.py').read_text()).body
          if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) for target in node.targets if isinstance(target, ast.Name)}
assert d['sglang_version'] == o['sglang_version'] == values['__version__'] and d['image'] == o['image'] and d['package'] == o['package']
assert values['__commit_id__'] == 'g' + revisions[0][:7] and '.rs' not in o['source_suffixes']
s, t, p = [json.loads((root / name).read_text()) for name in ['submission.json', 'terminal.json', 'platform-verification.json']]
assert s['job'] == t['job'] == p['job'] == base.name and s['creator'] == t['creator'] == p['creator'] == 'i-fengyicheng'
assert t['native_execution_succeeded'] and t['status'] == p['status'] and p['status']['phase'] == 'Succeeded'
assert len(p['replicas']) == 1 and len(p['tasks']['source']['containers']) == 1
c, replica = p['tasks']['source']['containers'][0], p['replicas'][0]
assert len(replica['containers']) == 1
container = replica['containers'][0]; terminated = container['state']['terminated']
assert c['image'] == s['image'] == d['image'] and p['tasks']['source']['source_mount'] == s['source_mount']
assert c['limits'] == {'cpu': '2', 'memory': '8000Mi', 'nvidia.com/gpu': '0'} and s['requested_gpus'] == d['requested_gpus'] == 0
assert replica['owner_uid_matches_job'] and replica['phase'] == 'Succeeded' and container['restart_count'] == 0
assert terminated['exitCode'] == 0 and terminated['reason'] == 'Completed'
assert sha((root / 'worker.py').read_bytes()) == s['worker_source_sha256']
binding = d['loaded_binding']; assert binding['bundled'] and not binding['cuda_initialized'] and d['environment']['SGLANG_RUST_BUILD_MODE'] == 'never'
assert binding['origin'] == d['package'] + '/srt/mem_cache/rust_tree_core/mem_cache' + d['extension_suffix']
assert d['binary_source_commit'] == 'UNVERIFIED' and binding['module_version'] is None and not any(p.endswith('.so') for p in files)
result = {'files': len(files), 'rust_rows': sum(p.endswith('.rs') for p in files), 'source_bytes': sum(v['bytes'] for v in files.values()),
          'original_files': len(original), 'original_bytes': sum(v['bytes'] for v in original.values()), 'artifact_map_sha256': fingerprint(files),
          'workspace_files': len(sets[0]), 'workspace_map_sha256': fingerprint(sets[0]), 'radix_files': len(radix), 'radix_map_sha256': fingerprint(radix),
          'candidate_revisions': revisions, 'all_selected_sources_equal': True, 'other_crate_missing_includes': sorted(missing), 'platform': 'PASS', 'binary_source_commit': d['binary_source_commit']}
print(json.dumps(result, indent=2))
```

Executed local replay command (the retained block and `replay_expected` matched exactly, PASS):

```bash
python3 -B - <<'PY'
from pathlib import Path
import json
report = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/test_report_2026-11-11_rust_binding_source.md')
scope = {}; exec(compile(report.read_text().split('```python\n', 1)[1].split('\n```', 1)[0], '<retained-source-replay>', 'exec'), scope)
assert scope['result'] == json.loads((scope['root'] / 'source-verification.json').read_text())['replay_expected']
PY
```

Checkpoint: hash/size verification and candidate comparison PASS; deliver the two owned artifacts, then let the other analyzer qualify the actual walker/seam independently. D1–D7 CLEAR in this follow-up; no retry, build or scope expansion. S5: parent `plan.md:136`, `tickets/04-a-full.md:49-51` and `tickets/05-b-full.md:46-48` still describe old Running/pending WIT status, unlike `progress.md:194`; primary owns reconciliation, not this task. No other scope/criteria defect identified; formal HOLD and existing WIT acceptance are not reset.
