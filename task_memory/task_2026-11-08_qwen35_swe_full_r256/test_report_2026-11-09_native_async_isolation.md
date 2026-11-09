## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Apply phase-review acceptance and correct the fault timestamp from the original fault.json. |
| 2026-11-09 | Record the actual DeepSWE training, injected HF2 submission failure, HF3 native grading and reader cleanup. |

# Native asynchronous evaluation isolation

## Observed result

**PASS for the observed isolation scenario; independent phase review supports Ticket03 capability acceptance.** This is a smoke qualification, not a complete400 evaluation or capacity acceptance.

- Training job: `exp-1108-234430-904523`; admission: `evidence/admission-deepswe-native-async-permissions-fixed-20261108.json`.
- The first HF2 submitter subprocess deliberately received an empty `AK_BASEMIND`. It failed before GPU admission at Unix time1794153345.1932557, as recorded in the original `fault.json`. The watcher recorded `UNVERIFIED`, retained the queued point and did not retry or fabricate an allocation receipt.
- Native hook receipts recorded successful updates1/2/3, with update3 at1794153695.3950486, **350.2017929s after the injected failure**. This is hook evidence, not an independent optimizer-state or gradient proof.
- The platform stopped the teacher only after the critical student succeeded. The exact system reason was `All critical tasks are finished.`; the local terminal record classified native execution as successful.
- HF3 evaluator job `exp-1109-000222-377438` exited0. Its actual persisted native outcome was `success=true`, for `astropy__astropy-12907#attempt-0`, seed1729.
- Actual serving identity: weight version3; 131072 context; thinking and history preservation enabled; reasoning parser `qwen3`; tool parser `qwen3_coder`; SGLang `0.5.24.dev80+g056f871`.
- All55 request hashes and the native config, trajectory and grader hashes were independently checked against the retained cloud bytes and matched. Native pytest collected15 tests and passed all15, covering the2 FAIL_TO_PASS and13 PASS_TO_PASS tests.
- All3 readers exited with recorded finish timestamps. Both HF directories still contained `.complete` and `qwen_text_export.json`, identifying versions2 and3 respectively.
- HF2 remains QUEUED with no reader/start/deadline. HF3 remains INCOMPLETE with1/400 completed slots and399 missing. No avg@4 is available; neither qualification HF is released.

## Exact collection commands and environment

Primary collection used `timeout 60s ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng 'python3 -'` with scoped read-only Python programs; no platform or cloud state was changed. The cloud source paths were read through the personal `/mnt/ws-jfs/ycfeng` mount. Local Python3 performed the subsequent JSON inspection. The original CPU submission used personal-auth StepMind Python3.10 and the existing pinned-image worker interpreters; no dependency or environment version was changed.

Retained raw collection outputs on the approved temporary disk:

- `/data/ycfeng/tmp/qwen35-swe-native-async-live-training-proof-20261109.json`: original updates, optimizer-attempt receipts and HF publications.
- `/data/ycfeng/tmp/qwen35-swe-native-async-final-store-20261109.json`: actual HF2/HF3 state, outcomes and reader records.
- `/data/ycfeng/tmp/qwen35-swe-native-async-verified-artifacts-20261109.json`: exact source paths, checked hashes, native grader and retained text-export inventories.

The checked persistent cloud point is `/mnt/codesign-exp/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/qualification-evaluations/points/qualification.A-r256.exp-1108-234430-904523.HF3`. Its result is `results/astropy__astropy-12907.1729.json`. Native artifacts are under `native/astropy__astropy-12907.1729/c4125d55bb8f483da0f5ea99cc8cc35e`.

| Check | Expected | Actual | Result |
| --- | --- | --- | --- |
| Training after injected failure | Update3 remains successful | Update3 timestamp later by350.2017929s | PASS |
| Later HF evaluation | Native attempt runs without repeating HF2 | HF3 actual native success,55 requests | PASS |
| Native grader | All15 required tests pass | 15 passed | PASS |
| File identity | Recorded hashes equal original bytes | 55 requests plus3 artifacts matched | PASS |
| Reader cleanup | No live reader after evaluation | 3/3 EXITED with finish timestamps | PASS |
| Qualification retention | Preserve incomplete HF2/HF3 | Both versions and `.complete` retained | PASS |
| Full avg@4 |400 complete slots required |1/400 only; null result | NOT COMPLETE |

## Limits

The injected failure occurred in the real local evaluation submitter before GPU admission, not inside the ACS/native grader. Missing admission is correctly classified as unverified rather than retried. Independent reviewer `ses_e43dee3a4ffe7TwCS350olE3Pw` confirmed that this matches the expressly recorded failure scenario; no additional post-admission failure test is required. Earlier CPU and cloud fault-injection tests cover additional evaluator failures, but are not substituted for this observed run. This smoke does not prove256-candidate acquisition, multi-microbatch memory capacity, finalizer scaling, independent optimizer state, formal training, or a full SWE score.
