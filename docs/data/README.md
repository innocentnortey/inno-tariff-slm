# Data reality — first check (2026-10-30, preliminary)

Run by Claude on the Mac; implementation then paused. Commands: `scripts/build_dataset.py` (see its docstring) and
`eval.py --model baseline:<name> --eval-set data/processed/test.jsonl`. Raw and processed data are git-ignored.

| Fact | Value |
|---|---|
| HF `orlandowhite/hts-cross-rulings` full file | 54,558 unique rulings, 2000–2025 (viewer's 80,844 = full + 26,286-row filtered subset) |
| Codes valid in today's schedule (full file) | 22,540 of 54,558 (41.3%) |
| USITC export (2026-10-30) | 19,949 ten-digit lines |
| Single-code rulings after cleaning (all chapters) | 33,144 (dropped: 19,207 not one 10-digit code, 2,123 leaking descriptions, 84 too short) |
| Chapters 61, 62, 64 | 9,566; 3,154 obsolete codes dropped |
| Splits | train 6,064 (≤2022) · dev 146 rulings (2023) · test 202 rulings (2024–2025) + 33 ablated NEED_INFO copies = 235 items |
| Test kinds | decide 102 · residual 62 · unlabelled 21 · natural NEED_INFO 17 · ablated NEED_INFO 33 |
| BM25 recall on test rulings | 4.0% @8 · 8.4% @20 · 20.3% @50 |
| Baselines, exact 10-digit on items needing a code | random 10.3% · keyword 14.1% · attribute rules 20.5% (rules NEED_INFO recall 24%) |

Caveats: the `full_description` and `reasoning` fields are model-written summaries; the attribute lexicon defines
dimensions and NEED_INFO labels and needs a 50-item hand review; the rules baseline shares that lexicon.
