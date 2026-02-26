---
name: gen-doc
description: "Generate taosdata docs (RS/FS/DS/TS/TM) with consistent engineering conventions and routing."
---

# gen-doc (Router)

This skill is the single entrypoint for generating taosdata documentation:
- RS: Requirement Spec
- FS: Functional Spec
- DS: Design Spec
- TS: Test Spec
- TM: Threat Modeling report

## Input

Ask the user for:
- doc type: RS/FS/DS/TS/TM
  - If the user did not specify, infer from keywords (Requirement/需求/RS, Functional/概要设计/FS, Design/详细设计/DS, Test/测试/TS, Threat Model/威胁建模/TM).
  - If still ambiguous, ask a single clarification question.
- requirement slug (short, kebab-case preferred; used in filename)
- document content inputs (links or pasted text) relevant to the chosen type

## Common Engineering Conventions (MUST)

### Category detection

Determine `category` from the git repository root directory (preferred). If not in a git repo, use current working directory name.

Mapping rules (match by path segment or directory name):
- if path contains `community/TDinternal` => `taosd`
- if repo root dir name is `taosx` or path contains `/taosx/` => `taosx`
- if repo root dir name is `taosadapter` or path contains `/taosadapter/` => `taosadapter`
- if repo root dir name is `taosgen` or path contains `/taosgen/` => `taosgen`
- otherwise => use repo root dir name as category

### Filename

Use strict date format `YYYY-MM-DD` (not shell snippets).

Filename pattern:
- RS: `YYYY-MM-DD-{slug}-RS.md`
- FS: `YYYY-MM-DD-{slug}-FS.md`
- DS: `YYYY-MM-DD-{slug}-DS.md`
- TS: `YYYY-MM-DD-{slug}-TS.md`
- TM: `YYYY-MM-DD-{slug}-TM.md`

### Output location

If environment variable `TAOSDATA_GLOBAL_DOCS_DIR` exists, use:
- `${TAOSDATA_GLOBAL_DOCS_DIR}/{category}/`

Otherwise, use repository/project specific `docs/` directory.

### Output format

After generating the document, the agent MUST print the absolute file path in this exact format:

- `OutputPath: /absolute/path/to/file`

## Routing

Once doc type is selected:
- RS => use `gen-doc/references/RS.md` (via `gen-doc-rs`)
- FS => use `gen-doc/references/FS.md` (via `gen-doc-fs`)
- DS => use `gen-doc/references/DS.md` (via `gen-doc-ds`)
- TS => use `gen-doc/references/TS.md` (via `gen-doc-ts`)
- TM => use `gen-doc/references/TM.md` (via `gen-doc-tm`)

Then generate the requested document strictly following the selected template, while also obeying all Common Engineering Conventions above.
