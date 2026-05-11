# analysis read flow

The frontend analysis list page mainly relies on two paths:

1. owner-scoped listing: `getElementAnalysisListByPage()`
2. global search: `getAnalysisListByCondition()`

Typical order:

1. When the owner element is known:

   ```bash
   idmp-cli analysis analyses list --params '{"elementId":123,"current":1,"size":20}'
   ```

2. When the owner element is not known yet:

   ```bash
   idmp-cli analysis analysis search --params '{"keyword":"Current","current":1,"size":20}'
   ```

3. When one analysis must be confirmed precisely:

   ```bash
   idmp-cli analysis analyses get --params '{"elementId":123,"id":456}'
   ```

4. When the status must change:

   ```bash
   idmp-cli analysis analyses resume --ack-risk --params '{"elementId":123,"id":456}'
   idmp-cli analysis analyses pause --ack-risk --params '{"elementId":123,"id":456}'
   ```

If the next step is create or edit, do not stop at the read layer. Switch to the workflow skill and continue with:

- `element path`
- `attributes`
- `sub-templates`
- `trigger-types`
- `new-name`
