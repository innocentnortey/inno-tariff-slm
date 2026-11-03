"""Prompts for benchmark v2. Every model in a comparison gets the same messages for the same item.

Modes:
  * `rag`    — product facts + retrieved precedents + retrieved HTSUS lines (Track B primary).
  * `closed` — product facts only (Track B closed-book reference).
  * `atlas`  — ATLAS's own question text, verbatim (Track A); the only addition is the answer-line instruction.
The answer is the last `CODE:` line. An optional `MISSING:` line names a deciding fact the description lacks; it
never replaces the code.
"""
from __future__ import annotations

import re

PROMPT_VERSION = "openset-v1"

SYSTEM = (
    "You classify imported goods under the Harmonized Tariff Schedule of the United States (HTSUS), current edition. "
    "Given a product description, give the single 10-digit statistical reporting number that U.S. Customs and Border "
    "Protection would assign. Classify by the terms of the headings and any section or chapter notes, then by "
    "subheading, following the General Rules of Interpretation.\n"
    "{reference}"
    "End your answer with one line exactly in this form:\nCODE: XXXX.XX.XX.XX\n"
    "If a fact that decides between codes is not stated, still give the most likely code, and add a line before it:\n"
    "MISSING: <the fact>"
)
REF_RAG = (
    "The user message includes reference material found by an automatic search: earlier CBP rulings on similar goods "
    "and HTSUS lines with their full text. It is a search result, not an answer key: the correct code may be absent, "
    "and an earlier ruling may concern different goods. Any valid HTSUS code may be given.\n"
)


SYSTEM_QA = ("You are an expert on the Harmonized Tariff Schedule of the United States (HTSUS), current edition. "
             "Answer exactly and concisely.")


def dotted(code: str) -> str:
    return f"{code[:4]}.{code[4:6]}.{code[6:8]}.{code[8:10]}"


def render_rag(item: dict) -> str:
    lines = [f"Product: {item['product'] or '(not named)'}", f"Description: {item['description']}", "",
             "Earlier CBP rulings on similar goods (most similar first):"]
    for i, p in enumerate(item["precedents"], 1):
        lines.append(f"{i}. [{p['ruling_id']}] {p['product'] or 'goods'}: {p['description']} -> {dotted(p['code'])}")
    if not item["precedents"]:
        lines.append("(none found)")
    lines += ["", "HTSUS lines found by search (may not include the answer):"]
    lines += [f"- {dotted(c['code'])}: {c['text']}" for c in item["candidates"]]
    return "\n".join(lines)


def render_closed(item: dict) -> str:
    return f"Product: {item['product'] or '(not named)'}\nDescription: {item['description']}"


def messages(item: dict, mode: str) -> list[dict]:
    if mode == "rag":
        return [{"role": "system", "content": SYSTEM.format(reference=REF_RAG)},
                {"role": "user", "content": render_rag(item)}]
    if mode == "closed":
        return [{"role": "system", "content": SYSTEM.format(reference="")},
                {"role": "user", "content": render_closed(item)}]
    if mode == "qa":  # schedule-knowledge drills (training only): a direct question about the HTSUS
        return [{"role": "system", "content": SYSTEM_QA}, {"role": "user", "content": item["question"]}]
    if mode == "atlas":
        return [{"role": "system", "content": SYSTEM.format(reference="")},
                {"role": "user", "content": item["question"]}]
    raise ValueError(mode)


def target(item: dict) -> str:
    """Training target for the small model: the answer line, preceded by a verified rationale when the item has one."""
    if item.get("target_text"):
        return item["target_text"]
    if item.get("rationale"):
        return f"REASONING: {item['rationale']}\nCODE: {dotted(item['code'])}"
    return f"CODE: {dotted(item['code'])}"


_CODE_LINE = re.compile(r"CODE:\s*([0-9][0-9.\s-]{3,20})", re.I)
_ANY_CODE = re.compile(r"\b\d{4}\.?\d{2}\.?\d{2}\.?\d{2}\b")


def parse(raw: str) -> dict:
    """{'code': 10 digits or partial digits or None, 'missing': str|None}."""
    raw = raw or ""
    hits = _CODE_LINE.findall(raw)
    code = re.sub(r"\D", "", hits[-1]) if hits else None
    if not code:
        any_ = _ANY_CODE.findall(raw)
        code = re.sub(r"\D", "", any_[-1]) if any_ else None
    miss = re.findall(r"^\s*MISSING:\s*(.+)$", raw, re.M)
    return {"code": code[:10] if code else None, "missing": miss[-1].strip() if miss else None}
