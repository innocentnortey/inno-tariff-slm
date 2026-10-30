# Problem Framing — GP-120 to GP-130

How to find the real problem behind a brief before building anything. The other principle files say
how to build well; these say how to know you are building the right thing. They apply at Stage 1
(Frame) of `zero-to-hero`, whenever a PRD or partner brief arrives, and again whenever a metric or
a design choice cannot be traced back to a business reason.

**Source and its weight.**

| Code | Source | Weight |
|---|---|---|
| **BP** | `transcripts/identifying-business-problems-transcript.md`: a ~58-minute cohort session on identifying business problems (Steve Jobs's iPhone launch clip, the elevator-mirrors story, a "keep asking why" method, a worked observability example, and a ten-minute group exercise). Auto-captions. **The host is not named in the captions**; the session reads as staff-run, with cohort members (Taylor, Ban, Zach, Michael, Innocent) answering. | Strong evidence for *what Gauntlet wants from us on hiring-partner projects*. Cohort answers are peer opinion and are labelled as such. Anecdotes (the elevator, the laid-off engineer, the Langfuse migration) are told secondhand or from memory, so use them as illustrations, not as proof. |

**Not in this lecture.** The Week 2 intro (`intro-to-week-2-project.md` [3:32–3:47]) asks for
*"leading and lagging indicators"* to tell success from drift. This lecture never defines them; it
only says to pick a north-star metric (GP-127). They are defined in `business-metrics.md`
(GP-133, GP-134), which also covers how to choose the metrics around the north star (GP-131 – GP-144).

Citation format: `BP [8:18]` = transcript timestamp (minutes:seconds). Quotes are cleaned for
readability (fillers removed), never for meaning.

---

## GP-120 — As implementation gets cheaper, planning has to get longer

**Statement.** Writing the code is now the short part. The time freed up belongs to working out what to build, because a fast build of the wrong thing is still the wrong thing.

**Source.** Host, BP [1:01–1:16]: *"the time to implement has shrunk so much that… the time to plan naturally has to increase so that we can ensure that what we're building is actually what we want."* BP [13:44–14:07]: *"The implementation is so short. We can have more time to plan, more time to think about these questions and make a better solution… if we just build for build's sake and we're just building what we're being told… we're just engineers in the hub and someone tosses something over the fence and we just do it… Those days are gone."* BP [56:10–56:16]: *"Build the implementation of code is so cheap."* Innocent (cohort), BP [42:08–42:33]: we used to feel *"we're not allowed to ask that many questions… implementation is so much shorter that we really want to make sure we get it right."* The host answered: *"there always are tons of questions we can ask."*

**In practice.** Stage 1 is real work with a signed-off artifact, not a formality before the tickets. The time a team once spent coding is the time we spend on the brief audit, the why-chain (GP-124) and the metrics tree (GP-127). If a project is a 1–2 day time box, the plan still gets its share; the build is what shrinks.

**Raise at Stage 1.**
- What would we have built if we had taken the brief literally, and what did the audit change?
- How much of the time box is going to understanding versus typing?

---

## GP-121 — A PRD is someone's answer to a problem; find the problem

**Statement.** The brief tells you the solution the partner already chose. Your job is to work out which problem they were solving and whether that solution is the best one.

**Source.** Host, BP [10:54–11:11]: *"the PRDs that you guys get are someone's answer to a problem. But I would like to challenge all of you to really dig behind why this is their answer. What's the real problem we're trying to solve here?"* BP [13:08–13:28]: *"take a moment and really stop and ask why is this the solution they come up with? What are they actually trying to solve… Research the company, see what they're doing, see how this PRD relates to their customers and try to understand where their customers are coming from. If you can identify the core issue, then… the solution can change and you can address it."* BP [56:01–56:10]: *"these companies are just giving you solutions… There's an underlying question there. They want to see if you can actually find and identify what the real problem is that's going to provide more value to their customers."*

**In practice.** The brief audit (`docs/analysis/…-brief-audit.md`) opens with a section **"The problem behind this brief"**: the partner's stated solution, the problem we believe it answers, the customer it serves, and the evidence for that belief (company research, customer-facing pages). It is separate from the traps list, and a partner's grader is reading for it. Never present the build as a feature list (this sits underneath `hiring-partner-framing`'s two layers: layer 2 is what this principle finds).

**Raise at Stage 1.**
- In one sentence, what problem is the partner solving for *their* customer?
- If the brief's solution did not exist, what would the partner's customer do instead?

---

## GP-122 — Question the assumption hidden inside the question

**Statement.** The question you were handed often rests on an unexamined assumption. Ask whether the assumption is needed before you work on answering the question.

**Source.** Host, BP [8:18–8:35], on the iPhone launch: *"How do we fit a keyboard into a phone? That was the question. And then he comes back and goes, why does a phone need a keyboard in the first place?"* BP [6:22–6:44]: Jobs *"questioned some assumptions… why we have a keyboard… why do we need a stylus… by asking those questions and digging a little bit more into why we do these things in the first place."* Taylor (cohort), BP [9:03–9:16], did this work in education leadership and taught design thinking. Host, BP [9:45–10:08]: a principal he follows *"has done away with lesson plans… why do we even have it in the first place?"* BP [10:34–10:46]: a chat comment named annual employee reviews, and the host agreed: *"why do I have to wait till 12 months to know how I'm doing?"* Host, BP [10:27–10:34]: even where there is a reason (*"red tape… usually because someone broke something before"*), *"it still warrants the question. No one should get mad about asking that question."* BP [44:44–44:55]: a co-worker who would stop and say *"you just said these words and I don't know what you mean"*: *"I had a lot of respect for him there."*

**In practice.** For each requirement, constraint and "must" in the brief, write the assumption it rests on in one line and mark it *needed*, *probably needed* or *question it*. Anything marked *question it* goes to Innocent as options, never silently dropped (a brief's hard requirements are not ours to waive; see the brief-conformance check in the project). Asking a "dumb" question is part of the job: a term you cannot define is a gap, and it goes in the open questions.

**Raise at Stage 1.**
- Which sentence in the brief assumes something nobody has justified?
- If that assumption were false, would the requirement still stand?

---

## GP-123 — What people complain about is a symptom; observe before you fix

**Statement.** The complaint names a symptom, not the cause. Watch what is really happening first, because the best fix may be different from, and cheaper than, the one requested.

**Source.** Host, BP [11:16–12:38]: office workers complained the elevators were too slow; the company wanted faster elevators or more of them. Someone first *"just sat and watched people go in and out of these elevators every day"*, then proposed **mirrors**: *"as soon as you walk in… you look at yourself… next thing you know, the door's open and you're there. And people stopped complaining."* BP [12:42–13:03]: *"It's not that we hate… we see something and we say this is what we don't like about this, but that's not always the problem. There's something else underlying that's really the problem. And there's a different solution than attacking what the customer necessarily says."* BP [22:02–22:48]: the why-chain on the elevator (*are they minding the speed, or are they impatient? if we take their attention off it, does that solve it?*).

**In practice.** This is the same instinct as Stage 2 (look at real data): before accepting "make X faster / more accurate / more automated", look at the real behaviour behind it, whether that is real samples, real user logs or the partner's public product. Record "what the complaint was → what we observed → what we think is underneath" in the brief audit. A fix that changes the *experience* of the problem (the mirrors) is a legitimate option to put next to one that removes it.

**Raise at Stage 1.**
- What would we see if we watched a real user hit this problem?
- Is there a cheaper change that makes the pain go away without solving the stated problem?

---

## GP-124 — Keep asking why until the answer is obvious

**Statement.** One "why" gets you the reason; five get you the cause. Stop when the answer is obvious, and at the same time check the alternatives you skipped on the way down.

**Source.** Host, BP [21:42–21:57]: *"here's one way of doing it. You keep asking why, and then you ask why, and you ask why, and you keep going until you hit a point where you're going, I think we found it. And it should become pretty obvious when you get to that point."* It is **not the only method**, per the host. Worked example, BP [24:34–28:34] (host's previous company): the observability platform (Langfuse) was slow, errors piled up, error analysis was blocked; the first instinct was to *swap to another vendor*. The tech lead asked *why is slow a problem?* (we can't get data fast enough) → *why do we send the data out at all?* (we could own it) → *why not just try Postgres?* (it bogged down the database; tried and failed) → an OLAP database in-house. Outcome as told: *"we saved money. We got faster responses. We were able to do a lot more error analysis."* The chain to the business: *platform was slow → engineers wait on every incident → incidents resolve slower → revenue bleeds every hour* (BP [28:10–28:22]). A cohort answer that gets the same treatment: *"it improves productivity" → why?* (BP [54:46–55:18]).

**In practice.** The brief audit contains a **why-chain**: the stated problem at the top, each "why?" below it with its answer and its evidence, ending at a cause we can build against and a link to money or customer value (GP-126). Write down where the chain forked (the vendor swap versus in-house) so the rejected branch is on record. If a link has no evidence, label it an assumption (GP-129). The test for stopping: the last answer is something we could change, measure and explain to the partner in a sentence.

**Raise at Stage 1.**
- What is the fifth "why" here, and is it something we can act on?
- At which "why" did the obvious fix stop being obvious?

---

## GP-125 — Decide the level you are asking "why" at

**Statement.** The same problem looks different at the team, department and company level. Say which one you are working at, or the why-chain wanders.

**Source.** Taylor (cohort), BP [43:52–44:34]: *"the challenge is a matter of granularity… are we talking about just this team? Are we talking about this department? Are we talking about this whole company in general, and finding where you can ask the question versus you hit that wall or that ceiling."* The host's reply (BP [44:34–44:44]): *"How deep do you go? There's always you want to find those answers."* Innocent, BP [45:48–47:09], on the exercise ("more AI workflows needed, few engineers know how, they are bottlenecked"): the problem *"replicates a system design problem"*: why are so many requests going to these engineers, what justifies delegating to them, what infrastructure are we giving them and the other staff. The host's contrast (BP [47:09–47:37]): in system design the end goal is clear; in an organisation's problems it often isn't, so these questions *"help demystify"* it.

**In practice.** Open each why-chain with a scope line: *"scope: the partner's [team / product / company]; customer: [who]"*. When the answer to a "why" lives at a higher level than the one we can affect, write that down as context and move the chain back to the level the project can change. This is what keeps a time-boxed build from trying to solve the partner's whole business.

**Raise at Stage 1.**
- Which level can this project actually change?
- Which "why" answers sit above that level, and are they context or constraints?

---

## GP-126 — Tie the work to the money, in as many hops as it takes

**Statement.** The closer your work is to revenue or cost, the easier it is to justify. If you cannot trace what you do to the bottom line, you cannot defend it. It may take several hops, and a hop through customer behaviour (retention, drop-off) is legitimate.

**Source.** Host, BP [14:48–16:25]: asked what every business needs, he answered *money*: *"if your company cannot bring in revenue and be sustaining, the business is gone."* Real problems are things that stop money coming in: revenue falling, costs too high, growth blocked. *"The closer you can be to the money, the more valuable you are. If you can't justify what you're doing to the company's bottom line, that's a problem."* BP [16:43–18:24], the founding engineer let go in a layoff although respected and expert, *"because when it came down to how we make money as a business, they could not tie what I did directly to our revenue."* BP [18:17–18:24]: *"We're trying to tie what we do to the bottom line."* The qualifier, BP [20:29–21:31], answering a cohort member's question: it is *not* always revenue. A long-latency feature that makes customers drop off has the north star *get them through that feature*; *"there's almost always going to be a way to tie that to some sort of revenue, and it might take a couple hops to get there."* BP [19:38–19:52]: valid payoffs include fewer LLM calls (lower token cost), more customers, or more value to the customers.

**In practice.** Every metric on the tree carries a one-line **hop chain** to money or customer value: *latency ↓ → fewer drop-offs → more completed orders → revenue*. A chain longer than three hops, or one that skips a step with no evidence, is flagged. The three families the lecture names (more revenue, lower cost, more customer value) are the top of every tree; a metric that fits none of them is cut or explained.

**Raise at Stage 1.**
- Which of revenue, cost or customer value does each metric move, and through which hops?
- Which hop in the chain are we least sure about?

---

## GP-127 — Name the north-star metric before building; it is how you will know

**Statement.** Decide up front which metric will tell you the solution works. Then judge the result against that metric, not against how much was built.

**Source.** Host, BP [13:34–13:46]: *"how do we know that we are solving the problem? Because this is the key metric I'm looking at and this is what I'm going to judge my results based on."* BP [19:22–19:38]: you will be asked for *"north star metrics that say this is going to increase customer retention. Customers are going to like this feature for these reasons."* BP [56:21–56:33]: *"what's going to be that north star that's going to say this is how I know this is working. This is how I know this solution is actually providing the right value."* The example BP [23:33–24:04]: a cohort member cited Netflix's north star as *minutes streamed, not subscribers*, with competitors being *anything that attracts our eyeballs*. The host called it *"an interesting north star metric"*, while noting it can feel inhumane. A cohort question from the exercise, BP [53:16]: *"what metrics do we plan for these supposedly improved [workflows]?"*

**In practice.** The one north star is written into the PRD before any ticket and shown on the success surface (this is the root of the `hiring-partner-framing` metrics tree). It must be measurable from data the system actually stores. It gets a *before* number or an honest "no baseline", never an invented one. It also gets a **guard**: a number that would show we improved the north star by harming something else. The Week 2 intro asks for leading and lagging indicators on top of this; they sit below the north star on the same tree, and `business-metrics.md` (GP-133, GP-139) defines them and the supporting metrics.

**Raise at Stage 1.**
- What is the single number that moves if this works, and where is it stored?
- What would we see if it got better for the wrong reason?

---

## GP-128 — More output is not more value; count only what keeps being used

**Statement.** Producing more of a thing (workflows, features, reports) proves nothing. The test is whether people keep using it. Pick the ones worth building, and make the path to adoption standard.

**Source.** Ban (cohort), BP [42:46–43:15]: *"the bottleneck isn't necessarily the number of engineers, but rather the number of workflows that are still continuously used. There is no standardized process to set up a workflow that people will continue to use… it becomes obsolete, and that's wasted the engineer's time and whoever is using that workflow."* Host, BP [43:15–43:46], agreeing: he has built many workflows he never used. *"It's a signal to me that there's no value here. That's not where I place my value, even though it seems like the right thing I should do… doesn't mean every workflow is the same. So it's identifying which ones are the most valuable."* BP [55:41–55:49]: productivity tools *"if used wrong can all decrease productivity."* BP [52:26–52:44], the host's answer to the exercise's bottleneck: teach non-engineers to write *skills* so they build their own workflows; BP [54:22–54:33]: *harnesses* so one expert engineer stays on one and others build elsewhere.

**In practice.** Do not measure a build by what shipped. The success surface for a feature shows *use over time* (does the second week look like the first?), and a feature with no usage signal is on the cut list. When the brief's request is "build more X", ask what makes an X worth keeping and who chooses which to build; that question is usually the real problem. It also applies to our own tooling: a scheduled job or dashboard nobody looks at is a cost, not an asset.

**Raise at Stage 1.**
- How will we know, a month from now, that people still use this?
- Which of the things we plan to build would nobody miss?

---

## GP-129 — When you cannot ask the partner, research, label the guess, and test it

**Statement.** You will often have no way to ask the people who wrote the brief. Do the research you can, mark every inference as an inference, and use building and trying as a way to find out.

**Source.** James (cohort, in the chat) and the host, BP [45:05–45:36]: *"there are a lot of unknowns without getting feedback and answers from this company. So we're just guessing."* Host: *"you are. In this exercise you definitely are. But you don't always have that available either. You're going to look up these companies, you're going to get an idea of what they're doing, but you're not going to know for sure. You might do some extra research and you might just have to take your best guess… And sometimes you just have to try things. See if it breaks."* BP [13:12–13:17]: *"Research the company, see what they're doing."*

**In practice.** This is where the defensibility rules apply: every belief about the partner's customer or business is recorded as an assumption with its source and how it could be checked (a decision log row), never stated as fact. Cheap trials are legitimate evidence, so a small spike that confirms or kills an assumption gets recorded the same way. The interview answer is "I could not confirm this, so I treated it as X, here is why, and here is what would change my mind."

**Raise at Stage 1.**
- Which parts of our picture of the partner's customer are guesses?
- What is the cheapest thing we could try to turn one guess into evidence?

---

## GP-130 — The engineer's job now includes owning the "why"

**Statement.** The old role of taking a spec and building it is gone. The engineer is expected to think about problems at a higher level: why we are doing this, and how it affects the business. Anyone can build; the differentiator is picking and justifying the right problem.

**Source.** Host, BP [14:07–14:17]: *"It is our job to ask these questions, to be the problem solvers, to be those thinkers."* BP [56:10–56:21]: *"Everybody can build these days… The implementation of code is so cheap. So what value are you going to bring to this? What are you going to add to this problem? What are you going to identify in this problem is the real issue here?"* BP [57:28–57:57]: *"Our old role as engineers is gone. There's no coming back to what we used to do. It is this new role that we're in. And it requires us to be thinking about problems in a higher way so we can understand why we're actually doing what we're doing and how it impacts our business."* BP [2:03–2:34]: *"we're all looking for problem solvers… something that is difficult… is solving the right problem and digging into a problem until we can really find the reason behind it."* And the practice requirement, BP [18:46–19:09]: *"It's not something you read about… It's a skill. It's a muscle. So you've got to practice this over and over again,"* which the hiring-partner projects supply. For anyone who has only been an individual contributor, BP [57:02–57:23]: ask the cohort members who have led teams how this works.

**In practice.** This is the grading lens for hiring-partner projects: the demo, the write-up and the interview open with the problem we found and the value it protects, then show the build. It is the reason `hiring-partner-framing` leads with layer 2. For Innocent, the interview version is a short story: *brief said X → we found Y → so we built Z → the metric moves because…*

**Raise at Stage 1.**
- Could a stranger read our write-up and say what problem we chose, and why that one?
- What did we decide *not* to build because of the problem we found?
