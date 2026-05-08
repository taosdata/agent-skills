---
name: idmp-openapi-explorer
description: "IDMP OpenAPI explorer skill. Use it to inspect schema paths, required inputs, and generated commands; fall back to raw API only after schema and generated commands are exhausted."
metadata:
  author: "TaosData"
  version: "0.3.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli schema --help"
---

# OpenAPI Explorer

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

## What this skill covers

- Find the exact `service.resource.method` for an IDMP operation.
- Inspect required path, query, and body inputs before execution.
- Prefer generated commands for validation, paging, and risk handling.
- Use raw API only as a controlled fallback.

## Recommended reference

- [`OpenAPI explorer`](references/openapi-explorer.md)

## Missing context to resolve first

| Context | Why it must be resolved before a raw or generated write |
| --- | --- |
| Target operation | You need the exact `service.resource.method` or raw API path before you can trust the payload shape. |
| Owner scope | Path or query IDs such as `elementId`, `elementTemplateId`, or `eventId` must be fixed before mutation. |
| Generated-command availability | Decide whether a structured command already exists before falling back to raw API. |
| Verification target | Decide which follow-up read will prove the write actually matched the intended scope. |
| Risk level | Decide whether the operation is safe for preview only or for a real `--ack-risk` execution. |

## Constrained live behaviors

- For writes, inspect schema first, preview with `--dry-run`, execute with `--ack-risk`, and verify by reading the result back.
- Prefer generated commands whenever they exist; raw API is the controlled fallback, not the default path.
- A schema path that looks close is not good enough for mutation; confirm the exact path and required body before sending the write.
- Raw API success is not proof of correctness unless the equivalent generated-command scope and reread match.

## Operator workflow

1. Start with the nearest domain skill first, such as element, attribute, analysis, panel, dashboard, event, notification, or a workflow skill.
2. Use `idmp-cli schema` or `idmp-cli schema search` to identify the exact schema path, risk level, and required fields.
3. Prefer generated commands after the schema check so validation, paging, and risk prompts stay intact.
4. Use raw API only when no generated command covers the case or when low-level request confirmation is necessary.
5. For writes, inspect schema first, preview with `--dry-run`, execute with `--ack-risk`, and verify by reading the result back.

## Key commands

```bash
idmp-cli schema
idmp-cli schema search element
idmp-cli schema element.elements.list
idmp-cli schema attribute.historydata.list

idmp-cli element elements list --params '{"parentId":123}'
idmp-cli attribute historydata list --params '{"elementId":1,"attributeId":2,"current":1,"size":20,"start":1704067200000,"end":1704153600000}'

idmp-cli api GET /api/v1/elements --params '{"parentId":123}'
idmp-cli api POST /api/v1/elements/batch/attributes/data --data '{"elementIds":[123],"attributeNames":["temperature"]}'
idmp-cli api POST /api/v1/elements/batch/attributes/data --ack-risk --dry-run --data '{"elementIds":[123],"attributeNames":["temperature"]}'
```

## Exception paths

- `schema search` returns no match: broaden the search term, inspect the adjacent domain, and only then consider raw API.
- A generated command exists but validation fails: fix the inputs using `idmp-cli schema ...` instead of switching immediately to raw API.
- The panel verify split is unclear: `panel verify create` only accepts the time-range body with `from` and `to` via plain `--data`; owner params such as `elementId` and full panel DTO fields belong on `panel.panels.query` / `panel.panels.create`, while `panel verify create-post` is reserved for the advanced-query DTO.
- A paginated read looks incomplete: use `--page-all`, `--page-limit`, and a small `--page-delay`.
- Raw API works but the product still looks wrong: confirm you used the same IDs, scope, and root context as the generated command flow.
- A write path is unclear: stop, inspect schema again, and do not guess the request body.

## Validation scenarios

1. Find a schema path with `idmp-cli schema search element`.
2. Inspect an exact schema such as `idmp-cli schema element.elements.list`.
3. Run the corresponding generated command for a known element scope.
4. Inspect a second schema in another domain, such as `attribute.historydata.list`.
5. Use a raw API call only after the schema check with `idmp-cli api POST /api/v1/elements/batch/attributes/data --data '{"elementIds":[123],"attributeNames":["temperature"]}'`, then confirm the safe preview path and the generated-command behavior still match.
