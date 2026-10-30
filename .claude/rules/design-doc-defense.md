<!-- Provenance: copied from Gauntlet AI/.claude/rules/design-doc-defense.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
---
paths:
  - "**/ARCHITECTURE*.md"
  - "**/*_ARCHITECTURE.md"
  - "**/USERS.md"
  - "**/USER.md"
  - "**/AUDIT.md"
  - "**/KEY_METRICS.md"
  - "**/TECH_DEBT.md"
---

# Design Docs Built to Be Defended

Applies to the AgentForge hard-gate documents. Gauntlet grades whether you can defend what you built, live, in a technical interview — these docs are the script.

Source: `principles/` GP-1, GP-3, GP-16, GP-19, GP-22, GP-30, GP-31, Gauntlet AI repo.

## Rules

1. **Precise mechanisms, not "the AI" [GP-1].** Name the model, the tool, the retrieval step or the rule that does the work. Every claim should be checkable by a grader.
2. **Every model decision is listed [GP-2, GP-3].** `ARCHITECTURE.md` enumerates each place a model chooses control flow, its complexity rung, and why one rung lower would not work — and each place deterministic code was chosen instead.
3. **Every decision carries its cost [GP-30].** Each architectural choice has a "what this costs us" line: latency, dollars, reliability, operational complexity.
4. **Verification rungs are explicit [GP-16].** State which verification rungs each output path uses, what each catches, and what it doesn't.
5. **Agent-shaped use cases only [GP-3, GP-4].** In `USERS.md`, every use case answers why a conversational agent beats a query, dashboard or sorted list. If it doesn't, cut the capability.
6. **Metrics split quality from operations [GP-22].** `KEY_METRICS.md` separates "is it right" (groundedness, correct refusal, tool-selection accuracy) from "does it run" (p95 latency, cost per interaction), each with a baseline and target.
7. **Evals are part of the architecture [GP-19].** The architecture doc describes the eval set and how changes are gated, not only the runtime path.
8. **Debt is written down with a due date [GP-31].** Shortcuts taken for an early submission go in `TECH_DEBT.md` with the week they must be paid by.
9. **Agentic or retrieval systems carry an Evaluation Plan [GP-19, GP-20, GP-22, GP-27].** `ARCHITECTURE.md` defines end-to-end evals (does it work) and component evals for each layer present — retrieval, agent behaviour, answer (where to fix it) — each with a domain definition, ground truth and pass bar, plus the trace fields to capture now. Template: `gauntlet-prd-workflow/templates/eval-plan.md`. Skip for systems with no agent loop or retrieval.

## Review checklist

- [ ] Could you answer "why is this an agent and not an `if`?" for every capability from this doc alone?
- [ ] Does every decision have a stated cost?
- [ ] Is there a known limitation for each verification rung?
- [ ] If there's an agent loop or retrieval: is each component eval defined in this domain, with its ground truth and the trace fields that make it runnable later?
