"""Build the v4 training file: v2 rebalanced toward rare schedule branches (no new or relabelled items).

Usage:
  uv run python -I scripts/make_train_v4.py --in data/processed/train_v2.jsonl --out data/processed/train_v4.jsonl

Why (Codex review, 2026-11-01, verified): 72% of decidable training items are gender splits and 752 of 1,814 residual
items are the knit-to-shape family, while v2's failures sit in rare branches (underwear against tops, sets, suits,
contamination-use apparel). v4 keeps half of the gender-split decidable items and 35% of the knit-to-shape residual
family, repeats every other decidable and residual item twice, and keeps all NEED_INFO items. Labels are unchanged.
"""
from __future__ import annotations

import argparse
import json
import random
from collections import Counter

KEEP_GENDER, KEEP_KNIT_TO_SHAPE, REPEAT_RARE = 0.5, 0.35, 2


def family(it: dict) -> str:
    if it["kind"] == "decide":
        return "decide_gender" if it["deciding_dimension"] == "gender_age" else "decide_rare"
    if it["kind"] == "decide_residual":
        return "residual_knit_to_shape" if "knit to shape" in it["sibling_node"].lower() else "residual_rare"
    return it["kind"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=2028)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    items = [json.loads(l) for l in open(a.src, encoding="utf-8")]
    out, before = [], Counter(family(it) for it in items)
    for it in items:
        f = family(it)
        if f == "decide_gender" and rng.random() >= KEEP_GENDER:
            continue
        if f == "residual_knit_to_shape" and rng.random() >= KEEP_KNIT_TO_SHAPE:
            continue
        copies = REPEAT_RARE if f in ("decide_rare", "residual_rare") else 1
        out += [it] * copies
    rng.shuffle(out)
    with open(a.out, "w", encoding="utf-8") as fh:
        for it in out:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(json.dumps({"v2_items": len(items), "v4_items": len(out), "before": before,
                      "after": Counter(family(it) for it in out)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
