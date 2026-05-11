---
name: idmp-element
description: "IDMP element skill for locating elementId, resolving business-root paths, browsing children, and preparing downstream analysis or panel work."
metadata:
  author: "TaosData"
  version: "0.4.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli element --help"
---

# element

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

**Before any write:** Follow the [🛑 Destructive op confirmation protocol](../idmp-shared/SKILL.md#-destructive-op-confirmation-mandatory). Read-only commands stay read-only here, but delete / write / patch flows still require the shared yes-gate.


## Recommended shortcuts

| Shortcut | Purpose |
|----------|---------|
| [`+list`](references/idmp-element-list.md) | Browse elements under the current `parentId`. |
| [`+get`](references/idmp-element-get.md) | Confirm one element after search or path lookup. |
| [`+tree`](references/idmp-element-tree.md) | Inspect child nodes and tree structure. |
| [`+search`](references/idmp-element-search.md) | Find elements by keyword, root, or parent filters. |

## What this skill solves

- Find a reliable `elementId` before downstream create or update work.
- Resolve the full path so `rootElementId` comes from the business root, not from the current leaf element. Proof: pair `element elements path` with `element fullpath get` and confirm the root is a first-level owner or an explicitly confirmed ancestor.
- Reverse-check a resolved path with `by-path` before handing it to another workflow.
- Read child templates before hierarchy-based analysis or panel work.
- Discover the current shared first-level root from live reads instead of assuming a historical `demo` tree is still present.
- Distinguish plain container create from template-backed create before downstream analysis, panel, or alert workflows.

## Element create paths

- `element.elements.create` is for plain container elements. Use it when you need a parent node without template-backed metrics.
- `element.new.create` is for template-backed elements. Use it when the payload needs `templateId` and `keywordValues`.
- If the template is keyword-backed, confirm the upstream source table already exists before treating the new element as data-bearing.

## Evidence of completion

- A container create is only complete after `element elements get` or `element elements list` rereads the new node under the intended parent.
- A path-resolution task is only complete after `element elements path`, `element fullpath get`, and `element by-path list` agree on the same root-to-leaf record.
- A template-backed create is only complete after reread proves the final template binding and keyword values survived the write.

## Key commands

```bash
idmp-cli schema element.elements.search
idmp-cli element elements search --params '{"keyword":"Chaoyang","current":1,"limitSize":20}'

idmp-cli schema element.elements.path
idmp-cli element elements path --params '{"elementId":123}'

idmp-cli schema element.fullpath.get
idmp-cli element fullpath get --params '{"rootElementId":100,"elementId":123}'

idmp-cli schema element.by-path.list
idmp-cli element by-path list --params '{"elementPath":"Utilities/Beijing/Chaoyang/Device-A"}'

idmp-cli schema element.elements.sub-templates
idmp-cli element elements sub-templates --params '{"elementId":123}'

idmp-cli schema element.elements.create
idmp-cli element elements create --dry-run --ack-risk --data '{"name":"sandbox-parent","parentElementId":123,"referenceType":"ParentChild"}'

idmp-cli schema element.new.create
idmp-cli template +keywords 456
idmp-cli element new create --dry-run --ack-risk --data '{"parentElementId":123,"referenceType":"ParentChild","templateId":456,"keywordValues":{"<TEMPLATE_KEY>":"<existing-source-keyword-value>"},"force":true}'
```

## Recommended sequence

```bash
idmp-cli element elements search --params '{"keyword":"Chaoyang","current":1,"limitSize":20}'
idmp-cli element elements path --params '{"elementId":123}'
idmp-cli element fullpath get --params '{"rootElementId":100,"elementId":123}'
idmp-cli element by-path list --params '{"elementPath":"Utilities/Beijing/Chaoyang/Device-A"}'
idmp-cli element elements get --params '{"elementId":123}'
idmp-cli element elements sub-templates --params '{"elementId":123}'
```

## Exception and failure handling

- If search returns no rows, widen the keyword or add parent/root filters; do not guess IDs.
- If several elements share similar names, always confirm with `path` and `get` before handing the ID to another workflow.
- If `fullpath` and `by-path` do not round-trip to the same record, stop and resolve the correct business path before any write.
- If the path is incomplete or the business root is unclear, stop before any write that needs `rootElementId`. Treat the path as unclear when no first-level owner is visible or the `path -> fullpath -> by-path` roundtrip lands on different nodes.
- If a historical `demo` root is absent, start from `element elements list`, then resolve the currently visible first-level root and reuse that real tree for temporary owners.
- If `sub-templates` is empty, hierarchy-based analysis or panel options may not be available; switch to self scope or choose another element.
- If the write needs `templateId` or `keywordValues`, do not use `element.elements.create`; switch to `element.new.create`.
- If auth or permission checks fail while browsing, repair the session before attempting risky commands.

## Validation scenarios

1. Search by keyword with `idmp-cli schema element.elements.search` and `idmp-cli element elements search --params '{"keyword":"Chaoyang","current":1,"limitSize":20}'`.
2. Resolve the business-root path with `idmp-cli schema element.elements.path`, then read the root-to-leaf name path with `idmp-cli element fullpath get --params '{"rootElementId":100,"elementId":123}'`.
3. Reverse-check the path with `idmp-cli element by-path list --params '{"elementPath":"Utilities/Beijing/Chaoyang/Device-A"}'`, then confirm the selected record with `idmp-cli element elements get --params '{"elementId":123}'`.
4. Check hierarchy readiness with `idmp-cli schema element.elements.sub-templates` and `idmp-cli element elements sub-templates --params '{"elementId":123}'`.
5. Verify downstream ownership by reading `idmp-cli analysis analyses list --params '{"elementId":123,"current":1,"size":20}'`, then distinguish create paths with `idmp-cli element elements create --dry-run --ack-risk --data '{"name":"sandbox-parent","parentElementId":123,"referenceType":"ParentChild"}'` for a plain container and `idmp-cli element new create --dry-run --ack-risk --data '{"parentElementId":123,"referenceType":"ParentChild","templateId":456,"keywordValues":{"<TEMPLATE_KEY>":"<existing-source-keyword-value>"},"force":true}'` for a template-backed element.
