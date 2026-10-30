# Evals and Observability — GP-19 to GP-24

Tests tell you deterministic code works. Evals tell you a probabilistic system works *often enough*. Observability tells you what it actually did.

---

## GP-19 — Evals ship with the MVP

**Statement.** A small but meaningful golden set is part of the first working version, not a later phase. Building evals *is* building the system.

**Source.** Aaron, V2 [37:19–37:44]: *"Have evals and start with evals early. I would say you need to start considering at the very least like basic evals, a small but meaningful golden set as part of MVP. Okay? You don't wait and say, 'Oh, you know, we'll do evals in a few days. Let's just crank on the system first.' No. Evals are part of cranking on the system."* V1 [36:08]: *"Evals, you need evals."*

**In practice.** Before the Wednesday early submission, the eval set exists, runs with one command, and its latest results are committed.

---

## GP-20 — An eval is a human-verified input with its expected behaviour

**Statement.** Eval cases pair an input with what should happen: which tool gets chosen, what the query looks like, what the final answer is. A realistic set includes edge and hard cases, so the score should not be 100%.

**Source.** Aaron, V1 [32:08–33:04]: *"having some hold-out good cases that have often been, if not made, then at least verified by a human… when this is the request, the agent should choose to use the search tool and not the database query tool… and also maybe end-to-end ones… it probably shouldn't be 100%. If you want to have a real-world representative set, you're going to have examples, edge cases, and hard cases that the system might get wrong."*

**In practice.** Three layers of case: tool selection, tool arguments, and final answer. The PRD adds that every case must target a boundary, an invariant or a regression risk.

---

## GP-21 — A baseline turns changes into experiments

**Statement.** Once the eval gives a baseline score, any change — prompt, model, tool — is an experiment with a measurable result and a cost. Without it, you are vibe-checking and cannot tell whether you improved.

**Source.** Aaron, V1 [33:36–34:56]: *"your MVP system gets 92%… Great. You now have a baseline. And now if a new model comes out… you can just run an experiment… oh, now it's 95% right… Oh, but it also costs more. Well, is that worth it?… otherwise… you vibe check it and you feel good… did the change help? I don't know… you aren't able to iterate… you get very stuck very quickly."*

**In practice.** Every PR that touches prompts, models or tools reports eval score and cost before and after. Week 2 formalizes this as a PR-blocking CI gate.

---

## GP-22 — Measure quality and operations separately, per agent

**Statement.** Quality metrics (retrieval precision/recall, groundedness) say how *good* the system is; operational metrics (latency, cost) say how well it *runs*. You need both, and each sub-agent that makes decisions needs its own eval.

**Source.** Aaron, V2 [37:44–38:56]: *"these first two are really like classic metrics… measuring how well your retrieval works assuming you have labeled data… groundedness is a little bit fuzzier because it's probably like an LLM-as-judge… and then latency and cost. Those are also real numbers, but… operational numbers… You need both. And you can also have metrics at the level of agents. If you're going to split out into sub-agents… you can have a separate eval for each of those."*

**In practice.** `KEY_METRICS.md` separates "is it right" from "is it fast and affordable". A supervisor's routing gets its own eval, separate from each worker's.

---

## GP-23 — Instrument from the start with LLM-aware observability

**Statement.** Record every request's steps, timings, tool calls, token usage and spend from the first commit, in a tool that understands LLM calls. Curated production traces later become eval data.

**Source.** Aaron, V1 [36:40–37:04]: *"measure everything — both the evals as well as just good old software observability… there's ones specialized for LLMs, LangSmith and Langfuse, that… have your stack traces and stuff but they're also LLM-aware, so they know about your tokens and your model and your token spend."* V1 [39:56–40:12], the demo agent: *"observability first… how long it took the agent and how many iterations and how much we spent, whether it pulled it off."* V2 [53:08–53:24]: *"You should be instrumenting things."* V2 [39:08–39:24]: *"have an observability platform like LangSmith be collecting stuff and then use those traces as evals… once you've validated some of your actual production logs, that is a really good source of truth."* Jacob, V3 [43:40–44:28]: when a tool fails, *"you need to have observability in production to make sure you know when things are going wrong, what's going wrong."*

**In practice.** The tracer is wired before the second tool is written. Each trace shows the retrieved documents and tool results, not just the final answer.

---

## GP-24 — Most of the work is in the data

**Statement.** Writing the agent entry point is the fun part. The bulk of the work — and most of the quality — is building, labelling and checking cases, often with domain experts.

**Source.** Aaron, V1 [33:04–33:36]: *"this is where most of the work is — dealing with data and dealing with labeling and getting it right and having tests and evals and cases. That's where all the work is. It's not in just writing the run code and the entry point. That's the fun part. This is where the slog is and this is where you often have to collaborate a lot with domain experts."*

**In practice.** Budget eval-set work into the first two days of every week, not the last evening.
