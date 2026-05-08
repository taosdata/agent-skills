---
name: idmp-datasource
description: "IDMP datasource skill. Use it to list and inspect connections, verify connectivity before deeper metadata reads, and diagnose database or table visibility issues instead of stopping at the connection list."
metadata:
  author: "TaosData"
  version: "0.4.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli datasource --help"
---

# datasource

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

## What this skill covers

- Inspect datasource connections, redacted connection details, connectivity probes, database and table discovery, and column metadata.
- Keep read-first metadata diagnosis separate from mutating import workflows.

## Recommended reference

- [`references/datasource-read-flows.md`](references/datasource-read-flows.md)

## Missing context to resolve first

- Credential source.
- Verification rereads.
- Which datasource connection or environment is in scope.
- Which database, table, or stable must be traced.
- Whether the operator wants metadata only or a full model-to-source mapping explanation.

## Constrained live behaviors

- `datasource connections get` can return redacted secrets.
- `datasource check list` is the safe health probe.
- `datasource columninfo create` is a write-like metadata probe.
- Connection reads can be redacted and still be usable for diagnosis.
- Connectivity probes validate reachability, not schema correctness.
- Metadata walks should stay ordered: connection -> connectivity -> databases -> tables -> columns.
- Source-to-model explanations must use the real mapped fields, not guessed TDengine column names.

## Execution flow

1. Start with `idmp-cli datasource connections list`, then lock the exact connection through `connections get`.
2. Run `idmp-cli datasource check list` before deeper diagnosis so connection-health boundaries are explicit.
3. Use `idmp-cli datasource connectivity create --ack-risk --data` only after the target connection is fixed; treat it as live reachability proof, not schema proof.
4. Walk `dbnames -> tablenames -> columninfo` in order so every metadata claim stays grounded in the same database and table scope.
5. Finish by comparing the discovered source fields against the real model mapping rather than guessed TDengine column names.

## Evidence of completion

- A connection diagnosis is only complete when the connection reread and the health probe refer to the same connection ID.
- A metadata claim is only complete when the same database and table survive the `dbnames -> tablenames -> columninfo` chain.
- Redacted connection reads are still valid evidence; never treat masked secrets as missing data.

## Key commands

1. `idmp-cli datasource connections list` to find the target connection.
2. `idmp-cli datasource connections get --params` to inspect the selected connection object.
3. `idmp-cli datasource check list` to read built-in datasource health summaries.
4. `idmp-cli datasource connectivity create --ack-risk --data` to probe live reachability.
5. `idmp-cli datasource dbnames list --params` to enumerate databases.
6. `idmp-cli datasource tablenames list --params` to enumerate tables or stables.
7. `idmp-cli datasource columninfo create --ack-risk --params` to lock the final metadata shape.

## Exception paths

- If connectivity fails, stop before interpreting missing tables as modeling problems.
- If column metadata is missing, show the exact database and table boundary that failed.
- Never unredact or log credentials from a connection read.

## Validation scenarios

### 1. Connection discovery
Start with `idmp-cli datasource connections list`, then pick one connection for deeper reads. The next step should always be a targeted `get`.

### 2. Redaction-aware connection read
Use `idmp-cli datasource connections get --params` and accept masked secrets. Diagnosis can continue without exposing credentials.

### 3. Built-in health check
Run `idmp-cli datasource check list` and `idmp-cli datasource connectivity create --ack-risk --data` together. Separate summary checks from a live reachability probe.

### 4. Database and table discovery
Walk `idmp-cli datasource dbnames list --params` and `idmp-cli datasource tablenames list --params` in order. Do not jump straight to columns without a verified table target.

### 5. Metadata closure
Finish with `idmp-cli datasource columninfo create --ack-risk --params`. Treat successful `dbnames -> tablenames -> columninfo` as a real metadata closure.
