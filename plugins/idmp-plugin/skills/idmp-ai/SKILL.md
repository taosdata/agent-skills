---
name: idmp-ai
description: "IDMP AI skill. Use it to confirm AI availability and usable data, inspect chat sessions, generate recommended questions or panels, create analyses or panels from prompts, and decide when `record` should persist the session."
metadata:
  author: "TaosData"
  version: "0.4.0"
  owner_team: "AI"
  requires:
    bins:
      - idmp-cli
  cliHelp: "idmp-cli ai --help"
---

# ai

**Read [`../idmp-shared/SKILL.md`](../idmp-shared/SKILL.md) first.**

## What this skill covers

- Prove AI availability, AI-visible data, chat-session visibility, and generation boundaries before claiming success.
- Keep generation grounded in a real element scope and hand off to non-AI workflows when the backend is empty or unavailable.

## Recommended reference

- [`references/ai-read-flows.md`](references/ai-read-flows.md)

## Missing context to resolve first

- AI backend availability.
- Record policy.
- Whether the operator wants availability only, recommendations, a draft object, or a recorded chat.
- The target element scope for recommend or create requests.
- Whether `record:true` is acceptable.

## Constrained live behaviors

- Treat `datasource available list=false` as a hard stop.
- `idmp-cli datasource available list` is the hard availability gate.
- `recommend` can return an empty array.
- `idmp-cli ai anydata list` measures AI-visible data, not chat history.
- `idmp-cli ai chat sessions` is the safest proof that recorded chat is visible.
- `ai recommend create` and `ai recommend create-post` still need `questionType` values from the backend `QuestionType` enum. Use `GENERAL_QUESTION`, `GEN_PANEL_QUESTION`, or `GEN_ANALYSIS_QUESTION`; do not send intuitive aliases such as `PANEL` or `ANALYSIS`.
- Keep the endpoint path in the evidence: `ai recommend create` calls `/api/v1/ai/panels/recommend`, while `ai recommend create-post` calls `/api/v1/ai/prompts/recommend`.
- Recommendation endpoints can return `[]`; classify that as empty output instead of inventing advice.
- If the backend returns a structured error, surface that error verbatim.
- If recommend fails with `Can't parse the value: PANEL to AiGenPromptType`, classify it as a backend contract mismatch instead of datasource or auth unavailability.
- If recorded chat creation complains about an invalid session, retry with `sessionId:null`.
- AI analysis draft creation can time out even when `datasource available list` and `ai anydata list` are healthy; classify `context deadline exceeded` as backend AI/API latency and hand off to structured analysis workflows instead of mutating the request semantics blindly.

## Execution flow

1. Start with `idmp-cli datasource available list` and stop immediately if availability is false.
2. Use `idmp-cli ai anydata list` to prove the AI backend can see usable data instead of assuming data visibility from availability alone.
3. Read `idmp-cli ai chat sessions` before any recorded chat or follow-up AI write so the session state is grounded in a real reread.
4. Use `idmp-cli ai recommend create-post --ack-risk --data` with the final `questionType` locked to `GENERAL_QUESTION`, `GEN_PANEL_QUESTION`, or `GEN_ANALYSIS_QUESTION`, then classify the result as populated, empty, structured failure, or backend contract mismatch.
5. Use `idmp-cli ai create create --ack-risk --data` or `idmp-cli ai create create-post --ack-risk --data` only when a draft object is requested, then prove the response actually contains a generated object before claiming success. If analysis draft creation times out, stop and hand off to the structured analysis workflow instead of claiming AI unavailability.

## Evidence of completion

- Availability is only complete when `datasource available list` and `ai anydata list` agree on the backend state.
- Recommendation work is only complete when the returned array, empty result, or structured error is preserved exactly; do not fabricate advice.
- AI create work is only complete when the response proves a real generated draft or clearly classifies the failure boundary.

## Key commands

1. `idmp-cli datasource available list` to prove the backend is reachable.
2. `idmp-cli ai anydata list` to prove the AI service can see usable data.
3. `idmp-cli ai chat sessions` to inspect visible chat history before new writes.
4. `idmp-cli ai recommend create-post --ack-risk --data '{"elementId":123,"questionType":"GENERAL_QUESTION","async":true}'` for generic prompt suggestions.
5. `idmp-cli ai recommend create-post --ack-risk --data '{"elementId":123,"questionType":"GEN_PANEL_QUESTION","async":true}'` or `...GEN_ANALYSIS_QUESTION...` for panel or analysis-oriented recommendations.
6. `idmp-cli ai create create --ack-risk --data '{"elementId":123,"prompt":"Create a 1-minute average-current analysis","record":true,"deepThinking":false,"deviceDocument":false}'` for analysis drafts.
7. `idmp-cli ai create create-post --ack-risk --data '{"elementId":123,"prompt":"Create a maximum-current trend panel","record":true,"deepThinking":false,"deviceDocument":false}'` for panel drafts.

## Exception paths

- Stop if availability is false; hand off to datasource or asset bootstrap workflows instead of forcing AI generation.
- Keep empty recommendation results separate from backend failures.
- Do not claim a panel or analysis exists unless the response payload proves it and the draft is visible through a follow-up read.
- If create fails, stop and report the backend-unavailable state.

## Validation scenarios

### 1. Availability gate
Run `idmp-cli datasource available list` and `idmp-cli ai anydata list` first. Success here only means the environment can support later AI work.

### 2. Data readiness
Use `idmp-cli ai anydata list` after availability passes. If the list is empty, treat that as weak AI context rather than a fabricated success.

### 3. Session visibility
Read `idmp-cli ai chat sessions` before recorded chat creation. Only use session detail reads if the list result gives you a trusted session ID.

### 4. Recommendation path after availability passes
Use `idmp-cli ai recommend create-post --ack-risk --data` with a locked element scope and an explicit backend enum such as `GENERAL_QUESTION`, `GEN_PANEL_QUESTION`, or `GEN_ANALYSIS_QUESTION`. Empty arrays, structured backend errors, and enum-contract errors are all valid, different outcomes.

### 5. Explicit unavailable-backend failure branch
If `idmp-cli ai create create --ack-risk --data` or `idmp-cli ai create create-post --ack-risk --data` fails, classify the failure and stop. Distinguish backend timeouts from true availability failures, and never report a generated object unless the response proves it.
