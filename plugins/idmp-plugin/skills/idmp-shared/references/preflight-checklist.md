# preflight checklist

Use this checklist before any mutating workflow. It is intentionally shared so analysis, panel, alert, datasource, and import or export skills do not invent different gate rules for the same risks.

## Universal preflight

1. **Resolve the working mode**: element mode or template mode.
2. **Resolve the owner**: final `elementId` or `elementTemplateId`.
3. **Resolve the business root**: in element mode, read the path and capture the correct `rootElementId`.
4. **Resolve the scope**: self scope, child scope, dashboard scope, template scope, or datasource scope.
5. **Resolve the payload family**: plain DTO, advanced-query DTO, multipart import DTO, notify-rule DTO, or wrapper DTO.
6. **Reserve safe names**: call `new-name` when the workflow supports it, and pass the correct candidate `name`.
7. **Inspect the schema**: use `idmp-cli schema <schemaPath>` before any nontrivial write, especially when body shape is not already proven.
8. **Choose the verification target**: decide which reread proves success before the write happens.

## Risk gate

Before any actual write:

1. run the destructive-op confirmation protocol from `../SKILL.md`
2. prefer `--dry-run` when the command supports it
3. make sure `--ack-risk` is present for non-readonly automation paths
4. confirm that the user actually wants the side effect, not just a read or a preview

## Workflow-specific gates

| Workflow family | Additional checks that must be explicit |
| --- | --- |
| analysis create | trigger type, `applyOnSelf`, output attribute scope, runtime target (`Ready` vs `Running`) |
| panel build | chart intent, SQL generation expectation, dashboard placement, refresh owner, advanced-query fallback need |
| alert create / debug | failure boundary (`no event` vs `no delivery`), event template, notify-rule scope, resend or ack permission |
| datasource diagnose | trusted credential source, connection scope, `dbName`, `stableName`, and metadata probe boundary |
| data import / export | package vs CSV chain, artifact expectation, multipart field shape, post-write record reread |
| user / role / permission | subject type (`userId`, `roleId`, `userGroupId`), permission boundary, safe preview strategy |

## Copyable preflight summary

Use a compact summary like this before switching from reads to writes:

```text
Preflight summary:
- Mode: <element|template>
- Owner: <elementId|elementTemplateId>
- Root / parent scope: <rootElementId or parent scope>
- Payload family: <plain DTO|advanced DTO|multipart|wrapper>
- Name seed or target IDs: <resolved values>
- Verification target: <get/list/query/sqls/event/history/rule reread>
- Risk gate: <dry-run first / direct write approved>
```

## Stop conditions

Do not write yet when any of these is still unknown:

- owner or business root
- self vs child scope
- output attribute or target template IDs
- datasource connection, database, or table scope
- notification rule scope
- verification target

The right next step in that case is another read, not a guessed write.
