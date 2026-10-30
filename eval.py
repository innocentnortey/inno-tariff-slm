"""Score a model (or baseline) on a tariff eval set with deterministic checks and an optional LLM judge.

  uv run python -I eval.py --model <hf-repo-id | mlx:<id> | anthropic:<id> | openai:<id> | baseline:<random|lexical|rules>> \
      --eval-set data/processed/test.jsonl [--strategy zero_shot|few_shot|cot] [--limit N] [--judge anthropic:<id>]

Writes runs/<stamp>-<model>/{predictions.jsonl, summary.json[, judge.jsonl]} and prints the summary.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from tariff_slm.evals import backends  # noqa: E402
from tariff_slm.evals.checks import parse, score, summarise  # noqa: E402
from tariff_slm.evals.judge import judge_messages  # noqa: E402
from tariff_slm.evals.prompts import messages  # noqa: E402


def load_items(path: str, limit: int | None) -> list[dict]:
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    return rows[:limit] if limit else rows


def main() -> int:
    ap = argparse.ArgumentParser(description="Tariff specialist evaluation")
    ap.add_argument("--model", required=True)
    ap.add_argument("--eval-set", required=True)
    ap.add_argument("--strategy", default="zero_shot", choices=["zero_shot", "few_shot", "cot"])
    ap.add_argument("--shots", default="data/processed/train.jsonl", help="pool for few-shot examples")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--judge", help="judge model, e.g. anthropic:claude-sonnet-5-5 (optional)")
    ap.add_argument("--out", default="runs")
    a = ap.parse_args()

    items = load_items(a.eval_set, a.limit)
    shots = []
    if a.strategy == "few_shot":
        pool = [json.loads(l) for l in open(a.shots, encoding="utf-8")]
        shots = [next(x for x in pool if x["kind"] == k) for k in ("decide", "need_info_natural", "decide_residual")]
    is_baseline = a.model.startswith("baseline:")
    gen = backends.load(a.model)
    run_dir = Path(a.out) / f"{time.strftime('%Y%m%d-%H%M%S')}-{re.sub(r'[^A-Za-z0-9._-]+', '_', a.model)}-{a.strategy}"
    run_dir.mkdir(parents=True, exist_ok=True)
    rows, t0 = [], time.time()
    with open(run_dir / "predictions.jsonl", "w", encoding="utf-8") as f:
        for i, it in enumerate(items):
            t = time.time()
            raw = gen(it) if is_baseline else gen(messages(it, a.strategy, shots))
            r = score(it, raw)
            r["latency_s"] = round(time.time() - t, 3)
            rows.append(r)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            if (i + 1) % 25 == 0:
                print(f"  {i + 1}/{len(items)}", file=sys.stderr)
    summary = summarise(rows)
    summary.update(model=a.model, strategy=a.strategy, eval_set=a.eval_set, seconds=round(time.time() - t0, 1),
                   by_kind={k: summarise([r for r in rows if r["kind"] == k]) for k in sorted({r["kind"] for r in rows})})
    if a.judge:
        jgen = backends.load(a.judge, max_tokens=200)
        with open(run_dir / "judge.jsonl", "w", encoding="utf-8") as f:
            for it, r in zip(items, rows):
                ans = parse(r["raw"]) or {}
                if ans.get("decision") != "SELECT":
                    continue
                verdict = parse(jgen(judge_messages(it, ans))) or {}
                f.write(json.dumps({"id": it["id"], "judge": a.judge, **verdict}) + "\n")
    json.dump(summary, open(run_dir / "summary.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in summary.items() if k != "by_kind"}, indent=1))
    print(f"run dir: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
