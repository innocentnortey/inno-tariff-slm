"""Normalise CROSS rulings from both sources into one record shape with a trusted single label.

Sources: the HF copy `orlandowhite/hts-cross-rulings` (2000 → 2025-08-01) and rulings fetched from the CROSS
single-ruling endpoint (`scripts/fetch_cross_recent.py`, 2025-08 onward). A record is kept only when it is a tariff
classification ruling for one product with one primary 10-digit code (chapters 01–97) that exists in the current
HTSUS. Every drop is counted by reason.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from ..data.schedule import ScheduleLine, digits
from .facts import extract_facts, leaks_code

_WS = re.compile(r"\s+")
_CODE = re.compile(r"\b\d{4}\.\d{2}(?:\.\d{2,4})?(?:\.\d{2})?\b")
_APPLICABLE = re.compile(r"applicable (?:tariff )?(?:sub)?heading[^.]{0,300}?(\d{4}\.\d{2}(?:\.\d{2,4})?(?:\.\d{2})?)",
                         re.I)


@dataclass(frozen=True)
class Record:
    ruling_id: str     # "NY N360000" / "HQ H304455"
    date: str          # ISO date of the ruling
    code: str          # 10 digits, no dots
    product: str       # CBP's subject-line name for the goods, e.g. "a data processing server"
    description: str   # verbatim fact sentences from the letter (facts.extract_facts)
    source: str        # "hf" or "cross_api"
    text_sha1: str     # hash of the full ruling text, for provenance
    code_mapped: bool  # True when an 8-digit ruling code was mapped to its only current 10-digit line

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)


def subject(text: str) -> str:
    m = re.search(r"RE:\s*(.{0,200}?)(?:\s+Dear\b|\s{2,}|$)", _WS.sub(" ", text))
    return m.group(1).strip() if m else ""


def product_name(subj: str) -> str:
    """'The tariff classification of a remote control from China' -> 'a remote control'."""
    s = re.sub(r"^.*?\bclassification\b\s*", "", subj, flags=re.I)
    s = re.sub(r"^(?:,?\s*and\s+(?:the\s+)?(?:country of origin|origin|marking|status|eligibility|applicability)\b[^,]*?"
               r"(?:,\s*|\s+(?=of\b)))+", "", s, flags=re.I)
    s = re.sub(r"^of\s+", "", s, flags=re.I)
    s = re.sub(r"\s+from\s+[A-Z][\w .,'()-]*$", "", s)
    s = re.sub(r"[;:].*$", "", s).strip(" .")
    return "" if _CODE.search(s) or re.search(r"\b(?:sub)?heading|HTS", s, re.I) else s


def is_classification(subj: str, text: str) -> bool:
    if subj:
        return "classification" in subj.lower()
    return bool(re.search(r"\btariff classification\b", text[:1500], re.I))


def primary_code(codes: list[str], sched: dict[str, ScheduleLine], children: dict[str, list[str]]) -> tuple[str, bool] | None:
    """One 10-digit code from a ruling's code list, ignoring chapter 98/99 lines; None if zero or several remain."""
    main = {digits(c) for c in codes if digits(c)[:2] not in ("98", "99") and len(digits(c)) >= 8}
    norm: set[tuple[str, bool]] = set()
    for c in main:
        if len(c) == 10:
            norm.add((c, False))
        elif len(c) == 8 and len(children.get(c, [])) == 1:
            norm.add((children[c][0], True))
        else:
            return None
    if len({c for c, _ in norm}) != 1:
        return None
    return next(iter(norm))


def children_index(sched: dict[str, ScheduleLine]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for c in sched:
        out.setdefault(c[:8], []).append(c)
    return out


def _record(rid: str, date: str, text: str, codes: list[str], source: str, sched, children, drop) -> Record | None:
    def skip(reason: str) -> None:
        drop[reason] = drop.get(reason, 0) + 1

    subj = subject(text)
    if not is_classification(subj, text):
        return skip("not a classification ruling")
    applicable = {digits(c)[:8] for c in _APPLICABLE.findall(_WS.sub(" ", text)) if digits(c)[:2] not in ("98", "99")}
    if len(applicable) > 1:
        return skip("several products or codes")
    got = primary_code(codes, sched, children)
    if got is None:
        return skip("not one primary 10-digit code")
    code, mapped = got
    if code not in sched:
        return skip("code not in current HTSUS")
    desc, _ = extract_facts(text)
    if not desc:
        return skip("too few fact sentences")
    prod = product_name(subj)
    if leaks_code(desc, code) or leaks_code(prod, code):
        return skip("description carries the code")
    sha = hashlib.sha1(text.encode()).hexdigest()
    return Record(rid, date, code, prod, desc, source, sha, mapped)


def load_hf(path: str, sched, drop: dict) -> list[Record]:
    children = children_index(sched)
    out, seen = [], set()
    for r in json.load(open(path, encoding="utf-8")):
        rid = (r.get("ruling_id") or "").strip()
        if not rid or rid in seen:
            drop["duplicate id"] = drop.get("duplicate id", 0) + 1
            continue
        seen.add(rid)
        try:
            date = datetime.strptime((r.get("date") or "").strip(), "%b %d, %Y").date().isoformat()
        except ValueError:
            drop["bad date"] = drop.get("bad date", 0) + 1
            continue
        text = r.get("original_ruling_text") or ""
        rec = _record(rid, date, text, [r.get("hts_code") or ""], "hf", sched, children, drop)
        if rec:
            out.append(rec)
    return out


def load_api(paths: list[str], sched, drop: dict) -> list[Record]:
    children = children_index(sched)
    out, seen = [], set()
    for p in paths:
        if not Path(p).exists():
            continue
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            rid = f"{r['collection'].upper()} {r['rulingNumber']}"
            if rid in seen:
                continue
            seen.add(rid)
            if r.get("revokedBy") or r.get("operationallyRevoked"):
                drop["revoked"] = drop.get("revoked", 0) + 1
                continue
            text = (r.get("subject") and f"RE: {r['subject']}  " or "") + _WS.sub(" ", r.get("text") or "")
            codes = [c for c in re.split(r"[;,]\s*", r.get("tariffs") or "") if c.strip()]
            rec = _record(rid, r["rulingDate"][:10], text, codes, "cross_api", sched, children, drop)
            if rec:
                out.append(rec)
    return out
