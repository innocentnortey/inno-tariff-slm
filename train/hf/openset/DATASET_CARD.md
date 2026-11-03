---
license: other
license_name: us-government-works-and-apache-2.0
language: en
tags: [tariff, hts, htsus, customs, cbp, cross-rulings, classification, retrieval]
pretty_name: Open-set HTSUS classification from CBP rulings (benchmark v2)
---

# Open-set 10-digit HTSUS classification from CBP rulings (benchmark v2)

Product description → the single 10-digit US tariff code CBP assigned. Built 2026-11-02 for a Gauntlet AI project
testing whether domain fine-tuning improves a small model on this task.

| File | Items | What |
|---|---|---|
| `test.jsonl` | 500 | CBP rulings issued 2025-08-07 → 2026-10-09 (fetched from CROSS; after every training ruling). Frozen. |
| `dev.jsonl` | 300 | Rulings 2024-01 → 2025-08-01. Frozen; used for every development decision. |
| `atlas_test.jsonl` | 200 | The ATLAS benchmark test split (arXiv 2509.18400), question and label only, for closed-book comparison. |
| `train.jsonl` | 27,841 | Training rulings (≤ 2025-08-01), each with its retrieval context (5 earlier rulings, 20 HTSUS lines). |
| `train_mix.jsonl` | 10,872 | The exact training file of the released model: rationales ×3, replay, backfilled rulings. |

Each item: `ruling_id`, `date`, `code` (10 digits), `product` (CBP's subject line), `description` (verbatim fact
sentences with answer-revealing sentences removed), `candidates` and `precedents` (retrieval), `gold_rank`.

**Rules:** one product and one primary current code per ruling; descriptions never contain the code's heading or
subheading digits; dev and test items with a near-copy among earlier rulings were dropped; training rulings that
resemble ATLAS test items were removed; labels come only from CBP rulings and the USITC HTSUS export of 2026-10-30.
SHA-256 checksums: `SHA256SUMS`.

**Sources and terms:** CBP rulings are US government works. The ATLAS split comes from the public copy
`Dayanand314Krishna/cross_rulings_hts_dataset_for_tariffs` (Apache-2.0). This dataset adds no personal data beyond what
CBP publishes in its rulings.
