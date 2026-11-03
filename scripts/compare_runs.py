"""Paired comparison of runs on the same items: accuracy, retrieval split, and A-minus-B with a bootstrap interval.

  uv run python -I scripts/compare_runs.py --items data/benchmark/dev.jsonl \
      --run tuned=runs/openset-modal/try1-full-r16-e1/predictions-dev-rag.jsonl \
      --run opus=runs/openset/<run>/predictions.jsonl --run base=... [--pairs tuned:opus tuned:base] [--json out.json]

Each prediction file is one row per item with `id` and the scorer's fields (`acc10`, `acc6`, `valid`, ...).
Every run must cover exactly the item ids in --items.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tariff_slm.openset.scoring import paired, wilson  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--items", required=True)
    ap.add_argument("--run", action="append", required=True, help="name=path/to/predictions.jsonl")
    ap.add_argument("--pairs", nargs="*", default=[], help="a:b pairs to compare (default: first run vs each other)")
    ap.add_argument("--json")
    a = ap.parse_args()
    items = [json.loads(l) for l in open(a.items, encoding="utf-8")]
    ids = [it["id"] for it in items]
    retrieved = {it["id"]: it.get("gold_rank") is not None for it in items}
    runs = {}
    for spec in a.run:
        name, path = spec.split("=", 1)
        rows = {r["id"]: r for r in map(json.loads, open(path, encoding="utf-8"))}
        missing = set(ids) - set(rows)
        if missing:
            raise SystemExit(f"{name}: {len(missing)} items missing")
        runs[name] = rows
    out = {"items": a.items, "n": len(ids), "runs": {}, "pairs": {}}
    print(f"{'run':10s} {'exact10':>16s} {'95% CI':>15s} {'acc8':>6s} {'acc6':>6s} {'valid':>6s} {'ret':>6s} {'not ret':>8s}")
    for name, rows in runs.items():
        k = sum(rows[i]["acc10"] for i in ids)
        ret = [rows[i]["acc10"] for i in ids if retrieved[i]]
        nret = [rows[i]["acc10"] for i in ids if not retrieved[i]]
        s = {"acc10": k / len(ids), "acc10_ci95": wilson(k, len(ids)),
             "acc8": sum(rows[i]["acc8"] for i in ids) / len(ids), "acc6": sum(rows[i]["acc6"] for i in ids) / len(ids),
             "valid": sum(rows[i]["valid"] for i in ids) / len(ids),
             "acc10_retrieved": sum(ret) / len(ret) if ret else None,
             "acc10_not_retrieved": sum(nret) / len(nret) if nret else None}
        out["runs"][name] = s
        print(f"{name:10s} {k:5d} ({s['acc10']:.1%}) {str(s['acc10_ci95']):>15s} {s['acc8']:6.1%} {s['acc6']:6.1%} "
              f"{s['valid']:6.1%} {s['acc10_retrieved'] or 0:6.1%} {s['acc10_not_retrieved'] or 0:8.1%}")
    names = list(runs)
    pairs = [p.split(":") for p in a.pairs] or [[names[0], n] for n in names[1:]]
    for x, y in pairs:
        r = paired([bool(runs[x][i]["acc10"]) for i in ids], [bool(runs[y][i]["acc10"]) for i in ids])
        out["pairs"][f"{x}-{y}"] = r
        print(f"{x} - {y}: {r['diff']:+.1%}  95% CI [{r['ci95'][0]:+.1%}, {r['ci95'][1]:+.1%}]  "
              f"only {x} {r['only_a']}, only {y} {r['only_b']}, McNemar p={r['mcnemar_p']}")
    if a.json:
        json.dump(out, open(a.json, "w"), indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
