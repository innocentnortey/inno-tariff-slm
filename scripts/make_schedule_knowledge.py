"""Schedule-knowledge training examples: one per current HTSUS 10-digit line, text -> code (labels from USITC only).

  uv run python -I scripts/make_schedule_knowledge.py --schedule data/raw/hts_current.json \
      --out data/benchmark_try2/schedule_knowledge.jsonl

Each example uses the closed-book prompt (`mode: closed`): the line's full heading-to-line text is the description,
the line's code is the target. It teaches which statistical lines exist under a heading, which the retrieval misses
need (dev: 52 of 76 misses share the gold heading with a candidate).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tariff_slm.data.schedule import load_schedule  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--schedule", default="data/raw/hts_current.json")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sched = load_schedule(a.schedule)
    with open(a.out, "w", encoding="utf-8") as f:
        for code, line in sched.items():
            if code[:2] in ("98", "99"):
                continue
            f.write(json.dumps({"id": f"hts_{code}", "product": "", "description": line.text, "code": code,
                                "mode": "closed", "source": "usitc_schedule"}, ensure_ascii=False) + "\n")
    print(sum(1 for _ in open(a.out)), "examples")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
