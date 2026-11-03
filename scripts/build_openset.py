"""Build benchmark v2 (open-set 10-digit classification): cleaned corpus, date splits, retrieval contexts.

  uv run --extra bench python -I scripts/build_openset.py --out data/benchmark \
      [--api data/raw/cross_recent/rulings.jsonl data/raw/cross_recent_b/rulings.jsonl ...] [--test-n 500]

Splits by ruling date: train <= 2023-12-31; dev pool 2024-01-01 .. 2025-08-01 (HF corpus); test = rulings fetched
from CROSS after the corpus ended (never seen by earlier work). Eval items whose description is a near-duplicate of
an earlier ruling are dropped; training items with conflicting labels for the same text are dropped; ATLAS test
rulings (and their likely matches) are dropped from train and from every index. Retrieval for an item only sees
rulings dated before its split (train items: every other train ruling, leave-one-out).

Writes: train.jsonl (training items with contexts), dev.jsonl (eval sample), dev_pool_records.jsonl, test.jsonl
(when API files are given), atlas_test.jsonl (ATLAS track, closed-book), stats.json, SHA256SUMS.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tariff_slm.data.schedule import load_schedule  # noqa: E402
from tariff_slm.openset.corpus import load_api, load_hf  # noqa: E402
from tariff_slm.openset.retrieval import CONFIG, Retriever, query_text  # noqa: E402

TRAIN_END, DEV_END = "2023-12-31", "2025-08-01"


def norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def max_sim(vec, A: list[str], B: list[str], chunk: int = 1000) -> tuple[np.ndarray, np.ndarray]:
    """For each text in A, the highest cosine against any text in B, and its index."""
    XA, XB = vec.transform(A), vec.transform(B)
    best, arg = np.zeros(len(A)), np.zeros(len(A), dtype=int)
    for s in range(0, len(A), chunk):
        S = (XA[s:s + chunk] @ XB.T).toarray()
        best[s:s + chunk], arg[s:s + chunk] = S.max(axis=1), S.argmax(axis=1)
    return best, arg


def pairs_above(vec, A: list[str], t: float, chunk: int = 1000):
    X = vec.transform(A)
    for s in range(0, len(A), chunk):
        S = (X[s:s + chunk] @ X.T).tocoo()
        for i, j, v in zip(S.row, S.col, S.data):
            if v >= t and s + i < j:
                yield s + i, j


def item(rec, ctx, sched) -> dict:
    d = asdict(rec)
    d["id"] = rec.ruling_id.replace(" ", "_")
    d["candidates"] = [{"code": c, "text": sched[c].text} for c in ctx.candidates]
    d["precedents"] = ctx.precedents
    d["gold_rank"] = ctx.candidates.index(rec.code) + 1 if rec.code in ctx.candidates else None
    d["gold_in_precedents"] = rec.code in ctx.precedent_codes
    return d


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rulings", default="data/raw/cross_rulings.json")
    ap.add_argument("--schedule", default="data/raw/hts_current.json")
    ap.add_argument("--api", nargs="*", default=[])
    ap.add_argument("--atlas-test", default="data/raw/atlas/test.jsonl")
    ap.add_argument("--atlas-matches", default="data/benchmark/atlas_test_matches.jsonl")
    ap.add_argument("--atlas-min-cos", type=float, default=0.15)
    ap.add_argument("--out", default="data/benchmark")
    ap.add_argument("--dev-n", type=int, default=300)
    ap.add_argument("--test-n", type=int, default=500)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--dense", action="store_true", help="fuse dense embeddings (CONFIG['dense_model']) with TF-IDF")
    ap.add_argument("--temporal-train", action="store_true",
                    help="training items see only precedents issued before them (the condition test items face)")
    ap.add_argument("--train-add-dev-pool", action="store_true",
                    help="also train on dev-pool rulings, minus the dev eval items and their near-duplicates")
    a = ap.parse_args()
    embed = None
    if a.dense:
        from sentence_transformers import SentenceTransformer
        st = SentenceTransformer(CONFIG["dense_model"])
        embed = lambda xs: st.encode(xs, batch_size=256, normalize_embeddings=True,  # noqa: E731
                                     show_progress_bar=False, convert_to_numpy=True)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sched = load_schedule(a.schedule)
    stats: dict = {"config": {k: v for k, v in CONFIG.items() if k != "vectorizer"}, "dense": a.dense,
                   "drops_hf": {}, "drops_api": {}}

    hf = load_hf(a.rulings, sched, stats["drops_hf"])
    api = load_api(a.api, sched, stats["drops_api"])
    hf_ids = {r.ruling_id for r in hf}
    api = [r for r in api if r.ruling_id not in hf_ids and r.date > DEV_END]
    stats["kept_hf"], stats["kept_api"] = len(hf), len(api)

    # ATLAS test rulings and their likely matches never enter train, dev or any index.
    atlas_ids = set()
    for line in open(a.atlas_matches, encoding="utf-8"):
        m = json.loads(line)
        atlas_ids |= {x["ruling_id"] for x in m["matches"] if x["cosine"] >= a.atlas_min_cos}
    before = len(hf)
    hf = [r for r in hf if r.ruling_id not in atlas_ids]
    stats["atlas_excluded"] = before - len(hf)

    train = sorted([r for r in hf if r.date <= TRAIN_END], key=lambda r: r.date)
    dev_pool = sorted([r for r in hf if TRAIN_END < r.date <= DEV_END], key=lambda r: r.date)

    # Training text conflicts: identical or near-identical descriptions with different codes are dropped; identical
    # descriptions with the same code keep the latest ruling only.
    vec = TfidfVectorizer(**CONFIG["vectorizer"]).fit([query_text(r.product, r.description) for r in hf + api])
    texts = [query_text(r.product, r.description) for r in train]
    drop, exact = set(), {}
    for i, r in enumerate(train):
        exact.setdefault(norm(texts[i]), []).append(i)
    for idx in exact.values():
        if len({train[i].code for i in idx}) > 1:
            drop |= set(idx)
        else:
            drop |= set(idx[:-1])
    n_exact = len(drop)
    conflict_pairs = 0
    for i, j in pairs_above(vec, texts, 0.95):
        if train[i].code != train[j].code:
            drop |= {i, j}
            conflict_pairs += 1
    stats["train_dropped_exact_dup_or_conflict"] = n_exact
    stats["train_near_dup_conflict_pairs"] = conflict_pairs
    train = [r for i, r in enumerate(train) if i not in drop]
    stats["train_records"] = len(train)

    def dedupe_eval(cands, earlier, name):
        ct = [query_text(r.product, r.description) for r in cands]
        best, _ = max_sim(vec, ct, [query_text(r.product, r.description) for r in earlier])
        keep = [r for r, b in zip(cands, best) if b < CONFIG["near_duplicate"]]
        stats[f"{name}_dropped_near_dup_of_earlier"] = len(cands) - len(keep)
        kt = [query_text(r.product, r.description) for r in keep]
        within = {j for _, j in pairs_above(vec, kt, CONFIG["near_duplicate"])}
        stats[f"{name}_dropped_near_dup_within"] = len(within)
        return [r for i, r in enumerate(keep) if i not in within]

    rng = random.Random(a.seed)
    dev_clean = dedupe_eval(dev_pool, train, "dev")
    dev = sorted(rng.sample(dev_clean, min(a.dev_n, len(dev_clean))), key=lambda r: r.ruling_id)
    stats["dev_pool_records"], stats["dev_clean"], stats["dev_items"] = len(dev_pool), len(dev_clean), len(dev)

    as_prec = lambda rs: [{"ruling_id": r.ruling_id, "product": r.product, "description": r.description,  # noqa: E731
                           "code": r.code, "date": r.date} for r in rs]
    files: dict[str, list[dict]] = {}

    r_train = Retriever(sched, as_prec(train), embed)
    q = lambda rs: [{"ruling_id": r.ruling_id, "product": r.product, "description": r.description} for r in rs]  # noqa: E731
    files["dev.jsonl"] = [item(r, c, sched) for r, c in zip(dev, r_train.batch(q(dev)))]
    train_items = train
    if a.train_add_dev_pool:
        dev_ids = {r.ruling_id for r in dev}
        extra = [r for r in dev_pool if r.ruling_id not in dev_ids]
        best, _ = max_sim(vec, [query_text(r.product, r.description) for r in extra],
                          [query_text(r.product, r.description) for r in dev])
        extra = [r for r, b in zip(extra, best) if b < CONFIG["near_duplicate"]]
        stats["train_added_from_dev_pool"] = len(extra)
        train_items = train + extra
        r_tr = Retriever(sched, as_prec(train + extra), embed)
    else:
        r_tr = r_train
    tq = q(train_items)
    if a.temporal_train:
        for d, r in zip(tq, train_items):
            d["before"] = r.date
    files["train.jsonl"] = [item(r, c, sched) for r, c in zip(train_items, r_tr.batch(tq))]
    files["dev_pool_records.jsonl"] = [asdict(r) for r in dev_pool]

    if api:
        test_clean = dedupe_eval(sorted(api, key=lambda r: r.date), train + dev_pool, "test")
        test = sorted(random.Random(a.seed + 1).sample(test_clean, min(a.test_n, len(test_clean))),
                      key=lambda r: r.ruling_id)
        stats["test_clean"], stats["test_items"] = len(test_clean), len(test)
        stats["test_date_range"] = [min(r.date for r in test), max(r.date for r in test)]
        r_full = Retriever(sched, as_prec(train + dev_pool), embed)
        files["test.jsonl"] = [item(r, c, sched) for r, c in zip(test, r_full.batch(q(test)))]
        files["test_pool_records.jsonl"] = [asdict(r) for r in test_clean]

    atlas = []
    for i, line in enumerate(open(a.atlas_test, encoding="utf-8")):
        msgs = json.loads(line)["messages"]
        qtext = next(x["content"] for x in msgs if x["role"] == "user")
        ans = next(x["content"] for x in msgs if x["role"] == "assistant")
        code = re.sub(r"\D", "", re.search(r"HTS US Code ->\s*([\d.]+)", ans).group(1))
        atlas.append({"id": f"atlas_{i:03d}", "question": qtext, "code": code, "code_in_current_hts": code in sched})
    files["atlas_test.jsonl"] = atlas
    stats["atlas_items"] = len(atlas)
    stats["atlas_codes_in_current_hts"] = sum(x["code_in_current_hts"] for x in atlas)

    for name, rows in files.items():
        with open(out / name, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    for name in ("dev.jsonl", "train.jsonl", "test.jsonl"):
        if name in files:
            rows = files[name]
            stats[f"{name}_retrieval"] = {
                f"recall@{k}": round(sum(1 for r in rows if r["gold_rank"] and r["gold_rank"] <= k) / len(rows), 4)
                for k in (1, 5, 10, 20)} | {"gold_in_precedent_codes": round(
                    sum(r["gold_in_precedents"] for r in rows) / len(rows), 4)}
    json.dump(stats, open(out / "stats.json", "w"), indent=2)
    with open(out / "SHA256SUMS", "w") as f:
        for name in sorted(files):
            f.write(f"{hashlib.sha256((out / name).read_bytes()).hexdigest()}  {name}\n")
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
