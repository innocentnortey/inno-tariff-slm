# Data reality — first check (2026-10-30), labels reviewed 2026-11-01

Run by Claude on the Mac. Labels reviewed and the build fixed on 2026-11-01: [label review](label-review-2026-11-01.md). Commands: `scripts/build_dataset.py` (see its docstring) and
`eval.py --model baseline:<name> --eval-set data/processed/test.jsonl`. Raw and processed data are git-ignored.

| Fact | Value |
|---|---|
| HF `orlandowhite/hts-cross-rulings` full file | 54,558 unique rulings, 2000–2025 (viewer's 80,844 = full + 26,286-row filtered subset) |
| Codes valid in today's schedule (full file) | 22,540 of 54,558 (41.3%) |
| USITC export (2026-10-30) | 19,949 ten-digit lines |
| Single-code rulings after cleaning (all chapters) | 33,144 (dropped: 19,207 not one 10-digit code, 2,123 leaking descriptions, 84 too short) |
| Chapters 61, 62, 64 | 9,566; 3,154 obsolete codes dropped; 83 dropped as conflicting (description points at the sibling line); 124 dropped as an unstated attribute against an "Other" sibling (review decision 5) |
| Splits | train 5,865 (≤2022) · dev 143 rulings + 14 ablated = 157 items (2023) · test 197 rulings + 24 ablated = 221 items (2024–2025); robustness set `dev_robust.jsonl` 58 items |
| Test kinds | decide 110 · residual 70 · unlabelled 4 · natural NEED_INFO 13 · ablated NEED_INFO 24 |
| BM25 recall on test rulings | 4.0% @8 · 8.5% @20 · 20.6% @50 |
| Baselines, exact 10-digit on items needing a code (2026-11-01, after review round 3) | random 11.4% · keyword 16.3% · attribute rules 37.5% (rules spec pass 24.9%, NEED_INFO recall 13.5%, over-asking 7.1%). Before the label fixes: 10.3% · 14.1% · 20.5% |

Caveats: the `full_description` and `reasoning` fields are model-written summaries, and most natural NEED_INFO items
exist because the summary dropped a fact the original ruling states (see the review). The attribute lexicon defines
dimensions and NEED_INFO labels; it was reviewed by Claude (100 items read, every item pattern-audited), not by an
independent human. The rules baseline shares that lexicon, so its attribute scores are optimistic.

## Frozen evaluation files (2026-11-01)

These files are the canonical eval sets for every reported number from the prompt-ceiling run onward. Rebuilding with
`scripts/build_dataset.py` no longer reproduces them byte for byte: before 2026-11-01 the candidate order was seeded
with Python's `hash()` of a string, which changes per process, so each build reshuffled the eight candidates (same
codes, different order). The seed is now stable (SHA-1), but the frozen files were made before the fix. Publish these
files, not a rebuild.

| File | Items | SHA-256 |
|---|---|---|
| `dev.jsonl` | 157 | `8d88fcd95ced407d228b5eabfce743c5207e72275cf430bfe30ecc970344390a` |
| `test.jsonl` | 221 | `f46a27fd28442ecbd92ff84a711d923d99274932914251266b89d4d3b0d848dc` |
| `dev_robust.jsonl` | 58 | `901bf7efcf943926bb867048a329a45cbafe7216f6c8385b276df09663d9d390` |
| `train.jsonl` (v1) | 5,865 | `bf15cab1505e59f95d92f4a53525cbe4a56973abbc959c19cf4b7ec95883e2e8` |
| `train_v2.jsonl` (v1 + 678 ablated `NEED_INFO` copies, `scripts/make_train_v2.py --share 0.25 --seed 2026`) | 6,543 | `ac8d4f7264c11b9585e44e3c8a1a2a21c474d52cbb27d966ef7fb872c08386f0` |
| `train_v3.jsonl` (v2 + 1,290 perturbed copies, `scripts/make_train_v3.py --share 0.2 --seed 2027`; negative result, not used) | 7,833 | `1f2bb5cd19acf277d78cd216d1606d533726de41e97623d183c12eb8f93382d3` |
| `test_robust.jsonl` (60 test items, same perturbation phrasing as the dev robustness set) | 60 | `766ab66478deb11b7ba407e8680e115521a57fd130e849b7e93eded31e06d070` |
