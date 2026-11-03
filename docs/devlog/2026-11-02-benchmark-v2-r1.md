# 2026-11-02 — benchmark v2 (open-set) built and baselined

**Changed.** New open-set benchmark: product facts → any 10-digit code, no gold-in-candidates. Track A reproduces
ATLAS (200 items, closed-book); Track B uses 500 rulings fetched from CROSS after the corpus ends (2025-08 → 2026-10),
CBP's own fact sentences, hybrid TF-IDF + bge retrieval (recall@20 dev 74.7%, test 80.0%). Protocol frozen:
`docs/evals/benchmark-protocol.md`; data: `docs/data/benchmark-v2.md`.

**Why.** The earlier benchmark always supplied the answer among eight codes.

**Checked.** Dev `rag`: retrieval-only 36.7%, base Qwen3-4B 42.0%, Opus 5.5 71.3%. ATLAS: Opus 41.0% (paper's
fine-tuned 70B: 40.0%), base 0%.

**Remaining.** Three training tries against the Opus target (Innocent, 2026-11-02); one final-test run.

## Tries 1–3 (2026-11-02)

**Changed.** Try 1 (19.5k rulings) dev 57.7%; try 2 (temporal retrieval, recent rulings, schedule lines) 59.3%; Opus
71.3%. Try 3 adds 488 Codex-judged Opus rationales (labels from CBP) and 6,480 backfilled CROSS rulings, continuing
try 2's adapter. **Why.** The gap is 25 retrieval-miss items and 11 close-code items. **Checked.** Judge rejected all
50 planted controls. **Remaining.** Try 3 dev result; one final test.

## Final test (2026-11-02)

**Checked.** Tuned (try 3) 59.8%, base 42.0%, retrieval-only 38.0%, Opus 71.6% on 500 fresh rulings. Tuned − base
+17.8 (CI +13.6 to +22.0): hypothesis supported. Tuned − Opus −11.8: goal not met. Closed-book the tuned model scores
0%. **Remaining.** Memory follow-up (outside the three tries) on dev. Report: `docs/evals/results-v2.md`.
