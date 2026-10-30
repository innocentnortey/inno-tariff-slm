"""Non-language-model baselines. They answer in the same JSON format the models must produce."""
from __future__ import annotations

import json
import math
import random
import re
from collections import Counter

from ..data.attributes import DIMENSIONS as LEX, describes, dimension_of, stated_value

_TOK = re.compile(r"[a-z0-9]+")


def _toks(t: str) -> list[str]:
    return _TOK.findall(t.lower())


def _answer(dec: str, code: str | None, dim: str | None, val: str | None, runner: str | None) -> str:
    return json.dumps({"decision": dec, "code": code, "deciding_attribute": {"dimension": dim or "other", "value": val},
                       "runner_up": runner})


def _divergence(a: str, b: str) -> tuple[str | None, str]:
    for x, y in zip(a.split(" > "), b.split(" > ")):
        if x != y:
            d = dimension_of(x) if not x.lower().startswith("other") else None
            return d or (dimension_of(y) if not y.lower().startswith("other") else None), x
    return None, ""


def random_baseline(item: dict, seed: int = 0) -> str:
    c = random.Random(f"{seed}-{item['id']}").choice(item["candidates"])["code"]
    return _answer("SELECT", c, None, None, None)


def lexical_baseline(item: dict) -> str:
    """Pick the candidate whose schedule text shares the most IDF-weighted words with the description."""
    docs = {c["code"]: Counter(_toks(c["text"])) for c in item["candidates"]}
    df = Counter(w for d in docs.values() for w in d)
    n = len(docs)
    q = set(_toks(item["description"]))
    score = {k: sum(math.log(1 + n / df[w]) for w in q if w in d) for k, d in docs.items()}
    ranked = sorted(score, key=lambda k: -score[k])
    text = {c["code"]: c["text"] for c in item["candidates"]}
    dim, _ = _divergence(text[ranked[0]], text[ranked[1]])
    return _answer("SELECT", ranked[0], dim, stated_value(item["description"], dim) if dim else None, ranked[1])


def rules_baseline(item: dict) -> str:
    """Attribute rules: reward schedule nodes whose attribute words appear in the description, penalise conflicts.

    Caution: it shares the lexicon used to label deciding dimensions, so its dimension and NEED_INFO scores are
    optimistic. Its code accuracy is fair, because gold codes come from CBP, not the lexicon.
    """
    desc = item["description"].lower()
    def node_score(node: str) -> float:
        if node.lower().startswith("other"):
            return 0.0
        d = dimension_of(node)
        if d is None:
            return 0.0
        words = set(re.findall(LEX[d], node, re.I))
        hit = any(w and w.lower() in desc for w in words if isinstance(w, str))
        return 1.0 if hit else (-1.0 if describes(desc, d) else -0.25)
    score = {c["code"]: sum(node_score(n) for n in c["text"].split(" > ")) for c in item["candidates"]}
    ranked = sorted(score, key=lambda k: -score[k])
    text = {c["code"]: c["text"] for c in item["candidates"]}
    dim, gnode = _divergence(text[ranked[0]], text[ranked[1]])
    if dim and not gnode.lower().startswith("other") and not describes(desc, dim):
        return _answer("NEED_INFO", None, dim, None, None)
    return _answer("SELECT", ranked[0], dim, stated_value(item["description"], dim) if dim else None, ranked[1])


BASELINES = {"random": random_baseline, "lexical": lexical_baseline, "rules": rules_baseline}
