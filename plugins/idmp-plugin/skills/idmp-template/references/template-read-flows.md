# template read flow

Template mode corresponds to the TDasset frontend libraries page. Do not substitute real-element endpoints for template-mode reads.

Recommended order:

1. start with `idmp-cli template +list`
2. then use `idmp-cli template +get <template-id>`
3. use `idmp-cli template +attributes <template-id>` when attribute templates are needed
4. use `idmp-cli template +levels <template-id>` when template hierarchy is needed
5. use `idmp-cli template +keywords <template-id>` when naming keywords are needed
6. for analysis-template dependencies, add:

   ```bash
   idmp-cli template elements sub-templates --params '{"elementTemplateId":123}'
   idmp-cli analysis-template trigger-types list --params '{"elementTemplateId":123,"applyOnSelf":false}'
   idmp-cli attr-template attributes new-name --params '{"elementTemplateId":123}'
   ```

These three calls answer:

- `sub-templates`: selectable child element templates in template mode
- `trigger-types`: which analysis triggers the template supports
- `new-name`: how the frontend gets the default name before creating an attribute template
