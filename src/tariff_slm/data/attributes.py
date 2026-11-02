"""Attribute dimensions that separate sibling HTS codes in apparel and footwear, and how to detect them.

The deciding dimension for an item is read from the schedule: the first node where the gold code's chain and
its nearest sibling's chain differ, and the first dimension on which those two nodes actually differ. Whether
the product description states that attribute is read with `evidence`, which requires the cited words to
support the gold line over the sibling (not merely to mention the dimension). No language model is involved.

Label review 2026-11-01 (docs/data/label-review-2026-11-01.md) drove the value-level checks for gender, fiber
and knit-to-shape, the pair-aware dimension choice, and the artifact check on ablated descriptions.
"""
from __future__ import annotations

import re

_APOS = r"(?:['’]s|s['’]|['’]|s)?"   # possessives and plurals: men's, mens, boys', girl’s
_END = r"(?![\w-])"


def _w(*stems: str) -> str:
    return r"\b(?:" + "|".join(stems) + r")" + _APOS + _END


_GENDER_TERMS = {
    "W": _w("wom[ae]n", "lad(?:y|ie)", "miss(?:es|y)", "junior") + r"|\bfemales?\b",
    "G": _w("girl"),
    "M": _w(r"m[ae]n(?![\s-]?made)") + r"|\bmales?\b",
    "B": _w("boy"),
    "INF": _w("infant", "bab(?:y|ie)"),
    "CHILD": _w("child(?:ren)?", "kid", "youth", "toddler"),
    "ADULT": _w("adult"),
    "UNI": r"\bunisex\b|\bboth sexes\b|\bfor (?:men and women|women and men)\b",
}
_GENDER_RX = {k: re.compile(v, re.I) for k, v in _GENDER_TERMS.items()}
_EXPAND = {"CHILD": {"G", "B"}, "ADULT": {"W", "M"}}
_MIXED = re.compile(r"\b(?:m[ae]n|wom[ae]n|boys?|girls?)['’]?s?['’]?\s+(?:and|&|or)\s+(?:m[ae]n|wom[ae]n|boys?|girls?)\b", re.I)

# Order matters only between dimensions that both separate the two nodes; the first one wins.
DIMENSIONS: dict[str, str] = {
    "value": r"\bvalued\b|\$\s?\d|\bper pair\b|\bper dozen\b|\bF\.?O\.?B\b",
    "gender_age": "|".join(_GENDER_TERMS.values()) + r"|\bfor other persons\b",
    "fiber_content": r"\bcotton\b|\bwool\b|\banimal hair\b|\bman[- ]made\b|\bsynthetic\b|\bartificial\b|\bsilk\b|\bflax\b|\bramie\b|\blinen\b|\bhemp\b|\bjute\b|\bpolyester\b|\bnylon\b|\bpolyamide\b|\bacrylic\b|\bmodacrylic\b|\brayon\b|\bviscose\b|\bmodal\b|\blyocell\b|\bacetate\b|\bspandex\b|\belastane\b|\blycra\b|\belastomeric\b|\baramid\b|\bpolypropylene\b|\bolefin\b|\bcashmere\b|\bmohair\b|\balpaca\b|\bangora\b|\bpercent by weight\b|\bcontaining \d+",
    "material": r"\bleather\b|\brubber\b|\bplastics?\b|\btextile materials?\b|\bcomposition\b|\bwood(en)?\b|\bcork\b|\bfelt\b|\bfur\b|\bpigskin\b",
    "construction": r"\bknit(ted)?\b|\bcrochet(ed)?\b|\bwoven\b|\bwelt\b|\bmou?lded\b|\bturn(ed)?\b|\bstitched\b|\bcemented\b|\bvulcaniz|\blined\b|\bquilted\b|\bfourchettes?\b|\bknit to shape\b|\bfully fashioned\b|\bjersey\b|\bterry\b|\bpile\b|\bnapped\b|\bcolors in the warp\b",
    "garment_type": r"\bshirts?\b|\bblouses?\b|\btrousers?\b|\bshorts\b|\bsweaters?\b|\bpullovers?\b|\bcardigans?\b|\bsweatshirts?\b|\bwaistcoats?\b|\bjackets?\b|\bcoats?\b|\bovercoats?\b|\braincoats?\b|\bcarcoats?\b|\bcapes?\b|\bcloaks?\b|\banoraks?\b|\bwind ?breakers?\b|\bparkas?\b|\bblazers?\b|\bdress(es)?\b|\bskirts?\b|\bsuits?\b|\bensembles?\b|\bunderwear\b|\bunderpants\b|\bboxers?\b|\bbodysuits?\b|\bbodyshirts?\b|\btops?\b|\bjumpers?\b|\bplay ?suits?\b|\bsunsuits?\b|\bwashsuits?\b|\bsets\b|\bpajamas?\b|\bnightdress|\bbathrobes?\b|\bdressing gowns?\b|\brobes?\b|\bt-shirts?\b|\bsinglets?\b|\btank tops?\b|\bvests?\b|\bbriefs?\b|\bpanties\b|\bundershirts?\b|\bbras?\b|\bbrassieres?\b|\bgloves?\b|\bmittens?\b|\bmitts?\b|\bhosiery\b|\bsocks?\b|\btights\b|\bleggings\b|\bstockings?\b|\btrack ?suits?\b|\boveralls?\b|\bcoveralls?\b|\bjumpsuits?\b|\bheadbands?\b|\bponytail holders?\b|\bscar(f|ves)\b|\bshawls?\b|\bties\b|\bcravats?\b",
    "use": r"\bsports?\b|\btennis\b|\bski(ing)?\b|\bsnowboard|\bgolf\b|\bathletic\b|\bsneakers?\b|\btrainers?\b|\bbasketball\b|\bgym\b|\bhockey\b|\bsoccer\b|\bfootball\b|\bcleat(s|ed)?\b|\bbaseball\b|\bsoftball\b|\brunning\b|\bhiking\b|\bcycling\b|\bsurgical\b|\bisolation\b|\bwater[- ](resistant|repellent)\b|\bdwr\b|\bdurable water repellent\b|\bwork footwear\b|\bprotective\b|\bwater ?proof\b|\bsafety\b|\bslippers?\b|\bhouse\b|\boccupational\b|\bhospitals?\b|\bclinics?\b|\blaborator(y|ies)\b|\bswim(wear)?\b|\bsleep(wear)?\b|\bnight",
    "shape_coverage": r"\bankle\b|\bknee\b|\bboots?\b|\bsandals?\b|\bslip-on\b|\bopen toes?\b|\bheels?\b|\bsleeves?\b|\bhooded\b|\bzipper\b|\bcollar\b|\bpockets?\b|\blength\b",
}
_RX = {k: re.compile(v, re.I) for k, v in DIMENSIONS.items()}

# Fiber families. "Man-made" is synthetic plus artificial.
_FIBER = {
    "synthetic": r"polyester|nylon|polyamide|acrylic|modacrylic|spandex|elastane|lycra|aramid|polypropylene|olefin|polyethylene|microfib(?:er|re)|synthetic",
    "artificial": r"rayon|viscose|modal|lyocell|tencel|acetate|triacetate|cupro|artificial",
    "cotton": r"cotton",
    "wool": r"wool|animal hair|cashmere|alpaca|mohair|angora|camel hair|merino",
    "silk": r"silk",
    "flax": r"flax|linen|ramie|hemp|jute",
    "elastomeric": r"spandex|elastane|lycra|elastomeric|rubber thread|elastic yarn",
}
_FIBER_RX = {k: re.compile(r"\b(?:" + v + r")\b", re.I) for k, v in _FIBER.items()}
_FIBER_PHRASE = re.compile(
    r"(?:(\d+(?:\.\d+)?)\s*(?:%|percent)\s+(?:[a-z/-]+\s+){0,2}?)?\b(" + "|".join(_FIBER.values()) + r")\b", re.I)
_THRESHOLD = re.compile(r"(\d+)\s*percent or more", re.I)
_KNIT_TO_SHAPE = re.compile(r"knit[- ]to[- ]shape|fully[- ]fashioned|knit(?:ted)?\s+(?:\w+\s+){0,2}to\s+(?:their|its)?\s*(?:final\s+)?shape", re.I)

_COVERALL = re.compile(r"coveralls?|jumpsuits?|overalls?", re.I)
_UPPER_BODY = re.compile(r"upper[- ]body garment", re.I)

CONFLICT = "__conflict__"


def dimension_of(text: str) -> str | None:
    for name, rx in _RX.items():
        if rx.search(text):
            return name
    return None


def _terms(text: str, dim: str) -> set[str]:
    """Lexicon terms in a node; a term under "without"/"not" is marked, so "With fourchettes" and
    "Without fourchettes" differ."""
    out = set()
    for m in _RX[dim].finditer(text):
        negated = re.search(r"\b(?:without|not)\b[^,;]*$", text[: m.start()], re.I)
        out.add(("not " if negated else "") + m.group(0).lower())
    return out


def separating_dimension(gold_node: str, sibling_node: str) -> str | None:
    """First dimension on which the two nodes differ: one side has terms and the other none, or neither side's
    terms contain the other's (so "Gloves" against "Ice hockey gloves" is decided by use, not garment type)."""
    # Only a bare "Other" is a residual; "Other gloves ... designed for use in sports" still names attributes.
    g_other = gold_node.strip(" :").lower() == "other"
    s_other = sibling_node.strip(" :").lower() == "other"
    for dim in _RX:
        tg = set() if g_other else _terms(gold_node, dim)
        ts = set() if s_other else _terms(sibling_node, dim)
        if not tg and not ts:
            continue
        if bool(tg) != bool(ts) or not (tg <= ts or ts <= tg):
            return dim
    return None


def describes(description: str, dimension: str) -> bool:
    """True when the product description states something about this dimension (dimension-level only)."""
    return bool(_RX[dimension].search(description))


def stated_value(description: str, dimension: str) -> str | None:
    """The first words in the description that state this dimension, or None (dimension-level only)."""
    m = _RX[dimension].search(description)
    return m.group(0) if m else None


def _gender_cats(text: str) -> set[str]:
    return {k for k, rx in _GENDER_RX.items() if rx.search(text)}


def _expand(cats: set[str]) -> set[str]:
    out = set(cats)
    for k, extra in _EXPAND.items():
        if k in cats:
            out |= extra
    return out


def _gender_evidence(description: str, gold_node: str, sibling_node: str) -> str | None:
    gold = _expand(_gender_cats(gold_node))
    sib = _expand(_gender_cats(sibling_node))
    if not gold:
        return stated_value(description, "gender_age")
    if _MIXED.search(description):
        return CONFLICT
    if not (sib & {"W", "G"}) and (gold & {"W"}):
        gold = gold | {"UNI"}   # Ch. 61/62 notes and Ch. 64 "commonly worn by both sexes": unisex goes to women's
    hits = sorted((m.start(), m.group(0), k) for k, rx in _GENDER_RX.items() for m in rx.finditer(description))
    found = None
    for _, words, k in hits:
        cats = _expand({k})
        support = cats & gold
        if (cats & sib) and not support:
            return CONFLICT   # a wearer term points only at the sibling line (e.g. two products in one description)
        if found is None and support and not support <= sib:
            found = words
    return found


def _fiber_families(node: str) -> set[str]:
    n = node.lower()
    fam = set()
    if re.search(r"man-made", n):
        fam |= {"synthetic", "artificial"}
    for k in ("synthetic", "artificial", "cotton", "wool", "silk", "flax", "elastomeric"):
        if _FIBER_RX[k].search(n) and not (k == "elastomeric" and "rubber or plastics" in n and "thread" not in n):
            fam.add(k)
    return fam


def _fiber_evidence(description: str, gold_node: str, sibling_node: str) -> str | None:
    gold = _fiber_families(gold_node)
    if not gold:
        return stated_value(description, "fiber_content")
    sib = _fiber_families(sibling_node)
    need = _THRESHOLD.search(gold_node)
    seen_sib = False
    for m in _FIBER_PHRASE.finditer(description):
        fams = {k for k, rx in _FIBER_RX.items() if rx.search(m.group(2))}
        if fams & gold:
            if need and (m.group(1) is None or float(m.group(1)) < float(need.group(1))):
                continue   # a threshold line needs a stated percentage at or above it
            return m.group(0).strip()
        if fams & sib:
            seen_sib = True
    return CONFLICT if seen_sib and not need else None


def evidence(description: str, dimension: str | None, gold_node: str, sibling_node: str) -> str | None:
    """Words in the description that support the gold node over the sibling on this dimension; None when the
    description doesn't state it; CONFLICT when the description points at the sibling instead."""
    if dimension is None:
        return None
    if dimension == "gender_age":
        return _gender_evidence(description, gold_node, sibling_node)
    if dimension == "fiber_content":
        return _fiber_evidence(description, gold_node, sibling_node)
    if dimension == "garment_type" and _COVERALL.search(sibling_node) and not _COVERALL.search(gold_node):
        m = _UPPER_BODY.search(description)   # an upper-body garment cannot be a coverall or jumpsuit
        if m:
            return m.group(0)
    if dimension == "construction" and _KNIT_TO_SHAPE.search(gold_node):
        m = _KNIT_TO_SHAPE.search(description)
        return m.group(0) if m else None
    return stated_value(description, dimension)


_ARTIFACT = re.compile(
    r"(?:^|\s)[,;/.:](?=\s|$)|[,;]\s*[,;.]|\ba\s+(?=[aeiou])|\(\s*\)|\b\d+\.(?:\s|,|$)|\b(?:a|an|the|for|of|and|or|with|by|in)\s*[,;/:.]"
    r"|^\s*(?:and|or|of|for|with|in)\b|\s/\s|^\W|\bof\s+and\b|\bit\s*[,;.]"
    r"|['’]s\s+(?:crafted|constructed|made|composed|featuring|from|with|in)\b", re.I)


def strip_dimension(description: str, dimension: str) -> str | None:
    """Remove the words that state a dimension (attribute-ablation NEED_INFO items). Returns None when the
    result shows where words were cut, since a model could learn the gap instead of the attribute."""
    if dimension == "fiber_content":
        out = _FIBER_PHRASE.sub(" ", description)
        out = re.sub(r"\b\d+(?:\.\d+)?\s*(?:%|percent)", " ", out)
    else:
        out = _RX[dimension].sub(" ", description)
    out = re.sub(r"\s+([,;.:])", r"\1", out)
    out = re.sub(r"\s{2,}", " ", out).strip(" ,;")
    return None if _ARTIFACT.search(out) or len(out.split()) < 6 else out


def deciding_dimension(gold_chain: tuple[str, ...], sibling_chain: tuple[str, ...]) -> tuple[str | None, str, str]:
    """Return (dimension, gold node, sibling node) at the first divergence of the two chains."""
    for g, s in zip(gold_chain, sibling_chain):
        if g != s:
            return separating_dimension(g, s), g, s
    return None, "", ""
