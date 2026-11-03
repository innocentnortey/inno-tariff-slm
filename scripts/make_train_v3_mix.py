"""Assemble try 3's training file: verified rationales, code-only replay, and the new backfilled rulings.

  python -I scripts/make_train_v3_mix.py --train data/benchmark_try3/train.jsonl \
      --pool data/benchmark_try2/rationale_pool.jsonl --judged runs/rationales/*.judged.jsonl \
      --schedule-knowledge data/benchmark_try2/schedule_knowledge.jsonl --out data/benchmark_try3/train_mix.jsonl

Recipe (Codex review, 2026-11-02, plus the backfill): each kept rationale R appears `--passes` times (target
"REASONING: ... CODE: ..."), with `--replay` code-only examples per presentation, 90% rulings / 10% schedule lines;
every backfilled ruling appears once, code-only. A ruling with a kept rationale never also appears code-only. Training
continues try 2's adapter at a lower learning rate (see the roadmap command). The rationale item keeps the exact
context it was written for (the try-2 pool item), so the explanation matches what the model sees.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--train", required=True)
    ap.add_argument("--pool", required=True)
    ap.add_argument("--judged", nargs="+", required=True)
    ap.add_argument("--schedule-knowledge", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--replay", type=int, default=2)
    ap.add_argument("--seed", type=int, default=31)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    pool = {json.loads(l)["id"]: json.loads(l) for l in open(a.pool, encoding="utf-8")}
    kept: dict[str, str] = {}
    for path in a.judged:
        for line in open(path, encoding="utf-8"):
            r = json.loads(line)
            if r.get("keep") and not r.get("control"):
                kept[r["id"]] = r["rationale"]  # a later file (e.g. repairs) may supply an item's rationale
    rationale_items = [pool[i] | {"rationale": t} for i, t in kept.items() if i in pool]
    train = [json.loads(l) for l in open(a.train, encoding="utf-8")]
    rulings = [t for t in train if t["id"] not in kept]
    backfill = [t for t in rulings if t.get("is_backfill")]
    old = [t for t in rulings if not t.get("is_backfill")]
    sched = [json.loads(l) for l in open(a.schedule_knowledge, encoding="utf-8")]
    n_replay = len(rationale_items) * a.passes * a.replay
    n_sched = n_replay // 10
    replay = rng.sample(old, min(len(old), n_replay - n_sched)) + rng.sample(sched, n_sched)
    rows = [dict(x, sft_kind="rationale") for x in rationale_items for _ in range(a.passes)]
    rows += [dict(x, sft_kind="replay") for x in replay] + [dict(x, sft_kind="backfill") for x in backfill]
    rng.shuffle(rows)
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    stats = {"rationales_kept": len(rationale_items), "rationale_presentations": len(rationale_items) * a.passes,
             "replay_rulings": n_replay - n_sched, "replay_schedule": n_sched, "backfill_rulings": len(backfill),
             "rows": len(rows), "retrieval_miss_share_rationales": round(
                 sum(x["gold_rank"] is None for x in rationale_items) / max(1, len(rationale_items)), 3),
             "sha256": hashlib.sha256(Path(a.out).read_bytes()).hexdigest()}
    json.dump(stats, open(Path(a.out).with_suffix(".stats.json"), "w"), indent=2)
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
