<!-- Provenance: copied from Gauntlet AI/.claude/rules/business-metrics.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
---
paths:
  - "**/KEY_METRICS*.md"
  - "**/*metrics*.md"
  - "**/docs/prd/**"
  - "**/docs/delivery/**"
  - "**/*angle-and-demo-framing*.md"
  - "**/*success*.md"
---

# Choose Metrics That Prove the Work

> **Provenance:** this is the original. Spin-off repos carry a copy in `.claude/rules/` and the
> principles at `docs/principles/`; change `Gauntlet AI/` first, then re-copy. Added 2026-10-16.

Applies whenever `KEY_METRICS.md`, a metrics tree, a success surface or a dashboard is written or
reviewed. The principles are `principles/business-metrics.md` (GP-131 – GP-144); in a spin-off repo,
`docs/principles/business-metrics.md`. It builds on `problem-framing` (GP-126, GP-127: money hops
and the north star).

## Rules

1. **Every claim has a number [GP-131].** A claim with no metric, source and comparison is labelled
   an opinion.
2. **Two groups, never one [GP-132].** Health metrics (does it run) and value metrics (did the
   customer benefit). A dashboard of health metrics alone is monitoring, not a success surface.
3. **Leading and lagging, paired [GP-133].** Each branch of the tree names one of each and says which
   is which. Leading ones alert; lagging ones settle whether it worked.
4. **No victory from a lagging move [GP-134].** State the comparison group or baseline and what else
   could explain the change. Without one, call the claim an association.
5. **Each metric feeds a decision [GP-135]:** *if it drops below X we do Y*. No decision line → demote
   or remove. Cumulative counters are never headline metrics.
6. **Per what, and for whom [GP-136].** Every headline metric states its unit, denominator and segments.
7. **Match the customer's value [GP-137, GP-144].** Open the framing with the user, the use case and
   what that customer values. Missing information becomes an open question or a labelled assumption.
8. **Small set [GP-138]:** one north star, a few supporting metrics, a short health list.
9. **North star plus explainers [GP-139].** Each supporting metric names how it explains the north
   star's movement.
10. **Coverage and bias [GP-140].** A north star must be computable for every user. Surveys and ratings
    are supporting trends, with their response rate shown.
11. **Engagement is paired with quality [GP-141].**
12. **Baseline, aspiration, hard gate [GP-142].** Each with a label for where it came from
    (measurement, assumption or target; GP-119). No target is a gut call.
13. **Review line and the best objection [GP-143].** Each metric says when it is reviewed. Interview
    prep has the strongest objection to the north star and an answer.

## Review checklist (`KEY_METRICS.md`, metrics tree, success surface)

- [ ] Health metrics and value metrics are in separate, labelled groups.
- [ ] Each branch has a leading and a lagging indicator, marked.
- [ ] Each metric names its decision, unit, denominator and segments.
- [ ] One north star: computable for every user, tied to money by a hop chain, not a counter.
- [ ] Every engagement metric has a quality partner.
- [ ] Baseline (or "none yet"), aspiration and hard gate are present and labelled.
- [ ] A review line and the best objection with an answer are written.
