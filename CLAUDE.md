# inno-tariff-slm — project entry

## What this project is
Gauntlet AI Week 7 ("Train Your Own Small Language Model"). We fine-tune a 1B–4B open model (QLoRA) into a
**tariff-classification specialist**: given an importer's product description and a retrieved shortlist of US HTS
codes, it picks the one code CBP would assign and names the deciding attribute, or asks for the missing attribute.
The specialist is one component of a human-supervised **AI trade-compliance analyst** (intake → retrieval →
specialist → duty maths → evidence → human review). Stack: Python 3.12 with `uv`, Hugging Face datasets and
models, Unsloth/TRL for QLoRA. Innocent owns scope and every sign-off; Claude drafts and builds.

## System boundaries
| Area | Owns | Home |
|---|---|---|
| Data | Rulings ingest, cleaning, subset, splits, candidate sets | `src/tariff_slm/data/` (planned), `data/` |
| Evals | Behavior checks, baselines, judge, prompt-ceiling runner, `eval.py` | `src/tariff_slm/evals/` (planned), `evals/` |
| Training | QLoRA runs, data-efficiency sweep | `train/` (planned) |
| Product vision and planning | PRD, behavior and evals, data and training, architecture, execution plan | `Gauntlet AI/docs/planning/tariff-*.md` |

## Non-negotiable boundaries
- **The model trains on one behavior only.** Retrieval, duty maths and validation stay outside the model. Rule: [agent-architecture](.claude/rules/agent-architecture.md).
- **Labels come from CBP rulings and the USITC schedule, never from a teacher model.** Teacher text is explanation only, filtered against the ruling. Rule: [verification-evals-observability](.claude/rules/verification-evals-observability.md).
- **Evals exist before training, and no number is reported that was not measured.** Rule: [verification-evals-observability](.claude/rules/verification-evals-observability.md).
- **Every model sees the same candidates.** A retrieval miss is reported as retrieval recall, never as a model error. Rule: [retrieval-and-context](.claude/rules/retrieval-and-context.md).
- **No ruling text or dataset is republished before its terms are checked.** Domain reference: [domain](.claude/reference/domain.md).
- **HTML means a local file, never a Claude Artifact.** Rule: [html-files-not-artifacts](.claude/rules/html-files-not-artifacts.md).
- **Versioning on Gauntlet GitLab** (`origin` created by Innocent; port 22022). Rule: [gauntlet-gitlab-versioning](.claude/rules/gauntlet-gitlab-versioning.md).

## Read only what the task needs
**Start at the router: [`.claude/README.md`](.claude/README.md).** These are ordinary links, not imports.

| Task | Read |
|---|---|
| Which document wins a disagreement | *How this project is governed*, below |
| Change the data subset, splits or candidates | [router → Data](.claude/README.md), [domain](.claude/reference/domain.md), `Gauntlet AI/docs/planning/tariff-data-training.md` |
| Change the behavior spec or an eval | `Gauntlet AI/docs/planning/tariff-behavior-and-evals.md`, [router → Evals](.claude/README.md) |
| Start or resume work | [`.claude/state/resume.md`](.claude/state/resume.md), then [`PROJECT-CHECKLIST.md`](PROJECT-CHECKLIST.md) |

## How this project is governed
Entry points **route**, rules **prohibit**, references **explain**, canonical documents **prove**.

| Concern | Owner |
|---|---|
| Where anything is, what to load | [router](.claude/README.md) |
| How to keep context true while working | [maintenance rule](.claude/rules/context-maintenance.md) — read on any task that moves code or an owner |
| Context-system maturity | [ICM progress checklist](.claude/state/icm-progress.md) |
| Requirements / decisions | Gauntlet brief `Gauntlet AI/course-material/2026-10-27-week7-train-your-own-slm-brief.md`, then `Gauntlet AI/docs/planning/tariff-project-prd.md` |
| Stage and gates | [`PROJECT-CHECKLIST.md`](PROJECT-CHECKLIST.md); submission items in [`SUBMISSION.md`](SUBMISSION.md) |
| Where we left off | [`.claude/state/resume.md`](.claude/state/resume.md) |
| Run history | [dev log](docs/devlog/) |
| Which document wins a disagreement | 1. Gauntlet brief · 2. Innocent's decisions in the PRD · 3. planning docs · 4. this repo's docs |

## Commands
- `uv run python -I scripts/<script>.py --help` — every script documents its inputs.
- `python3 ~/.claude/skills/icm-project/scripts/check_context.py .` — context shape check (proves navigability only).
