"""One prompt format for every model under test. Three strategies for the prompt-ceiling ablation."""
from __future__ import annotations

import json

DIMENSIONS = ["gender_age", "fiber_content", "construction", "material", "use", "garment_type",
              "shape_coverage", "value", "other"]

SCHEMA = {
    "decision": "SELECT or NEED_INFO",
    "code": "one candidate code exactly as listed, or null when NEED_INFO",
    "deciding_attribute": {"dimension": f"one of {DIMENSIONS}",
                           "value": "the words from the description that decide it, or null"},
    "runner_up": "the closest other candidate code, or null",
}

BASE_SYSTEM = (
    "You classify imported products under the Harmonized Tariff Schedule of the United States (HTSUS). "
    "You are given a product description and candidate 10-digit HTS codes with their schedule text. "
    "Choose the one candidate U.S. Customs would assign. If the description does not state the attribute "
    "that separates the best candidate from the closest alternative, do not guess: answer NEED_INFO and name "
    "that missing attribute dimension. Reply with one JSON object only, no prose, matching: "
    + json.dumps(SCHEMA)
)

COT_SYSTEM = BASE_SYSTEM + (
    " Work through these checks silently before answering: (1) read each candidate's full schedule path; "
    "(2) find the first level where the two most plausible candidates differ; (3) name that attribute's "
    "dimension; (4) check whether the description states it — quote the words if so; (5) if it is not stated "
    "and the better candidate is not a residual 'Other' line, answer NEED_INFO; (6) apply GRI 1, then GRI 3(b) "
    "essential character for composite goods. Output only the final JSON object."
)


def render_user(item: dict) -> str:
    lines = [f"Product description: {item['description']}", "", "Candidates:"]
    for c in item["candidates"]:
        lines.append(f"- {c['code']}: {c['text']}")
    return "\n".join(lines)


def target_json(item: dict) -> str:
    """Reference answer used for few-shot examples and SFT targets (labels from the ruling and schedule only)."""
    exp = item["expected"]
    return json.dumps({
        "decision": exp["decision"], "code": exp["code"],
        "deciding_attribute": {"dimension": exp["dimension"] or "other", "value": item.get("gold_value")},
        "runner_up": item.get("nearest_sibling") if exp["decision"] == "SELECT" else None,
    })


def messages(item: dict, strategy: str, shots: list[dict] | None = None) -> list[dict]:
    system = COT_SYSTEM if strategy == "cot" else BASE_SYSTEM
    msgs = [{"role": "system", "content": system}]
    if strategy == "few_shot":
        for s in shots or []:
            msgs += [{"role": "user", "content": render_user(s)}, {"role": "assistant", "content": target_json(s)}]
    msgs.append({"role": "user", "content": render_user(item)})
    return msgs
