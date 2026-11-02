---
license: apache-2.0
base_model: Qwen/Qwen3-1.7B
language: en
tags: [tariff, hts, customs, classification, qlora, gauntlet]
---

# Tariff specialist (Qwen3-1.7B, QLoRA, merged)

Given a product description and eight candidate US tariff (HTS) codes with their schedule text, the model returns one
JSON object that either **selects** one candidate and names the deciding attribute in words copied from the
description, or answers **`NEED_INFO`** and names the attribute whose absence keeps it from choosing. It covers
apparel and footwear (HTS chapters 61, 62, 64). It is a component for a human-supervised workflow, not an automated
customs classifier: candidate retrieval, duty calculation and the final determination stay outside the model.

## Results (measured, 2026-11-01)

Sealed test set: 221 items from 2024–2025 CBP rulings, plus 60 perturbed items. Same eight candidates and prompt for
every model.

| | Base Qwen3-1.7B | This model | Claude Opus 5.5 (structured CoT) |
|---|---|---|---|
| Spec adherence | 6.3% | 80.1% (177/221)* | 84.6% (187/221) |
| Robustness | 10.0% | 75.0% (45/60)* | 75.0% (45/60) |
| Asks when the deciding fact is missing (`NEED_INFO` recall) | 0% | 83.8% | 73.0% |

\*Measured with the one-command check below on these published full-precision weights (the 4-bit development evaluation gave 81.0% / 89.2%). Robustness is from the 4-bit evaluation. This model (v4 data, 2 epochs) was chosen on the dev set after the sealed test had already been used once (for the
v2 model: 78.7% / 71.7%), so its test numbers are a second look, not a fresh sealed result. Dev: 137/157 clean,
52/58 robust (single seed).

The model asks for missing facts more reliably than the frontier reference and ties it on robustness, but trails it
on choosing the code, mainly on residual "Other" lines decided by legal definitions that the candidate text names but
does not include.

## Training

QLoRA (4-bit NF4, LoRA r16, alpha 32, dropout 0.05, all linear projections), lr 2e-4, cosine, 2 epochs, loss on the
answer tokens only, thinking mode off. 6,791 examples: CBP-labelled rulings (2000–2022) plus attribute-ablated
`NEED_INFO` copies, rebalanced toward rare schedule branches. Labels come from CBP rulings and the USITC schedule,
never from a model. Product descriptions are model-written summaries from the Hugging Face copy
`orlandowhite/hts-cross-rulings`, which carries no license; CBP rulings are US government works.

## Use

The prompt format must match training: the zero-shot prompt v2 in `src/tariff_slm/evals/prompts.py` of the project
repository, rendered with the chat template and `enable_thinking=False`, greedy decoding.

    uv run python -I eval.py --model youngjr1232/tariff-specialist-qwen3-1.7b --eval-set data/processed/test.jsonl

## Limits

Single training seed; dev sets of 157 and 58 items (about 6 items of seed-to-seed variation observed); some
descriptions omit facts the original ruling states; the evaluation assumes the correct code is among the eight
candidates (plain BM25 retrieval finds it in the top 8 only 4% of the time). Not legal advice.
