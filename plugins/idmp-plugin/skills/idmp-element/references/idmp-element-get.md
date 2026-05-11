# idmp-cli element +get

```bash
idmp-cli element +get 123
```

The common frontend order is not "call get immediately". It is:

1. use `search` to find candidate elements
2. use `path` to confirm the path and `rootElementId`
3. use `get` to read the current element detail

Generated commands:

```bash
idmp-cli element elements get --params '{"elementId":123}'
idmp-cli element elements path --params '{"elementId":123}'
```

Useful for:

- reading element details
- pairing with `path` to verify that `elementId` is correct
- confirming the owner element before writing an analysis, panel, or rule
