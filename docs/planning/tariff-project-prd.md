# Tariff analyst: product requirements (concept stage)

Status: **concept draft, 2026-10-30.** Nothing here is built except what *Current state* lists. Companion page:
`docs/research/tariff-compliance-vision.html`. Labels: **Established** (published or measured) · **Hypothesis** ·
**Proposed** · **Future validation**.

## Problem

Every product imported into the US needs a 10-digit HTS code. The last four digits turn on attributes such as
fiber content, knit or woven, intended user and upper material. The importer is legally responsible for the code,
and a wrong one means a wrong duty on every shipment of that product.

- **Established:** today's schedule has 19,949 ten-digit lines (USITC export, 2026-10-30).
- **Established:** in ATLAS (arXiv 2509.18400, 2025), GPT-5-Thinking got 25.0% of 10-digit codes fully right on 200
  CBP rulings and Gemini 2.5 Pro Thinking got 13.5%.
- **Established:** one attribute can change the duty. Silk scarves with at least 70% silk take 1.2%
  (6214.10.10.00), and other silk scarves take 3.9% (6214.10.20.00); CBP ruling NY N346508 placed a 100% silk scarf
  in the 1.2% line.

## Users and buyers

| User | Job | What they need from us |
|---|---|---|
| Classification specialist at a mid-size importer | Classify new products and re-check old ones | A recommendation with evidence, not a blank search |
| Licensed customs broker | Sign off filings for many clients | Risk-tiered queue, audit trail, supplier questions handled |
| Cross-border e-commerce seller | Price products before shipping | Duty and landed-cost scenarios per code |

## Product vision (Proposed)

An autonomous, **human-supervised** trade-compliance analyst. It ingests product documents, extracts attributes,
retrieves candidate codes and precedent rulings, uses a fine-tuned specialist to choose between close codes or ask
for the missing fact, computes duty scenarios in code, and sends a documented recommendation to a person. It never
makes a legally binding determination.

## Core workflow

1. Intake: product descriptions, invoices, catalogs, spec sheets.
2. Attribute extraction into a fixed schema, with a quote for each attribute.
3. Retrieval of candidate schedule lines and similar CBP rulings.
4. Specialist decision: `SELECT` one candidate with its deciding attribute, or `NEED_INFO`.
5. Clarification: one targeted question to the supplier when needed.
6. Duty and landed cost: deterministic rates, origin-based Chapter 99 measures, arithmetic.
7. Recommendation with evidence, risk tier and audit record.
8. Human review: approve, edit or escalate.

## Scope

| In scope for the Week 7 project | Out of scope until later |
|---|---|
| One trained behavior (the specialist), apparel and footwear (Chapters 61, 62, 64) | Training the whole agent |
| Evaluation harness, prompt-ceiling ablation, data-efficiency curve | Production APIs and backend services |
| A minimal agent demo around the specialist (stretch) | Filing with CBP, legally binding determinations |
| Published dataset and checkpoint | Other chapters, other countries' schedules |

## Success criteria

- **Week 7 (Future validation):** the tuned model beats its base model on the behavior spec on held-out 2024–2025
  rulings (target ≥20 points), with thresholds in `tariff-behavior-and-evals.md`.
- **Product (Hypothesis):** less reviewer time per product, more recommendations accepted unchanged, supplier
  questions that change the code, fewer post-entry corrections. None of these are measured yet.

## Current state

- Exists: this concept package; a scaffolded repo `inno-tariff-slm` (zero-to-hero Stage 0); a data-reality profile
  of the rulings and schedule; a paused draft data build and deterministic checks; three preliminary non-model
  baselines.
- Does not exist: a trained model, base-model or frontier results, a published dataset, a working product.
- This concept package does not yet meet the technical evidence requirements of Gauntlet's early-submission rubric.
