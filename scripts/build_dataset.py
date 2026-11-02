"""Build the v0 apparel-and-footwear dataset: subset, time splits, candidate sets, deciding-attribute labels.

Usage:
  uv run python -I scripts/build_dataset.py --rulings data/raw/cross_rulings.json \
      --schedule data/raw/hts_current.json --out data/processed --chapters 61 62 64 --k 8
Writes {train,dev,test}.jsonl and stats.json to --out. Labels come only from the ruling code and the schedule.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tariff_slm.data.attributes import CONFLICT, deciding_dimension, evidence, strip_dimension  # noqa: E402
from tariff_slm.data.candidates import BM25, candidate_set, nearest_siblings  # noqa: E402
from tariff_slm.data.rulings import load_rulings  # noqa: E402
from tariff_slm.data.schedule import load_schedule  # noqa: E402


def split_of(date: str) -> str:
    y = int(date[:4])
    return "train" if y <= 2022 else "dev" if y == 2023 else "test"


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--rulings", required=True)
    ap.add_argument("--schedule", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--chapters", nargs="+", default=["61", "62", "64"])
    ap.add_argument("--k", type=int, default=8, help="candidates per item, gold included")
    ap.add_argument("--ablate-share", type=float, default=0.25, help="share of decidable dev/test items copied as ablated NEED_INFO")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()

    sched = load_schedule(a.schedule)
    rulings, dropped = load_rulings(a.rulings)
    stats: dict = {"schedule_10digit": len(sched), "rulings_loaded": len(rulings), "dropped": dropped}
    sub = [r for r in rulings if r.code10[:2] in a.chapters]
    stats["in_chapters"] = len(sub)
    obsolete = [r for r in sub if r.code10 not in sched]
    sub = [r for r in sub if r.code10 in sched]
    stats["obsolete_code_dropped"] = len(obsolete)

    # Leakage: a description seen in test or dev never appears in train (exact match after normalising).
    by_split: dict[str, list] = {"train": [], "dev": [], "test": []}
    for r in sub:
        by_split[split_of(r.date)].append(r)
    held = {norm(r.description) for s in ("dev", "test") for r in by_split[s]}
    before = len(by_split["train"])
    by_split["train"] = [r for r in by_split["train"] if norm(r.description) not in held]
    stats["train_dropped_as_duplicate_of_heldout"] = before - len(by_split["train"])

    # Realistic retrieval recall: BM25 over the whole subset schedule (not the oracle candidate set).
    docs = {c: line.text for c, line in sched.items() if c[:2] in a.chapters}
    bm = BM25(docs)
    rng = random.Random(a.seed)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    kinds, dims, recall = Counter(), Counter(), {s: Counter() for s in by_split}
    for split, rows in by_split.items():
        items = []
        for i, r in enumerate(rows):
            # A stable seed: Python's hash() of a string changes per process, which reshuffled candidates on every
            # build before 2026-11-01. The frozen eval files predate this fix (checksums in docs/data/README.md).
            cands = candidate_set(r.code10, sched, a.k,
                                  seed=int(hashlib.sha1(f"{a.seed}:{r.ruling_id}".encode()).hexdigest()[:8], 16))
            sib = nearest_siblings(r.code10, sched, 1)
            dim, gnode, snode = deciding_dimension(sched[r.code10].chain, sched[sib[0]].chain) if sib else (None, "", "")
            ev = evidence(r.description, dim, gnode, snode)
            residual = gnode.lower().startswith("other")
            if ev == CONFLICT and not residual:
                # The description points at the sibling line (mixed wearers, or a fiber the gold line excludes).
                kinds["dropped_conflict"] += 1
                continue
            sibling_residual = snode.strip(" :").lower() == "other"
            if dim and not ev and not residual and sibling_residual:
                # The gold line names an attribute, its sibling is "Other", and the description doesn't state it. From
                # the description alone the answer would be "Other", yet CBP chose the attribute line (the ruling
                # stated a fact the summary dropped), so the item can't be labelled consistently. Label review
                # decision 5, 2026-11-01.
                kinds["dropped_absent_vs_residual"] += 1
                continue
            # A residual gold line ("Other") is decided by the absence of the sibling's attribute, so it is never NEED_INFO.
            kind = ("decide_unlabelled" if dim is None else "decide_residual" if residual
                    else "decide" if ev else "need_info_natural")
            base = {
                "id": f"{r.ruling_id.replace(' ', '')}", "ruling_id": r.ruling_id, "date": r.date, "split": split,
                "chapter": r.code10[:2], "description": r.description,
                "candidates": [{"code": sched[c].dotted, "text": sched[c].text, "general_rate": sched[c].general_rate} for c in cands],
                "gold_code": sched[r.code10].dotted, "nearest_sibling": sched[sib[0]].dotted if sib else None,
                "deciding_dimension": dim, "gold_node": gnode, "sibling_node": snode, "kind": kind,
                "gold_value": ev if kind == "decide" else None,
                "expected": {"decision": "NEED_INFO" if kind == "need_info_natural" else "SELECT",
                             "code": None if kind == "need_info_natural" else sched[r.code10].dotted,
                             "dimension": dim},
                "provenance": {"source": "CBP CROSS via HF orlandowhite/hts-cross-rulings", "original_text_sha1": r.source_sha1},
            }
            items.append(base); kinds[kind] += 1; dims[dim] += 1
            if split != "train" and kind == "decide" and not sibling_residual and rng.random() < a.ablate_share:
                stripped = strip_dimension(r.description, dim)
                # Keep the copy only if it reads cleanly and no longer supports either line on this dimension.
                if stripped and evidence(stripped, dim, gnode, snode) is None:
                    ab = dict(base, id=base["id"] + "-ablated", kind="need_info_ablated", description=stripped,
                              gold_value=None, expected={"decision": "NEED_INFO", "code": None, "dimension": dim})
                    items.append(ab); kinds["need_info_ablated"] += 1
                else:
                    kinds["ablation_rejected"] += 1
            if i % 4 == 0 or split != "train":
                top = bm.search(r.description, 50)
                recall[split]["n"] += 1
                for kk in (8, 20, 50):
                    recall[split][f"at{kk}"] += r.code10 in top[:kk]
        with open(out / f"{split}.jsonl", "w", encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
        stats[f"{split}_items"] = len(items)
        stats[f"{split}_kinds"] = dict(Counter(it["kind"] for it in items))
    stats["kinds"] = dict(kinds); stats["dimensions"] = {str(k): v for k, v in dims.most_common()}
    stats["bm25_recall"] = {s: {k: (round(v / c["n"], 3) if k != "n" else v) for k, v in c.items()}
                            for s, c in recall.items() if c["n"]}
    stats["chapters"] = a.chapters; stats["k"] = a.k; stats["seed"] = a.seed
    json.dump(stats, open(out / "stats.json", "w"), indent=1)
    print(json.dumps(stats, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
