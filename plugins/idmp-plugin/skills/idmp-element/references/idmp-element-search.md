# idmp-cli element +search

```bash
idmp-cli element +search "meter-keyword"
```

This maps to `getElementsBySearchCondition()` and calls `GET /elements/search`.

Useful for:

- searching elements by device name or area keyword
- locating an asset before you know the `elementId`

Recommended frontend-style query order:

```bash
idmp-cli element elements search --params '{"keyword":"district","current":1,"limitSize":20}'
idmp-cli element elements path --params '{"elementId":123}'
```

Common filters:

- `keyword`: fuzzy match on name or description
- `elementRootId`: search only under one business root
- `elementParentId`: search only under one parent
- `includeSubElements`: enable recursive search
- `templateId`: search only one template type
