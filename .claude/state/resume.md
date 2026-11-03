# Resume — inno-tariff-slm

- **Phase:** zero-to-hero Stage 0 done 2026-10-30; Stage 1–2 drafts in progress (light mode). ICM: Phases 1 and 3 done; see [icm-progress](icm-progress.md).
- **Inspected environment:** Mac, `uv` 3.12; no model API keys on the Mac (frontier calls run on the VPS); raw data in `data/raw/` (git-ignored).
- **Unresolved:** GitLab `origin` (Innocent creates it); skip approvals for Stages 1–4 gates under the deadline; HF account for publishing.
- **Resumed 2026-11-01** (Innocent: "we also can start working on this whole slm thing"). The data build was revised after the label review; code and docs are uncommitted.
- **Concept video done 2026-10-30:** `docs/artifacts/2026-10-30-concept-video.mp4`; regenerate with `.demo/build_shotlist.py` then `demo.py render --subs` (project skill copy in `.claude/skills/demo-video/`).
- **Label review done 2026-11-01** by Claude, delegated by Innocent ("i trust you to do a better job than me"): `docs/data/label-review-2026-11-01.md`; 21 regression tests in `tests/test_attributes.py`; rules baseline now 40.8% exact on the 227-item test set.
- **Prompt-ceiling ablation done 2026-11-01:** `docs/evals/prompt-ceiling-2026-11-01.md` (run `runs/prompt-ceiling-20261102-013242/`, also on the VPS). Best: Opus 5.5 CoT 86.0% spec, 87.9% robustness; surviving failure: residual "Other" lines. About $56 spent; OpenRouter $25.28 left (Innocent topped up $25). Label review round 3 + decision 5 applied (125 more items dropped). Repo copy on the VPS at `/home/linuxuser/workspaces/inno-tariff-slm` (rsync, no git remote).
- **Decided 2026-11-01:** reliability bar B (match or beat Opus 5.5 CoT: ≥86.0% spec, ≥87.9% robustness; head-to-head on test in step 10); GPU = Modal H100.
- **Training 2026-11-01 (Modal H100, Qwen3-1.7B QLoRA):** smoke done; v1 (5,865) dev 79.0% spec / 79.3% robust; v2 (+678 ablated NEED_INFO, `train_v2.jsonl`) 84.7% / 82.8%, NEED_INFO recall 94.4%. Frozen eval checksums in `docs/data/README.md`. Data-efficiency curve done (5 points, `runs/modal/data-efficiency-curve-v2.json`): still rising at 6,543, below the bar; asking appears between 304 and 624 NEED_INFO examples.
- **Step 10 done 2026-11-01** (`docs/evals/step10-head-to-head-2026-11-01.md`): tuned v2 78.7% spec / 71.7% robust on the sealed test vs Opus 84.6% / 75.0% — bar B not met; tuned wins on asking (86.5% vs 73.0%), loses on residual "Other" lines (74.3% vs 92.9%). v3 was a negative result. Codex GPT-6 Astra review running → `docs/reviews/`.
- **Next action:** decide how to close the gap to the bar (more data or a second data change for residual lines), then step 10 head-to-head on test; decides whether training prompts include retrieved rulings. The judge still needs ~20 human labels before it gates.
- **Training roadmap page 2026-11-01:** `docs/artifacts/2026-11-01-training-roadmap.html` walks ten steps; step 10 tests the SLM-versus-RAG hypothesis (added to `docs/planning/tariff-behavior-and-evals.md` as experiment 6). Open decision: do training prompts include retrieved rulings.
- **Research imported 2026-11-01:** start at `docs/research/README.md`; original research and Week 7 requirements now have local copies with source checksums. `docs/research/slm-vs-rag.md` records the unproven fine-tuning hypothesis; implementation remains paused.
- **Reset 2026-11-02 (Innocent): answer the original question on an open-set benchmark.** Roadmap
  `docs/planning/tariff-research-roadmap.md`; protocol frozen `docs/evals/benchmark-protocol.md`; data
  `docs/data/benchmark-v2.md`. Goal set the same day: tuned model to beat Opus 5.5 on the Track B final test, three
  training tries. Heavy work runs on Modal (builds, training, small-model evals) and the VPS (fetch, API evals); the
  VPS disk is nearly full, so never put training files there.
- **Blocked 2026-11-02 02:59 CST: Modal workspace hit its spend limit** ("exceeded its spend limit"). Try 1
  (`try1-full-r16-e1`, 89% done) and try 2 (`try2-temporal-recent-sched-r16-e1`, 49% done) were killed before saving;
  neither produced an adapter, and both are treated as not yet run. Checkpointing every 150 steps with resume is now in
  `train/modal_openset.py`. **Next action once Modal accepts jobs:** rerun both with the same `--name`
  (commands in `docs/planning/tariff-research-roadmap.md`), read dev results, then try 3, then the one final test.
- **Benchmark v2 finished 2026-11-02:** results `docs/evals/results-v2.md`. Final test (500 fresh rulings): tuned
  try 3 59.8%, base 42.0%, Opus 71.6%. Hypothesis supported; Opus goal not met after three tries. Checkpoint
  `checkpoints/try3-rationales-backfill-cont-b4/`. Memory follow-up done (dev `rag` 60.3%, closed-book
  45.7%, ATLAS 12.5%; in the report). **Next action:** Innocent's call on publishing, committing, or a next
  experiment (e.g. combining closed-book and retrieval answers, more memory passes); the CROSS backfill can resume from each fetcher's last
  number (`data/raw/cross_backfill_x*/misses.txt` on the VPS). Nothing from this round is committed yet.
