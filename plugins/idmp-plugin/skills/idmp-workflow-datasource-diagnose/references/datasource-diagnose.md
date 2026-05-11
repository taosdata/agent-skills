# datasource diagnose flow

Use this reference after the main workflow doc. It separates datasource failures into connection, credential, database, table, metadata, and model-mapping layers.

## Failure-boundary matrix

| Symptom | Most likely boundary | First proving read |
| --- | --- | --- |
| `connections list` is empty | visibility or permission | `connections get` on a known ID, if available |
| `connectivity create` fails after copying `connections get` | redacted secret problem | reread `connections get` and compare masked fields |
| `dbnames` fails | transport, auth, or DB visibility | `datasource check list` or a trusted connectivity payload |
| `tablenames` or `subtablenames` fails | wrong database, wrong table family, or scope issue | reread `dbnames`, then rerun table discovery |
| `columninfo` or `meta` fails | wrong stable names or metadata shape | confirm `stableName` and `stableNames` from table reads |
| metadata exists but IDMP modeling still fails | model mapping mismatch | compare template attributes and UOMs against datasource metadata |

## Safe read-first sequence

1. confirm the connection object
2. decide whether you have reusable credentials or must stay on listener checks
3. confirm database visibility
4. confirm table and stable visibility
5. confirm metadata
6. compare metadata against IDMP templates and UOMs
7. reread records if CSV import or package import was part of the diagnosis

## Connection object and redaction check

```bash
idmp-cli datasource connections list
idmp-cli datasource connections get --params '{"id":123}'
idmp-cli datasource additional-properties list-get --params '{"connectionId":123}'
idmp-cli datasource check list
```

Interpretation rules:

- if the password or token fields look masked, do not reuse the returned payload for `connectivity create`
- if the built-in listener health check is enough, prefer `datasource check list`
- only use `connectivity create` when a trusted unmasked payload is available from the operator or a secure source

## Connectivity payload starter

This starter is schema-derived and should be filled only from a trusted secret source, never from a masked `connections get` reread.

```json
{
  "name": "connection1",
  "dsType": "MySQL",
  "authType": "UserPassword",
  "url": "jdbc:mysql://host:3306/db1",
  "host": "host",
  "dbName": "db1",
  "enableSsl": false,
  "additionalProps": {},
  "password": "<trusted-secret-only>"
}
```

Run:

```bash
idmp-cli datasource connectivity create --ack-risk --data '{...}'
```

## Metadata probe starters

### Stable metadata probe

```bash
idmp-cli datasource dbnames list --params '{"connectionId":123,"includeIDMPDefaultDB":true}'
idmp-cli datasource tablenames list --params '{"connectionId":123,"dbName":"power"}'
idmp-cli datasource subtablenames list --params '{"connectionId":123,"dbName":"power","stableName":"meters","pageSize":20}'
idmp-cli datasource columninfo create --ack-risk --params '{"connectionId":123}' --data '{"dbName":"power","stableNames":["meters"]}'
idmp-cli datasource meta list --params '{"connectionId":123,"dbName":"power"}'
```

### External-table or non-subtable discovery

```bash
idmp-cli datasource dbnames list --params '{"connectionId":123,"includeIDMPDefaultDB":true}'
idmp-cli datasource tablenames list --params '{"connectionId":123,"dbName":"power"}'
idmp-cli datasource meta list --params '{"connectionId":123,"dbName":"power"}'
```

## Model-mapping closure

Once metadata is readable, compare it to IDMP model expectations:

```bash
idmp-cli template elements get --params '{"elementTemplateId":456}'
idmp-cli attr-template elements attributes --params '{"elementTemplateId":456}'
idmp-cli uom uomclasses list
idmp-cli uom uom search --params '{"keyword":"A","limitSize":20}'
```

Treat these mismatches as modeling errors rather than datasource outages:

- column exists but no attribute-template matches it
- metric column exists but the template expects a tag-like field
- units are incompatible or missing

## Import-trace check

If CSV import or package import was part of the incident:

```bash
idmp-cli data records list
```

Use this only as a trace and audit signal. It does not replace direct datasource metadata checks.

## One-shot recovery rules

1. Empty connection list does not prove the environment has no datasource; confirm one known ID if you have it.
2. A failed copied connectivity payload most often means the stored secret was masked.
3. Always derive `dbName`, `stableName`, and `stableNames` from earlier reads.
4. Always pass `pageSize` to `subtablenames list`.
5. If metadata reads succeed, stop blaming the transport layer and compare model mappings next.
6. If a CSV write was attempted, reread `data records list` before declaring success or failure.
