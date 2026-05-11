---
name: idmp-workflow-panel-build
description: "IDMP panel build workflow. Resolve owner, reserve names, create panel objects, verify query and SQL output, place panels into dashboards, and clean up safely."
metadata:
  author: "TaosData"
  version: "0.7.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli panel --help"
---

# workflow: panel build

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

## Recommended references

- [`references/panel-build.md`](references/panel-build.md)
- [`../idmp-panel/SKILL.md`](../idmp-panel/SKILL.md)

## Missing context to resolve first

- Whether the request is natural-language friendly enough for AI-first panel drafting.
- Candidate panel name.
- Placement plan.
- AI create prompt seed.
- `idmp-cli ai create create-post --ack-risk --data '{"elementId":123,"prompt":"demo panel prompt","record":true}'`
- `idmp-cli panel panels new-name --params '{"elementId":123,"name":"demo-panel"}'`
- Candidate dashboard name.
- `idmp-cli dashboard dashboards new-name --params '{"elementId":123,"name":"demo-dashboard"}'`
- Hierarchy persistence plan.
- Whether the goal is leaf self, middle self, child aggregation, or a text/manual panel.

## Constrained live behaviors

- Prefer AI draft-first create for natural-language panel requests: `POST /api/v1/ai/panels/create` first, then persist the returned draft through `panel.panels.create`.
- `panel verify create` is the time-range-only validator and does not take owner `--params`.
- `panel verify create-post` validates advanced SQL entries.
- Creating a panel does not place it into a dashboard.
- `panel.params` owns the panel time range.
- `dashboard.params` owns dashboard refresh settings.
- If generated SQL is empty, stop before persistence.
- Every advanced fallback must keep a valid `advancedQueryType`.
- `panel.panels.query` and `panel.panels.create` use the panel DTO shape.
- Keep `checked` boolean and `dimensions` as an array of strings.
- Standard child-scope roundtrips can collapse back to self scope.
- Persist the advanced fallback only after reread shows `enableAdvanced=true`; save that SQL with `enableAdvanced=true`. A verified advanced fallback still counts as first-attempt success for child-scope panel work.
- Empty-body `400` responses usually mean the payload shape is wrong.
- AI panel drafts can include an `id`; remove it before persistence. If the AI draft collapses child scope, loses required placement fields, or fails to persist, fall back to the existing structured workflow.

## Execution flow

1. Lock the owner and current shells with `idmp-cli element elements get --params`, `idmp-cli panel panels list --params`, and `idmp-cli dashboard dashboards list --params`.
2. For natural-language requests, try AI draft-first create with `idmp-cli ai create create-post --ack-risk --data`, then persist the returned draft through `idmp-cli panel panels create --ack-risk --params` after removing `id`.
3. If the AI draft is unsuitable, persistence fails, or reread/query proves the draft collapsed scope, fall back to the current structured panel path.
4. Reserve names with `idmp-cli panel panels new-name --params` and `idmp-cli dashboard dashboards new-name --params` when the AI path is skipped or unsuitable.
5. Create or inspect the dashboard shell through `idmp-cli dashboard dashboards create --ack-risk --params` when placement is required.
6. Create the panel object with `idmp-cli panel panels create --ack-risk --params`, then reread with `idmp-cli panel panels get --params`.
7. Validate query behavior in three separate branches: use `idmp-cli panel panels query --ack-risk --params` and `idmp-cli panel panels sqls --ack-risk --params` for the full panel DTO, use `idmp-cli panel verify create --ack-risk --data` only for time-range validation, and use `idmp-cli panel verify create-post --ack-risk --params` only for the advanced child-scope fallback DTO. In the current generated schema, `panel.panels.query` is readonly so `--ack-risk` is optional there, but `panel.panels.sqls` and both `panel.verify.*` commands are still generated as write-risk commands and keep `--ack-risk`. If the no-code child-scope DTO collapses on reread or returns empty-body `400`, keep the verified SQL and persist the advanced fallback instead of restarting the workflow.
8. Attach or update placement with `idmp-cli dashboard dashboards update --ack-risk --params` after the panel is stable.

## Exception paths

- If child-scope query results collapse or SQL is empty, stop and switch to the advanced fallback deliberately.
- If the AI panel draft is malformed, unsuitable for the owner scope, or cannot survive `get/query/sqls` rereads, stop using that draft and continue with the structured DTO family.
- Do not mix dashboard refresh settings into the panel DTO.
- If the advanced fallback rereads with `enableAdvanced=true` and the SQL still matches the intended child scope, count the workflow as successful even when the original no-code DTO did not survive reread.
- Delete temporary dashboard shells or panels when the workflow is only exploratory.

## Validation scenarios

### 1. Leaf self query-backed panel
Use `idmp-cli panel panels create --ack-risk --params`, then `idmp-cli panel panels get --params`. The persisted panel must still query and render on reread.

### 2. Middle self query-backed panel
Keep the same panel DTO family, but verify the middle owner really has metric-bearing context. Query and SQL reads should still succeed.

### 3. Middle child aggregation with advanced-query fallback
Use `idmp-cli panel panels sqls --ack-risk --params` first, then `idmp-cli panel verify create-post --ack-risk --params`. Persist only after the advanced payload is verified, and treat that advanced persistence as the success path whenever the original no-code child-scope DTO collapses on reread.

### 4. Text or manual panel shell
If no SQL-backed panel is needed, keep the object simple and skip advanced verification. The panel still needs a reread after create.

### 5. Panel plus dashboard placement and cleanup
After `idmp-cli dashboard dashboards update --ack-risk --params`, reread the dashboard after `dashboard.dashboards.update`. Remove temporary shells if the workflow was only a probe.
