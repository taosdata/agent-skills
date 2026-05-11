---
name: idmp-data
description: "IDMP data import/export skill. Use it to inspect exportable root elements, review import/export records, download artifacts, and distinguish package export, artifact download, and import flows."
metadata:
  author: "TaosData"
  version: "0.5.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli data --help"
---

# data

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

## What this skill covers

- Discover which top-level elements are available for package import/export.
- Review import/export records before downloading artifacts or investigating failures.
- Distinguish package export, artifact download, package import, and single import/export operations.
- Use records as the operator’s source of truth for status, filenames, and error messages.
- Accept both valid export outcomes: a record-backed artifact or a ZIP archive streamed directly to stdout.

## Recommended shortcuts

| Shortcut | Purpose |
|----------|---------|
| `+roots` | List first-level elements visible to import/export |
| `+records` | List import/export records |
| `+download` | Download the artifact for a known record |

## Recommended reference

- [`Data import/export read flows`](references/data-read-flows.md)

## Missing context to resolve first

| Context | Why it must be resolved before import or export |
| --- | --- |
| Workflow type | Package export, package import, and datasource CSV import are different mutation chains. |
| Scope | You need the final `elementIds`, `elementTemplateIds`, or datasource scope before the write. |
| Expected artifact | Exports can either stream a ZIP directly to stdout or create a record that later exposes `fileName`. |
| Datasource context | CSV import needs a validated `connectionId`, `dbName`, and table or stable names from earlier reads. |
| Verification window | Decide when and how you will reread `data records list` after the write. |

## Constrained live behaviors

- Package export, package import, and datasource CSV import must not share guessed payloads or filenames.
- `data records list` is the authoritative confirmation after every write; a quick success response is not the final state.
- `data download get` must use the real record artifact name as the `name` path parameter, not a guessed path.
- A successful export can end in two valid ways: ZIP bytes on stdout or a later record-backed artifact with `fileName`.
- High-impact import or export work should start with schema inspection or `--dry-run` before the real write.
- If a probe import creates assets you do not want to keep, cleanup belongs to the owning asset workflow, not to record deletion.

## Operator workflow

1. Start with `first-level-elements` before any export or import decision.
2. Read `records` before downloading an artifact, reviewing a failure, or confirming the generated filename.
3. Use `import-and-export export` for package creation, `download get` only when a record exposes `fileName`, and `import-and-export import` or `single-import create` for uploads.
4. Expect exports and imports to be long-running or asynchronous; the CLI response alone is not the final confirmation.
5. If export already streamed ZIP bytes to stdout, treat that stream as the artifact and still re-check `records` for audit history.
6. Re-check `records` after every write to confirm status, artifact name, and failure details.

## Key commands

```bash
idmp-cli schema data.first-level-elements.list
idmp-cli data first-level-elements list

idmp-cli schema data.records.list
idmp-cli data records list

idmp-cli schema data.import-and-export.export
idmp-cli data import-and-export export --ack-risk --data '{"elementIds":[123]}'

idmp-cli schema data.download.get
idmp-cli data download get --params '{"name":"export.zip"}'

idmp-cli schema data.import-and-export.import
# `data.import-and-export.import` is multipart/form-data in the current schema.
# Inspect the schema output first and build the request with the exact transport and fields
# (for example `jsonFile` / `taosgenFiles[]`) instead of assuming a plain JSON body.
idmp-cli data import-and-export import --ack-risk --data '{...}'

idmp-cli schema data.single-import.create
# `data.single-import.create` is also multipart/form-data in the current schema.
# Inspect the schema output first and use the exact upload fields instead of guessing a JSON DTO.
idmp-cli data single-import create --ack-risk --data '{...}'
```

## Exception paths

- `first-level-elements` is empty: confirm the current account can see any import/export roots before troubleshooting files.
- The export call returns quickly but no usable record appears: check whether stdout already contains a ZIP artifact before retrying.
- A download fails with file-not-found behavior: re-read `records`, use the exact artifact name as `name`, or skip download when the export already streamed ZIP bytes.
- An import fails validation: inspect the schema first, then read `records` for the real failure reason instead of guessing from the upload step.
- Package and single import/export results differ: confirm the operator chose the correct flow before retrying.

## Validation scenarios

### 1. Export root discovery

List first-level elements before choosing an export scope:

```bash
idmp-cli data first-level-elements list
```

### 2. Record baseline

Read import/export records before writing anything:

```bash
idmp-cli data records list
```

### 3. Package export

Export one known element package:

```bash
idmp-cli data import-and-export export --ack-risk --data '{"elementIds":[123]}'
```

### 4. Artifact branch detection

Re-read records and distinguish a record-backed artifact from a ZIP that was already streamed to stdout:

```bash
idmp-cli data records list
```

### 5. Download only when the record exposes fileName

Download the reported artifact when the export created a downloadable record:

```bash
idmp-cli data download get --params '{"name":"export.zip"}'
```
