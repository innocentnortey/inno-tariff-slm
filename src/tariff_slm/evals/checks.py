"""Deterministic scoring of one model output against one eval item. No model involved."""
from __future__ import annotations

import json
import re

from .prompts import DIMENSIONS

_JSON = re.compile(r"\{.*\}", re.S)


def parse(raw: str) -> dict | None:
    raw = re.sub(r"<think>.*?</think>", "", raw or "", flags=re.S)
    m = _JSON.search(raw)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def _digits(c) -> str:
    return re.sub(r"\D", "", c or "")


def score(item: dict, raw: str) -> dict:
    exp = item["expected"]
    out = parse(raw)
    r = {"id": item["id"], "kind": item["kind"], "valid_json": out is not None, "raw": raw}
    cands = {_digits(c["code"]) for c in item["candidates"]}
    if out is None:
        r.update(schema_ok=False, decision_correct=False, spec_pass=False)
        return r
    dec = str(out.get("decision", "")).upper()
    code = _digits(out.get("code"))
    attr = out.get("deciding_attribute") or {}
    dim = attr.get("dimension") if isinstance(attr, dict) else None
    val = attr.get("value") if isinstance(attr, dict) else None
    r["schema_ok"] = dec in ("SELECT", "NEED_INFO") and dim in DIMENSIONS and (dec == "NEED_INFO" or code in cands)
    r["decision"] = dec
    r["decision_correct"] = dec == exp["decision"]
    r["false_confidence"] = exp["decision"] == "NEED_INFO" and dec == "SELECT"
    r["over_asking"] = exp["decision"] == "SELECT" and dec == "NEED_INFO"
    gold = _digits(exp["code"])
    if exp["decision"] == "SELECT":
        for n in (10, 8, 6, 4):
            r[f"match{n}"] = dec == "SELECT" and len(code) >= n and code[:n] == gold[:n]
        r["in_candidates"] = code in cands
    labelled = exp["dimension"] is not None and item["kind"] in ("decide", "need_info_natural", "need_info_ablated")
    r["dimension_correct"] = (dim == exp["dimension"]) if labelled else None
    grounded = None
    if dec == "SELECT" and item["kind"] == "decide":
        grounded = bool(val) and str(val).lower().strip(" .'\"") in item["description"].lower()
    r["value_grounded"] = grounded
    if exp["decision"] == "SELECT":
        ok = r["schema_ok"] and r["match10"]
        if item["kind"] == "decide":
            ok = ok and bool(r["dimension_correct"]) and bool(grounded)
    else:
        ok = r["schema_ok"] and dec == "NEED_INFO" and bool(r["dimension_correct"])
    r["spec_pass"] = bool(ok)
    return r


def summarise(rows: list[dict]) -> dict:
    def rate(key, subset):
        vals = [x[key] for x in subset if x.get(key) is not None]
        return round(sum(bool(v) for v in vals) / len(vals), 3) if vals else None
    sel = [x for x in rows if x["kind"] in ("decide", "decide_residual", "decide_unlabelled")]
    need = [x for x in rows if x["kind"].startswith("need_info")]
    return {
        "n": len(rows), "n_select": len(sel), "n_need_info": len(need),
        "spec_pass": rate("spec_pass", rows), "valid_json": rate("valid_json", rows), "schema_ok": rate("schema_ok", rows),
        "code_exact10_on_select": rate("match10", sel), "code_match6_on_select": rate("match6", sel),
        "dimension_correct": rate("dimension_correct", rows), "value_grounded": rate("value_grounded", rows),
        "need_info_recall": rate("decision_correct", need), "false_confidence_rate": rate("false_confidence", need),
        "over_asking_rate": rate("over_asking", sel),
        "spec_pass_select": rate("spec_pass", sel), "spec_pass_need_info": rate("spec_pass", need),
    }
