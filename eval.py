"""Score a model (or baseline) on a tariff eval set with deterministic checks and an optional LLM judge.

  uv run python -I eval.py --model <hf-repo-id | mlx:<id> | anthropic:<id> | openrouter:<id> | openai:<id> | baseline:<random|lexical|rules>> \
      --eval-set data/processed/dev.jsonl [--strategy zero_shot|few_shot|cot] [--limit N] [--workers 8] \
      [--effort high] [--judge openrouter:<id>]

Writes runs/<stamp>-<model>-<strategy>/{predictions.jsonl, summary.json[, judge.jsonl]} and prints the summary.

Spec adherence is reported two ways: `spec_pass` (deterministic checks only) and, when a judge is named,
`spec_pass_judged` (a decidable SELECT must also get "yes" to both judge questions: the cited attribute is stated in
the description, and it separates the chosen code from the runner-up).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from tariff_slm.evals import backends  # noqa: E402
from tariff_slm.evals.checks import parse, score, summarise  # noqa: E402
from tariff_slm.evals.judge import judge_messages  # noqa: E402
from tariff_slm.evals.prompts import PROMPT_VERSION, messages  # noqa: E402

# USD per million tokens (input, output) for backends that don't return a cost. Claude API list prices, 2026-10.
PRICES = {"anthropic:claude-opus-5-5": (4.0, 20.0), "anthropic:claude-sonnet-5-5": (2.0, 10.0),
          "anthropic:claude-haiku-5-5": (0.10, 0.50), "anthropic:claude-fable-5-1": (10.0, 50.0)}


def load_items(path: str, limit: int | None) -> list[dict]:
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    return rows[:limit] if limit else rows


def call_cost(model: str, usage: dict | None) -> float | None:
    if not usage:
        return None
    if usage.get("cost_usd") is not None:
        return float(usage["cost_usd"])
    p = PRICES.get(model)
    if p and usage.get("input_tokens") is not None:
        return (usage["input_tokens"] * p[0] + (usage.get("output_tokens") or 0) * p[1]) / 1e6
    return None


def with_retry(fn, tries: int = 3):
    """API errors on one item must not end the run; after the last try the item is scored as an empty answer."""
    for i in range(tries):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 - recorded on the row, never swallowed silently
            if i == tries - 1:
                return f"__error__: {type(e).__name__}: {str(e)[:200]}"
            time.sleep(2 * (i + 1))


def main() -> int:
    ap = argparse.ArgumentParser(description="Tariff specialist evaluation")
    ap.add_argument("--model", required=True)
    ap.add_argument("--eval-set", required=True)
    ap.add_argument("--strategy", default="zero_shot", choices=["zero_shot", "few_shot", "cot"])
    ap.add_argument("--shots", default="data/processed/train.jsonl", help="pool for few-shot examples")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=1, help="parallel API calls")
    ap.add_argument("--effort", default="high", help="reasoning effort for frontier backends")
    ap.add_argument("--judge", help="judge model, e.g. openrouter:google/gemini-3.1-pro-preview (optional)")
    ap.add_argument("--out", default="runs")
    ap.add_argument("--tag", default="", help="suffix for the run directory name")
    ap.add_argument("--resume", help="earlier run dir: reuse its answers and judge verdicts that succeeded, retry "
                                     "only the items that hit an API error")
    a = ap.parse_args()

    items = load_items(a.eval_set, a.limit)
    shots = []
    if a.strategy == "few_shot":
        pool = [json.loads(l) for l in open(a.shots, encoding="utf-8")]
        shots = [next(x for x in pool if x["kind"] == k) for k in ("decide", "need_info_natural", "decide_residual")]
    is_baseline = a.model.startswith("baseline:")
    gen = backends.load(a.model, effort=a.effort)
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", a.model)
    run_dir = Path(a.out) / f"{time.strftime('%Y%m%d-%H%M%S')}-{name}-{a.strategy}{('-' + a.tag) if a.tag else ''}"
    run_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    prior, prior_judge = {}, {}
    if a.resume:
        prior = {r["id"]: r for r in map(json.loads, open(Path(a.resume) / "predictions.jsonl", encoding="utf-8"))
                 if not r.get("api_error")}
        jf = Path(a.resume) / "judge.jsonl"
        if jf.exists():
            prior_judge = {v["id"]: v for v in map(json.loads, open(jf, encoding="utf-8"))
                           if v.get("verdict") and not str(v.get("raw", "")).startswith("__error__")}

    def one(it: dict) -> dict:
        if it["id"] in prior:
            return {k: v for k, v in prior[it["id"]].items() if k not in ("judge_ok", "spec_pass_judged")}
        t = time.time()
        raw = gen(it) if is_baseline else with_retry(lambda: gen(messages(it, a.strategy, shots)))
        r = score(it, raw)
        usage = backends.last_usage(gen)
        r.update(latency_s=round(time.time() - t, 3), usage=usage, cost_usd=call_cost(a.model, usage),
                 api_error=raw.startswith("__error__") if isinstance(raw, str) else False)
        return r

    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
        rows = list(ex.map(one, items))
    with open(run_dir / "predictions.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    judge_cost = 0.0
    if a.judge:
        jgen = backends.load(a.judge, max_tokens=2000, effort="low")

        def judge_one(pair):
            it, r = pair
            ans = parse(r["raw"]) or {}
            if ans.get("decision") != "SELECT":
                return None
            if it["id"] in prior_judge and it["id"] in prior:
                return prior_judge[it["id"]]
            raw = with_retry(lambda: jgen(judge_messages(it, ans)))
            usage = backends.last_usage(jgen)
            return {"id": it["id"], "kind": it["kind"], "judge": a.judge, "verdict": parse(raw) or {},
                    "raw": raw, "cost_usd": call_cost(a.judge, usage)}

        with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
            verdicts = [v for v in ex.map(judge_one, zip(items, rows)) if v]
        with open(run_dir / "judge.jsonl", "w", encoding="utf-8") as f:
            for v in verdicts:
                f.write(json.dumps(v, ensure_ascii=False) + "\n")
        by_id = {v["id"]: v["verdict"] for v in verdicts}
        judge_cost = sum(v["cost_usd"] or 0 for v in verdicts)
        judge_errors = sum(1 for v in verdicts if not v["verdict"])
        for r in rows:
            v = by_id.get(r["id"])
            if r["kind"] == "decide" and r.get("decision") == "SELECT":
                ok = bool(v) and str(v.get("attribute_stated")).lower() == "yes" \
                    and str(v.get("attribute_separates")).lower() == "yes"
                r["judge_ok"] = ok
                r["spec_pass_judged"] = r["spec_pass"] and ok
            else:
                r["spec_pass_judged"] = r["spec_pass"]

    summary = summarise(rows)
    if a.judge:
        jp = [r["spec_pass_judged"] for r in rows]
        summary["spec_pass_judged"] = round(sum(jp) / len(jp), 3) if jp else None
        jok = [r["judge_ok"] for r in rows if "judge_ok" in r]
        summary["judge_agrees_on_decide_selects"] = round(sum(jok) / len(jok), 3) if jok else None
        summary["judge_errors"] = judge_errors
    costs = [r["cost_usd"] for r in rows if r.get("cost_usd") is not None]
    summary.update(model=a.model, strategy=a.strategy, prompt_version=PROMPT_VERSION, effort=a.effort, eval_set=a.eval_set, judge=a.judge,
                   seconds=round(time.time() - t0, 1), resumed_from=a.resume, api_errors=sum(r["api_error"] for r in rows),
                   refusals=sum(1 for r in rows if (r.get("usage") or {}).get("stop_reason") == "refusal"),
                   cost_usd=round(sum(costs), 4) if costs else None, judge_cost_usd=round(judge_cost, 4),
                   output_tokens=sum((r.get("usage") or {}).get("output_tokens") or 0 for r in rows),
                   by_kind={k: summarise([r for r in rows if r["kind"] == k]) for k in sorted({r["kind"] for r in rows})})
    json.dump(summary, open(run_dir / "summary.json", "w"), indent=1)
    if a.judge:   # rewrite predictions with the judged fields
        with open(run_dir / "predictions.jsonl", "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "by_kind"}, indent=1))
    print(f"run dir: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
