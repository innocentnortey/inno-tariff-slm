# System Design — GP-107 to GP-119

How to reason from a requirement to a design you can defend, so the design conversation surfaces
the right issues before tickets exist. Each principle ends with **Raise in the design
conversation**: the questions to put on the table (options-first) whenever a project designs a
system. The step-by-step process these support is
`.claude/skills/system-design-readiness/GUIDELINE.md`; this file is the principle layer under it.

**Sources and their weight.**

| Code | Source | Weight |
|---|---|---|
| **SD** | `transcripts/2026-10-08-system-design.md`: cohort session led by **Zach Gardner, a cohort member (not staff)**, with Innocent, Kaushal and Sefath. AssemblyAI, speaker-labelled | Peer experience from years at startups, so weaker than the staff lectures. Rules of thumb in it are labelled as such |
| **RD** | `prep/2026-10-08-requirements-driven-system-design-process.md`: a ChatGPT synthesis of SD, citing Google SRE, AWS and Brewer | It **corrects** several SD claims; where they disagree, the correction is stated below and wins |

Citation format: `SD [00:12:38]` = transcript timestamp; `RD §1 Step 3` = section of the synthesis.

---

## GP-107 — The economics come first: price each successful outcome

**Statement.** Before any architecture, work out what one successful outcome earns and what it may
cost. That budget decides what you can afford: freshness, model calls, redundancy. Then check the
other direction: the budget never *proves* a quality level is acceptable to the user.

**Source.** Zach, SD [00:11:52–00:12:19]: *"the average bet is $60… 1% of that isn't even a dollar,
it's 60 cents… I still need a 30% margin."* Kaushal [00:12:20]: *"This is gonna factor into what
services you could afford with that margin level."* Zach [00:12:38]: *"This is step 1… from years at
working at startups."* Sefath [00:12:30]: *"I usually have to do system design questions with an
unlimited budget… I never did this portion of it."* **Correction**, RD §1 Step 1: revenue per trade
is not revenue per visiting user (free browsing still costs money), and *"the fee does not
mathematically determine acceptable freshness"*. The useful unit is **cost per successful outcome**,
including every model call, retry and background job behind it.

**In practice.** The design brief opens with one line: *outcome → revenue or value per outcome →
cost ceiling per outcome*, each figure labelled target, assumption or measurement.

**Raise in the design conversation.**
- What is one successful outcome here, and what does it earn or save?
- What is the most each outcome may cost, all model calls and retries included?
- Which quality level (freshness, accuracy, latency) is the budget tempting us to cut, and does the user actually accept that?

---

## GP-108 — Name the scale bucket you are designing for

**Statement.** Systems are designed per order of magnitude: one user, ten, a thousand, a hundred
thousand, a million. Each bucket has different concerns. Pick the bucket from the requirement, say
it, and design for that one — not the one above it, not the one below.

**Source.** Zach, SD [00:13:08–00:13:54]: *"there are buckets of design… you are starting to design
for each next logarithm."* [00:13:54]: *"The design of the system that you build for 1 user is not
going to work for… 10, for 100, for 1,000 to 100K… the concerns that you have to deal with are
vastly different."* [00:15:05–00:16:29]: *"if you don't know which bucket you're designing for,
you're going to design a system that too complicated to maintain and too expensive to keep, or one
that doesn't meet your requirements."* [00:45:24–00:46:17]: SQLite for yourself; one VPS for ten;
backups and a second server around a thousand.

**In practice.** The system design states the bucket and the two or three concerns that bucket
brings, and names what is deliberately *not* built because it belongs to a bigger bucket.

**Raise in the design conversation.**
- Which bucket does the requirement put us in, and is that users per day, concurrent users, or something else?
- What does this bucket require that the one below doesn't (backups, a second server, a queue)?
- What are we tempted to build that belongs to a bigger bucket?

---

## GP-109 — Spend design effort where the partner's uncertainty is

**Statement.** Most of a system is a solved problem. Design depth goes to the part nobody knows
can be done, because that is what the partner is paying to learn. The rest is stated as standard
and kept small.

**Source.** Zach, SD [00:26:22]: *"they're not even sure just the market normalization bit is
feasible in an automated fashion. So that's the thing I would be very, very careful to prove."*
[00:28:15–00:28:49]: *"They know the web problem is solvable… they don't know that the problem of
Kalshi and… markets"* — Kaushal: *"The equivalence can be proved."* — Zach: *"So that's what I would
drill hard in."* [00:30:05–00:30:15], on his own HTTP service: *"notice how it's nothing… I'm
treating it as a big black blob that doesn't matter."* Kaushal [00:28:53]: *"it deeply informs where
you put your effort on the technical side."*

**In practice.** The hard-problems page (`zero-to-hero` Stage 3) holds the partner's uncertainty;
the solved parts get one line each under *Handled by default*.

**Raise in the design conversation.**
- What does the partner not know is possible? Is that the centre of our design?
- Which components are solved problems we can treat as standard?
- What evidence would prove the uncertain part works?

---

## GP-110 — Turn "fast", "live" and "reliable" into separate, measurable promises

**Statement.** Latency, freshness, correctness, availability and recovery are different
requirements and are measured separately. A fast response can carry stale data. Correctness rules
are invariants, never hidden inside a good percentile.

**Source.** Zach, SD [00:08:02–00:08:22]: *"for a user that can pay me $1 each time they make a
trade, you get a minute, you get 5 minutes… that's my guarantee, quote unquote, on how fresh your
data is… I'm not gonna even call it a guarantee… that's my, like, P95."* RD §1 Step 2: *"A response
can arrive in 100 milliseconds while containing a five-minute-old quote. Fast delivery and fresh
information require separate measurements."* SLI = the measurement, SLO = its target, SLA = an
agreement with consequences.

**In practice.** A requirements table with one row per important operation and one column per
promise. Each target states where timing starts and stops. Invariants ("never simulate an
unaccepted fill") are listed on their own.

**Raise in the design conversation.**
- For each key operation: how fast, how fresh, what must always be true, what may degrade, how much loss is tolerable?
- Which of these is an invariant (never violated) rather than a percentile?
- Where exactly does each measurement start and stop?

---

## GP-111 — Translate users into work, and model each workload separately

**Statement.** "50,000 users" is not a workload. Turn it into requests: which kind of users (daily
or concurrent), actions per user, requests per action, read, write or AI, the peak multiplier and
**how long the burst lasts**. Background work (ingestion, normalization, jobs) is a separate
workload, and often the bigger one.

**Source.** Zach's sizing prompt, SD [00:33:42–00:35:21]: *"60K users per day. Assume spiky,
pathologically spiky usage. 15 to 20x spikes over the baseline average. What are my requests a
second?"* [00:42:41]: *"a 20x spike, which is insane. You usually calculate for 8x and 12x in the
worst case."* Innocent, on the 30–50K target, [00:31:10]: *"how do you digest that information into
your architecture?"* RD §1 Step 3: 60,000 × 10 = 600,000 requests/day ≈ 6.9/s average ≈ 139/s at a
20× peak; *"a 20× spike lasting 50 milliseconds creates a different problem from a 20× spike lasting
half an hour."* RD §3: *"A system can have relatively few users and still process a large amount of
market data."*

**In practice.** A workload table: one row per request class plus one per background job, with the
assumption behind every number visible, an expected case and one stress case.

**Raise in the design conversation.**
- Is the user number daily, monthly or concurrent? Who said so?
- How many requests does one user action create, and of which kind (cheap read, write, model call)?
- What background work runs with no user present, and how big is it?
- How big is the peak, and how long does it last?

---

## GP-112 — Elapsed time is not resource demand: trace what each request holds

**Statement.** Little's Law turns rate × time into average overlapping work; it does not give a
server count, a p99, or a bottleneck. To size anything, trace one real operation and ask which
resource it occupies, for how long, and how many operations can hold that resource at once.

**Source.** Zach, SD [00:37:12–00:37:19]: *"I just have to serve 87 concurrent requests per second in
the worst case"* — RD §1 Step 3 corrects the units: *"87 requests in flight is different from 87
requests per second."* Innocent, SD [00:44:24]: *"you're not even factoring in what's going on in
your actual architecture… can't we look inside of our actual… architecture?"* — RD: *"your
objection about the missing architecture details was valid."* Innocent, [00:47:06–00:47:56]: the
first OpenEMR build *"blew up"* at 50 users. Zach [00:49:31–00:49:43]: *"if you design it right, you
can sip RAM, you can sip CPU… the degradation that I had is like the single event loop thing."* RD
§1 Step 5: two requests that both take 250 ms can need 0.7 or 35 CPU-seconds per second at 140
req/s; a database connection held 20 ms versus 200 ms means ~2.8 versus ~28 busy connections. RD §3:
*"What resource is occupied, for how long, and how many operations can hold it at once?"*

**In practice.** Trace one representative operation (reads, computes, writes, waits) before
choosing machines. A load test splits time into app waiting, pool checkout, query, external API and
model generation.

**Raise in the design conversation.**
- Walk one important request end to end: what does it read, compute, write, and wait on?
- What does it hold while waiting: a worker, a DB connection, an event loop, a provider slot?
- Which of those has a fixed limit, and how many requests fill it?
- Which waits can move before the request (precompute) or after it (background)?

---

## GP-113 — Find the thing that breaks first at this load, and fix it before it breaks

**Statement.** Every load level has a first failure, and it differs between levels. Design and test
for the first breaker at the bucket you're in; the next one waits until growth makes it real.

**Source.** Zach, SD [00:46:19–00:47:06]: *"you always go for and you fix the thing that breaks first
for whatever load that you're at… you want to fix it like before it's going to do that. But the
thing that breaks first is different for the different load factors… At 1 million users… very, very
different than going from 1,000 to 10,000."* RD §1 Step 5 output: *"a hypothesis about the first
bottleneck."*

**In practice.** The system design names the suspected first bottleneck and the test that will
confirm or move it. The growth trigger for the next one is written down, not built.

**Raise in the design conversation.**
- At our bucket, what do we expect to break first: DB connections, a provider rate limit, model latency, memory, disk?
- What test will show it before users do?
- What number tells us the next breaker has become real?

---

## GP-114 — A queue absorbs a mismatch; it adds no capacity. Decide overload behaviour per operation

**Statement.** Queues buy time, not throughput. A growing backlog can finish work too late to
matter, and clearing it needs spare capacity above ongoing arrivals. So each operation gets an
explicit overload behaviour: wait briefly, move to the background, return a reduced answer, throttle
or fail fast.

**Source.** Zach, SD [00:02:48–00:03:06]: *"queuing theory applies to any queue. Your queue at the
supermarket… Load balancers are our checkout registers."* [00:40:19–00:40:36]: *"tolerable ingress
queue… 63 requests per node… more than 63… the client is probably going to timeout."* RD §1 Step 6:
*"A queue can absorb a temporary mismatch. It does not increase the workers' processing capacity…
If workers finish 140 jobs/second and 100 new jobs/second keep arriving, only 40 jobs/second remain
available to clear the backlog."*

**In practice.** A table with one row per operation giving its deadline, queue limit and overload
behaviour; retries are bounded and only for failures where a retry can help.

**Raise in the design conversation.**
- For each operation: when we're over capacity, does it wait, defer, degrade, throttle or fail fast?
- What is its deadline, after which the work is useless?
- What is the queue limit, and what happens to the request beyond it?
- Which failures are worth a retry, and how many?

---

## GP-115 — Autoscaling helps only with spikes that outlast the time to add capacity

**Statement.** Compare how fast demand rises, how long the spike lasts, and how long new capacity
takes to become usable. Short spikes need capacity already running and controlled admission; only
sustained growth is an autoscaling problem.

**Source.** Zach, SD [00:42:51–00:43:27]: *"Because the requests are fast enough, it will take you
longer to spin up new pods than the spike will last. So dynamic autoscaling doesn't even really help
you here."* [00:37:35]: *"it even says don't rely on dynamic auto scaling for spikes."* RD §1 Step 6:
*"The service time of an individual request does not tell you how long the spike lasts."*

**In practice.** Headroom for the modelled spike is provisioned; autoscaling is justified only with
the spike-duration and spin-up numbers side by side.

**Raise in the design conversation.**
- How long do our spikes last, and how long does new capacity take to serve traffic?
- Is the answer always-on headroom, admission control, or autoscaling, and why?

---

## GP-116 — Partitions will happen: choose consistency or availability per operation

**Statement.** In any distributed system a network partition is not optional, so during one you
choose between consistent shared state and answering every request. Make that choice **per
operation**: most stay available on eventually consistent data, while the ones guarding an invariant
refuse rather than answer wrongly.

**Source.** Zach, SD [00:20:39–00:21:37]: *"this is the underpinning of every single system design
you will ever make, whether you know it or not… Pick 2… you always have to pick this one"*
(partition tolerance). [00:21:51–00:22:33]: *"Somebody's gonna trip over the fucking network
cable… Amazon's gonna blow up… US East 1."* [00:22:34–00:23:42]: if Amazon chose consistency, *"nobody
can buy from me because we had a network blip."* Kaushal [00:24:13]: *"That's why you usually direct
consistency to a cold path."* **Correction**, RD §1 Step 6: *"The discussion's claim that you must
always choose availability is too broad… The decision can differ by operation. Some operations
should reject work to preserve an invariant while other functions remain available."* For Equinox:
*"browsing labeled older information and refusing a routing claim based on untrustworthy liquidity
can coexist."*

**In practice.** A list of operations, each marked *available on stale data (labelled with its age)*
or *refuses without a trustworthy state*, with the invariant that justifies each refusal.

**Raise in the design conversation.**
- Which operations may answer with stale data, and is the staleness shown to the user?
- Which operations guard an invariant and must refuse rather than guess?
- Where does the consistent "cold path" live, and what reconciles afterwards?

---

## GP-117 — A cache is a decision about authority and staleness; say why this one, now

**Statement.** Read-through (load on a miss) and write-through (the writer updates the cache) can
both be right. Choose from what the system values (latency, consistency, debuggability), say why
it fits *now*, and define which store is authoritative and how stale data is handled. Writing to the
database and the cache separately does not keep them consistent.

**Source.** Zach, SD [00:04:33–00:04:40]: *"That's pull-through. It followed the chain all the way
to the data it needs."* [00:04:56–00:05:21]: write-through, *"instead of just writing it to the
database, it also writes it to Redis."* [00:05:32–00:05:47]: *"I would argue right-through is what we
want… we're worried about more is latency for the end user, and we're worried about consistency of
the data."* [00:05:58–00:06:33]: *"this is not a case where unequivocally this is the right
answer… This just happens to be the one that I think is the better solution for this right now…
That might change in a few hours."* **Correction**, RD §2: *"A worker independently writing to both a
database and Redis does not itself guarantee that they remain consistent. Define the authority,
update sequence, and stale-data behavior."*

**In practice.** Every cache in the design has one line each for: authority, write path, staleness
bound, and what the user sees when it's stale.

**Raise in the design conversation.**
- Does this data need a cache at all, at our bucket?
- Which store is the source of truth, and what order do writes happen in?
- How stale may the cached copy be, and what happens on a miss or a failed write?

---

## GP-118 — Replicas, zones and regions answer different questions; size them from measured capacity

**Statement.** More replicas add serving capacity or survive one instance failing. Zones survive a
location failure. Regions serve distant users, regional disasters or residency rules. Each needs its
own justification. Size replicas from a **measured** per-replica capacity and the failure you claim
to survive.

**Source.** Zach, SD [00:17:12–00:17:56]: multi-region *"depends on your availability requirements…
You do not need it to actually handle your load… this is a rule of thumb… I would have to derive
numbers to back it up… around 2,500 requests per second."* [00:18:04]: *"the difference between
having multi-region to survive a load and multi-region to keep high availability is pretty
significant."* [00:19:33]: *"write-ahead log is always, always, always a thing… just have everything
touch the primary, because your load is not high enough to overwhelm that… You really should have
3."* **Correction**, RD §1 Step 7: *"There is no general rule that reaching 2,500 requests/second
requires another region."* Worked example: if one replica sustains 80 req/s within target and the
requirement is 140 req/s *with one replica down*, two replicas (80 after a failure) fail and three
(160) pass.

**In practice.** Each replica, zone or region in the deployment carries its reason (capacity,
fault tolerance, geography) and the benchmark number it was sized from. Cost covers the whole
deployment: database, backups, transfer, model use and monitoring.

**Raise in the design conversation.**
- What failure are we promising to survive: one process, one machine, one zone, one region?
- What does one replica sustain, measured within our latency target?
- Is a second region for load, availability, latency or law, and which number justifies it?

---

## GP-119 — Keep targets, assumptions, calculations and measurements apart, and end every choice with a revisit trigger

**Statement.** Every number in a design is one of four kinds: target, assumption, calculation or
measurement. Label each one, because in an LLM conversation a plausible assumption becomes an
apparent fact within a few messages. Every major choice closes with the sentence: *Because [specific
requirement or measured limit], we chose [design]. It should provide [measurable result]. We will
verify it with [test], and revisit it when [trigger].*

**Source.** Zach labels his own figures: *"let's assume"* (SD [00:32:34]), *"this is a rule of thumb…
I would have to derive numbers to back it up"* ([00:17:12]), and *"Now, this is wrong because I
actually meant 3.83 million requests per day"* ([00:38:33]). RD §1 Step 3: the PDF's *"3.83 million
requests/day becomes 600,000… Those should not be treated as one continuous calculation."* RD §4:
*"Keep targets, assumptions, calculations, and measurements visibly separate. That distinction is
especially valuable when working with an LLM."* RD §1 Step 8, for AI systems: *"Does the system make
valid decisions? Can it produce those decisions reliably at the required workload?"*

**In practice.** The system design tags numbers `[T]`, `[A]`, `[C]` or `[M]`, and each decision row
ends with its verify-and-revisit sentence. Validation covers both questions: valid decisions, and
reliability at the workload.

**Raise in the design conversation.**
- Which numbers in this design are measured, and which are we only assuming?
- For each major choice: which requirement forced it, what test proves it, and what would make us revisit it?
- Does the system make valid decisions, and can it make them at the required load? Which have we actually shown?
