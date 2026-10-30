<!-- Provenance: copied from Gauntlet AI/.claude/rules/problem-framing.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
---
paths:
  - "**/docs/prd/**"
  - "**/docs/analysis/**brief-audit*"
  - "**/docs/delivery/**"
  - "**/docs/source/**"
  - "**/*brief-audit*.md"
  - "**/*angle-and-demo-framing*.md"
  - "**/*why-chain*.md"
---

# Find the Real Problem Before You Frame the Solution

> **Provenance:** this is the original. Spin-off repos carry a copy in `.claude/rules/` and the
> principles at `docs/principles/`; change `Gauntlet AI/` first, then re-copy. Added 2026-10-16.

Applies whenever a brief is audited, a PRD or success framing is drafted, or a metric is chosen. The
principles are `principles/problem-framing.md` (GP-120 – GP-130); in a spin-off repo,
`docs/principles/problem-framing.md`. It sits underneath `hiring-partner-framing`: that rule says
how to present the two layers, this one says how to find layer 2.

## Rules

1. **The brief is the partner's answer, not the problem [GP-121].** The brief audit opens with
   *The problem behind this brief*: the partner's stated solution, the problem we think it answers,
   the customer it serves, and the evidence.
2. **List the assumptions inside the requirements [GP-122].** One line each, marked *needed*,
   *probably needed* or *question it*. A hard requirement of the brief is never waived by us; a
   *question it* goes to Innocent as options.
3. **Observe before fixing [GP-123].** Record *complaint → what we observed → what we think is
   underneath*. A cheaper fix that changes the experience of the problem is a legitimate option.
4. **Write the why-chain [GP-124, GP-125].** Open with a scope line (team / product / company, and
   the customer). Each "why?" has an answer and evidence. End at a cause we can change, measure and
   explain in one sentence. Record the branch we rejected.
5. **Every metric has a hop chain to money or customer value [GP-126].** Revenue, cost, or customer
   value. More than three hops, or a hop with no evidence, is flagged.
6. **One north star, named before any ticket [GP-127]**, measurable from data the system stores,
   with a before-number or an honest "no baseline" and a guard against improving it for the wrong
   reason. Leading and lagging indicators sit below it on the same tree.
7. **Count use, not output [GP-128].** A success surface shows use over time. A feature with no usage
   signal is on the cut list.
8. **Label every belief about the partner [GP-129].** Assumption, its source, how it could be
   checked. Cheap spikes count as evidence. Never state a guess as fact.
9. **Lead the write-up with the problem we found [GP-130]**: *brief said X → we found Y → we built
   Z → the metric moves because…*, and what we chose not to build.

## Review checklist (brief audit, framing doc, PRD)

- [ ] Does the audit open with the problem behind the brief, with evidence?
- [ ] Are the brief's assumptions listed and each marked?
- [ ] Is there a why-chain with a scope line, and does it end at something we can change?
- [ ] Does every metric trace to money or customer value, and is each hop supported?
- [ ] Is one north star named, stored, baselined (or marked no baseline), and guarded?
- [ ] Is every claim about the partner's business labelled fact or assumption?
