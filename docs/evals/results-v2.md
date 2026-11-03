# Results: does domain fine-tuning improve 10-digit tariff classification? (benchmark v2, 2026-11-02)

**Answer.** Yes. On 500 fresh CBP rulings (issued Aug 2025 → Oct 2026) the fine-tuned Qwen3-4B assigns the exact
10-digit code **59.8%** of the time against **42.0%** for the same base model with the same retrieved evidence:
**+17.8 points (95% CI +13.6 to +22.0)**. Both pre-registered criteria are met. The goal set on 2026-11-02, beating
Claude Opus 5.5, is **not** met: Opus scores **71.6%**, **11.8 points** ahead (95% CI 7.6 to 16.0), after the three
allowed training tries.

Protocol: [benchmark-protocol.md](benchmark-protocol.md) (frozen before any tuned model was evaluated). Data:
[benchmark-v2.md](../data/benchmark-v2.md). Plan: [tariff-research-roadmap.md](../planning/tariff-research-roadmap.md).

## Final test (Track B, `rag`, 500 items, evaluated once per arm)

Every arm gets identical messages: CBP's fact sentences, 5 earlier rulings with their codes and 20 HTSUS lines
from the same search. Retrieval found the gold code among the 20 lines for 80.0% of items.

| Arm | Exact 10-digit | 95% CI | 8-digit | 6-digit | Valid code | Gold retrieved / not | Cost per item | Latency |
|---|---|---|---|---|---|---|---|---|
| Retrieval only (top candidate) | 38.0% | 33.9–42.3% | | | 100% | | $0 | |
| Base Qwen3-4B-Instruct-2507 | 42.0% | 37.8–46.4% | 48.4% | 51.4% | 98.4% | 52.5% / 0.0% | ≈ $0.004 (H100) | 3.5 s/item batched (dev run) |
| **Fine-tuned (try 3)** | **59.8%** | 55.4–64.0% | 66.6% | 70.8% | 94.0% | 74.5% / 1.0% | **≈ $0.0002 (H100, batched)** | **0.89 s per request (H100); 0.21 s/item batched** |
| Claude Opus 5.5 (effort high) | **71.6%** | 67.5–75.4% | 77.6% | 83.6% | 93.4% | 82.0% / 30.0% | $0.034 | 9.9 s p50, 16.2 s p90 |

| Criterion (pre-registered) | Result | Verdict |
|---|---|---|
| 1. Tuned − base ≥ 5 points, paired 95% CI excludes 0 | **+17.8** (+13.6 to +22.0); 108 items only tuned right, 19 only base | **Supported** |
| 2. Tuned − retrieval-only, CI excludes 0 | **+21.8** (+17.6 to +26.0) | **Met** |
| Goal (2026-11-02): tuned beats Opus | **−11.8** (−16.0 to −7.6); 31 only tuned, 90 only Opus | **Not met** |

Small-model cost is H100 time at Modal's list price (~$3.95/hour) for batched generation of 16; it excludes idle
capacity and hosting. Opus cost is measured tokens at list price.

## Latency (single requests, measured 2026-11-02)

One classification at a time on a warm GPU, 100 test items (`train/serve_openset.py --action bench`;
`runs/latency/`). End to end includes the live search over 27,841 rulings and the HTSUS. The single-request path
reproduces the evaluation: 66/100 exact on these items, the same as the batched run.

| | Median | p90 | Cost per request (list price) |
|---|---|---|---|
| Fine-tuned 4B on an H100, end to end | **0.89 s** | 0.99 s | ≈ $0.001 |
| Fine-tuned 4B on an A10G (the demo's GPU), end to end | **1.74 s** | 1.89 s | ≈ $0.0005 |
| Claude Opus 5.5 (API, adaptive thinking) | 9.9 s | 16.2 s | $0.034 |
| Base Qwen3-4B, same evidence (it reasons at length before answering) | ≈ 28 s on an A10G (one request) | | |

So the small model answers **about 11× faster than Opus on an H100 and about 6× faster on an A10G**. The earlier
"≈0.2 s per item" figure is batched throughput (16 items at a time), not the wait for one answer.

## Deployment

- **Model:** https://huggingface.co/youngjr1232/tariff-classifier-qwen3-4b (public; commit `4eb6e2029468a5ce8eda708c1664228856c63cd2`), merged bf16 weights of try 3.
- **Dataset:** https://huggingface.co/datasets/youngjr1232/tariff-hts-openset-v2 (public; commit `4797cce5f131cbaea40f76420203f7847bd5f21e`), dev, test, ATLAS split, training files and checksums.
- **Live demo:** https://youngjr1232--tariff-classifier-demo-web.modal.run (Modal, A10G, scales to zero; the first request after idle loads the model in about 3 minutes). It runs the evaluated pipeline (search, then the tuned model) and optionally the base model on the same evidence. Every request needs the demo key (Modal secret `tariff-demo`; a copy is in the Mac Keychain as `tariff-demo-key`).

## Development path (dev, 300 items, `rag`)

| Run | What changed | Exact 10 | Gold not retrieved (76) |
|---|---|---|---|
| Base | — | 42.0% | 0% |
| Try 1 | LoRA on 19,141 rulings, code-only answers | 57.7% | 0% |
| Try 2 | + earlier-only retrieval in training, 1,931 recent rulings, 19,831 HTSUS lines | 59.3% | 2.6% |
| **Try 3 (selected)** | continue try 2 + 6,480 backfilled CROSS rulings + 488 verified rationales | **59.7%** | 5.3% |
| Try 3, forced to reason first | same weights, answer prefilled with `REASONING:` | 48.0% | 1.3% |
| Opus 5.5 | — | 71.3% | 35.5% |

Dev and test agree within half a point for both the tuned model and Opus, so the dev choices carried over.

## Data-efficiency curve (dev, 300 items, `rag`; 2026-11-02)

Same recipe as try 1 (base model, LoRA r=16, lr 2e-4, one epoch), nested subsets of the same shuffled training rulings
(`modal_openset.py --mode train --n N`; each subset is a prefix of the next). Comparison file:
`runs/data-efficiency-curve-v2.json`.

| Training rulings (after length filter) | Optimizer steps | Exact 10-digit | − base (95% CI) | − full 19,141 (95% CI) |
|---|---|---|---|---|
| 0 (base) | 0 | 42.0% | — | — |
| 2,356 | 148 | 52.3% | +10.3 (+5.7 to +15.0) | −5.3 (−9.0 to −2.0) |
| 4,716 | 295 | 53.3% | +11.3 (+6.3 to +16.3) | −4.3 (−7.0 to −1.7) |
| **9,431** | 590 | **56.3%** | +14.3 (+9.3 to +19.3) | **−1.3 (−4.0 to +1.3)** |
| 19,141 (try 1) | 1,197 | 57.7% | +15.7 (+10.7 to +20.3) | — |

**Minimum viable dataset: about 9,400 rulings**, the smallest size whose accuracy is statistically indistinguishable
from the full set. The behavior (beating the base model) already appears at about 2,400 rulings. Gains flatten after
about 10,000; the later tries (2 and 3) added data and recipe changes for +1.6 and +0.4 more points. **Caveat:** epochs
were held fixed, so smaller sets also had fewer optimizer steps; data size and training length are confounded. One seed
per point.

## Closed-book (no retrieval)

| Test | Base | Fine-tuned | Opus 5.5 | ATLAS paper |
|---|---|---|---|---|
| ATLAS test, 200 items, ATLAS's question verbatim | 0.0% | try 2: 0.5%; try 3: 0.0% | **41.0%** | fine-tuned LLaMA-3.3-70B 40.0%; GPT-5-Thinking 25.0% |
| Frozen dev, facts only | — | try 3: 0.0% (6-digit 6.0%) | — | |

Opus 5.5 closed-book matches the paper's fine-tuned 70B model (41.0% vs 40.0%; 6-digit 67.0% vs 57.5%). Our 4B model
cannot recall codes without retrieval: training covered 4,264 codes with a median of two rulings each.

## What improved and what did not

- **Fine-tuning taught judgment over evidence.** Given the same 20 candidate lines, the tuned model picks the right
  one 74.5% of the time against 52.5% for its base.
- **More rulings helped a little; schedule exposure barely.** Try 2's schedule lines and try 3's 6,480 extra rulings
  added about 2 points in total; one or two exposures per code do not make the model remember it.
- **Rationales did not transfer.** 488 Opus rationales (labels from CBP, each passing a Codex judge that rejected all
  50 planted controls) taught the format but not good reasoning: the model never chose to reason on its own, and
  forcing it to dropped dev accuracy by 11.7 points.
- **The remaining gap is memory.** Opus's lead comes mostly from the 20% of items where retrieval missed the code:
  it answers 30.0% of those from knowledge, the tuned model 1.0%. Where the code was retrieved, the gap is 7.5 points.
- **Missing information.** Opus flagged a missing deciding fact on 37.8% of test items; its accuracy on flagged
  items was 60.3% against 78.5% unflagged, so the flag carries real signal. The tuned model never flags: no training
  target contained a flag. This is reported as calibration only (no item was labelled in advance).

## Follow-up outside the three tries: schedule-memory drills (dev only)

Requested by Innocent on 2026-11-02 and designed before any test result existed (`scripts/make_memory_data.py`):
continue try 3 on 154,000 rows: two passes over 73,099 drills (every HTSUS line text → code and code → text, every
subheading's line list, every training ruling closed-book; labels from USITC and CBP only) plus 8,000 retrieval
rows, lr 1e-4, 9,625 steps, 3.4 H100-hours. Judged on dev; not run on the test set.

| Dev, 300 items | Try 3 | Memory follow-up | Opus 5.5 |
|---|---|---|---|
| `rag` exact 10-digit | 59.7% | **60.3%** (+0.7, CI −3.0 to +4.3) | 71.3% |
| `rag` 8-digit / 6-digit | 67.0% / 71.7% | 69.7% / 76.0% | 80.7% / 85.7% |
| `rag` when retrieval missed the code (76) | 5.3% | 10.5% | 35.5% |
| Closed-book exact 10-digit | 0.0% | **45.7%** (6-digit 60.0%) | 44.0% on the earlier 150-item sample (not the same items) |
| ATLAS closed-book exact 10-digit | 0.0% | **12.5%** (6-digit 29.0%) | 41.0% |

**Reading.** The drills gave the small model real recall: closed-book it went from 0% to 45.7% on dev and to 12.5% on
ATLAS, close to Gemini-2.5-Pro-Thinking's 13.5% in the paper. With retrieval it barely changed (+0.7, not
significant), and on retrieval misses it still answers 10.5% against Opus's 35.5%: those items mostly carry codes
seen once or never in training. This is a development result on dev only; the selected checkpoint for the final
test remains try 3. Adapter: Modal volume `tariff-slm:/openset/followup-memory-from-try3/adapter`.

## Deliverables and commands

| Artifact | Location |
|---|---|
| Selected checkpoint (LoRA r=16 on `Qwen/Qwen3-4B-Instruct-2507` @ `cdbee75f`) | `checkpoints/try3-rationales-backfill-cont-b4/` (local, with `SHA256SUMS`; also Modal volume `tariff-slm:/openset/try3-rationales-backfill-cont-b4/adapter`) |
| Frozen dev, test and ATLAS files | `data/benchmark/` (`SHA256SUMS`) |
| Training sets | `data/benchmark/train.jsonl` (try 1), `data/benchmark_try2/`, `data/benchmark_try3/` (`train.jsonl`, `train_mix.jsonl`, stats) |
| Rationales and judge verdicts | `runs/rationales/` |
| Predictions and summaries | `runs/openset-modal/` (small model), `runs/openset/` (Opus); comparison `runs/final-test-comparison.json` |

```bash
# Rebuild the benchmark (Modal H100; dense retrieval); try-2 and try-3 training data
modal run train/modal_build.py
modal run train/modal_build.py --extra "--temporal-train --train-add-dev-pool" --out-name benchmark_try2
modal run train/modal_build.py --v3 --out-name benchmark_try3
uv run python -I scripts/make_train_v3_mix.py --train data/benchmark_try3/train.jsonl \
  --pool data/benchmark_try2/rationale_pool.jsonl \
  --judged runs/rationales/direct1500.judged.jsonl runs/rationales/repair509.judged.jsonl \
  --schedule-knowledge data/benchmark_try2/schedule_knowledge.jsonl --out data/benchmark_try3/train_mix.jsonl

# Train tries 1-3 (detached; checkpoints every 150 steps; a rerun with the same --name resumes)
modal run --detach train/modal_openset.py --mode train --train-file train.jsonl --name try1-full-r16-e1
modal run --detach train/modal_openset.py --mode train --train-file "try2/train.jsonl,try2/schedule_knowledge.jsonl" --name try2-temporal-recent-sched-r16-e1
modal run --detach train/modal_openset.py --mode train --train-file try3/train_mix.jsonl --lr 5e-5 \
  --init-adapter try2-temporal-recent-sched-r16-e1 --batch 4 --grad-accum 4 --max-new 768 --name try3-rationales-backfill-cont-b4

# Evaluate (small model on Modal; Opus via the API on the VPS)
modal run --detach train/modal_openset.py --mode eval --adapter try3-rationales-backfill-cont-b4 --items test.jsonl --prompt-mode rag --max-new 768
../bin/with-provider-env -- uv run --extra api --extra bench python -I scripts/eval_openset.py \
  --model anthropic:claude-opus-5-5 --items data/benchmark/test.jsonl --mode rag --workers 10
uv run python -I scripts/compare_runs.py --items data/benchmark/test.jsonl --run tuned=<pred> --run opus=<pred> --run base=<pred>
```

## Spend

- **Anthropic API (Opus), this reset:** about $90: baselines $21.2 (dev, ATLAS, closed-book, pilot), rationale
  generation and repair $52.0, final test $17.0. Within the limits Innocent approved.
- **Modal:** roughly 17–19 H100-hours, including the 3.4-hour memory follow-up, across builds, tries (including two runs killed by the spend limit and one by
  a network drop) and evaluations; an estimate from run logs, not a bill.
- **Codex judging:** Innocent's Codex subscription; about 2,050 judgments.

## Limits

- **One benchmark, one model family.** 500 test items give a ±4-point interval; the tuned-vs-base gap is far larger
  than that, the tuned-vs-Opus gap too.
- **Single training seed per try.** Run-to-run variation was not measured in this round.
- **The Opus goal was tested at three tries,** plus one follow-up outside them (schedule memory, dev only, above). A
  test number for the follow-up would be a second look at an already-inspected test set.
- **Labels follow the current HTSUS.** Rulings whose codes no longer exist were dropped, not remapped.
