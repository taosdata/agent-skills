---
name: idmp-uom
description: "IDMP unit-of-measure skill. Use it to inspect UOM classes, class-scoped units, free UOM lookup, search, and conversion, while keeping `get` and `get-get` clearly separated."
metadata:
  author: "TaosData"
  version: "0.3.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli uom --help"
---

# uom

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

## What this skill covers

- Read UOM classes and the units that belong to them.
- Search for units before modeling or import mapping.
- Distinguish the free/global UOM read from the class-scoped UOM read.
- Use single-row and multi-row conversion batches to confirm compatible units before writing model definitions.

## Recommended shortcuts

| Shortcut | Purpose |
|----------|---------|
| `+classes` | List UOM classes |
| `+class` | Read one UOM class |
| `+search` | Search UOMs |
| `+get` | Read one UOM in the common class-scoped flow |

## Recommended reference

- [`UOM read flows`](references/uom-read-flows.md)

## Missing context to resolve first

| Context | Why it must be resolved before conversion or modeling work |
| --- | --- |
| Lookup mode | Decide whether the target is a class lookup, a free/global UOM read, or a class-scoped UOM read. |
| Target unit family | Search terms can be fuzzy, so you need the intended unit name, abbreviation, or class before you trust an ID. |
| Conversion direction | Decide the exact `fromUomId`, `toUomId`, and whether the batch is expected to stay in one compatible class. |
| Verification target | Decide whether proof should come from class inventory, exact `get`, class-scoped `get-get`, or a successful conversion result. |

## Constrained live behaviors

- `uom search` is unit-oriented rather than class-oriented. Do not rely on class labels or family words alone—whether they are English or localized labels—to prove that a unit family is missing. Search appears to work best with exact unit names and abbreviations.
- Use `uomclasses list` and `uomclasses get` to discover class IDs before you rely on `uom get-get`.
- `uom get` is the free/global read. `uom get-get` needs both `uomClassId` and `uomId`.
- `convert` is batch-wide and all-or-nothing: one invalid or incompatible row can fail the full request.
- Treat exact unit name or abbreviation matches as stronger evidence than fuzzy search hits when modeling depends on the result.

## Execution flow

1. Start with `uomclasses` so the operator understands the class context before choosing a unit.
2. Use `uom get` for the free/global UOM read when only a standalone `uomId` is known.
3. Use `uom get-get` for the class-scoped read when both `uomClassId` and `uomId` are known.
4. When `search` returns near-matches, prefer an exact unit name or abbreviation match before you choose IDs for `get`, `get-get`, or `convert`.
5. Use `search` and `convert` before attribute modeling, import mapping, or cross-unit comparisons.
6. Treat `convert` as all-or-nothing for one batch: one invalid UOM ID or incompatible pair can fail the full request with a structured `400`.
7. Re-check the class and IDs whenever a lookup or conversion result looks inconsistent.

## Evidence of completion

- A lookup is only complete when `uom get` or `uom get-get` returns the exact target row you intended to inspect.
- A class-discovery task is only complete when `uomclasses list` or `uomclasses get` exposes the matching family, even if fuzzy `search` is empty.
- A conversion task is only complete when the structured result reflects the requested `fromUomId`, `toUomId`, and numeric output.

## Key commands

```bash
idmp-cli schema uom.uomclasses.list
idmp-cli uom uomclasses list

idmp-cli schema uom.uomclasses.get
idmp-cli uom uomclasses get --params '{"uomClassId":264033646}'

idmp-cli schema uom.uom.search
idmp-cli uom uom search --params '{"keyword":"kWh","limitSize":20}'

idmp-cli schema uom.uom.get
idmp-cli uom uom get --params '{"uomId":1753955006}'

idmp-cli schema uom.uom.get-get
idmp-cli uom uom get-get --params '{"uomClassId":264033646,"uomId":1753955006}'

idmp-cli schema uom.uom.convert
idmp-cli uom uom convert --ack-risk --data '[{"fromUomId":1,"inputValue":100,"toUomId":2},{"fromUomId":1,"inputValue":5,"toUomId":2}]'
```

## Exception paths

- Search returns multiple similar units: read the class first, then prefer an exact unit name or abbreviation match (for example ampere `A` instead of ampere-hour `Ah`) before conversion.
- Search returns empty for class labels or family words alone: fall back to `uomclasses list` and `uomclasses get`; do not treat empty fuzzy search as proof that the unit family does not exist.
- `uom get` returns not found: confirm whether the operator actually needs the class-scoped `uom get-get` path.
- `uom get-get` returns not found: verify both `uomClassId` and `uomId`; a valid free UOM ID is not enough here.
- Conversion fails or looks wrong: confirm the two units belong to a compatible class before trusting the result.
- A mixed valid/invalid conversion batch returns a structured error for the full request; do not treat the first valid row as partial success.
- Modeling still rejects the chosen unit: verify the target attribute expects the same UOM class and unit semantics.

## Validation scenarios

1. List UOM classes with `idmp-cli uom uomclasses list`.
2. Read one class with `idmp-cli uom uomclasses get --params '{"uomClassId":264033646}'`.
3. Search for a known unit such as `kWh` with `idmp-cli uom uom search`.
4. Read one free UOM with `idmp-cli uom uom get` and one class-scoped UOM with `idmp-cli uom uom get-get`.
5. Convert a multi-row compatible batch with `idmp-cli uom uom convert --ack-risk --data '[{"fromUomId":1,"inputValue":100,"toUomId":2},{"fromUomId":1,"inputValue":5,"toUomId":2}]'`, then probe a mixed valid/invalid batch and confirm the CLI surfaces the structured `400` instead of partial success.
