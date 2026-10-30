"""Load CROSS rulings from the HF copy, normalise codes and dates, and drop rows that cannot be trusted."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime

from .schedule import digits

_LEAK = re.compile(r"\bHTS|\bHTSUS|subheading|heading \d|classif|tariff|\b\d{4}\.\d{2}", re.I)


@dataclass(frozen=True)
class Ruling:
    ruling_id: str
    date: str          # ISO yyyy-mm-dd
    description: str   # model-written product summary from the HF copy (not CBP text)
    code10: str        # the ruling's single 10-digit code
    source_sha1: str   # hash of the original ruling text, for provenance


def _iso(s: str) -> str | None:
    try:
        return datetime.strptime(s.strip(), "%b %d, %Y").date().isoformat()
    except (ValueError, AttributeError):
        return None


def load_rulings(path: str) -> tuple[list[Ruling], dict[str, int]]:
    """Return trusted single-code rulings and a count of every reason a row was dropped."""
    drop: dict[str, int] = {}
    out, seen = [], set()

    def skip(reason: str) -> None:
        drop[reason] = drop.get(reason, 0) + 1

    for r in json.load(open(path, encoding="utf-8")):
        rid = (r.get("ruling_id") or "").strip()
        if not rid or rid in seen:
            skip("duplicate or missing id"); continue
        seen.add(rid)
        raw = (r.get("hts_code") or "").strip()
        code = digits(raw)
        if len(code) != 10:
            skip("not exactly one 10-digit code"); continue
        date = _iso(r.get("date") or "")
        if not date:
            skip("unparseable date"); continue
        desc = re.sub(r"\s+", " ", (r.get("full_description") or "")).strip()
        if len(desc.split()) < 6:
            skip("description under 6 words"); continue
        if _LEAK.search(desc) or code[:4] in digits(desc):
            skip("description leaks classification"); continue
        sha = hashlib.sha1((r.get("original_ruling_text") or "").encode()).hexdigest()
        out.append(Ruling(rid, date, desc, code, sha))
    return out, drop
