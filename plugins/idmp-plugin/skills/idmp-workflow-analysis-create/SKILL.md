---
name: idmp-workflow-analysis-create
description: "IDMP analysis creation workflow. Resolve mode, owner, trigger types, output attributes, creation payload, post-create verification, resume, and cleanup."
metadata:
  author: "TaosData"
  version: "0.8.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli analysis --help"
---

# workflow: analysis create

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

## Recommended references

- [`references/analysis-create.md`](references/analysis-create.md)
- [`../idmp-analysis/SKILL.md`](../idmp-analysis/SKILL.md)

## Missing context to resolve first

- Whether the request is natural-language friendly enough for AI-first create.
- Candidate analysis name.
- Runtime expectation.
- AI create prompt seed.
- `idmp-cli ai create create --ack-risk --data '{"elementId":123,"prompt":"demo analysis prompt","record":true}'`
- `idmp-cli analysis analyses new-name --ack-risk --params '{"elementId":123,"name":"demo-analysis"}'`
- `idmp-cli analysis-template analyses new-name --ack-risk --params '{"elementTemplateId":456,"name":"demo-analysis"}'`
- `analysis.analyses.new-name` and `analysis-template.analyses.new-name` require a proposed `name` value.
- Live middle-owner proof plan.
- Whether the workflow is leaf self, middle self, or child aggregation.

## Constrained live behaviors

- Prefer AI draft-first create for natural-language requests: `POST /api/v1/ai/analysis/create` first, then persist the returned draft through `analysis analyses create`.
- The AI draft request body follows `ai.create.create`: keep `prompt`, `record`, `deepThinking`, and `deviceDocument` explicit, plus either `elementId` or `elementTemplateId`.
- Minimal payloads fail in live environments.
- Create success does not guarantee `Running`.
- `new-name` for analyses requires a candidate `name`.
- `rootElementId` is not the current element ID.
- A plain container plus ad-hoc attributes does not unlock self trigger types.
- `element.elements.create` and `element.new.create` do different jobs.
- Keep `startAfterCreated`, `rootElementId`, and output `valueType` explicit in the create payload.
- Trigger-type preflight decides whether the requested scope is valid before any create.
- AI create drafts can contain temporary output attributes or an `id`; remove the draft `id`, inject `rootElementId`, and clean draft-created attributes if persistence fails.
- If AI draft creation fails with a timeout such as `context deadline exceeded`, classify that first attempt as backend AI/API latency and fall back to the structured payload path without mutating the business intent.
- In the current live backend, analysis delete can return success while output attributes remain referenced. Treat cleanup after a proven create or running reread as best-effort instead of a hard create failure.

## Execution flow

1. Use `idmp-cli element elements get --params` and `idmp-cli element elements path --params` to lock the owner and business root.
2. Read dependencies with `idmp-cli attribute elements attributes --params` and `idmp-cli analysis analyses list --params`.
3. For natural-language requests, try AI draft-first create with `idmp-cli ai create create --ack-risk --data '{"elementId":123,"prompt":"...","record":true,"deepThinking":false,"deviceDocument":false}'`, then persist the returned draft through `idmp-cli analysis analyses create --ack-risk --params` after removing `id` and setting `rootElementId`.
4. If the AI draft is unsuitable, persistence fails, or the backend returns a structured AI failure, fall back to the current structured path: reserve/validate with `idmp-cli analysis analyses new-name --ack-risk --params`, `idmp-cli analysis trigger-types list --params`, and `idmp-cli attribute elements attributes-post --ack-risk --params` if the output attribute does not exist.
5. Create and reread through `idmp-cli analysis analyses create --ack-risk --params` and `idmp-cli analysis analyses get --params`.
6. Finish with `idmp-cli analysis analyses resume --ack-risk --params`. Cleanup is best-effort: use `idmp-cli analysis analyses delete --ack-risk --params` only when the draft is abandoned or when the probe must be removed. If delete succeeds but the output attribute remains backend-referenced, record the leaked IDs and stop retrying generic delete loops.

## Exception paths

- Stop when trigger types do not support the requested scope instead of forcing creation.
- If AI create returns an unusable draft, misses required scope details, or persistence fails, clean any draft-only output attributes and continue with the structured workflow instead of retrying the same draft blindly.
- If AI create times out, classify the first attempt as backend AI/API latency and move to the structured payload path without weakening the requested scope or runtime target.
- If reread shows the wrong `rootElementId`, delete the draft and rebuild the payload.
- Temporary output attributes should be deleted when the analysis draft is abandoned. If delete succeeds but the backend still reports those attributes as referred by the analysis, keep the IDs in the evidence and stop cleanup retries.
- Reread immediately and resume if needed.

## Validation scenarios

### 1. Element-mode create on a leaf owner
Run `idmp-cli analysis analyses create --ack-risk --params`, then reread with `idmp-cli analysis analyses get --params`. In shared environments, once `get` and `resume` prove the analysis exists and runs, cleanup stays best-effort.

### 2. Element-mode create on a middle metric owner
Use `idmp-cli analysis trigger-types list --params` to prove the middle owner is metric-bearing. A plain container is not enough.

### 3. Element-mode hierarchy create with child template output
Keep child-scope creation gated by `applyOnSelf=false` trigger types. The payload still needs the child template in `output.elementTemplate.id`, but current live `ELE_SUBET` flows can reuse or create output attributes on the owner element instead of requiring attribute-template IDs.

### 4. Template-mode create with reused attribute template
If template mode is requested, preserve the candidate name and payload discipline. Do not collapse the payload to a guessed minimal DTO.

### 5. Root owner has no trigger types and the attempt must be cleaned up
If preflight fails on the chosen owner, stop before create. Any temporary output attribute created for the failed attempt must be removed, but if the backend leaks references after a proven create or delete, record the leak and stop retrying generic cleanup.
