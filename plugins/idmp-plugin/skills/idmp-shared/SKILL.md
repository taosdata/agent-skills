---
name: idmp-shared
description: "Shared IDMP CLI rules for choosing element mode vs template mode, resolving business-root rootElementId, acknowledging risky writes, and verifying results."
metadata:
  author: "TaosData"
  version: "0.4.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli --help"
---

# Shared IDMP CLI rules

## 🛑 Destructive op confirmation (mandatory)

Before executing any `DELETE`, non-readonly `POST` / `PUT` / `PATCH`, `--ack-risk` command, or local destructive helper (`config remove` / `profile remove` / `auth logout --clear`), the agent MUST print the 4 items below and then **wait for an explicit user `yes`** before running the command:

1. **Target** — resource type + id + name + owning element / template / profile.
2. **Action** — HTTP method + path + `schemaPath` + param summary (mask secrets).
3. **Reason** — why this operation is needed (trace it back to the user's request; if it is a rollback of a failed previous step, say so).
4. **Blast radius** — dependent analyses / panels / dashboards / alerts / notifications; whether the action is reversible; whether sub-objects are deleted transitively; cross-profile impact.

Read-only commands (`get`, `list`, `search`, `path`, `tree`, `new-name`, `*-search`, `*-query`, `forecast`) do not require this confirmation. For detailed wording and the ready-to-use template, see `references/idmp-safety-rules.md`.

## Two working modes

| Mode | CLI families | Use when |
| --- | --- | --- |
| element mode | `idmp-cli element ...`, `attribute ...`, `analysis ...`, `panel ...`, `dashboard ...`, `event ...` | The target is a real element, live data, a live dashboard, or a live event. |
| template mode | `idmp-cli template ...`, `attr-template ...`, `analysis-template ...`, `panel-template ...` | The target is a reusable template, template attribute, or template analysis. |

Pick the mode first. Do not mix `elementId` and `elementTemplateId`.

## Preflight

```bash
idmp-cli config init --server http://your-idmp:6042 --username admin@example.com
idmp-cli doctor --offline
idmp-cli auth check
idmp-cli auth list
idmp-cli doctor
```

If login is required:

```bash
printf '%s\n' "$IDMP_E2E_PASSWORD" | idmp-cli auth login --username "$IDMP_E2E_USERNAME" --password-stdin
```

## Recommended shared references

- [`preflight checklist`](references/preflight-checklist.md)
- [`expression rules`](references/expression-rules.md)
- [`chart-type guide`](references/chart-type-guide.md)
- [`error recovery`](references/error-recovery.md)

## Missing context to resolve first

| Context | Why it must be explicit |
| --- | --- |
| Working mode | Every create and update path depends on choosing `element mode` or `template mode` first. |
| Owner | You need the final `elementId` or `elementTemplateId` before you can discover names, trigger types, or related objects. |
| Business root | Element-mode writes often need a higher `rootElementId` from `element path`, even when the real write must move to a leaf owner. Treat `rootElementId` as the business-root ancestor, not as a synonym for the final leaf owner. |
| Candidate name seed | `analysis.analyses.new-name`, `panel.panels.new-name`, and `dashboard.dashboards.new-name` all need a proposed `name`; do not call them with only the owner ID. |
| Scope details | Decide `applyOnSelf`, child-template scope, and whether the workflow targets a real data-bearing leaf before any mutating request. |
| Verification target | Decide which `get`, `list`, runtime state, event, or delivery reread will prove that the workflow really finished. |

## Constrained live behaviors

- Treat every write as incomplete until a follow-up `get`, `list`, runtime check, or delivery reread proves the backend kept the change.
- Do not assume a historical `demo` root exists. Start from the currently visible first-level root that owns the shared leaf fixtures, then create any temporary middle-scope owners under that real tree.
- If `trigger-types list` is empty on the current owner, move the create flow to a data-bearing leaf element and keep the business root as `rootElementId`.
- Use `new-name` only with the correct payload shape. Analyses, panels, and dashboards need both the owner and a candidate `name`; attribute `new-name` only needs the owner scope. `analysis.analyses.new-name` is a POST reserve call and still requires `--ack-risk`, while panel/dashboard/attribute `new-name` commands remain readonly.
- Shared environments often require fixture reuse. Notify rules are typically updated in place because the documented create and update paths do not come with a matching delete flow here.
- For alert validation, `event.events.list --params '{"analysisId":...}'` is more reliable than filtering only by `status=Unack` in a noisy shared environment.
- Successful config writes do not prove runtime behavior. Analyses can remain `Ready`, alerts can need `fill-history`, and notification history can lag behind resend or new-event creation.

## Evidence of completion

- A CLI success line is not proof by itself.
- For create flows, reread the object and confirm the final `id`, owner scope, reserved name, and expected status bits.
- For update flows, reread the same object and confirm the changed field persisted on the backend.
- For delete flows, prove absence through a scoped `list` reread or a structured not-found `get`.
- For element-mode writes, prove the business-root boundary with `element elements path` plus `element fullpath get` before you reuse `rootElementId`.

## Standard read-before-write flow

1. Locate the target with `search`, `list`, or `path`.
2. Read the current state with `get`, `attributes`, `analyses list`, or the relevant list endpoint.
3. Resolve dependencies such as `new-name`, `sub-templates`, `trigger-types`, and any contact-point or event-template prerequisites.
4. Inspect the schema, preview with `--dry-run`, and add `--ack-risk` for non-read-only generated commands.
5. Verify with `get` or `list`; resume the object if the product expects a running state.

## Key product rules

- In element mode, `rootElementId` comes from the business root in the element path, not from the current leaf element. The leaf owner and the business root are separate write inputs.
- `applyOnSelf=false` means the configuration depends on child-template or hierarchical scope; read `sub-templates` and `trigger-types` first.
- Use `new-name` before creating attributes, analyses, panels, or dashboards when that helper exists, and provide the correct payload shape for that helper.
- Keep credentials in profiles, environment variables, or stdin only.
- Prefer generated service commands; use `idmp-cli api` only when no structured command is sufficient.

## Key commands

```bash
idmp-cli schema element.elements.sub-templates
idmp-cli schema analysis.analyses.create
idmp-cli schema attribute.elements.attributes-post
idmp-cli element elements search --params '{"keyword":"beijing","current":1,"limitSize":20}'
idmp-cli element elements path --params '{"elementId":123}'
idmp-cli analysis analyses list --params '{"elementId":123,"current":1,"size":20}'
```

## Exception and failure handling

- If `idmp-cli auth check` or `idmp-cli doctor` fails, stop mutating work until the session and connectivity are healthy again.
- If the task starts with a template but the command expects `elementId` (or the reverse), switch modes instead of forcing the request.
- If the path lookup does not clearly show the business root, do not reuse the leaf element as `rootElementId`; resolve the path first. An unclear path is one where `element elements path`, `element fullpath get`, and `element by-path list` do not round-trip to the same root-to-leaf chain.
- If a create flow reserves a temporary output attribute or default name and the main object is canceled or rejected, clean up the temporary artifact before retrying.
- If a write reports success but the follow-up `get` or `list` does not show the change, treat the workflow as incomplete and re-read before sending another mutation.

## Live test environment variables

Only use:

- `IDMP_E2E_ENABLED`
- `IDMP_BASE_URL`
- `IDMP_E2E_USERNAME`
- `IDMP_E2E_PASSWORD`

## Validation scenarios

1. Confirm local readiness with `idmp-cli doctor --offline`.
2. Confirm the active session with `idmp-cli auth check`.
3. Validate the chosen mode by comparing `idmp-cli schema element.elements.search` and `idmp-cli schema template.elements.get`.
4. Resolve the business root before a write with `idmp-cli element elements path --params '{"elementId":123}'`.
5. Preview and verify a mutating workflow with `idmp-cli schema analysis.analyses.create` followed by `idmp-cli analysis analyses list --params '{"elementId":123,"current":1,"size":20}'`.
