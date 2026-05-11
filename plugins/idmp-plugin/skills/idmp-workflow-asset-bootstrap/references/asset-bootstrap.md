# asset bootstrap flow

Use this reference after the main workflow doc. Bootstrap should answer one question before any modeling or ingestion write: **is this environment model-ready, ingestion-ready, both, or neither?**

## Bootstrap outcome matrix

| Outcome | What must be true |
| --- | --- |
| model-ready | visible roots, stable paths, template family, child templates, attribute templates, and UOM expectations are all readable |
| ingestion-ready | datasource visibility and import or export traces are readable |
| fully ready | both model-ready and ingestion-ready |
| blocked | any of the required visibility or scope reads fail or are missing |

## 1. Root and path closure

```bash
idmp-cli element elements list --params '{"current":1,"size":20}'
idmp-cli element elements path --params '{"elementId":123}'
idmp-cli element fullpath get --params '{"rootElementId":100,"elementId":123}'
idmp-cli element by-path list --params '{"elementPath":"Utilities/Beijing/Chaoyang/Device-A"}'
```

Required closure:

- a visible root or parent scope
- a stable path from owner to root
- a reverse lookup path that resolves the same object

## 2. Template-family closure

```bash
idmp-cli template elements list --params '{"current":1,"size":20}'
idmp-cli element elements sub-templates --params '{"elementId":123}'
idmp-cli attr-template elements attributes --params '{"elementTemplateId":456}'
```

Required closure:

- the intended template family exists
- the chosen owner exposes expected child templates
- the attribute-template set matches the intended metrics or tags

## 3. Measurement semantics

```bash
idmp-cli uom uomclasses list
idmp-cli uom uom search --params '{"keyword":"kWh","limitSize":20}'
```

Use this to prove the model can express the intended units before any attribute or template mutation.

## 4. Ingestion visibility

```bash
idmp-cli datasource connections list
idmp-cli data first-level-elements list
idmp-cli data records list
```

Interpretation:

- if datasource connections are empty but roots and templates are healthy, the environment can still be model-ready
- if records exist but roots do not, import or export traces may belong to another scope or an old environment state

## Next-step handoff starters

Bootstrap itself should remain read-first, but once it passes you can hand off these payload starters to the owning workflows.

### Plain container owner

```json
{
  "name": "sandbox-parent",
  "parentElementId": 0,
  "referenceType": "ParentChild"
}
```

This belongs to:

```bash
idmp-cli element elements create --ack-risk --data '{...}'
```

### Template-backed metric owner

```json
{
  "parentElementId": 0,
  "referenceType": "ParentChild",
  "templateId": 456,
  "keywordValues": {
    "<TEMPLATE_KEY>": "<existing-source-keyword-value>"
  },
  "force": true
}
```

This belongs to:

```bash
idmp-cli element new create --ack-risk --data '{...}'
```

If later async delete tasks for this temporary hierarchy return task IDs but finish in `FAILED`, keep the created owner and child IDs in the evidence and treat that as a backend cleanup boundary. The bootstrap proof is still valid once the hierarchy was created and reread successfully.

### Datasource CSV starter

```text
datasource csv create
- required multipart fields: csvFile, tableName
- optional fields: hasHeader, quote, escapeChar
```

Use this only after ingestion visibility is confirmed and hand off to `../idmp-workflow-data-import-export/SKILL.md`.

## One-shot checklist

1. Prove the root path in both directions.
2. Prove the template family and child-template inventory.
3. Prove UOM compatibility for the intended model.
4. Prove datasource and record visibility separately.
5. Record the outcome as model-ready, ingestion-ready, fully ready, or blocked.
