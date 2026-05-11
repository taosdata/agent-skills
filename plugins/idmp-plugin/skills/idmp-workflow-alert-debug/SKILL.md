---
name: idmp-workflow-alert-debug
description: "IDMP alert debugging workflow. Walk the operator chain from event count and detail to context, acknowledgement, resend, annotations, notify rules, and delivery history."
metadata:
  author: "TaosData"
  version: "0.5.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli event --help"
---

# workflow: alert debug

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

## Recommended references

- [`references/alert-debug.md`](references/alert-debug.md)
- [`../idmp-event/SKILL.md`](../idmp-event/SKILL.md)

## Missing context to resolve first

- Failure boundary.
- Reread window.
- Event scope.
- Notify-rule scope.
- Whether the complaint is “no event opened” or “event opened but delivery failed”.

## Constrained live behaviors

- `confirm` and `resend` have side effects.
- `status=Unack` is the safest default when the operator needs an open event.
- Prefer `analysisId` when correlating an event back to alert creation.
- Notification history can lag behind resend.
- A linked analysis was already deleted in some valid debug branches.
- Capture event evidence before any acknowledge or resend action.

## Execution flow

1. Start with `idmp-cli event count list` and `idmp-cli event events list --params` to decide whether the failure is missing events or missing delivery.
2. Use `idmp-cli event events get --params` and `idmp-cli event events items --params` to lock a single event and its payload.
3. Only after evidence is captured should you consider `idmp-cli event events confirm --ack-risk --params` or `idmp-cli event events resend --ack-risk --params`.
4. Read `idmp-cli notification config list` to confirm the notification side is configured.
5. Finish with `idmp-cli notification page list --params` to inspect delivery history after the event-side review.

## Exception paths

- If no event exists, stop and hand off to alert creation or analysis diagnosis.
- If delivery history is empty right after resend, call out history lag before declaring failure.
- Any temporary debug artifact must be deleted before you leave the workflow.

## Validation scenarios

### 1. Event exists and explains the alert
Use `idmp-cli event events list --params`, then `idmp-cli event events get --params`. The result should prove the alert opened and what the event currently says.

### 2. Delivery failure with no mutation
Use `idmp-cli notification config list` and `idmp-cli notification page list --params` without changing event state. This path is for diagnosis only.

### 3. Acknowledge and resend with evidence captured
Only after reading `idmp-cli event events items --params` should you use `idmp-cli event events confirm --ack-risk --params`. Mutation is never the first debugging step.

### 4. Temporary debug annotation lifecycle
If you add any temporary note while debugging, plan its cleanup explicitly. The workflow is still incomplete until the temporary artifact is removed.

### 5. No event exists
Start with `idmp-cli event count list` and `idmp-cli event events list --params`. If both prove there is no event, stop and report the upstream boundary. Reread `notification page list` after resend only when resend was actually executed.
