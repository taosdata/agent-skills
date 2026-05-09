---
name: idmp-panel
description: "IDMP panel skill for listing panels, reading details, creating and validating panel queries, and separating panel lifecycle from dashboard placement."
metadata:
  author: "TaosData"
  version: "0.5.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli panel --help"
---

# panel

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

**Before any write:** Follow the [🛑 Destructive op confirmation protocol](../idmp-shared/SKILL.md#-destructive-op-confirmation-mandatory). Read-only commands stay read-only here, but delete / write / patch flows still require the shared yes-gate.


## Recommended shortcuts

| Shortcut | Purpose |
|----------|---------|
| `+list` | List panels under one element. |
| `+search` | Search panels globally. |
| `+templates` | List panel templates available to one element. |

## Recommended references

- [`panel read flows`](references/panel-read-flows.md)
- [`../idmp-workflow-panel-build/SKILL.md`](../idmp-workflow-panel-build/SKILL.md)

## Missing context to resolve first

| Context | Why it must be resolved before create or verify |
| --- | --- |
| Owner element | You need the final `elementId` for list, get, naming, create, and every verification call. |
| Candidate panel name | `panel.panels.new-name` requires both `elementId` and a proposed `name`. |
| Verification mode | Decide whether this panel should generate SQL at all, and whether you need plain `query` and `sqls` checks or advanced-query verification. |
| Dashboard placement target | Decide whether the panel remains standalone or must be inserted into a dashboard before the workflow counts as complete. |
| Refresh owner | Decide whether refresh belongs on the panel shell or the dashboard shell so `refreshInterval` lands in the right `params` block. |

## Constrained live behaviors

- Prefer `POST /api/v1/ai/panels/create` for natural-language panel requests, then persist the returned draft through `panel.panels.create`. Use the structured panel DTO workflow only as fallback when the draft is unsuitable or persistence fails.
- `panel.panels.new-name` requires a candidate `name`; do not call it with only the owner scope.
- Text and manual panels can legitimately return `generated SQL is empty`, so `query` is inapplicable for those panel types.
- `panel verify create` validates only the time-range payload with `from` and `to`; use plain `--data`, not `--params`, and do not send `elementId`.
- `panel.panels.query` and `panel.panels.create` use the panel DTO shape. `panel.panels.sqls` uses the same DTO together with owner `--params`.
- `panel verify create-post` is only for advanced-query payloads. Keep `uuid`, `advancedQueryType`, `querySqls`, and the advanced query fields inside that single DTO.
- If a child-scope no-code DTO collapses to self scope on reread or returns empty-body `400`, capture the working SQL and switch to the advanced fallback instead of treating the first attempt as a total panel failure.
- If the backend returns HTTP 400 with an empty body on panel query, verify, or create, assume a DTO-shape mismatch first and recheck the typed schema output before retrying.
- `refreshInterval` belongs in `params` on the object that owns refresh behavior, not in an arbitrary top-level field.
- Creating a panel does not place it into a dashboard automatically; a separate dashboard update is still required.

## Evidence of completion

- A panel create is only complete when `panel panels get` rereads the persisted object with the intended owner, name, and params.
- A query-backed panel is only complete when the same DTO succeeds through `panel.panels.query` or `panel.panels.sqls`.
- An advanced fallback is only complete when reread shows `enableAdvanced=true` and the advanced DTO still validates. For child-scope workflows, this advanced fallback still counts as first-attempt success when the no-code payload collapsed but the verified SQL stayed correct.
- Dashboard placement is separate proof; do not treat a panel create as dashboard membership.

## Product behavior to preserve

- Read `list` first, then `get`, before changing a panel.
- For natural-language creation asks, prefer the AI draft endpoint first and keep structured DTO creation as the fallback.
- Use `new-name` with a candidate `name` before creating a panel.
- Run `query` and `sqls` only for panels that should generate SQL, and use `verify` only for the single advanced-query DTO rather than the full panel DTO.
- When `advancedQueries` is present, keep `checked` boolean and `dimensions` as an array of strings.
- `refreshInterval` belongs in `params` on the object that owns refresh behavior, not in an arbitrary top-level field.
- Creating a panel does not place it into a dashboard automatically.

## Key commands

```bash
idmp-cli schema panel.panels.list
idmp-cli panel panels list --params '{"elementId":123}'

idmp-cli schema panel.panels.get
idmp-cli panel panels get --params '{"elementId":123,"panelId":456}'

idmp-cli schema panel.verify.create
idmp-cli panel verify create --ack-risk --data '{"from":"now-12h","to":"now"}'

idmp-cli schema panel.verify.create-post
idmp-cli panel panels new-name --params '{"elementId":123,"name":"demo-panel"}'
idmp-cli panel panels create --dry-run --ack-risk --params '{"elementId":123}' --data '{...}'

# In the current generated schema, `panel.panels.query` is readonly and `--ack-risk` is optional,
# but `panel.panels.sqls`, `panel.verify.create`, and `panel.verify.create-post` are still generated
# as write-risk commands and must keep `--ack-risk`.
idmp-cli panel panels query --ack-risk --params '{"elementId":123}' --data '{...}'
idmp-cli panel panels sqls --ack-risk --params '{"elementId":123}' --data '{...}'
idmp-cli panel verify create-post --ack-risk --params '{"elementId":123}' --data '{...}'

idmp-cli panel panel-templates list --params '{"elementId":123}'
```

## Exception and failure handling

- If a panel is created successfully but no dashboard is updated, the panel remains standalone by design.
- If `refreshInterval` is set outside `params`, treat the payload as incomplete and fix it before retrying.
- If a text or manual panel returns empty SQL, skip `query` and treat SQL-based validation as inapplicable for that panel type.
- If `panel verify create` fails, send only the time-range payload with `from` and `to`; it is not the advanced-query validator.
- If `panel verify create-post` fails with missing `uuid` or `advancedQueryType`, you passed a plain panel DTO instead of an advanced-query DTO.
- If panel query, verify, or create returns HTTP 400 with an empty body, compare the typed `schema` output against your payload before changing the SQL itself.
- If child-scope no-code rereads collapse to self scope but `panel.panels.sqls` already proved the intended grouped SQL, persist the advanced fallback instead of restarting from an unrelated self-scope DTO.
- If the panel was copied from a template, create a new panel instead of assuming the copied identifier is updatable.
- If a time range returns empty data, adjust the query window before changing metrics or dimensions.

## Validation scenarios

1. Read the panel list with `idmp-cli schema panel.panels.list` and `idmp-cli panel panels list --params '{"elementId":123}'`.
2. Reserve a create-safe name with `idmp-cli panel panels new-name --params '{"elementId":123,"name":"demo-panel"}'`.
3. Preview panel creation with `idmp-cli panel panels create --dry-run --ack-risk --params '{"elementId":123}' --data '{...}'`.
4. Run SQL-based checks only when the panel should generate SQL: use `idmp-cli panel panels query --ack-risk --params '{"elementId":123}' --data '{...}'` and `idmp-cli panel panels sqls --ack-risk --params '{"elementId":123}' --data '{...}'` for query-backed panels, use `idmp-cli panel verify create --ack-risk --data '{"from":"now-12h","to":"now"}'` only for time-range validation, and use `idmp-cli panel verify create-post --ack-risk --params '{"elementId":123}' --data '{...}'` only for advanced-query DTOs that include fields such as `uuid` and `advancedQueryType`. If the child-scope no-code branch collapses, switch to the advanced fallback and keep that as the success path.
5. Confirm template reuse or separate dashboard work with `idmp-cli panel panel-templates list --params '{"elementId":123}'` and `idmp-cli dashboard dashboards get --params '{"elementId":123,"dashboardId":789}'`.
