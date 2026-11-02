# Gauntlet Week 7 Brainlift

## Behavior thesis

A small tariff model should choose among eight supplied HTS candidates and name the deciding attribute using words from the product description. If that attribute is missing, it should return `NEED_INFO` and name the missing dimension. The thesis is that examples of both decisions and justified abstentions can teach this boundary. Candidate retrieval, duty calculations, and final professional classification remain separate responsibilities. This is the approved [behavior specification](../planning/tariff-behavior-and-evals.md), not a claim to automate customs classification end to end.

## Did data change behavior?

Yes, within the measured task. On the sealed test, Qwen3-1.7B base scored 6.3% spec adherence; the v2 adapter scored 78.7%, against Opus 5.5 structured CoT at 84.6%. Robustness rose from 10.0% to 71.7%, against Opus at 75.0%. All arms received the same candidates; these results measure selection with the gold code available, not retrieval success. [Source: sealed-test head-to-head](../evals/step10-head-to-head-2026-11-01.md).

The clearest targeted change was asking for missing information. v1 learned classification but underlearned abstention. Adding 678 attribute-ablated training copies produced v2: dev `NEED_INFO` recall rose from 61.1% to 94.4%, while over-asking fell from 2.2% to 0.7%. Overall dev adherence rose from 79.0% to 84.7%. Training settings were unchanged, although adding examples increased updates. This supports the data-to-behavior thesis without isolating example composition from training duration. [Source: submission evidence](../../SUBMISSION.md).

The gain also appeared beyond constructed ablations. Test `NEED_INFO` recall was 86.5% for v2 versus 73.0% for Opus; on natural missing-information items, v2 asked correctly on 11/13 versus 6/13. “Natural” refers to the supplied summary: summaries often omit facts present in the original ruling. These are useful missing-input cases, but not necessarily ambiguous original rulings. [Sources: head-to-head](../evals/step10-head-to-head-2026-11-01.md), [label review](../data/label-review-2026-11-01.md).

## Minimum viable dataset

A minimum dataset that meets the agreed reliability bar has not been established. The nested v2 curve measured 500, 1,000, 2,000, 4,000, and 6,543 examples, with dev adherence of 30.6%, 45.2%, 61.8%, 76.4%, and 84.7%. At 4,000 examples, asking first became effective among the tested sizes: recall reached 94.4%, from 0% at 2,000. That makes 4,000 a useful exploratory floor for learning both actions, not a minimum for reliable deployment. [Source: data-efficiency curve](../../runs/modal/data-efficiency-curve-v2.json).

The full 6,543-example dataset was the best measured v2 point, but the curve was still rising and remained below the Opus dev reference of 86.0% adherence and 87.9% robustness. Epochs, not optimizer steps, were held fixed: the smallest and largest runs used 32 and 409 updates. Data quantity and optimization effort are therefore confounded. No saturation point or sufficient minimum follows from this experiment. [Sources: submission](../../SUBMISSION.md), [prompt ceiling](../evals/prompt-ceiling-2026-11-01.md).

## What did not work and why

v3 added 1,290 perturbed examples. Dev adherence fell to 82.2%, while robustness stayed at 82.8%. The verified review found that v3 fixed three robustness items and broke three others. The broad augmentation mix produced no net gain; this does not establish that perturbation training cannot help. v2 itself had four clean-to-perturbed regressions, so genuine sensitivity remained. [Sources: training devlog](../devlog/2026-11-01-training-r1.md), [verified review note](../reviews/2026-11-01-codex-astra-improvement-review.md).

v2 did not meet reliability bar B, which requires matching or beating Opus on both measures on the same test items. Residual “Other” lines exposed the main weakness: v2 scored 74.3% versus Opus at 92.9%. The head-to-head diagnosis points to word matching where legal definitions or earlier schedule branches control the answer; referenced definitions were not included in candidate text. This is an interpretation of failures, not a controlled causal result. [Source: head-to-head](../evals/step10-head-to-head-2026-11-01.md).

Coverage and labels also constrain the conclusion. The verified review found 12/22 correct selections on unseen gold codes versus 104/117 on seen codes, and 72% of ordinary training decisions were gender splits. Label review found contradictions and summary omissions. Residual and unlabelled items are scored on code only, so aggregate adherence does not verify every part of the intended attribute-grounding behavior. [Sources: verified review](../reviews/2026-11-01-codex-astra-improvement-review.md), [label review](../data/label-review-2026-11-01.md).

## Later dev experiments

Later that night, v4 downsampled gender splits and the knit-to-shape family and repeated rare branches without adding new labels ([builder](../../scripts/make_train_v4.py)). With two epochs, it reached 137/157 clean and 52/58 robust, above the Opus dev reference of 135/157 and 51/58. Rebalancing alone reached 133/157 and 49/58; two epochs on v2 reached 135/157 and 49/58. Neither alone cleared both measures. [Sources: v4 plus two epochs](../../runs/modal/v4-rebal-2ep/meta.json), [v4](../../runs/modal/v4-rebal/meta.json), [v2 plus two epochs](../../runs/modal/v2-2ep/meta.json), [Opus](../evals/prompt-ceiling-2026-11-01.md).

These are single-seed dev results. A second v2 seed scored 127/157 versus the original 133/157: observed seed variation is about six items, not an estimated uncertainty interval. Qwen3-4B on v2 reached 138/157 clean and 50/58 robust, still short on robustness. The v4 result is promising evidence for confirmation, not a replacement for the sealed-test finding. [Sources: second seed](../../runs/modal/v2-seed8/meta.json), [original v2](../../runs/modal/full-n6543-v2/meta.json), [4B](../../runs/modal/v2-qwen4b/meta.json).

## Next steps

[PENDING: confirmation seed]

**Test second look (v4 plus two epochs, chosen on dev before this look).** On the 221 sealed-test items it scored 81.0% spec adherence (179/221) against v2's 78.7% (174/221) and Opus's 84.6% (187/221); robustness 75.0% (45/60), tying Opus (45/60); `NEED_INFO` recall 89.2% against Opus's 73.0%. The dev gain carried over (+5 clean, +2 robust over v2), but the model remains 8 items short of Opus on clean adherence, so bar B is still not met on test, and it again fell from dev (87.3%) to test (81.0%). Because the test set had already informed the bar decision, this is a second look, not a fresh sealed result. [Source: `runs/modal/test2-v4-rebal-2ep/`.]

Confirm v4 plus two epochs before drawing a stronger conclusion. Any further test evaluation must be labelled a second look because the sealed set has already informed the bar decision. Next experiments should equalize optimizer steps across dataset sizes, improve rare-branch coverage and source fidelity, and test paired perturbations. Independent label review and human calibration of the judge remain necessary. Publish the frozen data, checkpoint, and reproduction record; the staff held-out evaluation remains outstanding. [Sources: head-to-head](../evals/step10-head-to-head-2026-11-01.md), [prompt ceiling](../evals/prompt-ceiling-2026-11-01.md), [submission](../../SUBMISSION.md).
