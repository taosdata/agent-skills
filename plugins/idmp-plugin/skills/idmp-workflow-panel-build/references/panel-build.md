# panel build flow

Use this reference after the main workflow doc. It distills the payload shapes that already succeed in the repo's live panel variants.

## AI-first panel draft path

For natural-language panel requests, prefer this two-step chain before the manual DTO families:

1. `idmp-cli ai create create-post --ack-risk --data '{"elementId":123,"prompt":"...","record":true}'`
2. Persist the returned draft through `idmp-cli panel panels create --ack-risk --params '{"elementId":123}' --data '{...}'`

Hard rules:

- remove the draft `id`
- reread with `panel panels get`
- rerun `panel.panels.query` or `panel.panels.sqls` on the persisted DTO before claiming success
- if the AI draft collapses child scope, loses required placement/query fields, or cannot persist, switch to the structured DTO families below

The JSON starters below are intentionally separated by scope:

- self scope: leaf owner or middle owner acting on itself
- child aggregation: middle owner aggregating child elements
- advanced fallback: persisted SQL when no-code child scope collapses on reread

Do not merge these payload families. Older TDasset examples that force `interval` plus `window` for every aggregate should be treated only as time-bucketed cases, not as the default for grouped child aggregation.

## Three DTO families

| Use | Command | Payload family | Hard rule |
| --- | --- | --- | --- |
| time-range validation | `panel.verify.create` | `{from,to}` only | Do not send `elementId` or panel DTO fields here. |
| query-backed / no-code panel query | `panel.panels.query` / `panel.panels.sqls` | panel DTO | Keep `rootElementId`, `params`, `xaAttributes`, and `yaAttributes` on the payload. |
| panel persistence | `panel.panels.create` | panel DTO | Creating the panel object does not place it into a dashboard. |
| advanced SQL verification | `panel.verify.create-post` | one advanced-query DTO | Do not send the full panel DTO here. |

## Child-scope success rule

For child aggregation, there are two acceptable first-attempt endings:

1. the no-code child-scope DTO survives reread, query, and SQL checks; or
2. the no-code DTO proves the intended SQL through `panel.panels.sqls`, then the advanced fallback survives `panel.verify.create-post` plus persisted reread with `enableAdvanced=true`.

Do not downgrade case 2 into a failure just because the no-code DTO collapsed to self scope on reread.

## Proven payload starters

### 1. Self-scope leaf or middle-self query-backed line panel

This starter works on a data-bearing leaf owner and on a template-backed middle owner.

```json
{
  "name": "demo-panel",
  "description": "copilot query-backed panel",
  "panelType": "line",
  "enableAdvanced": false,
  "advancedQueries": [],
  "enablePercentile": false,
  "limit": 0,
  "thumbnail": "",
  "rootElementId": 1,
  "params": {
    "fromText": "now-12h",
    "toText": "now"
  },
  "xaAttributes": [],
  "yaAttributes": [
    {
      "uuid": "00000000-0000-0000-0000-000000000001",
      "attributeExpression": "attributes['Current']",
      "expression": "${attributes['Current']}",
      "function": "",
      "parameters": [],
      "checked": true,
      "timeShift": "0m",
      "filter": "",
      "alias": "Current",
      "formula": false,
      "displayDigits": null,
      "displayUom": null,
      "defaultUomClassId": null
    }
  ]
}
```

## 2. Child-aggregation no-code preflight payload

This is intentionally a grouped compare, not a time-bucketed panel. The aggregate expression is valid even without a `window`.

```json
{
  "name": "demo-child-compare",
  "description": "copilot child aggregation panel",
  "panelType": "line",
  "enableAdvanced": false,
  "advancedQueries": [],
  "enablePercentile": false,
  "limit": 0,
  "thumbnail": "",
  "rootElementId": 1,
  "otherElementTemplateId": 456,
  "params": {
    "fromText": "now-12h",
    "toText": "now"
  },
  "xaAttributes": [
    {
      "uuid": "00000000-0000-0000-0000-000000000010",
      "attributeExpression": "element",
      "expression": "element",
      "groupBy": true,
      "checked": true,
      "timeShift": "0m",
      "filter": "",
      "alias": "element",
      "formula": false,
      "displayDigits": null,
      "displayUom": null,
      "defaultUomClassId": null
    }
  ],
  "yaAttributes": [
    {
      "uuid": "00000000-0000-0000-0000-000000000011",
      "attributeExpression": "attributes['Current']",
      "expression": "AVG(${attributes['Current']})",
      "function": "",
      "parameters": [],
      "checked": true,
      "timeShift": "0m",
      "filter": "",
      "alias": "avg-Current",
      "formula": false,
      "displayDigits": null,
      "displayUom": null,
      "defaultUomClassId": null
    }
  ]
}
```

Hard rules for this variant:

- `otherElementTemplateId` must be the explicit child template ID.
- Keep the x-axis grouping on `element`.
- Do not add a fake `window` only because the y-axis expression uses `AVG(...)`.
- Use this payload first for `panel.panels.sqls` and `panel.panels.query`; only then decide whether you need the advanced fallback.
- If reread collapses this DTO back to self scope, keep the proven SQL and move directly to the advanced fallback instead of redesigning the business intent.

### 3. Advanced fallback payload

After `panel.panels.sqls` returns the correct child-scope SQL, persist that exact SQL as an advanced panel:

```json
{
  "name": "demo-child-compare",
  "description": "copilot advanced child aggregation panel",
  "panelType": "line",
  "enableAdvanced": true,
  "enablePercentile": false,
  "limit": 0,
  "thumbnail": "",
  "advancedQueries": [
    {
      "uuid": "00000000-0000-0000-0000-000000000020",
      "name": "child-aggregation",
      "advancedQueryType": "TDengine",
      "querySqls": [
        "SELECT _wstart, AVG(voltage) AS avg_voltage, element FROM meters INTERVAL(1h) PARTITION BY element"
      ],
      "timeColumn": "",
      "dimensions": [
        "element"
      ],
      "checked": true
    }
  ],
  "params": {
    "fromText": "now-12h",
    "toText": "now"
  },
  "xaAttributes": [],
  "yaAttributes": []
}
```

Verify the single object inside `advancedQueries[0]` with `panel.verify.create-post` before you call `panel.panels.create`.

Typical child-scope command chain:

```bash
idmp-cli panel panels new-name --params '{"elementId":123,"name":"demo-child-compare"}'
idmp-cli panel panels sqls --ack-risk --params '{"elementId":123}' --data '{...no-code child DTO...}'
idmp-cli panel verify create-post --ack-risk --params '{"elementId":123}' --data '{...advancedQueries[0] object...}'
idmp-cli panel panels create --ack-risk --params '{"elementId":123}' --data '{...advanced fallback panel DTO...}'
idmp-cli panel panels get --params '{"elementId":123,"panelId":456}'
```

## One-shot rules that prevent common misses

1. Use `panel.panels.new-name` before `create`.
2. Use `panel.verify.create` only for the `{from,to}` payload; extra owner params such as `elementId` are a type mismatch.
3. Use the plain panel DTO for `query`, `sqls`, and `create`.
4. Use the advanced-query DTO only for `panel.verify.create-post`.
5. For time-bucketed aggregation, keep `expression`, `interval`, and `window` together.
6. For grouped child comparisons, `AVG(...)` plus `groupBy` can be enough with no `window`.
7. Accept the advanced fallback only when reread proves `enableAdvanced=true` survived.

## Source-derived specialized starter deltas

These starters are adapted from TDasset panel templates and translated to the current repo's panel DTO conventions. Use them as deltas on top of the self-scope or child-aggregation starters above, and always run `query`, `sqls`, or `verify` before `create`.

### Gauge current-value delta

```json
{
  "panelType": "gauge",
  "yaAttributes": [
    {
      "attributeExpression": "attributes['Power']",
      "expression": "LAST(${attributes['Power']})",
      "alias": "Power"
    }
  ],
  "params": {
    "fromText": "now-5m",
    "toText": "now",
    "chart": {
      "standardOptions": {
        "min": 0,
        "max": 5000,
        "colorSchema": "from-thresholds"
      },
      "colorThresholds": [
        {
          "value": 0,
          "color": "#91CC75",
          "default": true
        },
        {
          "value": 2000,
          "color": "#FAC858"
        },
        {
          "value": 4000,
          "color": "#EE6666"
        }
      ]
    }
  }
}
```

### Pie grouped-share delta

```json
{
  "panelType": "pie",
  "xaAttributes": [
    {
      "attributeExpression": "element",
      "expression": "element",
      "groupBy": true,
      "alias": "element"
    }
  ],
  "yaAttributes": [
    {
      "attributeExpression": "attributes['Power']",
      "expression": "AVG(${attributes['Power']})",
      "alias": "avg-Power"
    }
  ]
}
```

Use this only when one grouping dimension is explicit.

### Scatter correlation delta

```json
{
  "panelType": "scatter",
  "xaAttributes": [
    {
      "attributeExpression": "attributes['Current']",
      "expression": "${attributes['Current']}",
      "alias": "Current"
    }
  ],
  "yaAttributes": [
    {
      "attributeExpression": "attributes['Voltage']",
      "expression": "${attributes['Voltage']}",
      "alias": "Voltage"
    }
  ],
  "params": {
    "chart": {
      "series": {
        "symbol": "circle",
        "symbolSize": 10
      }
    }
  }
}
```

### State timeline delta

```json
{
  "panelType": "state-timeline",
  "yaAttributes": [
    {
      "attributeExpression": "attributes['Status']",
      "expression": "LAST(${attributes['Status']})",
      "alias": "Status"
    }
  ],
  "params": {
    "chart": {
      "valueMappings": [
        {
          "valueType": "value",
          "value": 0,
          "display": "offline",
          "color": "#EE6666"
        },
        {
          "valueType": "value",
          "value": 1,
          "display": "online",
          "color": "#91CC75"
        }
      ],
      "colorThresholds": [
        {
          "value": 0,
          "color": "#EE6666",
          "default": true
        },
        {
          "value": 1,
          "color": "#91CC75"
        }
      ]
    }
  }
}
```

### Derivative no-window delta

```json
{
  "panelType": "line",
  "yaAttributes": [
    {
      "attributeExpression": "attributes['Voltage']",
      "expression": "DERIVATIVE(${attributes['Voltage']}, 1h, 1)",
      "alias": "voltage-derivative"
    }
  ]
}
```

Do not add `interval` or `window` here.

### Composite-expression delta

```json
{
  "panelType": "line",
  "yaAttributes": [
    {
      "attributeExpression": "attributes['Current']",
      "expression": "AVG((${attributes['Current']})*(${attributes['Voltage']}))",
      "alias": "computed-Power"
    }
  ]
}
```

## Degradation strategy

Use the lightest successful panel family first:

1. **AI draft + persist** for natural-language requests
2. **plain self-scope or child-scope panel DTO**
3. **`query` and `sqls` reread on the plain DTO**
4. **advanced-query fallback** only when child scope collapses or persistence breaks
5. **text or manual shell** only when SQL generation is not applicable by design

Stop and redesign instead of escalating blindly when:

- the chart intent is still ambiguous
- the backend keeps rejecting the same DTO family after one schema correction
- the panel type does not actually match the user's question

## Batch build mode

When the operator wants many panels:

1. parallelize read-only discovery: owners, paths, templates, attributes, and existing panel inventory
2. group targets by payload family: self-scope line, grouped child compare, gauge or stat, specialized chart
3. reserve names before writes
4. create in serial or small bounded batches in shared environments
5. rerun `get`, `query`, and `sqls` for each panel class before the next batch starts

Recommended guardrails:

- do not mix grouped child compare and self-scope line panels in one blind batch
- if the first panel in a batch needs advanced fallback, redesign the whole batch before continuing
- dashboard placement should happen only after panel persistence is already stable
