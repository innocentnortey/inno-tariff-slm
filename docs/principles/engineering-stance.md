# Engineering Stance — GP-1 to GP-7

How Gauntlet wants you to think before you pick any tool.

---

## GP-1 — Use precise terms, not marketing terms

**Statement.** Say "language model", "tool call", "retrieval", "agent loop" — words you can specify and test — rather than "AI".

**Source.** Aaron, V1 [3:52–4:48]: *"it's just unspecified… dare I say, it's a marketing term… we are learning engineering… we care about terms that are precise that allow us to be well specified and understand what we're building and know if it's going to work or not, know how to test it."*

**In practice.** In `ARCHITECTURE.md` and in interviews, name the mechanism: *"Claude Sonnet decides which of four FHIR tools to call"*, not *"the AI figures it out."* A precise claim is one a grader can check — and one you can defend.

---

## GP-2 — An agent is a program whose control flow the model influences

**Statement.** The defining property of an agent is that the language model — not a hand-written `if` — chooses the next branch, which function runs, and how often.

**Source.** Aaron, V1 [7:28–8:40]: *"an agent… is when you are basically allowing the control flow of your program to be impacted by the language model… With agents, we can just expose potential paths, essentially tools, and the agent quote decides which way to go."* V1 [11:36–12:40]: an LLM with tools but a single turn is *"still just doing one thing"*; an agentic system *"starts having a loop… the ReAct loop for reasoning plus acting."*

**In practice.** Everything the model decides is a place the system can go wrong. List those decisions explicitly in your architecture doc — each one needs a bound (GP-14) and an eval (GP-19).

---

## GP-3 — Match the complexity of the solution to the complexity of the problem

**Statement.** There is a spectrum — single LLM call → LLM with tools → ReAct loop → planning agent → multi-agent graph. Each rung adds capability *and* latency, cost and unreliability. Pick the lowest rung that solves the problem.

**Source.** Aaron, V1 [14:48]: *"it's all about matching the complexity of our solution to the complexity of the problem."* V1 [15:44–16:48]: the spectrum's numbers are *"vague orders of magnitude… if you need things to be really fast, use less stuff… there should be a dollar sign next to all of these."* V2 [15:36–16:00]: *"I'm pretty sure you heard me say that last week, and I'm pretty sure you'll hear me say it next week. You don't always want the most complex solution, but you don't always want the simplest solution either."* V1 [35:04] key takeaway: *"match the complexity of your solution to the complexity and uncertainty in your problem."*

**In practice.** For each AgentForge capability, name its rung and the reason it can't sit one rung lower. "Show today's schedule" is a query, not an agent. "What changed since the last visit, and does it interact with current meds?" plausibly needs a loop.

---

## GP-4 — Deterministic first

**Statement.** Never use a model where a static boolean will do. Don't use agentic patterns for deterministic logic, strict-latency paths, or large batch jobs.

**Source.** Aaron, V1 [8:56–9:12]: *"If you can just write an if statement, like a good old deterministic if statement, you always should — never use an LLM when a static boolean will do, because the static boolean is cheaper, faster, more reliable."* V1 [16:56–18:00]: if it's deterministic, *"embrace that"*; a full ReAct loop is *"arguably never going to be sub-second"*; for huge batch processing *"you might not want to use an expensive agent… basically, if something can be simpler, make it simpler."*

**In practice.** Patient-scope checks, role checks, dose thresholds, date math, drug-interaction lookups against a table — all code, never a prompt. The model gets the part that is genuinely uncertain.

---

## GP-5 — Unstructured in, structured out

**Statement.** The typical good problem shape: the model turns unstructured or semi-structured input into a well-defined structured output, and deterministic code takes over from there.

**Source.** Aaron, V1 [19:04–20:16]: *"if your data has that level of structure, then if statements can probably make most of your decisions… But if it's unstructured data… that's where the LLM can quote understand that. And you often still want to target structured output. I would say that's the majority case… at some point the system transitions… deterministic code might well take over once you've finished that sort of extraction."* Takeaway V1 [35:12].

**In practice.** Week 2: a lab PDF becomes a typed `LabResult` (value, unit, reference range, source page), then validation, persistence and trend math are plain code. A human-readable summary, if any, is the last step — not the data format.

---

## GP-6 — The model confabulates; facts and math come from tools

**Statement.** "Hallucination" is a misnomer: the model always emits likely tokens, and humans judge them wrong against the real world. So truth has to be checked against something outside the model, and facts and arithmetic should come from retrieval and tools, not weights.

**Source.** Aaron, V1 [27:12–28:32]: *"the LLM is a statistical model that is giving us the most likely tokens and sometimes we the humans based on the real world… judge those tokens to be wrong… It's called confabulating."* V1 [45:08–45:24]: *"LLMs, despite being big math functions, suck at math… If you want to do arithmetic, give it the right tool."* V1 [49:16–49:32]: *"LLMs do not retrieve facts… it's probabilistic. It's lossy. It's not a guarantee."*

**In practice.** Any number the co-pilot states — a lab value, a dose, days since last visit — is either read from a tool result or computed in code, and cited.

---

## GP-7 — Mental models over memorizing tools

**Statement.** The field churns; the underlying concepts mostly don't. Learn enough of how things work to choose between solution types, and use abstractions freely.

**Source.** Aaron, V1 [1:28–2:08]: *"a lot of the things that matter don't really change. Math is math… you do need to not be afraid of math."* V1 [6:16–6:40]: new releases are *"an iterative improvement, but it's not actually that different."* V2 [59:40–59:56], on how deep to go on embeddings: *"try to get enough of an intuition to feel like you can make decisions between solution types. You don't need to understand how to build everything from scratch."*

**In practice.** When a framework does something for you (a recursion limit, a retriever, a tool wrapper), know what it is doing underneath well enough to explain it in the technical interview.
