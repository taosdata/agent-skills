# idmp-cli attribute +data

```bash
idmp-cli attribute +data 123
idmp-cli attribute +data 123 --attribute-ids 456,789
```

When the frontend wants to show current values in an attribute list, it first loads definitions and then runs a batch value read:

- `POST /elements/{elementId}/attributes/data`
- implemented by `batchGetAttributeData()`

The CLI can use it in two ways:

1. let the shortcut resolve a set of attributes before reading
2. pass known attribute IDs directly

Equivalent generated command:

```bash
idmp-cli attribute attributes data-post --ack-risk --params '{"elementId":123}' --data '[456,789]'
```

Useful for:

- reading several current values from one element at once
- choosing input attributes for analysis or panel expressions
- confirming current state before `write-data`
