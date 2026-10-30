# Tariff analyst: architecture (proposed)

Status: **proposed** (2026-10-30). Nothing in this document is built. The diagram lives in
`docs/research/tariff-compliance-vision.html` §7.

## Principle

Each component owns one kind of decision:

- language models handle language;
- deterministic code handles rules, lookups and arithmetic;
- a licensed person owns the final classification.

The fine-tuned specialist is the only component we train.

## Components

| Component | Kind | Owns | Must never |
|---|---|---|---|
| Intake agent | LLM agent | Splitting documents into product records | Choose a code |
| Attribute extractor | LLM agent | A fixed attribute schema with quotes | Infer a missing attribute |
| Schedule and rulings index | Data store | Schedule by effective date, CBP rulings, chapter notes | Act as a rate authority until validated |
| Candidate retrieval | Code | Likely heading, then sibling lines | Hide codes from the reviewer |
| Precedent search | Code | Similar past rulings for evidence | Override schedule text |
| **Tariff specialist (SLM)** | **Fine-tuned model** | `SELECT` + deciding attribute, or `NEED_INFO` | Compute duty, invent a code outside the list, file anything |
| Clarification agent | LLM agent | One supplier question per `NEED_INFO` | Answer its own question |
| Duty and landed-cost engine | Code | Rates, Chapter 99 origin measures, exclusions, arithmetic | Let a model touch numbers |
| Evidence and audit log | Code | Inputs, candidates, versions, citations, reviewer actions (append-only) | Lose a record |
| Orchestrator | LLM agent with code guards | Routing, budgets, retries, stop conditions | Change a specialist decision or skip review |
| Licensed reviewer | Human | Approve, edit, escalate | (none: final authority) |

## Specialist interface

- **Input:** `{description, candidates: [{code, schedule_text, general_rate}]}`.
- **Output:** the JSON contract in `tariff-behavior-and-evals.md`.
- **Validation in code before use:**
  - the output parses;
  - the code is in the candidate list;
  - the dimension comes from the enum;
  - the cited value appears in the description.

  On failure, the item goes to review rather than being retried by the model.

## Version 1 (concept to demo)

Apparel and footwear only, with candidates from the schedule tree. It makes one specialist call per product and
applies the general rate only. Every recommendation goes to a reviewer queue.

## Production challenges

- **Effective dates:** classify against the schedule edition in force on the entry date.
- **Origin-based duties:** Chapter 99 measures, exclusions and trade remedies. For example, ruling NY N344447 cites
  U.S. Note 20 for China-origin goods.
- **Old or conflicting rulings:** 3,154 rulings in the subset cite codes that no longer exist (*Measured*). Prefer the
  newest, and flag conflicts.
- **Retrieval quality:** plain BM25 put the right code in the top 8 for 4% of test rulings (*Measured, preliminary*).
  Retrieval needs its own design (for example, a heading classifier first, then siblings).
- **Accountability:** risk tiers based on duty exposure, confidence and conflicts decide what a broker must sign.
- **Cost and latency:** one short structured specialist call per product; frontier models are used only where
  language work needs them.
