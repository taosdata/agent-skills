---
name: idmp-template
description: "IDMP template skill for reading element templates, template attributes, sub-templates, trigger types, and create-safe names without mixing template mode with live element mode."
metadata:
  author: "TaosData"
  version: "0.4.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli template --help"
---

# template

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

**Before any write:** Follow the [🛑 Destructive op confirmation protocol](../idmp-shared/SKILL.md#-destructive-op-confirmation-mandatory). Read-only commands stay read-only here, but delete / write / patch flows still require the shared yes-gate.


## Recommended shortcuts

| Shortcut | Purpose |
|----------|---------|
| `+list` | List element templates. |
| `+get` | Read one element template in detail. |
| `+attributes` | Read attribute templates under one element template. |
| `+levels` | Inspect available levels for path-style templates. |
| `+keywords` | Read naming keyword guidance for the template family. |

## Recommended reference

- [`template read flows`](references/template-read-flows.md)
- [`../idmp-workflow-analysis-create/SKILL.md`](../idmp-workflow-analysis-create/SKILL.md)

## Missing context to resolve first

| Context | Why it must be resolved before template-side create work |
| --- | --- |
| Final template owner | You need the exact `elementTemplateId` before you can read attributes, sub-templates, trigger types, or create-safe names. |
| Trigger scope | Decide `applyOnSelf` and whether a child template must be selected before you reuse trigger-type results. |
| Candidate analysis name | `analysis-template.analyses.new-name` requires a proposed `name`. |
| Template output plan | Decide whether template attributes are reused or created fresh and which `valueType` they should carry. |

## Constrained live behaviors

- Do not mix template commands with live element commands; template mode and element mode use different owners and endpoints.
- If `applyOnSelf=false`, reread `sub-templates` first and then refresh trigger types with the chosen child template scope.
- `analysis-template.analyses.new-name` requires a candidate `name` and `--ack-risk`; `attr-template attributes new-name` only needs the owner scope.
- `attr-template attributes new-name` does not require `--ack-risk`; reserve the name first, then use the later write path for the actual risk gate.
- If the task must create a live analysis or alert under a real element, switch back to the element-mode workflows rather than forcing template endpoints.

## Evidence of completion

- A template lookup is only complete when the reread shows the intended `elementTemplateId`, keyword family, or trigger scope.
- A template-side name reservation is only complete when the later create path keeps the same suggested name.
- A child-scope decision is only complete when `sub-templates` and the final trigger-type reread still agree on the same template branch.

## Template-mode rules

- Use template commands only; do not substitute live element commands.
- Read attribute templates, sub-templates, and trigger types before building template-side analysis or attribute changes.
- Trigger type choices change when `applyOnSelf` changes.
- Use `new-name` before creating template attributes or template analyses.

## Key commands

```bash
idmp-cli schema template.elements.list
idmp-cli template elements list --params '{"current":1,"size":20}'

idmp-cli schema template.elements.get
idmp-cli template elements get --params '{"elementTemplateId":123}'

idmp-cli schema attr-template.elements.attributes
idmp-cli attr-template elements attributes --params '{"elementTemplateId":123}'

idmp-cli schema template.elements.sub-templates
idmp-cli template elements sub-templates --params '{"elementTemplateId":123}'

idmp-cli analysis-template trigger-types list --params '{"elementTemplateId":123,"applyOnSelf":false}'
idmp-cli analysis-template analyses new-name --ack-risk --params '{"elementTemplateId":123,"name":"demo-analysis"}'
idmp-cli attr-template attributes new-name --params '{"elementTemplateId":123}'
```

## Exception and failure handling

- If you only have an `elementId`, verify that the task is not really live element work before switching to template mode.
- If `sub-templates` is empty, child-scope analysis options are not available for that template.
- If `applyOnSelf` changes, re-read trigger types before reusing an earlier choice.
- If `new-name` suggests a different value, use the suggested name instead of forcing a duplicate.
- If a template is missing, renamed, or access is denied, refresh the list and session before attempting template writes.

## Validation scenarios

1. List available templates with `idmp-cli schema template.elements.list` and `idmp-cli template elements list --params '{"current":1,"size":20}'`.
2. Read one template with `idmp-cli schema template.elements.get` and `idmp-cli template elements get --params '{"elementTemplateId":123}'`.
3. Read template attributes with `idmp-cli attr-template elements attributes --params '{"elementTemplateId":123}'`.
4. Check child-scope analysis readiness with `idmp-cli template elements sub-templates --params '{"elementTemplateId":123}'` and `idmp-cli analysis-template trigger-types list --params '{"elementTemplateId":123,"applyOnSelf":false}'`.
5. Reserve create-safe names with `idmp-cli analysis-template analyses new-name --ack-risk --params '{"elementTemplateId":123,"name":"demo-analysis"}'` and `idmp-cli attr-template attributes new-name --params '{"elementTemplateId":123}'`.
