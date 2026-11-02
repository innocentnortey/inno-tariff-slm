# Label review — 2026-11-01

**Who and why.** Innocent delegated the Step 1 label review to Claude on 2026-11-01: "to be honest i dont need to
review it i trust you to do a better job than me of identifying what makes sense". This record is that review.

**What was reviewed.** Not the HTS codes: those come from CBP rulings and are trusted. The review checked the labels
our build derives from the schedule wording with a word list (`src/tariff_slm/data/attributes.py`):

- the *deciding dimension* (for example `gender_age` for "For men" against "For women");
- the *value* the model must quote (for example "Men's");
- the *decision*: `SELECT`, or `NEED_INFO` when the description doesn't state the deciding fact;
- the *ablated* copies, where the attribute words are removed on purpose.

The scorer (`src/tariff_slm/evals/checks.py`) fails a model on decidable and `NEED_INFO` items when the dimension or
decision label is wrong, so those are the labels that matter. Residual ("Other") and unlabelled items are scored on
the code only.

## Method

1. **Pattern audit of every item** (6,412 before the fixes): every distinct pair of gold-line and sibling-line
   wording with the dimension the build gave it (184 patterns), plus scripted checks for gender values that
   contradict the gold line, fiber values from the wrong family, and `NEED_INFO` items whose original ruling states
   the attribute.
2. **Read 50 items**, stratified by kind and weighted to dev and test (seed `20261101`), against the original ruling
   text where the label depends on what the summary kept.
3. **Fix the patterns in code**, never by editing a label, and add each reviewed case as a regression test
   (`tests/test_attributes.py`, 25 tests after round 3).
4. **Read a fresh 50** (seed `20261102`) after the fixes, fix what it found, and re-check every reviewed item by
   script.

Sampling scripts were scratch files; the sample IDs are reproducible from the seeds and the stratification
(decide 12, residual 8, unlabelled 5, natural `NEED_INFO` 13, ablated `NEED_INFO` 12).

## Results

| Round | Correct | Clear errors | Judgment calls |
|---|---|---|---|
| 1 (before fixes) | 38 | 8 | 4 |
| 2 (after round-1 fixes, fresh sample) | 43 | 5 | 2 |

After the round-2 fixes, every item flagged in both rounds carries the intended label (checked by script).

## Error patterns and fixes

| Pattern | Example from the sample | Items affected (full set) | Fix |
|---|---|---|---|
| Fiber value is the first fiber listed, not the one the line is about | Poncho "52% acrylic and 48% wool" cited "acrylic" for a ≥23% wool line | 44 | Fiber families; the cited fiber must be in the gold line's family, and a threshold line needs a stated percentage at or above it ("48% wool") |
| "5% or more elastomeric yarn" lines labelled `material`, so "22% spandex" counted as missing | Women's bodysuit, 78% nylon / 22% spandex, labelled `NEED_INFO` | ≈37 | `elastomeric`, `lycra` and more fibers added; the line is now fiber, and the item is decidable |
| Garment and use words missing; "ski-jackets" read as a sport | Raincoat (overcoat against anorak) labelled `use`; "sneaker" and "soccer shoe" not recognised | dozens; unlabelled items fell from 411 to 49 | Lexicon additions; the dimension is the first one on which the two lines actually differ ("Gloves" against "Ice hockey gloves" is use), with "with/without" seen as a difference |
| Gender word that doesn't separate the two lines, or points at the sibling | "adult" cited for a girls' line; one description covering a men's jacket and a women's vest | ≈10 wrong cites; 83 conflicting items dropped in total | Wearer categories; the cited word must support the gold line over the sibling; any wearer word pointing only at the sibling drops the item as a conflict |
| "Knit" cited as evidence for "knit to shape" | Rib-knit pullover on a knit-to-shape line | 68 | Requires "knit to shape", "fully fashioned" or "knit … to their final shape"; otherwise `NEED_INFO` |
| Ablated copies show where words were cut | "a , closed toe…", "garments for / ,", "72. aramid", ";,", "a open-toe" | 4 of 12 sampled ablations | Fiber phrases removed with their percentages; a copy with any cut mark, or that still states the attribute, is rejected (8 rejected) |
| Possessives produced odd values | "girl'" | 70+ | Possessive-aware patterns ("girl's", "boys'", "men’s") |

## Decisions on the judgment calls

These are label policy, not lexicon bugs. Each is recorded so a later change is deliberate.

1. **Unisex.** "Unisex" is a valid deciding value for women's lines against men's lines. CBP rulings quote the
   rule: Chapter 62 Note 8, "Garments which cannot be identified as either men's or boys' garments or as women's or
   girls' garments, are to be classified in the headings covering women's or girls' garments" (29 rulings, e.g.
   NY K85566), and footwear "commonly worn by both sexes" (63 rulings). It does not separate women's from girls'.
2. **Unstated wearer on men's/boys' against women's/girls' lines: keep `NEED_INFO`.** The legal default above
   applies to a garment CBP examined and could not identify. A description that leaves the wearer out is
   different, and asking is the safer product behavior. Items affected: the natural and ablated `NEED_INFO` items
   on those lines.
3. **Facts a reader can infer but the lexicon can't see: keep the label, accept the noise.** *Revised after the
   prompt-ceiling run (see round 3): "upper body garment" against a coverall line is now decidable, because both
   frontier models chose CBP's code from it.* Original reasoning, kept for the record: Examples: "pocket
   for protective sport cup" (men's), "upper body garment extending below the hips" (a jacket, not a coverall),
   "neck size and sleeve length" (men's, not boys'). Two to three such items per 50. A strong model that decides
   them is marked wrong; the judge check in the eval plan is where this gets measured.
4. **Residual "Other" stays decided by absence.** One known hole: coated work gloves are "Other" because the
   coating is over 50% of the weight, a fact only the original ruling states. Residuals are scored on the code
   only, so no attribute is penalised.

5. **An attribute line whose sibling is "Other", with the attribute unstated: drop the item** (added in round 3).
   "Other" is what the schedule assigns when a product lacks the attribute, so from the description alone the answer
   is "Other". CBP chose the attribute line only because the original ruling stated a fact the summary dropped.
   Labelling these `NEED_INFO` (as before) contradicted the residual items, where the same missing attribute is
   labelled "choose Other": identical inputs, opposite labels. Dropped: 124 train, 6 dev, 4 test items (73 of the
   train items are knit-to-shape lines). `NEED_INFO` now covers only forks where both lines name an attribute (men's
   against women's, cotton against man-made), where a missing fact truly blocks the choice.

## Round 3 — label-side failures found by the prompt-ceiling run

The first full prompt-ceiling run (`runs/prompt-ceiling-20261102-005624/`) was read item by item. Of the 10
`NEED_INFO` items where Claude Opus 5.5 (zero-shot) chose a code, 4 were label errors (the model chose CBP's code with
valid evidence: a removed-attribute copy that still said "brief", "undershirt", and two "upper body garment" items) and
4 were the contradiction in decision 5; 2 were genuine failures to ask. Fixes: "brief" and "undershirt" as garment
words, "DWR" as water resistance, "upper body garment" against coverall lines, three more cut-mark patterns
("made of and", "making it;", "women's crafted from"), and decision 5. Four more regression tests (25 in total).
The 10 wrong codes on residual items were read too: they are model-side (the unisex footwear rule, tank top against
T-shirt by neckline, essential character of a mixed upper) or depend on facts the summary dropped, not label bugs.

## Facts the summaries drop

The model's input is the dataset's model-written summary, not CBP's text. In about 280 of 464 natural `NEED_INFO`
items (before the fixes), the original ruling's facts state the attribute and the summary dropped it. Asking is
still correct for the input the model sees, and it mimics an importer leaving a fact out, but "natural" ambiguity
is mostly created by the summarizer. Say so wherever these items are described.

## Effect on the dataset and baselines

| | Before (2026-10-30) | After (2026-11-01) |
|---|---|---|
| Train items | 6,064 | 5,987 |
| Dev items (rulings + ablated) | 165 (146 + 19) | 161 (143 + 18) |
| Test items (rulings + ablated) | 235 (202 + 33) | 227 (199 + 28) |
| Test kinds | decide 102 · residual 62 · unlabelled 21 · natural 17 · ablated 33 | decide 105 · residual 70 · unlabelled 4 · natural 20 · ablated 28 |
| Dropped as conflicting | — | 83 |
| After round 3 (decision 5 and its fixes) | — | train 5,865 · dev 157 (143 + 14) · test 221 (197 + 24); 124 more items dropped |

Non-model baselines on the test set (exact 10-digit on items that need a code; runs `runs/20261101-184129-*`):

| Baseline | Before | After |
|---|---|---|
| Random | 10.3% | 10.1% |
| Keyword overlap | 14.1% | 16.8% |
| Attribute rules | 20.5% | 40.8% (spec pass 28.6%, `NEED_INFO` recall 35%, over-asking 5%) |

The rules baseline uses the same lexicon, so most of its gain is the lexicon fixes: on the old test file the new
code scores 36.8% (`runs/20261101-184140-*`). Its attribute scores remain optimistic for that reason. Its code
accuracy is scored against CBP's codes, though, so about 41% is now the bar a trained model has to clear.

## Limits of this review

- It is a review by Claude, who also wrote the lexicon, not an independent human review.
- The eval plan's LLM judge still needs about 20 human labels before it enters the gate (rule
  `verification-evals-observability`, item 14). This delegation covered the derived labels, not that calibration.
- 100 items read in total; the pattern audit covers every item but only for error types it can detect.
