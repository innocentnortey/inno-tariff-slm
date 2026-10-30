# Business Metrics — GP-131 to GP-144

How to choose the numbers that prove a thing we built is worth having. `problem-framing.md`
(GP-120 – GP-130) says to find the real problem and name a north star; this file says how to pick
that north star and the metrics around it, how to tell a useful metric from a flattering one, and
how to set and revise targets. It applies at Stage 1 (success framing and metrics tree), when
`KEY_METRICS.md` is written, and again when a dashboard or success surface is designed.

**Source and its weight.**

| Code | Source | Weight |
|---|---|---|
| **DM** | `transcripts/defining-business-metrics.md`: a ~60-minute cohort session on defining business metrics (terms, a two-part group exercise on a fake grocery-delivery app "Crate Fresh" and a fake email assistant "Desk Pilot", then a north-star discussion). Auto-captions, no speaker labels. **The host is presumably Byron Mackay (staff)**: a participant addresses him as "Byron" at ~15:39 and he hands off to "Aaron" at the end; unconfirmed (GQ-25). He says he is *"not an expert by any stretch of defining metrics"* [3:34]. | Strong evidence for *what Gauntlet expects when it asks for key metrics*, and for how the interviews will challenge them [44:02–44:28]. Cohort answers (Zach, Michael, Joshua, Joe, Nicholas, Kell, Taylor, Charlie, Brian, James, Rolando, Jesse, Nathan, Innocent) are peer opinion and labelled as such. The two slide decks (the five and the nine metrics) were screenshots sent to Slack and are **not captured**. |

**Cross-references.** GP-126 / GP-127 (`problem-framing.md`) say to tie work to money and to name a
north star before building. This file extends them. The Week 2 intro's request for *"leading and
lagging indicators"* (`intro-to-week-2-project.md` [3:32–3:47]) is defined here, in GP-133 and
GP-134.

Citation format: `DM [6:20]` = transcript timestamp (minutes:seconds). Quotes are cleaned for
readability (fillers removed), never for meaning.

---

## GP-131 — If you cannot prove it with a number, it is a good feeling, not a result

**Statement.** Building is cheap, so the differentiator is showing a business person that what you built worked. That means a number whose movement tells them yes or no. Engineers who can do this are worth far more.

**Source.** Host, DM [1:20–1:50]: *"we have to identify metrics that prove that what we're building is actually worthwhile. It has to prove to a business person that yes indeed if this number changes we know we're successful and/or unsuccessful… then the idea becomes much more viable… and we can point to the numbers and it's not just this good feeling thing that hey we deployed something."* DM [1:54–2:17]: *"deploying is so cheap these days we can deploy anything, we can build anything, but how do we make sure that what we're building is provable?… our hiring partners ask again and again… they need people who are thinking in terms of actually providing value, not just building."* DM [3:06–3:15]: *"When an engineer does know how to do this and does this well, the value of that engineer goes up tremendously."* Close, DM [59:46–1:00:15]: it *"shows that you're not just a builder. And quite frankly building is the easy part these days… we can not only build, we can define what success is, and one way we can do that effectively is by defining good metrics and telling a good story."*

**In practice.** Every claim in a demo, write-up or interview answer ("it's faster", "it's more accurate", "users like it") is followed by the number that shows it, where it is stored, and the comparison it is measured against. A claim with no number is labelled as an opinion.

**Raise at Stage 1.**
- If this works, which number changes, and by how much would a business person need to see it move?
- What do we say in the interview if we have no number?

---

## GP-132 — Telemetry shows the system runs; it does not show the system is worth running

**Statement.** Engineers have plenty of metrics for health (error rates, latency, failures). The harder, more valuable metrics measure whether the customer got value. Both are needed, and the first never substitutes for the second.

**Source.** Host, DM [4:10–4:57]: the technical side — *"How do we ensure that this is running and running effectively? … Datadog… error rates, latency, where things are breaking."* DM [4:57–5:16]: the other side *"is often a little more opaque… how do we actually measure if this is providing value to the customer aside from just asking them? And even that can be a grayish area."* DM [5:16–5:45], the strongest signal is *"Do they pay for it?"*, with the caveat that a subscriber can pay every month and never use the product. DM [5:45–5:59]: *"it's up to us to decide what do we measure, and that's a hard problem… It's not always as clear as we think it will be."* DM [2:57–3:06]: engineers know how to produce latency but may not find *"those true metrics that prove if we've actually accomplished some goal."*

**In practice.** `KEY_METRICS.md` and the success surface have two labelled groups: **health** (does it run) and **value** (did the customer or the business benefit). A dashboard that is all health is a monitoring tool, not a success surface. Payment or retention is strong evidence of value; note the caveat that payment without use is not.

**Raise at Stage 1.**
- Which of our metrics would still look healthy if no one ever got value from the product?
- What is the value metric we can compute from data we already store?

---

## GP-133 — Leading indicators predict; lagging indicators confirm; keep both

**Statement.** A **leading** indicator is an early signal, measured before the value is realized, that gives confidence things are heading the right way without proving it happened. A **lagging** indicator is measured after the fact and shows what actually happened. You want both.

**Source.** Host, DM [6:20–6:57]: *"your leading indicators are your early signals that maybe predict the outcome. They're not necessarily telling you that this thing actually happened. But it does give you some strong confidence that things are moving in the right direction when these things are good. So things like tool latency, retrieval confidence, retry or error counts."* DM [7:02–7:07]: if those are fine, *"if there's an issue with customers adopting this it's not going to be from the tools itself."* Example DM [7:13–8:19]: a mobile-engineering rule of thumb is that anything over about two seconds needs an indefinite spinner; the spinner is *"almost a way of mitigating that leading indicator"*, and he still sees it today (a black screen on a Plex load made him not want to wait more than two or three seconds). Lagging, DM [8:23–8:37]: *"what happens afterwards. What actually showed up after the fact?"*, such as *"did the physician actually save time in this visit? Was the visit shorter?"*, *"did the agent's claim hold up? Did a bad response reach a user?"* [9:18–9:34]. DM [9:44–9:54]: *"you want both of these. They both provide value to you as the engineer."* A host's gloss when a cohort member asked, DM [18:54–19:45]: leading happens *"before the value is realized"* (such as call latency); lagging is *"any number that you would get after the fact"* (such as the total on the receipt).

**In practice.** Each branch of the metrics tree names its leading indicator and its lagging indicator, and says which is which. For an agent: leading = tool latency, retrieval confidence, retry and error counts, verification pass rate; lagging = the visit got shorter, the claim held up under review, a bad response reached a user. Leading indicators are the ones that fire an alert; lagging indicators are the ones that settle whether the project worked. A leading indicator that has no lagging partner (or the reverse) is flagged.

**Raise at Stage 1.**
- For each lagging result we care about, what early signal predicts it?
- For each early signal, which result is it supposed to predict, and how will we check it does?

---

## GP-134 — A lagging metric moving tells you to investigate, not that you caused it

**Statement.** When a lagging number improves, it is a good sign, not a verdict. Work out what actually produced the change before taking credit, and compare against a group that did not get the change when you can.

**Source.** Host, DM [8:37–9:18]: a shorter physician visit *"doesn't prove necessarily that your product was better… if we're doing a comparison with physicians who are using our product and physicians who are not, and the physicians who are using it, [visit time] is going down, that's a good sign. And what it should tell you is not 'we did it', but rather 'we should go figure out what exactly is saving them this time.' Maybe it's partially our product and maybe it's partially something else, or maybe it's completely our product… We still have to figure out exactly what's going on. But again, good signal."* The same shape from a cohort member, DM [23:56–25:00] (Zach): a 400–500% spike in repeat usage of a shortcuts app was traced to a viral social-media trend, which started a two-year design effort. And [25:29–25:51]: repeat orders could be up *because of a pop-up restaurant nearby*; the metric says something is going well and *"the challenge is going to be figuring out what is that specific thing that is going good."*

**In practice.** A results section never says "our feature cut visit time"; it says what changed, in which group, against what comparison, and what else could explain it. If the design has no comparison group, say so and label the claim an association. A surprising movement opens an investigation task with the supporting metrics (GP-139) as its starting data.

**Raise at Stage 1.**
- What comparison group or baseline would let us say the project caused this?
- What other change at the same time could have produced the same number?

---

## GP-135 — A good metric is tied to a decision; a vanity metric only feels good

**Statement.** Prefer metrics you can act on. A vanity metric makes you feel good but changes no decision. The test is whether anyone would do something different if the number moved.

**Source.** Host, DM [10:15–11:40]: vanity metrics *"are just the ones that make us feel good… like total requests served, total tokens processed, who cares? At the end of the day that doesn't actually do anything for you."* If that were all Anthropic tracked they'd be *"aiming for a totally wrong target… more tokens could lead to better output or could lead to worse output. You don't really know."* An **actionable** metric *"is tied to something, tied to a decision"*, such as *"verification pass rate or tool failure rate."* His story, DM [11:47–13:06]: a colleague's tool-calling feature in a chatbot succeeded about 70% of the time; he set a goal of 99%, made tool success rate the north star, and put it on a dashboard on a TV that about 40 engineers saw every day; when it reached 99 *"we all saw it, we all knew it."* Host's caveat: you don't need a TV for every metric; the point is that *"he knew what his metric was, he knew what he was going for to determine success, and ultimately he reached it."* Cohort result on Crate Fresh, DM [20:05–20:28]: total orders since launch was called lagging and vanity, app downloads vanity, and average delivery time actionable and lagging. Kell, DM [31:41–31:57]: downloads *"could be because there's some download incentive; it really doesn't tell you if value ever got delivered."*

**In practice.** Next to each metric write the decision it feeds: *"if this drops below X we do Y."* A metric with no such line is demoted to context or removed. Cumulative counters ("total requests", "total tokens", "orders since launch") are never headline metrics.

**Raise at Stage 1.**
- If this number moved, what exactly would we do differently?
- Is this metric here because it is useful or because it is easy to count?

---

## GP-136 — Give a metric a denominator, and split it by who and where

**Statement.** A raw count has no basis for comparison, and one blended number can hide different stories for different kinds of customers. Normalize it and segment it.

**Source.** Zach (cohort), DM [30:54–31:32]: *"if you don't have a denominator, you don't have a basis of comparison… I can humanly measure the total orders placed since launch forever and ever. And all I have done is implemented a program counter. Congratulations. How many ticks have we had since launch?"* The host's agreement: *"very vanity."* Host, DM [22:54–23:41], on repeat orders within 30 days: some customers *"are never going to order every 30 days… you almost have to separate this out and say for this customer profile we want them to be repeat customers, and for this customer profile we're okay if they're just ordering regularly, whether that's 30, 60, 90 days… you don't want to clump all them together. It doesn't tell the right story, which is very important when it comes to these metrics, is telling that story."* Zach, DM [26:23–26:42]: *"Metrics are intersectional"*: break by location, time of day, type of cuisine. Innocent (cohort), DM [54:20–55:01]: prefers a per-user usage metric to a total emails-drafted count because *"one user just drafting a lot of emails"* can inflate a total; *"how consistently is each user using the platform"* shows whether the product is sticking.

**In practice.** Each headline metric states its unit and denominator (per user, per order, per visit, per week) and its segments (customer profile, location, time). When a number moves, the first step is to break it down by those segments (GP-134).

**Raise at Stage 1.**
- Per what? A total with no "per" is a counter.
- Which group of customers does this metric represent well, and which does it hide?

---

## GP-137 — Choose the metric for what this product's customer actually values

**Statement.** The right metric depends on the product and its customer. The obvious one (faster) can be the wrong one (a grocery shopper wants it when they said, not fastest), and you often need more information about the business before you can choose.

**Source.** Nicholas (cohort), DM [35:21–35:59]: for groceries, *"average delivery time we don't really care about… I want it scheduled so I can get it in my fridge right away. So a better metric might be promised delivery time and the delta between if it arrived early or late."* The host, DM [37:07–37:48]: *"I actually don't want this to show up in five minutes. I actually want this to show up when I want it to show up. So how close does it show up to the actual time that I said? … that's a really important number… these are perishable items."* Taylor, DM [32:54–33:27]: *"I like five because it's groceries… people get groceries often, so 30 days is a lot."* Nicholas, DM [36:07–36:42]: *"I would need to know a lot more about Crate Fresh and their goals… you can make an argument for everything."* The host calls this a good summary [36:49]. DM [44:44–44:55] on Desk Pilot: *"a trust and correctness dimension, not just speed."*

**In practice.** Before choosing a metric, write one line on what the customer values in this product ("on time, not fast"; "correct, not quick"). Where we lack the information to choose, record the missing information as an open question to the partner or an assumption (GP-129), and do not pick the generic metric by default.

**Raise at Stage 1.**
- What does this customer value in this product, in their words?
- What do we not know about the partner's goals that would change which metric we pick?

---

## GP-138 — Keep the set small; the wrong metrics are noise

**Statement.** A handful of well-chosen metrics beats a hundred. Wrong metrics don't just fail to help, they make noise and send you looking at the wrong things.

**Source.** Host, DM [9:54–10:10]: *"coming up with the right number of them is often the challenge. You don't want to do a hundred things and just throw it all out there. That can be cumbersome and you won't be able to find your answers very easily. So scoping it down and identifying those key ones is pretty important."* DM [40:43–41:10]: *"if we get the wrong metrics now it's just noise, and now it's really just actually hurting more than it is helping because we're looking at the wrong things… we can look back at metrics we've looked at before and go, actually that was not helpful. That was actually just making a lot of noise and maybe a bit of a red herring."* The exercises force the discipline: pick two of five [29:24–30:02]; pick the one north star and a few supporting metrics from nine [49:29–56:26].

**In practice.** A launch dashboard or success page has at most one north star, a few supporting metrics, and a short list of health metrics. Anything beyond that must justify itself against a metric already on the list. When asked "what two would you pick and why?", Innocent answers with the pair and the one he'd drop first.

**Raise at Stage 1.**
- If we could only show two metrics on launch day, which two, and why?
- Which metric on the list would we never miss?

---

## GP-139 — One north star, with supporting metrics that explain why it moved

**Statement.** A north star is the small number (often one) that defines success. Around it sit supporting metrics that show it is really moving and explain *why* it moved up or down.

**Source.** Host, DM [38:05–38:42]: *"there's not always just one. Sometimes there's a couple, but it's a pretty small group, and often one that you can just point to and say this is how we define our success… the one thing that we're really looking to push… And then how do we support that? What are the key indicators that show that this north star metric is actually passing?"* GoFundMe example, DM [38:58–39:27]: a screen of donations through the day with a predicted curve; for a donation-based company, donations are the north star. DM [39:33–40:12]: *"how can we explain the movements behind that one metric? Imagine you just have the north star and you're saying, 'oh look, it changed.' And then we go 'well why did that move up or down?'… sometimes we don't have all the metrics we need in front of us, but it does at least give us enough that we can go and figure out what's going on. And that can produce opportunities."* DM [40:23–40:36]: *"verification pass rate… latency and tool failure rate. These are the two supporting metrics that lead to this north star."* In the Desk Pilot discussion cohort members offered supporting metrics: weekly active usage per user (Jesse, DM [56:29–56:39]), and the share of drafts sent without edits (Rolando, DM [57:03–57:37]; the host: *"a very strong indicator of engagement… or of happiness with the product"* [57:42–57:50]).

**In practice.** The metrics tree has one north star at the root (GP-127). Each supporting metric is chosen because it explains a way the north star can move (more users, better quality, fewer failures), and the tree says which way. When the north star moves, the supporting metrics are the first thing we read. Universally useful supporting metrics (usage per user, a quality signal) are checked first; the rest depend on the north star.

**Raise at Stage 1.**
- If the north star dropped tomorrow, which supporting metric would tell us why?
- Which supporting metric would we want even if we picked a different north star?

---

## GP-140 — A north star has to cover every user, not only those who answer

**Statement.** Choose a north star you can compute for every customer, and be wary of self-reported ones. Surveys and ratings are skewed toward people with strong feelings, and a north star should connect to revenue. Still, a biased measure can be a useful *trend* line.

**Source.** On a customer-satisfaction survey as the north star for Desk Pilot (cohort consensus metric 8): Brian, DM [49:55–50:17]: *"people don't like responding to surveys… it's a convenient sample of your user base… it's going to be pretty biased."* James, DM [50:26–50:35]: *"it's usually the angriest people who speak the loudest."* Host, DM [50:44–50:55]: a hint of suspicion at Google ratings that show 500 five-star reviews and single digits for the rest. Zach, DM [51:37–52:24]: *"eliminate it immediately as a north star because… it doesn't directly impact your revenue. You can have 500 of the angriest customers in the world and you will still have revenue… self-selecting… People who are neutral never fill these out. So pick a metric as your north star that you're always going to have for every single person."* A counter-view, Joshua, DM [51:01–51:20]: *"even if it's not accurate, it could still be a useful measure because what you want to look at is how it changes in response to other factors"*; if it slowly rises, the product is getting better. The host: *"it can show a trend of some kind over time."* Zach's own pick, emails drafted per day, DM [52:30–53:24]: *"someone on your platform, regardless of whether or not they're paying, if they're drafting emails, they're engaged… that's the top of the funnel you need to drive to a conversion."* He calls it *"also a little bit of a vanity metric, but true north star metrics do a little bit of both."*

**In practice.** Sampling bias goes into the metric's caveat line in `KEY_METRICS.md`. A survey or rating is a supporting trend metric, with its response rate shown, not the north star. A candidate north star is checked on three questions: can we compute it for every user, does it connect to revenue or retention in a stated chain (GP-126), and can it be gamed by a few heavy users (GP-136)?

**Raise at Stage 1.**
- What fraction of users would this metric even cover?
- Who is missing from this measurement, and which way does that skew it?

---

## GP-141 — Adoption and engagement are not quality

**Statement.** People using a product more does not mean it is good. Pair every engagement metric with a signal about whether the output was right or useful.

**Source.** Taylor (cohort), DM [57:56–58:18]: *"how many of these are reliant on adoption, and that's not necessarily a reflection of the product itself… with every new thing you're going to have people who don't want it… there are so many other factors that aren't evaluating the item itself."* Host, DM [58:18–58:58], adding: *"just because people adopt the product doesn't necessarily mean your product is good. It might just be the only one out there that does the thing. I have been on those products before where we thought 'oh we're doing great.' No, we were doing good because we were meeting a need, but we were actually meeting it rather poorly and we just happened to be the only one out there… or the one that had the most grassroots marketing effort."* Rolando, DM [57:03–57:37]: the share of drafts sent without edits stands out because *"if the product is giving out really useful, almost one-shot great emails, people are going to be really excited and stay engaged."* And DM [11:20–11:25]: more tokens may mean better or worse output.

**In practice.** Each engagement metric (active users, sessions, volume) is paired in the tree with a quality metric from the same flow (accepted without edit, claim held up, error reached a user). If adoption is the only evidence of success, the write-up says so and says what it cannot show. This links to the eval work (GP-19, GP-38): quality metrics need a way to be graded, which the evals provide.

**Raise at Stage 1.**
- If usage doubled but quality fell, would our dashboard show it?
- Is there an alternative product, or is this just the only option?

---

## GP-142 — Ground the target in something real, know a good number, and separate the aim from the floor

**Statement.** A metric needs a measurable basis and a target. Don't set targets by gut. Know what number counts as good (and find out), and say separately where you want to be and where it stops working.

**Source.** Host, DM [41:36–42:08]: *"first ground it in something real. We should be able to trace this back to something tangible, something we can measure. If you can't measure it, it's going to be really hard to put any value in it. Some people love to just go by their gut, and we'll talk about this tomorrow in eval, but don't go by your gut. Let that gut lead you somewhere, but make sure you're grounded in something tangible."* DM [42:08–42:35]: you need to know what a good number is, *"and that can be a challenge sometimes to find out. Sometimes you just don't know until you know. Sometimes we can think this is a good number and really it's not. So it's something you kind of have to play with and measure and ask other people's opinions, or ask AI, and try to get some consensus."* DM [42:40–43:13], **aspirational versus hard gate**: *"know where you want to be, and know where, if we're not hitting this level, this is not working… so you can tell the story better and help make decisions better. If we just have numbers just to see numbers… I'm sure they look great in a board meeting but probably not something we can leverage to make better decisions."* Example target in the lecture: tool success rate from about 70% to 99% [12:06].

**In practice.** `KEY_METRICS.md` gives each metric three values: **baseline** (measured, or "none yet"), **aspiration**, and **hard gate** (the level below which we say it isn't working and act). Each carries a label for where it came from (GP-119: measurement, assumption, target), and the target rationale says how we'd learn if the number is wrong. A target with no basis is written as an assumption, never as a given.

**Raise at Stage 1.**
- What is the baseline, and how did we measure it?
- Below what number do we say this isn't working, and what do we do then?

---

## GP-143 — Review the metrics, change them, and expect to be challenged on them

**Statement.** Metrics are a first draft. Check on a schedule whether they are still showing the right things and whether the targets are right. Choosing them early and changing them later is fine, and the interviews will push back on your choice.

**Source.** Host, DM [43:20–43:58]: *"every now and then it's always good to come back and say, are these actually showing us the right things? Are these actually vanity metrics and we thought they were good ones? … are our targets wrong? Should we have moved this up, moved this down? Is it really okay if they fall a little bit?… it's definitely always worth reviewing."* DM [44:02–44:28], on the week's project: *"it's totally fine to come up with them now and then change them later. And we'll try to challenge you on your metrics when it comes to our interviews to tease out maybe some extra insights. Don't feel offended if we come hard at what metric you picked. It's more of a way for us to think through it together."*

**In practice.** `KEY_METRICS.md` has a *review* line per metric (when we'll look, what would make us drop it) and a change log. Interview prep for each project includes the strongest objection to the chosen north star (GP-140 and GP-141 supply the usual ones), with a calm answer that says what we'd change if the objection is right.

**Raise at Stage 1.**
- What is the best argument against our north star, and how would we answer it?
- When do we next review these, and what would make us swap one out?

---

## GP-144 — Pick the user and the use case before defining success

**Statement.** "Is it working?" has no answer until you decide who it is working for and for what job. Choose the user and the use case first, then ask what success is for them.

**Source.** Host, DM [59:09–59:37], to the cohort building the OpenEMR co-pilot: *"how are you going to make sure that your app is working for your user, right? You've got to pick your user. I mean, it's a physician, but you kind of got to pick a little bit of the use case. So think about that in terms of okay, how do I determine what success is for this use case that I'm really gunning towards."* Innocent (cohort), DM [22:05–22:50], on the repeat-order metric: the comp asks whether it is "actually working"; *"if they're speaking from a technical standpoint, that's one thing, but if from a business standpoint, is this an actual viable product, then I would want to ask what are the things that are making a customer not want to do a repeat purchase… there's layers to that metric."* Nicholas, DM [35:36–35:45]: the same metric matters more for groceries than for other products.

**In practice.** The success framing starts with a one-line user and use case ("a clinician on a 15-minute visit asking about meds", "a provider placing a supplement order"). Metrics are written for that user. When the brief names several users, the north star is chosen for the one the partner pays for or cares about most, and the rest become segments (GP-136).

**Raise at Stage 1.**
- Who is the one user whose success we are measuring, and in what situation?
- Whose success would we trade away if we had to?
