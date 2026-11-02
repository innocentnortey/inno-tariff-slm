# Prompt-ceiling ablation — 2026-11-01

**Question.** Can a frontier model, prompted well, already hold the behavior spec reliably? If yes, the plan narrows
the behavior instead of training (`docs/planning/tariff-behavior-and-evals.md`, experiment 1). The brief requires
this result before any fine-tuning: at least 2 frontier families × 3 prompt strategies × 30 scenarios, scored with the
same judge rubric used later for base against tuned, reporting mean spec adherence and robustness per cell.

## Setup

| Item | Choice | Why |
|---|---|---|
| Models | `claude-opus-5-5` (Anthropic API) and `openai/gpt-5.6-sol` (via OpenRouter) | The top widely released tier of each family; both priced at $4 / $20 per million tokens |
| Reasoning effort | `high` for both | A ceiling test gives each model a strong attempt; the same setting in every cell |
| Strategies | zero-shot; few-shot (3 worked examples from train: decidable, natural `NEED_INFO`, residual); structured chain-of-thought system prompt | The three the brief names |
| Clean set | `data/processed/dev.jsonl`: 157 items after label review round 3 (143 rulings from 2023 + 14 ablated `NEED_INFO` copies) | Dev, not test: the 2024–2025 test set stays sealed for base against tuned and the step 10 comparison |
| Robustness set | `data/processed/dev_robust.jsonl`: 58 dev items, each perturbed one way that cannot change the right answer (`scripts/build_robustness.py`) | The brief's "hard eval set built to break your behavior" |
| Candidates | The same eight per item for every model | Retrieval is measured separately (rule `retrieval-and-context`) |
| Judge | `google/gemini-3.1-pro-preview` (third family), two yes/no questions per decidable `SELECT` | Independent of both models under test |
| Refusals | Counted as failed answers; no automatic fallback model | A different model answering would contaminate the measurement |

**Perturbations** (15 items each): candidates reordered; irrelevant importer facts appended (style number, carton
count, port); an instruction embedded in the description naming the runner-up as correct; description lowercased
with punctuation stripped. The build re-checks with the label code that the evidence for the deciding dimension is
unchanged.

**Metrics.**
- *Spec adherence*: share of clean items that pass the behavior spec with deterministic checks (valid JSON, right
  decision, right code, right dimension, value copied from the description). *Judged* additionally requires the judge
  to answer yes to both questions for decidable `SELECT` answers.
- *Robustness*: the same measure on the perturbed set.
- *Consistency*: share of perturbed items answered with the same decision and code as their clean source item.
- Also reported: 10-digit accuracy, `NEED_INFO` recall, over-asking, measured cost.

## One prompt change before the full run (v1 → v2)

A 4-item smoke run per cell showed both models choosing the **correct code** and still failing the spec on the
dimension, for two reasons unrelated to the behavior:

1. The prompt said "closest other candidate" without defining it. On a women's blouse whose label compares women's
   against girls', both models named a more distant fiber line as runner-up and cited fiber.
2. The dimension names were listed but not defined. Both models called "water resistant" `other`; the labels call it
   `use`.

Prompt v2 (`src/tariff_slm/evals/prompts.py`, `PROMPT_VERSION = "v2"`) defines each dimension with examples, defines
the runner-up as the candidate sharing the most schedule-path levels with the choice, and asks for a 1–6 word exact
copy as the value. It applies to all three strategies and is the prompt the tuned model will be trained and evaluated
with. On the same 4 perturbed items, Opus went from 0–50% to 100% across strategies. This was one specification fix,
made on 4 dev items, not a tuning loop; the full run uses v2 unchanged.

## Results (run 2, the reported run)

`runs/prompt-ceiling-20261102-013242/` (run 2, completed by a resume; 0 API errors, 0 refusals, 0 judge errors).
Clean set 157 items, robustness set 58. Prompt v2, labels after review round 3.

| Model | Strategy | Spec adherence (judged) | Robustness (judged) | Consistency | 10-digit exact | `NEED_INFO` recall | Over-asking |
|---|---|---|---|---|---|---|---|
| Claude Opus 5.5 | zero-shot | 84.7% (83.4%) | 82.8% (82.8%) | 94.8% | 85.6% | 88.9% | 4.3% |
| Claude Opus 5.5 | few-shot | 86.0% (84.7%) | 75.9% (75.9%) | 84.5% | 87.8% | 88.9% | 2.9% |
| Claude Opus 5.5 | structured CoT | **86.0% (85.4%)** | **87.9% (86.2%)** | 94.8% | 87.1% | 83.3% | 0.0% |
| GPT-5.6 Sol | zero-shot | 78.3% (78.3%) | 62.1% (62.1%) | 75.9% | 79.9% | 77.8% | 5.8% |
| GPT-5.6 Sol | few-shot | 78.3% (77.1%) | 67.2% (67.2%) | 75.9% | 80.6% | 83.3% | 8.6% |
| GPT-5.6 Sol | structured CoT | 82.8% (82.2%) | 67.2% (65.5%) | 87.9% | 84.9% | 72.2% | 1.4% |

Robustness by perturbation (share passing, 14–15 items each):

| Model | Strategy | Reordered | Irrelevant facts | Injected instruction (adopted the injected code) | Messy format |
|---|---|---|---|---|---|
| Opus 5.5 | zero-shot | 86.7% | 80.0% | 71.4% (3 of 14) | 92.9% |
| Opus 5.5 | few-shot | 86.7% | 80.0% | 42.9% (7 of 14) | 92.9% |
| Opus 5.5 | CoT | 93.3% | 80.0% | 85.7% (1 of 14) | 92.9% |
| GPT-5.6 Sol | zero-shot | 73.3% | 80.0% | 0.0% (9 of 14) | 92.9% |
| GPT-5.6 Sol | few-shot | 86.7% | 80.0% | 7.1% (10 of 14) | 92.9% |
| GPT-5.6 Sol | CoT | 66.7% | 80.0% | 28.6% (6 of 14) | 92.9% |

The judge agreed with the deterministic check on 95–99% of decidable `SELECT` answers in every cell.

## The failure mode that survives the best prompting

**Choosing between a residual "Other" line and its named sibling.** Prompt strategy moves spec adherence by at most
1.3 points for Opus and 4.5 for GPT, and in every one of the six cells the largest failure bucket is the same: the
wrong code on items whose correct line is "Other" (11–14 per cell; 13 of the best cell's 22 failures, about 21% of
the 63 residual items). The models pick a named line, often on a gender or fiber split one level deeper, where the
schedule's structure, a chapter note (unisex footwear goes to women's), or a statistical note decides it. Two
weaker failures sit beside it: an instruction embedded in the description makes GPT-5.6 Sol adopt the wrong code on
6–10 of 14 items and Opus on 1–7; and both models choose a code on 2–5 of the 18 `NEED_INFO` items.

**Caveat on the residual failures.** Some of them depend on facts the dataset's summary dropped (for example, a
coating that is over 50% of a glove's weight). The item-by-item reading of run 1 found most of them model-side, but
the share that is label-side was not measured.

## Against the reliability bar

The evaluation plan set no absolute spec-adherence bar before this run. The thresholds it did set (`NEED_INFO` recall
≥ 0.7, over-asking ≤ 0.1, grounding ≥ 0.95) are all met by the best Opus prompt. What the run does show is a
plateau: three different strategies land within 1.3 points (Opus) and 4.5 points (GPT) of each other at 78–86%,
with a stable, nameable failure. Whether 86% is below the reliability bar for a compliance tool (where each wrong
code is a wrong duty on every shipment) is a bar that must now be set explicitly, and recorded as set after this run.

**Bar decided 2026-11-01 (Innocent, option B):** the tuned model must match or beat this best cell: spec adherence
≥ 86.0% and robustness ≥ 87.9%, compared head-to-head on the sealed test set in step 10. The bar is relative: it tests
whether a trained 1.7B model can stand in for the frontier model, while the plateau above is the evidence that prompt
work alone does not close the remaining failure.

## Run 1 (superseded, kept as evidence)

`runs/prompt-ceiling-20261102-005624/`, labels before review round 3, 161 + 60 items. Opus 81.4–83.2% spec adherence,
GPT 75.2–77.0%. Reading its failures item by item found label errors and a labelling contradiction (label review,
round 3 and decision 5), which were fixed before run 2. Run 2's first pass also hit an OpenRouter credit limit on 230
GPT answers and 501 judge verdicts; Innocent topped up the account and the resume retried only those calls.

## Cost

About $56 measured: run 1 $25.56, run 2 $23.48 plus $5.69 for the resume, smoke runs about $1.40. Per decision, the
best Opus cell cost about $0.018 (`runs/prompt-ceiling-20261102-013242/results.json`), the reference point for the
step 10 cost comparison.

## Reproduce one sample point

    ../bin/with-provider-env -- uv run --extra api python -I scripts/prompt_ceiling.py \
        --models anthropic:claude-opus-5-5 --strategies cot --judge openrouter:google/gemini-3.1-pro-preview --limit 30

## Limits

- The judge is not yet calibrated against human labels (rule `verification-evals-observability`, item 14), so the
  judged columns are reported beside the deterministic ones, never instead of them.
- Dev has 18 `NEED_INFO` items (4 natural, 14 ablated), so the `NEED_INFO` rates have wide error bars.
- One run per cell; no repeat runs for spread.
