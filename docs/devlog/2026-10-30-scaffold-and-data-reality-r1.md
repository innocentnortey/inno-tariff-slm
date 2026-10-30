# 2026-10-30 — scaffold and data reality (run r1)
Project: inno-tariff-slm · Writer: Claude (Opus 5.5), background session on the Mac · Base: no commits yet.

## Stage 0 scaffold
- **Changed:** Created the repo, copied the principles pack (both halves) and the build-loop rules, bootstrapped the context system with `icm-project` 1.6.1.
- **Why:** zero-to-hero requires Stage 0 before any design or code.
- **Checked:** `check_context.py` (shape only); route walkthrough for two requests.
- **Remaining:** GitLab `origin` (Innocent), Stage 1–4 sign-offs.

## Data reality and draft pipeline
- **Changed:** Profiled the HF rulings copy and the USITC export; drafted the subset build (Ch. 61/62/64), candidate siblings, deciding-attribute labels and deterministic checks; ran three non-model baselines.
- **Why:** Choose the subset on coverage, not preference; learn whether rules already solve the task.
- **Checked:** Numbers in `docs/data/README.md`; two lexicon bugs found by reading samples and fixed.
- **Remaining:** 50-label hand review; no model runs.

## Paused for the concept video
- **Changed:** Stopped implementation at Innocent's instruction; results preserved, code uncommitted.
- **Why:** Concept-stage submission first.
- **Checked:** `check_context.py` passes.
- **Remaining:** Resume per `.claude/state/resume.md`.

## Concept video
- **Changed:** Copied `demo-video` into the repo and adapted it for a concept-stage video (page sections instead of an app, status-labelled claims, no technical-challenges segment); Codex (gpt-6.1-sol) wrote the 662-word narration; rendered `docs/artifacts/2026-10-30-concept-video.mp4`.
- **Why:** Innocent asked for a conceptual early-submission introduction.
- **Checked:** Dry run passed; 4:27 at 155 wpm; no silent overruns; captions match narration word count; frames reviewed, one scroll defect fixed.
- **Remaining:** Innocent's listening check (pronunciation, emphasis); `journey_ask` reads at 186 wpm.
