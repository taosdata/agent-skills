---
name: idmp-annotation
description: "IDMP annotation skill. Use it to read and write element annotations while keeping element annotations separate from event annotations."
metadata:
  author: "TaosData"
  version: "0.4.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli annotation --help"
---

# annotation

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

## What this skill covers

- Read, create, update, and delete annotations attached to elements.
- Keep element annotations separate from event annotations, which use the `event annotations *` family.
- Use annotation IDs for follow-up changes after the initial list read.
- Use filtered rereads by `content` or time window to prove the exact note you just changed.

## Recommended shortcuts

| Shortcut | Purpose |
|----------|---------|
| `+list` | List annotations for one element, optionally filtered by content |

## Recommended reference

- [`Annotation read flows`](references/annotation-read-flows.md)

## Missing context to resolve first

| Context | Why it must be resolved before mutation |
| --- | --- |
| Annotation scope | Decide whether the note belongs to an element or an event before choosing the command family. |
| Owner element | Element annotation create needs the final `elementId`. |
| Target annotation ID | Update and delete need `annotationId`, not the element ID. |
| Verification plan | Decide how you will reread the annotation list after create, update, and delete. |

## Constrained live behaviors

- `annotation annotation create` writes element annotations only; event notes use the `event annotations *` family.
- `annotation annotation update` and `annotation annotation delete` act on `annotationId`, not on the owner element.
- Annotation writes are not complete until `annotation annotation list` reread shows the expected text or confirms deletion.
- `annotation annotation list` supports `content`, time windows, and small page sizes, so use filtered rereads before widening to the full page.
- `annotation annotation list` time-window filters expect epoch milliseconds, even though `annotation annotation update` can return a timestamp string. Convert the returned time before you feed it back into `updateTimeFrom` or `updateTimeTo`.
- Disposable debug notes should be deleted when the workflow ends so shared environments do not accumulate stale annotations.

## Operator workflow

1. Use this skill for element annotations only.
2. If the operator is discussing an event timeline, switch to `event annotations *`.
3. Read the element annotation list first and capture the `annotationId` before any update or delete.
4. `update` and `delete` operate on the annotation record, not on the element itself.
5. Re-read with a `content` filter first, then widen to the unfiltered first page if needed, to confirm the final text and timestamps.
6. When you need an `updateTime*` filter after `update`, normalize the returned timestamp to epoch milliseconds before the reread.

## Key commands

```bash
idmp-cli schema annotation.annotation.list
idmp-cli annotation annotation list --params '{"elementId":123,"current":1,"size":20}'
idmp-cli annotation annotation list --params '{"elementId":123,"content":"copilot note","current":1,"size":1}'

idmp-cli schema annotation.annotation.create
idmp-cli annotation annotation create --ack-risk --data '{...}'

idmp-cli schema annotation.annotation.update
idmp-cli annotation annotation update --ack-risk --data '{...}'

idmp-cli schema annotation.annotation.delete
idmp-cli annotation annotation delete --ack-risk --params '{"annotationId":456}'
```

## Exception paths

- The list is empty: treat that as “no annotations yet,” not as a product failure.
- Reads return 404 or permission errors: verify the `elementId` and the current user’s access level.
- Update or delete fails unexpectedly: confirm you passed `annotationId`, not `elementId`.
- The operator expected event notes: switch to `event annotations *` instead of forcing element commands.
- A write succeeds but the note still seems missing: remove filters and re-read the first page of results.
- Update succeeds but `updateTimeFrom` filtering misses the note: convert the returned update time to epoch milliseconds and retry the filtered list.

## Validation scenarios

1. List annotations for a known element with `idmp-cli annotation annotation list`.
2. Repeat the list with a content filter and small page size to isolate one known note.
3. Create a disposable annotation with `idmp-cli annotation annotation create --ack-risk`.
4. Update that annotation by `annotationId` with `idmp-cli annotation annotation update --ack-risk`.
5. Delete the same annotation by `annotationId` and confirm it no longer appears in the list.
