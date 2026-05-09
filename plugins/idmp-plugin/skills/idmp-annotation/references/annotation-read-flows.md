# annotation read flow

Common pattern:

```bash
idmp-cli annotation +list <element-id> --size 20
idmp-cli annotation +list <element-id> --content warning --size 20
```

When the generated command path is needed:

```bash
idmp-cli schema annotation.annotation.list
idmp-cli annotation annotation create --ack-risk --data '{...}'
idmp-cli annotation annotation update --ack-risk --data '{...}'
idmp-cli annotation annotation delete --ack-risk --params '{"annotationId":123}'
```

Notes:

- This domain is for **element annotations**.
- Event annotations should use `idmp-cli event annotations list/create/update/delete`.
