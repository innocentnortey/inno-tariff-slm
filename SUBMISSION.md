# Submission tracker — Week 7, Train Your Own SLM

Source of every row: `Gauntlet AI/course-material/2026-10-27-week7-train-your-own-slm-brief.md`. Status: ☐ not started · ◐ in progress · ☑ done (with evidence link).

## Version 2 — open-set classification (2026-11-02, current)

The earlier version always placed the correct code among eight supplied candidates. Version 2 replaces that with an
open-set benchmark (any of ~19,800 HTSUS lines; fresh CBP rulings; no answer in the input). Results:
[`docs/evals/results-v2.md`](docs/evals/results-v2.md).

| Requirement | Status | Evidence |
|---|---|---|
| Dataset published | ☑ | https://huggingface.co/datasets/youngjr1232/tariff-hts-openset-v2 (commit `4797cce5f131cbaea40f76420203f7847bd5f21e`), card + checksums |
| Model on HF Hub (public) | ☑ | https://huggingface.co/youngjr1232/tariff-classifier-qwen3-4b (commit `4eb6e2029468a5ce8eda708c1664228856c63cd2`), merged bf16 |
| Running inference demo | ☑ | https://youngjr1232--tariff-classifier-demo-web.modal.run (key in Keychain `tariff-demo-key`); base vs tuned side by side on the same evidence |
| Eval harness + results, base vs tuned | ☑ | Final test 500: base 42.0% → tuned 59.8% (+17.8, CI +13.6 to +22.0); Opus 71.6%. `scripts/eval_openset.py`, `train/modal_openset.py`, `scripts/compare_runs.py` |
| Latency and cost | ☑ | Single request: 0.89 s (H100) / 1.74 s (A10G) vs Opus 9.9 s; `runs/latency/` |
| Brainlift | ☑ | [`docs/delivery/brainlift-v2.md`](docs/delivery/brainlift-v2.md) |
| Data-efficiency curve (≥4 checkpoints) with justified minimum N | ☑ | 2,356 → 52.3%, 4,716 → 53.3%, 9,431 → 56.3%, 19,141 → 57.7% (base 42.0%); minimum viable N ≈ 9,400 (−1.3 vs full, CI −4.0 to +1.3). [`results-v2.md`](docs/evals/results-v2.md#data-efficiency-curve-dev-300-items-rag-2026-11-02); caveat: steps scale with N |
| 3–5 min demo video, base vs tuned live | ◐ | `docs/artifacts/2026-11-02-demo-video-v2.mp4` (4:07, 183 wpm, captions `.srt`): two real fresh CBP rulings run live on the deployed demo, base vs tuned on the same evidence. Narration by Codex (`docs/delivery/2026-11-02-demo-narration-v2.md`); source `.demo/v2/`. **Not grader-supplied:** both examples were picked from the test set (said so in the video); a grader can type their own product into the live demo during review |
| Staff held-out set | ☐ | Not received |

## Version 1 — eight-candidate selection (2026-11-01, historical)

## Early submission (Thursday midnight)
| Requirement | Status | Evidence |
|---|---|---|
| Finalized Behavior Spec (falsifiable, 1–2 sentences) | ☑ | `docs/planning/tariff-behavior-and-evals.md` (approved by Innocent 2026-11-01) |
| Prompt-Ceiling Ablation report (≥2 families × 3 strategies × ≥30 scenarios) | ☑ | `docs/evals/prompt-ceiling-2026-11-01.md` (Opus 5.5 + GPT-5.6 Sol × 3 strategies × 157 clean + 58 robustness items, judged; plateau at 78–86%; absolute reliability bar still to be set) |
| Eval harness: judge, behavioral check, base-vs-tuned mechanism | ◐ | `eval.py` with deterministic checks, Gemini judge (uncalibrated), robustness set, resume; base-vs-tuned runs pending |
| Full loop generate → train → eval on a smoke batch | ☑ | `train/modal_app.py --mode smoke` on a Modal H100, 2026-11-01: 64 examples, 20 steps, base 3.3% → tuned 20.0% spec pass on 30 dev items (`runs/modal/20261102-020543-smoke-n64/meta.json`) |
| First real dataset generated and filtered; first QLoRA run | ☑ | Reviewed dataset (`docs/data/`); Qwen3-1.7B QLoRA on 5,865 examples, 1 epoch, 367 steps, 13 min on a Modal H100 (`runs/modal/full-n5865-v1/meta.json`) |
| First base-vs-tuned numbers | ☑ | Dev (157): spec adherence 3.2% → 79.0%, exact code 14.9% → 81.3%, NEED_INFO recall 0% → 61.1%; robustness (58) 0.0% → 79.3% (`runs/modal/base-eval-v1/`, `runs/modal/full-n5865-v1/`). Below the bar (Opus 86.0% / 87.9%) |
| One failure mode diagnosed and fixed by a data change (v2) | ☑ | v1 chose a code on 39% of NEED_INFO dev items (6% of training items were NEED_INFO). v2 adds 678 ablated NEED_INFO copies (`scripts/make_train_v2.py`), same hyperparameters: NEED_INFO recall 61.1% → 94.4%, over-asking 2.2% → 0.7%, spec adherence 79.0% → 84.7% (`runs/modal/full-n6543-v2/`). Caveat: 18 dev NEED_INFO items, 14 built like the new training copies |
| ≥2 points on the data-efficiency curve | ☑ | 5 points on v2 data, nested subsets (`runs/modal/data-efficiency-curve-v2.json`): 500 → 30.6%, 1,000 → 45.2%, 2,000 → 61.8%, 4,000 → 76.4%, 6,543 → 84.7% dev spec adherence; asking appears between 304 and 624 NEED_INFO examples. Caveat (Codex review): epochs were held fixed, not optimizer steps (32 vs 409 updates), so size and training length are confounded |
| Drafts: dataset shape, checkpoint, Brainlift | ☐ | |
| Concept-stage video (direction only, not the technical evidence) | ☑ | `docs/artifacts/2026-10-30-concept-video.mp4` (4:27, Codex narration `docs/delivery/2026-10-30-concept-narration.md`) |

## Final submission (Sunday noon)
| Requirement | Status | Evidence |
|---|---|---|
| Dataset published | ☑ | https://huggingface.co/datasets/youngjr1232/tariff-slm-hts-61-62-64 (HF commit `03edafdeb1168bc5c01bb0c5adcada11e6416c14`), provenance card + checksums |
| Model on HF Hub (public) + running inference demo | ☑ | https://huggingface.co/youngjr1232/tariff-specialist-qwen3-1.7b (weights commit `ba966b95f65fb5b748d14d39fa94ab506d624706`, card `4dc89636`); live demo `modal run train/modal_app.py --mode predict --adapter v4-rebal-2ep --subheading <6-digit> --description "..."` |
| Eval harness + results, base vs tuned, own set and staff held-out set | ◐ | Sealed test (221 + 60): base 6.3% → tuned 80.1% (one command; 4-bit eval 81.0%), robustness 75.0% (Opus 84.6% / 75.0%) — `docs/evals/step10-head-to-head-2026-11-01.md`, `docs/delivery/brainlift.md`. Staff held-out set not received |
| Full data-efficiency curve (≥4 checkpoints) with justified minimum N | ◐ | 5 checkpoints done; still rising at the full set and below the bar (86.0% / 87.9%), so a minimum N that holds the behavior is not yet found |
| Brainlift | ☑ | `docs/delivery/brainlift.md` |
| 3–5 min demo video incl. a live grader-supplied prompt | ☐ | |
| Verification: public checkpoint + commit hash; `eval.py --model --eval-set` one command; raw judge JSONL; pinned versions; ablation scripts and logs | ☑ | `eval.py --model hf:youngjr1232/tariff-specialist-qwen3-1.7b --eval-set data/processed/test.jsonl` → 80.1% (177/221), 0 errors (`runs/eval-hf-test.log`); judge JSONL in `runs/prompt-ceiling-*/cells/*/judge.jsonl`; versions in `runs/modal/*/meta.json`; ablation `scripts/prompt_ceiling.py` |
