<!-- Provenance: copied from Gauntlet AI/.claude/rules/agent-architecture.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
---
paths:
  - "**/*.py"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.js"
---

# Agent Architecture

Applies to any code that calls a language model or runs an agent loop. Skip for code that doesn't.

Source: `principles/engineering-stance.md`, `guardrails-and-verification.md`, `architecture-and-tradeoffs.md`, `loops-and-harnesses.md` and `graphs.md` in the Gauntlet AI repo. GP IDs in brackets.

## Rules

1. **Deterministic first [GP-4].** If a decision can be written as code — role or patient-scope checks, thresholds, date or dose math, table lookups — write it as code. Never route it through a prompt.
2. **Name the rung [GP-3].** Before adding a model call, a loop, or a new agent, state in the PR or design doc which rung it sits on (single call / call with tools / loop / planner / multi-agent) and why one rung lower would not work.
3. **Unstructured in, structured out [GP-5].** Model steps produce typed objects (Pydantic / Zod). Downstream logic consumes those objects, never free text. Prose for humans is the last step.
4. **Facts and arithmetic come from tools [GP-6].** Any number or clinical fact in an answer comes from a tool result or from code, never from model weights.
5. **Every loop has four brakes [GP-14].** Set explicitly, never inherited from framework defaults: `max_iterations`, a wall-clock timeout, a token or dollar budget, and a circuit breaker on repeated identical tool calls (default 3). Log which brake fired.
6. **Two stopping criteria [GP-15].** A happy-path stop (final structured answer that passes verification) plus the brakes as backstop.
7. **Keep choices small [GP-13].** Scope the tool set per role and flow. More than ~10 tools on one decision point means split into sub-agents or pre-select tools.
8. **Multi-agent needs a reason [GP-29].** A new agent must isolate context or a distinct trust role (judge, router, narrow worker). The orchestrator's context holds the request and worker list — not documents or tool output.
9. **Mind per-call cost [GP-33].** Tool definitions and history are resent every call: use prompt caching for stable prefixes and trim history.

## Loops and graphs

10. **Name both decisions of every loop [GP-64, GP-65].** Write down who answers "what next" and who answers "am I done". Exactly one owner declares done, and in a supervisor graph that is the supervisor.
11. **Static skeleton [GP-72].** Draw the graph yourself. The model chooses only the edges whose next step can't be known in advance, and the design doc lists each one.
12. **State first, and code writes it [GP-73, GP-76].** The typed state schema is reviewed before any node exists. Every field a router reads is declared. A node gives the model a narrow slice and writes back only its own keys.
13. **Routers are pure [GP-74, GP-75].** Branching lives in conditional-edge functions over typed fields. Branch on a code check of the output where one exists, never on the model's opinion of itself.
14. **Workers never route [GP-78].** A worker does one job and returns a typed result to the supervisor, never its transcript [GP-67]. Supervisor routing is evaluated as a classification problem against chance [GP-79].
15. **Bound every cycle in state [GP-77, GP-66].** Per-loop counters, including human revise rounds and evaluator rounds. Set `recursion_limit` explicitly. Hitting it is a failed run with a graceful response.
16. **Parallelize reads, serialize writes [GP-80].** Fan out only for independent reads. Shared state and external writes go through one node.
17. **One tool node, gated by risk tier [GP-81, GP-82].** Tools run in a guard node that re-checks scope. Only irreversible or external actions interrupt, and gate placement has eval cases.
18. **Pause, persist, resume [GP-83].** Use a durable checkpointer keyed by thread. Work before `interrupt()` must be idempotent.
19. **Guarantees come from structure [GP-84, GP-85].** Citations, caps and retries are enforced by nodes and edges. RAG is route → grade → rewrite-or-fallback with capped retries.
20. **Cost per decision [GP-69, GP-70, GP-87].** Use the cheapest model that makes each decision well, a classifier where a label is all you need, and cost logged per role. Limits live in a harness around the loop, not in its body [GP-71].

## Review checklist

- [ ] Could any model decision here be an `if`?
- [ ] Are all four brakes set to explicit values, with a test that each one stops the loop?
- [ ] Does every model step end in a validated schema?
- [ ] If a new agent or sub-agent was added, is its reason written down?
- [ ] Is the state schema reviewed, and does each node write only its own keys?
- [ ] Does every cycle have its own counter, and is `recursion_limit` set explicitly?
- [ ] Is any pre-`interrupt()` side effect idempotent?
