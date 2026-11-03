# Benchmark v2 protocol: open-set 10-digit HTSUS classification

Status: **frozen 2026-11-02**, after the dev baselines below and before any tuned model was evaluated. After freezing, a change needs its own dated entry under *Changes*, and any number produced under the
old protocol stays labelled with it.

## What is measured

Given a product description, a model must output the single 10-digit HTSUS statistical reporting number that CBP
assigned in its ruling. Nothing in the input contains the answer. If retrieval is used, it is our own search, and an
item whose code the search did not find still counts in the denominator.

**Example.** Ruling NY N360000 (2026-04-03). Input: *Product: a data processing server. Description: The merchandise
under consideration is identified as the Dell PowerEdge R7625 Server. The subject device is described as a scalable,
rack-style database/data processing server…* Expected output: `CODE: 8471.50.01.50`. The model may see earlier
rulings and HTSUS lines found by search; it never sees a list that is guaranteed to contain `8471.50.01.50`.

## Tracks

| | Track A: ATLAS reproduction | Track B: primary benchmark |
|---|---|---|
| Items | ATLAS test split, 200 items | Fresh CROSS rulings issued after the HF corpus ends (Aug 2025 → Oct 2026), 500-item sample; dev: 300 items from 2024 → Jul 2025 |
| Input | ATLAS question verbatim: "What is the HTS US Code for …?" | CBP's own fact sentences from the ruling + its subject-line product name |
| Reference given | None (closed-book), as in ATLAS | `rag`: 5 earlier rulings + 20 HTSUS lines from our retrieval; `closed`: none |
| Label | ATLAS's code | The ruling's single primary code, present in the current HTSUS export (2026-10-30) |
| Scoring | Exact 10-digit, 6-digit, average leading digits correct | Exact 10-digit (primary); 8-, 6-, 4-, 2-digit; valid-code rate |

### ATLAS: what we reproduce and where we differ

ATLAS (arXiv 2509.18400, v1) builds 18,731 CROSS rulings into question/answer pairs with GPT-4o-mini, splits them
at random into 18,254 / 200 / 200, asks each model the question closed-book, and scores exact 10-digit, 6-digit and
average digits correct. Reported: Atlas (fine-tuned LLaMA-3.3-70B) 40.0% / 57.5%; GPT-5-Thinking 25.0% / 55.5%;
Gemini-2.5-Pro-Thinking 13.5% / 31.0%; base LLaMA-3.3-70B 2.1% / 20.7%.

- **Data source.** The `flexifyai` HF repos are no longer public. We use the public copy
  `Dayanand314Krishna/cross_rulings_hts_dataset_for_tariffs` at revision `0a66ad34`, whose split sizes match the
  paper exactly. SHA-256: test `58e2d071…5c18`, validation `36900c8b…b5d1`, train `0d2af9dc…de4877`.
- **Prompt.** ATLAS does not publish its evaluation prompt. We send its question verbatim and add a system message
  that sets the task and asks for a final `CODE:` line so that answers can be parsed. The system message is the same
  for every model.
- **Digit average.** ATLAS does not define "average digits correct". We count leading digits that agree (0–10).
- **Labels.** ATLAS labels are not checked against any schedule version; 32 of the 200 test codes are not in the
  current HTSUS. We score against ATLAS's label as given and also report the 168-item subset with current codes.
- **Leakage in ATLAS itself.** Descriptions were written by GPT-4o-mini while it could see the code, and the split
  is random, so near-identical rulings can sit in train and test. We do not correct this; it is why Track A is a
  reproduction, not our primary evidence.
- **Models.** We cannot run GPT-5-Thinking or LLaMA-3.3-70B. Track A uses the models available to us.

### Why Track B is primary

- **Fresh items.** Every Track B test ruling was issued after the newest ruling in any training data we use, and
  after the corpus our earlier work inspected. Rulings were fetched one by one from CROSS
  (`scripts/fetch_cross_recent.py`).
- **Faithful, answer-free descriptions.** Descriptions are CBP's own sentences, not a model's summary
  (`src/tariff_slm/openset/facts.py`). We keep the fact span (the HQ `FACTS` section, or the NY sentences before the
  analysis) and drop every sentence that names a tariff number, heading, chapter, note, a proposed classification,
  duty, or letter boilerplate. A final check rejects any description containing the code's first 4 or 6 digits.
- **Schedule alignment.** Labels must exist in the current HTSUS export, which matches the test rulings' dates
  (2025-08 → 2026-10). Older rulings whose codes no longer exist are dropped, not remapped.
- **Realistic retrieval, misses counted.** See below.

## Retrieval (Track B `rag` mode)

Two indexes, each searched two ways: TF-IDF and dense embeddings (`BAAI/bge-base-en-v1.5`), fused at equal weight
(`src/tariff_slm/openset/retrieval.py`, settings in `CONFIG`). The dense side was added after a probe on 800 dev-pool
rulings that are not in the dev eval sample: recall@20 rose from 70.8% (TF-IDF only) to 76.0%, recall@40 from 75.1%
to 80.6% (`train/modal_retrieval_probe.py`, 2026-11-02). Expanding every top subheading to all its lines was also
tried and gave less (77.2% at 60 lines). The indexes:

1. **Precedents:** earlier rulings (product + description → code). Dev items search train rulings (≤ 2023); test
   items search train + dev-pool rulings (≤ 2025-08-01). No item ever sees a ruling from its own period or later.
2. **Schedule:** the full heading-to-line text of every 10-digit HTSUS line.

Codes from both are fused by reciprocal rank. The prompt shows the 5 most similar precedents (with codes) and the top
20 fused codes with their HTSUS text. Any ruling at cosine ≥ 0.90 to the query is hidden, so a reissued copy of the
same ruling cannot answer it. Eval items with such a near-copy among earlier rulings are dropped from the eval set.
Recall@k of the gold code is reported for every run, and accuracy is split by whether the gold code was retrieved.

## Models and arms

| Arm | Model | Modes |
|---|---|---|
| Retrieval only | Top fused candidate, no model | `rag` |
| Base small model | Qwen3-4B-Instruct-2507 (revision `cdbee75f`), bf16, greedy | `rag`, `closed`, `atlas` |
| Tuned small model | Same base + LoRA trained on train-split rulings in `rag` format | `rag` (primary); `atlas` reported |
| Frontier | Claude Opus 5.5, adaptive thinking, effort high | `rag`, `closed`, `atlas` |
| Second frontier family | GPT-5.6 Sol via OpenRouter, if the budget allows | `rag` |

All arms use prompt `openset-v1` (`src/tariff_slm/openset/prompts.py`): the same system message and user message
for the same item. Answers are parsed from the last `CODE:` line. An invalid or missing code is wrong.

## Success criteria (pre-registered 2026-11-01, before any tuned model is evaluated)

On the Track B final test, `rag` mode:

1. **Hypothesis supported:** tuned exact 10-digit accuracy minus base exact 10-digit accuracy is at least
   **5 points**, and the paired bootstrap 95% interval (10,000 resamples, seed 0) excludes 0.
2. **Useful system (secondary):** tuned accuracy exceeds the retrieval-only baseline, and the interval excludes 0.
3. **Frontier comparison (reported, not a criterion):** tuned minus Opus 5.5 `rag`, with its interval.

If criterion 1 fails, the hypothesis is not supported on this benchmark, whatever the other numbers show. The final
test is evaluated once per arm; development decisions use dev only.

## Amendment 2026-11-02: the Opus target

Innocent set the goal after the Track A result: "finish the new fine tuned Model to be better than how Opus is
performing. You get three tries total." This adds a target; it does not change criteria 1 and 2.

- **Test.** Track B final test, `rag` mode, both arms given the same items and retrieval context. *Better than Opus:*
  tuned exact 10-digit accuracy is higher than Opus 5.5's. *Clearly better:* the paired 95% interval of tuned minus
  Opus excludes 0. Both are reported, whichever way they come out.
- **Three tries** means at most three training runs. Each is chosen and judged on dev (`rag`, 300 items). The final
  test is run once, for the one checkpoint picked on dev, plus the base model and Opus.
- **No moving the target.** The scorer, items, retrieval and prompt stay as frozen. A deterministic post-check that
  replaces invalid codes may be reported as a secondary row, applied to every arm alike, never as the headline.

## Checkpoint selection (recorded 2026-11-02, before the final test was run)

Dev `rag`, 300 items: base 42.0%; try 1 57.7%; try 2 59.3%; try 3 59.7% answering directly; try 3 with its answer
prefilled with `REASONING:` 48.0%; Opus 5.5 71.3%. **Selected: try 3 (`try3-rationales-backfill-cont-b4`), answering
directly (no prefill), greedy, up to 768 new tokens.** Try 3 and try 2 are tied on dev (+0.3 pts, CI −2.7 to +3.3); try
3 is chosen on the higher point estimate. Reasoning mode is rejected on its dev score. The final test is run once for
this checkpoint, the base model (`rag`) and Opus 5.5 (`rag`), with the frozen prompt, items and retrieval.

## Missing information

The prompt allows an optional `MISSING:` line naming an unstated deciding fact, always with a best-guess code. We
report how often each model flags, and its accuracy on flagged versus unflagged items. No item is labelled
"missing information" in advance, so this is reported as calibration, not scored as recall.

## Cost and latency

API arms: measured tokens × list price, per item, and p50/p90 latency. Small model: H100 seconds per item from
batched generation (batch 16), and the training run's GPU time. Modal H100 list price is used for dollars.

## Baselines (recorded before any tuned model was evaluated)

Frozen files: `data/benchmark/` (`docs/data/benchmark-v2.md`). Runs: `runs/openset/` (VPS, API arms) and
`runs/openset-modal/` (small model).

| Split, mode | Arm | n | Exact 10 | 8-digit | 6-digit | Valid code | Exact when gold retrieved / not | Cost per item | p50 latency |
|---|---|---|---|---|---|---|---|---|---|
| Dev, `rag` | Retrieval only (top candidate) | 300 | 36.7% | | | 100% | | $0 | |
| Dev, `rag` | Base Qwen3-4B | 300 | 42.0% | 48.3% | 54.7% | 97.7% | 56.3% / 0.0% | H100 3.5 s | |
| Dev, `rag` | Opus 5.5 | 300 | **71.3%** | 80.7% | 85.7% | 96.0% | 83.5% / 35.5% | $0.033 | 9.4 s |
| ATLAS test, `atlas` | Base Qwen3-4B | 200 | 0.0% | 0.0% | 1.0% | 0.5% | | | |
| ATLAS test, `atlas` | Opus 5.5 | 200 | **41.0%** | 59.0% | 67.0% | 80.0% | | $0.031 | 15.0 s |
| Dev v0 sample, `closed` | Base Qwen3-4B | 300 | 0.0% | 0.0% | 0.7% | 0.7% | | | |
| Dev v0 sample, `closed` | Opus 5.5 | 150 | 44.0% | 62.0% | 74.7% | 80.0% | | $0.029 | |

The two closed-book rows used the first (Mac) build's dev sample, of which 157 of 300 items are in the frozen dev
set; they are references for what retrieval adds, not comparisons with the frozen `rag` rows. Opus on ATLAS's 168
items with current codes: 42.9% exact, 69.0% 6-digit. Base-model latency is H100 time per item in batches of 16
with up to 768 generated tokens. Dev retrieval recall@20 is 74.7%.

## Changes

_None yet._
