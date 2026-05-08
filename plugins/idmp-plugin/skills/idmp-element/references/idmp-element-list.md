# idmp-cli element +list

```bash
idmp-cli element +list --parent-id 123 --size 20 --current 1
```

This maps to `getElements()` in `TDasset/frontend/src/api/element.ts`, which is essentially `GET /elements`.

Common use cases:

- browsing root nodes
- browsing elements under a site, line, or device group
- quick inspection with `--format table`

When more control is needed, use the generated command directly:

```bash
idmp-cli element elements list --params '{"parentId":123,"current":1,"size":20}'
idmp-cli element elements list --params '{"parentId":123,"templateId":456,"current":1,"limitSize":100}'
```

Parameter meaning:

- `parentId`: parent of the current level; omit it to list root nodes
- `templateId`: filter to one template type
- `topElementId`: restrict browsing to a business root
- `current` / `size` / `limitSize`: frontend-style paging controls
