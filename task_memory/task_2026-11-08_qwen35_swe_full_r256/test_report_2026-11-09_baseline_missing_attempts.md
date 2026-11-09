## Modification History

| Date | Change |
| --- | --- |
| 2026-11-09 | Record four missing native attempts without replacing them with False or changing the live baseline. |

# Original4B baseline: four missing attempts

## Observation

The recorded point readback has23 completed results:9 true/14 false,plus four historical failure files with no corresponding final result. The point's400 denominator,first start,original72-hour deadline and protected source weights are unchanged. These four failures are not additional modelFalse results.

| Frozen slot | Native observation | Status |
| --- | --- | --- |
| astropy__astropy-13398#attempt-1,seed1730 | ModelError HTTP400:input131220>context131072. | Missing,no final grader result. |
| astropy__astropy-13398#attempt-2,seed1731 | ModelError HTTP400:input131489>context131072. | Missing,no final grader result. |
| astropy__astropy-13579#attempt-2,seed1731 | ModelError HTTP400:input131230>context131072. | Missing,no final grader result. |
| astropy__astropy-13579#attempt-1,seed1730 | Earlier context-limit warning;terminalRemoteProtocolError/server disconnected at03:58:35. Native autosubmission retains an infrastructure exit and the integration rejects a final outcome. | Missing;terminal cause is not identical to the three explicit input-overflow exceptions. |

The fourth selected log records the context-limit warning at03:00:06 and terminaldisconnect at03:58:35. It does not prove an infinite503 retry orKV pressure;no503 is claimed. These observations do not establish a model score,permission to alter128K,or permission to resample.

## Evidence and method

Read-only SSH used `shai-ycfeng` solely for the authorized personal volume `/mnt/ws-jfs/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/evaluations/points/original4b`. Cloud equivalents use `/mnt/codesign-exp/ycfeng/...`.

- Selected failure identities/error messages/final-result lookup:`/data/ycfeng/tmp/qwen35-swe-original4b-failure-readback-20261109-expanded.json`.
- Native child-log selections:`/data/ycfeng/tmp/qwen35-swe-original4b-native-errors-20261109-expanded.json`.
- Fourth log full read and selected line numbers:`/data/ycfeng/tmp/qwen35-swe-original4b-fourth-failure-20261109.json`.

Native attempt paths relative to point/native:

- `astropy__astropy-13398.1730/3886ac488be74ab880326a086996970d`
- `astropy__astropy-13398.1731/93e247c461e842b883101354948ebfb2`
- `astropy__astropy-13579.1730/71a2af7d60a14647b58fc24885b9a371`
- `astropy__astropy-13579.1731` is linked by its failure record in the selectedreadback;do not infer an unrecorded attemptdirectory.

The decisive fourth read command:

```bash
timeout 60s ssh -o BatchMode=yes -o ConnectTimeout=10 shai-ycfeng 'python3 -' <<'PY' > /data/ycfeng/tmp/qwen35-swe-original4b-fourth-failure-20261109.json
import json,re,time
from pathlib import Path
p=Path('/mnt/ws-jfs/ycfeng/miles-qwen35-swe-full-r256/deepswe-0913/evaluations/points/original4b/native/astropy__astropy-13579.1730/71a2af7d60a14647b58fc24885b9a371/child.log')
s=re.sub(r'\x1b\[[0-9;]*m','',p.read_text());rows=[]
for n,line in enumerate(s.splitlines(),1):
 if any(x in line for x in ('exit_status','ERROR','Error:','error:','infrastructure','context length')):rows.append({'line':n,'text':line[:1500]})
print(json.dumps({'observed_at':time.time(),'source':str(p),'bytes':p.stat().st_size,'selected_lines':rows},indent=2))
PY
```

The command exited0 and read30580 bytes. NoGPU,job control,client/config/source edit or native outcome reclassification was performed.

## Follow-up boundary

The baseline worker remains independent ofD13 capacity. Keep healthy execution running. Any later explicit recovery must diagnose/remedy the missing attempt,retain originaldeadline and resume only missing slots through the existing store rules once reader-state prerequisites hold. Do not reroll modelFalse outcomes or infer a completebaseline from partial results. The frozen point is not modified to hide these failures.
