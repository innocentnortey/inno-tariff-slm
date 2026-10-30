# Gauntlet Principles

Engineering principles extracted from Gauntlet's lectures: the three async pre-work videos (GP-1 – GP-37, 2026-09-13) and seven live cohort lectures on evals, observability, loops and graphs (GP-38 – GP-88, added 2026-09-23), Week 3's security lecture, PRD and kickoff (GP-89 – GP-106, added 2026-09-28), the 2026-10-08 system-design session (GP-107 – GP-119), and the identifying-business-problems lecture (GP-120 – GP-130), and the defining-business-metrics lecture (GP-131 – GP-144), both added 2026-10-16, and RAG evaluation (GP-145 – GP-155, added 2026-10-27 from web research after Ash Tilawat's Slack reminder — not a lecture). Each principle has a stable **GP-N** ID (never reused), a one-line statement, what the lecturer actually said with a timestamp, and what it means in practice.

**These are the source of truth.** `.claude/rules/` turns them into checks that load automatically while writing code and design docs; every rule cites the GP IDs it enforces. When a principle changes, change it here first, then the rule.

---

## Sources

| File | Lecture | Lecturer | Syllabus async item |
|---|---|---|---|
| `course-material/video1.md` | Production AI Agents + Data Synthesis | Aaron Gallant | *Agents and Generating Synthetic Data* |
| `course-material/video2.md` | Agentic RAG | Aaron (program announcements first) | *Agentic RAG* |
| `course-material/video3.md` | Tool Calling ("stop talking to models, start having them do things") | Jacob | *Tool Calling* |

**Source quality.** These are staff lectures, so they are strong evidence for *what Gauntlet teaches*. Two caveats:
- **They were recorded with an earlier cohort.** Video 2 opens *"Week one of Gauntlet is done"*; video 3 opens *"this is you guys' first week."* Teaching content transfers; logistics in them are that cohort's.
- **The transcripts are auto-captions.** Speaker labels are empty in videos 2 and 3, and words are sometimes misheard ("Langmith" = LangSmith, "React loop" = ReAct). Quotes below are cleaned for readability, never for meaning.

Citation format: `V1 [36:16]` = video 1 at 36 minutes 16 seconds.

### Live cohort lectures (added 2026-09-23)

Recorded with **Innocent's own cohort** (he asks questions in E1, E3, O1 and G1), so the logistics in them are current too. Auto-captions, with speaker labels in Aaron's sessions; Byron's are unlabelled.

| Code | Lecture | Lecturer | Transcript (`transcripts/`) | Slides (`course-material/`) | Principles |
|---|---|---|---|---|---|
| **O1** | AI Observability (LangSmith, Langfuse) | Aaron Gallant | `ai-observability-meeting-transcript.md` | none captured | GP-56 – GP-63 |
| **E2** | Evals That Actually Work, part 1 | Byron Mackay | `eval-meeting-transcript.md` | `eval-part-1-and-2-slides.pdf` (image-only) → S-EV | GP-38 – GP-55 |
| **E1** | Evaluating Agents | Aaron Gallant | `ai-Eval-meeting-transcript.md` | `evaluating_agents.pdf` → S-EA | GP-38 – GP-55 |
| **E3** | Evals That Actually Work, part 2 | Byron Mackay | `eval-part2-byron-transcript.md` | `eval-part-1-and-2-slides.pdf` → S-EV | GP-38 – GP-55 |
| **L1** | Loops (lecture 1 of 3: loops → harnesses → factories) | Byron Mackay | `loops-byron-transcript.md` | `loops.pdf` (image-only) → S-LP | GP-64 – GP-71 |
| **G1** | Intro to Graphs | Aaron Gallant | `intro-to-graphs-transcript.md` | `AI School Week 6.1_ LangGraph .pdf` (a reused deck) → S-LG | GP-72 – GP-88 |
| **G2** | Advanced Graph Techniques | Aaron Gallant | `graphs-part2-transcript.md` | `advanced-graphs.pdf` → S-AG | GP-72 – GP-88 |
| **SEC** | AI Security: Threats & Defenses (OWASP LLM Top 10) | Byron Mackay | **not yet received** | `2026-09-28-ai-security-threats-defenses-slides.pdf` (image-only) → S-SEC | GP-89 – GP-97 |
| **K3** | Week 3 project kickoff: Byron walks the PRD | Byron Mackay | `2026-09-28-intro-to-week-3-project-byron.md` (AssemblyAI, speaker-labelled) | Week 3 PRD, `2026-09-28-week3-agentforge-prd.pdf` → W3 | GP-98 – GP-106 |
| **DM** | Defining business metrics (cohort session; leading and lagging indicators defined here) | Presumably Byron Mackay (GQ-25) | `defining-business-metrics.md` | none captured | GP-131 – GP-144 |
| **BP** | Identifying business problems (cohort session) | Host not named in the captions (see GQ-24) | `identifying-business-problems-transcript.md` | none captured | GP-120 – GP-130 |

`lecture-notes/` holds the full extraction for each lecture: metadata, every candidate principle with verified quotes, which existing GPs it restates, every tool named, and every anti-pattern with a timestamp. The principle files are the curated, de-duplicated layer on top. Slide citations use `S-XX p.N`, where N is the PDF page number.

**Not yet ingested:**
- The syllabus's Harnesses / Orchestration (Zac) and Factories (Tom) sessions, which follow L1 and may refine GP-71.
- **The recording of the SEC lecture.** GP-89 – GP-97 currently cite slide text only.

---

## The one idea underneath all of them

> A language model is a probabilistic next-token predictor. **Engineering with one is the work of taming that uncertainty** — shrinking what the model has to decide, bounding what it is allowed to do, and proving what it produced.

Aaron, V1 [5:12]: *"they are inherently probabilistic. They're inherently uncertain. And so a lot of what we're doing is about taming that uncertainty and channeling it."*

---

## Index

| File | IDs | Covers |
|---|---|---|
| [`engineering-stance.md`](engineering-stance.md) | GP-1 – GP-7 | What an agent is, matching complexity to the problem, deterministic-first, structured output |
| [`tool-design.md`](tool-design.md) | GP-8 – GP-13 | Atomic tools, descriptions as routing, the model advises and your code executes |
| [`guardrails-and-verification.md`](guardrails-and-verification.md) | GP-14 – GP-18 | Loop brakes, stopping criteria, the verification ladder, refusal |
| [`evals-and-observability.md`](evals-and-observability.md) | GP-19 – GP-24 | Evals in the MVP, baselines, metric families, tracing |
| [`context-and-rag.md`](context-and-rag.md) | GP-25 – GP-28 | Context engineering, the RAG ladder, retrieval defaults |
| [`rag-evaluation.md`](rag-evaluation.md) | GP-145 – GP-155 | Evaluating a RAG pipeline: retriever vs generator vs answer, error analysis by stage, a labelled retrieval set, recall@k / precision@k / MRR / nDCG by stage, the recall–noise trade, claim-level faithfulness, citation recall and precision, nugget coverage, unanswerable questions, calibrated judges, retrieval settings as experiments. Source: web research (RAGChecker, ALCE, ARES, UAEval4RAG, TREC RAGTIME, Ragas, TruLens, Hamel Husain, Anthropic), prompted by Ash's 2026-10-27 Slack |
| [`architecture-and-tradeoffs.md`](architecture-and-tradeoffs.md) | GP-29 – GP-33 | Multi-agent restraint, trade-off thinking, debt, security, token cost |
| [`synthetic-data.md`](synthetic-data.md) | GP-34 – GP-37 | Four ways to generate test data |
| [`agent-evaluation.md`](agent-evaluation.md) | GP-38 – GP-55 | Trajectory grading, spread and error bars, must-pass core vs coverage set, the grader ladder, error analysis, holdout, replay, judges and their calibration, rubrics, gates, experiments |
| [`observability-in-practice.md`](observability-in-practice.md) | GP-56 – GP-63 | Full-context and hierarchical traces, green ≠ right, what never to log, where traces live, traces as audit trail |
| [`loops-and-harnesses.md`](loops-and-harnesses.md) | GP-64 – GP-71 | The two decision points, one owner of "done", bounded evaluators, plan-and-execute, cost per decision, classifiers, harnesses |
| [`adversarial-security.md`](adversarial-security.md) | GP-89 – GP-106 | OWASP LLM Top 10 mapped to the co-pilot; capability not bugs; untrusted output; stacked sanitization; documents as instruction channels; least privilege; HITL outside the model; gateway defenses; cost DoS; context extraction; independent judge; regressions that pass for the right reason; mutation; orchestrator on observability; per-role model choice; trust boundaries; reproducible reports; typed contracts; black-box scope |
| [`business-metrics.md`](business-metrics.md) | GP-131 – GP-144 | Prove it with a number; health vs value metrics; leading and lagging indicators; a lagging move means investigate; actionable vs vanity; denominators and segments; match what this customer values; a small set; one north star plus supporting metrics; coverage and bias; adoption is not quality; baseline, aspiration and hard gate; review and expect challenge; pick the user first. Source: the defining-business-metrics lecture (DM) |
| [`problem-framing.md`](problem-framing.md) | GP-120 – GP-130 | Cheaper builds mean longer planning; a PRD is the partner's answer, not the problem; question the assumption inside the question; a complaint is a symptom, observe first; keep asking why; scope the why; tie work to money in as many hops as it takes; name the north star before building; count use, not output; when you can't ask, research, label and try; the engineer owns the "why". Source: the host's identifying-business-problems lecture (BP) |
| [`system-design.md`](system-design.md) | GP-107 – GP-119 | Economics first, scale buckets, depth where the partner is uncertain, measurable promises, users → work, elapsed time ≠ resource demand, first breaker, queues and overload, autoscaling limits, per-operation CAP, caches as authority, replicas/zones/regions, labelled numbers. Each ends with questions to raise in the design conversation. Source: the 2026-10-08 cohort session (a peer, not staff) and its ChatGPT synthesis |
| [`graphs.md`](graphs.md) | GP-72 – GP-88 | Static skeleton, state-first, nodes vs edges, supervisor/worker contract, routing as classification, reads vs writes, tool node, risk-tier gates, pause/persist/resume, RAG as edges |
| [`frameworks.md`](frameworks.md) | — | Every framework and tool the lectures recommend or demo |
| [`lecture-notes/`](lecture-notes/) | — | Full per-lecture extractions for the live lectures |

---

## Most impactful for AgentForge (weeks 1–3)

Ranked by how directly they decide a grade. The HTML briefing (`artifacts/2026-09-13-principles-briefing.html`) expands each.

1. **GP-3 / GP-4 — Earn every model decision.** Deterministic first; match complexity to the problem. This is the backbone of every technical-interview answer.
2. **GP-11 — The model advises; your code executes.** Where auth, patient scoping and refusal live. Kwabena's week-1 grader asked for exactly this proof.
3. **GP-8 / GP-9 — Tool descriptions are the router.**
4. **GP-14 — Every loop has four brakes.** Iterations, timeout, budget, circuit breaker.
5. **GP-16 / GP-18 — The verification ladder, climbed as far as the stakes demand.** Healthcare is high-stakes.
6. **GP-19 / GP-21 — Evals ship with the MVP.** A baseline is what turns changes into experiments.
7. **GP-23 — Instrument before you need it.**
8. **GP-25 / GP-27 — Fewer, better tokens; climb the RAG ladder by eval.** Week 2.
9. **GP-5 — Unstructured in, structured out.** Week 2's lab PDFs and intake forms.

### Week 2 additions — the ten that most change the build (2026-09-23)

1. **GP-73 / GP-76 — State first, and code writes it.** Review `CopilotState` before any node exists. Each node writes only its own keys.
2. **GP-78 / GP-79 / GP-65 — The supervisor contract.** It routes, talks to the user and alone declares "done". Workers report back. Routing is evaluated as a classification problem against chance.
3. **GP-40 / GP-50 — The gate is the PRD's.** A 50-case golden set with five boolean categories. It fails on any category regressing more than 5% or dropping below threshold. A labelled behavioural set sits *on top of* the 50 (kickoff). Safety categories are floored at 1.00. Thresholds are committed before the first run. Run with repeats, because a single run's noise exceeds 5% (GP-39).
4. **GP-41 / GP-47 / GP-48 — Cheapest grader first.** Code assertions for extraction and routing. A binary, per-claim judge only for groundedness, and only after it agrees with ~20 human labels.
5. **GP-44 — Error analysis before graders.** Read ~20 traces, note the first failure in each, and build your own taxonomy.
6. **GP-45 / GP-53 — Cases before prompts; a sealed holdout; never edit an expectation to go green.**
7. **GP-38 / GP-52 — Grade the trajectory, per model call, upstream first.**
8. **GP-81 / GP-82 / GP-83 — Human-in-the-loop done right.** One tool node as the chokepoint. Gates by risk tier: only chart writes pause. A durable checkpointer, and idempotent pre-interrupt work.
9. **GP-85 / GP-86 — RAG as edges.** Grade, rewrite once, fall back to "no evidence", cap retries. Prove any query transform on the golden set.
10. **GP-56 / GP-59 — Trace the full context the model saw**, under a written PHI and retention policy.

---

### Week 3 additions — the ten that most decide the grade (2026-09-28)

1. **GP-98 — The judge is a separate agent with its own audit.** Deterministic checks first (canary strings, rendered DOM, budget brakes). An LLM judge only for fuzzy categories, and only once calibrated. A canary set of known exploits is re-graded every run: if the judge approves any of them, it has drifted.
2. **GP-99 — A regression passes only for the right reason.** Replay the original and its variants, several times each. Assert that *the control fired*, not just that the bad output is missing.
3. **GP-102 — Choose each role's model by measured refusal rate and cost.** Frontier models refuse red-team work (Byron, K3 [15:33]). A build-versus-configure record (Garak, ZAP, Burp, Semgrep) is a strong stretch goal. It became optional in Byron's 2026-09-28 correction.
4. **GP-101 — The orchestrator scores coverage gaps in code.** Observability is its data source, and the six questions on W3 p.11 are the acceptance test.
5. **GP-94 — Human approval is triggered by the tool, never by the model.** Answer *"where does your HITL live?"* in `ARCHITECTURE.md`.
6. **GP-92 / GP-97 — Uploaded documents are instruction channels. A pass means the data is absent, not that the model refused.** Seed every synthetic patient with a unique canary string.
7. **GP-100 — Mutate on a *partial* verdict.** Keep a finite, logged list of mutation operators so novelty can be measured. Static payload lists fail the requirement.
8. **GP-106 — Attack black-box through the chat interface, against an allowlisted live target.** Build it as a greenfield GitLab repo. The scope is LLM and agentic vulnerabilities, not OpenEMR's PHP.
9. **GP-89 — Every fix names the architectural control that changed.** A prompt edit is a layer, not a fix.
10. **The OWASP mapping is the one required engineering deliverable** (Byron, Slack 2026-09-28). Every eval case carries its OWASP web or LLM category. GP-105's typed contracts are a stretch goal.

---

## How principles become rules

| Rule (`.claude/rules/`) | Loads when editing | Enforces |
|---|---|---|
| `agent-architecture.md` | Python / TypeScript / JavaScript source | GP-2 – GP-6, GP-13 – GP-15, GP-29, GP-33; loops and graphs GP-64 – GP-88 (key ones) |
| `agent-tools.md` | Python / TypeScript / JavaScript source | GP-8 – GP-12, GP-32 |
| `verification-evals-observability.md` | Source, `tests/`, `evals/` | GP-16 – GP-24; evals GP-38 – GP-55 and observability GP-56 – GP-62 (key ones) |
| `retrieval-and-context.md` | Retrieval, RAG, embedding, prompt and corpus paths | GP-25 – GP-28, GP-145 – GP-155 |
| `synthetic-test-data.md` | Seeds, fixtures, golden sets, demo assets | GP-34 – GP-37 |
| `design-doc-defense.md` | `ARCHITECTURE.md`, `USERS.md`, `AUDIT.md`, `KEY_METRICS.md` | GP-1, GP-3, GP-16, GP-19, GP-30, GP-31 |
| `system-design-conversation.md` | PRDs, interviews, hard-problems pages, design and architecture docs | GP-107 – GP-119 |
| `problem-framing.md` | PRDs, brief audits, success-framing docs, converted sources | GP-120 – GP-130 |
| `business-metrics.md` | `KEY_METRICS.md`, metrics docs, PRDs, success-framing docs | GP-131 – GP-144 |

**Portability (2026-10-14).** Every new coding repo gets a copy of this folder at `docs/principles/` (all principle files and this README; `lecture-notes/` stays here) alongside the rules, via `zero-to-hero` Stage 0. The rules cite GP IDs, so without the copy the citations point nowhere. Change a principle here first, then re-copy.

**Earlier note.** The AgentForge build will live in its own repo (the OpenEMR fork). Per the workspace rule on cross-project reuse, copy these rule files into that repo's `.claude/rules/` when it is created and adjust the `paths:` globs to its layout. They are written to stand alone.

**Where AgentForge carries them (2026-09-23).** `../inno-agentforce/.claude/rules/evals-and-observability.md` holds the eval and observability lines. `llm-agent-code.md` §0 holds the loop and graph lines. That repo keeps its rules short, so each line cites a GP ID, and the full principle lives here.
