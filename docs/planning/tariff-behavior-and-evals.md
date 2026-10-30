# Tariff specialist: behavior spec and evaluation plan (proposed)

Status: **proposed, not run** (2026-10-30), except the preliminary baselines marked *Measured*.

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

1. **Prompt-ceiling ablation (required, not run).** Two frontier families (proposed: Anthropic and OpenAI) × three
   strategies (zero-shot, few-shot, structured chain-of-thought) × at least 30 scenarios per cell, scored with the
   same checks and judge. Every model gets the same eight candidates. If the best prompt already passes reliably, we
   narrow the behavior rather than force a fine-tune.
2. **Baselines on the same candidates.**
   - *Measured 2026-10-30, preliminary, non-model,* on a 235-item draft test set (202 rulings from 2024–2025 plus 33
     ask-when-unsure copies). Exact 10-digit match on items that need a code: random 10.3%, keyword overlap 14.1%,
     attribute rules 20.5%. The rules caught 24% of ask-when-unsure cases. The rules share the lexicon used to label
     attributes, so their attribute scores are optimistic.
   - *Planned:* base Qwen3, frontier with the same candidates, frontier with realistic retrieval, tuned specialist.
3. **Base vs tuned (required, not run).** Same eval set, same prompt template as training.
4. **Data-efficiency curve (required, not run).** Four checkpoints on nested subsets (for example 500, 1,000, 2,000
   and 4,000 rulings); report the smallest N that clears the bar.
5. **Generalization (not run).** The staff held-out set, and one chapter outside training reported separately.

## Metrics and proposed thresholds

| Metric | Definition | Proposed bar |
|---|---|---|
| Spec pass rate | Share of items passing the spec | Tuned ≥ base + 20 points |
| 10-digit accuracy | Exact match on items that need a code; 6 and 8 digits alongside | Reported, no bar |
| NEED_INFO recall | Share of insufficient items answered `NEED_INFO` | ≥ 0.7 |
| Over-asking | `NEED_INFO` on decidable items | ≤ 0.1 |
| Grounding | Cited value appears in the description | ≥ 0.95 |
| False confidence | `SELECT` on insufficient items | Reported; lower is better |
| Retrieval recall@8 | Gold code in the retrieved list (separate system) | Reported. Measured preliminary: plain BM25 4% at 8 and 20% at 50 on test rulings |

**Judge:** two yes/no questions per `SELECT` answer (is the attribute stated, does it separate the chosen code from
the runner-up), calibrated against about 20 hand labels before it enters the gate. Raw judge transcripts are saved
as JSONL.

**Failure condition:** no gain over base, or frontier prompting already passes. We report that finding and narrow
the behavior instead of tuning hyperparameters.
