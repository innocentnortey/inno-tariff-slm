# Results and reproduction

HF model: <to be filled>

## Sealed-test and dev results

All values below are deterministic scores, not LLM-judged scores. The small-model arms use Qwen3-1.7B; the frontier reference uses Opus 5.5 structured CoT. Every arm receives the same eight candidates, including the gold code. Retrieval is outside this comparison.

| Split and metric | Base | Tuned v2 | Opus 5.5 CoT |
|---|---:|---:|---:|
| Test spec adherence | 6.3% (14/221) | 78.7% (174/221) | 84.6% (187/221) |
| Test robustness | 10.0% (6/60) | 71.7% (43/60) | 75.0% (45/60) |
| Test exact 10-digit code, items needing a code | 17.0% | 77.7% | 89.1% |
| Test `NEED_INFO` recall | 0% | 86.5% | 73.0% |
| Test over-asking | 0% | 1.6% | 3.3% |
| Dev spec adherence | 3.2% (5/157) | 84.7% (133/157) | 86.0% (135/157) |
| Dev robustness | 0.0% (0/58) | 82.8% (48/58) | 87.9% (51/58) |
| Dev exact 10-digit code, items needing a code | 14.9% | 83.5% | 87.1% |
| Dev `NEED_INFO` recall | 0% | 94.4% | 83.3% |
| Dev over-asking | 0% | 0.7% | 0.0% |

Sources: test rows from [step 10](../evals/step10-head-to-head-2026-11-01.md); dev rows from [base metadata](../../runs/modal/base-eval-v1/meta.json), [v2 metadata](../../runs/modal/full-n6543-v2/meta.json), and [prompt ceiling](../evals/prompt-ceiling-2026-11-01.md). Counts express the reported rates on the recorded denominators.

**v2 did not meet reliability bar B on the sealed test.** It asked correctly on natural `NEED_INFO` items more often than Opus (11/13 versus 6/13), but residual “Other” adherence was lower (74.3% versus 92.9%). Natural missing information often reflects facts omitted by the summary. Sources: [step 10](../evals/step10-head-to-head-2026-11-01.md), [label review](../data/label-review-2026-11-01.md).

## Later dev-only experiments

These runs followed the sealed-test comparison. Each configuration below has a single training seed; the second v2 seed measures repeat-run variation. They do not replace the sealed-test table.

| Run | Clean passes | Robust passes | Source |
|---|---:|---:|---|
| v2, second seed | 127/157 | 48/58 | [meta.json](../../runs/modal/v2-seed8/meta.json) |
| v4 rebalanced | 133/157 | 49/58 | [meta.json](../../runs/modal/v4-rebal/meta.json) |
| v2, two epochs | 135/157 | 49/58 | [meta.json](../../runs/modal/v2-2ep/meta.json) |
| v4 rebalanced, two epochs | 137/157 | 52/58 | [meta.json](../../runs/modal/v4-rebal-2ep/meta.json) |
| Qwen3-4B, v2 data | 138/157 | 50/58 | [meta.json](../../runs/modal/v2-qwen4b/meta.json) |
| Opus dev reference | 135/157 | 51/58 | [prompt ceiling](../evals/prompt-ceiling-2026-11-01.md) |

Only v4 plus two epochs exceeds both reference counts in these runs. The original and second v2 seeds differ by six clean items; this is observed variation, not a confidence interval. The [v4 builder](../../scripts/make_train_v4.py) keeps half of gender-split items and 35% of the knit-to-shape residual family in expectation, repeats rare branches, and keeps missing-information items.

[PENDING: confirmation seed]

[PENDING: test second look]

## Data-efficiency curve

| Training examples | Dev spec adherence | Dev robustness | Dev exact 10-digit | Dev `NEED_INFO` recall | Optimizer steps |
|---:|---:|---:|---:|---:|---:|
| 500 | 30.6% | 17.2% | 47.5% | 0.0% | 32 |
| 1,000 | 45.2% | 37.9% | 60.4% | 0.0% | 63 |
| 2,000 | 61.8% | 46.6% | 72.7% | 0.0% | 125 |
| 4,000 | 76.4% | 77.6% | 74.1% | 94.4% | 250 |
| 6,543 | 84.7% | 82.8% | 83.5% | 94.4% | 409 |

Scores and sizes: [data-efficiency-curve-v2.json](../../runs/modal/data-efficiency-curve-v2.json). Steps: [500](../../runs/modal/curve-v2-n500/meta.json), [1,000](../../runs/modal/curve-v2-n1000/meta.json), [2,000](../../runs/modal/curve-v2-n2000/meta.json), [4,000](../../runs/modal/curve-v2-n4000/meta.json), [full v2](../../runs/modal/full-n6543-v2/meta.json).

These are nested subsets with one epoch held fixed, not equal optimizer steps. The curve is still rising; dataset size and optimization effort are confounded. No tested size clears both Opus dev measures, so a minimum viable size for bar B has not been established. The first tested size with effective asking is 4,000; that is an exploratory milestone, not the reliability threshold.

## Build and train

Run commands from the repository root with the raw inputs present, `uv` installed, and Modal installed and authenticated. Command sources: [dataset builder](../../scripts/build_dataset.py), [v2 builder](../../scripts/make_train_v2.py), [Modal app](../../train/modal_app.py).

The build recipe below writes to a separate directory to preserve the canonical frozen files. A fresh build does **not** reproduce the historical bytes: candidate ordering formerly used process-dependent Python hashes. For the reported runs, use the frozen files in `data/processed` and verify their checksums below. A rebuilt dataset is a new artifact, even when labels and candidate membership agree. [Source: frozen-file record](../data/README.md).

```bash
uv run python -I scripts/build_dataset.py \
  --rulings data/raw/cross_rulings.json \
  --schedule data/raw/hts_current.json \
  --out data/rebuilt --chapters 61 62 64 --k 8

uv run python -I scripts/make_train_v2.py \
  --in data/rebuilt/train.jsonl --out data/rebuilt/train_v2.jsonl \
  --share 0.25 --seed 2026
```

The historical v2 construction command, when starting from the frozen v1 file, is:

```bash
uv run python -I scripts/make_train_v2.py \
  --in data/processed/train.jsonl --out data/processed/train_v2.jsonl \
  --share 0.25 --seed 2026
```

Train on the canonical v2 file; this also evaluates dev and dev robustness:

```bash
modal run train/modal_app.py --mode train --n 0 --train-file train_v2.jsonl
```

The command creates a timestamped run name. Set `RUN_NAME` below to that name, or to `full-n6543-v2` only when the original adapter exists in the connected Modal volume. Run metadata records training settings and package versions; local metadata alone does not contain the adapter.

## Evaluate

The [eval.py docstring](../../eval.py) defines `--model` and `--eval-set`, with optional `--strategy`, `--limit`, `--workers`, `--effort`, and `--judge`. A directly runnable baseline example and the future published-model invocation are:

```bash
uv run python -I eval.py --model baseline:rules --eval-set data/processed/dev.jsonl

# Replace this value after publication.
HF_MODEL='<hf-repo-id>'
uv run python -I eval.py --model "$HF_MODEL" --eval-set data/processed/dev.jsonl
```

Modal evaluates the saved adapter directly; `--adapter base` evaluates the untuned model. Source: [Modal eval entry point](../../train/modal_app.py).

```bash
RUN_NAME='full-n6543-v2'
modal run train/modal_app.py --mode eval --adapter base
modal run train/modal_app.py --mode eval --adapter "$RUN_NAME"

modal run train/modal_app.py --mode eval --adapter base \
  --dev-file test.jsonl --robust-file test_robust.jsonl
modal run train/modal_app.py --mode eval --adapter "$RUN_NAME" \
  --dev-file test.jsonl --robust-file test_robust.jsonl
```

In test-mode metadata, the clean results remain under the key `dev`; `dev_file` identifies the actual split. Any new model evaluated on this already-inspected test set must be reported as a **second look**.

Reproduce one prompt-ceiling sample point, verbatim from the [prompt-ceiling report](../evals/prompt-ceiling-2026-11-01.md):

```bash
../bin/with-provider-env -- uv run --extra api python -I scripts/prompt_ceiling.py \
    --models anthropic:claude-opus-5-5 --strategies cot --judge openrouter:google/gemini-3.1-pro-preview --limit 30
```

This requires the local provider-environment wrapper and API credentials. It is a limited sample point, not the full reported run. Deterministic and judged scores remain separate: the judge has not been calibrated against human labels. [Source: prompt-ceiling report](../evals/prompt-ceiling-2026-11-01.md).

## Frozen file checksums

All paths are relative to `data/processed`. Values are copied from [docs/data/README.md](../data/README.md); v3 is retained as a negative-result artifact, not the selected model's training data.

| File | SHA-256 |
|---|---|
| `dev.jsonl` | `8d88fcd95ced407d228b5eabfce743c5207e72275cf430bfe30ecc970344390a` |
| `test.jsonl` | `f46a27fd28442ecbd92ff84a711d923d99274932914251266b89d4d3b0d848dc` |
| `dev_robust.jsonl` | `901bf7efcf943926bb867048a329a45cbafe7216f6c8385b276df09663d9d390` |
| `train.jsonl` | `bf15cab1505e59f95d92f4a53525cbe4a56973abbc959c19cf4b7ec95883e2e8` |
| `train_v2.jsonl` | `ac8d4f7264c11b9585e44e3c8a1a2a21c474d52cbb27d966ef7fb872c08386f0` |
| `train_v3.jsonl` | `1f2bb5cd19acf277d78cd216d1606d533726de41e97623d183c12eb8f93382d3` |
| `test_robust.jsonl` | `766ab66478deb11b7ba407e8680e115521a57fd130e849b7e93eded31e06d070` |

```bash
shasum -a 256 data/processed/dev.jsonl data/processed/test.jsonl \
  data/processed/dev_robust.jsonl data/processed/train.jsonl \
  data/processed/train_v2.jsonl data/processed/train_v3.jsonl \
  data/processed/test_robust.jsonl
```
