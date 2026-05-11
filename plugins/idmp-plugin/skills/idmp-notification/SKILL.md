---
name: idmp-notification
description: "IDMP notification skill. Use it to inspect global notification config, contact points, templates, delivery history, template-level rules, and test-send behavior."
metadata:
  author: "TaosData"
  version: "0.3.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli notification --help"
---

# notification

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

**Before any write:** Follow the [🛑 Destructive op confirmation protocol](../idmp-shared/SKILL.md#-destructive-op-confirmation-mandatory). Read-only commands stay read-only here, but delete / write / patch flows still require the shared yes-gate.


## What this skill covers

- Read global notification configuration, contact points, default contact point, and templates.
- Read delivery history and message details for troubleshooting.
- Distinguish global infrastructure from element or element-template notify rules.
- Use `try-send` only when a real test notification is acceptable.

## Recommended shortcuts

| Shortcut | Purpose |
|----------|---------|
| `+config` | Show notification config |
| `+contacts` | List notification contact points |
| `+default` | Show the default contact point |
| `+details` | List notification delivery details |
| `+rules` | List notification rules for one element template |

## Recommended reference

- [`Notification read flows`](references/notification-read-flows.md)
- [`../idmp-workflow-alert-create/SKILL.md`](../idmp-workflow-alert-create/SKILL.md)
- [`../idmp-workflow-alert-debug/SKILL.md`](../idmp-workflow-alert-debug/SKILL.md)

## Missing context to resolve first

| Context | Why it must be resolved before side effects |
| --- | --- |
| Scope type | Decide whether you are reading global notification infrastructure, element-scoped notify rules, or template-scoped notify rules. |
| Owner scope | If the task touches notify rules, you need the exact `elementId` or `elementTemplateId` first. |
| Delivery intent | Decide whether you only need history and config reads or whether a real `try-send` side effect is allowed. |
| Template ID source | If you do not already know a template `id`, start with the generated template-list command `notification notification templates`. |
| Rule target | Decide which contact point, template, severity, and resend policy the final rule should cover. |
| Verification window | Decide how you will reread delivery history after resend or `try-send`. |

## Constrained live behaviors

- Element-scoped investigations use `notification notify-rules list`; template-scoped investigations use `notification notify-rules list-get`.
- `notification template get` does have a generated list companion, but it lives under the awkward path `notification notification templates`. Use that list before you guess a template ID.
- `try-send` is a real notification side effect when it runs without `--dry-run`, and it should run only when the operator explicitly accepts that validation.
- If the task only needs a safe payload preview on a real event, prefer `try-send --dry-run --ack-risk`; treat that as validation of command shape, not proof that delivery completed.
- `notification page list` is backed by message-detail pages, not by raw resend attempts. A resend can update an existing detail row and append records under it instead of creating a new top-level page row.
- Delivery history can lag behind resend or `try-send`, so reread `notification page list` instead of assuming the first response is final.
- Delivery retries can also be throttled by the event's minimum notification interval, so “no obvious new row yet” is not always a send failure.
- Global notification config and contact points can be healthy even when no rule binds the target event template or severity.
- If the task is really about creating or repairing alert delivery bindings, switch to [`../idmp-workflow-alert-create/SKILL.md`](../idmp-workflow-alert-create/SKILL.md) or [`../idmp-workflow-alert-debug/SKILL.md`](../idmp-workflow-alert-debug/SKILL.md).

## Evidence of completion

- A global config read is only complete when the reread exposes the same config or contact-point object you summarized.
- A rule workflow is only complete when the scoped `notify-rules` reread shows the intended binding on the same owner.
- A delivery proof is only complete when `notification page list` or the message-detail reread reflects the send or resend outcome you claimed.

## Operator workflow

1. Treat `config`, `contact-point`, `default`, and `template` / `templates` as global notification infrastructure.
2. Treat `notify-rules` as bindings on elements or element templates, not as global config.
3. Use `notification notification templates` before `template get` when no template ID is already known.
4. Use `page list` and `details get` for delivery history and message-level troubleshooting.
5. Remember that resend visibility is detail-centric: a retry can land as an extra record under an existing detail instead of a brand-new page row.
6. Use `try-send --dry-run --ack-risk` for safe preview-only validation, and use non-dry-run `try-send` only when the operator explicitly accepts a real notification side effect.
7. After any change, verify by re-reading config or rules and then checking delivery history.

## Key commands

```bash
idmp-cli schema notification.config.list
idmp-cli notification config list

idmp-cli schema notification.list.list
idmp-cli notification list list

idmp-cli schema notification.notification.templates
idmp-cli notification notification templates

idmp-cli schema notification.template.get
idmp-cli notification template get --params '{"id":123}'

idmp-cli schema notification.notify-rules.list-get
idmp-cli notification notify-rules list-get --params '{"elementTemplateId":123}'

idmp-cli schema notification.page.list
idmp-cli notification page list --params '{"current":1,"size":20}'

idmp-cli schema notification.try-send.create-post
idmp-cli notification try-send create-post --ack-risk --data '{...}' --params '{"elementTemplateId":123}'

idmp-cli schema notification.try-send.create
idmp-cli notification try-send create --dry-run --ack-risk --data '{...}' --params '{"elementId":123}'
```

## Exception and failure handling

- Global config is missing or disabled: notify rules may exist but delivery still will not happen.
- Contact-point or template reads fail: confirm the current account has notification administration access.
- You need a template read but have no template ID: use `idmp-cli notification notification templates` first, and create a temporary template fixture only if the environment truly has no reusable template to inspect.
- A template rule list is empty: treat that as “no binding exists yet,” not as proof of a delivery outage.
- Dry-run `try-send` succeeds but there is no notification history: that is expected; dry-run only proves the payload shape and preview path.
- Non-dry-run `try-send` runs but no message arrives: inspect contact points, template content, channel settings, and delivery history.
- Delivery history looks empty after resend: widen the paging or time scope, inspect the existing detail row, and consider minimum-interval throttling before deciding no retry was attempted.

## Validation scenarios

1. Read global notification config with `idmp-cli notification config list`.
2. List contact points with `idmp-cli notification list list`.
3. List templates with `idmp-cli notification notification templates`, then read one template with `idmp-cli notification template get --params '{"id":123}'`.
4. List template rules with `idmp-cli notification notify-rules list-get --params '{"elementTemplateId":123}'`, or list element rules with `idmp-cli notification notify-rules list --params '{"elementId":123}'` when the scope is element mode.
5. Query delivery history with `idmp-cli notification page list --params '{"current":1,"size":20}'`, or preview a safe element-scoped `try-send` with `idmp-cli notification try-send create --dry-run --ack-risk --data '{...}' --params '{"elementId":123}'` when a live test only needs payload validation.
