## Modification History

| Date | Change |
| --- | --- |
| 2026-11-10 | Retain the exact substantive local command bodies used for corrected-A prefix verification. |

# Local command receipts

Working directory: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. These are recorded one-off CPU invocations, not new persistent Python test machinery. Generated artifacts use exclusive creation; do not rerun into the same output filenames.

## Scope readiness attempts

```bash
timeout 60s systemd-run --user --scope -p MemoryMax=30G /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c 'import pathlib,json; print(json.dumps({"memory_limit_bytes":pathlib.Path("/sys/fs/cgroup/memory" + pathlib.Path("/proc/self/cgroup").read_text().split("10:memory:")[1].splitlines()[0] + "/memory.limit_in_bytes").read_text().strip()}))'
```

Observed exit1: `Failed to connect to bus: No such file or directory`.

```bash
timeout 60s systemd-run --scope -p MemoryMax=30G /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B -c 'print("CPU scope readiness")'
```

Observed exit1: `Failed to start transient scope unit: Interactive authentication required.` No authentication or privilege escalation was attempted. Substantive checks below use a process address-space limit instead.

## Inspector, original-file rebuild, reporter and input preservation

```bash
timeout 60s env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import hashlib, json, os, platform, resource, sys, time
from pathlib import Path
from tests.manual.agent_opd.distillation_profile import DistillationProfile
from tests.manual.agent_opd.distillation_report import build_report, write_report
from tests.manual.agent_opd.inspect_distillation_run import inspect_run
resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
started = time.perf_counter()
root = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/formal-H200-A-r2-first-two-20261110')
training = root / 'training'
retention = json.loads((root / 'retention.json').read_bytes())
def digest(path):
    with path.open('rb') as stream:
        sha = hashlib.file_digest(stream, 'sha256').hexdigest()
    return {'bytes': path.stat().st_size, 'sha256': sha}
before = {name: digest(root / name) for name in retention['files']}
retention_before = digest(root / 'retention.json')
assert before == retention['files'], 'Retained inputs differ from retention.json'
receipt, profile = inspect_run(training, job='exp-1110-165312-132926', expected_updates=200)
assert receipt['native']['successful_updates'] == 2
assert receipt['profile']['verified_updates'] == 2
assert receipt['native']['complete'] is False and receipt['profile']['complete'] is False
assert profile is not None
rebuilt = DistillationProfile.rebuild(training / 'distillation_profile')
observation_count = sum(profile.update(u).turns for u in (1, 2))
assert rebuilt.summary() == profile.summary()
assert all(rebuilt.observation(i) == profile.observation(i) for i in range(observation_count))
with (root / 'inspection-prefix.json').open('x', encoding='utf-8') as stream:
    stream.write(json.dumps(receipt, indent=2, allow_nan=False) + '\n')
report = build_report(receipt, profile, cell='A/full', limitations=(
    'Actual exact retained corrected-A snapshots through successful update 2, captured 2026-11-10T09:54:56.550810+00:00; not synthetic.',
    'Expected formal budget remains 200. Training was active at retention; no terminal receipt is supplied, so no terminal success or native offload repair verdict is claimed.',
    'Historical failed A exp-1110-140032-491115 (1/200) is independent and is not joined to this attempt.',
))
outputs = write_report(report, output_prefix=root / 'profile-report-prefix')
checks = {
    'task_id': 'profile-corrected-A-first-two-profile-20261110',
    'job': retention['job'], 'retention_observed_at': retention['observed_at'],
    'input_fingerprints_before': before, 'retention_fingerprint_before': retention_before,
    'input_retention_manifest_match': True,
    'direct_original_file_rebuild': {'summary_exact_equal': True, 'observations_exact_equal': True, 'updates': rebuilt.latest_update, 'observations': observation_count},
    'inspection': receipt,
    'report_outputs': [str(path) for path in outputs],
    'environment': {'executable':sys.executable, 'python':sys.version, 'platform':platform.platform(), 'conda_prefix':os.environ.get('CONDA_PREFIX'), 'cwd':str(Path.cwd()), 'tmpdir':os.environ.get('TMPDIR'), 'RLIMIT_AS_bytes':resource.getrlimit(resource.RLIMIT_AS)},
    'elapsed_seconds':time.perf_counter() - started,
    'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
}
checks['input_fingerprints_after'] = {name: digest(root / name) for name in retention['files']}
checks['retention_fingerprint_after'] = digest(root / 'retention.json')
checks['input_bytes_preserved'] = (checks['input_fingerprints_after'] == before and checks['retention_fingerprint_after'] == retention_before)
assert checks['input_bytes_preserved']
checks['total_raw_bytes'] = sum(item['bytes'] for item in before.values())
with (root / 'prefix-verification.json').open('x', encoding='utf-8') as stream:
    stream.write(json.dumps(checks, indent=2, allow_nan=False) + '\n')
print(json.dumps({'verdict':'PASS', 'raw_bytes':checks['total_raw_bytes'], 'native':receipt['native'], 'profile':receipt['profile'], 'original_rebuild':checks['direct_original_file_rebuild'], 'report_disposition':report['disposition'], 'report_macro':report['macro'], 'report_conversations':report['conversations'], 'elapsed_seconds':checks['elapsed_seconds'], 'peak_rss_kib':checks['peak_rss_kib'], 'outputs':['inspection-prefix.json','prefix-verification.json',*[path.name for path in outputs]]}, indent=2, allow_nan=False))
PY
```

Observed exit0/PASS: prefix2, original512 observations exactly reproduce; both formal complete flags false. Elapsed3.173605169169605s, peak RSS39,708KiB.

## Streamed bank counts, original masks, errors and all-sample versions

```bash
timeout 60s env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import collections, hashlib, json, math, resource, time
from datetime import datetime, timezone
from pathlib import Path
from tests.manual.agent_opd.distillation_profile import DistillationProfile
resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
began = time.perf_counter()
root = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/formal-H200-A-r2-first-two-20261110')
training = root / 'training'
load = lambda path: [json.loads(line) for line in path.read_text().splitlines()]
native = load(training / 'updates.jsonl')
attempts = load(training / 'optimizer_attempts.jsonl')
summaries = load(training / 'distillation_profile/updates.jsonl')
observations = load(training / 'distillation_profile/observations.jsonl')
profile = DistillationProfile.rebuild(training / 'distillation_profile')
assert len(native) == len(attempts) == len(summaries) == len(observations) == 2
assert all({k:v for k,v in row.items() if k != 'update'} == attempt for row,attempt in zip(native,attempts,strict=True))
result = {'task_id':'profile-corrected-A-first-two-profile-20261110', 'job':'exp-1110-165312-132926', 'optimizer_attempts_exact_match_successful_updates_minus_update_field':True, 'updates':[], 'banks':[]}
uids_by_bank = []; identities_by_bank = []
for n, summary, observation in zip(native,summaries,observations,strict=True):
    update_id = n['update']; rows = observation['rows']
    row = profile.update(update_id)
    metrics = {}
    for metric, native_field, sum_field in (('rkl','kl_before_tis','rkl_sum'), ('nll','nll_before_tis','nll_sum')):
        predicted = getattr(row,metric); actual = n[native_field]
        absolute = abs(predicted - actual)
        relative = absolute / abs(actual) if actual != 0 else None
        metrics[metric] = {'profile_recomputed':predicted, 'native':actual, 'absolute_error':absolute, 'relative_error':relative, 'relative_error_percent':relative * 100 if relative is not None else None, 'profile_sum':getattr(row,sum_field), 'native_numerator':n[native_field + '_numerator'], 'native_denominator':n[native_field + '_denominator'], 'persisted_macro_exact_equal':summary[metric] == predicted, 'numerator_exact_equal':getattr(row,sum_field) == n[native_field + '_numerator'], 'pass_math_isclose':math.isclose(predicted,actual)}
    result['updates'].append({'update_id':update_id, 'bank':n['bank'], 'bank_visit':n['bank_visit'], 'actual_turns':n['actual_turns'], 'original_tokens':n['original_tokens'], 'surviving_tokens':n['surviving_tokens'], 'tis_retention':n['tis_retention'], 'current_weight_version':n['current_weight_version'], 'native_attempted_count':n['native_attempted_count'], 'native_skipped_count':n['native_skipped_count'], 'replay_number_counts':dict(collections.Counter(str(r[3]) for r in rows)), 'new_conversations':len(observation['new_conversations']), 'finished_conversations':observation['finished'], 'metrics':metrics})
    per_uid = {r[0]:r for r in rows}
    sources = {}; version_sets = collections.Counter(); decode_versions = collections.Counter(); prefill_versions = collections.Counter(); decode_tokens = collections.Counter(); prefill_tokens = collections.Counter(); calls_hist = collections.Counter(); event_counts = collections.Counter()
    samples_with_versions = samples_with_prefill = aligned_teacher = matching_acquisition = 0
    prompt_counts = []; response_counts = []; target_counts = []; finished_times = []; sample_small_keys = set(); raw_source_policy = set(); original_epochs = set()
    with (training / f'bank_{n["bank"]}.jsonl').open() as stream:
        for line in stream:
            event = json.loads(line); event_counts[event['event']] += 1
            if event['event'] == 'acquisition_start':
                start = event
                continue
            if event['event'] == 'acquisition_sealed':
                sealed = event
                continue
            assert event['event'] == 'slot_finished' and event['status'] == 'completed' and event['error'] is None
            sample = event['sample']; source = sample['metadata']['source']; uid = source['uid']; mask = sample['loss_mask']; observed = per_uid[uid]
            assert source['group_id'] == profile.conversation(observed[1]).group_id and source['assistant_turn_ordinal'] == observed[2]
            assert sum(mask) == observed[6] and len(mask) == sample['response_length'] and set(mask) <= {0,1}
            assert sample['train_metadata']['source_uid'] == uid and sample['train_metadata']['source_group_id'] == source['group_id']
            sources[event['slot']] = (uid, source['group_id'],source['assistant_turn_ordinal'])
            calls = sample['weight_versions']; calls_hist[str(len(calls))] += 1
            versions = set(); has_prefill = False
            for call in calls:
                assert call['output_start'] == len(sample['tokens']) - sample['response_length']
                for kind, version_counts, token_counts, begin, end in (('spans',decode_versions,decode_tokens,call['output_start'],len(sample['tokens'])),('prefill_spans',prefill_versions,prefill_tokens,0,call['prompt_tokens'])):
                    cursor = begin
                    for span in call[kind]:
                        assert span['abs_start'] == cursor and span['abs_end'] > cursor
                        versions.add(span['version']); version_counts[span['version']] += 1; token_counts[span['version']] += span['abs_end'] - span['abs_start']; cursor = span['abs_end']
                    assert cursor == end
                has_prefill = has_prefill or bool(call['prefill_spans'])
            version_sets[','.join(sorted(versions))] += 1
            samples_with_versions += bool(calls); samples_with_prefill += has_prefill
            assert versions == {str(n['current_weight_version'])}
            teacher = sample['metadata']['teacher_scoring']
            aligned_teacher += teacher['identity'] == n['teacher_identity'] and teacher['token_ids_match'] is True and teacher['scored_tokens'] == sample['response_length']
            acq = sample['metadata']['swe_acquisition']
            matching_acquisition += acq == {'bank':n['bank'],'slot':event['slot'],'started_at':start['started_at'],'deadline_at':start['deadline_at']}
            prompt_counts.append(len(sample['tokens']) - sample['response_length']); response_counts.append(sample['response_length']); target_counts.append(sum(mask)); finished_times.append(event['ended_at'])
            sample_small_keys.update(sample['metadata']); raw_source_policy.add(source['target_policy']); original_epochs.add(source['epoch'])
    assert len(sources) == len(per_uid) == len(start['slots']) == sealed['actual_turns'] == 256
    assert set(uid for uid,_,_ in sources.values()) == set(per_uid)
    assert sealed['membership'] == list(range(256)) and sealed['missing_slots'] == sealed['pending_slots'] == []
    assert all(sources[entry['slot']][0] == entry['source_uid'] for entry in start['slots'])
    assert sum(target_counts) == n['original_tokens']
    ordered = [sources[i] for i in range(256)]; by_group = collections.defaultdict(list)
    for uid,group,turn in ordered: by_group[group].append(turn)
    assert len(by_group) == 32 and all(turns == sorted(turns) and len(turns) == len(set(turns)) == 8 for turns in by_group.values())
    uids_by_bank.append({uid for uid,_,_ in ordered}); identities_by_bank.append({(group,turn) for _,group,turn in ordered})
    result['banks'].append({'bank':n['bank'], 'event_counts':dict(event_counts), 'candidate_slots':len(start['slots']), 'actual_turns':sealed['actual_turns'], 'missing_slots':sealed['missing_slots'], 'pending_slots':sealed['pending_slots'], 'started_at':start['started_at'], 'sealed_at':sealed['ended_at'], 'started_at_utc':datetime.fromtimestamp(start['started_at'],timezone.utc).isoformat(), 'sealed_at_utc':datetime.fromtimestamp(sealed['ended_at'],timezone.utc).isoformat(), 'acquisition_seconds':sealed['ended_at'] - start['started_at'], 'deadline_at':start['deadline_at'], 'deadline_seconds_from_start':start['deadline_at'] - start['started_at'], 'sealed_before_deadline':sealed['ended_at'] <= start['deadline_at'], 'elapsed_seconds_min_max': [min(finished_times)-start['started_at'], max(finished_times)-start['started_at']], 'native_measurement_timestamp':n['timestamp'], 'acquisition_start_to_native_measurement_seconds':n['timestamp']-start['started_at'], 'sealed_to_native_measurement_seconds':n['timestamp']-sealed['ended_at'], 'target_tokens':sum(target_counts), 'response_tokens':sum(response_counts), 'prompt_tokens_min_max':[min(prompt_counts),max(prompt_counts)], 'response_tokens_min_max':[min(response_counts),max(response_counts)], 'all_original_masks_all_ones':sum(target_counts) == sum(response_counts), 'conversations':len(by_group), 'turns_per_conversation_histogram':dict(collections.Counter(str(len(turns)) for turns in by_group.values())), 'per_conversation_training_turn_range':sorted(set((min(turns),max(turns)) for turns in by_group.values())), 'sample_weight_versions_present':samples_with_versions, 'sample_prefill_spans_present':samples_with_prefill, 'calls_per_sample_histogram':dict(calls_hist), 'sample_version_set_counts':dict(version_sets), 'decode_span_version_counts':dict(decode_versions), 'prefill_span_version_counts':dict(prefill_versions), 'decode_token_version_counts':dict(decode_tokens), 'prefill_token_version_counts':dict(prefill_tokens), 'native_generation_weight_versions_scope':'metadata of the first native train-data sample only; not a bank-wide aggregate', 'native_first_sample_generation_receipt_exact_match':n['generation_weight_versions'] == next(json.loads(line)['sample']['weight_versions'] for line in (training / f'bank_{n["bank"]}.jsonl').open() if json.loads(line)['event'] == 'slot_finished' and json.loads(line)['slot'] == 0), 'teacher_alignment_metadata_pass_count':aligned_teacher, 'sample_acquisition_metadata_pass_count':matching_acquisition, 'target_policies':sorted(raw_source_policy), 'epochs':sorted(original_epochs), 'per_sample_training_current_weight_version_field_present':False})
result['cross_bank'] = {'distinct_banks_used_once':True, 'uid_intersection_count':len(uids_by_bank[0] & uids_by_bank[1]), 'group_turn_intersection_count':len(identities_by_bank[0] & identities_by_bank[1]), 'union_uid_count':len(uids_by_bank[0] | uids_by_bank[1])}
assert result['cross_bank']['uid_intersection_count'] == result['cross_bank']['group_turn_intersection_count'] == 0
assert all(bank['teacher_alignment_metadata_pass_count'] == bank['sample_acquisition_metadata_pass_count'] == 256 for bank in result['banks'])
result['limits'] = ['Per-sample generation decode/prefill versions are retained in sample.weight_versions, not inferred from bank or update number.', 'Native current_weight_version is the rollout input scalar copied to training metadata; retained pre-materialization bank samples do not contain that scalar.', 'Native record timestamp is taken at before_optimizer and the success receipt is published after_optimizer; derived intervals are not optimizer/scoring duration or ACK completion time.', 'Separate teacher request/stage timings, trainer log-prob/train/offload timings, whole-model checksum equality and terminal success are unverified by these six raw files.', 'B10 and k10 are immature at update2; N8 is already complete and positive for all32 conversations. This is not mature run/trend or200-update evidence.']
result['elapsed_seconds'] = time.perf_counter() - began
result['peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
result['verdict'] = 'PASS'
with (root / 'prefix-measurements.json').open('x',encoding='utf-8') as stream:
    stream.write(json.dumps(result,indent=2,allow_nan=False) + '\n')
print(json.dumps(result,indent=2,allow_nan=False))
PY
```

Observed exit0. Required counts/mask/metric/acquisition/version checks passed, elapsed5.631639575585723s and peak RSS39,224KiB. The `native_first_sample_generation_receipt_exact_match` slot0 check was an unsupported audit assumption and returned false in both banks. Its output remains preserved. The next command resolves that provenance and actually counts scalar presence across all retained samples rather than relying on the earlier fixed false field.

## Focused native generation-receipt provenance and scalar-presence check

```bash
timeout 60s env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import collections, json, resource, time
from pathlib import Path
resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
began = time.perf_counter()
root = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/formal-H200-A-r2-first-two-20261110')
native = [json.loads(line) for line in (root / 'training/updates.jsonl').read_text().splitlines()]
result = {'task_id':'profile-corrected-A-first-two-profile-20261110', 'banks':[]}
for n in native:
    matches = []; checked = 0; current_scalar_count = 0; field_locations = collections.Counter(); slot_zero = None; missing_decode = missing_prefill = 0
    with (root / f'training/bank_{n["bank"]}.jsonl').open() as stream:
        for line in stream:
            row = json.loads(line)
            if row['event'] != 'slot_finished': continue
            checked += 1
            sample = row['sample']; metadata = sample['train_metadata']; calls = sample['weight_versions']
            current_scalar_count += 'current_weight_version' in metadata
            for field in ('current_weight_version','generation_weight_versions'):
                field_locations[field] += field in metadata
            missing_decode += not calls or any(not call['spans'] for call in calls)
            missing_prefill += not calls or any(not call['prefill_spans'] for call in calls)
            if row['slot'] == 0: slot_zero = calls
            if calls == n['generation_weight_versions']:
                source = sample['metadata']['source']
                matches.append({'slot':row['slot'],'source_uid':source['uid'],'group_id':source['group_id'],'assistant_turn_ordinal':source['assistant_turn_ordinal'],'prompt_tokens':len(sample['tokens'])-sample['response_length'],'response_length':sample['response_length']})
    assert checked == 256 and len(matches) == 1 and current_scalar_count == missing_decode == missing_prefill == 0
    result['banks'].append({'bank':n['bank'],'completed_samples_checked':checked,'native_generation_receipt_exact_matches':matches,'native_generation_receipt_match_count':len(matches),'canonical_slot_zero_matches_native_generation_receipt':slot_zero == n['generation_weight_versions'],'per_sample_current_weight_version_count':current_scalar_count,'retained_train_metadata_field_counts':dict(field_locations),'samples_missing_decode_spans':missing_decode,'samples_missing_prefill_spans':missing_prefill,'verdict':'PASS'})
result['provenance'] = {
    'retained_per_sample_generation_fields':'bank_N.jsonl slot_finished.sample.weight_versions[*].spans[*].{version,abs_start,abs_end} and prefill_spans[*].{version,abs_start,abs_end}',
    'serialization_owner':'miles/utils/types.py:23-43,312-318 (WeightVersionsPerCall and Sample.to_dict)',
    'native_metadata_copy':'tests/manual/agent_opd/swe_replay.py:119-137 (CanonicalTrajectory.materialize copies sample.weight_versions to train_metadata.generation_weight_versions)',
    'native_rollout_input_scalar':'tests/manual/agent_opd/swe_replay.py:423-429 (sets train_metadata.current_weight_version from RolloutFnTrainInput.weight_version)',
    'native_single_sample_selector':'tests/manual/agent_opd/swe_training.py:277,302-303 (reads data_iterator[0].rollout_data[metadata][0]; not an aggregate over all samples)',
    'current_training_scalar_evidence_limit':'Only the native receipt scalar0/1 is retained; pre-materialization bank samples lack current_weight_version and generation_weight_versions in train_metadata. The generation span receipts are available for all256 samples in each bank.',
    'initial_comparison_limit':'prefix-measurements.json native_first_sample_generation_receipt_exact_match compares against canonical slot0. Both false values are the observed outcome of that unsupported slot0 assumption, not a native/profile defect. This new receipt checks all actual retained samples and finds one exact matching native-generation receipt per bank. Native train-data order itself is not retained.',
}
result['elapsed_seconds'] = time.perf_counter()-began
result['peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
result['verdict'] = 'PASS'
with (root / 'generation-provenance-verification.json').open('x',encoding='utf-8') as stream:
    stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(result,indent=2,allow_nan=False))
PY
```

Observed exit0/PASS, elapsed2.4980510901659727s and peak RSS32,764KiB. Unique matching native receipts: bank0 slot119, bank1 slot118; every retained sample lacks the materialization-time current scalar, and all samples carry actual generation decode/prefill spans.

## Final delivery and preservation check

The final executed command is appended below with its observed receipt. No raw inputs are staged or committed.

```bash
timeout 60s env PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import hashlib, json, re, resource, time
from pathlib import Path
from tests.manual.agent_opd.distillation_report import render_markdown
resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
began = time.perf_counter()
task = Path('task_memory/task_2026-11-08_qwen35_full_kl_nll')
root = task / 'evidence/formal-H200-A-r2-first-two-20261110'
report_path = task / 'test_report_2026-11-10_corrected_profile_prefix.md'
load = lambda path: json.loads(path.read_bytes())
def digest(path):
    with path.open('rb') as stream:
        sha = hashlib.file_digest(stream,'sha256').hexdigest()
    return {'bytes':path.stat().st_size,'sha256':sha}
retention = load(root / 'retention.json')
verification = load(root / 'prefix-verification.json')
inputs = {name:digest(root / name) for name in retention['files']}
assert inputs == retention['files'] == verification['input_fingerprints_before'] == verification['input_fingerprints_after']
assert digest(root / 'retention.json') == verification['retention_fingerprint_before'] == verification['retention_fingerprint_after']
receipt = load(root / 'inspection-prefix.json')
report = load(root / 'profile-report-prefix.json')
measurements = load(root / 'prefix-measurements.json')
provenance = load(root / 'generation-provenance-verification.json')
assert report['inspection'] == receipt == verification['inspection']
assert receipt['expected_updates'] == 200 and receipt['job'] == 'exp-1110-165312-132926'
assert receipt['native']['successful_updates'] == receipt['profile']['verified_updates'] == 2
assert receipt['native']['complete'] is receipt['profile']['complete'] is False
assert receipt['native']['terminal_phase'] is None and receipt['profile']['missing_pair_ranges'] == [[3,200]]
assert render_markdown(report) == (root / 'profile-report-prefix.md').read_text()
assert verification['direct_original_file_rebuild'] == {'summary_exact_equal':True,'observations_exact_equal':True,'updates':2,'observations':512}
assert len(measurements['updates']) == 2 and [n['bank'] for n in measurements['updates']] == [0,1]
assert all(n['bank_visit'] == 1 and n['replay_number_counts'] == {'0':256} for n in measurements['updates'])
assert all(metric['absolute_error'] == metric['relative_error'] == 0 and metric['persisted_macro_exact_equal'] and metric['numerator_exact_equal'] for n in measurements['updates'] for metric in n['metrics'].values())
assert all(bank['actual_turns'] == 256 and bank['acquisition_seconds'] < 1800 and bank['sealed_before_deadline'] for bank in measurements['banks'])
assert all(bank['sample_version_set_counts'] == {str(bank['bank']):256} for bank in measurements['banks'])
assert [bank['native_generation_receipt_exact_matches'][0]['slot'] for bank in provenance['banks']] == [119,118]
assert all(bank['native_generation_receipt_match_count'] == 1 and bank['per_sample_current_weight_version_count'] == 0 and bank['verdict'] == 'PASS' for bank in provenance['banks'])
text = report_path.read_text()
assert text.startswith('## Modification History')
assert all(str(n['metrics'][metric]['profile_recomputed']) in text for n in measurements['updates'] for metric in ('rkl','nll'))
assert all(str(bank['acquisition_seconds']) in text for bank in measurements['banks'])
links = re.findall(r'\]\(([^)]+)\)',text)
missing = [target for target in links if not (report_path.parent / target).exists() and target != 'evidence/formal-H200-A-r2-first-two-20261110/delivery-verification.json']
assert not missing, missing
checkpoint = (root / 'scope-checkpoint.md').read_text()
assert re.findall(r'^## ([1-4])\.',checkpoint,re.M) == ['1','2','3','4']
assert all(f'| D{i} ' in checkpoint for i in range(1,8)) and checkpoint.count('| CLEAR |') == 7
artifacts = [root / name for name in ('inspection-prefix.json','prefix-verification.json','profile-report-prefix.json','profile-report-prefix.md','prefix-measurements.json','generation-provenance-verification.json','scope-checkpoint.md','verification-commands.md')]
artifacts.append(report_path)
result = {'task_id':'profile-corrected-A-first-two-profile-20261110','verdict':'PASS','input_bytes_preserved':True,'raw_bytes':sum(item['bytes'] for item in inputs.values()),'input_fingerprints':inputs,'retention_fingerprint':digest(root / 'retention.json'),'generated_markdown_exact_render_match':True,'original_rebuild_exact_match':True,'native_successful_updates':2,'profile_verified_updates':2,'native_complete':False,'profile_complete':False,'actual_errors_all_zero':True,'native_receipt_provenance_verified':True,'local_report_links_verified':True,'scope_checkpoint_verified':True,'outputs':{str(path):digest(path) for path in artifacts},'elapsed_seconds':time.perf_counter()-began,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
with (root / 'delivery-verification.json').open('x',encoding='utf-8') as stream:
    stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(result,indent=2,allow_nan=False))
PY
```

The actual exit/result, elapsed time, peak RSS, exact input fingerprints and delivered artifact fingerprints are retained in `delivery-verification.json`. This check does not run the training job or add terminal evidence.
