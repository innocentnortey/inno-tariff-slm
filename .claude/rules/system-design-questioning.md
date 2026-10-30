<!-- Provenance: copied from Gauntlet AI/.claude/rules/system-design-questioning.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
---
paths:
  - "**/docs/prd/**"
  - "**/docs/design/**"
  - "**/*readiness*"
  - "**/*system-design*"
  - "**/ARCHITECTURE*.md"
  - "**/SYSTEM_DESIGN*.md"
  - "**/PROJECT-CHECKLIST.md"
---

# System Design: Ask the Questions Before and While Designing

> **Provenance:** this is the original. Spin-off repos carry a copy in `.claude/rules/` (zero-to-hero
> principles pack, general set); change `Gauntlet AI/` first, then re-copy. Recorded 2026-10-19 at
> Innocent's instruction: "i need it so that the zero to hero scaffolding includes a rule where you
> perform the proper questioning before and while building the system design".

Applies from the moment a system design starts (zero-to-hero §6, the `system-design-readiness`
audit, or any architecture, sizing or hosting work) until the §6 gate is ticked. It sits beside
`system-design-conversation.md`. That rule says *which* questions to walk. This one says **who
answers them, when, and what may not be drafted until they are answered.**

## What went wrong (why this rule exists)

On 2026-10-19 the same mistake happened twice in one day:

- **YourAI:** the audit marked peak and concurrency (SD-3.4) "n/a". Innocent had to reopen it
  himself: "built for 50 users … how we would scale it to 1000" (its Q-036).
- **Riverside:** the Stage 6 design was drafted while Innocent was away. The brief's *test* load
  ("20 concurrent virtual users for 60 s, generated with k6") was treated as the design target. A
  scale target of "1,000 office locations ≈ 300 model calls a minute" was invented from company
  location counts. One replica was taken as a default. None of it was asked. Innocent:
  "how did you do the system design without asking me about the load on the system? i thought the
  skill explicitly addresses this".

The readiness skill already said these were his decisions. What failed was the order: the design
was drafted before the questions were asked, and stand-ins were counted as answers.

## Rules

### Before designing

1. **Ask the foundation questions first, before anything that depends on them.** These shape every
   later number, so they are asked of Innocent before DO-1 is drafted. This holds even when he asks
   for design progress while away, and even when the brief seems to imply an answer:

   | Item | The question | Example of a stand-in that is *not* an answer |
   |---|---|---|
   | SD-3.1 | What load is it built for, and what larger load needs a written path? Registered, daily-active or *at once*? | A benchmark condition ("20 VUs for 60 s"); a company's location count |
   | SD-3.4 | Peak and concurrency: how many at the same moment, how bursty? | "n/a"; "same as the test" |
   | SD-7.2 | What failure must the deployment survive: a restart, losing one copy, a zone? | "One replica" as a default |
   | SD-1.6 | Spending ceiling: hosting, model spend, paid APIs | "Free tier, presumably" |
   | SD-1.9 | The hardest uncertainty: what the project most needs to prove | Claude's own guess at the risk |

   The stack, host and database also join this list when no earlier decision record settles them.
   Ask the load question first: the others depend on it.

2. **A stand-in is never an answer.** An item is *Found* only when an issued source answers the
   question asked. A test condition, a benchmark, a vendor default, a framework default, a public
   count of locations or customers, or "what we did last project" is evidence for a question.
   It is not the answer. If the brief is silent, the item is **Missing (decision)**, never Found,
   Assumed or n/a.

3. **Tell decisions from assumptions with one test: could a measurement settle it?**
   - If yes (a model's latency, the time per OCR read, tokens per turn), label it `[A]`, give
     the measurement that will replace it, and carry on.
   - If no, because it is a choice of what to build for, what to spend or what risk to accept, it
     is Innocent's question. A recommendation goes *with* the question. It never replaces the
     question.

4. **If Innocent is away, draft only what doesn't depend on an open foundation answer.**
   - Mark the dependent parts *blocked on SDQ-N* and stop there.
   - Don't fill them with a placeholder target to show progress. A design drawn on a guessed load
     reads as decided, however carefully it is labelled.
   - Work that is independent can proceed: the traced request, the component map, contract gaps,
     evals and the observability contract.

5. **Ask in the house format.** Use the workspace rule `decision-requests-story-driven.md` (in the
   Nortorious-Technologies root `.claude/rules/`): the story,
   2–4 options with the recommendation first, then a **Decision needed:** line.
   - One decision per question, the load question first.
   - In a background job, the `needs input:` line carries the decision.
   - If he answers with a kind of answer and no numbers ("a number I set"), ask the follow-up
     straight away. The item stays open until the numbers arrive.

6. **Record the answer before using it.** Put it in three places:
   - the readiness report row (status Decided, with date and his words);
   - the PRD decision table, or the decision record;
   - the dev log.

   Only then may the design use it. Each number derived from it is labelled `[T]` (his target) or
   `[C]` (calculated from it).

### While designing

7. **Stop and ask when the design reaches a choice no requirement settles.** For example:
   - a calculation crosses a limit that forces a paid tier, a plan change or a second service;
   - two options trade cost against risk;
   - a requirement turns out ambiguous;
   - a spike result contradicts an earlier answer.

   Raise it as a new `SDQ-N` in the readiness report's Decide table, in the same session.
   - **Foundation-type choices** (load, money, failure to survive, what must be proven) block the
     parts that depend on them, as in rule 4.
   - **Other choices** may be drawn on the recommended option, but only if all of these are true:
     - it is labelled *Proposal, awaiting you*;
     - it appears as a `data-ask` card on the Stage 6 page;
     - the decision sentence names what changes if he picks differently.

8. **Re-ask when the numbers undercut an answer he gave.** Sometimes the arithmetic shows his
   target is unaffordable, impossible on the current plan, or needs a vendor tier he hasn't
   chosen. Example: 1,000 people at once at the k6 pace exceeds every published Anthropic tier.
   Put that back to him as a question with options. Don't quietly shrink the target, and don't
   quietly add the spend.

9. **Never change a recorded answer yourself.** A recorded answer is changed only by a new
   decision of his, recorded the same way (rule 6).

### Before the gate

10. **Sweep before asking for sign-off.** Every Decision-type item in the readiness checklist must
    be in one of three states:
    - **Decided by Innocent**, with date and source;
    - **Proposed**, and listed for his review on the Stage 6 page;
    - **n/a**, with a reason a reviewer could disagree with.

    No foundation item may be Proposed or defaulted. The Stage 6 page names which questions he
    answered and which are still open, and the §6 gate is not ticked while a foundation item is
    open. The only exception is a *Skips* row recording his own yes.

## Self-check before drafting any sizing, replica, plan or tier choice

- [ ] Have SD-3.1, SD-3.4, SD-7.2, SD-1.6 and SD-1.9 each been answered **by Innocent**, in his
  words, and recorded?
- [ ] Is any "answer" really a test condition, a default or a public count?
- [ ] Would this number change if he gave a different answer to an open question? If so, stop.
- [ ] Is every new choice since the last sweep either asked, or drawn as a labelled proposal with a
  `data-ask` card?
