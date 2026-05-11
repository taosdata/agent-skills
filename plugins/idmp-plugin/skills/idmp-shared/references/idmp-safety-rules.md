# Safety and Risk Rules

## Destructive Operation Confirmation Protocol

> **Hard requirement for AI agents**: before any **write / delete / update** operation against the IDMP server or local CLI configuration, first print the four items below and stop for an explicit `yes` / `no` answer. Until the user confirms, do **not** call `DELETE`, non-readonly `POST`, `PUT`, `PATCH`, any command with `--ack-risk`, or local destructive commands such as `config remove` and `profile remove`.

### The four required items

1. **Target**: the object `type`, `id`, `name`, and the relevant scope such as `elementId`, `elementTemplateId`, or `profileName`.
   - Example: `Delete target: attribute id=42, name="vibration_test", owner elementId=100`
2. **Action**: the HTTP method and path, the `schemaPath`, or the local command name, plus the full parameter summary with sensitive fields masked.
   - Example: `Action: DELETE /api/v1/elements/100/attributes/42 (attribute.attributes.delete)`
3. **Reason**: why the action is needed, tied back to the user's request. If this is a compensating cleanup step, say so explicitly.
   - Example: `Reason: the user asked to remove temporary test attributes created during debugging so the production element stays clean`
4. **Blast radius**: dependent analyses, panels, dashboards, event rules, or notifications; rollbackability; child-object side effects; and whether the change affects other users or sessions.
   - Example: `Impact: deleting this attribute will invalidate 3 analyses that reference it; the action is not reversible; no cross-profile impact`

### Copyable output template

```
WARNING: destructive operation pending. Please confirm:
- Target: <type> id=<id>, name="<name>" (<other context>)
- Action: <METHOD> <path> (<schemaPath>) payload=<summary>
- Reason: <why>
- Impact: <downstream effects / rollbackability / dependent objects>
Continue? (yes/no)
```

### When this protocol applies

| Scenario | Confirmation required |
| --- | --- |
| `GET` / `HEAD` / readonly suffixes such as `search`, `query`, `list` | No |
| Any `DELETE` path | **Yes (`dangerous`)** |
| Non-readonly `POST` / `PUT` | **Yes (`write`)** |
| `PATCH` | **Yes (`write`)** |
| `config remove` / `profile remove` / `auth logout --clear` | **Yes (`local dangerous`)** |
| Any non-`GET` `idmp-cli api` request | **Yes** |
| `--dry-run` only | No, but still summarize the preview result |

### When confirmation can be skipped

- The user explicitly granted batch permission in the current session or gave a concrete list and said to delete those exact items. Even then, restating the target list is still recommended.
- The command is `--dry-run` only or purely readonly.

### Batch operations

When doing the same action on N objects, you must:

- list all N targets and reasons;
- explain whether execution is item-by-item, stop-on-error, or continue-on-error;
- stop immediately and ask again if any step fails.

## Additional rules

- Prefer `--password-stdin` for passwords.
- Never store tokens, passwords, or secrets in scripts, logs, or docs.
- Inject live-environment credentials only through environment variables.
- Non-readonly generated commands and raw API calls normally require `--ack-risk`.
- Run `--dry-run` before a real write whenever possible.
- Do not guess `elementId`, `elementTemplateId`, or `rootElementId`; use `search`, `path`, or `get` first.
- Prefer `new-name` before creating attributes or analyses.
- Before hierarchy aggregation, child-template output, or trigger enumeration, read `sub-templates` and `trigger-types`.
- After creating analyses, panels, or rules, always reread with `get` or `list`; if the status is not running, follow up with `resume`.
- If a workflow created a temporary attribute but the main object failed to persist, delete the temporary attribute explicitly and run the same confirmation protocol.
- `IDMP_CLI_SESSION_STORAGE=auto` uses keychain or keyring only when a secure-store session is already available. In Linux, CI, or headless environments without a D-Bus session bus, it should stay on file storage and must not rely on auto-launching `dbus-launch`.
- If file storage is used, keep the config directory private. If strict keyring behavior is required, set `IDMP_CLI_SESSION_STORAGE=keyring` explicitly and verify that Secret Service or keyring is ready.
- **The CLI does not guarantee safe multi-process writes to `~/.idmp-cli/`.** Do not run `config set`, `auth login`, or `profile ...` concurrently. Network file systems such as NFS, SMB, or sshfs are even riskier.

## Risk classification (`x-risk`)

The CLI no longer infers risk from string matching. It reads the generator-injected OpenAPI `x-risk` extension instead:

- `readonly`: `GET`, `HEAD`, `OPTIONS`, plus generated `POST` and `PUT` endpoints whose OpenAPI `x-risk` is `readonly`. Query-like suffixes such as `search`, `query`, `list`, `export`, `preview`, `exists`, `tree`, `path`, `children`, `parents`, `history`, `versions`, `changes`, `full-path`, `path-items`, `single-path`, `samples`, `forecast`, and `preview-result` often land here. **Use `idmp-cli schema <path>` as the final source of truth for `--ack-risk`.**
- `write`: normal `POST`, `PUT`, and `PATCH`. Interactive environments prompt; CI and automation require `--ack-risk`.
- `dangerous`: `DELETE`, backup or restore, batch delete, sync-meta, and similar endpoints matched by path prefix, such as `/api/v1/backup`, `/api/v1/system/backup`, `/api/v1/sync-meta`, `/api/v1/system/import`, `/api/v1/users/delete`, `/api/v1/batch/delete`, and `/api/v1/notifications/templates/import`.

Common gotchas:

- `POST /*/search`, `/*/query`, and `/*/forecast` used to be misclassified as writes. When the current schema reports them as `readonly` (for example `panel.panels.query`), old scripts can remove `--ack-risk` there.
- Do not assume every `*/validate` endpoint is readonly by name alone. The generated schema currently marks `panel.verify.create` and `panel.verify.create-post` as `write`, so they still require `--ack-risk`.
- Local destructive commands such as `idmp-cli config remove` and `idmp-cli profile remove` now use the unified wording `Confirm local remove on profile <name> (risk=dangerous)`, and CI must still pass `--ack-risk`.
- `PATCH` is no longer automatically `dangerous` unless the path is in the dangerous list.

## Response size and token lifetime

- `--max-response-size` supports suffixes such as `16m`, `1g`, and `1024k`, defaults to 64 MB, and blocks oversized download responses.
- Login and token-refresh expiry is no longer hardcoded to 7 days. The CLI parses JWT `exp` when possible. For non-JWT tokens, `ExpiresAt` stays empty and `auth check --remote` is the authoritative check.

## Paging

- `--page-all` auto-detects row keys in this order: `rows -> records -> items -> data -> list`. It uses the first array field found, so callers do not need to declare it explicitly.
- If no row key is found, the error explains which fields were returned. `current`, `size`, and `total` also support spec-defined custom keys.

## Live-environment checklist

Use only the following environment variables for credentials. Never hardcode them in code, docs, or fixtures:

```bash
export IDMP_E2E_ENABLED=1
export IDMP_BASE_URL=http://<host>:6042
export IDMP_E2E_USERNAME=<user>
export IDMP_E2E_PASSWORD=<pass>
```

When these skills are maintained inside the `idmp-cli` source repository, the recommended validation order is `make vet lint unit-test skills-test cli-e2e-test race-test coverage-test`.

## Concurrency

- Session and config writes use `validate.AtomicWrite` (temp file + atomic rename on the same filesystem), not `flock`-style lock files.
- `APIClient` token refresh uses a mutex, and `PersistToken` runs outside the lock to avoid re-entrancy.
- Atomic writes prevent partial-file corruption, but the higher-level Load -> mutate -> Save helpers are not serialized across concurrent writers; do not describe them as cross-process concurrency-safe.
- If a custom tool writes session files in a loop, call `core.SaveProfileSession` directly instead of implementing your own Load -> mutate -> Save sequence, and serialize concurrent writers at the caller when race-free updates matter.
