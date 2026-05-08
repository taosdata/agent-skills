---
name: idmp-analysis
description: "IDMP analysis skill for listing, searching, reading, resuming, and preparing analysis create flows with path, trigger type, sub-template, and output-attribute checks."
metadata:
  author: "TaosData"
  version: "0.5.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli analysis --help"
---

# analysis

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

**Before any write:** Follow the [🛑 Destructive op confirmation protocol](../idmp-shared/SKILL.md#-destructive-op-confirmation-mandatory). Read-only commands stay read-only here, but delete / write / patch flows still require the shared yes-gate.


## Recommended shortcuts

| Shortcut | Purpose |
|----------|---------|
| `+list` | Read analyses under one element. |
| `+search` | Search analyses globally, including an empty-keyword starting point. |

## Recommended references

- [`analysis read flows`](references/analysis-read-flows.md)
- [`../idmp-workflow-analysis-create/SKILL.md`](../idmp-workflow-analysis-create/SKILL.md)
- [`../idmp-workflow-alert-create/SKILL.md`](../idmp-workflow-alert-create/SKILL.md)

## Missing context to resolve first

| Context | Why it must be resolved before create or resume |
| --- | --- |
| Final owner and mode | You need the exact `elementId` or `elementTemplateId` before you can choose the right command family or reserve a name. |
| Business root | Element-mode analysis creates still need `rootElementId` from the business root, even when the real owner moves to a data-bearing leaf. Prove that root with `element elements path` plus `element fullpath get` before you send the create payload. |
| Candidate analysis name | `analysis.analyses.new-name` and `analysis-template.analyses.new-name` require a candidate `name` and `--ack-risk`. |
| Trigger scope | You need to know `applyOnSelf`, child-template scope, and which trigger type is valid after that choice. |
| Output plan | Decide whether to reuse or create output attributes, which `valueType` they need, and whether they land on self or child scope. |
| Runtime target | Decide whether `Ready` is acceptable or whether the final workflow must end in `Running` and therefore needs `resume`. |

## Constrained live behaviors

- Prefer `POST /api/v1/ai/analysis/create` for natural-language analysis or alert intents, then persist the returned draft through the normal create path. Use the structured DTO workflow as the fallback when the draft is unsuitable or persistence fails.
- `analysis.analyses.new-name` and `analysis-template.analyses.new-name` require a candidate `name` and `--ack-risk`; do not call them with only the owner scope.
- In element mode, `rootElementId` comes from the business root rather than the current leaf element.
- Shared environments can force analysis creation onto a data-bearing leaf when `trigger-types list` is empty on the current owner.
- Child scope does not inherit self-scope triggers. When `applyOnSelf=false`, the backend can legitimately expose only `Session` and `Interval`, so do not assume `DataInput` or `Event` will stay available.
- Minimal create payloads need `rootElementId`, `startAfterCreated`, a valid `trigger`, and real `output.attributes[].attrId` values. For current live `ELE_SUBET` flows, child-scope analyses can use owner-element output attributes while `output.elementTemplate.id` continues to point at the child template.
- Analysis create is not complete until `get`, `list`, and, when needed, `resume` prove the backend kept the object in the expected runtime state.
- Current live backends can return success for analysis delete while the generated output attributes remain referenced. Once create, reread, and `resume` prove the analysis itself worked, classify leaked output-attribute cleanup as a backend boundary instead of a wrong create payload.
- If the workflow must emit events or notifications, switch to [`../idmp-workflow-alert-create/SKILL.md`](../idmp-workflow-alert-create/SKILL.md) instead of treating it as a generic read or create flow.

## Evidence of completion

- A reserved name is only useful when the later `create` reread shows the same name on the persisted object.
- A create is only complete when `analysis analyses get` and `analysis analyses list` show the same `id`, owner scope, and expected state bits.
- If the success condition is a running analysis, do not stop at `Ready`; reread after `resume` and confirm the runtime state actually changed.
- Shared-environment cleanup is best-effort. If delete returns success but the output attribute still shows a backend reference leak, keep the leaked IDs with the report and do not downgrade an already-proven create or running analysis into a payload-shape failure.
- If `rootElementId` was part of the write path, keep the `element elements path` and `element fullpath get` evidence with the create proof.

## Product behavior to preserve

- Read `path`, `attributes`, `sub-templates`, `trigger-types`, and `new-name` before create or edit.
- For natural-language creation asks, prefer the AI draft endpoint first and keep the structured create flow as the fallback.
- `analysis.analyses.new-name` and `analysis-template.analyses.new-name` require a candidate `name` and `--ack-risk`; do not call them with only the owner scope.
- In element mode, the create payload needs `rootElementId` from the business root, not the current element.
- Copyable live-safe create shapes belong in [`../idmp-workflow-analysis-create/SKILL.md`](../idmp-workflow-analysis-create/SKILL.md), especially when the payload must include `output.attributes[]`.
- Trigger type choices depend on `applyOnSelf` and, for child scope, the selected template.
- If a create flow is abandoned after reserving a temporary output attribute, clean up that temporary attribute before retrying.
- After create or update, read the analysis back and `resume` it if the expected state is running.

## Key commands

```bash
idmp-cli schema analysis.analyses.list
idmp-cli analysis analyses list --params '{"elementId":123,"current":1,"size":20}'

idmp-cli schema analysis.analyses.get
idmp-cli analysis analyses get --params '{"elementId":123,"id":456}'

idmp-cli schema analysis.analysis.search
idmp-cli analysis analysis search --params '{"keyword":"voltage","current":1,"size":20}'

idmp-cli analysis analyses new-name --ack-risk --params '{"elementId":123,"name":"demo-analysis"}'
idmp-cli analysis trigger-types list --params '{"elementId":123,"applyOnSelf":true}'
idmp-cli analysis trigger-types list --params '{"elementId":123,"applyOnSelf":false,"elementTemplateId":456}'

idmp-cli schema analysis.analyses.resume
idmp-cli analysis analyses resume --ack-risk --params '{"elementId":123,"id":456}'
```

## Exception and failure handling

- If `trigger-types list` changes after `applyOnSelf` or the child template changes, discard the earlier trigger choice and re-read it.
- If child-scope trigger types only show `Session` or `Interval`, redesign the analysis around those trigger families or move back to self scope; do not force `Event` or `DataInput`.
- If the element path does not resolve to a business root, do not create the analysis until `rootElementId` is known. Treat “resolved” as `element elements path` plus `element fullpath get` agreeing on the same first-level owner.
- If output attributes were created only for a draft analysis and the draft is canceled, remove the temporary outputs before the next attempt.
- If delete succeeds but `attribute elements attributes-delete` still reports the output attribute is referred by the analysis, classify that as a backend cleanup boundary after you have already captured the create or running proof; stop retrying generic cleanup loops.
- If create or update succeeds but `get` still shows an unexpected state, verify with `list` and then use `resume` instead of sending another create.
- If search results are ambiguous, confirm the owner element before editing; do not reuse an `id` from a different element or template scope.

## Validation scenarios

1. Read the owner list with `idmp-cli schema analysis.analyses.list` and `idmp-cli analysis analyses list --params '{"elementId":123,"current":1,"size":20}'`.
2. Read one analysis in detail with `idmp-cli analysis analyses get --params '{"elementId":123,"id":456}'`.
3. Check global discoverability with `idmp-cli analysis analysis search --params '{"keyword":"voltage","current":1,"size":20}'`.
4. Resolve the business-root proof chain with `idmp-cli element elements path --params '{"elementId":123}'` and `idmp-cli element fullpath get --params '{"rootElementId":100,"elementId":123}'`, then validate create prerequisites with `idmp-cli analysis analyses new-name --ack-risk --params '{"elementId":123,"name":"demo-analysis"}'` and `idmp-cli analysis trigger-types list --params '{"elementId":123,"applyOnSelf":false,"elementTemplateId":456}'`.
5. Preview and verify the write path with `idmp-cli analysis analyses create --dry-run --ack-risk --params '{"elementId":123}' --data '{...}'`, then prove the runtime branch with `idmp-cli analysis analyses get --params '{"elementId":123,"id":456}'`, `idmp-cli analysis analyses list --params '{"elementId":123,"current":1,"size":20}'`, and `idmp-cli analysis analyses resume --dry-run --ack-risk --params '{"elementId":123,"id":456}'`.
