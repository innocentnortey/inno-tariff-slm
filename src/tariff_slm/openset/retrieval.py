"""Realistic candidate generation: past rulings (precedents) plus HTSUS line text, fused into one ranked code list.

Nothing here knows the answer. A query is the product name and description. Two TF-IDF indexes answer it:
  * precedents: earlier rulings' product + description -> their codes (the lookup a broker does in CROSS);
  * schedule: every 10-digit line's full description chain (heading > subheading > ... > line).
Codes are fused by reciprocal-rank fusion. Callers pass `exclude` to keep a ruling (and its near-duplicates) out of
its own context, and build the precedent index only from rulings dated before the evaluated period.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from ..data.schedule import ScheduleLine

# Retrieval configuration, in one place (rule retrieval-and-context §5).
CONFIG = {
    "vectorizer": {"sublinear_tf": True, "ngram_range": (1, 2), "min_df": 2, "max_df": 0.4, "stop_words": "english"},
    "precedents_scanned": 30,   # precedent hits used for code voting
    "precedents_shown": 5,      # precedents rendered into the prompt
    "schedule_scanned": 30,     # schedule lines used for fusion
    "candidates_shown": 20,     # codes rendered into the prompt (K)
    "rrf_k": 10,
    "near_duplicate": 0.90,     # TF-IDF cosine at or above which a precedent counts as the same ruling text
    "dense_model": "BAAI/bge-base-en-v1.5",  # optional dense side; chosen on dev-pool recall (+5.2 pts @20)
    "dense_weight": 1.0,
    "dense_precedents": 60,
    "dense_schedule": 30,
}


def query_text(product: str, description: str) -> str:
    return f"{product}. {product}. {description}" if product else description


@dataclass
class Context:
    candidates: list[str]                  # ranked 10-digit codes
    precedents: list[dict]                 # shown precedents: ruling_id, product, description, code, score
    precedent_codes: list[str] = field(default_factory=list)  # all scanned precedent codes, ranked


class Retriever:
    def __init__(self, sched: dict[str, ScheduleLine], precedents: list[dict], embed=None):
        """`precedents`: dicts with ruling_id, product, description, code (the index is built once). `embed`: optional
        callable(list[str]) -> L2-normalised numpy array; when given, dense hits are fused with the TF-IDF ones."""
        self.sched = sched
        self.codes = list(sched)
        self.prec = precedents
        cfg = CONFIG["vectorizer"]
        self.sv = TfidfVectorizer(**cfg).fit([sched[c].text for c in self.codes])
        self.S = self.sv.transform([sched[c].text for c in self.codes])
        self.pv = TfidfVectorizer(**cfg).fit([query_text(p["product"], p["description"]) for p in precedents])
        self.P = self.pv.transform([query_text(p["product"], p["description"]) for p in precedents])
        self.pid = {p["ruling_id"]: i for i, p in enumerate(precedents)}
        self.pdate = np.array([p.get("date", "") for p in precedents])
        self.embed = embed
        if embed is not None:
            self.Pd = embed([query_text(p["product"], p["description"]) for p in precedents])
            self.Sd = embed([sched[c].text for c in self.codes])

    def batch(self, queries: list[dict], exclude: list[set[str]] | None = None, chunk: int = 512) -> list[Context]:
        """`queries`: dicts with product, description (and ruling_id; optional `before`, an ISO date: precedents on or
        after it are hidden). `exclude[i]`: ruling ids hidden from query i."""
        out: list[Context] = []
        k_p, k_s, rrf = CONFIG["precedents_scanned"], CONFIG["schedule_scanned"], CONFIG["rrf_k"]
        for start in range(0, len(queries), chunk):
            qs = queries[start:start + chunk]
            texts = [query_text(q["product"], q["description"]) for q in qs]
            ps = (self.pv.transform(texts) @ self.P.T).toarray()
            ss = (self.sv.transform(texts) @ self.S.T).toarray()
            if self.embed is not None:
                qd = self.embed(texts)
                pds, sds = qd @ self.Pd.T, qd @ self.Sd.T
            for j, q in enumerate(qs):
                i = start + j
                row = ps[j]
                hide = set(exclude[i]) if exclude else set()
                if q.get("ruling_id") in self.pid:
                    hide.add(q["ruling_id"])
                for rid in hide:
                    if rid in self.pid:
                        row[self.pid[rid]] = -1.0
                row[row >= CONFIG["near_duplicate"]] = -1.0
                if q.get("before"):  # temporal: only rulings issued before the query's own date
                    row[self.pdate >= q["before"]] = -1.0
                blocked = row < 0
                top_p = [int(x) for x in np.argsort(-row)[:k_p] if row[x] > 0]
                top_s = [int(x) for x in np.argsort(-ss[j])[:k_s] if ss[j][x] > 0]
                score: dict[str, float] = {}
                seen_codes: list[str] = []
                for r, x in enumerate(top_p):
                    c = self.prec[x]["code"]
                    score[c] = score.get(c, 0.0) + 1.0 / (rrf + r)
                    if c not in seen_codes:
                        seen_codes.append(c)
                for r, x in enumerate(top_s):
                    c = self.codes[x]
                    score[c] = score.get(c, 0.0) + 1.0 / (rrf + r)
                prec_rank = {x: 1.0 / (rrf + r) for r, x in enumerate(top_p)}
                if self.embed is not None:
                    w = CONFIG["dense_weight"]
                    dp = pds[j].copy()
                    dp[blocked] = -1.0
                    top_dp = [int(x) for x in np.argsort(-dp)[:CONFIG["dense_precedents"]]]
                    for r, x in enumerate(top_dp):
                        c = self.prec[x]["code"]
                        score[c] = score.get(c, 0.0) + w / (rrf + r)
                        prec_rank[x] = prec_rank.get(x, 0.0) + w / (rrf + r)
                        if c not in seen_codes:
                            seen_codes.append(c)
                    for r, x in enumerate(np.argsort(-sds[j])[:CONFIG["dense_schedule"]]):
                        c = self.codes[int(x)]
                        score[c] = score.get(c, 0.0) + w / (rrf + r)
                    top_p = sorted(prec_rank, key=lambda x: -prec_rank[x])
                ranked = sorted(score, key=lambda c: -score[c])[:CONFIG["candidates_shown"]]
                shown = [{"ruling_id": self.prec[x]["ruling_id"], "product": self.prec[x]["product"],
                          "description": " ".join(self.prec[x]["description"].split()[:70]),
                          "code": self.prec[x]["code"], "score": round(float(row[x]), 3)}
                         for x in top_p[:CONFIG["precedents_shown"]]]
                out.append(Context(ranked, shown, seen_codes))
        return out
