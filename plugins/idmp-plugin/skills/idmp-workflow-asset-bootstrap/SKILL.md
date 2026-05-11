---
name: idmp-workflow-asset-bootstrap
description: "IDMP asset bootstrap workflow. Read roots, paths, templates, attribute templates, UOMs, datasources, and record visibility before any modeling or ingestion write."
metadata:
  author: "TaosData"
  version: "0.5.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli element --help"
---

# workflow: asset bootstrap

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

## Recommended references

- [`references/asset-bootstrap.md`](references/asset-bootstrap.md)
- [`../idmp-element/SKILL.md`](../idmp-element/SKILL.md)

## Missing context to resolve first

- The visible business root or path the operator wants to model against.
- Whether the goal is leaf-only context, middle-owner context, or source-ingestion context.
- Whether a reusable template family is already known.

## Constrained live behaviors

- Root discovery must be real-environment evidence, not a guessed `demo` tree.
- Template and sub-template checks come before any modeling assumption.
- UOM and datasource checks prove measurement semantics and ingestion visibility, not object mutability.
- If a downstream workflow temporarily creates a middle-owner hierarchy and the async delete task later lands in `FAILED`, treat that as a backend cleanup boundary after the reread proof instead of a reason to keep retrying destructive cleanup loops.

## Execution flow

1. Use `idmp-cli element elements list --params`, `idmp-cli element elements path --params`, `idmp-cli element fullpath get --params`, and `idmp-cli element by-path list --params` to lock the visible root and chosen owner.
2. Use `idmp-cli template elements list --params` and `idmp-cli element elements sub-templates --params` to confirm the template family behind that scope.
3. Use `idmp-cli attr-template elements attributes --params` to inspect measurement-ready attribute templates before proposing analysis or panel work.
4. Use `idmp-cli uom uomclasses list` and `idmp-cli uom uom search --params` to verify measurement semantics.
5. Use `idmp-cli datasource connections list`, `idmp-cli data first-level-elements list`, and `idmp-cli data records list` to confirm ingestion visibility.

## Exception paths

- If visible roots are empty, classify the issue as auth, permission, or environment scope before continuing.
- If the chosen root exposes the wrong template family, stop and pick a different owner instead of forcing later workflows.
- If ingestion traces are invisible, do not promise downstream import or alert success.
- If previous temporary hierarchy cleanup tasks failed but the owner is still readable, classify the environment as reusable with a cleanup caveat instead of pretending the root inventory changed.

## Validation scenarios

### 1. Unknown environment bootstrap
Start with `idmp-cli element elements list --params` and `idmp-cli element elements path --params`. The goal is to prove the current visible root before anything else.

### 2. Model-ready but ingestion-unknown environment
Use `idmp-cli attr-template elements attributes --params` to prove template readiness, then `idmp-cli datasource connections list` to confirm ingestion visibility separately.

### 3. Root list is empty
Stop after `idmp-cli element elements list --params` returns nothing useful. The next step is auth or permission diagnosis, not a guessed bootstrap answer.

### 4. Template mismatch on the chosen root
Use `idmp-cli template elements list --params` and `idmp-cli element elements sub-templates --params` to show the mismatch. Switch owners instead of inventing template compatibility.

### 5. Post-write reread
If a previous operator already created temporary objects, reread with `idmp-cli data first-level-elements list` and `idmp-cli data records list` before claiming the environment is reusable. If the objects are still readable only because an async delete task previously failed, record that as a backend cleanup caveat instead of retrying destructive cleanup here.
