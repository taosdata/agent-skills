# idmp-cli attribute +list

```bash
idmp-cli attribute +list 123
```

The frontend usually starts with `GET /elements/{elementId}/attributes`, that is, `getAttributes()`.

This answers "which attribute instances exist on this element, and what are their type, template, UOM, and traits?" It is not a historical-value query.

If current values are also needed, the frontend adds a batch value read:

```bash
idmp-cli attribute +data 123
idmp-cli attribute attributes data-post --ack-risk --params '{"elementId":123}' --data '[456,789]'
```

Recommended order:

1. `attribute +list <element-id>`
2. confirm the target attribute `id`, `attrTempId`, and `name`
3. then choose `+get`, `+data`, or `+history`
