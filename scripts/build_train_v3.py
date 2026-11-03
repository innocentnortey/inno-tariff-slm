"""Training set for try 3: try 2's rulings plus backfilled CROSS rulings, with the frozen dev and test sets untouched.

  python -I scripts/build_train_v3.py --backfill data/raw/cross_backfill_all/*.jsonl --out data/benchmark_try3 [--dense]

Backfilled rulings are NY N-series rulings missing from the HF corpus (`scripts/fetch_cross_recent.py --known`). They
pass the same filters as every ruling (`openset.corpus`). Kept for training only when dated on or before 2025-08-01
(before every test ruling), not one of the frozen dev or test items, not a near-copy (TF-IDF cosine >= 0.90) of any
dev or test item, and not in conflict with another training ruling. Every training item gets a temporal retrieval
context: precedents issued before it, drawn from the whole training pool. Dev and test files are read, never written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from build_openset import DEV_END, item, max_sim, norm, pairs_above  # noqa: E402
from tariff_slm.data.schedule import load_schedule  # noqa: E402
from tariff_slm.openset.corpus import load_api, load_hf  # noqa: E402
from tariff_slm.openset.retrieval import CONFIG, Retriever, query_text  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rulings", default=str(ROOT / "data/raw/cross_rulings.json"))
    ap.add_argument("--schedule", default=str(ROOT / "data/raw/hts_current.json"))
    ap.add_argument("--try2-train", default=str(ROOT / "data/benchmark_try2/train.jsonl"))
    ap.add_argument("--frozen", default=str(ROOT / "data/benchmark"), help="dir with frozen dev.jsonl and test.jsonl")
    ap.add_argument("--backfill", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dense", action="store_true")
    ap.add_argument("--atlas-test", default=str(ROOT / "data/raw/atlas/test.jsonl"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sched = load_schedule(a.schedule)
    stats: dict = {"drops_backfill": {}}

    prior_ids = {json.loads(l)["ruling_id"] for l in open(a.try2_train, encoding="utf-8")}
    dev = [json.loads(l) for l in open(Path(a.frozen) / "dev.jsonl", encoding="utf-8")]
    test = [json.loads(l) for l in open(Path(a.frozen) / "test.jsonl", encoding="utf-8")]
    held_ids = {x["ruling_id"] for x in dev + test}
    held_text = [query_text(x["product"], x["description"]) for x in dev + test]

    # The try-2 training pool, as records (re-derived from the HF corpus so every field matches).
    hf = {r.ruling_id: r for r in load_hf(a.rulings, sched, {})}
    pool = [hf[i] for i in prior_ids if i in hf]
    stats["try2_records"] = len(pool)

    back = load_api(a.backfill, sched, stats["drops_backfill"])
    stats["backfill_kept_by_filters"] = len(back)
    back = [r for r in back if r.ruling_id not in prior_ids and r.ruling_id not in held_ids and r.ruling_id not in hf]
    stats["backfill_new_ids"] = len(back)
    back = [r for r in back if r.date <= DEV_END]
    stats["backfill_before_test_period"] = len(back)

    vec = TfidfVectorizer(**CONFIG["vectorizer"]).fit([query_text(r.product, r.description) for r in pool + back]
                                                      + held_text)
    best, _ = max_sim(vec, [query_text(r.product, r.description) for r in back], held_text)
    stats["backfill_dropped_near_copy_of_dev_or_test"] = int((best >= CONFIG["near_duplicate"]).sum())
    back = [r for r, b in zip(back, best) if b < CONFIG["near_duplicate"]]

    # ATLAS test rulings may be among the backfill too: drop any backfilled ruling that shares an ATLAS test item's
    # first 6 digits and resembles it (cosine >= 0.15, the threshold used for the main corpus).
    atlas = []
    for line in open(a.atlas_test, encoding="utf-8"):
        m = json.loads(line)["messages"]
        atlas.append(" ".join(x["content"] for x in m))
    import re as _re
    acodes = [_re.sub(r"\D", "", _re.search(r"HTS US Code ->\s*([\d.]+)", t).group(1))[:6] for t in atlas]
    S = (vec.transform([query_text(r.product, r.description) for r in back]) @ vec.transform(atlas).T).toarray()
    bad = {i for i, r in enumerate(back) for j, c in enumerate(acodes) if r.code[:6] == c and S[i, j] >= 0.15}
    stats["backfill_dropped_atlas_match"] = len(bad)
    back = [r for i, r in enumerate(back) if i not in bad]

    allr = pool + back
    texts = [query_text(r.product, r.description) for r in allr]
    drop, exact = set(), {}
    for i, t in enumerate(texts):
        exact.setdefault(norm(t), []).append(i)
    for idx in exact.values():
        if len({allr[i].code for i in idx}) > 1:
            drop |= set(idx)
        else:
            drop |= set(idx[:-1])
    for i, j in pairs_above(vec, texts, 0.95):
        if allr[i].code != allr[j].code:
            drop |= {i, j}
    n_pool = len(pool)
    stats["dropped_dup_or_conflict"] = {"try2": sum(1 for i in drop if i < n_pool),
                                        "backfill": sum(1 for i in drop if i >= n_pool)}
    allr = [r for i, r in enumerate(allr) if i not in drop]
    stats["train_records"] = len(allr)
    stats["train_records_backfill"] = sum(1 for r in allr if r.ruling_id not in prior_ids)

    embed = None
    if a.dense:
        from sentence_transformers import SentenceTransformer
        st = SentenceTransformer(CONFIG["dense_model"])
        embed = lambda xs: st.encode(xs, batch_size=256, normalize_embeddings=True,  # noqa: E731
                                     show_progress_bar=False, convert_to_numpy=True)
    prec = [{"ruling_id": r.ruling_id, "product": r.product, "description": r.description, "code": r.code,
             "date": r.date} for r in allr]
    ret = Retriever(sched, prec, embed)
    q = [{"ruling_id": r.ruling_id, "product": r.product, "description": r.description, "before": r.date}
         for r in allr]
    rows = [item(r, c, sched) for r, c in zip(allr, ret.batch(q))]
    for r in rows:
        r["is_backfill"] = r["ruling_id"] not in prior_ids
    with open(out / "train.jsonl", "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    stats["recall@20"] = round(sum(1 for r in rows if r["gold_rank"]) / len(rows), 4)
    stats["codes"] = len({r["code"] for r in rows})
    stats["dev_codes_unseen"] = sum(1 for x in dev if x["code"] not in {r["code"] for r in rows})
    json.dump(stats, open(out / "stats.json", "w"), indent=2)
    (out / "SHA256SUMS").write_text(f"{hashlib.sha256((out / 'train.jsonl').read_bytes()).hexdigest()}  train.jsonl\n")
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
