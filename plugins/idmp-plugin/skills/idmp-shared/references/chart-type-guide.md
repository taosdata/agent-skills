# chart-type guide

Use this guide together with `../../idmp-workflow-panel-build/references/panel-build.md`. The workflow reference holds the main payload families; this guide helps choose the right panel type and the safest starter.

## Intent to chart-type map

| User intent | Recommended `panelType` | Default metric pattern |
| --- | --- | --- |
| trend, monitor, time series | `line` | raw series or time-bucketed `AVG` |
| ranking, compare categories | `bar` | grouped `AVG` / `SUM` / `COUNT` |
| proportion, share, composition | `pie` | grouped aggregate plus one group-by dimension |
| current value, latest status | `gauge` or `stat` | `LAST(...)` |
| correlation between two numeric signals | `scatter` | one x numeric series plus one y numeric series |
| state history or online/offline | `state-timeline` or `state-history` | `LAST(...)` plus `valueMappings` and `colorThresholds` |
| detail grid | `table` | query-backed table DTO |
| computed metric over time | `line` | composite expression such as `AVG((A)*(B))` |

## Type-specific rules

### `line`

- best default for trends and monitoring
- use `xaAttributes=[]` for plain time series
- use time buckets only when the user explicitly asks for hourly, daily, or similar aggregation

### `bar`

- use for grouped comparisons or rankings
- if a dashboard asks for "top N", pair grouped metrics with explicit sort or limit behavior in the chart settings

### `pie`

- require one grouping dimension
- keep the number of slices small
- prefer grouped child aggregation or tag grouping; do not use it for long time series

### `gauge` / `stat`

- use `LAST(...)`
- treat them as single-value panels, not multi-series comparisons
- thresholds and color bands are usually more important than axes

### `scatter`

- x-axis numeric series goes in `xaAttributes`
- y-axis numeric series goes in `yaAttributes`
- this is a relationship panel, not a trend panel

### `state-timeline` / `state-history`

- require `valueMappings` and `colorThresholds`
- use them only when the underlying attribute behaves like a state code or status signal

## Starter selection

| Starter you should begin from | Use when |
| --- | --- |
| self-scope line starter | leaf or middle owner trend panel |
| child-aggregation preflight payload | grouped child compare |
| advanced fallback payload | child scope collapses on reread |
| gauge delta | current-value display |
| pie delta | grouped share or composition |
| scatter delta | two-signal correlation |
| state delta | status history or online-offline history |
| derivative delta | rate-of-change panel without buckets |

Those starters live in `../../idmp-workflow-panel-build/references/panel-build.md`.

## Anti-patterns

| Anti-pattern | Better choice |
| --- | --- |
| `pie` with dozens of groups | `bar` |
| `gauge` for multiple metrics | `bar`, `line`, or `table` |
| `scatter` for one time-series metric | `line` |
| state timeline without value mappings | `line` or a completed state starter |
| forcing `window` into derivative or grouped compare panels | use the dedicated derivative or child-aggregation starter |
