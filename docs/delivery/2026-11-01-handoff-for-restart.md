# Handoff for the restart session — what this project proved, and how it differs from the original hypothesis

Written 2026-11-01 for the session that restarts the Week 7 project. Read this before designing the new benchmark.

## The one difference that matters

| | Original hypothesis (what the restart should test) | What this project actually measured |
|---|---|---|
| Task | Find the right 10-digit HTS code among all ~19,949 schedule lines (the ATLAS setup, arXiv 2509.18400) | Choose among **8 close candidates**, with the correct code **guaranteed** to be in the list, or answer `NEED_INFO` |
| Frontier result | GPT-5-Thinking: 25.0% fully correct (ATLAS) | Claude Opus 5.5, best prompt: 84.6% on our sealed test |
| What it tests | Search through a deep hierarchy + legal judgment | Careful reading of eight close lines |
| Consequence | Frontier models struggle, so a specialist can win | Frontier models do well, so the specialist can't show "frontier fails" |

The narrowing was set in the planning docs (the behavior spec put "finding candidates" outside the model and gave every
model the same eight). It is defensible engineering, but it removed the difficulty the research is about. **If the
restart wants to test "a small model beats frontier models at tariff classification", the benchmark must include the
search: either the full schedule, or candidates from a realistic retriever where the gold code is not guaranteed.**

## What this project did establish (usable in the restart's framing)

- **Calibrated abstention is the specialist's measured edge.** Sealed test: asks when the deciding fact is missing
  84–89% vs Opus 73.0%; natural missing-fact cases 11/13 vs 6/13; over-asking 1.6% vs 3.3%. Taught by a data change
  (v1 → v2: 61% → 94% recall on dev, settings unchanged).
- **On choosing the code the specialist trails** (80.1% vs 84.6%), mostly on residual "Other" lines decided by legal
  definitions (Note 3(a) suits, "sets", statistical notes) that the candidate text names but does not include.
- **Data levers that worked:** rebalancing away from gender splits (72% of decidable items) toward rare branches, plus
  a second epoch. Neither alone helped; together +6 clean / +3 robust on dev over v2, held across two seeds. A 2.4x
  larger model (Qwen3-4B) added nothing on top.
- **Seed noise is about 6 dev items** (157-item dev set). Never judge a 1–3 item change on one seed.
- **Coverage matters:** dev accuracy 54.5% on codes unseen in training vs 88.9% on seen codes.

## What to change in the restart

1. **Benchmark the hard task first.** Run the frontier baseline on the open search (or realistic retrieval) before
   designing the specialist's behavior, so the prompt ceiling is measured on the task the research describes.
2. **Treat retrieval as part of the system under test.** Plain BM25 recall@8 is 4%; a hierarchical retriever (chapter →
   heading → subheading) is the first thing to build.
3. **Put the legal definitions in the input** (the notes a candidate line references), for every model, as its own arm.
4. **Grow coverage of rare codes** from the 3,154 obsolete-code rulings and the 124 dropped items, using facts from the
   original ruling text, before reaching for synthetic data. A strict synthetic swap (same-subheading gender/fiber)
   yields only ~20 items: men's and women's garments sit in different headings.
5. **Keep a fresh holdout.** This project's test set has been looked at twice.

## Reusable assets

- Eval harness: `eval.py` (deterministic checks, judge, robustness set, resume, parallel), `scripts/prompt_ceiling.py`.
- Modal training/eval/predict/publish app: `train/modal_app.py` (written for transformers 5.x; image cached).
- Data build + label code: `scripts/build_dataset.py`, `src/tariff_slm/data/attributes.py` (+25 regression tests).
- Frozen eval files + checksums: `docs/data/README.md`. Public HF: model `youngjr1232/tariff-specialist-qwen3-1.7b`,
  dataset `youngjr1232/tariff-slm-hts-61-62-64`.

## Pitfalls already paid for

- Candidate order used Python `hash()` (per-process random) before 2026-11-01; the seed is now SHA-1.
- transformers 5: `warmup_ratio` removed (use float `warmup_steps`), `torch_dtype` → `dtype`,
  `apply_chat_template(return_tensors=...)` returns a mapping.
- codex-cli ≥ 0.165: `codex exec --full-auto` is gone; use `--sandbox workspace-write`.
- OpenRouter in-flight credit reservation fails parallel runs on a low balance; Modal limits app creation per second
  (stagger launches ~25 s).
- macOS has no `timeout`; use a PID watchdog loop.
