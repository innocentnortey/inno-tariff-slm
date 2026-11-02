"""Find the CROSS ruling behind each ATLAS item, so ATLAS test rulings stay out of our training data and indexes.

  uv run --extra bench python -I scripts/match_atlas.py --atlas data/raw/atlas/test.jsonl \
      --rulings data/raw/cross_rulings.json --out data/benchmark/atlas_test_matches.jsonl

ATLAS items carry no ruling number: each is a GPT-4o-mini rewrite (question + code + reasoning) of one ruling. We
compare each item's text with every HF-corpus ruling text by TF-IDF cosine and keep the best match among rulings
whose code shares the item's first 6 digits. A match at cosine >= --threshold is treated as the source ruling; the
next best are recorded too, because a reissued or near-identical ruling must be excluded as well.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def atlas_items(path: str) -> list[dict]:
    out = []
    for i, line in enumerate(open(path, encoding="utf-8")):
        m = json.loads(line)["messages"]
        q = next(x["content"] for x in m if x["role"] == "user")
        a = next(x["content"] for x in m if x["role"] == "assistant")
        code = re.sub(r"\D", "", re.search(r"HTS US Code ->\s*([\d.]+)", a).group(1))
        desc = re.sub(r"^What is the HTS US Code for\s*", "", q).rstrip("?").strip()
        out.append({"atlas_idx": i, "question": q, "description": desc, "code": code, "answer": a})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--atlas", required=True)
    ap.add_argument("--rulings", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--threshold", type=float, default=0.30)
    a = ap.parse_args()
    items = atlas_items(a.atlas)
    rul = json.load(open(a.rulings, encoding="utf-8"))
    texts = [re.sub(r"\s+", " ", r.get("original_ruling_text") or "") for r in rul]
    codes = [re.sub(r"\D", "", r.get("hts_code") or "") for r in rul]
    vec = TfidfVectorizer(sublinear_tf=True, min_df=2, max_df=0.5, ngram_range=(1, 2), stop_words="english")
    X = vec.fit_transform(texts)
    Q = vec.transform([it["description"] + " " + it["answer"] for it in items])
    S = (Q @ X.T).toarray()
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    hits = 0
    with open(a.out, "w", encoding="utf-8") as f:
        for it, row in zip(items, S):
            same = np.array([c[:6] == it["code"][:6] for c in codes])
            order = np.argsort(-row)
            best = [int(j) for j in order[:50] if same[j]][:3]
            top_any = int(order[0])
            m = {"atlas_idx": it["atlas_idx"], "code": it["code"], "description": it["description"],
                 "matches": [{"ruling_id": rul[j]["ruling_id"], "date": rul[j]["date"], "code": codes[j],
                              "cosine": round(float(row[j]), 4)} for j in best],
                 "top_any": {"ruling_id": rul[top_any]["ruling_id"], "code": codes[top_any],
                             "cosine": round(float(row[top_any]), 4)}}
            m["matched"] = bool(best) and bool(row[best[0]] >= a.threshold)
            hits += m["matched"]
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    print(f"{hits}/{len(items)} ATLAS items matched at cosine >= {a.threshold}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
