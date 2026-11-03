"""Evaluate a model on benchmark v2 (open-set 10-digit classification) or the ATLAS track.

  uv run --extra api --extra bench python -I scripts/eval_openset.py --model anthropic:claude-opus-5-5 \
      --items data/benchmark/dev.jsonl --mode rag [--limit N] [--workers 8] [--effort high] [--tag x] [--resume DIR]

--mode rag (facts + retrieved precedents and HTSUS lines), closed (facts only) or atlas (ATLAS question verbatim).
Writes runs/openset/<stamp>-<model>-<mode>[-tag]/{predictions.jsonl, summary.json}. An API error after retries is
scored as no answer and flagged; --resume reuses the successful rows of an earlier run and retries the rest.
Small local models are evaluated with the same prompts and scorer by train/modal_openset.py.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tariff_slm.data.schedule import load_schedule  # noqa: E402
from tariff_slm.evals import backends  # noqa: E402
from tariff_slm.openset.prompts import PROMPT_VERSION, messages, parse  # noqa: E402
from tariff_slm.openset.scoring import score_row, summarise  # noqa: E402

# USD per million tokens (input, output) for backends that do not return a cost. Claude API list prices, 2026-10.
PRICES = {"anthropic:claude-opus-5-5": (4.0, 20.0), "anthropic:claude-sonnet-5-5": (2.0, 10.0),
          "anthropic:claude-haiku-5-5": (0.10, 0.50)}


def cost(model: str, usage: dict | None) -> float | None:
    if not usage:
        return None
    if usage.get("cost_usd") is not None:
        return float(usage["cost_usd"])
    p = PRICES.get(model)
    if p and usage.get("input_tokens") is not None:
        return (usage["input_tokens"] * p[0] + (usage.get("output_tokens") or 0) * p[1]) / 1e6
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--mode", required=True, choices=["rag", "closed", "atlas"])
    ap.add_argument("--schedule", default=str(ROOT / "data/raw/hts_current.json"))
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--effort", default="high")
    ap.add_argument("--max-cost", type=float, default=30.0, help="stop submitting new items past this many USD")
    ap.add_argument("--tag", default="")
    ap.add_argument("--resume")
    ap.add_argument("--out", default=str(ROOT / "runs/openset"))
    a = ap.parse_args()

    valid = set(load_schedule(a.schedule))
    items = [json.loads(l) for l in open(a.items, encoding="utf-8")][: a.limit or None]
    gen = backends.load(a.model, max_tokens=4000, effort=a.effort)
    prior = {}
    if a.resume:
        prior = {r["id"]: r for r in map(json.loads, open(Path(a.resume) / "predictions.jsonl", encoding="utf-8"))
                 if not r.get("api_error")}
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", a.model)
    run = Path(a.out) / f"{time.strftime('%Y%m%d-%H%M%S')}-{name}-{a.mode}{('-' + a.tag) if a.tag else ''}"
    run.mkdir(parents=True, exist_ok=True)
    spent = [0.0]

    def one(it: dict) -> dict:
        if it["id"] in prior:
            return prior[it["id"]]
        if spent[0] >= a.max_cost:
            raw, err = "__error__: budget stop", True
            usage, lat = None, 0.0
        else:
            t = time.time()
            raw = ""
            for i in range(3):
                try:
                    raw = gen(messages(it, a.mode))
                    break
                except Exception as e:  # noqa: BLE001 - recorded on the row
                    raw = f"__error__: {type(e).__name__}: {str(e)[:200]}"
                    time.sleep(3 * (i + 1))
            err = raw.startswith("__error__")
            usage, lat = backends.last_usage(gen), round(time.time() - t, 2)
        r = score_row(it, parse("" if err else raw), valid)
        c = cost(a.model, usage)
        spent[0] += c or 0.0
        r.update(raw=raw, api_error=err, latency_s=lat, usage=usage, cost_usd=c)
        return r

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
        rows = list(ex.map(one, items))
    with open(run / "predictions.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    s = summarise(rows)
    costs = [r["cost_usd"] for r in rows if r.get("cost_usd") is not None]
    lats = sorted(r["latency_s"] for r in rows if r.get("latency_s"))
    s.update(model=a.model, mode=a.mode, items=a.items, prompt_version=PROMPT_VERSION, effort=a.effort,
             api_errors=sum(r["api_error"] for r in rows), cost_usd=round(sum(costs), 4),
             cost_per_item=round(sum(costs) / len(costs), 5) if costs else None,
             latency_p50_s=lats[len(lats) // 2] if lats else None,
             latency_p90_s=lats[int(len(lats) * 0.9)] if lats else None, wall_s=round(time.time() - t0, 1))
    json.dump(s, open(run / "summary.json", "w"), indent=2)
    print(run)
    print(json.dumps(s, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
