# expression rules

These rules adapt the useful TDengine expression guidance from TDasset to this repo's direct-HTTP skill model.

## Hard rules

1. **Do not nest aggregates**: `SUM(AVG(x))` is invalid.
2. **Do not use `BETWEEN`** in panel or analysis expressions. Rewrite it as `>=` and `<=`.
3. **Do not use subqueries** inside `expression`.
4. **Use raw comparison operators**: `>`, `<`, `>=`, `<=`, `=`. Do not send HTML entities such as `&gt;` or `&lt;`.
5. **Time-series functions and time buckets are mutually exclusive**: `DERIVATIVE`, `DIFF`, `STATEDURATION`, `STATECOUNT`, `LAST_ROW`, and `CSUM` should not travel with `interval` or `window`.
6. **Grouped child aggregation is not automatically time-bucketed**: `AVG(...)` plus `groupBy` on `element` can be valid without `window`.
7. **Time-bucketed aggregation must travel as a set**: if the chart truly needs hourly or daily buckets, keep `expression`, `interval`, and `window` aligned.
8. **Leaf-only helpers should stay leaf-only by default**: `LAST`, `FIRST`, and `SPREAD` are safe defaults on self-scope leaf owners; grouped middle-owner comparisons usually need `AVG`, `MAX`, `MIN`, `SUM`, or `COUNT`.
9. **Composite metrics must keep each attribute reference explicit**: `AVG((${attributes['Current']})*(${attributes['Voltage']}))`, not `AVG(Current*Voltage)`.

## Prefer these starter patterns

### Raw self-scope series

```json
{
  "attributeExpression": "attributes['Current']",
  "expression": "${attributes['Current']}"
}
```

### Time-bucketed average

```json
{
  "attributeExpression": "attributes['Current']",
  "expression": "AVG(${attributes['Current']})",
  "interval": "1h",
  "window": {
    "windowType": "Interval",
    "timeColumn": "_wstart",
    "interval": "1h",
    "sliding": "1h",
    "fillType": "NONE"
  }
}
```

### Grouped child comparison without fake windows

```json
{
  "attributeExpression": "attributes['Current']",
  "expression": "AVG(${attributes['Current']})"
}
```

Use this together with child scope and x-axis grouping on `element`. Do not add a fake `window` unless the user explicitly wants time buckets.

### Derivative or diff without `window`

```json
{
  "attributeExpression": "attributes['Voltage']",
  "expression": "DERIVATIVE(${attributes['Voltage']}, 1h, 1)"
}
```

### State or status read

```json
{
  "attributeExpression": "attributes['Status']",
  "expression": "LAST(${attributes['Status']})"
}
```

### Composite metric

```json
{
  "attributeExpression": "attributes['Current']",
  "expression": "AVG((${attributes['Current']})*(${attributes['Voltage']}))"
}
```

## Anti-patterns

| Anti-pattern | Why it fails | Safer replacement |
| --- | --- | --- |
| `SUM(LAST(${attributes['X']}))` | nested aggregate | choose one aggregate only |
| `x BETWEEN 1 AND 10` | unsupported in expression DSL | `x >= 1 AND x <= 10` |
| `DERIVATIVE(...)` plus `window` | time-series function already defines row logic | remove `window` and `interval` |
| `AVG(...)` on grouped child compare plus fake `window` | overconstrains a non-time-bucketed panel | keep only grouped compare unless time buckets are requested |
| copying frontend HTML entities into a condition | backend receives the wrong operator tokens | use raw operators |

## When to hand off

- For full alert expressions and trigger payloads, use `../idmp-workflow-analysis-create/references/analysis-create.md`.
- For chart-specific payload starters, use `chart-type-guide.md` and `../../idmp-workflow-panel-build/references/panel-build.md`.
- For error handling after a failed expression write, use `error-recovery.md`.
