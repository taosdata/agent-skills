# idmp-cli element +tree

```bash
idmp-cli element +tree 123
```

The frontend tree view is still backed by level-by-level `list` calls. Analysis and panel workflows usually add `sub-templates` on top.

Useful for:

- checking one level or an entire subtree under a node
- inspecting the asset hierarchy

If you plan to do hierarchy aggregation or child-template outputs, do not stop at `+tree`:

```bash
idmp-cli element elements list --params '{"parentId":123,"current":1,"size":50}'
idmp-cli element elements sub-templates --params '{"elementId":123}'
idmp-cli element elements first-level-sub-templates --params '{"elementId":123}'
```

Notes:

- `sub-templates`: child element templates seen anywhere in the subtree
- `first-level-sub-templates`: child element templates only from the first level
