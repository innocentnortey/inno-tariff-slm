"""Parse the USITC HTS export into 10-digit codes with their full description chains and duty rates."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

_CAT = re.compile(r"\s*\(\d{3}\)\s*$")  # textile category numbers such as "(338)"


def digits(code: str | None) -> str:
    return re.sub(r"\D", "", code or "")


@dataclass(frozen=True)
class ScheduleLine:
    code10: str            # ten digits, no dots
    chain: tuple[str, ...]  # descriptions from the heading down to this line
    general_rate: str       # column-1 general rate inherited from the nearest rated ancestor

    @property
    def dotted(self) -> str:
        c = self.code10
        return f"{c[:4]}.{c[4:6]}.{c[6:8]}.{c[8:]}"

    @property
    def text(self) -> str:
        return " > ".join(self.chain)


def load_schedule(path: str) -> dict[str, ScheduleLine]:
    """Return {ten-digit code: ScheduleLine} for every statistical line in the export."""
    rows = json.load(open(path, encoding="utf-8"))
    stack: list[tuple[int, str, str]] = []  # (indent, description, rate)
    out: dict[str, ScheduleLine] = {}
    for r in rows:
        indent = int(r.get("indent") or 0)
        code = digits(r.get("htsno"))
        desc = _CAT.sub("", (r.get("description") or "").strip()).rstrip(":")
        if len(code) == 4:
            stack = []
        while stack and stack[-1][0] >= indent:
            stack.pop()
        rate = (r.get("general") or "").strip()
        stack.append((indent, desc, rate))
        if len(code) == 10:
            inherited = next((s[2] for s in reversed(stack) if s[2]), "")
            out[code] = ScheduleLine(code, tuple(s[1] for s in stack if s[1]), inherited)
    return out
