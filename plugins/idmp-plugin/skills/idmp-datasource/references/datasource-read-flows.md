# datasource read flow

Use this reference for inspection. If the goal becomes diagnosis, hand off to `../idmp-workflow-datasource-diagnose/SKILL.md`.

## Read-first sequence

1. Read the connection list and detail:

   ```bash
   idmp-cli datasource connections list
   idmp-cli datasource connections get --params '{"id":123}'
   idmp-cli datasource additional-properties list-get --params '{"connectionId":123}'
   ```

2. Read health or connectivity evidence:

   ```bash
   idmp-cli datasource check list
   ```

3. Drill into database and table structure:

   ```bash
   idmp-cli datasource dbnames list --params '{"connectionId":123,"includeIDMPDefaultDB":true}'
   idmp-cli datasource tablenames list --params '{"connectionId":123,"dbName":"power"}'
   idmp-cli datasource subtablenames list --params '{"connectionId":123,"dbName":"power","stableName":"meters","pageSize":20}'
   idmp-cli datasource columninfo create --ack-risk --params '{"connectionId":123}' --data '{"dbName":"power","stableNames":["meters"]}'
   idmp-cli datasource meta list --params '{"connectionId":123,"dbName":"power"}'
   ```

## Interpretation rules

- an empty UI list elsewhere does not prove the datasource API is healthy
- secrets returned by `connections get` may be masked and must not be copied directly into write payloads
- `dbName`, `stableName`, and `stableNames` must come from the discovery reads above
- `subtablenames list` needs explicit `pageSize`

## Write handoff

If the operator explicitly wants a connectivity repro or CSV import, switch to the workflow skill:

```bash
idmp-cli schema datasource.connectivity.create
idmp-cli schema datasource.csv.create
```
