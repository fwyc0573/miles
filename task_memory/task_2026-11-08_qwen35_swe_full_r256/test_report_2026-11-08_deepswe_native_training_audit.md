## Modification History

| Date | Change |
| --- | --- |
| 2026-11-08 | Primary supplied12 original PPO dumps and a byte-identical root receipt copy; rerun the unchanged full auditor successfully, preserve initial missing-coverage failure, and close saved PPO/scalar reconstruction while retaining native-mask/gradient/runtime limits. |
| 2026-11-08 | Independently audit the downloaded DeepSWE A/r256 run using the unchanged existing loader/replay auditor; preserve unsupported native-loss seams and bounded scoring observations. |

# DeepSWE native training audit — T02-DEEPSWE-ACTUAL-AUDIT

## Outcome

**NUMERICAL PASS WITH EXPLICIT UNVERIFIED SEAMS:** after the primary supplied the missing original artifacts, the **unchanged full auditor exits0**. Completion-only RKL, binary TIS/count reconstruction, saved native PPO loss/ratio inputs and scalar receipt reconstruction pass. Frozen bank reuse, source/model declarations, LR/success receipts and prior scoring-coverage evidence remain verified at their recorded scope. **Direct saved native post-TIS masks, live gradients/finalizer and independent optimizer-state/runtime gates remain UNVERIFIED.** No fabricated `l=s` assumption was used.

| Update / bank visit | Original completion tokens | Independent KL numerator | Independent KL | Retained tokens | Token / answer rejected / overlap | Maximum KL/TIS receipt error |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
|1 / bank0 visit1|1177|144.7875225869921|0.12301403788189644|842|0 /335 /0|0|
|2 / bank0 visit2|1177|121.64948724197478|0.10335555415630823|266|16 /910 /15|0|
|3 / bank1 visit1|8370|530.579206486456|0.06339058619909868|8370|0 /0 /0|0|

Independent FP32 `advantages=q-s`, `opd_reverse_kl=s-q`, saved PPO token loss and saved PPO KL match **all10724 saved completion-token presentations exactly**, maximum error0 for each. Actual PPO `train_log_probs` equals the independent actor score at every saved position (`max|l-s|=0`, observed `rho=1`); clipping-active token count is0. This equality is measured from the newly supplied original PPO dumps, not inferred from scalar receipts or substituted into missing tensors.

| Step | Independent native-style FP32 scalar | Native receipt | Absolute error | Relative error | Result |
| --- | ---: | ---: | ---: | ---: | --- |
|0|0.08012348005806073|0.08012348170389841|1.6458376744798997e-9|2.054126505088984e-8|PASS|
|1|0.02491965897526899|0.02491965897526899|0|0|PASS|
|2|0.06339058619673534|0.06339058619673534|0|0|PASS|

The independent float64 scalar comparison's maximum absolute error is3.4378713487104307e-9. Native-style FP32 scalar maximum absolute error1.6458376744798997e-9 is below the unchanged auditor's1e-8 tolerance. Actual saved pre-TIS PPO values are matched first, binary masks are independently reconstructed, and rank/sample FP32 sums are divided by global **original** tokens1177,1177,8370. The final reduced scalar is not a downloaded tensor: agreement is with the native receipt.

CPU: `/data/ycfeng/envs/miles-agent-opd-cpu/bin/python`, Python3.12.13, Torch2.11.0+cu130, one Torch thread. Existing30 GiB address-space limit plus plain timeout60s were used; no new systemd/resource operation was attempted. Full-rerun maximum RSS515604 KiB (about504 MiB); the exact value is retained in JSON. No environment/package changes were needed.

## Post-retrieval unchanged full command and provenance

The primary supplied **12 original** `policy_loss_debug/rank_{0,2,4,6}_call_{0,1,2}.pt` files from the same completed job, totaling **400212 bytes**, without any producer change. The primary also supplied root `updates.jsonl`; direct byte comparison verifies it equals `training/updates.jsonl`. No downloads, copy, alias or network action was performed by this audit follow-up.

The exact unchanged mathematical audit command was run under the bounded CPU settings:

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python \
  tests/manual/agent_opd/audit_swe_native_training.py \
  --root /data/ycfeng/tmp/qwen35-swe-deepswe-native-audit/exp-1108-221044-294843 \
  --output task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/native-training-deepswe-A-r256-audit.json \
  --ranks 0 2 4 6 --token-bounds 0.5 2 --answer-bounds 0.9897 1.001 \
  --ppo-bounds 0.8 1.28 --memory-gib 30 --expected-lr 2e-6
```

Actual result: **exit0**, `NUMERICAL_PASS_WITH_EXPLICIT_UNVERIFIED_SEAMS`. The surrounding one-off CPU invocation retained previous evidence in memory, ran this command via `subprocess.run(check=True)`, then restored the initial failure, source/bank/lifetime receipts and this task's identity into the **same** JSON. It introduced no helper or mathematical implementation. JSON `full_unchanged_cli.command` records the exact executed argument vector; `initial_audit` retains the old failure and its then-missing seams; `retrieval_resolution`/`modification_history` record the resolution. The unchanged auditor SHA before/after remains`ddaec198ed37552644bbc25cb516375d4935857cbcdf2f764087f28ade4cdadc`.

The12 PPO files cover24 sample/update records. Each is uniquely joined by exact old-score/behavior/advantage/mask/length equality to canonical metadata indices; filename/call order is not assumed. Full completion-scope checks additionally prove the newly available training-forward numerator matches the independent actor-scoring numerator exactly on each original completion mask. Actual rewards/returns remain zero.

The generic auditor's hardcoded task label and teacher-receipt-download flag are template metadata, not numerical evidence. The merged JSON retains the emitted template values, identifies this task correctly, and records the16 already-downloaded/verified teacher token-ID receipts from the initial bank/stage audit. No auditor or producer source was changed.

## Initial scope and unsupported full-audit invocation — retained history

Source root: `/data/ycfeng/tmp/qwen35-swe-deepswe-native-audit/exp-1108-221044-294843`.
Only this new run's12 actual train dumps, now12 original PPO dumps, five training JSONLs, root byte-identical receipt layout copy, eight scoring-observation files and existing local identity/configuration records are used. No producer/core/observer/launcher or historical audit/report is edited, and no GPU/auth/platform/cloud/network/SSH/resource action is taken in this follow-up. This report and `evidence/native-training-deepswe-A-r256-audit.json` are the only deliverables updated.

The requested unchanged full script **initially could not** verify its entire contract from the incomplete download:

```bash
timeout 60s systemd-run --user --scope -p MemoryMax=30G \
  /data/ycfeng/envs/miles-agent-opd-cpu/bin/python \
  tests/manual/agent_opd/audit_swe_native_training.py \
  --root /data/ycfeng/tmp/qwen35-swe-deepswe-native-audit/exp-1108-221044-294843 \
  --output task_memory/task_2026-11-08_qwen35_swe_full_r256/evidence/native-training-deepswe-A-r256-audit.json \
  --ranks 0 2 4 6 --token-bounds 0.5 2 --answer-bounds 0.9897 1.001 \
  --ppo-bounds 0.8 1.28 --memory-gib 30 --expected-lr 2e-6
```

Initial scope attempt: exit1, `Failed to connect to bus: No such file or directory`. No audit ran in that attempt. The same command without `systemd-run --user --scope -p MemoryMax=30G` then ran under the script's existing30 GiB `RLIMIT_AS`, and exited1 at `_match_debug:138`: **`AssertionError: Incomplete native PPO dump coverage`**. All12 native train dumps loaded successfully first. `policy_loss_debug/` was then absent; additionally, receipts were then downloaded only as `training/updates.jsonl`, whereas the unchanged CLI expects `updates.jsonl` directly under its root. This initial failure is preserved. The primary's later original-file retrieval and byte-identical root receipt copy resolve those two seams; no aliases, synthetic PPO tensors or audit-script changes were made by this audit.

The **historical partial** bounded direct command below reused unchanged `_load_training` and `_replay_identity` and performed only assertions supported by the then-available tensors. It returned`PARTIAL_NUMERICAL_PASS_NATIVE_PPO_LOSS_UNVERIFIED` and did not substitute a loss. The subsequent unchanged full run above supersedes that missing-loss verdict, while preserving its actual failure and already-established source/lifetime evidence.

## Initial bounded direct command — historical partial record

The following command was executed for the **initial partial audit**. It sets `RLIMIT_AS` before reading/importing Torch. The existing auditor remained unchanged. **Do not rerun this historical command to replace the current full evidence: use the unchanged full command above.**

```bash
timeout 60s /data/ycfeng/envs/miles-agent-opd-cpu/bin/python -B - <<'PY'
import resource
resource.setrlimit(resource.RLIMIT_AS, (30 * 1024**3, 30 * 1024**3))
from pathlib import Path
p = Path('task_memory/task_2026-11-08_qwen35_swe_full_r256/test_report_2026-11-08_deepswe_native_training_audit.md')
exec(compile(p.read_text().split('```python\n', 1)[1].split('\n```', 1)[0], str(p), 'exec'))
PY
```

One-off assertions (only the new evidence JSON is written):

```python
import collections, hashlib, importlib.util, json, math, platform, sys
import torch
torch.set_num_threads(1)
root = Path('/data/ycfeng/tmp/qwen35-swe-deepswe-native-audit/exp-1108-221044-294843')
task = Path('task_memory/task_2026-11-08_qwen35_swe_full_r256')
auditor = Path('tests/manual/agent_opd/audit_swe_native_training.py')
auditor_sha = hashlib.sha256(auditor.read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('unchanged_native_audit', auditor)
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
steps, files = a._load_training(root, [0, 2, 4, 6])
assert sorted(steps) == [0, 1, 2]
computed = []
for step, shards in sorted(steps.items()):
    records, rank_counts = [], {}
    for rank, shard in sorted(shards.items()):
        assert shard['data']['num_microbatches'] == [1]
        assert sorted(i for batch in shard['data']['micro_batch_indices'] for i in batch) == list(range(len(shard['samples'])))
        for x in shard['samples']:
            m, s, q, b = x['loss_masks'].bool(), x['log_probs'], x['teacher_log_probs'], x['rollout_log_probs']
            meta = x['metadata']; prompt = meta['prompt_token_count']; response = x['response_lengths']
            assert meta['swe_cell'] == 'A/r256' and meta['swe_attempt'] == root.name
            assert (meta['swe_bank'], meta['swe_bank_visit'], meta['swe_successful_before'], meta['current_weight_version']) == (step // 2, step % 2 + 1, step, step)
            assert m.numel() == response and int(m.sum()) == response and prompt + response == len(x['tokens'])
            for field, tokens in [('prompt_sha256', x['tokens'][:prompt]), ('completion_sha256', x['tokens'][prompt:])]:
                assert hashlib.sha256(json.dumps(tokens.tolist(), separators=(',', ':')).encode()).hexdigest() == meta[field]
            assert torch.equal(q - s, x['advantages']) and torch.equal(s - q, x['opd_reverse_kl'])
            delta = s.double() - b.double(); ratio = delta.exp(); answer_ratio = delta[m].mean().exp().item()
            token = (ratio >= .5) & (ratio <= 2); answer = .9897 <= answer_ratio <= 1.001
            x['retained'] = m & token & answer
            first = int(m.nonzero()[0]); n = (s.double() - q.double())[m].sum().item()
            assert n == ((s.double() - q.double()) * m).sum().item()
            records.append(dict(rank=rank, slot=meta['swe_slot'], sample_index=x['sample_index'], source_uid=meta['source_uid'],
                prompt_tokens=prompt, completion_tokens=response, original_tokens=int(m.sum()), surviving_tokens=int(x['retained'].sum()),
                student_vs_generation_changed_tokens=int((s != b).sum()), student_vs_generation_max_abs=(s - b).abs().max().item(),
                generation_versions=sorted({v['version'] for call in meta['generation_weight_versions'] for name in ['spans','prefill_spans'] for v in call[name]}),
                first_valid_response_offset=first, first_target_absolute_index=prompt + first, first_logit_absolute_row=prompt + first - 1,
                first_target_token_id=int(x['tokens'][prompt + first]), kl_numerator=n, answer_ratio=answer_ratio, answer_pass=answer,
                token_rejected_tokens=int((m & ~token).sum()), answer_rejected_tokens=int(m.sum()) if not answer else 0,
                rejection_overlap_tokens=int((m & ~token).sum()) if not answer else 0))
        rank_counts[str(rank)] = sum(int(x['loss_masks'].sum()) for x in shard['samples'])
    original = sum(r['original_tokens'] for r in records); surviving = sum(r['surviving_tokens'] for r in records)
    n = math.fsum(r['kl_numerator'] for r in records)
    token_rejected = sum(r['token_rejected_tokens'] for r in records); answer_rejected = sum(r['answer_rejected_tokens'] for r in records)
    overlap = sum(r['rejection_overlap_tokens'] for r in records)
    assert original - token_rejected - answer_rejected + overlap == surviving
    assert len(records) == 8 and len({r['completion_tokens'] for r in records}) > 1
    computed.append(dict(attempted_rollout_id=step, bank=step // 2, bank_visit=step % 2 + 1, original_tokens=original,
        surviving_tokens=surviving, kl_before_tis_numerator=n, kl_before_tis_denominator=original, kl_before_tis=n / original,
        tis_retention=surviving / original, token_rejected_tokens=token_rejected, answer_rejected_tokens=answer_rejected,
        rejection_overlap_tokens=overlap, prompt_tokens_excluded=sum(r['prompt_tokens'] for r in records),
        original_rank_counts=rank_counts, samples=sorted(records, key=lambda r: r['slot'])))
replay = a._replay_identity(steps)
assert len(replay) == 8
assert set(r['source_uid'] for r in computed[0]['samples']).isdisjoint(r['source_uid'] for r in computed[2]['samples'])
updates = [json.loads(l) for l in (root / 'training/updates.jsonl').read_text().splitlines() if l.strip()]
attempts = [json.loads(l) for l in (root / 'training/optimizer_attempts.jsonl').read_text().splitlines() if l.strip()]
assert len(updates) == len(attempts) == 3
by_id = {r['attempted_rollout_id']: r for r in updates}
for c in computed:
    step = c['attempted_rollout_id']; r = by_id[step]
    assert {k: v for k, v in r.items() if k != 'update'} == next(x for x in attempts if x['attempted_rollout_id'] == step)
    for name in ['bank', 'bank_visit', 'original_tokens', 'surviving_tokens', 'kl_before_tis_numerator', 'kl_before_tis_denominator', 'kl_before_tis', 'tis_retention', 'token_rejected_tokens', 'answer_rejected_tokens']:
        assert c[name] == r[name], (step, name, c[name], r[name])
    assert r['update'] == r['successful_updates'] == r['native_attempted_count'] == step + 1
    assert r['native_skipped_count'] == 0 and r['update_successful'] and r['lr'] == [2e-6, 2e-6]
    assert r['actual_turns'] == 8 and r['attempt'] == root.name and r['cell'] == 'A/r256' and r['current_weight_version'] == step
    assert r['diagnostics_verified'] and not r['unverified_diagnostics'] and r['nonfinite_tokens'] == 0
    c['receipt_loss_comparison_only'] = r['loss']; c['kl_and_tis_max_receipt_error'] = 0
teacher_rows = [json.loads(l) for l in (root / 'training/teacher_stages.jsonl').read_text().splitlines() if l.strip()]
bank_checks = []
for bank in [0, 1]:
    rows = [json.loads(l) for l in (root / 'training' / f'bank_{bank}.jsonl').read_text().splitlines() if l.strip()]
    sealed, = [r for r in rows if r['event'] == 'acquisition_sealed']
    assert sealed['actual_turns'] == 8 and sealed['membership'] == list(range(8)) and not sealed['missing_slots'] and not sealed['pending_slots']
    finished = {r['source_uid']: r for r in rows if r['event'] == 'slot_finished'}
    first = steps[bank * 2]
    for shard in first.values():
        for x in shard['samples']:
            row = finished[x['metadata']['source_uid']]; sample = row['sample']
            assert row['slot'] == x['metadata']['swe_slot'] and row['status'] in ['completed', 'truncated'] and row['error'] is None
            assert sample['tokens'] == x['tokens'].tolist() and sample['loss_mask'] == x['loss_masks'].tolist()
            for name in ['teacher_log_probs', 'rollout_log_probs']:
                assert torch.equal(torch.tensor(sample[name], dtype=x[name].dtype), x[name])
            t = sample['metadata']['teacher_scoring']
            assert t['token_ids_match'] and t['scored_tokens'] == x['response_lengths'] and t['identity'] == x['metadata']['swe_teacher_identity']
            ends = [r for r in teacher_rows if r['event'] == 'end' and r['bank'] == bank and r['source_uid'] == row['source_uid']]
            assert len(ends) == 2 and {r['stage'] for r in ends} == {'teacher_request', 'teacher_validation'}
            assert all(r['status'] == 'success' and r['error'] is None and r['response_tokens'] == x['response_lengths'] and r['input_tokens'] == x['total_lengths'] and r['teacher_identity'] == t['identity'] for r in ends)
    bank_checks.append(dict(bank=bank, actual_turns=8, teacher_payloads_and_token_id_receipts_verified=8))
configuration = json.loads((task / 'deepswe_integration_config.json').read_text())
identity = json.loads((task / 'evidence/deepswe-native-worker-identity-20261108.json').read_text())
identity, = [r for r in identity['cases'] if r['job'] == root.name]
assert identity['pair'] == 'A' and identity['protocol'] == 'r256'
for node in identity['nodes']:
    assert node['model_path'] == configuration['pairs']['A'][node['role']]['path'] and node['image'] == configuration['image']
assert identity['skip_masked_assistant_turns'] is True
assert identity['native_source_arguments']['--swe-source-root'] == configuration['inputs']['source_root']
assert identity['native_source_arguments']['--swe-native-loader-sha256'] == configuration['inputs']['native_loader_sha256']
source_manifest = json.loads((task / 'evidence/deepswe-input-source-manifest.json').read_text())['manifest']
manifest_files = {r['sha256']: r['path'] for r in source_manifest['files']}
assert all(r['source_uid'].split(':')[0] in manifest_files for c in computed for r in c['samples'])
source_sha = json.loads(Path('tests/manual/agent_opd/megatron_scoring_lifetime.json').read_text())['after_sha256']
observations, lifetime_ranks = [], []
for rank in range(8):
    path = root / 'megatron_scoring_lifetime/observations' / f'rank_{rank}.jsonl'
    rows = [json.loads(l) for l in path.read_text().splitlines() if l.strip()]
    assert all(r['rank'] == rank for r in rows)
    counts = collections.Counter(r['event'] for r in rows)
    identities = [r for r in rows if r['event'] == 'source_identity']
    soft = [r for r in rows if r['event'] == 'observer_unverified']
    coverage = {(r['scoring_pass_index'], r['forward_microbatch_index'], r['event']) for r in rows if r['event'] != 'source_identity'}
    expected = {(p, 0, event) for p in range(3) for event in ['forward_enter', 'projection_enter', 'forward_exit']}
    source_ok = len(identities) == 3 and all(r['source_verified'] and r['source_sha256'] == r['expected_source_sha256'] == source_sha for r in identities)
    lifetime_ranks.append(dict(rank=rank, rows=len(rows), events=dict(counts), source_sha_matches=source_ok,
        coverage_status='PASS' if coverage == expected and not soft and source_ok else 'UNVERIFIED', soft_errors=soft,
        measured_prior_output_alive=sum(r.get('prior_full_output_alive') is True for r in rows),
        forward_microbatch_indices=sorted({r['forward_microbatch_index'] for r in rows if r['event'] != 'source_identity'})))
    observations.extend(rows)
assert hashlib.sha256(auditor.read_bytes()).hexdigest() == auditor_sha
result = dict(task_id='T02-DEEPSWE-ACTUAL-AUDIT', status='PARTIAL_NUMERICAL_PASS_NATIVE_PPO_LOSS_UNVERIFIED',
    data_root=str(root), python=platform.python_version(), torch=torch.__version__, memory_limit_gib=30,
    maximum_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, unchanged_auditor_sha256=auditor_sha,
    training_files=files, bounds=dict(token=[.5, 2], answer=[.9897, 1.001], ppo=[.8, 1.28]), expected_lr=2e-6,
    full_unchanged_cli=dict(status='UNSUPPORTED_ARTIFACTS', exit_code=1, error='AssertionError: Incomplete native PPO dump coverage',
        missing='policy_loss_debug/*.pt', secondary_layout_issue='updates.jsonl is under training/ rather than the dump root',
        systemd_scope_error='Failed to connect to bus: No such file or directory; existing RLIMIT_AS used'),
    updates=computed, replay_identity=replay, bank_checks=bank_checks,
    completion_rkl_semantics='Unweighted current-student minus frozen-teacher mean over the original eligible completion mask; prompts have no score entries. This is a fixed-completion sampled statistic, not an exact full current-policy expectation',
    source_identity=dict(snapshot_job=identity['job'], model_nodes=identity['nodes'], runtime_source_arguments=identity['native_source_arguments'],
        dataset=source_manifest['dataset'], sampled_source_files={sha: manifest_files[sha] for sha in {r['source_uid'].split(':')[0] for c in computed for r in c['samples']}}),
    native_boundary_receipts=[{k:r[k] for k in ['update', 'successful_updates', 'native_attempted_count', 'native_skipped_count', 'current_weight_version', 'lr', 'loss']} for r in updates],
    lifetime=dict(status='PASS_SAVED_SINGLE_MICROBATCH_COVERAGE' if all(r['coverage_status']=='PASS' for r in lifetime_ranks) else 'UNVERIFIED',
        ranks=lifetime_ranks, installed_schedule_sha256=source_sha, total_rows=len(observations),
        source_rows=sum(r['event']=='source_identity' for r in observations),
        memory_rows=sum('prior_full_output_alive' in r for r in observations),
        measured_prior_output_alive=sum(r.get('prior_full_output_alive') is True for r in observations),
        full_output_storage_bytes=sorted({r['full_output_storage']['storage_bytes'] for r in observations if 'full_output_storage' in r}),
        limit='Each pass has microbatch0 only; new observer state resets its previous weakref per pass. No within-pass next-microbatch or before/after GPU lifetime effect is verified'),
    unverified=dict(native_ppo_loss='No actual training-forward logprobs, native PPO token-loss/ratio or post-TIS mask dumps; no independent native loss reconstruction or loss error is available',
        gradient_optimizer='No live graph, gradient, finalizer token tensor or independent optimizer state; scalar receipts and LR/counters are not that proof',
        capacity='Only A/r256, eight slots, three updates, one microbatch/rank; not256-turn/multi-microbatch/formal capacity',
        evaluator='Observer-start/evaluator isolation is outside scope and blocked by the separately owned mount-list alias issue'))
(task / 'evidence/native-training-deepswe-A-r256-audit.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
print(json.dumps(dict(task_id=result['task_id'], status=result['status'], updates=[{k:c[k] for k in ['bank','bank_visit','original_tokens','surviving_tokens','kl_before_tis','token_rejected_tokens','answer_rejected_tokens','rejection_overlap_tokens']} for c in computed], lifetime=result['lifetime']['status'])))
```

## Completion-only counting and fresh scores

All12 train dumps pass the unchanged loader's schema, CP1, finite-value, binary-mask, metadata/index and disjoint four-rank checks. All24 sample/update records have exactly one saved score/mask/teacher/behavior/advantage entry per completion token; none has a prompt score entry. Original masks are all1 here, verified rather than presumed. The independent sum is `sum(original_completion_mask*(current_student-frozen_teacher))`, divided by the same original completion-mask sum, before either TIS layer. No behavior ratio or additional rollout enters RKL.

| Bank/visits | Prompt tokens excluded per visit | Completion/original-mask denominator | Per-rank originals `[0,2,4,6]` |
| --- | ---: | ---: | --- |
|0 /1,2|134192|1177|667,134,316,60|
|1 /1|479562|8370|482,3585,2911,1392|

Per-sample lengths and target offsets (bank0 identical on both visits):

| Bank | Slot | Prompt | Completion/original mask | First target absolute index | First predicting logits row |
| --- | ---: | ---: | ---: | ---: | ---: |
|0|0|4366|60|4366|4365|
|0|1|5707|91|5707|5706|
|0|2|12808|109|12808|12807|
|0|3|13957|170|13957|13956|
|0|4|19501|207|19501|19500|
|0|5|20792|128|20792|20791|
|0|6|21771|278|21771|21770|
|0|7|35290|134|35290|35289|
|1|0|36121|245|36121|36120|
|1|1|59455|2948|59455|59454|
|1|2|60837|1147|60837|60836|
|1|3|62304|435|62304|62303|
|1|4|63028|478|63028|63027|
|1|5|63167|2433|63167|63166|
|1|6|66961|637|66961|66960|
|1|7|67689|47|67689|67688|

First valid response offset is0 for every sample. Current source `miles/backends/training_utils/data/context_parallel.py:142–152` takes target IDs from `tokens[-response_length:]` and logits rows `[total_length-1-response_length,total_length-1)`. Thus response token0 at absolute `prompt_length` is predicted by logits row`prompt_length-1`; that logits row is not a prompt target included in RKL. This one-token alignment is an inspected source contract plus matching tensor lengths/IDs, not a rerun of missing logits. Prompt/completion hashes are independently recomputed from actual token lists and match metadata.

Metadata-indexed replay uses the unchanged auditor's `(attempt,bank,slot,source_uid,sample_index)` key, not filename or list order. All eight bank0 samples retain exact tokens, original masks, teacher/behavior values, prompt/completion hashes, teacher identity and generation metadata. Student values change on **8/8 samples,1008/1177 tokens**, maximum absolute change **4.128511428833008**. Reconstructed survivor masks change988 positions. Every derived advantage and reverse-KL tensor remains exactly consistent with its visit's current student.

Generation versions remain0 on bank0 visits1/2, while current versions advance0/1; bank1 generates/uses version2. Current student also differs from original generation behavior on1041/1177,1043/1177 and8143/8370 token presentations respectively, supporting distinct score sources. The implementation statistic is the unweighted logprob gap on each fixed completion with refreshed current scores; it is **not** an exact current-policy expectation over every possible output.

## TIS, bank and identity observations

The independent token mask uses `exp(s-b)∈[.5,2]`; each answer mask uses `exp(mean(s-b))∈[.9897,1.001]` over **all original eligible completion tokens**, not survivors. Binary intersection yields the exact table above. Visit2 has both rejection layers: token16, answer910, overlap15, union911, survivors266. Nonuniform lengths are present on all three visits. All computed counts and pre-TIS KL numerators/denominators match receipts exactly; no native row enters reconstruction.

**Direct native mask limit:** healthy post-TIS full vectors are not among downloaded artifacts. Exact reconstruction plus matching receipt counts does not independently prove bitwise identity of the unrecorded native mask, and is not described as a downloaded final-mask observation.

Both acquisition ledgers contain one start, eight completed slots and one sealed event; sealed membership is0–7 with no missing/pending slots. Each ledger sample is joined by source UID/slot and its full tokens/mask/teacher/behavior exactly matches the training sample (teacher/behavior JSON values are compared at the actual FP32 tensor dtype). For all16 bank samples, `teacher_scoring.token_ids_match=true`, scored length matches completion length, and corresponding teacher request/validation end events succeed with matching input/response lengths and identity. The stage log supplies those recorded token-ID validation receipts; teacher logits/probability forwards are not rerun here.

Bank1 contains eight new source UIDs and sample indices8–15, disjoint from bank0 indices0–7. `training/updates.jsonl` and `optimizer_attempts.jsonl` contain all **three** native success boundaries, not merely the first two in the earlier business snapshot: successful/attempted1→2→3, skipped0, LR`[2e-6,2e-6]`, and bank0 visits1/2→bank1 visit1. The two ledgers match field-for-field except the update-only field. These remain actual native-hook receipts, **not** independent Adam state/group settings/counter-continuity or gradient proof.

The exact-job local worker-identity snapshot matches the integration configuration:

- Student: `/mnt/codesign-exp/ycfeng/opd-assets/models/Qwen/Qwen3.5-4B/851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`.
- Teacher: `/mnt/posttrain/checkpoints/open-models/Qwen/Qwen3.5-27B/model`, matching every bank/teacher/training identity.
- Native loader path and SHA: the approved `s4_swe_turn_data_1001.py`, SHA`8850287f633b03b188659778136e81c1d5a6fb4e87591a8a4fb05639e7603980`; source-root argument matches the new DeepSWE root and masked assistant turns are skipped.
- All sampled UIDs belong to DeepSWE resolved file1, SHA`00e890ea9815f44285414507e5bdfd69e4e67d3a1768d70d1f57393e0ecc17e6`, matching the recorded eight-source manifest rather than any historical GLM input.

These are declared path/version/source identities in exact-job local receipts, independently joined to actual sample/token identities. They are not a fresh hash of all source/model weight bytes or a repeat of the full dataset/native-loader parity acceptance. No other job's capacity/gradient verdict is transferred here.

## Bounded scoring-lifetime coverage

All8 rank files contain12 rows each: **96 total**, **24 source identities**, **24 forward-enter**, **24 projection-enter**, **24 forward-exit**. Each rank covers scoring passes0/1/2 and microbatch0 only. There are **zero observer soft-error rows** and no missing expected single-microbatch observations. All24 installed-source SHA receipts match the pinned patched schedule:

```text
8b0370c0d50a2463781ae3c622e30f923d096485aed3c0f8939be4cc13689081
```

Across72 memory snapshot rows, measured `prior_full_output_alive=true` count is **0**. Actual full-output storage sizes range1,144,258,560–32,420,659,200 bytes; complete distinct sizes are in JSON. These are storage observations, not a computed memory saving.

**No lifetime/capacity effect is inferred:** each pass creates a new observation state with no previous weakref (`megatron_scoring_lifetime_observer.py:111–115`), and `forward_exit` snapshots before recording its current output weakref (`:96–106`). With only microbatch0 per pass, no next within-pass microbatch tests old-output survival. There is no unpatched before-run comparator,256-turn/multiple-microbatch coverage or measured before/after effect in these files. SHA coverage proves the recorded schedule identity, not the requested unchanged256-trajectory memory improvement.

## Acceptance limits and final checks

| Criterion | Verdict |
| --- | --- |
| Completion-only current-student RKL / frozen teacher / no weighting | PASS |
| Independent binary TIS reconstruction and exact receipt counts | PASS |
| Direct saved healthy native TIS vector identity | UNVERIFIED — missing vectors |
| Frozen bank0 reuse, fresh scores and bank transition | PASS |
| Declared model/input identities and sample/token joins | PASS, limited to recorded declarations/payloads |
| Native receipt success/LR | PASS — native-hook observations only |
| Full unchanged audit CLI / saved native PPO loss and scalar reconstruction | PASS after original artifact retrieval — exact saved token errors0, scalar max absolute error1.6458376744798997e-9 |
| Eight-rank saved source/single-microbatch observer coverage | PASS |
| GPU lifetime before/after effect /256 capacity / actual optimizer-gradient proof | UNVERIFIED, outside available evidence |
| Observer-start/evaluator isolation | Not accepted here; the separately owned mount-list alias bug remains outside this audit |

Unchanged auditor SHA before/after both stages: `ddaec198ed37552644bbc25cb516375d4935857cbcdf2f764087f28ade4cdadc`. No auxiliary generic test framework/helper or producer change was added. Final bounded checks parse the evidence JSON and verify complete train/PPO coverage, exact token errors, scalar tolerance, retained initial failure and current real UNVERIFIED labels; both owned files are checked for trailing whitespace. JSON retains exact maximum RSS and numerical/source identities. The initial full-CLI failure remains reported, rather than hidden by the subsequent successful full command.

## 1. 规划完成情况

**汇总：** PASS3｜BLOCKED0；仅本委派的已保存数值范围。GPU运行验收仍由父会话拥有。
- PASS：独立KL/TIS/replay/identity/counter检查及两项记录。
- PASS：8-rank lifetime已保存观察覆盖与限制。
- PASS：补齐原始debug和receipt layout后，不改脚本完成saved native PPO/scalar重算；未补造证据。

## 2. 偏离检测

**结论：** 未偏移；当前前沿仍是父任务02/03。
D1工具打磨、D2重复试错、D3支线修补、D4重复并行工作、D5扩范围、D6空转和D7路线违背均CLEAR：只复用现有loader/replay并做有证据的CPU断言；不改producer、不扩observer、不接受容量或evaluator。
**文档检查：** D11和S4仍约束新数据及原数学口径；未发现本范围内S1–S6缺陷。初次PPO/debug缺口已由原始下载解决；直接mask/gradient和运行容量仍是各自记录的验收边界，不修改spec/tickets。

## 3. 纠正建议

**分支A：** spec/tickets合理，无需改动；需停止的偏离行为无。
1. 交还本次完整saved PPO/scalar重算；直接native post-TIS mask、live gradient/finalizer和optimizer state尚未下载，不能从scalar agreement推断其已通过。
2. 按原分工继续256多microbatch/容量对照与单独evaluator隔离验收；本审计不操作平台或改动配置。

## 4. 最值得关注的3点

1. 新数据三步completion KL/TIS精确匹配，1008/1177 student分数在冻结bank0上刷新。
2. 实际native PPO/debug已补齐，token误差0、scalar误差1.64584e-9；直接post-TIS mask及live gradient仍不得标为已独立验收。
3. 96条lifetime记录覆盖完整但每pass仅microbatch0，old-output计数0不能证明256容量或修复效果。
