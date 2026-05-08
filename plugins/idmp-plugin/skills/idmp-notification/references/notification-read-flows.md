# notification read flow

Use this reference to inspect delivery infrastructure and decide whether the issue belongs to notification configuration, notify-rule binding, or alert debugging.

## Read-first sequence

1. Read global config and contact points:

   ```bash
   idmp-cli notification config list
   idmp-cli notification list list
   idmp-cli notification default list
   ```

2. Read templates and contact-point detail:

   ```bash
   idmp-cli notification notification templates
   idmp-cli notification template get --params '{"id":123}'
   idmp-cli notification contact-point get --params '{"id":456}'
   ```

3. Inspect delivery details:

   ```bash
   idmp-cli notification page list --params '{"current":1,"size":20}'
   idmp-cli notification details get --params '{"id":789}'
   ```

4. Read concrete notify-rule bindings:

   ```bash
   idmp-cli notification notify-rules list --params '{"elementId":123}'
   idmp-cli notification notify-rules list-get --params '{"elementTemplateId":123}'
   ```

## Boundary decisions

- if the global config or contact point is broken, this is notification infrastructure
- if notify rules are missing or mismatched, hand off to `../idmp-workflow-alert-create/SKILL.md`
- if rules exist and the event already exists, hand off to `../idmp-workflow-alert-debug/SKILL.md`

## Safe write handoff

```bash
idmp-cli notification template create --dry-run --ack-risk --data '{...}'
idmp-cli notification contact-point create --dry-run --ack-risk --data '{...}'
```

## One-shot rules

1. `notification page list` is the paged delivery-detail view; resend may not create a brand-new top-level row.
2. Widen time or page scope before concluding that resend produced nothing.
