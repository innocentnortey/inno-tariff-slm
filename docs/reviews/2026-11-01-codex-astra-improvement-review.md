> **Review by Codex (GPT-6 Astra, `xhigh`, read-only), 2026-11-01. Verified by Claude the same day** against the data:
> coverage 12/22 unseen vs 104/117 seen ✓; robustness sources 52/58 clean → 48/58 perturbed, 4 regressions ✓ (this
> corrects Claude's earlier claim that robustness failures were residual items failing either way); v3 fixed 3 and broke
> 3 robustness items ✓ (corrects "v3 changed nothing"); 72% of decide training items are gender splits, 1 of 678 v2
> ablations is `use` ✓; 120 non-bare-"Other" training residuals ✓; the "without fourchettes" label bug ✓ (the label
> cites "Knit"). Scorer vulnerabilities (a value of "." passes grounding; a NEED_INFO answer with a non-null code
> passes) confirmed by reading `checks.py`. The Codex brief is reproducible from the session; no files were changed.

**v2 is close to the reference score, but the remaining gap is a mixture of schedule-path errors, sparse training coverage, genuine perturbation sensitivity, and imperfect labels. I would prioritize targeted data work before increasing model size or sweeping hyperparameters.**

I inspected all 24 clean-dev failures and all 10 robustness failures, rescored the predictions, and checked selected descriptions against the original rulings. The supplied dev and training checksums match. No files were changed, and I did not inspect the pending test results.

**The failure analysis changes the diagnosis in several important ways.**

| Measurement | Verified result |
|---|---:|
| Clean spec passes | 133/157 |
| Clean failures | 15 residual, 7 ordinary SELECT, 1 unlabelled SELECT, 1 NEED_INFO |
| Robustness passes | 48/58 |
| Robustness failures | 4 residual code errors, 4 ordinary code errors, 1 attribute/quote error, 1 NEED_INFO error |
| Those same 58 items, before perturbation | 52/58 |
| Perturbation-induced regressions | 4; no compensating improvements |
| Dev SELECT accuracy on gold codes absent from training | 12/22, **54.5%** |
| Dev SELECT accuracy on gold codes present in training | 104/117, **88.9%** |

These results come from the [clean predictions](/Users/innocentnortey/Desktop/Nortorious-Technologies/inno-tariff-slm/runs/modal/full-n6543-v2/predictions-dev.jsonl) and [robustness predictions](/Users/innocentnortey/Desktop/Nortorious-Technologies/inno-tariff-slm/runs/modal/full-n6543-v2/predictions-robust.jsonl).

Matching the recorded Opus dev cell requires **two additional clean passes and three additional robustness passes**, without regressions. That is plausible, but small enough that noise or benchmark-specific fitting could also produce it.

The inspected failures support five conclusions:

- **The model often recognizes a word but follows the wrong schedule branch.** `NYN335632` says disposable nonwoven coveralls for contaminated areas, yet v2 chooses the generic coveralls branch, `6210.10.90.10`, instead of `6210.10.50.90`. `NYN334254` explicitly says “undershirt,” but v2 chooses the women’s tank-top branch. `NYN335606` explicitly says water resistant and DWR, but v2 chooses the non-water-resistant branch and cites gender. These are failures to prioritize controlling predicates over familiar product or wearer words.
- **Residual errors are not one homogeneous “choose Other” problem.** `NYN334245` chooses “Imported as parts of playsuits” without such evidence. `NYN332996` confuses a suit-type jacket with a jacket for a qualifying suit. `NYN333353` chooses “Sets” despite the description explicitly saying the articles do not meet the retail-set requirements. `NYN334685` and `NYN330352` select the named tank-top line rather than CBP’s residual line. Different mechanisms—unsupported positive attributes, negation, and specialized definitions—need different training examples.
- **There is real perturbation sensitivity.** `NYN332157`, `NYN336937`, and `NYN331506` pass clean and fail after injection; `NYN332867` passes clean and fails after formatting changes. The raincoat `NYN332157` still selects the correct code but changes its dimension to `fiber_content` and supplies a null quote. Thus the claim that robustness failures are residual items failing either way is incorrect. The matched-source deterioration is **89.7% → 82.8%, or 6.9 points**.
- **Some failures are not clean evidence against the model.** `NYN336500` lacks the two-color warp/filling fact required by its gold path. `NYN334627` omits the 17.5-micron wool measurement present in the ruling. `NYN336767` loses the cotton percentages. `NYN331506` loses the ruling’s statement that textiles constitute less than half the glove’s weight. Most seriously, `NYN329875` says “no vent holes,” while the ruling says there are numerous vent holes and the shoe is not designed to be waterproof.
- **Coverage matters, although the relationship is not necessarily causal.** Ten of the 24 clean failures have gold codes absent from training. The failing robustness items `NYN332157`, `NYN337067`, and `NYN335632` have no training examples with their gold code. Conversely, familiar codes can still fail: `NYN329875`’s gold code has 85 training examples. More examples alone will not fix missing facts or misunderstood distinctions.

The training distribution reinforces this diagnosis. Of 3,644 ordinary SELECT training examples, 2,629—72%—have gender as the deciding dimension. Of 1,814 residual examples, 752 compare Other against knit-to-shape. Meanwhile, only **one** of the 678 added ablations concerns `use`.

v2 fixed asking effectively, but its robustness gain contains a trade-off: NEED_INFO passes rose from 11 to 17, while SELECT spec passes fell from 35 to 31. v3 then fixed three v2 robustness failures and broke three previously passing items. Its identical aggregate and per-perturbation rates therefore conceal movement; they do not prove augmentation cannot help.

The implementation does not suggest an immediate formatting or truncation bottleneck: v2 has 100% parsed JSON/schema validity, no training examples were dropped for length, and clean SELECT spec accuracy equals code accuracy. Increasing context length or adding JSON constraints is unlikely to close this gap.

**I would rank the improvement options below.** Effect ranges are speculative *upside estimates in percentage points*, not forecasts or additive gains. Every option can regress. GPU estimates use your measured run times; API costs exclude human review.

1. **Data: rebalance training around verified residual and hierarchical contrasts.**

   Build a bounded collection of genuine CBP examples contrasting named lines with residual siblings: underwear versus ordinary tops, contamination-use apparel versus generic garments, qualifying sets versus multiple articles, specialized material predicates, and positive versus absent attributes. Include both sides of each distinction. Cap duplication and reduce domination by the knit-to-shape residual family.

   The mechanism is learning which earlier branch controls the classification before applying easy gender distinctions. Do not manufacture opposite-code examples by changing a word: use independently supported rulings.

   **Plausible upside:** clean +1–4; robust +0–5. Medium confidence in direction, low confidence in magnitude. **Cost:** approximately 20–25 H100 minutes; $0 API. **Risk:** overlearning the few dev families or developing an “always Other” bias. **Measure:** frozen-dev residual accuracy, named-line accuracy, over-asking, and separate results for known versus unseen codes. Require gains across multiple families, not just the cited IDs.

2. **Data: repair source fidelity and product-to-code alignment in training.**

   Audit a stratified training sample, then repair the identified patterns throughout training: missing percentages, scope of percentages, negation, garment geometry, and descriptions combining multiple products. Prefer extractive factual passages from the ruling; exclude classification conclusions and code-bearing text from model inputs.

   This is more than restoring omitted facts. `NYN335404` demonstrates that a single-code HF field can accompany a ruling covering both a shirt and trousers with different codes. The summary combines them, and the model’s request for garment information is defensible.

   **Plausible upside:** clean +0–3; robust +0–4. Medium confidence that supervision improves, low confidence that the frozen scores improve. **Cost:** 15–20 H100 minutes after the audit; $0 API with manual/extractive preparation. **Risk:** accidentally copying the answer into the description, or repairing training toward a policy inconsistent with frozen labels. **Measure:** source-fidelity error rate on an independent training audit, plus dev results partitioned into clear model errors and disputed items. Keep the official denominator unchanged.

3. **Data: replace broad augmentation with balanced, paired invariance examples.**

   Retain clean examples alongside perturbations, concentrating on underrepresented schedule distinctions and attribute grounding. Include several instruction locations and wording patterns, candidate permutations, and formatting changes. Preserve controlling facts and validate meanings beyond the lexicon’s presence check.

   The four observed clean-to-perturbed regressions justify this narrower experiment. v3’s three repairs and three regressions suggest that retaining clean behavior and balancing families matter.

   **Plausible upside:** clean +0–1; robust +2–5. Low-to-medium confidence. **Cost:** approximately 20–25 H100 minutes; $0 API. **Risk:** memorizing attack templates, diluting useful examples, or repeating v3’s regressions. **Measure:** matched-source pass→fail rates, code consistency, attribute consistency, and clean performance. Add a separately frozen diagnostic set with new perturbation wording; do not select on the same 58 items alone.

4. **Data: recover additional authoritative examples within chapters 61/62/64.**

   Start with pre-2023 rulings excluded because summaries lost facts, including the 124 decision-5 exclusions. Then consider multi-product rulings only where factual passages and CBP codes can be aligned unambiguously. Apply product/ruling-family deduplication before splitting.

   This could supply rare distinctions and codes rather than repeating existing descriptions. The 54,558-row raw file is not 54,558 suitable training examples; yield is unknown. I would not begin by adding unrelated chapters or automatically mapping obsolete codes to current ones.

   **Plausible upside:** clean +1–4; robust +0–5 if several hundred useful examples are recovered. Low confidence until the yield audit. **Cost:** roughly 20–30 H100 minutes for a modest expansion; $0 API using source-based extraction and review. **Risk:** code-product misalignment, temporal schedule mismatch, and near-duplicate leakage. **Measure:** coverage growth, unseen-code performance, and a diagnostic holdout drawn from recovered rulings never used by v1–v3.

5. **Data/input representation: expose schedule structure and authoritative notes explicitly.**

   Render a shared tree or consistently indented paths, and supply relevant USITC definitions/notes selected from **all candidate codes**, independently of the gold label. Never expose dataset fields such as `gold_node` or the gold-derived `nearest_sibling`.

   This addresses requirements that leaf text does not explain: qualifying suits, footwear categories, or other defined terms. USITC describes the HTS as categories defined partly by legal rules and notes, rather than a product-name lookup. [USITC explanation](https://www.usitc.gov/harmonized_tariff_information/frequently_asked_questions)

   **Plausible upside:** clean +0–4; robust +0–5. Low confidence. **Cost:** approximately 20–35 H100 minutes; an additional frontier dev comparison would be roughly **$4 at the recorded $0.018/decision**, before judging and extra-context costs. **Risk:** this changes the input condition and can leak labels through selective context. **Measure:** identical enriched context for both models, with retrieval/context errors reported separately. This is a new comparison arm, not a fair comparison against the old frontier score alone.

6. **Training configuration: test additional exposure with a controlled update budget.**

   The existing curve holds epochs constant, not optimizer steps: 500 examples receive 32 updates, while 6,543 receive 409. “Still rising” therefore does not establish a pure data-scaling effect, and the apparent NEED_INFO emergence threshold is confounded with training duration.

   Run one narrowly specified exposure experiment, keeping rank, learning rate, objective, and data fixed—for example, two epochs with checkpoints at predetermined points. A 4k-example control trained for approximately 409 updates would help separate exposure from data diversity.

   **Plausible upside:** clean +0–3; robust +0–4, with credible regression risk. Low confidence. **Cost:** approximately 30–40 H100 minutes for the full two-epoch run; another 10–15 for the optional control; $0 API. **Risk:** memorizing noisy labels and selecting a lucky checkpoint. **Measure:** whole-dev and robustness results at preregistered checkpoints, particularly unseen codes and residuals. Low JSON-token loss alone is not evidence that classification has converged.

7. **Model configuration: try Qwen3-4B only after the targeted data experiments.**

   Use the same selected data, prompt, objective, and evaluation protocol. This tests whether capacity limits integration of multiple path predicates. A [Qwen3-4B checkpoint exists](https://huggingface.co/Qwen/Qwen3-4B), but nothing measured here establishes that model size is the limiting factor.

   **Plausible upside:** clean +0–4; robust +0–7. Low confidence. **Cost:** budget approximately 30–50 H100 minutes initially; $0 API; measure rather than assume deployment cost. **Risk:** greater inference expense without fixing contradictory inputs. **Measure:** paired dev gains concentrated on clear reasoning errors, plus latency and cost. Reject a larger model that only improves disputed cases or fails the economic objective.

**The current scores are useful experimental measurements, but they overstate some aspects of the behavior and understate others.**

- **“Spec adherence” is weaker than the written contract.** The [scorer](/Users/innocentnortey/Desktop/Nortorious-Technologies/inno-tariff-slm/src/tariff_slm/evals/checks.py:41) does not validate runner-up membership or correctness, require null code/value fields for NEED_INFO, enforce the 1–6-word limit, or require JSON-only output. Residual and unlabelled SELECT items do not need meaningful attributes. That exemption covers 64/157 clean items.

  Grounding is merely a case-insensitive substring check. I verified in memory that a value of `"."` passes because stripping produces an empty string, and that a malformed NEED_INFO answer with a non-null code and invented value can pass. These are scorer vulnerabilities, **not evidence that v2 exploited them**. Preserve the frozen metric and add a stricter supplementary audit applied equally to both models.

- **Labels inspect one sibling, although selection must resolve all eight candidates.** `NYN336500` gets a gender label because its nearest sibling is boys’, while the unresolved distinction against another candidate is fabric coloration. Decision 5 does not eliminate missing facts at earlier branches.

  `NYN329836-ablated` illustrates the opposite problem: it is labelled NEED_INFO from athletic footwear versus slippers, but the candidate list also contains residual footwear. Its selection of a residual code is consistent with a broad reading of the prompt’s “missing attribute → Other” rule. The ablation also retains the visible cut artifact “-like projections.” This is not a clean measure of asking competence.

- **Absence from a summary is not proof that a product lacks an attribute.** The residual policy deliberately treats those as equivalent. That can reward confident defaults and penalize justified questions. Freeze that policy for the existing benchmark, but describe it as a benchmark convention rather than general tariff reasoning.

- **The label implementation remains less semantic than its documentation implies.** Outside gender, fibers, and a few special cases, `evidence()` often returns the first dimension word. For example, “gloves **without** fourchettes” supplies `fourchettes` as evidence for a **with**-fourchettes line. Also, [dataset construction](/Users/innocentnortey/Desktop/Nortorious-Technologies/inno-tariff-slm/scripts/build_dataset.py:80) uses `startswith("other")`, while attribute logic distinguishes bare Other from qualified phrases. There are 120 training residuals whose divergent node is not bare Other.

- **Authority does not eliminate input/label inconsistency.** `NYN332360` is a 100% polyester gaiter, yet its ruling assigns the code represented by the supplied schedule as Other/Other; v2 chooses the man-made-fiber branch. I would flag this for schedule/source reconciliation, not confidently classify it as model error. Conversely, repairing an ambiguous benchmark after seeing predictions can inflate scores. Keep corrections in a versioned successor benchmark.

- **Robustness has a different mixture and limited independence.** NEED_INFO constitutes 18/58 robustness items versus 18/157 clean items. The 58 perturbations represent 55 underlying rulings, and each source receives only one perturbation. Consequently, 84.7% versus 82.8% is not the perturbation effect. Report the matched 52→48 result, conditional retention, and cluster uncertainty by ruling.

- **The split is chronological, but not a pristine blind holdout.** The label review sampled test items, and test baselines were already observed. Describe it as frozen after label engineering. Exact normalized-description deduplication does not remove similar products, revised rulings, or related styles. A code remaining valid in the current schedule also does not establish unchanged meaning since the original ruling.

- **The judge does not resolve these issues.** It is uncalibrated, cannot rescue deterministic false negatives, and does not enforce residual explanations in the reported judged score. Moreover, `judge_agrees_on_decide_selects` is the share receiving judge approval, not a full agreement calculation against deterministic judgments.

**The frontier comparison is fair for the narrow, frozen decision task, provided both models receive identical information and use the same scoring gate.** It does not demonstrate end-to-end tariff reliability or that fine-tuning beats a strong retrieval system. Oracle candidate inclusion and the reported 4% BM25 recall@8 make that distinction substantial.

The observed differences also do not establish statistical superiority. On clean dev, Opus uniquely passes 13 items and v2 uniquely passes 11; on robustness, the corresponding counts are five and two. Approximate unclustered 95% intervals for v2 are 78–90% clean and 71–90% robust. The actual uncertainty is not captured by a one-decimal leaderboard.

For test, use the **actual paired Opus result** for the relative bar. Report fixed absolute thresholds separately if they remain mandatory. Avoid threshold decisions based on rounded percentages: the reference clean score is 135/157, displayed as 86.0%.

**My next sequence would be bounded and precommitted.**

1. Preserve v2 and the current test run as the original experiment. Keep pending test outcomes out of subsequent data selection.
2. Create an error ledger separating clear model failures, missing/misstated facts, and policy conflicts. Audit training counterparts of those *patterns*, including correct examples.
3. Freeze a small additional diagnostic holdout from unused, recovered pre-2023 rulings, grouped by product/ruling family.
4. Run the residual/hierarchy data intervention first. Then choose source repair or paired augmentation according to that audit; change one substantive factor per run.
5. Allow at most **three exploratory training runs**, with one being the exposure control if data changes stall. Reserve one independent-seed confirmation for a candidate that reaches at least the reference counts of **135/157 clean and 51/58 robust**, with supporting diagnostic gains and no material asking regression.
6. Stop early on a confirmed candidate. If the bounded experiments fail, retain v2 and report that the chosen reliability bar was not demonstrated. Do not keep querying test to select successors; once test outcomes influence choices, subsequent claims require a fresh holdout.

The strongest immediate opportunity is teaching the model to respect controlling schedule branches while preserving v2’s improved asking behavior. The evidence does not support treating every remaining residual failure as learnable from the supplied description.