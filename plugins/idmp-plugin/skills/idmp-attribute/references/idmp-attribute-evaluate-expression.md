# attribute evaluate-expression

Use this reference when a formula or string-builder preview must succeed on the first attempt.

## Canonical command family

The live command is:

```bash
idmp-cli schema attribute.evaluate-expression.create
idmp-cli attribute evaluate-expression create --params '{"elementId":123}' --data '{...}' --dry-run --ack-risk
```

Do not guess an older path such as `attribute.attributes.evaluate-expression`; the real schema key is `attribute.evaluate-expression.create`.

## Minimal live-safe formula starter

The backend requires `dataReferenceType` and `expression`. This is the smallest safe preview body:

```json
{
  "dataReferenceType": "Formula",
  "expression": "AVG(${attributes['Current']})"
}
```

Use the schema-aligned command with that body before any create or update that depends on the formula result.

## Attribute-aware starter

If the preview must stay aligned with one existing attribute or UOM, add the optional context fields:

```json
{
  "attributeId": 456,
  "dataReferenceType": "Formula",
  "expression": "(${attributes['Current']} + ${attributes['Voltage']}) / 2",
  "uomId": 789
}
```

Use this only after `attribute elements attributes --params` confirmed the real IDs.

## One-shot rules

1. Keep `dataReferenceType` explicit. `Formula` is the safest default for arithmetic previews.
2. Treat `attributeId` and `uomId` as optional context, not as replacements for `expression`.
3. Start with `--dry-run --ack-risk`, then use the same body for the real preview if needed.
4. If evaluation fails, fix the expression first; do not create or update the attribute before the preview succeeds.
