## Modification History

| Date | Change |
| --- | --- |
| 2026-11-11 | Record the authorized r3 submissions and actual SDK/container completion, separately from pending native measurement qualification. |
| 2026-11-11 | Link primary acceptance of B bounded controls and serving/callback scope; leave A and physical/numerical qualification pending. |
| 2026-11-11 | Accept A bounded controls and both compact physical/source gates; preserve pending F/S ordering qualification and all numerical limits. |

# KV coherence r3 submission and platform completion

## Scope

D40 bounded diagnostics only: A and B each request four non-preemptible H800 GPUs in codesign, with the unchanged first-four/repetition-zero manifest, 16 scoring requests and 10 flushes. New `native/{A,B}/admission-{A,B}-r3` directories preserve r1/r2. Formal training remains HOLD.

Selected executable source is `f8b6b43a599502cb7ac7fac7231ecf9a5ae5523d`; review/checksum/driver closure is `c089f0b3`, pre-submission records are `4f76ae41`, and submitted-state records are `b4fd2039`. The selected native CPU R3 build receipt remains SHA256 `91458ef4659b03e4a867c6be474b09d92653d4e85c763c4054fee18e0934f4c7`.

## Commands and environment

Submission host/workdir: `/data/ycfeng/sota-engine/miles/.worktrees/agent-opd-image`. Controller interpreter: `/data/ycfeng/tmp/stepmind-env/bin/python`, Python 3.10.6, brainpp 2.8.6. `STEPMIND_BACKEND=rjob`; controller `PYTHONPATH` contains this worktree followed by `/data/ycfeng/steptron`. Proxy and existing personal credential files follow `/data/ycfeng/stepfun-env-handbook/stepmind-python-rjob.md`; no credential values were printed or archived. `TMPDIR=/data/ycfeng/tmp/opencode-v2-tmp/opencode`, with user-site and bytecode writes disabled.

Each command ran in its own background-managed local launcher, without an outer timeout:

```bash
/data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_coherence_probe_config.json --pair A --receipt task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111/admission-A-r3.json
/data/ycfeng/tmp/stepmind-env/bin/python -u -B -m tests.manual.agent_opd.submit_teacher_scoring_probe --config task_memory/task_2026-11-08_qwen35_full_kl_nll/teacher_scoring_kv_coherence_probe_config.json --pair B --receipt task_memory/task_2026-11-08_qwen35_full_kl_nll/evidence/teacher-scoring-kv-coherence-probe-20261111/admission-B-r3.json
```

Filtered platform inspection used the personal `brainpp.rjob.RJobClient`, `api.get_namespaced_custom_object(..., plural=client.plural, name=exact_job, _request_timeout=25)`, `get_rjob_infos(exact_job)`, then `_get_replica_kapis(exact_replica)`. Only creator, UID/owner references, allocation/image/mount, phase, node and terminal container fields were retained; no raw spec/env dump was saved.

## Observations

| Pair | Job | First filtered platform snapshot | SDK terminal UTC | Container terminal |
| --- | --- | --- | --- | --- |
| A | `exp-1111-194637-456465` | Starting | Succeeded, 2026-11-11T11:56:55Z | Completed / exit 0 / restart 0; finished 11:56:52Z |
| B | `exp-1111-194636-897299` | Running | Succeeded, 2026-11-11T11:54:54Z | Completed / exit 0 / restart 0; finished 11:54:52Z |

Both actual RJob records declare H800/codesign, one replica, CPU32, memory250Gi and GPU4. Creator is `i-fengyicheng`, image is `artifactory.stepfun-inc.com/docker-public/radixark/miles@sha256:165ff0beecf87a5acde0528e13298a5a274c500950d7eacf5ab6bd1cd5737805`, and current-machine NFS is `100.96.128.195:/data/ycfeng:/data/ycfeng`. A ran on `gpu-h800-0246.host.platform.shaipower.com`, B on `gpu-h800-0030.host.platform.shaipower.com`. Exact replica owner names/UIDs match their respective RJobs. The SDK stop messages follow successful completion as launcher cleanup; no manual stop or duplicate submission was made.

## Checks and limits

| Check | Expected | Actual | Verdict |
| --- | --- | --- | --- |
| Frozen source/receipt and fresh output admission | Reviewed executable/test bytes match; R3 receipt SHA unchanged; no prior r3 receipt/output | All assertions passed at HEAD `4f76ae41`; tracked worktree clean before launch | PASS |
| Independent A/B admission | Existing driver accepts each four-GPU request | Both receipts have `admitted=true`, `submitted=true`, `preemptible=false` | PASS |
| Actual platform/input shape | Personal creator, authorized image/local source, H800/codesign, GPU4 each | Exact CR tags, quota labels, image, mount and resources match | PASS, allocation only |
| Terminal workload/container | Successful SDK task plus owner-bound container exit0/restart0 | Both taskStatuses succeeded=1; both containers Completed0/restart0 | PASS, execution only |
| Active all16/6804 baseline control, serving binding and S/thread | Independent retained-evidence qualification | A/B bounded controls primary ACCEPTED: each all16/6804 exact, actual serving file/class/PID ties; A insert/OLD thread333/S647954864, B thread350/S532178656 | PASS, bounded |
| Independent7955 physical equality and complete FRESH | Separate physical/index coverage qualification | Both compact physical/source gates PASS: actual RID/window joins, exact device-index comparisons,7955 OLD rows, all A16/B10 FULL layers and successful all-layer FRESH drain gate | PASS, compact/source scope; original F/S ordering/lifetime qualification pending |
| KV numerical interpretation, race/root fix, warm correctness, formal200 | Prerequisites accepted before interpretation or formal run | Not accepted by this report; original warm failure and formal HOLD remain | UNVERIFIED / HOLD |

The first metadata collector invocation failed with `KeyError: 'nodename'` at `<stdin>:35`: it read the Replica spec, while the observed KAPI field is `status.nodeName`. A bounded field-name inspection established the correct path; the collector was corrected and both filtered terminal receipts were then written successfully. This is a metadata-harness failure, not a native-job failure. No native/source/config/job behavior changed and no GPU job was resubmitted.

The first local controls-archive format check raised `KeyError: 'pair'`: the A artifact exposes a root `pair` field while B identifies its pair through its `run` path and exact `job`. No files were staged by that failed check. The corrected archival check uses the existing root `job` field in both schemas, parses each JSON and checks acceptance labels, final newlines, trailing whitespace and the exact staged-file set. This is a local metadata-check error, not a native failure, and causes no probe/source change or rerun.

## Evidence

All paths below are under `evidence/teacher-scoring-kv-coherence-probe-20261111/`:

- `admission-{A,B}-r3.json`: requested allocation, worker command, exact job IDs and fresh output paths.
- `initial-platform-{A,B}-r3.json`: historical first snapshots and controller versions; the requested GPU tag is not a physical device measurement.
- `admission-{A,B}-r3.terminal.json`: actual SDK terminal status and task completion.
- `terminal-platform-{A,B}-r3.json`: actual CR tags/group plus exact owner-bound terminal container receipts.

This report does not accept copied/staged bytes as serving-process attestation, CPP scalars as Triton/all-TP coverage, metadata cardinality as physical index equality, or job success as KV numerical correctness. Subsequent native qualification reports own those distinct verdicts.

B details are in `test_report_2026-11-11_kv_coherence_native_B_r3_results.md` and `native-verification-B-r3.json`. Its CPP native/Torch forward F531885904 differs from insert/OLD scheduler S532178656: neither F/S equality nor cross-stream readiness is inferred from those scalars. Original warm1/4 FAIL is unchanged; qualification of the existing producer/readiness path remains pending before K/V interpretation.

A details are in `test_report_2026-11-11_kv_coherence_native_A_r3_results.md` and `native-verification-A-r3.json`: all16/6804 exact,24 zero-reference relative errors undefined,194 archive hashes/44 Rust inputs/twoELFs,2704 responding-TP0 CPP joins. Its F642383120 also differs from S647954864. The physical source-gate report is `test_report_2026-11-11_kv_coherence_r3_physical_indices.md`: exact independent device copies and equality checks, not metadata cardinality alone, establish its compact physical scope. Raw-index replay and paired Rust descriptors are not newly required archives. Qualification of the existing original-index producer/lifetime and F/S synchronization path remains in progress; K/V metric values have not been interpreted.
