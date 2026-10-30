<!-- Provenance: copied from Gauntlet AI/.claude/rules/system-design-conversation.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
---
paths:
  - "**/docs/prd/**"
  - "**/docs/design/**"
  - "**/*interview*.md"
  - "**/hard-problems*"
  - "**/ARCHITECTURE*.md"
  - "**/*system-design*.md"
  - "**/SYSTEM_DESIGN*.md"
---

# The System-Design Conversation

> **Provenance:** this is the original. Spin-off repos carry a copy in `.claude/rules/` and the
> principles at `docs/principles/`; change `Gauntlet AI/` first, then re-copy. Added 2026-10-14.

Applies whenever a PRD, interview, hard-problems page, architecture or system design is being
written or discussed. The principles are `principles/system-design.md` (GP-107 – GP-119); in a
spin-off repo, `docs/principles/system-design.md`. The process they support is
`system-design-readiness/GUIDELINE.md`.

## Rules

1. **Walk the questions, don't wait to be asked.** Before a design is called ready, go through each
   principle's *Raise in the design conversation* list. A question the docs already answer gets a
   citation; an open one goes to Innocent **as options** (2–4, recommendation first), never as a
   blank question. **Who answers, when, and what may not be drafted first** is
   `system-design-questioning.md`: the foundation questions (load, peak, failure to survive, spend
   ceiling, hardest uncertainty) are asked before anything that depends on them, and a stand-in such
   as a test load is never an answer.
2. **Economics and scale bucket first [GP-107, GP-108].** No component is chosen before the cost per
   successful outcome and the scale bucket are written down.
3. **Depth where the partner is uncertain [GP-109].** Solved parts get one line each; the uncertain
   part becomes a hard-problem card.
4. **Trace one real operation before sizing anything [GP-112].** A server count, pool size or
   replica number with no traced operation behind it is an assumption, and is labelled as one.
5. **Label every number [GP-119]**: `[T]` target, `[A]` assumption, `[C]` calculation, `[M]`
   measurement. Every major choice ends with its *because → chose → verify → revisit when* sentence.
6. **Per-operation answers [GP-110, GP-114, GP-116].** Promises, overload behaviour and
   consistency-versus-availability are decided per operation, never once for the whole system.
