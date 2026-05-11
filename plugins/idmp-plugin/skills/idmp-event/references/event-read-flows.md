# event read flow

Use this reference to inspect current event state before deciding whether the next action is acknowledgement, resend, or alert debugging.

## Read-first sequence

1. Start from event volume:

   ```bash
   idmp-cli event count list
   ```

2. Then inspect list or search results:

   ```bash
   idmp-cli event events list --params '{"current":1,"size":20}'
   idmp-cli event events search --params '{"keyword":"overcurrent","current":1,"size":20}'
   ```

3. When the event ID is known, drill into detail and context:

   ```bash
   idmp-cli event events get --params '{"eventId":123}'
   idmp-cli event events items --params '{"eventId":123}'
   idmp-cli event annotations list --params '{"eventId":123}'
   ```

## Action handoff

- if no event exists for the expected condition, switch to `../idmp-workflow-alert-debug/SKILL.md`
- if the event exists and the operator only wants acknowledgement or resend, stay in the event skill

## Mutating actions

```bash
idmp-cli event events confirm --dry-run --ack-risk --params '{"eventId":123}'
idmp-cli event confirm create --dry-run --ack-risk --data '[123,456]'
idmp-cli event events resend --dry-run --ack-risk --params '{"eventId":123}'
```

After a real write, reread `event events get` and `event annotations list`.
