# data import and export flow

Use this reference after the main workflow doc. There are three different write families here, and they should never be mixed.

## Three write families

| Workflow | Transport | Payload family | Verification |
| --- | --- | --- | --- |
| package export | JSON body | export DTO | stdout ZIP branch or `data records list` branch |
| package import | multipart form-data | import DTO | `data records list` plus post-import asset reads |
| datasource CSV import | multipart form-data | CSV DTO | `data records list` plus datasource rereads |

## Package export starter

This is schema-backed and readonly-risk in this CLI, even though it uses `POST`.

```json
{
  "categoryIds": [],
  "elementIds": [123],
  "elementTemplateIds": [456],
  "eventTemplateIds": [],
  "uomIds": []
}
```

Run:

```bash
idmp-cli data import-and-export export --data '{...}'
```

## Export branch handling

After export, accept either of these as success:

1. **stdout ZIP branch**: the command streamed the artifact immediately
2. **record-backed branch**: `data records list` later exposes the downloadable artifact name

Only call:

```bash
idmp-cli data download get --params '{"name":"real-export-name.zip"}'
```

after the real name is known.

## Package import starter

`data.import-and-export.import` is multipart form-data, not a JSON DTO:

```text
required transport: multipart/form-data
fields:
- connectionId
- contactId
- jsonFile
- taosgenFiles[]
```

Inspect first:

```bash
idmp-cli schema data.import-and-export.import
```

Then run:

```bash
idmp-cli data import-and-export import --ack-risk --params '{}' --data '{...}'
```

## Datasource CSV import starter

`datasource.csv.create` is also multipart form-data:

```text
required transport: multipart/form-data
required fields:
- csvFile
- tableName

optional fields:
- hasHeader
- quote
- escapeChar
```

Inspect first:

```bash
idmp-cli schema datasource.csv.create
```

Then run:

```bash
idmp-cli datasource csv create --ack-risk --params '{}' --data '{...}'
```

## Read-first sequence

### Package chain

```bash
idmp-cli data first-level-elements list
idmp-cli data records list
```

### CSV chain

```bash
idmp-cli datasource connections list
idmp-cli datasource dbnames list --params '{"connectionId":123,"includeIDMPDefaultDB":true}'
idmp-cli datasource tablenames list --params '{"connectionId":123,"dbName":"power"}'
```

## One-shot recovery rules

1. Never guess the artifact name for `download get`.
2. Never improvise the multipart body for package import or CSV import; inspect schema first.
3. Package export, package import, and CSV import have different verification targets.
4. Reread `data records list` after every write, even when the command itself printed success.
5. If the write returned success but no records changed, reread once after a short delay before trying another write.
