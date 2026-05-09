# analysis create flow

Use this reference after the main workflow doc. It distills the payload shapes that already succeed in the repo's live analysis variants.

## AI-first create path

For natural-language requests, prefer this two-step chain before the manual DTO workflow:

1. `idmp-cli ai create create --ack-risk --data '{"elementId":123,"prompt":"Create a 1-minute average-current analysis","record":true,"deepThinking":false,"deviceDocument":false}'`
2. Persist the returned draft through `idmp-cli analysis analyses create --ack-risk --params '{"elementId":123}' --data '{...}'`

Hard rules for the persisted payload:

- remove the draft `id`
- inject the real `rootElementId`
- keep the returned output attribute IDs only if they are still valid for the final owner scope
- if persistence fails, clean any draft-created output attributes before the structured fallback
- if AI draft creation times out, classify the first attempt as backend AI/API latency and switch to the structured payload flow instead of rephrasing the prompt into a different analysis

## Shared-environment success tiers

1. **Create proof**: `analysis analyses create`, `get`, and `list` all show the same persisted analysis.
2. **Runtime proof**: `analysis analyses resume` reread shows the analysis in the expected running state.
3. **Cleanup proof**: delete and attribute cleanup succeed. This is best-effort only in the current live environment.

Once tiers 1 and 2 succeed, current live output-attribute cleanup leaks should be reported separately as a backend boundary, not as a payload-shape failure.

## Proven variant matrix

| Variant | Owner | Trigger preflight | Output scope | Payload rule |
| --- | --- | --- | --- | --- |
| leaf self | data-bearing leaf element | `analysis trigger-types list --params '{"elementId":123,"applyOnSelf":true}'` includes `Interval` | `output.applyOnSelf=true` | Use the self-scope Interval payload below. |
| middle self | template-backed metric middle owner | same self-scope check on that middle owner | `output.applyOnSelf=true` | Reuse the same self-scope payload; only the owner changes. |
| middle child aggregation | template-backed middle owner plus child template from `element elements sub-templates` | `analysis trigger-types list --params '{"elementId":123,"applyOnSelf":false,"elementTemplateId":456}'` includes `Interval` | `output.applyOnSelf=false` | Start from the self-scope payload, then apply the child-scope delta. Keep `output.elementTemplate.id` on the child template, but resolve `output.attributes[].attrId` from a real persisted output attribute on the owner element. |

## Stable self-scope Interval payload

Replace only the obvious placeholders (`name`, `rootElementId`, source attribute, output attr IDs). Do not collapse this payload to `{"name":"..."}`.

```json
{
  "name": "demo-analysis",
  "rootElementId": 1,
  "startAfterCreated": true,
  "recalculate": false,
  "trigger": {
    "type": "Interval",
    "interval": "1m",
    "count": 5,
    "sliding": "1m",
    "periodTime": "1m",
    "offsetTime": "0s",
    "states": [],
    "expressions": [],
    "preFilter": true,
    "preFilterExpression": "",
    "fillHistory": false,
    "fillHistoryFirst": false,
    "fillHistoryStartTime": null,
    "eventTrigger": {
      "starts": [
        {
          "name": "",
          "expression": "",
          "duration": "10s",
          "parameters": [],
          "severity": "Information",
          "allowAck": false
        }
      ],
      "end": {
        "name": "",
        "expression": "",
        "duration": "1m",
        "parameters": [],
        "severity": "Information",
        "allowAck": false
      },
      "duration": "1m"
    }
  },
  "output": {
    "applyOnSelf": true,
    "elementTemplate": {
      "id": null,
      "filter": "",
      "rootElement": 0,
      "level": 0
    },
    "rollupWindow": {
      "enabled": true,
      "interval": "1m",
      "startTime": "_wstart",
      "startTimeOffset": "0s",
      "endTime": "_wend",
      "endTimeOffset": "0s"
    },
    "columnName": "_wend",
    "offset": "0s",
    "attributes": [
      {
        "attrId": 456,
        "attrName": "analysis-output",
        "expression": "AVG(${attributes['Current']})",
        "parameters": [],
        "eventAttrId": null,
        "eventAttrName": ""
      }
    ]
  }
}
```

## Child-aggregation delta

For the stable `applyOnSelf=false` variant, keep the entire self-scope payload above and change only the child-scope output fields:

```json
{
  "output": {
    "applyOnSelf": false,
    "elementTemplate": {
      "id": 456,
      "filter": "",
      "rootElement": 0,
      "level": 0
    },
    "attributes": [
      {
        "attrId": 789,
        "attrName": "owner-element-output",
        "expression": "AVG(${attributes['Current']})",
        "parameters": [],
        "eventAttrId": null,
        "eventAttrName": ""
      }
    ]
  }
}
```

Hard rules:

- Keep `rootElementId` on the business root. Do not rewrite it to the middle owner.
- `output.elementTemplate.id` must be the explicit child template ID returned by `sub-templates`.
- `output.attributes[].attrId` must be a real persisted output attribute ID. In current live `ELE_SUBET` flows, owner-local output attributes are valid and are the documented/tested path; template attribute IDs are not required.

## Middle-owner bootstrap that actually works

When the operator wants a non-leaf proof owner, first create a plain container parent, then create template-backed metric elements under it. Do not mix these paths.

```bash
idmp-cli element elements create --ack-risk --data '{"name":"sandbox-parent","parentElementId":1,"referenceType":"ParentChild"}'
idmp-cli template +keywords 456
idmp-cli element new create --ack-risk --data '{"parentElementId":2,"referenceType":"ParentChild","templateId":456,"keywordValues":{"<TEMPLATE_KEY>":"<existing-source-keyword-value-1>"},"force":true}'
idmp-cli element new create --ack-risk --data '{"parentElementId":2,"referenceType":"ParentChild","templateId":456,"keywordValues":{"<TEMPLATE_KEY>":"<existing-source-keyword-value-2>"},"force":true}'
idmp-cli element new create --ack-risk --data '{"parentElementId":2,"referenceType":"ParentChild","templateId":456,"keywordValues":{"<TEMPLATE_KEY>":"<existing-source-keyword-value-3>"},"force":true}'
```

The live-safe assumption is: the keyword-backed TDengine tables or source rows already exist, and the keyword field name must come from `template +keywords` for the chosen template.

## Temporary hierarchy cleanup boundary

The temporary middle-owner hierarchy is useful reusable evidence for later child-scope checks. If the async delete task returns a task ID but later lands in `FAILED`, classify that as a backend cleanup boundary after the owner and children were already created and reread successfully. Do not keep retrying destructive cleanup loops in the shared environment.

## One-shot checklist

1. Resolve the business root with `element elements path`; that value becomes `rootElementId`.
2. If the request is natural language, try `POST /api/v1/ai/analysis/create` first and keep the returned draft for persistence or fallback analysis.
3. Confirm the chosen owner advertises the trigger family you need.
4. Reserve the name with `analysis analyses new-name` only when the AI draft path is skipped or unsuitable.
5. Resolve the correct output scope before you create or reuse attributes.
6. Use the full live-safe payload shape, not a minimal payload.
7. Reread with `get` and `list`, then `resume` if runtime state matters.
8. If delete leaves the generated output attribute referenced after a proven running reread, stop cleanup retries and keep the leaked IDs in the evidence.

## Source-derived trigger starter library

These starters are adapted from the product trigger templates and translated to this repo's direct-HTTP payload style. They are **not all live-proven in this repo**, so always confirm `trigger-types list` and `schema` before the real write.

Start from the stable self-scope payload above unless a child-scope or Event-specific variant is already documented elsewhere in this file.

### Session offline delta

Replace the `trigger` block with:

```json
{
  "trigger": {
    "type": "Session",
    "interval": "5m"
  }
}
```

Typical output expression:

```json
{
  "expression": "LAST(${attributes['Voltage']})"
}
```

Use this when the intent is "no data for N minutes" or "offline detection". Do not add `sliding`.

### State-trigger delta

```json
{
  "trigger": {
    "type": "State",
    "expressions": [
      "${attributes['Phase']}"
    ],
    "states": [
      "0",
      "1",
      "2"
    ],
    "duration": "10m"
  }
}
```

Typical output expression:

```json
{
  "expression": "COUNT(${attributes['Phase']})"
}
```

Keep `expressions` and `states` together. If one is missing, stop and rebuild the trigger.

### Count-window delta

```json
{
  "trigger": {
    "type": "Count",
    "count": 100,
    "slidingCount": 20
  }
}
```

Typical output expression:

```json
{
  "expression": "AVG(${attributes['Power']})"
}
```

### Period delta

```json
{
  "trigger": {
    "type": "Period",
    "periodTime": "8h",
    "offsetTime": "10m"
  }
}
```

Typical output expressions:

```json
[
  {
    "expression": "AVG(${attributes['Power']})"
  },
  {
    "expression": "MAX(${attributes['Current']})"
  }
]
```

### DataInput delta

```json
{
  "trigger": {
    "type": "DataInput",
    "count": 1
  }
}
```

Typical output expression:

```json
{
  "expression": "${attributes['Current']} * ${attributes['Voltage']}"
}
```

### AnomalyDetection delta

```json
{
  "trigger": {
    "type": "AnomalyDetection",
    "sliding": "10m",
    "anomalyDetectionConfig": {
      "algorithm": "ksigma",
      "algorithmParameters": "k=3",
      "targetAttributeExpressions": [
        "${attributes['Voltage']}"
      ],
      "whiteNoiseDataCheck": false
    }
  }
}
```

Typical output expression:

```json
{
  "expression": "MAX(${attributes['Voltage']})"
}
```

## Trigger anti-patterns

1. Do not force a trigger family that `trigger-types list` does not advertise on the final owner scope.
2. Do not copy Event-trigger payloads into generic analysis flows; use the dedicated alert-create reference for that path.
3. Do not reuse output IDs across the wrong final owner scope. Child-scope analyses still need `output.elementTemplate.id` for the child template, but current live `ELE_SUBET` flows resolve `output.attributes[].attrId` on the owner element.
4. For anomaly detection, keep `sliding` at the trigger top level and keep `algorithmParameters` as a string.

## Batch creation mode

Use this when many analyses must be created with the same shape:

1. parallelize read-only discovery: owner search, path, sub-templates, trigger-types, and output-attribute inventory
2. reserve names and prepare output attributes in bounded batches
3. create analyses serially or in very small batches in shared environments
4. after each create, run `get`, `list`, and `resume` before moving to the next owner
5. stop the batch on the first scope drift, trigger mismatch, or repeated schema error

Recommended batch safety rules:

- reuse one proven payload family per owner class
- never mix self-scope and child-scope creates in the same blind batch
- keep cleanup local to the failed owner before the next create starts
