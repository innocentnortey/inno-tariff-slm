"""Extract the product facts from a CBP ruling letter, verbatim, without the classification that follows them.

The description a model sees must (a) be CBP's own wording, so no summary can drop or invent a fact, and (b) not
reveal the answer. A NY ruling states the merchandise first and the legal analysis after; an HQ ruling has a FACTS
section. We keep the sentences of that span, then drop any sentence that names a tariff number, heading, chapter,
note, a proposed classification, the duty, or letter boilerplate. Whatever survives is the description.
"""
from __future__ import annotations

import re

# The analysis has begun once a sentence matches one of these; nothing after it is used.
_STOP = re.compile(
    r"applicable (?:tariff )?(?:sub)?heading|General Rules? of Interpretation|\bGRIs?\b|In understanding the language"
    r"|Explanatory Notes?|\bENs?\b|rate of duty|\bISSUES?:|LAW AND ANALYSIS|HOLDING:|is classifiable|are classifiable"
    r"|is classified|are classified|we find that|provides for",
    re.I)
# A sentence that would leak the answer or isn't about the goods.
_LEAK = re.compile(
    r"\d{4}\.\d{2}|\b\d{4}\b(?=[^.]*\b(?:HTS|heading|subheading)\b)|\bHTSU?S?\b|Harmonized|tariff|(?:sub)?headings?\b"
    r"|\bchapters? \d|\bsection [IVX]+\b|\bnotes? \d|\bclassif|\bsuggest|\bpropos|\bduty|\bduties\b|\bCBP\b"
    r"|\bruling|\bprotest|\bliquidat|\bentr(?:y|ies)\b|Customs|\bsamples? (?:was|were|is|will|has|have)\b"
    r"|returned|for (?:our|your) review|you requested|your (?:letter|request|inquiry|submission)|requested a"
    r"|on behalf of|information was provided|provided (?:via|by) (?:e-?mail|telephone)|Dear |Sincerely|National Import Specialist|19 C\.?F\.?R|country of origin|\bstatistical\b",
    re.I)
_SENT = re.compile(r"(?<=[.!?])[\"”’)]?\s+(?=[A-Z“\"(])")
_WS = re.compile(r"\s+")

MAX_WORDS = 220
MIN_WORDS = 12


def sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT.split(_WS.sub(" ", text)) if s.strip()]


def _fact_span(text: str) -> str:
    """The part of the letter that describes the goods: HQ FACTS section, else everything after the request line."""
    t = _WS.sub(" ", text)
    m = re.search(r"\bFACTS?\s*:\s*(.*?)(?:\bISSUES?\s*:|\bLAW AND ANALYSIS\s*:|$)", t, re.S)
    if m and len(m.group(1).split()) >= MIN_WORDS:
        return m.group(1)
    m = re.search(r"you requested a (?:binding |tariff )*(?:classification )?ruling[^.]*\.", t, re.I)
    if m:
        return t[m.end():]
    m = re.search(r"Dear [^:]{1,80}:", t)
    return t[m.end():] if m else t


def extract_facts(text: str) -> tuple[str, dict]:
    """Return (description, stats). The description is '' when too little survives to describe the product."""
    kept, dropped, stopped = [], 0, False
    for s in sentences(_fact_span(text)):
        if _STOP.search(s):
            stopped = True
            break
        if _LEAK.search(s):
            dropped += 1
            continue
        kept.append(s)
    out, n = [], 0
    for s in kept:
        w = len(s.split())
        if n + w > MAX_WORDS and out:
            break
        out.append(s)
        n += w
    desc = " ".join(out)
    if len(desc.split()) < MIN_WORDS:
        desc = ""
    return desc, {"kept": len(out), "dropped": dropped, "stopped": stopped, "words": len(desc.split())}


def leaks_code(description: str, code10: str) -> bool:
    """True when the description carries the answer's digits (4-digit heading or longer) in any common form."""
    d = re.sub(r"\D", " ", description)
    flat = re.sub(r"\D", "", description)
    return code10[:6] in flat or bool(re.search(rf"(?<!\d){code10[:4]}(?!\d)", d))
