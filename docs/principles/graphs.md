# Graphs — GP-72 to GP-88

Week 2 is a graph: a supervisor routing to two workers over typed state, with ingestion, hybrid RAG, verification and a human gate. These principles cover how to design that graph — what the state holds, where the model is allowed to decide, how cycles stay bounded, where humans and tools plug in, and how RAG becomes edges.

**Sources.** Two live cohort lectures (Week 2, days 1–2):

| Code | Lecture | Lecturer | Transcript | Slides |
|---|---|---|---|---|
| **G1** | Intro to Graphs (LangGraph: nodes, edges, state, supervisor, hierarchical teams) | Aaron Gallant | `transcripts/intro-to-graphs-transcript.md` | `course-material/AI School Week 6.1_ LangGraph .pdf` (9 pp) → **S-LG p.N** |
| **G2** | Advanced Graph Techniques (human-in-the-loop, evaluating and ranking agents, agentic RAG) | Aaron Gallant | `transcripts/graphs-part2-transcript.md` | `course-material/advanced-graphs.pdf` (37 pp) → **S-AG p.N** |

Full extraction notes, including every LangGraph construct and tool named: `lecture-notes/G1-intro-to-graphs-aaron.md`, `lecture-notes/G2-advanced-graphs-aaron.md`.

**Source caveats.**
- The G1 deck was reused from another program (its title is "AI School Week 6.1", with diagrams "Accessed 4 June 2024"). Aaron still followed it page by page. Its demo code uses older LangGraph calls (`MessageGraph`, `set_entry_point`).
- G2 is built on LangGraph 1.2 and LangChain 1.4, and Aaron framed it as *"a survey of reusable patterns, not code to copy."*
- Neither lecture covers streaming, reducers or general node error handling.

**Merged elsewhere, not repeated here:**
- G2's "verifier first, judge second" and "measure the judge" are in **GP-41** and **GP-48**.
- G2's model audition on quality × cost is in **GP-51**.
- "One owner of done" is **GP-65**.

---

## GP-72 — Draw the skeleton yourself; give the model autonomy only where the path can't be known

**Statement.** Chain, DAG, graph and agent differ in how much control flow you fix in advance. Draw a static skeleton, and let the model choose branches only where the next step depends on output you cannot predict. Often that means an agent inside a single node of an otherwise fixed graph. The graph's extra calls (routing, grading, groundedness checks) are what buy its guarantees. An agent that owns the whole flow is never independently verified.

**Source.** Aaron, G1 [27:20–28:40]: *"how opinionated are you about the control flow of your program. With a chain you are fully opinionated… wherever there's like a potential logic branch that you can't necessarily figure out in advance… that pretty quickly puts you in graph territory. And then agent is like, I can't even draw a graph."* G1 [26:16–26:24]: *"don't add loops and stuff if you don't need them."* G2 [6:52–7:08]: *"autonomy… the LLM is making branching decisions… Only use that when you actually have to, which sometimes you do."* S-AG p.4: *"Most products today: static skeleton, dynamic inside a node."* S-AG p.29: *"The graph's extra calls are its guarantees… the agent's answer is never independently verified."*

**In practice.**
- The ingestion path is a chain or DAG with one bounded retry: upload → classify → extract → validate → write back.
- The question-answering path is ingest → supervisor → worker → verify → respond. The model chooses only the supervisor's route and the ReAct steps inside each worker.
- `ARCHITECTURE.md` lists every edge the model chooses. Every other edge is code.

**Builds on.** GP-2, GP-3. This adds a second measure of complexity and applies it node by node.

---

## GP-73 — Design the state schema first; it is the graph's real specification

**Statement.** Before drawing nodes, define the state: one typed schema holding everything the graph needs, most of it empty at the start of a run. It says more about the graph than the diagram does, and it must declare every field a routing decision reads.

**Source.** Aaron, G1 [18:08–18:40]: *"that's one of the main design decisions you make up front — what are the things you're keeping track of… and that is going to say a lot, honestly, almost more than the picture of the graph."* G1 [50:32–50:40]: *"a graph is defined by its state. That's kind of like the data schema of the graph."* G1 [43:56–44:20]: *"the routing decisions depend on who sent that last message"*, so that goes in state too.

**In practice.** Write and review the `CopilotState` Pydantic model before any node exists. It holds:
- the request and the pinned patient;
- the route;
- each worker's typed output (lab results, intake fields, passages with source ids);
- the verification result;
- the answer.

Fields a conditional edge reads (`next_worker`, `verification_passed`) are declared in the model, never parsed out of message text.

**Builds on.** New. It is the graph-level counterpart of GP-5 and GP-10.

---

## GP-74 — Nodes do work; conditional edges decide where to go

**Statement.** A node is a function from state to state. Branching lives in conditional edges: small router functions that read state and name the next node. Routers do no work.

**Source.** Aaron, G1 [6:00–6:40]: *"you might think, oh, the nodes are agents… But fundamentally the node is a function."* G1 [10:16–10:56]: *"The branches are not functions… The branches are conditional edges… There's an if statement in the edge."*

**In practice.** `route_after_supervisor(state) -> Literal["lab_worker", "intake_worker", "respond"]` is a pure function over typed fields and has its own unit tests. The supervisor's LLM call writes a validated enum into state, and the edge only reads that enum. Worker nodes contain no routing `if`s.

**Builds on.** GP-2. This pins down exactly where the model touches control flow.

---

## GP-75 — Branch on a code check of the model's output, not on the model's opinion

**Statement.** Where possible, a conditional edge branches on a deterministic check of structured output: does it validate, does it resolve, does it run. Split the output into typed parts so each part can be checked. Let a model decide a branch only where no code check exists.

**Source.** Aaron, G1 [8:56–9:12]: *"these checks, even though they are nodes, these do not have to be LLMs. In fact, I would argue that it is best for these not to be LLMs."* G1 [9:52–10:16]: *"the branches… are determined not directly from the LLM output, but based on an actual deterministic check of the LLM output. And if you can shape your problem that way, that's good."* S-LG p.3: the code-generation graph retries with the stack trace.

**In practice.** After lab-PDF extraction, the retry edge fires on any of these code checks:
- Pydantic validation fails.
- The unit is outside the allowed set.
- The value is outside physiological bounds.
- The cited page doesn't exist in the document.

The failure message goes back to the extractor, the same way the stack trace does in the lecture example.

**Builds on.** GP-4, GP-16, applied to routing.

---

## GP-76 — Code writes the state; the model sees and returns a narrow slice

**Statement.** Don't hand a model the whole state and ask it to update it. The node's code extracts the few fields the model needs, formats the prompt, validates the result and writes it to the right field. Any node can technically change any field, so write discipline is enforced in code.

**Source.** Aaron, G1 [20:48–21:12]: *"any node, at least in principle… could mutate any at least mutable field in your state."* G1 [21:28–22:32]: *"you wouldn't just give the researcher agent the direct research state dictionary object and say update this… it's kind of a lazy, potentially destructive approach… you often want to very tightly scope the input and output that you give to LLMs. That will highly improve the reliability."*

**In practice.** Each worker returns a partial update of only its own keys. For example, the lab worker returns `{"lab_results": [...]}`, built from a validated object. The worker's prompt gets the question and the document, never `CopilotState`. A test asserts that each node changes only the keys it owns.

**Builds on.** GP-11, GP-25.

---

## GP-77 — Every cycle is a `while` loop; bound it in state

**Statement.** A feedback edge makes the graph a `while` loop. The global recursion limit ends the run wherever it happens to be, possibly with the answer field empty. So bound each loop with its own counter in state, set the global limit deliberately, and treat hitting it as a failed run with a graceful response. Human revise loops count too: people can loop forever.

**Source.** Aaron, G1 [19:20–19:44]: *"This is basically a while loop, right? This is not a bounded for loop."* G1 [20:08–20:32]: *"if you hit the recursion limit… that is probably not a good run. You didn't get to the answer field… Better than an infinite loop though."* G2 [17:16–17:48]: *"cap revised loops… humans can loop forever too."* S-AG p.15: *"Cap revise-loops (attempts < 3)."*

**In practice.**
- `extraction_attempts` and `revision_count` live in state. The retry edge routes to `fail_gracefully` after two.
- `recursion_limit` is set explicitly, a little above the longest legitimate path.
- `GraphRecursionError` is caught, and the response returns any verified partial results with the name of the brake that fired.
- One golden-set case has a document that never validates.

*Aaron guessed the default limit "might be 10" while his demo passed 25. Check it against the installed LangGraph version.*

**Builds on.** GP-14, GP-15.

---

## GP-78 — The supervisor routes and talks to the user; workers do one job and report back

**Statement.** In the supervisor pattern the supervisor owns all control flow and all communication with the user. Workers make no routing decisions. Each one takes a task, does it with a narrow prompt and toolset, and returns the result to the supervisor, never to another worker or to the user.

**Source.** Aaron, G1 [52:24–52:48]: *"The supervisor is the concierge that takes users' requests and returns curated user responses and is also the boss, as it were, of all the sub-agents."* G1 [53:36–54:16]: *"These agents, these leaf nodes, they don't make any routing decisions… the only thing the agent can do is do the task and return the result back to the supervisor."* S-LG p.7.

**In practice.** The supervisor picks `lab_worker`, `intake_worker` or `respond`, and it is the only node that writes the user-facing answer. Each worker has one static edge back to the supervisor. Adding a third worker means one enum value and one edge.

**Builds on.** GP-29, GP-65.

---

## GP-79 — Supervisor routing is an N-way classification; evaluate it against chance

**Statement.** Every supervisor step answers "which worker gets this?" Evaluate it as a classification problem: labelled cases, per-class accuracy, a confusion matrix, and a comparison against chance (1/N). The problem gets harder as N grows. The scaling answer is hierarchical teams, where each team is a subgraph with its own supervisor, but only when the problem is truly that complex.

**Source.** Aaron, G1 [54:24–55:12]: *"did you assign this task to the right agent? It's making a classification decision… picking one out of three things… baseline accuracy… would be about 33%… A 10-class classification problem, baseline accuracy is 10%."* G1 [56:16–56:48]: *"Do not pick this off the shelf as your first thing… Never ever add unnecessary complexity."*

**In practice.** About a third of the golden set are routing cases, each labelled with the expected worker, `respond` or refusal. The gate reports routing accuracy and the confusion matrix apart from answer quality. With 2–3 routes, chance is 33–50%, so a score near that is a failure. AgentForge adds no team layer.

**Builds on.** GP-22, GP-13, GP-52.

---

## GP-80 — Parallelize reads, serialize writes

**Statement.** Fan out only when the branches are independent. Gathering information (search, retrieval, lookups) merges cleanly and parallelizes well. Writing to a shared artifact creates conflicts, so it gets a single thread or a lock. Parallelism is also what makes multi-agent latency acceptable at all.

**Source.** Aaron, G2 [7:56–9:08]: *"are you doing read versus write work… if you are doing read work… you don't care about the order things happen… then parallel fan out and multi-agent systems can work… If you have to write… a shared artifact, well if you have a bunch of writers, you're liable to run into write conflicts… some sort of mutex lock."* S-AG p.7.

**In practice.**
- A question that needs both the patient's labs and a guideline passage fans out with `Send`, because both are reads.
- The two extractors' updates to shared patient facts merge in one deterministic node, never through two agents editing concurrently.
- Every write back to OpenEMR goes through one serialized, gated node (GP-81).

**Builds on.** GP-29, GP-30.

---

## GP-81 — Tool execution is its own node: one place to check, approve or refuse

**Statement.** Route every tool request through one dedicated tool node instead of running tools inside agent nodes. That node is the single chokepoint where code re-checks the request, asks a human, or refuses. It also keeps reasoning separate from side effects.

**Source.** Aaron, G1 [40:48–41:44]: *"LangChain lets you isolate your tools in a specific node of the graph… you could imagine a graph where the routing involves checking a human… pause the graph execution and send a Slack message to Bob to see if it's okay to actually run the delete user function… by putting the tool call in on its own node, you can have some nice modularity and isolation."* S-LG p.6.

**In practice.** Wrap or replace LangGraph's `ToolNode` with a guard. Before running anything, it re-checks that the `patient_id` argument matches the pinned patient and that the caller's role allows the tool. A refusal returns as a structured tool result, not an exception, and is logged as an attempt (GP-54).

**Builds on.** GP-11, GP-17.

---

## GP-82 — Gate by risk tier, and test that you gated the right things

**Statement.** Decide per tool, from its consequences, whether it pauses for a human:
- **Read-only:** never pauses.
- **Reversible:** logged or sampled.
- **Irreversible or external:** always pauses, and the human sees and can edit the exact arguments.

Gate as little as you can, because approval fatigue buys the cost of oversight with none of the safety. Some gates are compliance and hold even when the model is right. Whether the system asks for a human exactly when it should is itself an eval.

**Source.** Aaron, G2 [14:28–15:48]: *"approval fatigue… it almost becomes actually another like metric or eval you could have for your system is like are you invoking human in the loop in the situations where you should… gating fewer things is always better."* G2 [29:04–29:44]: *"In the case of the medical domain, it might even be a compliance thing… there are certain things that a human just has to sign off on."* S-AG p.13: *"if people click 'approve' without reading, you have the cost of oversight and none of the safety… move tools down a tier only with evidence… per tool, not per agent."*

**In practice.**
- Chart reads, lab lookups and RAG never interrupt.
- A drafted summary is logged.
- Writing an extracted lab value or intake field into the chart always gates, and shows the value, unit and source page with edit power.
- Golden-set cases labelled `expects_interrupt: true/false` catch both over-gating and under-gating.

**Builds on.** GP-16, GP-17.

---

## GP-83 — Human approval is pause, persist, resume, so replayed steps must be idempotent

**Statement.** A human gate pauses execution and persists state durably, because the human may take hours and the process may restart. It then injects the human's answer and resumes. A rejection is feedback the model can adapt to, not a dead end. On resume the node restarts from the top, so any side effect before the pause runs again and must be idempotent.

**Source.** Aaron, G2 [10:52–11:48]: *"some sort of approval gate that basically has three steps. You pause execution… it has to persist the state when it pauses somehow… and then we resume."* G2 [16:28–17:16]: *"You have to think about things like idempotency… because basically you might end up re-executing stuff through that time travel."* G2 [13:56–14:20]: *"the rejection is just a signal back to the system."* S-AG p.10: *"a checkpointer… a thread_id… interrupt()."* S-AG p.15: *"anything before interrupt() runs twice. Make pre-interrupt side effects idempotent."*

**In practice.** Use a durable checkpointer (Postgres, not `InMemorySaver`), because a Railway redeploy would otherwise drop every pending approval. Key each thread to the conversation id. Put `interrupt()` at the top of its own node, before any audit write, FHIR write or model call, or give those calls idempotency keys. The review accepts approve, edit, or reject with a reason, and a rejection re-runs extraction under GP-77's cap.

**Builds on.** GP-17, GP-8.

---

## GP-84 — Guarantees come from graph structure, not from asking the model

**Statement.** Anything that must always hold is guaranteed by code and graph structure: citations, caps, retries, who may execute an action. For example, workers cite result numbers and code renumbers and validates them, and a gated tool physically cannot run before approval.

**Source.** S-AG p.32: *"Structural citations: workers cite result numbers; code renumbers them globally — guaranteed by the graph, not requested from the model."* S-AG p.12: *"The model never had the power to move money; the human saw the exact arguments first."* S-AG p.35: *"Structure beats prompts for guarantees (citations, caps, retries)."* Aaron, G2 [51:56–52:12]: the research agent's subgraphs *"check the citations so it didn't hallucinate."* *(Mostly slide-sourced; the spoken support is thin.)*

**In practice.** Claims point to `source_id`s drawn from the tool results the worker was given. A deterministic `cite_check` node removes or flags any claim whose id wasn't actually retrieved, and it renumbers citations for display. An uncited claim cannot pass the response node.

**Builds on.** GP-11, GP-6, GP-54.

---

## GP-85 — RAG techniques are edges: grade retrieval, fall back, cap every retry

**Statement.** Draw advanced RAG as nodes and conditional edges:
- a router picks the source;
- a grader checks whether the retrieved chunks are actually relevant;
- a failed grade triggers a rewrite or a fallback, so a bad route can be recovered;
- a final check asks whether the answer is grounded.

Structured-output graders make cheap models safe to branch on. Every retry edge is capped. Grounded is not the same as true: it only means faithful to the retrieved text.

**Source.** Aaron, G2 [43:16–44:12]: *"we route it, we retrieve it, we grade the results. If we pass, we generate an answer, we check if the answer is good… If we fail grading steps, we rewrite the query… what this lets us do is basically recover from a bad route."* S-AG p.27: *"Structured output turns cheap LLM graders into safe branch conditions. Bound every loop (MAX_REGENS=2, MAX_REWRITES=1, recursion_limit)… Grounded ≠ true."* S-AG p.35: *"RAG 'techniques' are edges — draw the graph for your failure modes."*

**In practice.** The guideline-RAG worker runs: route → hybrid retrieve → grade (a Pydantic `RelevanceGrade` from a cheap model) → generate, or rewrite once and fall back to "no supporting evidence". The fallback is never web search, which is off-limits for clinical claims. After generation come the groundedness check and a staleness check on the guideline's date. Each grader has its own eval cases (GP-52).

**Builds on.** GP-27, GP-18.

---

## GP-86 — Bridge the vocabulary gap between users and the corpus, then prove it on your data

**Statement.** When users write in lay or shorthand terms and the corpus is written in clinical language, plain embedding search misses. A query transform can close the gap: rewrite, multi-query, decomposition, or HyDE (the model writes a hypothetical passage in the corpus's style and you search with that). Each transform costs a call and can distort intent. Keep it only if your eval shows it helps.

**Source.** Aaron, G2 [44:44–47:16]: *"Let's say you're building a rag system on a medical knowledge base… regular people and academic doctor publisher people use very different language… we write hypothetical documents in the same style as the corpus… It's totally okay if they're hallucinations… it does add a LLM call up front."* S-AG p.28: *"HyDE, demoted… In our notebook ablation, HyDE pulled generic… passages while the plain query hit the passage… — not a free win. Test on your data."*

**In practice.** Clinician shorthand ("pt on warfarin, INR 4.1") and patient-written intake text both differ from guideline prose. Add an optional rewrite node that expands abbreviations and maps lay terms to clinical ones. A/B test it, and HyDE, on the golden set's retrieval cases before enabling either. Hypothetical passages are search queries only and never reach the answer.

**Builds on.** GP-27.

---

## GP-87 — Multi-agent cost follows the depth of delegated work, not the diagram

**Statement.** A multi-agent design's cost depends on how much work each sub-agent does, which model it runs on, and how much context it re-reads. The number of boxes doesn't decide it. Shallow workers on cheap models with isolated context can cost less than one long single loop that re-reads every earlier result. Log cost per role and measure your own case.

**Source.** S-AG p.33: *"Multi-agent used ~0.8× the tokens, ~0.7× the dollars — not Anthropic's 15×. Why? Model tiering: 6 of 8 calls ran on the cheap model. Context isolation… Cost follows the depth of work you delegate, not the box diagram. n = 1, one noisy LLM judge — measure your own."* S-AG p.23: *"Bound everything: rounds, subagents, searches, dollars. Log cost per role."* Aaron, G2 [8:28–8:44]: parallelism is what makes multi-agent latency workable. *(Mostly slide-sourced.)*

**In practice.** The supervisor runs on a cheap routing model. Workers keep raw retrieval hits to themselves and return a typed summary. Every span is tagged with its role, so `KEY_METRICS.md` reports cost per role: supervisor, extractor, RAG worker, judge.

**Builds on.** GP-29, GP-33, GP-69.

---

## GP-88 — Explain a graph through its state, its subgraphs and its impact

**Statement.** A full node-and-edge render of a real system is unreadable. Explain it in three moves: show the state schema as the summary of what the graph processes, cut the graph into subgraphs and explain each one, and lead with business impact for non-technical listeners.

**Source.** Aaron, G1 [11:36–12:24]: *"what you might need to do is cut it up… you can often cut them up into subgraphs… And then the top level, if you're talking to execs… impact, right? You always frame everything in impact. Business impact, metrics."* G1 [18:32–18:56]: *"showing the state might actually be a really good way to do it."*

**In practice.** The interview defense has three layers:
1. The one-screen `CopilotState`.
2. One diagram each for ingestion, question answering and verification.
3. One impact line, for example "the clinician gets a cited lab trend in N seconds instead of reading M pages".

Never open with the compiled-graph render.

**Builds on.** GP-1, GP-30.
