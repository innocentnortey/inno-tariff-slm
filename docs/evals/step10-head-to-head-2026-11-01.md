# Step 10 head-to-head on the sealed test set — 2026-11-01

**Question.** Does the trained small model match or beat the best frontier prompt on items no model was trained or
tuned on? This is reliability bar B (Innocent, 2026-11-01): match or beat Claude Opus 5.5 with the structured-CoT
prompt v2.

**Answer: not yet.** The tuned model trails Opus by 13 items on spec adherence (78.7% against 84.6%) and by 2 items on
robustness (71.7% against 75.0%). It beats Opus on asking for missing facts and loses on choosing the code,
above all on residual "Other" lines.

## Setup

- Test set: `data/processed/test.jsonl`, 221 items (197 rulings from 2024–2025 + 24 ablated `NEED_INFO` copies),
  frozen (SHA-256 `f46a27fd…`). Robustness: `data/processed/test_robust.jsonl`, 60 items, the same perturbation
  phrasing as the dev robustness set (`766ab664…`).
- Arms, same eight candidates and same prompt v2 for all:
  - A: Claude Opus 5.5, structured CoT, effort high, judge Gemini 3.1 Pro (`runs/prompt-ceiling-20261102-032602/`).
  - B: Qwen3-1.7B base, 4-bit, greedy (`runs/modal/step10-test-base/`).
  - C: Qwen3-1.7B + v2 adapter (`full-n6543-v2`), chosen over v3 on dev before the test was run
    (`runs/modal/step10-test-tuned-v2/`).
- Retrieved rulings were not added to any arm (the first-stage format; the retrieved-rulings question is still open).

## Results

| Test set | B: base | C: tuned v2 | A: Opus 5.5 CoT |
|---|---|---|---|
| Spec adherence | 6.3% (14/221) | 78.7% (174/221) | 84.6% (187/221); judged 82.8% |
| Robustness | 10.0% (6/60) | 71.7% (43/60) | 75.0% (45/60); judged 73.3% |
| Exact 10-digit code (items needing a code) | 17.0% | 77.7% | 89.1% |
| `NEED_INFO` recall (37 items) | 0% | 86.5% | 73.0% |
| Over-asking | 0% | 1.6% | 3.3% |

By kind (spec adherence):

| Kind | n | C: tuned | A: Opus |
|---|---|---|---|
| decide | 110 | 79.1% | 84.5% |
| residual "Other" | 70 | 74.3% | 92.9% |
| unlabelled | 4 | 75.0% | 100% |
| `NEED_INFO` ablated | 24 | 87.5% | 79.2% |
| `NEED_INFO` natural | 13 | 84.6% | 46.2% |

Overlap: 16 items fail both; 31 fail only the tuned model; 18 fail only Opus.

## Reading

- **Training works.** Base to tuned is +72.4 points of spec adherence on unseen 2024–2025 rulings.
- **The tuned model asks better than the frontier model.** On the 13 natural `NEED_INFO` items, where the summary
  genuinely lacks the deciding fact, it asks 11 times; Opus asks 6 times. It also over-asks less.
- **The frontier model chooses codes better.** The gap is concentrated in residual "Other" lines (18 items) and,
  to a lesser degree, decidable items (6 items). Reading v2's dev failures, the residual errors are mostly cases where
  the description uses a word that names the sibling line ("coveralls", "suit-type", "set") but a legal definition
  (Note 3(a), the "sets" note, statistical notes) puts the product in "Other". The definitions are referenced in the
  candidate text but not included, so the small model matches words; Opus brings the definitions from pretraining.
- **The tuned model generalizes less well from dev to test.** Opus: 86.0% dev → 84.6% test. Tuned: 84.7% → 78.7%. Dev
  is 2023, test 2024–2025, and the model trained on rulings up to 2022; v2 was also selected over v3 on dev.
- **Precision.** At these sizes one test item is 0.45 points (clean) and 1.7 points (robustness). The 13-item spec gap
  is larger than the noise; the 2-item robustness gap is not.

## Status of the test set

The test set has now been used for the bar decision. Any further model change must be chosen on dev; a re-test of a
new model on this set must be reported as a second look, not a fresh sealed result.

## Cost

Opus arm $4.35 + judge $0.83. Modal evaluation runs a few minutes of H100 time each.
