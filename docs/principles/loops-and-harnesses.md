# Loops and Harnesses — GP-64 to GP-71

GP-14 and GP-15 say every loop needs brakes and a stopping rule. These say where a loop's judgment actually lives, who owns it, what it costs at scale, and where its limits belong. Each principle applies to two kinds of loop, labelled on each:

- **Runtime** — the agent's own loop (the supervisor and worker loops in AgentForge).
- **Build** — the development loop that builds the product (PRD → issues → implement → review).

**Source.** One live cohort lecture, "Lecture 1 of 3" (harnesses with Zac and factories with Tom follow):

| Code | Lecture | Lecturer | Transcript | Slides |
|---|---|---|---|---|
| **L1** | Loops | Byron Mackay | `transcripts/loops-byron-transcript.md` | `course-material/loops.pdf` (8 pp, image-only) → **S-LP p.N** |

Full extraction notes, including the loop-pattern glossary and a line-by-line comparison against our build loop: `lecture-notes/L1-loops-byron.md`.

**The whole lecture in one slide**, S-LP p.5: *"A loop's reliability lives entirely in its decision points. Not in the model. Not in the framework."*

---

## GP-64 — Every loop has two decisions: what next, and am I done

**Statement.** A loop is decide → act → feed back → repeat. The only judgment calls are *what do I do next?* and *am I done?* For every loop, write down who or what answers each one and on what evidence; when a loop misbehaves, debug those two questions first. *(Runtime and build.)*

**Source.** Byron, L1 [2:07–3:03]: *"One is what do I do next?… And then the second… decision point that we have is when do we decide when we're done?"* L1 [34:38–35:01]: *"how does this loop decide what to do next? And how does this loop decide that it's done? And if you can… clearly answer those two questions, then… your loop will do just fine."* S-LP p.4: across ReAct, plan-and-execute, Ralph and generator–evaluator, *"the loop never changed — only who answers which question."*

**In practice.** `ARCHITECTURE.md` gets a two-row table per loop — supervisor loop, each worker loop — naming the next-step decider and the done decider (model / code / human) and its evidence. The build loop's table: next = the plan's issue order; done = frozen tests green and acceptance criteria met.

**Builds on.** GP-2, GP-15 (which covered only the "done" half).

---

## GP-65 — "Am I done" has exactly one owner

**Statement.** When several agents share a task, exactly one of them — or the code around them — may declare completion. Leave it to the group and each defers to the next; the loop never ends. *(Runtime and build.)*

**Source.** Byron, L1 [4:28–5:12]: *"I had three agents talking kind of passing things around and nobody… made the final call that it was done… nobody wanted to say it was all done. They just wanted to pass it off to the next one. And the transcript got to the point where they just started talking to each other about something totally unrelated to the task… we got to stop this before I get overcharged."*

**In practice.** Only the supervisor ends a Week 2 run; workers return a typed result and never declare the case closed (GP-78). In the build loop only the orchestrator merges; implementer and reviewer recommend.

**Builds on.** GP-15, GP-29.

---

## GP-66 — Bound the evaluator, or it becomes the reason the loop never ends

**Statement.** A generator–evaluator loop buys a second look, but an over-strict evaluator always finds something — even inventing small defects — and each extra round buys little. Give the evaluator a fixed, finite definition of done and cap its rounds. *(Build and runtime.)*

**Source.** Byron, L1 [3:24–3:43]: *"if either of those agents are too nitpicky, if they're trying to be too strict, you can be stuck in this loop forever. They'll just always find something."* L1 [11:23–12:01]: *"it can overcompensate… it can almost start to hallucinate like small details that it wants to capture and you can get into a larger loop for little value."*

**In practice.** Runtime: the judge scores against enumerated criteria (GP-49), gets one revise round, and then the answer ships with its verdict or is flagged. Build: the reviewer judges against the ticket's acceptance criteria — not open-ended "value" — and has a round cap alongside the implementer's attempt cap.

**Builds on.** GP-15, GP-16.

---

## GP-67 — Don't feed every decision back into the context that picks the next step

**Statement.** Appending the whole running transcript to "what next?" bloats the context and lets earlier stances — a verifier's "be very strict" — bias later decisions until the loop feeds on itself. Pass the next decision only what it needs. *(Runtime and build.)*

**Source.** Byron, L1 [3:39–4:05]: *"If we say, 'Hey, we're just going to shove the context like every time we get a new decision… into the context and pass the whole thing over.' What you're going to find is you're going to get this kind of context bloat and also get some information into that context that maybe you don't want influencing future decisions."* The naive loop on S-LP p.2 is exactly `context.append(result)` every step.

**In practice.** Workers hand the supervisor a typed result, not their transcript; a judge's critique goes back as a short list of specific defects, not its reasoning. In the build loop the implementer sees frozen tests and the reviewer's findings, never the reviewer's transcript.

**Builds on.** GP-25, GP-33.

---

## GP-68 — Answer "what next" with a reviewed plan

**Statement.** For decomposable work, prefer plan-and-execute: write the plan (PRD, tickets) before any code, review it, then let the loop walk it. The opposite — a model that picks its own work and declares its own completion (Ralph) — rarely stops without heavy reins. Choose by how you would solve the task yourself; there is no one-size-fits-all. *(Build; runtime secondary.)*

**Source.** Byron, L1 [6:53–7:46]: *"plan and execute. This is the one that I tend to work towards… we write up a plan, we write up the PRD, we write up tickets… we can… evaluate the plan and then we execute."* L1 [7:41–8:33]: *"Ralph is the opposite. It's completely non-methodical… Ralph would never say it's done… you would have to stop it."* L1 [14:14–14:21]: *"there's not a one-size-fits-all here."*

**In practice.** Week 2's build is already this: PRD → dependency-ordered GitLab issues → implement. At runtime, the supervisor's plan for a request (which workers, in what order) is decided up front and logged, so the trace shows plan against execution.

**Builds on.** New. GP-3 covers complexity rungs, not who plans the steps.

---

## GP-69 — Price each decision point at fleet scale, and tier the model per decision

**Statement.** A decision point is paid for every iteration, every run, every user. What is invisible in one loop becomes the largest line item at scale. Use the cheapest model that makes each specific decision well, and expect cost to be the main reason loops get redesigned. *(Runtime and build.)*

**Source.** Byron, L1 [16:02–16:38]: *"It's so easy for your AI cost to become your biggest line item in your engineering team… even higher than payroll… You don't want to use like Opus when Sonnet or Haiku would work."* L1 [16:53–17:43]: *"you just multiply that by 50… and you multiply that by 10,000 users and suddenly you've got something else going on… the cost was… always our… most common reason to go in and make changes to our loops."* S-LP p.7: 20 judged checks ≈ 20¢ per loop; ×50 ≈ *"$10 a run and 33 minutes of compute spent deciding, not working."*

**In practice.** `KEY_METRICS.md` records model and cost per decision (route, extract, judge). The eval gate runs on every PR, so its per-run cost × expected PRs is a budget line. In the build loop, the per-role model tier (Opus review, Sonnet implement) is justified per decision, not by habit.

**Builds on.** GP-22, GP-33.

---

## GP-70 — A narrow decision with code around it wants a classifier, not a generator

**Statement.** When the workflow is defined and code does the work, the model's job is a "glorified if statement": one specific question, a label (ideally with a probability), and code acting on it. Keep generative models for open-ended output you can't predict or write code for. *(Runtime.)*

**Source.** Byron, L1 [26:13–26:34]: *"You want to use [a classifier] when the workflow is defined where you have lots of… deterministic code to… do the workflow. What you're using [it] for at that point is… basically like glorified if statements."* L1 [29:01–29:17]: *"when we need a lot of text generated that we can't necessarily predict or write static code for, LLM becomes a really great tool."* Demo, L1 [24:54–25:22]: a Sonnet loop took 37 s and ~9¢ with 33 tool calls; the classifier plus code took 1.6 s and 0.2¢.

**In practice.** "Is this upload a lab report or an intake form?" and "is this line an analyte row, a header, or a reference-range note?" are classification decisions with code behind them — candidates for a small model with a confidence threshold. Generative calls stay for free-text intake answers and the clinician-facing summary. *The product Byron demoed is spelled "Jev" in the captions (unverified), and he said he hadn't tested it on "am I done"; the principle is the shape of the decision, not the product.*

**Builds on.** GP-4, GP-5 — a middle rung between an `if` and a generative call.

---

## GP-71 — A loop's limits live in a harness around it

**Statement.** Keep the loop minimal. A harness wraps one loop and owns escalation, retry counts, limits and which tools may run; a factory runs many harnessed loops in parallel. Brakes are harness policy, enforced from outside the loop's own decisions. *(Build; the runtime analogue is the supervisor as harness.)*

**Source.** Byron, L1 [14:52–15:35]: *"the harness… takes a loop and it kind of manages it for you… when does it escalate? How many retries?… what are the limitations? What tools are we going to allow to be run in here?… And then the factory has many of these harnesses… running in parallel."* S-LP p.6: *"Harness — Supervises one loop's decision points — limits, retries, escalation. Factory — Runs many harnessed loops at once."*

**In practice.** GP-14's four brakes, per-worker tool allow-lists and the escalate-to-clinician path live in one supervisor-side policy module, not scattered through prompts and worker code. The build loop's attempt caps, tamper checks and budget kill-switch are harness responsibilities. *Zac's harnesses lecture and Tom's factories lecture are not yet ingested and may refine this.*

**Builds on.** GP-14 — says where the brakes live.
