# idmp-cli attribute +history

```bash
idmp-cli attribute +history 123 456 --current 1 --size 20
```

This maps to `getAttributeHistoryData()` and calls:

```bash
GET /elements/{elementId}/attributes/{attributeId}/historydata
```

Optional flags:

- `--start`
- `--end`

Useful for:

- reading time-series history for a point
- debugging alert or analysis input data

When paging must be controlled precisely, use the generated command directly:

```bash
idmp-cli attribute historydata list --params '{"elementId":123,"attributeId":456,"start":1710000000000,"end":1710003600000,"current":1,"size":50}'
```
