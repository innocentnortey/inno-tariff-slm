<!-- Provenance: copied from Gauntlet AI/.claude/rules/verification-evals-observability.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
---
paths:
  - "**/*.py"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
  - "**/tests/**"
  - "**/evals/**"
  - "**/golden*/**"
---

# Verification, Evals and Observability

Applies to code that produces model output a user or downstream system will rely on, and to test and eval suites.

Source: `principles/guardrails-and-verification.md`, `evals-and-observability.md`, `agent-evaluation.md` and `observability-in-practice.md`, Gauntlet AI repo.

## Verification

1. **Pick rungs by stakes, and write them down [GP-16].** Available rungs in rough order of strength and cost: automated flags and authoritative-source checks → LLM-as-judge with a narrow input → hard business rules in code → human approval. Clinical, financial, compliance and security output uses the upper rungs.
2. **Every claim is attributable [GP-16, GP-18].** Output that states a fact carries a citation to the record or passage it came from. Uncited claims are withheld or explicitly marked as inference.
3. **Refusal is a valid answer [GP-18].** Retrieval has a relevance floor; below it, the system says the sources don't answer. The prompt explicitly permits refusal, and eval cases exist whose correct output is a refusal.
4. **Judges are narrow [GP-16, GP-29].** An LLM judge sees only what it needs (candidate output, evidence, rubric) and, where independence matters, runs on a different model from the generator.
5. **Human approval shows evidence [GP-17].** An approval step presents the proposed action and the evidence behind it, not a raw transcript.

## Evals

6. **Evals ship with the MVP [GP-19].** A new model-driven capability is not "done" without golden cases that run from one command.
7. **Three layers of case [GP-20].** Tool selection, tool arguments, and final answer. Each case names the failure mode it guards (boundary, invariant or regression). The set includes hard and edge cases, so a 100% score is a smell.
8. **Changes are experiments [GP-21].** Any PR changing a prompt, model, tool description or retrieval setting reports eval score and cost before and after. No "looks better" merges.
9. **Separate quality from operations, per agent [GP-22].** Report correctness metrics (precision/recall, groundedness) apart from latency and cost, and evaluate each decision-making sub-agent on its own.
10. **Two tiers, and the gate decided in advance [GP-40, GP-50].** A golden set that must pass, plus a labelled coverage set expected to fail sometimes. Safety-shaped checks are floored at 1.00. Thresholds are committed before the first run. Where an issued PRD defines the gate (AgentForge Week 2: 50 cases, five boolean categories, >5% regression fails), the PRD wins.
11. **Cheapest grader that works [GP-41, GP-42].** Order: assertion → invariant → trajectory → judge → human. Assert on the parts that matter, never snapshot whole statistical output.
12. **Grade the trajectory, per model call, upstream first [GP-38, GP-52].** A case checks the path as well as the answer. A step-level gain must also show up end to end.
13. **One run is an anecdote [GP-39].** Repeat cases and report a spread. A move smaller than the set's error bar is not a result.
14. **Judges are binary, per claim, and calibrated [GP-47, GP-48, GP-49].** Yes/no per claim from a narrow, anchored, human-written rubric. The judge enters the gate only after it agrees with ~20 human labels (≥ 0.8). Recalibrate when its prompt or model changes.
15. **The set is an artifact [GP-44, GP-45, GP-53].** Cases are written before the prompt and grown from error analysis (first failure per trace, your own taxonomy). There is a sealed holdout the agent can't read. An expected output is never edited to go green; changing one takes its own commit.
16. **One variable per experiment [GP-51].** Same set, prompts versioned in git, cost in the comparison table.
17. **Fix the environment before the prompt [GP-54].** Log blocked attempts separately from successes. A human reads agent-written tests before any builder runs [GP-55].

## Observability

18. **Instrument from the first model call [GP-23].** Every request gets a correlation ID and a trace in an LLM-aware backend (Langfuse or LangSmith) recording ordered steps, per-step latency, tool calls and failures, retrieved documents, tokens and cost.
19. **No PHI or secrets in logs or traces [GP-59].** Redact before export, and keep a test that drives real flows while capturing output and asserts no seeded identifiers appear.
20. **Traces feed evals [GP-23, GP-45].** Reviewed, corrected production or demo traces are promoted into the golden set — never unreviewed.
21. **Trace what the model saw, hierarchically [GP-56, GP-57].** Every model call's span holds the full rendered context and the raw output, nested under one request.
22. **Green is not right [GP-58].** Trace status and ops alerts report computation; quality has its own signal and is never reported as the other.

## Review checklist

- [ ] Which verification rungs does this path use, and is that written in the architecture doc?
- [ ] Is there at least one refusal case and one wrong-tool case in the evals?
- [ ] Does the PR state eval score and cost before and after?
- [ ] Can a single request be reconstructed end to end from its trace?
- [ ] Does the gate match the issued PRD, with safety categories at 1.00?
- [ ] Has any judge in the gate been calibrated against human labels?
- [ ] Did any PR change an expected output alongside agent code?
