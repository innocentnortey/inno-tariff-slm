# Tariff Specialist SLM — concept stage

**Live concept page:** https://inno-tariff-slm.onrender.com (Render static site `srv-dbi2uetg1s2s73drae0g`, auto-deploys from GitHub `main`)

Gauntlet AI Week 7, *Train Your Own Small Language Model*. The proposal: a human-supervised **AI trade-compliance
analyst** for importers and customs brokers, built around one small fine-tuned model. Given a product description and
eight candidate US tariff (HTS) codes, the model picks the one U.S. Customs would assign and names the deciding
attribute, or answers `NEED_INFO` and names the missing attribute.

**Status: concept stage.** No model has been trained. The page's walkthrough is a hand-written mock built on real CBP
rulings, codes and duty rates. Measured so far: a profile of the public rulings data and three non-model baselines.
This package does not yet meet Gauntlet's early-submission technical evidence requirements.

## What's here

| Path | What it is |
|---|---|
| `site/index.html` | The concept page served on Render (copy of `Gauntlet AI/docs/research/tariff-compliance-vision.html`) |
| `docs/planning/` | PRD, behavior spec and evals, data and training plan, architecture, execution plan, video outline (snapshot) |
| `docs/data/README.md` | First data-reality check: counts, splits, preliminary baselines |
| `docs/delivery/2026-10-30-concept-narration.md` | Concept-video narration (written by Codex) |
| `src/tariff_slm/`, `scripts/build_dataset.py`, `eval.py` | Draft data build and deterministic checks, **paused and unreviewed** |
| `.demo/` | Shot list that regenerates the concept video |

Data is not in this repo: the public copy of the CBP rulings used for profiling has no licence, so derived data is
published only after its terms are checked.

## Deploy

Render static site from this repo's `main` (publish directory `site/`, no build step). Source of truth is Gauntlet
GitLab (`innocentnortey/inno-tariff-slm`), mirrored to GitHub, which Render builds from.
