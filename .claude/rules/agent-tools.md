<!-- Provenance: copied from Gauntlet AI/.claude/rules/agent-tools.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
---
paths:
  - "**/*.py"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
---

# Agent Tools

Applies when defining, registering or dispatching tools that a language model can request. Skip for code that doesn't.

Source: `principles/tool-design.md` and GP-32 in `architecture-and-tradeoffs.md`, Gauntlet AI repo.

## Rules

1. **One tool, one job [GP-8].** A tool that branches on a "mode" or "what" argument gets split. Reads are idempotent; any write takes an idempotency key.
2. **Descriptions are routing [GP-9].** Every tool description says what it returns, when to use it, and when *not* to (naming the sibling tool to use instead). Write it for a junior engineer with no other context. A one-word description is a defect.
3. **Schemas are the source of truth [GP-10].** Inputs and outputs are Pydantic / Zod models; the JSON schema sent to the model is generated from them, never hand-maintained alongside.
4. **The model advises; code executes [GP-11].** Between the model's request and execution, validate in code: arguments against the schema, identifiers (e.g. `patient_id`) against the session's pinned scope, and the caller's role against the tool's allowed roles. A failed check returns a structured refusal to the model and is logged — it never executes.
5. **Structured errors [GP-8].** Tools return typed errors (`code`, `message`, `retryable`) instead of raising raw exceptions into the model context. Never put stack traces, secrets or PHI in an error message.
6. **Handle every branch [GP-12].** The dispatch loop handles: no tool call (final answer), multiple and parallel tool calls, unknown tool names, malformed or unparseable arguments, and tool exceptions. Every result is returned with its `tool_call_id`.
7. **No destructive or raw access [GP-32].** No generic SQL, shell or file-write tool. Queries are parameterized. Credentials are read from the environment inside the tool, never passed as arguments or placed in prompts.

## Review checklist

- [ ] Would a model pick the right tool from the descriptions alone?
- [ ] Is there a test for a tool call whose `patient_id` or scope doesn't match the session?
- [ ] Is there a test for the no-tool-call branch and for malformed arguments?
- [ ] Are tool-selection cases in the eval set?
