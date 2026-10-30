# Architecture and Trade-offs — GP-29 to GP-33

---

## GP-29 — Multi-agent sparingly; sub-agents to isolate context

**Statement.** Full multi-agent teams usually add more complexity than they solve. Specialized sub-agents — a judge, a router, a worker with a narrow tool set — are the useful form: they isolate context. An orchestrator stays lean; its job is routing, not holding everything.

**Source.** Aaron, V1 [36:16–36:40]: *"you don't always need that. Multi-agent tends to add a lot of complexity. Now you can have sub-agents where you have a very specialized agent like the LLM-as-judge… a good way to isolate and control the context… But actual full-on multi-agent where they're all really capable and they're all talking and working like a team — it sounds cool and it's usually a mess."* V2 [36:00–36:48]: *"one of the main ways to manage the complexity is to split it into sub-agents. That way, no one agent is expected to keep all the context or choose from all the tools… an orchestrator… might seem like the biggest agent, but the whole point is actually that agent shouldn't have a whole bunch of junk in its context window."*

**In practice.** Week 2's supervisor carries the request and the worker list, never the documents. Week 3's judge sees only the attack transcript and a rubric, on a different model from the attacker.

---

## GP-30 — Think in trade-offs; there is no free rung

**Statement.** Every architectural option trades latency, cost, reliability, scalability and complexity. Naming the trade-off — not picking the "best" option — is what reads as senior.

**Source.** Jacob, V3 [1:15:12–1:16:40], one agent with many tools vs an orchestrator with sub-agents: *"if you have to go through one agent that will determine the other agents and then they're waiting for those agent responses… when you're getting a million requests… you do have additional potential network latency."* V3 [1:16:48–1:17:28]: *"I'm glad you're thinking about trade-offs… that's really what separates the senior, lead, staff engineer type people… scalability really is like, what's the trade-off. There's no perfect answer."* Aaron, V2 [36:56–37:12]: *"The more complex you make it, the slower it's going to be, more expensive… the less reliable… at least implemented without appropriate guardrails and evals."*

**In practice.** Every decision in `ARCHITECTURE.md` gets an explicit "what this costs us" line.

---

## GP-31 — Ship the MVP, then pay prototype debt fast

**Statement.** Don't let perfect guardrails block the first feedback loop — but anti-patterns that slip in while prototyping accrue interest, and anything called "production" needs the guardrails.

**Source.** Aaron, V1 [23:04–23:20]: *"as you're prototyping… you might have some of these anti-patterns slip in your code. So be aware, pay that tech debt down quickly because it will accrue interest."* V1 [35:52–36:08]: *"don't let the perfect be the enemy of the good. When you're making your very first prototype MVP, getting the feedback loop going, you're not going to have perfect guardrails for everything. But certainly, if you want to call a system production… you need guardrails."*

**In practice.** Keep a short `TECH_DEBT.md` of shortcuts taken for the early submission, each with the week it must be paid by. The PRD's "technical debt costs double" makes weeks 2 and 3 the interest.

---

## GP-32 — Never give the model destructive access; keep secrets out of the repo

**Statement.** The model reaches data only through narrow tools your code controls — never raw database access. API keys live in environment files that are ignored by git, with a committed sample.

**Source.** Jacob, V3 [3:12–3:28]: *"that one company who… made software for rental car companies and just like their AI just dropped a bunch of their database tables."* V3 [19:12–19:20]: *"a lot of the times you don't want to give it direct access to your database because it could drop tables."* V3 [20:48–21:04]: *"we're not giving the LLM access to your database. We're giving your code access to the database and your code goes and gets the stuff."* V3 [33:16–33:48] and [1:09:12]: `.env` for the key, `sample.env` committed, `.gitignore` for `.env`.

**In practice.** Read-only FHIR tools with parameterized queries; no generic "run SQL" tool. A secret scan runs in CI.

---

## GP-33 — Every call resends the tools and the history

**Statement.** The model has no memory between calls: the tool list and conversation history travel with every request, so large tool sets and long histories cost tokens and latency on every turn.

**Source.** Jacob, V3 [24:00–24:24]: *"the model has no memory. So basically every time you call out to the model… you're going to have to… send the list of your tools every single time."* V3 [55:48–56:04]: *"we're basically chaining these messages. So the LLM knows our message history."* V3 [1:12:08–1:14:24], asked about caching repeated tool definitions, Jacob was unsure and suggested pre-classifying which tools to send.

**Note (not from the lecture).** Both Anthropic and OpenAI now offer prompt caching for repeated prefixes such as tool definitions and system prompts. Kwabena's co-pilot measured it cutting a brief's cost roughly in half. Treat caching as the first answer and tool pre-selection (GP-13) as the second.
