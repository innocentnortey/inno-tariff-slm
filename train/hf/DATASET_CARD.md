---
license: other
license_name: mixed-provenance
language: en
task_categories: [text-classification]
tags: [tariff, hts, customs, cbp, classification]
size_categories: [1K<n<10K]
---

# Tariff specialist dataset: HTS chapters 61, 62, 64

Each item gives a product description, eight candidate US tariff (HTS) codes with their full schedule text, and the
expected answer: **SELECT** one code with the deciding attribute (dimension + words from the description), or
**NEED_INFO** with the missing attribute's dimension. Built for the Gauntlet AI Week 7 "Train your own SLM" project.

## Files

| File | Items | Use |
|---|---|---|
| `train_v2.jsonl` | 6,543 | v1 training items (CBP rulings 2000–2022) + 678 attribute-ablated `NEED_INFO` copies |
| `train_v4.jsonl` | 6,791 | v2 rebalanced toward rare schedule branches (no new or relabelled items); the published model's data |
| `dev.jsonl` | 157 | 2023 rulings + ablated copies; model selection |
| `dev_robust.jsonl` | 58 | dev items perturbed one way each (reorder, irrelevant facts, injected instruction, messy format) |
| `test.jsonl` | 221 | 2024–2025 rulings + ablated copies; the sealed test |
| `test_robust.jsonl` | 60 | test items perturbed the same way |
| `CHECKSUMS.sha256` | — | SHA-256 of every file; the eval files are frozen |

## How labels were made

Codes come from the CBP ruling for each product (single-code rulings whose code is valid in the current schedule).
The deciding attribute and `NEED_INFO` labels come from the USITC schedule: the first level where the gold line and its
nearest sibling differ, mapped to a dimension by a word list and required to separate the two lines. No label was
written by a language model. Label review, decisions and known noise: `docs/data/label-review-2026-11-01.md` in the
project repository. Splits are by ruling date (train ≤ 2022, dev 2023, test 2024–2025).

## Provenance and licensing

- **CBP rulings and the USITC Harmonized Tariff Schedule** are works of the US government.
- **Product descriptions** are model-written summaries taken from the Hugging Face dataset
  `orlandowhite/hts-cross-rulings`, which carries **no license**. They are included because the task cannot be
  reproduced without them. If you are the rights holder and object, open a discussion on this repository and the
  descriptions will be removed.
- Ruling text itself is not redistributed here; each item carries the ruling ID and a hash of the original text.

## Known limits

Some summaries omit facts the original ruling states, so some `NEED_INFO` items exist because the summary dropped a
fact. Residual ("Other") items are scored on the code only. The evaluation assumes the correct code is among the eight
candidates. Not legal advice.
