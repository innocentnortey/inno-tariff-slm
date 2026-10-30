"""Attribute dimensions that separate sibling HTS codes in apparel and footwear, and how to detect them.

The deciding dimension for an item is read from the schedule: the first node where the gold code's chain and
its nearest sibling's chain differ. Whether the product description states that attribute is read from the
description with the same lexicon. No language model is involved.
"""
from __future__ import annotations

import re

# Order matters: the first dimension whose pattern matches a divergence node wins.
DIMENSIONS: dict[str, str] = {
    "value": r"\bvalued\b|\$\s?\d|\bper pair\b|\bper dozen\b|\bF\.?O\.?B\b",
    "gender_age": r"\bm[ae]n(?!-made)'?s?\b|\bboys?'?\b|\bwom[ae]n'?s?\b|\bgirls?'?\b|\bladies'?\b|\bfemale|\bmale\b|\binfants?'?\b|\btoddlers?\b|\bbab(y|ies)'?\b|\bchild(ren)?'?s?\b|\bunisex\b|\byouths?\b|\bjuniors?\b|\bmissy\b|\bkids?\b|\badults?\b|\bfor other persons\b",
    "fiber_content": r"\bcotton\b|\bwool\b|\banimal hair\b|\bman-made\b|\bsynthetic\b|\bartificial\b|\bsilk\b|\bflax\b|\bramie\b|\blinen\b|\bpolyester\b|\bnylon\b|\bacrylic\b|\brayon\b|\bviscose\b|\bspandex\b|\belastane\b|\bpercent by weight\b|\bcontaining \d+",
    "material": r"\bleather\b|\brubber\b|\bplastics?\b|\btextile materials?\b|\bcomposition\b|\bwood(en)?\b|\bcork\b|\bfelt\b|\bfur\b|\bpigskin\b",
    "construction": r"\bknit(ted)?\b|\bcrochet(ed)?\b|\bwoven\b|\bwelt\b|\bmou?lded\b|\bturn(ed)?\b|\bstitched\b|\bcemented\b|\bvulcaniz|\blined\b|\bquilted\b",
    "use": r"\bsports?\b|\btennis\b|\bski(ing)?\b|\bgolf\b|\bathletic\b|\bwork footwear\b|\bprotective\b|\bwater ?proof\b|\bsafety\b|\bslippers?\b|\bhouse\b|\boccupational\b|\bswim(wear)?\b|\bsleep(wear)?\b|\bnight",
    "shape_coverage": r"\bankle\b|\bknee\b|\bboots?\b|\bsandals?\b|\bslip-on\b|\bopen toes?\b|\bheels?\b|\bsleeves?\b|\bhooded\b|\bzipper\b|\bcollar\b|\bpockets?\b|\blength\b",
    "garment_type": r"\bshirts?\b|\bblouses?\b|\btrousers?\b|\bshorts\b|\bsweaters?\b|\bpullovers?\b|\bcardigans?\b|\bjackets?\b|\bcoats?\b|\bdress(es)?\b|\bskirts?\b|\bsuits?\b|\bensembles?\b|\bunderwear\b|\bpajamas?\b|\bnightdress|\brobes?\b|\bt-shirts?\b|\bsinglets?\b|\btank tops?\b|\bvests?\b|\bbriefs\b|\bpanties\b|\bgloves?\b|\bhosiery\b|\bsocks?\b|\btights\b|\btrack ?suits?\b|\boveralls?\b|\bcoveralls?\b|\bjumpsuits?\b",
}
_RX = {k: re.compile(v, re.I) for k, v in DIMENSIONS.items()}


def dimension_of(text: str) -> str | None:
    for name, rx in _RX.items():
        if rx.search(text):
            return name
    return None


def describes(description: str, dimension: str) -> bool:
    """True when the product description states something about this dimension."""
    return bool(_RX[dimension].search(description))


def stated_value(description: str, dimension: str) -> str | None:
    """The first words in the description that state this dimension (the reference 'value'), or None."""
    m = _RX[dimension].search(description)
    return m.group(0) if m else None


def strip_dimension(description: str, dimension: str) -> str:
    """Remove the words that state a dimension (used to build attribute-ablation NEED_INFO items)."""
    out = _RX[dimension].sub(" ", description)
    out = re.sub(r"\b\d+\s*%|\bpercent\b", " ", out) if dimension == "fiber_content" else out
    return re.sub(r"\s{2,}", " ", out).strip(" ,;")


def deciding_dimension(gold_chain: tuple[str, ...], sibling_chain: tuple[str, ...]) -> tuple[str | None, str, str]:
    """Return (dimension, gold node, sibling node) at the first divergence of the two chains."""
    for g, s in zip(gold_chain, sibling_chain):
        if g != s:
            dim = dimension_of(g) if g.lower() != "other" else None
            dim = dim or (dimension_of(s) if s.lower() != "other" else None)
            return dim, g, s
    return None, "", ""
