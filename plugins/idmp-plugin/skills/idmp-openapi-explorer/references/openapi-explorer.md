# openapi explorer

When a domain or workflow skill is not enough, troubleshoot in this order:

1. Find the closest frontend-mapped skill.
2. Use `idmp-cli schema <schemaPath>` to confirm the real method, path, and parameters.
3. Prefer rewriting the action as a generated command.
4. Fall back to `idmp-cli api` only when the generated command is still insufficient.

Common pattern:

```bash
idmp-cli schema analysis.analyses.create
idmp-cli analysis analyses create --params '{"elementId":123}' --data '{...}'
idmp-cli api POST /api/v1/elements/123/analyses --data '{...}'
```

At minimum, explain:

- the `schemaPath`
- the HTTP method and path
- where path, query, and body parameters come from
- whether the call is mutating and whether it needs `--ack-risk`

## `x-risk` extensions

Since v1.0.16, the spec includes three pre-injected extension fields and `idmp-cli schema <path>` echoes them:

- `x-risk`: `readonly` / `write` / `dangerous`
- `x-mutating`: whether the call changes server state
- `x-confirmation-required`: whether the CLI prompts in TTY mode

Rules summary:

- `GET` / `HEAD` / `OPTIONS` -> `readonly`
- `DELETE` -> `dangerous`
- `POST` / `PUT` whose final segment is one of `{search, query, list, export, preview, exists, tree, path, children, parents, history, versions, changes, full-path, path-items, single-path, samples, forecast, validate, preview-result}` -> `readonly`
- all other `POST` / `PUT` / `PATCH` -> `write`
- path prefixes such as `/api/v1/backup`, `/api/v1/system/backup`, `/api/v1/sync-meta`, `/api/v1/system/import`, `/api/v1/users/delete`, `/api/v1/batch/delete`, and `/api/v1/notifications/templates/import` -> `dangerous`

That is why `POST /*/search`, `POST /*/query`, and `POST /*/forecast` are readonly and do not need `--ack-risk`.
