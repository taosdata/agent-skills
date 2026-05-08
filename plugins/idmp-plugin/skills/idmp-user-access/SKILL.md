---
name: idmp-user-access
description: "IDMP user-access skill. Use it to inspect users, roles, permission groups, assignable roles, and granted roles while keeping current-user reads separate from admin paginated user lists."
metadata:
  author: "TaosData"
  version: "0.4.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli user --help"
---

# user / role / permission

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

## What this skill covers

- Read current-user context, paginated admin user views, roles, permission groups, and safe authorization previews.
- Keep current-user inspection separate from directory-wide admin surfaces.

## Recommended reference

- [`references/user-access-read-flows.md`](references/user-access-read-flows.md)

## Missing context to resolve first

- Admin visibility.
- Permission group seed.
- Whether the request is about the current user, a directory user, a role, or a permission scope.
- Whether the operator only needs a dry-run preview or a real mutation.
- Which scope, group, or role ID is already known.

## Constrained live behaviors

- `user users list` returns the current-user object.
- `permission users assignable` and `permission roles list-get` can return structured 403.
- `role roles create` requires a non-empty `permissionGroupIds` list.
- `user users list` is the current-user surface; `user page list` is the paginated directory view.
- Role and permission reads can succeed even when grant previews are permission-bound.
- Keep `--dry-run --ack-risk` on grant previews until the operator explicitly wants a real mutation.

## Execution flow

1. Start with `idmp-cli user users list` to separate current-user context from directory-wide admin views.
2. Use `idmp-cli user page list --params` only when the task really needs admin directory scope.
3. Pair role detail with `idmp-cli permission groups list` before any grant preview or temporary role create.
4. Keep authorization work on `permission policy grant-post --dry-run --ack-risk --params` until the operator explicitly wants a real mutation.
5. If a temporary role must be created, reread it and pair the create with a delete cleanup step in the same workflow.

## Evidence of completion

- A current-user answer is only complete when it comes from `user users list`, not from a guessed admin directory row.
- A permission boundary is still valid evidence when the backend returns a structured 403 for assignable or granted-role reads.
- A temporary-role workflow is only complete when both the reread and the delete cleanup succeed.

## Key commands

1. `idmp-cli user users list` for the current-user shape.
2. `idmp-cli user page list --params` for the admin directory view.
3. `idmp-cli user users get --params` to inspect a specific user.
4. `idmp-cli role roles get --params` to inspect one role deeply.
5. `idmp-cli permission groups list` to enumerate reusable permission bundles.
6. `idmp-cli permission policy grant-post --dry-run --ack-risk --params` to preview authorization safely.
7. `idmp-cli role roles create --ack-risk --data` when a temporary custom role is really needed.
8. `idmp-cli role roles delete --ack-risk --params` to remove that temporary role after verification.

## Exception paths

- If paginated admin reads are forbidden, do not infer that the current-user surface is also broken.
- Stop at dry-run when the operator has not explicitly requested a real grant.
- Clean up any temporary custom role you create.

## Validation scenarios

### 1. Current-user shape
Use `idmp-cli user users list` first. This should answer “who am I” questions without requiring admin directory access.

### 2. Admin directory view
Use `idmp-cli user page list --params` for scoped directory inspection. Treat permission failures here as directory-boundary evidence, not a total auth failure.

### 3. Role and permission-group context
Pair `idmp-cli role roles get --params` with `idmp-cli permission groups list`. The answer should explain both role detail and reusable permission groups.

### 4. Safe grant preview
Use `idmp-cli permission policy grant-post --dry-run --ack-risk --params` before any real grant. A dry-run failure is still useful boundary evidence.

### 5. Temporary custom-role lifecycle
If you must mutate, pair `idmp-cli role roles create --ack-risk --data` with `idmp-cli role roles delete --ack-risk --params`. Build a temporary custom role with one real permission group, reread it, then delete it.
