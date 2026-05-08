# alert debug flow

Use this reference after the main workflow doc. The most important question is whether the alert failed before event creation or after event creation.

## Failure-boundary matrix

| Symptom | Boundary | First proving command |
| --- | --- | --- |
| no event count, no matching event | generation failed upstream | `event count list`, then `event events search` |
| event exists but no operator notification | delivery path | `event events get`, then notification config and rule reads |
| resend succeeded but no obvious new top-level history row | history visibility or throttling | `notification page list` plus detail reread |
| event detail exists but `items` is weak or stale | old event or missing upstream context | reread a fresher event or the producing analysis |

## Evidence capture sequence

Capture evidence before any mutation:

```bash
idmp-cli event count list
idmp-cli event events list --params '{"current":1,"size":20}'
idmp-cli event events get --params '{"eventId":123}'
idmp-cli event events items --params '{"eventId":123}'
idmp-cli event annotations list --params '{"eventId":123}'
```

## Event-side actions

Only after the evidence capture:

```bash
idmp-cli event events confirm --ack-risk --params '{"eventId":123}'
idmp-cli event events resend --ack-risk --params '{"eventId":123}'
idmp-cli event annotations create --ack-risk --params '{"eventId":123}' --data '{...}'
```

Semantics:

- `confirm` changes acknowledgement state
- `resend` retries delivery only
- neither command recreates the original event condition

## Notification-side reads

```bash
idmp-cli notification config list
idmp-cli notification list list
idmp-cli notification default list
idmp-cli notification notify-rules list --params '{"elementId":123}'
idmp-cli notification notify-rules list-get --params '{"elementTemplateId":456}'
idmp-cli notification page list --params '{"current":1,"size":20}'
```

Use element-scope or template-scope rules intentionally. They are not interchangeable.

## Delivery reread strategy

After resend:

1. reread `notification page list`
2. widen the time window or page scope if nothing obvious changed
3. remember that resend can append under an existing detail instead of creating a fresh top-level row
4. remember that minimum notification interval throttling can suppress a visible retry

## Handback rules

- If no event exists, hand the case back to `../idmp-workflow-alert-create/SKILL.md` and debug generation, not delivery.
- If the event exists but no applicable notify rule exists, hand the case back to alert create to repair the binding.
- If global config or contact points are broken, this is notification infrastructure, not event generation.

## One-shot checklist

1. Decide the failure boundary first.
2. Capture event evidence before mutation.
3. Mutate only when the operator explicitly wants ack or resend.
4. Reread notification history with a wider lens than a single new row.
5. Hand off to alert-create when the problem is binding or event generation.
