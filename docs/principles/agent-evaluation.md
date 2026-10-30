# Evaluating Agents — GP-38 to GP-55

GP-19 – GP-24 say *that* you need evals, a baseline and traces. These say *how*: what a case checks, which grader checks it, how the set is split and grown, how a judge earns trust, and what the gate blocks.

**Sources.** Three live cohort lectures (Innocent's cohort, 2026-09-16 to 09-21):

| Code | Lecture | Lecturer | Transcript | Slides |
|---|---|---|---|---|
| **E1** | Evaluating Agents: a working loop, not a metrics catalogue | Aaron Gallant | `transcripts/ai-Eval-meeting-transcript.md` | `course-material/evaluating_agents.pdf` → **S-EA p.N** |
| **E2** | Evals That Actually Work, part 1 (golden sets, labelled coverage, error analysis) | Byron Mackay | `transcripts/eval-meeting-transcript.md` | `course-material/eval-part-1-and-2-slides.pdf` → **S-EV p.N** |
| **E3** | Evals That Actually Work, part 2 (replay, judges, rubrics, experiments) | Byron Mackay | `transcripts/eval-part2-byron-transcript.md` | same deck |

Full extraction notes, including every tool named and every anti-pattern with a timestamp: `lecture-notes/E1-evaluating-agents-aaron.md`, `lecture-notes/E2-E3-evals-parts-1-2-byron.md`.

---

## What the three lectures agree on, in one paragraph

An agent's output is a trajectory, not a string, so a green suite can hide a pass-for-the-wrong-reason. Keep a small must-pass core checked by code, a larger tagged set that is supposed to fail sometimes, and a holdout nobody tunes against. Grow the set from failures you found by reading traces yourself. Use the cheapest grader that can detect each failure; when you need a judge, make it binary and prove it agrees with humans. Decide before the first run what blocks a merge.

---

## GP-38 — Grade the trajectory, not just the answer

**Statement.** Measure both whether the agent got there and how. "Passed for the wrong reason" is a third result besides pass and fail, and it is the expensive one: on a dashboard it looks exactly like a real pass.

**Source.** Aaron, E1 [8:48–9:04]: *"these tests, they just check a final output… and what we really care about is the whole trajectory that made that output."* E1 [11:12–11:28]: *"in this case, we've got passed for the wrong reason, right?"* S-EA p.9: *"Outcome alone is how you ship a cheater. Trajectory alone is how you ship a beautiful process that returns garbage."* S-EA p.10: *"The third one is the expensive one, because it looks exactly like the first one on your dashboard."*

**In practice.** A Week 2 case asserts on the final answer *and* on the trace: the supervisor routed to the right worker, the lab worker called extraction before answering, every cited value came from a tool result.

**Builds on.** GP-20 (three layers of case) — adds that outcome and path are separate measurements.

---

## GP-39 — One run is an anecdote

**Statement.** The same input can take different paths, so run cases more than once and report a spread. Per-step errors compound over a trajectory, small sets carry wide error bars, and temperature 0 is not determinism.

**Source.** Aaron, E1 [9:52–10:24]: *"10 steps at 95% accuracy and you're only 60% likely to actually pass all those… 99% accurate, but 100 steps… about like 37."* E1 [22:36–22:44], on temperature 0: *"it does not make the model deterministic."* S-EA p.34: *"At n=10, a 90% pass rate carries roughly a 19 point margin… A four point move is noise wearing a lab coat."*

**In practice.** At n=50 a 90% score carries roughly ±8 points (same formula as the slide's n=10/30/100 figures; the n=50 value is our calculation). A 3-point move on one run proves nothing. AgentForge's own Week 1 result is the example: 30/36 at ×1, 13/36 at ×5.

**Builds on.** GP-21 — a baseline needs a spread before a change counts as an experiment.

---

## GP-40 — Two tiers: a must-pass core and a coverage set that should fail

**Statement.** A small golden set (10–20 cases) is a smoke test: every case passes on every commit, and one failure means something fundamental broke. A larger labelled coverage set (30–100+) is expected to fail sometimes; when it drifts toward 100%, add harder cases.

**Source.** Byron, E2 [24:25–24:46]: *"golden sets — should they all pass? Absolutely… These should pass every time. Behavioral coverage? No… We would expect there to be some failures and we'd hope there'd be some failures."* E2 [25:25–25:33]: *"if you start to get close to 100 it's time to start introducing some harder use cases."* S-EV p.13 (golden: 10–20, all must pass, every commit; labelled: 30–100+, every release). S-EV p.36 gives the cadence: commit → golden, release → labelled, weekly → replay, before shipping → rubric, on any change → experiment.

**In practice — Week 2 (corrected 2026-09-23 against the PRD and kickoff).** The issued contract fixes the gate: a **50-case golden set** with boolean rubric categories `schema_valid`, `citation_present`, `factually_consistent`, `safe_refusal` and `no_phi_in_logs`. The build fails if any category regresses by more than 5% or drops below its pass threshold, and graders plant a regression to confirm it (Week 2 PRD §6 and Hard Gate). The kickoff adds the coverage tier **on top of** the 50: *"we want 50 in your golden set and then we want more… some more labels, some more behavioral scenarios"* (kickoff 2:19–2:41; `../../inno-agentforce/docs/week2-kickoff-notes.md`). So Byron's two tiers map as: the PRD's 50 is the gated set, a labelled behavioural set sits alongside it, and safety categories (`safe_refusal`, `no_phi_in_logs`) take a pass threshold of 1.00 (GP-50). Watch GP-39: at n=50 a single run's noise (±8 points) exceeds the 5% regression threshold, so run the gate with repeats or on a fixed recorded baseline. *(Deck inconsistency on golden size: 10–20 on S-EV pp. 6, 9, 13; 10–15 on pp. 37, 39. The lecture says 10–20. The project says 50.)*

**Builds on.** GP-20.

---

## GP-41 — Use the cheapest grader that works

**Statement.** Graders form a ladder, and each rung costs more money, latency and trust: (1) assertion or exit code, (2) property/invariant check, (3) trajectory inspection, (4) LLM judge, (5) human label. Pick the lowest rung that detects the failure. Golden-set checks are code: right tool, right source, must-contain, must-not-contain.

**Source.** Aaron, E1 [13:56–14:36]: *"this is a hierarchy or a ladder of graders… you only want to climb this as you have to… if you can write an if statement with a hard-coded assertion… do that. That's fast. That's cheap."* E1 [25:40–25:48]: *"you want the cheapest grader that works."* Byron, E2 [10:06–10:21]: *"I don't need this to go to an LLM-as-a-judge and spend more tokens doing this every time because these are going to get run a lot… I can just do a static check."* S-EA p.16 (the ladder); S-EV p.8: *"Zero API cost. Zero ambiguity. Run after every commit."* Byron, E2 [9:37–9:45]: must-contain terms come from the source's own vocabulary. Aaron again in Advanced Graphs, G2 [28:00–28:48]: *"if you could do this, it's better programmatic verifiers… unit tests or deterministic conditions."* S-AG p.21: a judge that agreed with the unit tests on 12/12 cost *"~26× the cost of generating the candidates."* G2 [26:16–26:40]: if you can't score well, *"you probably shouldn't be doing this."*

**In practice.** Lab values (LOINC, value, unit) are graded by assertion. "Every claim cites a record id" and "no cross-patient data" are invariant checks. "Supervisor called the intake worker before answering" is trajectory inspection. Only groundedness that code cannot express reaches a judge — and never in the per-commit core.

**Builds on.** GP-16 (the *runtime* verification ladder) and GP-4. This is the *eval* ladder; it adds the invariant and trajectory rungs.

---

## GP-42 — Assert invariants on the parts that matter, not snapshots

**Statement.** A snapshot of statistical output fails on harmless changes, so it stops being a test. Replace it with narrow contracts: what must be present, what must be absent, and which known false positives must survive.

**Source.** Aaron (answering Innocent), E1 [49:28–50:08]: *"It was brittle. It was snapshot based… a lot of the time the snapshots change in a good way… it's not really a test at that point."* E1 [53:04–53:28]: *"I'm only enforcing those constraints on the pieces of the text that matter… patient name gone, right? Social security number gone."* E1 [56:32–56:48]: *"The evaluation I made was also deterministic. It was just… more tightly scoped to the bits that matter."*

**In practice.** Each lab-PDF or intake case lists the fields that must be extracted with their values, the values that must not appear (another patient, a hallucinated result), and the lookalike traps that must not be misread (a reference range read as a result). Migrate: hand-verify a few, let an LLM convert the rest few-shot, skim the output (E1 [52:24–53:04]).

**Builds on.** GP-20.

---

## GP-43 — Tag every case and read the coverage matrix

**Statement.** Label each case by category, subcategory and difficulty (straightforward / ambiguous / edge). Tags don't change how a case runs; they change what the results tell you. A category × difficulty matrix shows empty cells (missing tests) and red cells (failures). Keep one dataset per category so a failure points at its cause, and rerun a failing cell before calling it real.

**Source.** Byron, E2 [17:04–17:36]: *"this map is actually really helpful because it does show you where some gaps are."* E2 [17:54–18:05]: *"We ran it once, but these are LLMs… is it consistently failing and why?"* E2 [19:54–20:24]: *"I made this mistake early on where I would put all my tool calls in just one data set… when one or two of them broke I was left to figure out… which one is it?"* S-EV p.11: *"The tags don't change how the test runs — they change what the results tell you."*

**In practice.** Tag the 50 cases by worker (lab extraction, intake extraction, retrieval, supervisor routing), by input quality (clean, scanned, handwritten) and by difficulty. The report prints the matrix: "supervisor-routing × ambiguous: 1/3", not "47/50".

**Builds on.** GP-20, GP-22.

---

## GP-44 — Error analysis: read traces, log the first failure, then categorise

**Statement.** Read a representative sample of real traces yourself — ideally with a domain expert. Write one open-ended note per trace about the *first* failure only; everything after it is contaminated. Categorise only after the reading pass, into a taxonomy in your own words. Each category becomes a grader and a dataset. Don't hand the first pass to an LLM: it finds only what you knew to ask about, and it reports symptoms instead of causes.

**Source.** Byron, E2 [6:10–6:20]: *"If I'm going to take one thing away from this whole series of topics… I would take away error analysis."* E2 [40:48–41:05]: *"focus on the first failure. As soon as you see one failure in the trace, stop… everything after that, the bets are off."* E2 [53:54–54:16]: *"the AIs don't always know what to look for… I wouldn't have known to prompt it to look for that."* Aaron, E1 [36:24–36:56]: *"group your failures into types… the taxonomy is then how you inform… what mitigation you're using."* E1 [44:16–44:40]: *"read traces. Don't just trust the numbers."* S-EA p.13: *"Twenty traces is usually enough for the first pass."* S-EA p.14: published taxonomies — *"Borrow the shape. Write your own contents."*

**In practice.** Before writing Week 2 graders, read ~20 traces across the lab-PDF, intake and RAG paths and commit the tag table (`wrong_unit_extracted`, `cited_nonexistent_chunk`, `routed_to_wrong_worker`, `answered_without_retrieval`). For long supervisor traces, start from what the clinician saw and work backwards (E2 [58:49–59:11]). Byron's "we processed zero refunds" when there was no data (E2 [49:12–49:56]) has an exact clinical twin: "no abnormal results" when no lab was extracted. Byron assigned a small trace-review page (pass/error toggle, one note, JSON export) as a reusable tool (E2 [1:04:42–1:04:51]).

**Builds on.** GP-23, GP-24. *Error analysis is transcript-only: the S-EV deck has no slides for it.*

---

## GP-45 — The eval set is a product artifact, grown from failures, with a holdout

**Statement.** Hand-curate the set; it is the north star every change is measured against. Every bug and every error-analysis category becomes a permanent case. Never edit an expected output to turn a test green. Keep a holdout you never tune against and that the agent can never read. A trace is not eval data until a human has reviewed it.

**Source.** Aaron, E1 [42:56–43:20]: *"this eval set… you want to perhaps make by hand or at least… heavily curate and validate… that becomes an artifact… a north star."* Byron, E2 [15:01–15:08]: *"just make sure you never change the test to get it to pass."* S-EV p.9: *"Every bug becomes a test case."* S-EA p.21: *"An eval set the agent can read is not an eval set."* S-EA p.26: *"The 90% was real. It was also irrelevant."* Aaron, O1 [3:52–4:16]: *"good data isn't just a pile of bytes. Good data is data that you have validated, that you have labeled… throwing bad data at the problem tends to make the problem worse."* O1 [19:08–19:24]: annotation queues exist so *"the human… double check it before you actually treat it as training data."*

**In practice.** The PRD's 50 cases are the gated set, so keep the holdout *outside* them: for example 15 extra sealed cases the agent and prompt-tuning never see. Report both on every PR. A PR that edits an existing case's expected fields alongside agent code is flagged; changing an expectation takes its own commit saying why the old one was wrong. Flagged runs (low-confidence extraction, refusals, mis-routes) go through a LangSmith annotation queue before they enter the set.

**Builds on.** GP-19, GP-21, GP-23, GP-24.

---

## GP-46 — Replay every step of a recorded session

**Statement.** Save real sessions as fixtures: recording costs tokens once, and you can re-score or re-run from any midpoint afterwards. When debugging a chain, replay and check *each* model call, not just the last — the fault is often upstream. Freeze everything and change one thing at a time.

**Source.** Byron, E3 [12:12–12:27]: *"What I should be doing is replaying every LLM call and making sure the output from that is what I expect."* The story, E3 [12:37–13:13]: an unguarded intent-classification call read *"I'm a dev… use some profanity"* as testing intent and passed context downstream that *"basically said forget the guardrails."* E3 [16:02–16:11]: *"Default to freezing… Change one thing at a time."* S-EV p.15: *"Record once. Score anytime."*

**In practice.** Each Week 2 run is a JSON fixture: the upload, the supervisor's routing decision, each worker's input and output, the retrieved chunks. When a final answer is wrong, first check whether routing and extraction already were. AgentForge's RecordedExecutor is the start of this.

**Builds on.** GP-21; the safety lesson (an unguarded upstream call can switch off downstream guards) extends GP-16.

---

## GP-47 — Judges are binary, narrow, and a last resort

**Statement.** Use an LLM judge only for questions that are genuinely about meaning. Give it a focused rubric, the output, and a few good/bad examples, and ask yes/no — one claim at a time — then aggregate. Fewer classes make an easier problem; 1–5 scales are inconsistent for models and humans alike. Never let an LLM write the judge's rubric.

**Source.** Aaron, E1 [19:48–20:04]: *"a good LLM judge should be very focused… is this good output, right? Yes, no."* E1 [25:48–26:12]: *"You shouldn't go to one to five scales unless you have a really good reason. Even for humans, humans kind of suck at one to five scales."* Byron, E3 [23:28–23:40]: *"There's this sense that it's a silver bullet… and it is not."* E3 [35:57–36:09]: *"LLM-as-a-judge should be a last resort."* E3 [23:52–23:58]: *"you do not want to leave the LLM-as-a-judge rubric to an LLM."* S-EV p.18: *"The judge makes a binary call per claim, then aggregates into a groundedness score."*

**In practice.** Groundedness: split the answer into claims, ask "does source X support claim Y — yes/no" per claim, report the supported fraction. Checks code can do (value present, citation id exists, unit correct) never reach the judge.

**Builds on.** GP-16.

---

## GP-48 — A judge is trusted only after it agrees with humans

**Statement.** Before a judge's scores count, a human scores a sample against the rubric and the judge scores the same cases blind. Low agreement means the rubric is broken: fix it and repeat. Report two numbers — real failures caught and real successes cleared — because a judge that flags everything scores perfectly on the first. Expect uncalibrated judges to be generous, and recalibrate when the judge prompt or model changes.

**Source.** Byron, E3 [25:12–25:39]: *"we actually have a human scoring everything… And then we… have the LLM do the same thing without knowing what the human said."* E3 [25:56–26:08]: *"they tend to be a little overly optimistic."* E3 [47:15–47:31]: *"an eval of your eval."* Aaron, E1 [39:04–39:28]: *"we see whether or not the human and the judge agree."* S-EV p.19: *"If < 0.8, your rubric is broken — fix it before trusting the judge."* S-EA p.18: *"A judge that flags everything scores 100% on the first and is worthless."*

**In practice.** Commit `judge_calibration.jsonl` — ~20 hand-scored Week 2 answers — next to the judge prompt. CI re-runs calibration when the judge prompt or model changes and fails below 0.8 agreement.

**Which model judges.** The lecturers differ. Aaron: the judge's job is small, so *"just reach for the big one"* and run the agent on a mid/small model (E1 [29:40–30:12]). Byron: a cheaper model can judge, and a different family is optional (E3 [38:46–39:10]). **Resolution:** start with the stronger model; any model that passes calibration is acceptable, and cost decides among those.

**Builds on.** GP-16.

---

## GP-49 — Rubric criteria are narrow, anchored, falsifiable and expert-written

**Statement.** A criterion is done when you can write one example that clearly passes and one that clearly fails. Every score point has a written anchor, scales stay small, and narrow single-aspect criteria beat a general "quality" score. The domain expert defines good; the engineer coaches them to be narrow and concrete.

**Source.** Byron, E3 [40:03–40:26]: *"the narrower the better… we're doing a medical app and we don't have medical personnel next to us, but if we did, that's the person who should be making this rubric, right? Not us."* E3 [43:00–43:24]: *"if you get big — seven, 10 — beyond, there's too much of splitting hairs."* S-EV p.23: *"No anchor = no consistency."* S-EV p.32: *"A criterion is done when you can write a concrete example that unambiguously passes and one that unambiguously fails."* Anti-patterns named on S-EV pp. 29–31: the Likert trap, vague criteria, ambiguous ranges.

**In practice.** "Clinically safe summary" becomes separate criteria — "every abnormal lab value is stated with its reference range", "no medication is recommended" — each with a pass and a fail example from a synthetic chart. With no clinician available, name the published guideline standing in for the expert (the Week 2 source manifest already holds them).

**Builds on.** GP-16, GP-24.

---

## GP-50 — Decide what blocks before the first run

**Statement.** A suite that blocks nothing is a dashboard. Track each dimension as its own trend line, and decide in advance which score or drop on which dimension blocks a merge, triggers investigation, or routes to a human. Safety-shaped checks get a floor of 1.00. A baseline defined after you have been running on gut is hard to set and easy to argue away.

**Source.** Aaron, E1 [42:24–43:04]: *"we want to… actually have blocking moments here… to actually block… some code going out or some decision from happening, and possibly feed it back, possibly route it for human review."* S-EA p.33: `GATE = {"holdout tests pass": 0.85, "tests unmodified": 1.00, "no input special-casing": 1.00}` — *"Safety-shaped checks get a floor of 1.00."* Byron, E3 [44:58–45:24]: *"track each one of these individually… when is this problematic enough for us to have to go in and figure it out."* E3 [48:42–48:55]: *"If you don't start with evals and you just go by gut, then you have to define the baseline on the fly. And that can be really hard."*

**In practice.** The Week 2 CI gate reads a committed threshold table. Safety at 1.00: no cross-patient data, no uncited clinical claim, no write outside OpenEMR's paths. Quality floors set with GP-39's error bars in mind. The PRD fixes the regression rule itself: any category down more than 5%, or below its threshold, fails the build. Latency and cost are reported, not blocking. Floors go in `KEY_METRICS.md` before the first run.

**Builds on.** GP-21, GP-22.

---

## GP-51 — One variable per experiment, on a fixed set, with cost in the table

**Statement.** Every candidate change is an experiment: change one variable, run the same set, and put pass rate, rubric score, latency and cost side by side. Prompts are versioned files, so every result traces to an exact prompt. The biggest payoff is judging model swaps, in both directions.

**Source.** Byron, E3 [57:32–57:49]: *"one variable at a time. We're using the scientific method here."* E3 [59:12–59:23]: *"I wouldn't change multiple things in the prompt and change the sources you're pulling things from."* E2 [22:54–23:18]: a switch to a cheaper model with no evals *"straight up broke… A golden data set would have solved that problem."* S-EV p.27: *"6% quality gain at 5× cost may not be worth it."* Aaron, G2 [34:12–34:52]: *"This agent is 98.9% accurate and cost 10 times less. That's good enough."* G2 [35:16–36:04]: model families fail differently, so audition several and *"always narrow it down to one."* S-AG p.21: *"3 of 4 models failed the same subtle… edge case; a different family got it right."*

**In practice.** Before fixing a worker's model, audition three or four candidates through OpenRouter on the golden set, pick on accuracy × cost × p95, record the audition, and hard-code the winner — no runtime tournament. Prompts live under git. The eval runner writes one row per variant (pass %, rubric, p50/p95, $/case). A model-swap PR's description is that table. AgentForge's run-metadata gate — `compare` refuses runs whose metadata differs — already enforces the fixed-set half.

**Builds on.** GP-21.

---

## GP-52 — Every model call gets its own eval, built upstream first

**Statement.** In a multi-call workflow, each model call gets its own eval, built in pipeline order because each step's output is the next step's input. Test a change against the evals nearest the step you changed, then confirm the gain reaches the final output; if it doesn't, something downstream is undoing it.

**Source.** Byron (answering Innocent), E3 [53:16–54:09]: *"if I have a workflow that has five calls, every LLM call gets an eval. And the way I would build it is I would start with the first one and eval that one before I would eval the second one."* E3 [54:50–55:10]: *"I improved this by 10 percentage points. Well, that's great, but does it actually result in something better at the end?"*

**In practice.** Build Week 2 evals in order: supervisor routing → each worker's extraction (field-level exact match) → retrieval (precision/recall) → final answer (groundedness). A PR that improves the extractor also shows the final-answer score didn't drop.

**Builds on.** GP-22.

---

## GP-53 — Write the cases before the prompt, and expect the first honest score to be low

**Statement.** Writing cases first forces you to define "good" — a TDD opportunity. Cases can be AI-drafted but must be closely human-reviewed; the PRD is a natural place to draft them. Evals written after the fact routinely show the system is much worse than it felt.

**Source.** Byron, E2 [32:12–32:38]: *"I do find this helpful actually to write it before I write the prompt… So there is kind of like a TDD opportunity there."* E2 [32:50–33:07]: *"every time that I've written the eval after the fact, the results are dramatically worse than what I thought… To the tune of like 30% accuracy."*

**In practice.** Draft the Week 2 golden cases from the PRD on day 1, before the extraction prompts exist, and hand-check each expected value against its source PDF. A low first score is the baseline, not a failure.

**Builds on.** GP-19.

---

## GP-54 — Fix the environment before the prompt; a fence is not a fix

**Statement.** A prompt instruction is a request; a tool-layer constraint is a wall. Fix failures in the tools and environment first and use the prompt for what tools can't express. A guardrail that blocks damage doesn't stop the attempt, so measure attempts and successes separately.

**Source.** Aaron, E1 [38:16–38:32]: *"you can tell your LLM nicely, please don't edit tests. But again, that's not a hard guarantee. So you might want to actually look into sandboxing permissions, making it impossible."* E1 [45:04–45:20]: *"This isn't to say you never edit the prompt, but don't necessarily go to the prompt first."* S-EA p.27: *"One of these is a request. The other is a wall."* S-EA p.29: tamper attempts stayed at 70% → 70% after the guardrail. S-EA p.30: *"Measure attempts and successes separately."*

**In practice.** Patient scoping, write-back limits and PHI boundaries stay in the tool layer. Log refused tool calls as attempts and track "attempted out-of-scope access" beside "leaked data", so a guardrail that only hides a behaviour stays visible. This also feeds Week 3.

**Builds on.** GP-11.

---

## GP-55 — When an agent writes the code, a human reads the tests

**Statement.** In a "loop until green" workflow the tests matter more than the implementation. A wrong, trivial or hard-coded test — or one the agent quietly edited — turns "all green" into a false signal.

**Source.** Aaron, E1 [3:04–3:12]: *"with an LLM, you review the tests yourself because that's almost more important than the application code."* E1 [7:04–7:20]: *"Do you really read everything Claude responds to you?… every cohort we see students definitely… accidentally ship test changes still."* S-EA p.24 names the modes: `test_tampering`, `input_special_casing`, `stopped_unverified`.

**In practice.** Frozen tests get a human read before any builder runs; builders can't write test paths; any diff touching `tests/` or `evals/` (golden files included) is flagged at merge.

**Builds on.** New — GP-19 – GP-24 cover the product's evals, not the build loop's own tests.
