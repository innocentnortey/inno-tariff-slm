# Tariff specialist: behavior spec and evaluation plan (proposed)

Status: **behavior spec approved by Innocent 2026-11-01** ("approved, lets move on to the next thing"). Experiments are not run except the baselines marked *Measured*.

## Behavior spec

> Given a product description and eight candidate HTS codes with their schedule text, the model returns one JSON
> object that either selects exactly one candidate and names the deciding attribute in words taken from the
> description, or returns `NEED_INFO` naming the attribute whose absence keeps it from choosing. It never selects a
> code when the description lacks that attribute, and it never cites an attribute the description doesn't state.

Output contract:

```json
{"decision": "SELECT | NEED_INFO", "code": "<candidate code or null>",
 "deciding_attribute": {"dimension": "gender_age | fiber_content | construction | material | use | garment_type | shape_coverage | value | other",
                        "value": "<words from the description, or null>"},
 "runner_up": "<candidate code or null>"}
```

**Pass** for a decidable item: valid JSON, the CBP code, the expected attribute dimension, and a value that appears
in the description. **Pass** for an insufficient item: `NEED_INFO` with the expected dimension.

## What stays outside the model

| Component | Owner |
|---|---|
| Finding candidates | Retrieval (deterministic); recall measured on its own |
| Duty rates, origin measures, arithmetic | Deterministic duty service |
| Attribute extraction from documents | An LLM agent with a fixed schema |
| Final classification | A licensed person |

## Experiments

1. **Prompt-ceiling ablation (required; run 2026-11-01, `docs/evals/prompt-ceiling-2026-11-01.md`: best cell Opus 5.5 structured CoT 86.0% spec adherence, 87.9% robustness; GPT-5.6 Sol best 82.8% / 67.2%; surviving failure: residual "Other" lines; no absolute spec bar was set beforehand).** Two frontier families (proposed: Anthropic and OpenAI) × three
   strategies (zero-shot, few-shot, structured chain-of-thought) × at least 30 scenarios per cell, scored with the
   same checks and judge. Every model gets the same eight candidates. If the best prompt already passes reliably, we
   narrow the behavior rather than force a fine-tune.
2. **Baselines on the same candidates.**
   - *Measured 2026-11-01, non-model,* on the reviewed 221-item test set (197 rulings from 2024–2025 plus 24
     ask-when-unsure copies; `docs/data/label-review-2026-11-01.md`, after round 3). Exact 10-digit match on items
     that need a code: random 11.4%, keyword overlap 16.3%, attribute rules 37.5% (spec pass 24.9%, NEED_INFO recall
     13.5%, over-asking 7.1%). Before the label fixes the rules scored 20.5%; most of the gain is the shared lexicon,
     so their attribute scores are optimistic, but their code accuracy is a real bar the tuned model must clear.
   - *Planned:* base Qwen3, frontier with the same candidates, frontier with realistic retrieval, tuned specialist.
3. **Base vs tuned (required, not run).** Same eval set, same prompt template as training.
4. **Data-efficiency curve (required, not run).** Four checkpoints on nested subsets (for example 500, 1,000, 2,000
   and 4,000 rulings); report the smallest N that clears the bar.
5. **Generalization (not run).** The staff held-out set, and one chapter outside training reported separately.
6. **Hypothesis test: does the small model earn its place? (required, not run; added 2026-11-01).** Arms: (A) the best well-prompted general model from the prompt-ceiling ablation, (B) the base small model, (C) the tuned small model, all on identical products, candidates, schedule text and any retrieved rulings. The deciding comparison is C against A; C against B is experiment 3. Report two tables: gold code forced into the eight (decision quality) and candidates from the real retriever (end-to-end, retrieval scored separately). Score a hard slice (no matching ruling retrieved, or candidates differing by one attribute) with its rule fixed before any run, plus cost and latency per decision including hosting. Fix the margin that counts as a tie before the first run. If A meets the bar and beats C, narrow or reconsider the training target. Open: whether training prompts include retrieved rulings (a data-format change); see `docs/research/slm-vs-rag.md`.

## Metrics and proposed thresholds

| Metric | Definition | Proposed bar |
|---|---|---|
| Spec pass rate | Share of items passing the spec | Tuned ≥ base + 20 points, **and** tuned ≥ the best frontier prompt (reliability bar, below) |
| 10-digit accuracy | Exact match on items that need a code; 6 and 8 digits alongside | Reported, no bar |
| NEED_INFO recall | Share of insufficient items answered `NEED_INFO` | ≥ 0.7 |
| Over-asking | `NEED_INFO` on decidable items | ≤ 0.1 |
| Grounding | Cited value appears in the description | ≥ 0.95 |
| False confidence | `SELECT` on insufficient items | Reported; lower is better |
| Retrieval recall@8 | Gold code in the retrieved list (separate system) | Reported. Measured preliminary: plain BM25 4% at 8 and 20% at 50 on test rulings |

**Reliability bar (decided by Innocent 2026-11-01, option B, set after the prompt-ceiling run):** the tuned model must
match or beat the best frontier prompt on the same items: spec adherence ≥ 86.0% and robustness ≥ 87.9% (Claude Opus 5.5,
structured CoT, prompt v2, dev set; `docs/evals/prompt-ceiling-2026-11-01.md`). On the sealed test set the comparison is
head-to-head: that frontier cell is run on test in step 10, and the tuned model must match or beat it there. The bar is
relative, so it shows the tuned model is at least as good, not that the frontier falls short; the ablation's evidence
for training is the plateau and the surviving residual-line failure.

**Judge:** two yes/no questions per `SELECT` answer (is the attribute stated, does it separate the chosen code from
the runner-up), calibrated against about 20 hand labels before it enters the gate. Raw judge transcripts are saved
as JSONL.

**Failure condition:** no gain over base, or frontier prompting already passes. We report that finding and narrow
the behavior instead of tuning hyperparameters.
