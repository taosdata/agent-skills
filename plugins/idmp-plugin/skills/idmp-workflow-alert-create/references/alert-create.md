# alert create flow

Use this reference after the main workflow doc. It distills the payload shapes that already succeed in the repo's live alert variants.

## AI-first alert-analysis draft path

When the operator starts from natural language, prefer drafting the Event-trigger analysis through:

1. `idmp-cli ai create create --ack-risk --data '{"elementId":123,"prompt":"Create an Event-trigger alert analysis when current crosses the threshold","record":true,"deepThinking":false,"deviceDocument":false}'`
2. `idmp-cli analysis analyses create --ack-risk --params '{"elementId":123}' --data '{...}'`

Treat this as the preferred path only for the **analysis portion** of the alert workflow. Optional notify-rule configuration happens only after the analysis reaches `Running`. Do not trigger a real event just to prove creation.

Fallback rules:

- remove the draft `id` before persistence
- inject `rootElementId` on the persisted payload
- if the draft omits or corrupts the required Event-trigger fields, event template binding, or severity semantics, discard it and switch to the proven structured payload below
- if persistence fails, clean any draft-created output attributes before retrying

## Core create chain and optional routing chain

| Write chain | Command family | Payload family | Hard rule |
| --- | --- | --- | --- |
| Event-trigger analysis | `analysis analyses create` | analysis DTO | This is the real alert create path and the success boundary for this skill. |
| optional notify rule | `notification notify-rules create/update` | notify-rule DTO | Configure this only when downstream routing is explicitly in scope after Running proof. |

## Creation success rule

1. `analysis analyses create` persists the Event-trigger analysis.
2. `analysis analyses get` rereads the same analysis under the same owner.
3. `analysis analyses resume` leaves the analysis in `Running`.

A real event, `event events list`, `notification try-send create`, or downstream delivery is **not required** for create success.

## Proven Event-trigger analysis payload

Replace only the obvious placeholders (`name`, `rootElementId`, event template ID, source attribute, output attr IDs).

```json
{
  "name": "demo-alert",
  "rootElementId": 1,
  "startAfterCreated": true,
  "recalculate": false,
  "trigger": {
    "type": "Event",
    "preFilter": true,
    "preFilterExpression": "",
    "fillHistory": false,
    "fillHistoryFirst": false,
    "eventTrigger": {
      "starts": [
        {
          "name": "start",
          "expression": "${attributes['Current']} > 0",
          "duration": "1s",
          "parameters": [],
          "severity": "Information",
          "allowAck": false
        }
      ],
      "end": {
        "name": "end",
        "expression": "${attributes['Current']} <= 0",
        "duration": "1s",
        "parameters": [],
        "severity": "Information",
        "allowAck": false
      },
      "duration": "1s"
    }
  },
  "output": {
    "applyOnSelf": true,
    "elementTemplate": {
      "id": null,
      "filter": "",
      "rootElement": 0,
      "level": 0
    },
    "rollupWindow": {
      "enabled": true,
      "interval": "1m",
      "startTime": "_wstart",
      "startTimeOffset": "0s",
      "endTime": "_wend",
      "endTimeOffset": "0s"
    },
    "columnName": "_wend",
    "offset": "0s",
    "attributes": [
      {
        "attrId": 456,
        "attrName": "analysis-output",
        "expression": "AVG(${attributes['Current']})",
        "parameters": [],
        "eventAttrId": null,
        "eventAttrName": ""
      }
    ]
  },
  "event": {
    "templateId": 789,
    "allowAck": false,
    "severityLevel": "Information",
    "reasonEnumTypeId": null,
    "reasonEnumValueId": null,
    "eventMinInterval": "1m"
  }
}
```

## Optional notify-rule payload

If the environment already has a shared working rule, reread and update that rule instead of creating a duplicate. Preserve the returned `id` and working `eventRules` coverage.

```json
{
  "id": 321,
  "name": "demo-notify-rule",
  "description": "copilot reusable alert notify rule fixture",
  "content": "copilot reusable alert notify rule fixture",
  "contactId": 123,
  "escalationContactId": 123,
  "resendInterval": "30s",
  "escalationInterval": "1m",
  "maxResendCount": 1,
  "eventRules": [
    {
      "eventTemplateId": 789,
      "eventTemplateName": "demo-event",
      "severityLevel": "Default"
    }
  ]
}
```

Why `Default` can be correct:

- shared reusable rules often need broader coverage than the single alert severity
- if the environment already returns a working `eventRules` entry, preserve it instead of forcing a narrower severity

## Out of scope for create success

Do not use these as the success marker for this skill:

- `analysis attribute list`
- `attribute write-data create`
- `analysis analyses fill-history`
- `event events list`
- `event events confirm`
- `notification try-send create`

Those belong to later debugging or downstream delivery validation only.

## Scope guardrails

1. If `applyOnSelf=false` and `analysis trigger-types list` omits `Event`, stop. Do not force the create.
2. If a non-leaf self owner advertises `Event`, create can still succeed as soon as the analysis is created, reread, and `Running`; do not force replay.
3. Use analysis rereads plus `resume` as the primary proof path for this skill.
