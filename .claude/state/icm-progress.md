# ICM progress checklist
Tracks context-system maturity only; product work and status live in [`PROJECT-CHECKLIST.md`](../../PROJECT-CHECKLIST.md) and [`SUBMISSION.md`](../../SUBMISSION.md).
Update the affected row in the same task as the change, with an evidence link. Made by `icm-project` 1.6.1.
Status: pending (names its unblocking event) · provisional · established · verified · n/a (reason).

| Milestone | Status | Evidence / owner | Next check — enabled by |
|---|---|---|---|
| Work home, sources and owners located | established | [entry](../../CLAUDE.md) governance table; [domain](../reference/domain.md) | Re-check when GitLab `origin` exists |
| Purpose, audience and domain meaning (representative task) | provisional | `Gauntlet AI/docs/planning/tariff-project-prd.md` (draft) | Innocent's Stage 1 sign-off |
| Environment, tools and collaboration | provisional | Mac: `uv`, no model API keys; VPS: keys via `bin/with-provider-env` | First prompt-ceiling run on the VPS |
| Blueprint and first delivery step | provisional | `Gauntlet AI/docs/planning/tariff-architecture.md`, `tariff-execution-plan.md` | §6 design gate |
| Entry → router → maintenance instruction | established | [entry](../../CLAUDE.md), [router](../README.md), [maintenance](../rules/context-maintenance.md) | `check_context.py` after each route change |
| Fresh-context route walkthrough | verified | 2026-10-30: "change the candidate sets" and "run a baseline" both resolve entry → router → planning doc → rule ([dev log](../../docs/devlog/)) | Re-walk when a planned path is created |
| Code design: planned locations | provisional | Router *(planned)* paths; `tariff-architecture.md` §Repo layout | §6 DO-3 code design |
| Physical scaffold | established | `src/tariff_slm/{data,evals}/`, `scripts/build_dataset.py`, `eval.py` exist (draft, uncommitted, paused 2026-10-30) | Innocent un-pauses implementation |
| Routes verified against code and tests | pending | — | First slice with tests (data pipeline) |

Last reconciled: 2026-10-30 — Stage 0 bootstrap; draft data/eval code paused for the concept video.
