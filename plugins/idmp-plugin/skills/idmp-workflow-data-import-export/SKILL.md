---
name: idmp-workflow-data-import-export
description: "IDMP data import and export workflow. Separate package import or export from datasource CSV import, read first, write carefully, and reread records after every write."
metadata:
  author: "TaosData"
  version: "0.6.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli data --help"
---

# workflow: data import export

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

## Recommended references

- [`references/data-import-export.md`](references/data-import-export.md)
- [`../idmp-data/SKILL.md`](../idmp-data/SKILL.md)

## Missing context to resolve first

- Workflow type.
- Artifact expectation.
- Whether the operator needs package export, package import, or datasource CSV import.
- Which root or artifact record is already known.
- Whether the expected artifact is record-backed or streamed directly to stdout.

## Constrained live behaviors

- Accept both valid export branches.
- Always reread records after every write.
- Package import/export and datasource CSV import are different command families.
- `download get` only works after a record-backed artifact exists.
- Some export branches stream ZIP content directly; in that branch the streamed file is the final artifact.

## Execution flow

1. Start with `idmp-cli data first-level-elements list` and `idmp-cli data records list` to prove the visible roots and current artifact history.
2. Use `idmp-cli data import-and-export export --ack-risk --data` only after the root and export mode are clear.
3. Reread `idmp-cli data records list` before trying `idmp-cli data download get --params`.
4. Inspect `idmp-cli schema data.import-and-export.import` before any package import.
5. Treat `idmp-cli schema datasource.csv.create` as the separate datasource CSV chain, and keep `idmp-cli datasource csv create --ack-risk --params` out of package import/export payloads.

## Exception paths

- If no export record exists, stop before `download get` and explain whether the branch streamed a ZIP directly.
- If the operator asked for CSV import but only described package import, stop and rescope instead of mixing workflows.
- After every mutation, reread records so the artifact history is explicit.

## Validation scenarios

### 1. Package export with branch detection
Run `idmp-cli data import-and-export export --ack-risk --data`, then reread `idmp-cli data records list`. The result must say whether the branch is record-backed or stdout-ZIP.

### 2. Package import after schema inspection
Read `idmp-cli schema data.import-and-export.import` first. Only then is a package import payload discussion valid.

### 3. Datasource CSV import
Use `idmp-cli schema datasource.csv.create` to keep CSV import separate from package import/export. Do not reuse package DTO guidance here.

### 4. ZIP-stdout branch versus record-backed branch
Try `idmp-cli data download get --params` only after rereading records. If no record exists, record that stdout branch explicitly.

### 5. Wrong chain detected before write
If the request mixes export and CSV import, stop early. Reread `data records list` after every export, import, or CSV write.
