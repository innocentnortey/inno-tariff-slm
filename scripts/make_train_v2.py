"""Build the v2 training file: v1 training items plus attribute-ablated NEED_INFO copies (the v2 data change).

Usage:
  uv run python -I scripts/make_train_v2.py --in data/processed/train.jsonl --out data/processed/train_v2.jsonl \
      --share 0.25 --seed 2026

Why: the first full run chose a code on 39% of dev items where it should have asked (NEED_INFO recall 0.61); only 6%
of v1 training items are NEED_INFO, and the ablated copies used in dev and test were never made for training. v2 adds
copies of a share of decidable items with the deciding attribute removed, built the same way as the dev/test copies
(`attributes.strip_dimension`, rejected when a cut shows or the attribute is still stated). v1 items are copied
unchanged, so v1 and v2 differ only in the added examples; dev and test are untouched.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tariff_slm.data.attributes import evidence, strip_dimension  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--share", type=float, default=0.25)
    ap.add_argument("--seed", type=int, default=2026)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    items = [json.loads(l) for l in open(a.src, encoding="utf-8")]
    added, stats = [], Counter()
    for it in items:
        if it["kind"] != "decide" or it["sibling_node"].strip(" :").lower() == "other" or not it["deciding_dimension"]:
            continue
        if rng.random() >= a.share:
            continue
        dim = it["deciding_dimension"]
        stripped = strip_dimension(it["description"], dim)
        if not stripped or evidence(stripped, dim, it["gold_node"], it["sibling_node"]) is not None:
            stats["rejected"] += 1
            continue
        added.append(dict(it, id=it["id"] + "-ablated", kind="need_info_ablated", description=stripped, gold_value=None,
                          expected={"decision": "NEED_INFO", "code": None, "dimension": dim}))
        stats[f"added_{dim}"] += 1
    with open(a.out, "w", encoding="utf-8") as f:
        for it in items + added:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    kinds = Counter(it["kind"] for it in items + added)
    print(json.dumps({"v1_items": len(items), "added": len(added), "v2_items": len(items) + len(added),
                      "kinds": kinds, "need_info_share": round((kinds["need_info_natural"] + kinds["need_info_ablated"])
                                                               / (len(items) + len(added)), 3), **stats}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
