"""Candidate sets: the gold code plus its nearest schedule siblings, and a lexical retriever for recall."""
from __future__ import annotations

import math
import random
import re
from collections import Counter

from .schedule import ScheduleLine

_TOK = re.compile(r"[a-z0-9]+")


def tokens(text: str) -> list[str]:
    return _TOK.findall(text.lower())


def shared_prefix(a: tuple[str, ...], b: tuple[str, ...]) -> int:
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def nearest_siblings(gold: str, sched: dict[str, ScheduleLine], k: int) -> list[str]:
    """Up to k codes closest to gold in the schedule tree: same 8, then 6, then 4 digits, ties by chain prefix."""
    g = sched[gold]
    pool = [c for c in sched if c != gold and c[:4] == gold[:4]]
    pool.sort(key=lambda c: (-(c[:8] == gold[:8]), -(c[:6] == gold[:6]), -shared_prefix(g.chain, sched[c].chain), c))
    return pool[:k]


def candidate_set(gold: str, sched: dict[str, ScheduleLine], k: int, seed: int) -> list[str]:
    """Gold plus k-1 nearest siblings, shuffled with a fixed seed so position never reveals the answer."""
    cands = [gold] + nearest_siblings(gold, sched, k - 1)
    random.Random(seed).shuffle(cands)
    return cands


class BM25:
    """Small BM25 over schedule lines; used only to measure how often realistic retrieval finds the gold code."""

    def __init__(self, docs: dict[str, str], k1: float = 1.2, b: float = 0.75):
        self.ids = list(docs)
        self.tf = [Counter(tokens(docs[i])) for i in self.ids]
        self.len = [sum(t.values()) for t in self.tf]
        self.avg = sum(self.len) / max(len(self.len), 1)
        df: Counter = Counter()
        for t in self.tf:
            df.update(t.keys())
        n = len(self.ids)
        self.idf = {w: math.log(1 + (n - d + 0.5) / (d + 0.5)) for w, d in df.items()}
        self.k1, self.b = k1, b

    def search(self, query: str, top: int) -> list[str]:
        q = [w for w in tokens(query) if w in self.idf]
        scores = []
        for i, tf in enumerate(self.tf):
            s = 0.0
            for w in q:
                f = tf.get(w)
                if f:
                    s += self.idf[w] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * self.len[i] / self.avg))
            scores.append(s)
        order = sorted(range(len(self.ids)), key=lambda i: -scores[i])[:top]
        return [self.ids[i] for i in order]
