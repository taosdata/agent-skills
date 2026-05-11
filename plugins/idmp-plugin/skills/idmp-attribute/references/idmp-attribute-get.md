# idmp-cli attribute +get

```bash
idmp-cli attribute +get 123 456
```

Reading one current value in the frontend is effectively:

```bash
idmp-cli attribute attributes data-get --params '{"elementId":123,"attributeId":456}'
```

Useful for quick checks:

- whether the point currently has a value
- whether the analysis or panel input is valid
- whether the target attribute is the correct one before `create` or `update`
