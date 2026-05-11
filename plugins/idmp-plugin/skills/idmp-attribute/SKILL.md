---
name: idmp-attribute
description: "IDMP attribute skill for reading definitions and values, checking history, evaluating expressions, reserving names, and safely writing test data."
metadata:
  author: "TaosData"
  version: "0.4.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli attribute --help"
---

# attribute

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

**Before any write:** Follow the [🛑 Destructive op confirmation protocol](../idmp-shared/SKILL.md#-destructive-op-confirmation-mandatory). Read-only commands stay read-only here, but delete / write / patch flows still require the shared yes-gate.


## Recommended shortcuts

| Shortcut | Purpose |
|----------|---------|
| [`+list`](references/idmp-attribute-list.md) | Read attribute definitions before value or history work. |
| [`+get`](references/idmp-attribute-get.md) | Read one attribute's current value. |
| [`+data`](references/idmp-attribute-data.md) | Read multiple current values in one request. |
| [`+history`](references/idmp-attribute-history.md) | Read historical data for one attribute. |

## Recommended references

- [`references/idmp-attribute-evaluate-expression.md`](references/idmp-attribute-evaluate-expression.md)

## Product-style workflow

1. Read definitions with `attributes`.
2. Read current values with `data-get` or `data-post` only when needed.
3. Run `new-name` without `--ack-risk` before creating an attribute.
4. Run `attribute evaluate-expression create` before saving a formula or expression.
5. Use `write-data` only when you need controlled test input on a metric-backed attribute.

## Missing context to resolve first

| Context | Why it must be resolved before create or write |
| --- | --- |
| Owner element | You need the final `elementId` before you can reserve names, create the attribute, or reread definitions and values. |
| Candidate attribute name | `attribute attributes new-name` only works after the owner is fixed. |
| Attribute type plan | You need the intended `valueType` and whether the attribute is only metadata, expression-backed, or a metric-backed writable reference. |
| Write target | Decide whether `write-data` should target an existing TDengine metric reference rather than the newly created attribute. |
| Verification and cleanup target | Decide how you will prove create success, how you will reread written data, and which temporary attribute must be deleted at the end. |

## Constrained live behaviors

- `attribute attributes new-name` only needs the owner scope, but `attributes-post` must use the final reserved name and a real `valueType`.
- The expression-preview command family is `attribute evaluate-expression create`, and the schema path is `attribute.evaluate-expression.create`; the older guessed `attribute.attributes.evaluate-expression` path is wrong.
- Older checks may still mention the guessed `attribute.attributes.evaluate-expression` path; use `idmp-cli attribute evaluate-expression create --dry-run --ack-risk --params` for the real request.
- `attribute evaluate-expression create` needs a request body with at least `dataReferenceType` and `expression`. The live-safe starter is `{"dataReferenceType":"Formula","expression":"..."}`; `attributeId` and `uomId` are optional context helpers, not substitutes for the formula text.
- A newly created generic attribute is not automatically a TDengine metric reference. `attribute write-data create` can fail with `etda390037` unless the target attribute is backed by writable metric storage.
- In strict live validation, `attribute historydata list` should use explicit `start` and `end` bounds instead of relying on ambient defaults.
- Attribute create is not complete until `attributes` reread shows the new definition.
- Template-derived attributes are not generic scratch objects. If an attribute still has `attrTempId`, the generic `attribute elements attributes-delete` path is expected to reject the delete while the backing template exists.
- Temporary probe attributes should be deleted after the workflow, even when write-data validation used a different existing metric-backed attribute.

## Evidence of completion

- A create is only complete when `attribute elements attributes --params` rereads the new definition under the same owner.
- A value probe is only complete when `data-get`, `data-post`, or bounded `historydata list` returns the intended attribute data.
- A write probe is only complete when the target is known to be metric-backed and the reread reflects the inserted row, not just the CLI success line.

## Key commands

```bash
idmp-cli schema attribute.elements.attributes
idmp-cli attribute elements attributes --params '{"elementId":1}'

idmp-cli schema attribute.attributes.new-name
# new-name is read-only (reserves a name); no --ack-risk required
idmp-cli attribute attributes new-name --params '{"elementId":1}'

idmp-cli schema attribute.elements.attributes-post
idmp-cli attribute elements attributes-post --ack-risk --params '{"elementId":1}' --data '{"name":"probe-attribute","valueType":"Double"}'

idmp-cli schema attribute.evaluate-expression.create
idmp-cli attribute evaluate-expression create --params '{"elementId":1}' --data '{...}' --dry-run --ack-risk

idmp-cli schema attribute.attributes.data-get
idmp-cli attribute attributes data-get --params '{"elementId":1,"attributeId":2}'

idmp-cli schema attribute.historydata.list
idmp-cli attribute historydata list --params '{"elementId":1,"attributeId":2,"current":1,"size":20,"start":1704067200000,"end":1704153600000}'
```

## Exception and failure handling

- If an attribute is not returned by `attributes`, do not guess the ID from older notes or scripts.
- If the definition exists but the current value is empty, check history before treating it as a product failure.
- If `new-name` returns a different candidate, use the reserved value instead of forcing the original name.
- If expression evaluation fails, fix the formula before create or update; do not save a broken expression first.
- If test writes are rejected with errors such as `etda390037`, switch to a known metric-backed attribute; do not assume the newly created attribute is writable.
- If delete fails because the attribute came from an attribute template, treat that as a scope boundary; do not keep retrying the generic element-attribute delete path.
- If the preview differs from the intended payload, stay read-only until the schema and permissions are correct.

## Validation scenarios

1. Read attribute definitions with `idmp-cli schema attribute.elements.attributes` and `idmp-cli attribute elements attributes --params '{"elementId":1}'`.
2. Reserve a create-safe name with `idmp-cli attribute attributes new-name --params '{"elementId":1}'`.
3. Read one live value with `idmp-cli attribute attributes data-get --params '{"elementId":1,"attributeId":2}'`.
4. Create a probe attribute only after `idmp-cli attribute attributes new-name --params '{"elementId":1}'`, then verify the create path with `idmp-cli attribute elements attributes-post --ack-risk --params '{"elementId":1}' --data '{"name":"probe-attribute","valueType":"Double"}'`.
5. Check history paging with `idmp-cli attribute historydata list --params '{"elementId":1,"attributeId":2,"current":1,"size":20,"start":1704067200000,"end":1704153600000}'`, then use `idmp-cli attribute write-data create --dry-run --ack-risk --params '{"elementId":1}' --data '{"probe":"example"}'` only after confirming the target attribute is a writable metric reference and `idmp-cli attribute evaluate-expression create --params '{"elementId":1}' --data '{"dataReferenceType":"Formula","expression":"AVG(${attributes['"'"'Current'"'"']})"}' --dry-run --ack-risk` already succeeded.
