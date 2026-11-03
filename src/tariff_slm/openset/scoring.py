"""Scores for benchmark v2: exact 10-digit, hierarchical prefix levels, ATLAS digit average, paired comparisons."""
from __future__ import annotations

import math
import random

LEVELS = (10, 8, 6, 4, 2)


def prefix_digits(pred: str | None, gold: str) -> int:
    """Leading digits that agree (0–10). ATLAS's 'average digits correct' is computed this way here (see protocol)."""
    n = 0
    for a, b in zip(pred or "", gold):
        if a != b:
            break
        n += 1
    return n


def score_row(item: dict, parsed: dict, valid_codes: set[str]) -> dict:
    pred, gold = parsed.get("code"), item["code"]
    p = prefix_digits(pred, gold)
    row = {"id": item["id"], "gold": gold, "pred": pred, "prefix": p, "valid": bool(pred) and pred in valid_codes,
           "missing": parsed.get("missing")}
    for lv in LEVELS:
        row[f"acc{lv}"] = p >= lv and bool(pred) and len(pred) >= lv
    if "gold_rank" in item:
        row["gold_retrieved"] = item["gold_rank"] is not None
    return row


def summarise(rows: list[dict]) -> dict:
    n = len(rows)
    s = {"n": n}
    for lv in LEVELS:
        s[f"acc{lv}"] = round(sum(r[f"acc{lv}"] for r in rows) / n, 4)
    s["avg_prefix_digits"] = round(sum(r["prefix"] for r in rows) / n, 3)
    s["valid_code_rate"] = round(sum(r["valid"] for r in rows) / n, 4)
    s["no_answer"] = sum(1 for r in rows if not r["pred"])
    if rows and "gold_retrieved" in rows[0]:
        hit = [r for r in rows if r["gold_retrieved"]]
        miss = [r for r in rows if not r["gold_retrieved"]]
        s["acc10_when_gold_retrieved"] = round(sum(r["acc10"] for r in hit) / len(hit), 4) if hit else None
        s["acc10_when_gold_not_retrieved"] = round(sum(r["acc10"] for r in miss) / len(miss), 4) if miss else None
        s["gold_retrieved_rate"] = round(len(hit) / n, 4)
    flagged = [r for r in rows if r.get("missing")]
    s["missing_flag_rate"] = round(len(flagged) / n, 4)
    if flagged and len(flagged) < n:
        s["acc10_flagged"] = round(sum(r["acc10"] for r in flagged) / len(flagged), 4)
        rest = [r for r in rows if not r.get("missing")]
        s["acc10_unflagged"] = round(sum(r["acc10"] for r in rest) / len(rest), 4)
    return s


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (round(c - h, 4), round(c + h, 4))


def paired(a: list[bool], b: list[bool], iters: int = 10000, seed: int = 0) -> dict:
    """Difference a-b in accuracy over the same items: point estimate, paired bootstrap 95% CI, exact McNemar p."""
    assert len(a) == len(b)
    n = len(a)
    diff = (sum(a) - sum(b)) / n
    rng = random.Random(seed)
    ds = sorted(sum(a[i] - b[i] for i in (rng.randrange(n) for _ in range(n))) / n for _ in range(iters))
    lo, hi = ds[int(0.025 * iters)], ds[int(0.975 * iters) - 1]
    only_a = sum(1 for x, y in zip(a, b) if x and not y)
    only_b = sum(1 for x, y in zip(a, b) if y and not x)
    m = only_a + only_b
    k = min(only_a, only_b)
    p = min(1.0, 2 * sum(math.comb(m, i) for i in range(k + 1)) / 2 ** m) if m else 1.0
    return {"diff": round(diff, 4), "ci95": [round(lo, 4), round(hi, 4)], "only_a": only_a, "only_b": only_b,
            "mcnemar_p": round(p, 5), "n": n}
