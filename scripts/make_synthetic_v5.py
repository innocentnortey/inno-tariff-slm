"""Generate schedule-derived synthetic training items by swapping one explicit deciding fact (candidates for v5).

Usage:
  uv run python -I scripts/make_synthetic_v5.py --in data/processed/train_v2.jsonl \
      --out data/processed/synthetic_v5_candidates.jsonl --max 600 --per-code 4

Each candidate copies a CBP-labelled training item and changes only its deciding fact to the sibling's, within the same
8-digit subheading, then takes the sibling code as its label. Labels are therefore derived from the USITC schedule,
not issued by CBP; every candidate must still pass an independent LLM judge (scripts/judge_synthetic_v5.py) before it
is used. Strict scope, per the Codex GPT-5.6 Sol review (2026-11-01):
  gender: men's <-> women's and boys' <-> girls' only (no unisex, infants, children/adult transitions), descriptions
          with exactly one wearer word and no other wearer cue (closure direction, bra, maternity, genitalia, dress,
          skirt, blouse);
  fiber:  "Of cotton" <-> "Of man-made fibers" lines only, descriptions with exactly one fiber phrase of the form
          "100% <fiber>" and no other fiber word (no blends, linings or shells of another fiber).
Rare target codes are preferred and capped per code. Dev and test are never used as seeds.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tariff_slm.data.attributes import evidence  # noqa: E402

GENDER_SWAP = {"men": "women", "women": "men", "man": "woman", "woman": "man", "boys": "girls", "girls": "boys",
               "boy": "girl", "girl": "boy"}
NODE_SWAP = {"Men's": "Women's", "Women's": "Men's", "Boys'": "Girls'", "Girls'": "Boys'"}
WEARER = re.compile(r"\b(m[ae]n|wom[ae]n|boys?|girls?)(['’]s|s['’]|['’])?(?![\w-])", re.I)
OTHER_WEARER_CUES = re.compile(r"left[- ]over[- ]right|right[- ]over[- ]left|\bbras?\b|bralette|maternity|genital|"
                               r"\bdress(es)?\b|\bskirts?\b|\bblouses?\b|\bunisex\b|\binfant|\bbab(y|ies)\b|\btoddler|"
                               r"\bchild|\bkids?\b|\byouth|\bjunior|\bmissy\b|\bladies\b|\bfemale|\bmale\b|\badult", re.I)
FIBER_WORDS = re.compile(r"cotton|polyester|nylon|acrylic|rayon|viscose|spandex|elastane|lycra|wool|silk|linen|modal|"
                         r"lyocell|polyamide|man[- ]made|synthetic|ramie|flax|hemp|acetate", re.I)
FIBER_PHRASE = re.compile(r"\b100\s*(%|percent)\s+(cotton|polyester)\b", re.I)


def swap_word(m: re.Match) -> str:
    word, suffix = m.group(1), m.group(2) or ""
    new = GENDER_SWAP[word.lower()]
    if word[0].isupper():
        new = new[0].upper() + new[1:]
    return new + suffix


def gender_candidate(it: dict) -> tuple[str, str] | None:
    if it["gold_node"] not in NODE_SWAP or it["sibling_node"] != NODE_SWAP[it["gold_node"]]:
        return None
    d = it["description"]
    if OTHER_WEARER_CUES.search(d) or len(WEARER.findall(d)) != 1:
        return None
    return WEARER.sub(swap_word, d, count=1), it["sibling_node"]


def fiber_candidate(it: dict) -> tuple[str, str] | None:
    pair = {it["gold_node"], it["sibling_node"]}
    if pair != {"Of cotton", "Of man-made fibers"}:
        return None
    d = it["description"]
    phrases = FIBER_PHRASE.findall(d)
    if len(phrases) != 1 or len(FIBER_WORDS.findall(d)) != 1:
        return None
    new_fiber = "polyester" if it["gold_node"] == "Of cotton" else "cotton"
    return FIBER_PHRASE.sub(lambda m: m.group(0)[: m.start(2) - m.start(0)] + new_fiber, d, count=1), it["sibling_node"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--max", type=int, default=600)
    ap.add_argument("--per-code", type=int, default=4)
    ap.add_argument("--seed", type=int, default=2029)
    a = ap.parse_args()
    rng = random.Random(a.seed)
    items = [json.loads(l) for l in open(a.src, encoding="utf-8")]
    train_codes = Counter(it["gold_code"] for it in items)
    cands, stats = [], Counter()
    for it in items:
        if it["kind"] != "decide" or it["id"].endswith(("-ablated",)) or "-pert-" in it["id"]:
            continue
        if it["gold_code"][:10] != (it.get("nearest_sibling") or "")[:10]:   # same 8-digit subheading (dotted form)
            continue
        made = gender_candidate(it) if it["deciding_dimension"] == "gender_age" else (
            fiber_candidate(it) if it["deciding_dimension"] == "fiber_content" else None)
        if not made:
            continue
        desc, new_node = made
        new_code = it["nearest_sibling"]
        if new_code not in {c["code"] for c in it["candidates"]}:
            continue
        ev = evidence(desc, it["deciding_dimension"], new_node, it["gold_node"])
        if not ev or ev == "__conflict__":
            stats["rejected_by_label_check"] += 1
            continue
        cands.append(dict(it, id=f"{it['id']}-syn", description=desc, gold_code=new_code, nearest_sibling=it["gold_code"],
                          gold_node=new_node, sibling_node=it["gold_node"], gold_value=ev, synthetic=True,
                          synthetic_from=it["id"],
                          expected={"decision": "SELECT", "code": new_code, "dimension": it["deciding_dimension"]}))
    # Prefer target codes that are rare in training, cap per code, then trim to --max.
    rng.shuffle(cands)
    cands.sort(key=lambda c: train_codes[c["gold_code"]])
    per, out = Counter(), []
    for c in cands:
        if per[c["gold_code"]] >= a.per_code:
            continue
        per[c["gold_code"]] += 1
        out.append(c)
        if len(out) >= a.max:
            break
    with open(a.out, "w", encoding="utf-8") as f:
        for c in out:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(json.dumps({"candidates_before_cap": len(cands), "written": len(out),
                      "by_dimension": Counter(c["deciding_dimension"] for c in out),
                      "target_codes": len(per), "unseen_target_codes": sum(1 for k in per if train_codes[k] == 0),
                      **stats}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
