# Router — inno-tariff-slm

Common context for every task: [maintenance rule](rules/context-maintenance.md) · [ICM progress checklist](state/icm-progress.md) · [domain reference](reference/domain.md) · [dev log](../docs/devlog/). Paths marked *(planned)* do not exist yet.

| Request | Area · locations | Read first | Done when |
|---|---|---|---|
| Profile or re-pull the rulings data | Data · `data/raw/` (git-ignored); profile numbers in `docs/data/README.md` | [domain](reference/domain.md), `Gauntlet AI/docs/planning/tariff-data-training.md` §Sources | Profile numbers written to `docs/data/README.md` with the run date |
| Change the subset, splits or candidate sets | Data · `src/tariff_slm/data/`, `scripts/build_dataset.py` (draft, paused), `data/processed/` (git-ignored) | `tariff-data-training.md` §Subset, §Splits, §Candidates; rule [retrieval-and-context](rules/retrieval-and-context.md) | Leakage check passes; split counts recorded |
| Change the behavior spec, checks or judge | Evals · `src/tariff_slm/evals/`, `eval.py` (draft, paused, unreviewed) | `Gauntlet AI/docs/planning/tariff-behavior-and-evals.md`; rule [verification-evals-observability](rules/verification-evals-observability.md) | Eval set unchanged or re-versioned in its own commit |
| Run a baseline or the prompt ceiling | Evals · `eval.py --model baseline:<random\|lexical\|rules>`; prompt ceiling via `eval.py --strategy` *(runner planned)* | `tariff-behavior-and-evals.md` §Baselines, §Prompt ceiling | Results table + raw JSONL under `runs/` (git-ignored) and summary in `docs/evals/` |
| Train or sweep dataset sizes | Training · `train/` *(planned)* | `tariff-data-training.md` §QLoRA, §Sweep; rule [build-loop-test-scope](rules/build-loop-test-scope.md) | Checkpoint pushed with commit hash recorded in `SUBMISSION.md` |
| Product, architecture or plan questions | Planning · `Gauntlet AI/docs/planning/tariff-*.md`, `Gauntlet AI/docs/research/tariff-compliance-vision.html` | The one planning doc the question names | Owning doc updated; vision page refreshed if it restates it |

**Do not load:** `data/raw/*.json` whole (290 MB; stream it), the ATLAS paper PDF, or `docs/principles/` unless a rule cites a GP id you need.

**Fallback:** for a task no row covers, open the owning planning doc, settle the meaning (ask Innocent if it is a product choice), then add the row here.
