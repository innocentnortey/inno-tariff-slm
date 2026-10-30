# Guardrails and Verification — GP-14 to GP-18

An agent loop is, by construction, a program that could run forever and say anything. These principles are how you make it stop and how you check what it said.

---

## GP-14 — Every loop has four brakes

**Statement.** A production agent loop needs a max iteration count, a hard timeout, a cost budget, and a circuit breaker that stops repeated identical attempts. Framework defaults are not a substitute.

**Source.** Aaron, V1 [13:20–14:24]: the ReAct loop *"could be called however many times and it could loop forever… we need to be imposing that structure… There might be a default recursion limit, but it might be something like 10, and that might be way too much for the system you're actually running."* V1 [23:20–25:12]: *"unbounded while loops are not good… you want to have a max number of iterations and you also probably want a hard timeout… keep track of how much money you're spending… circuit breaker… if the agent just keeps bashing its head in the wall like more than say three times… it should try something else… a real production-grade one probably needs all four of these in some fashion."*

**In practice.** Set all four explicitly and log which one fired. The first three are fatal (return a graceful "couldn't complete" with what was found). The circuit breaker is recoverable — tell the model that path is failing so it can choose another tool.

---

## GP-15 — Two stopping criteria: a happy path and a backstop

**Statement.** Let the agent judge that its answer is good enough — and still keep a hard stop for when it never gets there.

**Source.** Aaron, V2 [33:36–34:16]: *"the risk with any agentic, loopy, complex… solution is it can just keep burning… you could have it actually basically try to judge how well it's answering the question and if it thinks the answer is good enough, that's a stopping criterion. You're still going to want another stopping criterion because what if it never reaches this point, but that might be your happy-path stop."*

**In practice.** Happy-path stop = the model emits a final structured response that passes verification. Backstop = GP-14's brakes.

---

## GP-16 — Climb the verification ladder only as far as the stakes demand

**Statement.** Model output is not assumed correct. Add checks in rough order of increasing strength and cost: automated flags and authoritative lookups → LLM-as-judge → hard business rules → human in the loop. Low-stakes toys need little; healthcare, finance, compliance and security need the upper rungs.

**Source.** Aaron, V1 [25:20–26:32]: *"it's not enough to just chuck input into a statistical model and assume the output is good… if it's a healthcare thing, if it's a finance thing… there's domains where we really care about things being right… you need to incorporate additional checks."* V1 [26:56–27:12]: *"structured authoritative checks, you know, sources that you know are right, incorporate that."* V1 [28:40–29:28], on LLM-as-judge: *"what if the judge hallucinates? You're right, that can happen. But by… having a specific sort of sub-agent as the judge that has a limited input that's focused on just that one task, its reliability statistically speaking is higher."* V1 [29:36–30:24]: *"these are kind of in order of increasing strength and cost… hard business rules… should never suggest more than four pills of that drug… But the ultimate check that you still need sometimes is a human in the loop."*

**In practice.** AgentForge is at the top of the stakes scale. Week 1: every claim cites a chart record (authoritative check) and passes code-enforced clinical rules (dose, interaction, allergy). Week 2: an LLM judge with a narrow rubric in the eval gate. Week 3: critical findings route to a human.

---

## GP-17 — Design human-in-the-loop for the human

**Statement.** When a person must approve, bring them in at the right moment with exactly the information they need, and no more friction than necessary — the system exists to save their time.

**Source.** Aaron, V1 [30:32–30:56]: *"you often have to start thinking about usability and design… making sure you're bringing the human in at the right time and giving them the information they need but not causing them too much pain, because the whole point of your system is probably to save their time in the first place."*

**In practice.** An approval prompt shows the proposed action, the evidence behind it, and one-click accept/reject — not a raw transcript.

---

## GP-18 — When the evidence doesn't answer, say so — and cite what you used

**Statement.** Retrieval always returns *something*, even for nonsense queries. The prompt and the verification step must allow — and prefer — "the provided sources don't answer this" over a plausible answer. Show sources.

**Source.** Aaron, V2 [52:04–52:36]: *"It doesn't matter what gobbledygook you put in your user question. The vector search will always find the most similar documents… there's always the least irrelevant. You always need to have in your prompt something like, 'Hey, if none of these answer the question, just don't answer the question. Say you can't.'"* V2 [50:08–50:24]: *"one of the nicest things about retrieval-augmented generation — you can cite your sources."*

**In practice.** A relevance threshold below which retrieval returns "no supporting evidence", a refusal path the model is explicitly allowed to take, and eval cases whose correct answer is a refusal.
