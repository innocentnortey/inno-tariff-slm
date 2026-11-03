"""One-off retrieval probe on Modal: does adding dense embeddings (bge) to TF-IDF raise recall of the gold code?

  modal run train/modal_retrieval_probe.py

Scores 800 dev-pool rulings that are not in the dev eval sample, so dev itself is never used to tune retrieval.
"""
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parents[1]
app = modal.App("tariff-slm-retrieval-probe")
image = (modal.Image.debian_slim(python_version="3.12")
         .pip_install("torch==2.9.0", "sentence-transformers==5.1.2", "scikit-learn")
         .add_local_dir(ROOT / "src", "/root/src")
         .add_local_file(ROOT / "data/benchmark/train.jsonl", "/root/data/train.jsonl")
         .add_local_file(ROOT / "data/benchmark/dev.jsonl", "/root/data/dev.jsonl")
         .add_local_file(ROOT / "data/benchmark/dev_pool_records.jsonl", "/root/data/dev_pool_records.jsonl")
         .add_local_file(ROOT / "data/raw/hts_current.json", "/root/hts_current.json"))


@app.function(image=image, gpu="H100", timeout=3600)
def probe(model_name: str) -> list[str]:
    import json, random, sys
    sys.path.insert(0, "/root/src")
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from tariff_slm.data.schedule import load_schedule
    from tariff_slm.openset import retrieval as R
    sched = load_schedule("/root/hts_current.json")
    train = [json.loads(l) for l in open("/root/data/train.jsonl")]
    dev_ids = {json.loads(l)["ruling_id"] for l in open("/root/data/dev.jsonl")}
    pool = [p for p in map(json.loads, open("/root/data/dev_pool_records.jsonl")) if p["ruling_id"] not in dev_ids]
    random.Random(0).shuffle(pool)
    pool = pool[:800]
    prec = [{k: t[k] for k in ("ruling_id", "product", "description", "code")} for t in train]
    m = SentenceTransformer(model_name, device="cuda")
    qt = lambda p: R.query_text(p["product"], p["description"])
    enc = lambda xs: m.encode(xs, batch_size=256, normalize_embeddings=True, show_progress_bar=False)
    codes = list(sched)
    P, S, Q = enc([qt(p) for p in prec]), enc([sched[c].text for c in codes]), enc([qt(p) for p in pool])
    R.CONFIG.update(candidates_shown=60, precedents_scanned=60)
    ctx = R.Retriever(sched, prec).batch([{"ruling_id": p["ruling_id"], "product": p["product"],
                                           "description": p["description"]} for p in pool])
    ps, ss = Q @ P.T, Q @ S.T
    lines = []
    for wd in (0.0, 0.5, 1.0, 2.0, "dense_only"):
        rec = {10: [], 20: [], 40: []}
        for i, p in enumerate(pool):
            score = {}
            if wd != "dense_only":
                for rk, c in enumerate(ctx[i].candidates):
                    score[c] = score.get(c, 0) + 1.0 / (10 + rk)
            w = 1.0 if wd == "dense_only" else wd
            if w:
                for rk, x in enumerate(np.argsort(-ps[i])[:60]):
                    if ps[i][x] >= R.CONFIG["near_duplicate"]:
                        continue
                    c = prec[x]["code"]
                    score[c] = score.get(c, 0) + w / (10 + rk)
                for rk, x in enumerate(np.argsort(-ss[i])[:30]):
                    score[codes[x]] = score.get(codes[x], 0) + w / (10 + rk)
            ranked = sorted(score, key=lambda c: -score[c])
            for k in rec:
                rec[k].append(p["code"] in ranked[:k])
        lines.append(f"{model_name} dense_weight={wd} " + str({k: round(float(np.mean(v)), 3) for k, v in rec.items()}))
    return lines


@app.local_entrypoint()
def main():
    for name in ("BAAI/bge-base-en-v1.5",):
        for line in probe.remote(name):
            print(line)
