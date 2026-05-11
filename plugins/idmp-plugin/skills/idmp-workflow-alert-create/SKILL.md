---
name: idmp-workflow-alert-create
description: "IDMP alert creation workflow. Prepare the event template, create the Event-trigger analysis, and treat reread plus Running as success without actively triggering alerts."
metadata:
  author: "TaosData"
  version: "0.7.1"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli analysis --help"
---

# workflow: alert create

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

## Recommended references

- [`references/alert-create.md`](references/alert-create.md)
- [`../idmp-workflow-analysis-create/SKILL.md`](../idmp-workflow-analysis-create/SKILL.md)

## Missing context to resolve first

- Whether the alert intent is natural-language friendly enough for AI-first analysis drafting.
- Candidate analysis name.
- Whether downstream notification routing is in scope after create success.
- Notify target when routing is in scope.
- AI alert prompt seed.
- `idmp-cli ai create create --ack-risk --data '{"elementId":123,"prompt":"alert when ...","record":true}'`
- `idmp-cli event-template events get --params '{"id":789}'`
- `idmp-cli analysis analyses new-name --ack-risk --params '{"elementId":123,"name":"demo-alert"}'`
- Trigger source.
- Non-leaf proof boundary.
- Whether the operator wants only create success or an extra downstream-debug pass later.

## Constrained live behaviors

- `try-send` is not part of create success.
- Write-chain boundary.
- Prefer AI draft-first create for the Event-trigger analysis when the operator starts from natural language; fall back to the structured alert chain when the AI draft is unsuitable or persistence fails.
- `event-template events get` uses `id`.
- `analysis.analyses.new-name` needs a candidate `name` and `--ack-risk`.
- Create or resume the analysis before you write the notify rule.
- If `analysis trigger-types list` for `applyOnSelf=false` does not include `Event`, stop instead of forcing child-scope alert creation.
- Trigger types gate create eligibility; they do not require a real event during create proof.
- Keep `escalationInterval` aligned with the actual notify-rule DTO.
- Create success means the analysis is created, reread, and `Running`.
- Do not write source attributes or replay history just to prove alert creation.
- Real event materialization and notification delivery are optional downstream diagnostics, not part of create success.

## Execution flow

1. Prepare the template side with `idmp-cli event-template events list`, `idmp-cli event-template events get --params`, and `idmp-cli event-template events create --ack-risk` only when no reusable template exists.
2. For natural-language alert requests, try AI draft-first create for the analysis portion with `idmp-cli ai create create --ack-risk --data '{"elementId":123,"prompt":"alert when ...","record":true,"deepThinking":false,"deviceDocument":false}'`, then persist the returned draft through `idmp-cli analysis analyses create --ack-risk --params` after removing `id` and injecting `rootElementId`.
3. If the AI draft does not preserve the required event template, severity, scope, or output bindings, fall back to the current structured alert flow.
4. Reserve the analysis name with `idmp-cli analysis analyses new-name --ack-risk --params`, then prove scope support with `idmp-cli analysis trigger-types list --params`.
5. Create the missing output attribute only if required by using `idmp-cli attribute elements attributes-post --ack-risk --params`.
6. Create and reread the alert analysis via `idmp-cli analysis analyses create --ack-risk --params` and `idmp-cli analysis analyses get --params`.
7. Resume the analysis with `idmp-cli analysis analyses resume --ack-risk --params`. Success means `analysis analyses get` reread plus `analysis analyses resume` reaching `Running`.
8. If downstream routing is explicitly in scope after the analysis is already `Running`, inspect or add notify-rule coverage with `idmp-cli notification notify-rules list --params`, `idmp-cli notification notify-rules create --ack-risk --params`, and `idmp-cli notification notify-rules update --ack-risk --params`.
9. Clean up abandoned drafts with `idmp-cli analysis analyses delete --ack-risk --params`.

For command-family coverage, the core create flow touches these steps in order: `idmp-cli event-template events list`, `idmp-cli event-template events get --params`, `idmp-cli analysis analyses new-name --ack-risk --params`, `idmp-cli analysis trigger-types list --params`, `idmp-cli attribute elements attributes-post --ack-risk --params`, `idmp-cli analysis analyses create --ack-risk --params`, `idmp-cli analysis analyses get --params`, and `idmp-cli analysis analyses resume --ack-risk --params`. Optional post-create routing can also use `idmp-cli notification notify-rules list --params`, `idmp-cli notification notify-rules create --ack-risk --params`, and `idmp-cli notification notify-rules update --ack-risk --params` after the analysis is already `Running`.

## Exception paths

- Stop immediately when child-scope trigger types do not include `Event`.
- If the AI draft does not survive persistence or comes back without the required Event-trigger fields, clean any draft-only output attributes and resume from the structured alert path.
- If `analysis analyses get --params` succeeds but `analysis analyses resume --ack-risk --params` does not leave the analysis in `Running`, classify the attempt as create incomplete or runtime-start boundary.
- A missing real event is not a create failure for this skill.
- `analysis attribute list`, `attribute write-data create`, `analysis analyses fill-history`, `event events list`, `event events confirm`, and `notification try-send create` belong to later debugging or delivery validation, not to create proof.
- Delete temporary output attributes, notify rules, or draft analyses when a proof attempt is abandoned.

## Validation scenarios

### 1. Leaf owner strict live proof
Use the chain from `idmp-cli analysis analyses create --ack-risk --params` through `idmp-cli analysis analyses resume --ack-risk --params`. Success is create + reread + `Running`; do not replay source data just to open a real event.

### 2. Middle owner strict replay proof
Keep the same create chain, but require only explicit evidence that the non-leaf self analysis was created, reread, and reached `Running`. Trigger support gates create eligibility; it does not require event materialization.

### 3. Middle child aggregation must stop when `Event` is unavailable
Run `idmp-cli analysis trigger-types list --params` first. If `Event` is absent for `applyOnSelf=false`, stop and report the boundary without forcing create.

### 4. New event template plus notify-rule reuse
Read event-template and notify-rule state separately before writing. Reuse a working notify rule when possible instead of duplicating it, but treat notify-rule work as optional follow-up after create success.

### 5. Template-mode alert workflow
Preserve the same proof discipline in template mode: scope check, create, reread, and `Running`. Do not call the workflow successful on template reads alone, and do not require real event materialization.
