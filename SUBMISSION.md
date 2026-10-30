# Submission tracker — Week 7, Train Your Own SLM

Source of every row: `Gauntlet AI/course-material/2026-10-27-week7-train-your-own-slm-brief.md`. Status: ☐ not started · ◐ in progress · ☑ done (with evidence link).

## Early submission (Thursday midnight)
| Requirement | Status | Evidence |
|---|---|---|
| Finalized Behavior Spec (falsifiable, 1–2 sentences) | ◐ | `Gauntlet AI/docs/planning/tariff-behavior-and-evals.md` (draft, awaiting sign-off) |
| Prompt-Ceiling Ablation report (≥2 families × 3 strategies × ≥30 scenarios) | ☐ | runner scaffolded; needs VPS API keys |
| Eval harness: judge, behavioral check, base-vs-tuned mechanism | ◐ | deterministic checks and baselines first |
| Full loop generate → train → eval on a smoke batch | ☐ | |
| First real dataset generated and filtered; first QLoRA run | ☐ | |
| First base-vs-tuned numbers | ☐ | |
| One failure mode diagnosed and fixed by a data change (v2) | ☐ | |
| ≥2 points on the data-efficiency curve | ☐ | |
| Drafts: dataset shape, checkpoint, Brainlift | ☐ | |
| Concept-stage video (direction only, not the technical evidence) | ☑ | `docs/artifacts/2026-10-30-concept-video.mp4` (4:27, Codex narration `docs/delivery/2026-10-30-concept-narration.md`) |

## Final submission (Sunday noon)
| Requirement | Status | Evidence |
|---|---|---|
| Dataset published | ☐ | |
| Model on HF Hub (public) + running inference demo | ☐ | |
| Eval harness + results, base vs tuned, own set and staff held-out set | ☐ | |
| Full data-efficiency curve (≥4 checkpoints) with justified minimum N | ☐ | |
| Brainlift | ☐ | |
| 3–5 min demo video incl. a live grader-supplied prompt | ☐ | |
| Verification: public checkpoint + commit hash; `eval.py --model --eval-set` one command; raw judge JSONL; pinned versions; ablation scripts and logs | ☐ | |
