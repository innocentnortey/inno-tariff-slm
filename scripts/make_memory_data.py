"""Schedule-memory drills for the follow-up experiment: every HTSUS line several ways, plus rulings closed-book.

  uv run python -I scripts/make_memory_data.py --train data/benchmark_try3/train_mix.jsonl \
      --rulings data/benchmark_try3/train.jsonl --out data/benchmark_try3/memory_mix.jsonl [--passes 2 --replay 8000]

Formats (labels from the USITC schedule or CBP rulings only): line text -> code (closed prompt); code -> line text
(qa); "list the statistical lines under subheading X" (qa); each training ruling's facts -> code (closed prompt).
`--passes` copies of the drills are shuffled with `--replay` retrieval-format rows from try 3's mix (code-only and
rationale rows as they are), so the model keeps its evidence-reading skill. Dev and test rulings never appear.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tariff_slm.data.schedule import load_schedule  # noqa: E402
from tariff_slm.openset.prompts import dotted  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--schedule", default="data/raw/hts_current.json")
    ap.add_argument("--rulings", required=True, help="try-3 training rulings (frozen dev/test already excluded)")
    ap.add_argument("--train", required=True, help="try-3 mix, for retrieval-format replay")
    ap.add_argument("--out", required=True)
    ap.add_argument("--passes", type=int, default=2)
    ap.add_argument("--replay", type=int, default=8000)
    ap.add_argument("--seed", type=int, default=41)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    sched = {c: l for c, l in load_schedule(a.schedule).items() if c[:2] not in ("98", "99")}
    drills = []
    for c, line in sched.items():
        drills.append({"id": f"mem_t2c_{c}", "product": "", "description": line.text, "code": c, "mode": "closed"})
        drills.append({"id": f"mem_c2t_{c}", "mode": "qa", "code": c,
                       "question": f"What does HTSUS statistical reporting number {dotted(c)} cover?",
                       "target_text": line.text})
    by6 = defaultdict(list)
    for c in sched:
        by6[c[:6]].append(c)
    for sub, codes in by6.items():
        lines = "\n".join(f"{dotted(c)}: {sched[c].chain[-1]}" for c in sorted(codes))
        drills.append({"id": f"mem_list_{sub}", "mode": "qa", "code": codes[0],
                       "question": f"List every 10-digit statistical line under HTSUS subheading {sub[:4]}.{sub[4:]}.",
                       "target_text": lines})
    for line in open(a.rulings, encoding="utf-8"):
        r = json.loads(line)
        drills.append({"id": f"mem_rul_{r['id']}", "product": r["product"], "description": r["description"],
                       "code": r["code"], "mode": "closed"})
    mix = [json.loads(l) for l in open(a.train, encoding="utf-8")]
    replay = rng.sample(mix, min(a.replay, len(mix)))
    rows = [dict(d, sft_kind="memory") for _ in range(a.passes) for d in drills] + \
           [dict(r, sft_kind="replay_" + r.get("sft_kind", "")) for r in replay]
    rng.shuffle(rows)
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    stats = {"drills_per_pass": len(drills), "passes": a.passes, "replay_rows": len(replay), "rows": len(rows),
             "sha256": hashlib.sha256(Path(a.out).read_bytes()).hexdigest()}
    json.dump(stats, open(Path(a.out).with_suffix(".stats.json"), "w"), indent=2)
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
