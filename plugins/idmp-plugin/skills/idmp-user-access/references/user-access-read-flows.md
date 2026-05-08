# user-access read flow

Use this reference to separate visibility, permission-boundary, and role-design problems before any grant or revoke write.

## Read-first sequence

1. Resolve the user inventory:

   ```bash
   idmp-cli user users list
   idmp-cli user page list --params '{"current":1,"size":20}'
   idmp-cli user users get --params '{"userId":123}'
   ```

2. Resolve role inventory and permission groups:

   ```bash
   idmp-cli role roles list --params '{"current":1,"size":20}'
   idmp-cli role roles get --params '{"roleId":330001}'
   idmp-cli permission groups list
   idmp-cli permission groups merge --params '{"roleIds":[330001,330002]}'
   ```

3. Resolve what can actually be assigned:

   ```bash
   idmp-cli permission users assignable --params '{"userId":123}'
   idmp-cli permission roles list-get --params '{"userId":123}'
   ```

4. For group-scoped permission chains:

   ```bash
   idmp-cli permission usergroups assignable --params '{"usergroupId":456}'
   idmp-cli permission roles list --params '{"usergroupId":456}'
   ```

## Boundary decisions

- if the target user is visible but `assignable` is 403, report a permission boundary instead of inventing a role fix
- if the role exists but the merged permission groups are wrong, this is a role-design problem
- if the role is correct and assignable, only then move to grant or revoke flows

## Safe write handoff

```bash
idmp-cli permission policy grant-post --dry-run --ack-risk --params '{"userId":123}' --data '{...}'
idmp-cli role roles create --dry-run --ack-risk --data '{"name":"demo-role","description":"temporary role","permissionGroupIds":[210021]}'
idmp-cli role roles delete --dry-run --ack-risk --params '{"roleId":123}'
```

After a real write, reread:

```bash
idmp-cli permission roles list-get --params '{"userId":123}'
idmp-cli role roles get --params '{"roleId":123}'
```

## One-shot rules

1. `user users list` and `user page list` are different views; do not substitute one for the other.
2. `role roles create` requires non-empty `permissionGroupIds`.
3. Always prove assignability before grant or revoke.
