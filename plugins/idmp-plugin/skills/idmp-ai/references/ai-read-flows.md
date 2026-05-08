# AI read flow

Use this reference to decide whether the environment can support AI-assisted generation before invoking recommend or create endpoints.

## Availability-first sequence

1. Confirm data availability:

   ```bash
   idmp-cli datasource available list
   idmp-cli ai anydata list
   ```

2. Confirm session visibility:

   ```bash
   idmp-cli ai chat sessions
   ```

   Treat `ai chat sessions` as the primary proof that recorded chat is visible. `ai chat sessions-get --params '{"sessionId":123}'` is optional and can return a permission-bound `403` even when the session list is readable.

3. Only then choose the generation path:

    ```bash
    idmp-cli ai ai chat --ack-risk --data '{"deepThinking":false,"deviceDocument":false,"messageId":null,"prompt":"How many elements are in the system?","record":true,"sessionId":null}'
    idmp-cli ai recommend create-post --ack-risk --data '{"elementId":123,"questionType":"GENERAL_QUESTION","async":true}'
    idmp-cli ai recommend create-post --ack-risk --data '{"elementId":123,"questionType":"GEN_PANEL_QUESTION","async":true}'
    idmp-cli ai recommend create-post --ack-risk --data '{"elementId":123,"questionType":"GEN_ANALYSIS_QUESTION","async":true}'
    idmp-cli ai create create --ack-risk --data '{"elementId":123,"prompt":"Create a 1-minute average-current analysis","record":true,"deepThinking":false,"deviceDocument":false}'
    idmp-cli ai create create-post --ack-risk --data '{"elementId":123,"prompt":"Create a maximum-current trend panel","record":true,"deepThinking":false,"deviceDocument":false}'
    ```

## Branching rules

- if `datasource available list` returns false, stop and hand off to `../idmp-workflow-asset-bootstrap/SKILL.md`
- if `ai anydata list` is false, the AI backend may still exist, but design generation will likely be low quality
- if recommendations return `[]` while availability probes are still true, classify that as an empty recommendation result instead of fabricating generated prompts or declaring an outage
- if sessions are visible but new recommendations fail with a structured error, this is AI-service availability, not data availability
- if recommend fails with `Can't parse the value: PANEL to AiGenPromptType`, switch the request to `GEN_PANEL_QUESTION` or `GEN_ANALYSIS_QUESTION` and classify the original failure as a backend contract mismatch
- if chat creation fails with `Invalid session ID`, retry with `sessionId:null` instead of `0`
- if `ai create create` returns `context deadline exceeded`, keep the original prompt and classify the first attempt as backend AI/API latency instead of mutating the intent into a different workflow

## Generation-path guidance

- use `recommend` when the operator wants suggested questions or panels
- use `create` when the operator already has a prompt and wants a draft output directly
- keep recommendation `questionType` aligned with the backend enum: `GENERAL_QUESTION`, `GEN_PANEL_QUESTION`, or `GEN_ANALYSIS_QUESTION`
- use `ai ai chat` with `record:true` and `sessionId:null` when the operator wants a visible recorded chat session
- use `record:true` only when the operator wants the result stored in chat history

## Request starters that match the current contracts

### Generic question recommendations

```json
{
  "elementId": 123,
  "questionType": "GENERAL_QUESTION",
  "async": true
}
```

### Panel or analysis-oriented recommendations

```json
{
  "elementId": 123,
  "questionType": "GEN_PANEL_QUESTION",
  "async": true
}
```

```json
{
  "elementId": 123,
  "questionType": "GEN_ANALYSIS_QUESTION",
  "async": true
}
```

### Analysis draft create

```json
{
  "elementId": 123,
  "prompt": "Create a 1-minute average-current analysis",
  "record": true,
  "deepThinking": false,
  "deviceDocument": false
}
```

### Panel draft create

```json
{
  "elementId": 123,
  "prompt": "Create a maximum-current trend panel",
  "record": true,
  "deepThinking": false,
  "deviceDocument": false
}
```

## Long-response tools

For streaming or interruption control:

```bash
idmp-cli ai stream create --ack-risk --data '{"deepThinking":false,"deviceDocument":false,"messageId":null,"prompt":"How many elements are in the system?","record":true,"sessionId":null}'
idmp-cli ai stop list --params '{"messageId":123,"sessionId":456}'
```
