# Brainlift v2 — open-set tariff classification (2026-11-02)

**Behavior thesis.** Given a product description and the evidence a broker would pull (earlier CBP rulings and
candidate HTSUS lines from a search), a small model trained on CBP's own decisions picks the exact 10-digit code more
often than the same model untrained, because the deciding facts and the code conventions are learnable from rulings.

**Did data → behavior hold? Yes, for judgment over evidence; no, for memory.**

| Final test (500 CBP rulings, Aug 2025 – Oct 2026), same evidence for every model | Exact 10-digit |
|---|---|
| Search alone | 38.0% |
| Base Qwen3-4B-Instruct-2507 | 42.0% |
| **Fine-tuned (released)** | **59.8%** (+17.8, 95% CI +13.6 to +22.0) |
| Claude Opus 5.5 | 71.6% |

- **What the data taught:** choosing among close candidate lines. When the right code was in the search results, the
  tuned model picked it 74.5% of the time against 52.5% for its base.
- **What it did not teach:** codes the search missed. Opus answers 30% of those from memory, the tuned model 1%. Most
  codes appear in only one or two training rulings; extra schedule drills raised closed-book recall (0% → 45.7% on dev)
  but barely moved the score with search (+0.7).
- **Data changes and their effect (dev):** 19.1k rulings → 57.7%; earlier-only retrieval in training + recent rulings
  + schedule lines → 59.3%; + 6,480 backfilled rulings + 488 verified rationales → 59.7%. Rationales taught the format
  of reasoning, not good reasoning (forcing reasoning: 48.0%).

**Why it is still worth deploying.** Same evidence, about 12 points less accurate than Opus, but 0.9 s against 9.9 s
per request on an H100 (about 11× faster) and about 1/150 of the cost per classification in bulk. For a human-reviewed
workflow, a fast cheap first pass with the evidence shown is the use case.

**What would change my mind / next.** The gap lives in rare codes and in retrieval misses (20% of test items). Better
retrieval and many more examples per rare code are the levers.

**Minimum viable dataset.** The data-efficiency curve (same recipe, nested subsets, dev) gives 2,356 → 52.3%,
4,716 → 53.3%, 9,431 → 56.3%, 19,141 → 57.7% (base 42.0%). The behavior appears by about 2,400 rulings; about 9,400 is
the smallest size statistically indistinguishable from the full set, so I state ~9,400 as the minimum viable size.
Training length grew with size (one epoch each), so the two effects are confounded.

Evidence: `docs/evals/results-v2.md`, protocol `docs/evals/benchmark-protocol.md`, data `docs/data/benchmark-v2.md`.
