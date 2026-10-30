# Observability in Practice — GP-56 to GP-63

GP-23 says to instrument from the start. These say what the trace must contain, what its status does and doesn't tell you, what must never go in it, and what it is for beyond debugging.

**Source.** One live cohort lecture:

| Code | Lecture | Lecturer | Transcript | Slides |
|---|---|---|---|---|
| **O1** | AI Observability (LangSmith and Langfuse) | Aaron Gallant | `transcripts/ai-observability-meeting-transcript.md` | none captured (screen-shared only) |

Full extraction notes, including 13 tools and 13 anti-patterns with timestamps: `lecture-notes/O1-ai-observability-aaron.md`. The lecture's point about curating traces into labelled data is merged into **GP-45**.

**A new reason for GP-23**, O1 [1:04–1:36]: observability matters more now *"since you're not writing all of it or even reading all of it necessarily yourself."* Agent-written code is code you haven't read.

---

## GP-56 — Trace what the model actually saw, not what the user typed

**Statement.** At every model call, record the full assembled input — system prompt, harness instructions, retrieved chunks, few-shot examples, user message — together with the raw output. The user's question is a small part of what the model was conditioned on.

**Source.** Aaron, O1 [8:16–8:48]: *"the X is the prompt and really the X is the context. The X is everything you give it… it's your harness. It's whatever gets dynamically intelligently loaded by your harness. It's whatever your RAG retrieves."* O1 [24:44–25:16]: *"from the user's perspective, they… said what is task decomposition? That's all they gave the LLM. But the system as a whole gave the system prompt, gave the retrieved context… even looking at the code, a lot of this is kind of obfuscated because the code is so magical and elegant."*

**In practice.** Every worker's LLM span records the prompt version, the hybrid-RAG chunks with ids and scores, the extracted fields passed in, and the completion before parsing. A wrong golden-set answer can then be pinned to retrieval, prompt assembly or the model. The PHI side of this is GP-59.

**Builds on.** GP-23.

---

## GP-57 — Traces are hierarchical: one span per step, under one request

**Statement.** Each stage is its own nested span under a single top-level run, so one request can be expanded step by step and every system it touched is visible in one place.

**Source.** Aaron, O1 [2:56–3:20]: *"a very rich explorable stack trace… we're going to be composing a bunch of systems together here. So a single comprehensive tool is just critical to be able to see all of them in the same place."* O1 [5:12–5:20]: *"you can actually dig into the inner steps of an interaction and see it hierarchically."*

**In practice.** The supervisor run is the root. Under it: each worker; under each worker, BM25 retrieval, dense retrieval, fusion, the LLM call and every OpenEMR tool call — all carrying the correlation id. Document extraction gets its own spans so ingestion failures separate from answer failures. Per-agent latency and cost (GP-22) fall straight out of the spans.

**Builds on.** GP-23, GP-22.

---

## GP-58 — A green check means it ran, not that it was right

**Statement.** Trace status reports computational success — no exception, no timeout. A run can succeed end to end and still answer badly or pick the wrong tool. Quality needs its own domain-defined signal and some manual review; the platform is where you do that work, not what does it.

**Source.** Aaron, O1 [27:28–28:08], on the green checks: *"This is just computationally saying… if an API times out or you have a logic error… then you'll have a red X… But if what you're talking about is more like… maybe it all ran but we don't think this answer is good."* O1 [28:40–29:04]: *"it's going to be context specific to define the metric… you might have to actually manually review at least some cases."* O1 [30:08–30:16]: *"This system does not solve that problem for you."*

**In practice.** The three Week 1 alerts cover operational failure. Quality is the eval gate plus a sample of *successful* production traces reviewed for wrong-tool and unsupported-claim failures. Never report either as the other.

**Builds on.** GP-22 — applies the quality/operations split to trace status and alerting.

---

## GP-59 — Decide what must never be logged before you log everything

**Statement.** What gets logged raw, and for how long, is set by sensitivity, not storage cost. Engineers over-log by default. Credentials, government ids and personal data need a written policy before tracing goes live.

**Source.** Aaron, O1 [10:24–11:04]: *"usually the storage isn't the issue. Usually be more about… if there's any sensitivity… Engineers don't always have a good instinct for when they should or shouldn't log something in the raw… you don't want to log passwords, you don't want to log social security numbers… log retention policy can also have to do with that."*

**In practice — reconciling with GP-56.** Full-context traces of a clinical co-pilot are PHI. AgentForge's current position holds: synthetic patients only; Byron's 2026-09-17 instruction to assume a signed BAA with every processor, LangSmith included; and the existing rule that a driven test asserts no seeded identifier reaches any declared exit. For a real deployment: redact identifiers at the span level while keeping OpenEMR record ids for citation, or send full-content traces only to a self-hosted backend (GP-60). Write the retention period in `AUDIT.md`.

**Builds on.** New. GP-32 covers secrets in the repo, not trace content.

---

## GP-60 — Choose where traces live by who you have to trust

**Statement.** A hosted-only platform means trusting its vendor with every prompt and response. When traces hold sensitive data or you need that control, choose one you can self-host — but don't take self-hosting on as a side project when nothing requires it.

**Source.** Aaron, O1 [15:24–15:48]: *"LangSmith is hosted. You cannot host LangSmith yourself… If you can't trust LangChain for whatever reason, Langfuse is a reasonable alternative… you can run it yourself."* O1 [16:20–16:36]: *"don't go down that rabbit hole unless you've done all your project… that's the sort of thing you can do in a situation where it's a good idea, such as you have sensitive information you want to log."*

**In practice.** `ARCHITECTURE.md` says what leaves the deployment in traces and why that is acceptable (synthetic cohort, assumed BAA), and names self-hosted Langfuse as the production path for real PHI. One defensible trade-off line.

**Builds on.** GP-30.

---

## GP-61 — Steer output with a handful of labelled examples

**Statement.** A few curated input–output examples in the prompt are one of the cheapest reliability gains. A handful, not a hundred — past that you are flooding the context.

**Source.** Aaron, O1 [44:00–44:32]: *"you could think of this as one of the cheapest forms of prompt engineering to steer the output with labeled data… you don't want to give like a hundred examples. That's just flooding your context window. But if you can give a handful of examples, you can often greatly improve the reliability."*

**In practice.** Each extraction worker gets two to four annotated examples: a clean document, a messy scan, a missing value. They must not overlap the golden set or the eval measures memorisation (GP-45).

**Builds on.** GP-25, GP-24.

---

## GP-62 — Traces are the audit trail; the model call stays a black box

**Statement.** When a conclusion affects a person, the trace lets you step back through how the system got there. But the model call itself is only visible from outside — tokens in, tokens out. Explainability has to come from the steps you control around it.

**Source.** Aaron, O1 [30:48–31:28]: *"it could also be used from like an auditability or compliance perspective, if you need to have some explainability for how your system reached a certain conclusion because that conclusion… impacts a real person's life."* O1 [31:28–31:52]: *"fundamentally, whenever there's one of these calls, this is a little bit of a black box… we give them these tokens, they give this response. That's all we can know."*

**In practice.** For any clinical claim, the audit answer is the chain: OpenEMR record ids retrieved, values extracted, deterministic rules fired, verification result. Never "the model decided."

**Builds on.** GP-11, GP-16.

---

## GP-63 — Choose tools by constraints, not by a "best" tool

**Statement.** There is no best framework or platform in the abstract. Scale, team, lifespan, existing cloud commitments, where it runs, and privacy needs decide. The concepts transfer; tool-specific constructs are the easy part.

**Source.** Aaron, O1 [49:16–50:12]: *"tool choice is a function not just of like what is the best tool in some hypothetical platonic ideal sense, because there isn't really an answer to that… is this a prototype, an MVP that I'm going to re-engineer in six months, or am I making something that I intend to have for the long haul?… Are there privacy, security concerns… all of those factors and constraints enter into all tool choice questions."*

**In practice.** Every tool row in `ARCHITECTURE.md` (LangGraph, LangSmith, the vector store, the model provider) names the constraint that chose it — week-long lifespan, solo team, Railway, PHI exposure — never "industry standard."

**Builds on.** GP-7, GP-30.
