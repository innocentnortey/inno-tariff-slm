# Benchmark v2 data: open-set 10-digit classification (built 2026-11-02)

The files live in `data/benchmark/` (git-ignored, like all derived ruling data; see *Terms* below). The earlier
chapter 61/62/64 files in `data/processed/` are kept unchanged as historical evidence. The first Mac build of v2 is
kept in `data/benchmark_mac_v0/` and is not used for any reported number.

## Sources

| Input | What it is | SHA-256 |
|---|---|---|
| `data/raw/cross_rulings.json` | HF `orlandowhite/hts-cross-rulings`, 54,558 rulings, 2000 → 2025-08-01 | `0c9fd822…8311` |
| `data/raw/cross_recent_all/*.jsonl` | 3,803 rulings fetched from CROSS, NY N351546–N365822, 2025-07-28 → 2026-10-09 (`scripts/fetch_cross_recent.py`) | `70027224…ef0a`, `e0c94f5c…7b85607`, `ddda992e…632701` |
| `data/raw/hts_current.json` | USITC HTSUS export, 2026-10-30 | `bea73f23…2a09` |
| `data/raw/atlas/test.jsonl` | ATLAS test split (public copy, revision `0a66ad34`) | `58e2d071…5c18` |

## Build

```bash
# Run on a Modal H100 (dense embeddings); outputs are copied back to data/<out-name>/.
modal run train/modal_build.py                                   # canonical: data/benchmark/
modal run train/modal_build.py --extra "--temporal-train --train-add-dev-pool" --out-name benchmark_try2
```

`scripts/build_openset.py` does the work. Its docstring lists each rule:

1. Keep a ruling only when it is a classification ruling for one product, with one primary 10-digit code
   (chapters 01–97, ignoring chapter 98/99 lines) that exists in the current HTSUS. An 8-digit code is mapped only
   when the current schedule has exactly one 10-digit line under it.
2. The description is CBP's own fact sentences (`src/tariff_slm/openset/facts.py`), with every sentence naming a code,
   heading, chapter, note, proposed classification, duty or boilerplate removed. Any description still carrying the
   code's first 4 or 6 digits is dropped (11 rulings).
3. Training text conflicts: identical text with different codes, and near-identical pairs (TF-IDF cosine ≥ 0.95)
   with different codes, are dropped (89 rulings, 170 pairs).
4. ATLAS test rulings: the top same-6-digit matches of each ATLAS test item at cosine ≥ 0.15 (210 rulings) are
   removed from train, dev and every index (`scripts/match_atlas.py`).
5. Eval items with a near-copy (cosine ≥ 0.90) among earlier rulings, or within their own split, are dropped.

## Counts and frozen files

| File | Items | What | SHA-256 |
|---|---|---|---|
| `train.jsonl` (try 1) | 19,508 | rulings ≤ 2023, leave-one-out retrieval context | `4e97a244…faf1b` |
| `dev.jsonl` | 300 | sample of 2,147 clean rulings, 2024-01 → 2025-08-01 | `ed09ab91…4e9d` |
| `test.jsonl` | 500 | sample of 2,174 clean fetched rulings, 2025-08-07 → 2026-10-09 | `94c9efad…fdc1df` |
| `atlas_test.jsonl` | 200 | ATLAS question + label; 168 labels exist in the current HTSUS | `3063f47c…dcb3cea` |
| `benchmark_try2/train.jsonl` (try 2) | 21,439 | train + 1,931 dev-pool rulings; each item sees only earlier precedents | `2070c630…76383` |

Retrieval recall of the gold code in the 20 shown candidates: dev 74.7%, test 80.0%; try-1 training items 88.1%,
try-2 training items 80.6%.

**Reproducibility.** Dense scores on a GPU vary in the last bits between runs, which can swap the order of tied
candidates: a second build reordered candidates for 47 of 300 dev items, with the same items, precedents and recall.
Reported numbers always use the frozen files above; a rebuild is a new artifact.

## Terms

CBP rulings are U.S. government works. The HF corpus copy has no stated licence, and the ATLAS public copy is
Apache-2.0. The derived files are kept out of git and were published on Innocent's instruction (2026-11-02) as
https://huggingface.co/datasets/youngjr1232/tariff-hts-openset-v2 (commit `4797cce5`), with a card and checksums.
