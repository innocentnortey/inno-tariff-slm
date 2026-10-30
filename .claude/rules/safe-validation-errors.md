<!-- Provenance: copied from Gauntlet AI/.claude/rules/safe-validation-errors.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
---
paths:
  - "agent/**/*.py"
---

# Safe Validation Errors — never repeat rejected input

Applies to every error message, exception, log line, trace span, tool refusal and HTTP error body the agent service produces. Added 2026-09-15 after E1-T1, where three review passes each found the same leak one layer deeper (`DEVLOG.md` F-2026-09-15-06): our own message echoed the value, then Pydantic's rendering did, then its structured errors did. A value that fails to validate as a `PatientRef` is exactly the value most likely to be a patient's name.

## Rules

1. **An error names the field, a stable error code and the violated constraint — never the value.** `patient_id: invalid_format (expected canonical UUIDv4)`, not `'John Smith' is not a valid patient_id`. This holds for hand-written messages, exception text, `ValidationError` rendering, tool refusals returned to the model, and HTTP error bodies.
2. **"May contain" is the test, not "does contain."** Anything that arrived in a request, a chart record, a tool argument, a model output, a header or an environment variable is treated as PHI, PII, a secret or user-controlled data.
3. **The framework defaults are the leak.** Every model inherits `agent.domain.AgentModel` (`hide_input_in_errors=True`); settings classes set the same flag; exactly one `RequestValidationError` handler, registered in `create_app()`, rewrites FastAPI's default 422 body to field, code and constraint; and `ValidationError.errors()` / `.json()` still carry `input` even with the flag set, so no call site serialises them without stripping it.
4. **Error codes are stable identifiers** (`invalid_format`, `out_of_scope`, `missing_required`) defined once in one module under `agent/domain/`, never inline, so tests and dashboards match on the code.
5. **Negative tests are mandatory.** A ticket that adds or changes validation, an error path, a log line or a trace field ships a test that submits a distinctive rejected value (a seeded name, DOB, SSN pattern, token) and asserts it is **absent** from the HTTP response body, the captured log output and the exported trace. "Redacted somewhere" is not a pass; absence in all three is.

## Enforcement

- The implementation includes the negative test whenever it changes validation, errors, logging or tracing.
- The focused test run proves the distinctive rejected value is absent from the declared exits.
- Diff review rejects any path that can expose rejected input in an error, log, trace or response.

Companion: `pydantic-data-modeling.md` §2 (`extra="forbid"`), `LEARNINGS.md` (the same rule in prompt form).
