# Tariff specialist: execution plan

Status as of 2026-10-30: **concept stage.** Implementation is paused at Innocent's instruction until the concept
video is done. Code repo: `inno-tariff-slm` (zero-to-hero Stage 0 done; Stages 1–4 drafts in these planning docs).

## Stages (dependency order)

| # | Stage | Kind | Depends on | Status |
|---|---|---|---|---|
| 1 | Finalize behavior and data subset; hand-review 50 labels | Mandatory | — | Started (spec and subset drafted) |
| 2 | Build the evaluation harness (checks, judge, `eval.py`) | Mandatory | 1 | Draft code exists, not reviewed |
| 3 | Prompt-ceiling ablation | Mandatory | 2, API keys (VPS) | Not started |
| 4 | Construct and filter training data | Mandatory | 1 | Draft build exists |
| 5 | Fine-tune and evaluate the first model | Mandatory | 2, 4, GPU | Not started |
| 6 | Diagnose failures, fix the data (v2) | Mandatory | 5 | Not started |
| 7 | Four-checkpoint data-efficiency curve | Mandatory | 5 | Not started |
| 8 | Minimal agent demo around the specialist | Stretch | 5 | Not started |
| 9 | Publish dataset, checkpoint, results, video | Mandatory | 3, 5, 7 | Not started |

## Gauntlet requirements vs today

| Requirement (brief) | Early | Final | Today |
|---|---|---|---|
| Falsifiable behavior spec | ✓ | | Drafted, awaiting sign-off |
| Prompt-ceiling report (2 families × 3 strategies × ≥30) | ✓ | | Not run |
| Eval harness with judge and behavioral check | ✓ | | Draft code, not reviewed |
| Generate → train → eval loop on a smoke batch | ✓ | | Not run |
| First dataset and QLoRA run; base-vs-tuned numbers | ✓ | | Not run |
| One failure fixed by a data change | ✓ | | Not run |
| ≥2 data-efficiency points (early), ≥4 (final) | ✓ | ✓ | Not run |
| Public model with commit hash; one-command eval; judge JSONL; pinned versions | | ✓ | Not done |
| Staff held-out evaluation; live grader prompt in demo | | ✓ | Not done |
| Published dataset; Brainlift; 3–5 minute video | | ✓ | Concept video next |

**This concept package does not meet the early-submission technical evidence requirements.** It presents the
direction only.

## Blockers and needed decisions

- **GitLab `origin`:** Innocent creates `innocentnortey/inno-tariff-slm`.
- **Frontier API access:** the keys live on the VPS; this Mac has none.
- **GPU for training:** Modal, RunPod or Colab; covered by Gauntlet.
- **Hugging Face account:** for publishing.
- **Stage-gate skips:** zero-to-hero needs Innocent's explicit yes for each skipped gate under the deadline.

## Verification status

The vision page was checked in Chrome on 2026-10-30:

- **Console:** no errors.
- **Mock workflow:** all 21 scenario-and-step panels render.
- **Architecture:** all 11 nodes open their details.
- **Roadmap filter:** works.
- **Layout:** no horizontal overflow at desktop width or at 500px.

None of these checks shows that any model works.
