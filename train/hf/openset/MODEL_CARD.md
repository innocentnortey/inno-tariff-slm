---
license: apache-2.0
base_model: Qwen/Qwen3-4B-Instruct-2507
language: en
tags: [tariff, hts, htsus, customs, classification, lora, retrieval-augmented, gauntlet]
---

# Tariff classifier (Qwen3-4B-Instruct-2507, LoRA, merged)

Given a product description plus retrieved evidence — five earlier CBP rulings with their codes and 20 candidate
HTSUS lines — the model returns the single 10-digit US tariff code (HTSUS statistical reporting number) CBP would
assign, as one line: `CODE: XXXX.XX.XX.XX`. Any of the ~19,800 current lines may be answered; the evidence is a
search result, not an answer key. It is a component of a human-supervised workflow, not an automated customs
determination.

## Results (measured 2026-11-02)

Final test: 500 CBP rulings issued Aug 2025 – Oct 2026, after every ruling used in training, described in CBP's own
words with the answer removed. Every model got identical messages and identical retrieved evidence (the correct code
was among the 20 candidates for 80% of items).

| Exact 10-digit code | Score | 95% CI |
|---|---|---|
| Retrieval only (top candidate) | 38.0% | 33.9–42.3% |
| Base Qwen3-4B-Instruct-2507 | 42.0% | 37.8–46.4% |
| **This model** | **59.8%** | 55.4–64.0% |
| Claude Opus 5.5 (adaptive thinking, effort high) | 71.6% | 67.5–75.4% |

Paired differences: this model − base **+17.8 points** (95% CI +13.6 to +22.0); − Opus **−11.8** (−16.0 to −7.6).
Cost: about $0.0002 of H100 time per classification in batches of 16, against $0.034 for Opus.

**Without retrieval it does not work:** closed-book it scores 0.0% on the ATLAS benchmark (Opus 5.5: 41.0%). Use it
with the retrieval step it was trained with.

## How it was trained

- Data: 27,841 CBP CROSS rulings (HF corpus `orlandowhite/hts-cross-rulings` plus 6,480 rulings fetched from CROSS),
  single product, one current 10-digit code, descriptions taken verbatim from each ruling's facts with every sentence
  naming a code, heading or the conclusion removed. Each example carries the same kind of retrieved evidence it gets at
  inference, built only from rulings issued before it.
- Three training runs: LoRA r=16 (all linear layers), bf16, Modal H100. The released weights are try 3: continued from
  try 2 at lr 5e-5 on 6,480 extra rulings, 488 verified rationales (labels from CBP; Opus wrote the explanation; a
  Codex judge kept only grounded ones) and code-only replay. Answers directly (no reasoning text).
- Labels come only from CBP rulings and the USITC schedule, never from a teacher model.

## Use

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
tok = AutoTokenizer.from_pretrained("youngjr1232/tariff-classifier-qwen3-4b")
model = AutoModelForCausalLM.from_pretrained("youngjr1232/tariff-classifier-qwen3-4b", dtype="bfloat16", device_map="auto")
# Build messages with the project's prompt (src/tariff_slm/openset/prompts.py, mode "rag"), generate greedily,
# read the last `CODE:` line.
```

Reproduce the test numbers: project repository `inno-tariff-slm`, `scripts/eval_openset.py` with
`data/benchmark/test.jsonl` from the companion dataset. Protocol, data checksums and every command:
`docs/evals/results-v2.md`.

## Limits

One benchmark and one training seed per run; labels follow the current HTSUS (rulings whose codes no longer exist were
dropped); the model never flags missing information; 4B parameters cannot hold rare codes the way a frontier model does.
