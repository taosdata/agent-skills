# dashboard read flow

Use this reference to inspect dashboard inventory and decide whether the next step belongs to dashboard mutation or panel-building.

## Read-first sequence

1. Start from the owner scope:

   ```bash
   idmp-cli dashboard dashboards list --params '{"elementId":123}'
   idmp-cli dashboard dashboards get --params '{"elementId":123,"dashboardId":456}'
   ```

2. When the operator wants reuse or cloning paths:

   ```bash
   idmp-cli dashboard dashboard-templates list --params '{"elementId":123}'
   ```

3. When the operator only knows a keyword:

   ```bash
   idmp-cli dashboard dashboards search --params '{"keyword":"energy","current":1,"size":20}'
   ```

## What to conclude from reads

- if the dashboard exists but the target panel is missing or wrong, hand off to `../idmp-workflow-panel-build/SKILL.md`
- if the dashboard layout is correct and only the ordering or top-pinning is wrong, dashboard mutation is enough
- if the operator wants a reusable artifact for other owners, prefer template creation after the dashboard itself is stable

## Write handoff points

### Layout-only follow-up

```bash
idmp-cli dashboard dashboards update --dry-run --ack-risk --params '{"elementId":123,"dashboardId":456}' --data '{...}'
idmp-cli dashboard dashboards make-top --dry-run --ack-risk --params '{"elementId":123,"dashboardId":456}'
```

### Reuse follow-up

```bash
idmp-cli dashboard template create --dry-run --ack-risk --params '{"elementId":123,"dashboardId":456}'
```

## One-shot rules

1. Always resolve the concrete owner and dashboard first.
2. Treat missing or broken panels as a panel-build problem before treating it as a dashboard problem.
3. Use dry-run on dashboard writes first.
