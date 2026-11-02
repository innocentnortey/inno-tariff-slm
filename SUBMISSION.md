# Submission tracker — Week 7, Train Your Own SLM

Source of every row: `Gauntlet AI/course-material/2026-10-27-week7-train-your-own-slm-brief.md`. Status: ☐ not started · ◐ in progress · ☑ done (with evidence link).

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
