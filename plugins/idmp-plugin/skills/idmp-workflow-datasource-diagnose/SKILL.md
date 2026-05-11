---
name: idmp-workflow-datasource-diagnose
description: "IDMP datasource diagnosis workflow. Read the connection, probe connectivity, inspect databases and metadata, compare model mappings, and reread after every probe or write."
metadata:
  author: "TaosData"
  version: "0.6.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli datasource --help"
---

# workflow: datasource diagnose

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

## Recommended references

- [`references/datasource-diagnose.md`](references/datasource-diagnose.md)
- [`../idmp-datasource/SKILL.md`](../idmp-datasource/SKILL.md)

## Missing context to resolve first

- Credential source.
- Verification rereads.
- The target connection, database, or table that the operator thinks is broken.
- Whether the complaint is reachability, metadata visibility, or model mismatch.
- Which element or template mapping should be compared back to source metadata.

## Constrained live behaviors

- Do not copy `connections get` into `connectivity create`.
- `datasource check list` for the built-in TDengine listener.
- After any write-like probe or import, reread.
- Read the connection object before probing reachability.
- Additional properties and metadata are evidence; they do not replace a live connectivity probe.
- Metadata diagnosis stays ordered: connection -> probe -> db -> table -> column -> model mapping.

## Execution flow

1. Read `idmp-cli datasource connections list` and `idmp-cli datasource connections get --params` before any probe.
2. Use `idmp-cli datasource additional-properties list-get --params` to capture datasource-side context.
3. Reread `idmp-cli datasource check list` and then run `idmp-cli datasource connectivity create --ack-risk --data` to separate summary health from live reachability.
4. Use `idmp-cli datasource dbnames list --params`, `idmp-cli datasource tablenames list --params`, and `idmp-cli datasource columninfo create --ack-risk --params` to lock the metadata boundary.
5. Compare that metadata with `idmp-cli attr-template elements attributes --params`, and use `idmp-cli datasource csv create --ack-risk --params` only when the diagnosis includes a write-like CSV probe.
6. Reread `idmp-cli data records list` if the diagnosis also touches import or export traces.

## Exception paths

- If the connectivity probe fails, fall back to `datasource check list` plus metadata reads before interpreting missing tables as schema bugs.
- If metadata exists but the model does not match, report the exact column or mapping mismatch.
- If record traces are absent, say whether the gap is ingestion history or datasource visibility. Capture whether the root cause is connectivity.

## Validation scenarios

### 1. Listener health confirmation
Start with `idmp-cli datasource connections list` and `idmp-cli datasource connections get --params`. Only then run `idmp-cli datasource check list`.

### 2. Redacted-payload connectivity failure isolation
Use `idmp-cli datasource connectivity create --ack-risk --data` after a redaction-aware connection read. Reachability failures should not trigger secret hunting.

### 3. Metadata versus model mismatch
Pair `idmp-cli datasource columninfo create --ack-risk --params` with `idmp-cli attr-template elements attributes --params`. The result should name the exact mapping mismatch.

### 4. Table discovery failure
Walk `idmp-cli datasource dbnames list --params` and `idmp-cli datasource tablenames list --params` in order. The failing step should become the reported boundary.

### 5. CSV import trace during diagnosis
If the datasource complaint touches ingestion, reread `idmp-cli data records list`. Keep record-trace evidence separate from connectivity evidence.
