# error recovery

Use this guide after the first failure. It is for deciding the next read or retry, not for masking errors.

## Failure matrix

| Symptom | Likely cause | Next action | Retry policy |
| --- | --- | --- | --- |
| HTTP 400 with an empty or weak body on panel query, verify, or create | DTO family mismatch | inspect `schema`, compare against the expected payload family, and retry only after the body is corrected | retry once after payload fix |
| HTTP 400 saying an attribute is still referred by another analysis | backend reference not released yet | reread the owner list and the specific analysis; treat cleanup as pending until the backend releases the reference | do not spam delete; wait and retry later |
| HTTP 403 on admin or permission endpoints | permission boundary | report the boundary explicitly and stop the write flow | no automatic retry |
| HTTP 404 on a previously known ID | stale ID, scope mismatch, or deleted object | re-resolve the owner, path, or search result before any new write | retry only after scope is refreshed |
| HTTP 500 from AI, datasource, or alert replay | backend or service-side problem | capture the structured error, narrow the probe to the smallest reproducible read or write, and stop repeated retries | at most one guarded repro |
| command says success but reread does not show the change | write not persisted yet, read lag, or wrong verification scope | reread once with the correct scope and wider window before any new mutation | one reread, then stop or redesign |
| resend succeeds but delivery history shows no new top-level row | history is detail-based, delayed, or throttled | widen `notification page list`, inspect the detail record, and remember minimum notification interval throttling | reread, do not blind-resend repeatedly |
| analysis is created but stays `Ready` | runtime state not advanced | `get`, `list`, then `resume` when the workflow expects `Running` | safe follow-up action |
| `trigger-types list` drops the trigger you wanted after scope changes | wrong owner or child-template scope | redesign around the supported trigger family or move the workflow to a leaf owner | no forced retry with unsupported trigger |

## Stop conditions

Stop mutating and return a clear failure when:

- auth or connectivity is unhealthy
- the owner or business root is still unknown
- the write needs credentials you do not actually have
- the backend returns the same structured 500 after one guarded repro
- the environment exposes a permission boundary instead of missing data

## Safe retry pattern

1. preserve the first error message
2. read the owning object again
3. read the schema again if payload family could be wrong
4. change exactly one thing
5. retry once only if the new read explains why the retry should succeed

## Escalation handoffs

- event generation problems -> `../../idmp-workflow-alert-create/SKILL.md`
- delivery or resend visibility problems -> `../../idmp-workflow-alert-debug/SKILL.md`
- complex panel payload failures -> `../../idmp-workflow-panel-build/SKILL.md`
- complex trigger or output-scope failures -> `../../idmp-workflow-analysis-create/SKILL.md`
