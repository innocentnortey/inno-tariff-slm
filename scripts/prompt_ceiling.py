"""Prompt-ceiling ablation: frontier models x prompt strategies, scored on the clean and robustness sets.

Usage (on the VPS, where the provider keys live):
  ../bin/with-provider-env -- uv run --extra api python -I scripts/prompt_ceiling.py \
      --models anthropic:claude-opus-5-5 openrouter:openai/gpt-5.6-sol \
      --judge openrouter:google/gemini-3.1-pro-preview --workers 8 [--limit 4]

Runs eval.py once per model x strategy x set, then writes runs/prompt-ceiling-<stamp>/{results.json, report.md}.
Spec adherence = spec pass on the clean dev set (deterministic, and judged); robustness = spec pass on the perturbed
set; consistency = share of perturbed items answered with the same decision and code as their clean source item.
Rerun one sample point with: --models <one> --strategies <one> --limit 30.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_eval(model: str, strategy: str, eval_set: str, tag: str, a) -> Path:
    cmd = [sys.executable, "-I", str(ROOT / "eval.py"), "--model", model, "--eval-set", eval_set,
           "--strategy", strategy, "--workers", str(a.workers), "--effort", a.effort, "--out", str(a.out_dir),
           "--tag", tag]
    if a.judge:
        cmd += ["--judge", a.judge]
    if a.limit:
        cmd += ["--limit", str(a.limit)]
    if a.resume:
        name = model.replace(":", "_").replace("/", "_")
        prev = sorted((Path(a.resume) / "cells").glob(f"*-{name}-{strategy}-{tag}"))
        if prev:
            cmd += ["--resume", str(prev[-1])]
    out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    line = next((l for l in out.stdout.splitlines() if l.startswith("run dir: ")), None)
    if out.returncode or not line:
        raise SystemExit(f"eval failed for {model} {strategy} {tag}:\n{out.stdout[-2000:]}\n{out.stderr[-2000:]}")
    return Path(line.removeprefix("run dir: "))


def load_preds(run: Path) -> dict[str, dict]:
    return {r["id"]: r for r in map(json.loads, open(run / "predictions.jsonl", encoding="utf-8"))}


def answer(r: dict) -> tuple:
    from_raw = r.get("raw") or ""
    sys.path.insert(0, str(ROOT / "src"))
    from tariff_slm.evals.checks import parse
    p = parse(from_raw) or {}
    return (str(p.get("decision", "")).upper(), p.get("code"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--strategies", nargs="+", default=["zero_shot", "few_shot", "cot"])
    ap.add_argument("--clean", default="data/processed/dev.jsonl")
    ap.add_argument("--robust", default="data/processed/dev_robust.jsonl")
    ap.add_argument("--judge")
    ap.add_argument("--effort", default="high")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--parallel-cells", type=int, default=6, help="model x strategy cells run at once")
    ap.add_argument("--resume", help="earlier report dir; each cell retries only the items that hit an API error")
    a = ap.parse_args()
    stamp = time.strftime("%Y%m%d-%H%M%S")
    report_dir = ROOT / "runs" / f"prompt-ceiling-{stamp}"
    a.out_dir = report_dir / "cells"
    report_dir.mkdir(parents=True, exist_ok=True)

    def cell(model: str, strategy: str) -> dict:
        clean_run = run_eval(model, strategy, a.clean, "clean", a)
        robust_run = run_eval(model, strategy, a.robust, "robust", a)
        cs = json.load(open(clean_run / "summary.json"))
        rs = json.load(open(robust_run / "summary.json"))
        clean_p, robust_p = load_preds(clean_run), load_preds(robust_run)
        robust_items = [json.loads(l) for l in open(ROOT / a.robust, encoding="utf-8")]
        if a.limit:
            robust_items = robust_items[: a.limit]
        same, n, by_pert = 0, 0, defaultdict(lambda: [0, 0])
        for it in robust_items:
            src = clean_p.get(it["source_id"])
            rob = robust_p.get(it["id"])
            if rob:
                by_pert[it["perturbation"]][0] += bool(rob["spec_pass"])
                by_pert[it["perturbation"]][1] += 1
            if src and rob:
                n += 1
                same += answer(src) == answer(rob)
        r = {
            "model": model, "strategy": strategy, "prompt_version": cs.get("prompt_version"),
            "n_clean": cs["n"], "n_robust": rs["n"],
            "spec_adherence": cs["spec_pass"], "spec_adherence_judged": cs.get("spec_pass_judged"),
            "robustness": rs["spec_pass"], "robustness_judged": rs.get("spec_pass_judged"),
            "consistency": round(same / n, 3) if n else None, "n_consistency_pairs": n,
            "robustness_by_perturbation": {k: round(v[0] / v[1], 3) for k, v in by_pert.items() if v[1]},
            "code_exact10": cs["code_exact10_on_select"], "need_info_recall": cs["need_info_recall"],
            "over_asking": cs["over_asking_rate"], "false_confidence": cs["false_confidence_rate"],
            "value_grounded": cs["value_grounded"], "dimension_correct": cs["dimension_correct"],
            "judge_agrees": cs.get("judge_agrees_on_decide_selects"),
            "judge_errors": (cs.get("judge_errors") or 0) + (rs.get("judge_errors") or 0),
            "api_errors": cs["api_errors"] + rs["api_errors"], "refusals": cs["refusals"] + rs["refusals"],
            "cost_usd": round((cs["cost_usd"] or 0) + (rs["cost_usd"] or 0), 3),
            "judge_cost_usd": round(cs["judge_cost_usd"] + rs["judge_cost_usd"], 3),
            "runs": [str(clean_run.relative_to(ROOT)), str(robust_run.relative_to(ROOT))],
        }
        print(json.dumps(r), flush=True)
        return r

    # Cells are independent, so they run at once (each still sends --workers calls in parallel); results keep the
    # model x strategy order.
    combos = [(m, s) for m in a.models for s in a.strategies]
    with ThreadPoolExecutor(max_workers=max(1, a.parallel_cells)) as ex:
        results = list(ex.map(lambda c: cell(*c), combos))

    json.dump({"args": {k: v for k, v in vars(a).items() if k != "out_dir"}, "results": results},
              open(report_dir / "results.json", "w"), indent=1)
    lines = ["| Model | Strategy | Spec adherence (judged) | Robustness (judged) | Consistency | 10-digit exact | "
             "NEED_INFO recall | Over-asking | Cost USD |", "|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['model']} | {r['strategy']} | {r['spec_adherence']} ({r['spec_adherence_judged']}) | "
                     f"{r['robustness']} ({r['robustness_judged']}) | {r['consistency']} | {r['code_exact10']} | "
                     f"{r['need_info_recall']} | {r['over_asking']} | {r['cost_usd'] + r['judge_cost_usd']:.2f} |")
    (report_dir / "report.md").write_text("# Prompt-ceiling ablation\n\n" + "\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"report dir: {report_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
