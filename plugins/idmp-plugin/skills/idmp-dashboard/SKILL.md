---
name: idmp-dashboard
description: "IDMP dashboard skill for listing dashboards, reading details, updating layout and order, templating stable dashboards, and keeping dashboard lifecycle separate from panel lifecycle."
metadata:
  author: "TaosData"
  version: "0.6.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli dashboard --help"
---

# dashboard

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

**Before any write:** Follow the [🛑 Destructive op confirmation protocol](../idmp-shared/SKILL.md#-destructive-op-confirmation-mandatory). Read-only commands stay read-only here, but delete / write / patch flows still require the shared yes-gate.


## Recommended shortcuts

| Shortcut | Purpose |
|----------|---------|
| `+list` | List dashboards under one element. |
| `+search` | Search dashboards globally. |
| `+templates` | List dashboard templates available to one element. |

## Recommended reference

- [`dashboard read flows`](references/dashboard-read-flows.md)
- [`../idmp-workflow-panel-build/SKILL.md`](../idmp-workflow-panel-build/SKILL.md)

## Missing context to resolve first

| Context | Why it must be resolved before create or update |
| --- | --- |
| Owner element | You need the final `elementId` before you can list, get, create, reorder, or template dashboards. |
| Candidate dashboard name | `dashboard.dashboards.new-name` requires both `elementId` and a proposed `name`. |
| Panel placement plan | Decide which panel IDs should appear in the dashboard and whether panel creation must happen first. |
| Refresh owner | Dashboard refresh belongs in `dashboard.params`, so you need to know whether the dashboard shell owns refresh behavior. |
| Verification target | Decide whether the final proof is layout readback, panel membership, ordering, template readiness, or all of them. |

## Constrained live behaviors

- `dashboard.dashboards.new-name` requires a candidate `name`; do not call it with only the owner scope.
- `refreshInterval` belongs in `dashboard.params`, not in a top-level field.
- Creating a panel does not add it to a dashboard automatically; dashboard membership is a separate update path.
- `make-top` only changes ordering. It does not replace layout edits or dashboard content updates.
- Deleting or editing a dashboard does not delete the underlying panels by itself.
- Removing a panel from a dashboard must be verified by rereading the dashboard layout and the standalone panel inventory; a dashboard update does not delete the panel object.
- After membership changes, reread both the dashboard and the standalone panel inventory before you conclude the change is complete.

## Evidence of completion

- A dashboard create is only complete when `dashboard dashboards get` or `dashboard dashboards list` returns the new shell with the intended owner.
- A layout or membership update is only complete when both the dashboard reread and the standalone panel inventory reflect the intended state.
- Ordering work is only complete when a reread shows the new position; `make-top` does not stand in for broader layout proof.

## Product behavior to preserve

- Read `list` first, then `get`, before changing a dashboard.
- Use `new-name` with a candidate `name` before creating a dashboard shell.
- `refreshInterval` belongs in `dashboard.params`, not in a top-level field.
- Creating a panel does not add it to a dashboard; dashboard membership is managed separately.
- Deleting or changing a dashboard does not delete the underlying panels by itself.
- After removing a panel from `dashboard.panels`, reread both the dashboard and the panel inventory before you conclude the layout change is complete.

## Key commands

```bash
idmp-cli schema dashboard.dashboards.list
idmp-cli dashboard dashboards list --params '{"elementId":123}'

idmp-cli schema dashboard.dashboards.get
idmp-cli dashboard dashboards get --params '{"elementId":123,"dashboardId":456}'

idmp-cli dashboard dashboards search --params '{"keyword":"energy","current":1,"size":20}'
idmp-cli dashboard dashboards new-name --params '{"elementId":123,"name":"demo-dashboard"}'

idmp-cli dashboard dashboards create --dry-run --ack-risk --params '{"elementId":123}' --data '{...}'
idmp-cli dashboard dashboards update --dry-run --ack-risk --params '{"elementId":123,"dashboardId":456}' --data '{...}'
idmp-cli dashboard dashboards make-top --ack-risk --params '{"elementId":123,"dashboardId":456}'
idmp-cli dashboard dashboards make-top --dry-run --ack-risk --params '{"elementId":123,"dashboardId":456}'

idmp-cli dashboard dashboard-templates list --params '{"elementId":123}'
```

## Exception and failure handling

- If a panel exists but does not appear in a dashboard, update the dashboard explicitly; panel creation alone is not enough.
- If `refreshInterval` is placed outside dashboard `params`, the dashboard will not behave as intended; correct the payload before retrying.
- If `make-top` succeeds, expect only ordering changes; do not use it as a substitute for layout edits.
- If an update succeeds but `get` still shows an old layout or `panelIds`, reread immediately before sending another mutation. If the mismatch remains, report stale state instead of retrying blindly.
- If a dashboard is removed, plan for panels to remain available until they are deleted separately.

## Validation scenarios

1. Read the dashboard list with `idmp-cli schema dashboard.dashboards.list` and `idmp-cli dashboard dashboards list --params '{"elementId":123}'`.
2. Read one dashboard in detail with `idmp-cli dashboard dashboards get --params '{"elementId":123,"dashboardId":456}'`.
3. Check discovery and naming with `idmp-cli dashboard dashboards search --params '{"keyword":"energy","current":1,"size":20}'` and `idmp-cli dashboard dashboards new-name --params '{"elementId":123,"name":"demo-dashboard"}'`.
4. Preview structure changes with `idmp-cli dashboard dashboards update --dry-run --ack-risk --params '{"elementId":123,"dashboardId":456}' --data '{...}'`, then apply the membership change and reread both the dashboard and the standalone panel inventory.
5. Verify ordering and template readiness with `idmp-cli dashboard dashboards make-top --ack-risk --params '{"elementId":123,"dashboardId":456}'`, then preview the same operation with `--dry-run` and check `idmp-cli dashboard dashboard-templates list --params '{"elementId":123}'`.
