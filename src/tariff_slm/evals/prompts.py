"""One prompt format for every model under test. Three strategies for the prompt-ceiling ablation."""
from __future__ import annotations

import json

DIMENSIONS = ["gender_age", "fiber_content", "construction", "material", "use", "garment_type",
              "shape_coverage", "value", "other"]

# v2 (2026-11-01): dimension definitions, the runner-up defined as the closest sibling in the schedule tree, and
# the value as a short exact copy. Added after the smoke run showed correct codes failing only because the models
# could not know which competitor or which dimension name the spec meant (docs/evals/prompt-ceiling-2026-11-01.md).
PROMPT_VERSION = "v2"

DIMENSION_DEFINITIONS = {
    "gender_age": "who wears it: men, women, boys, girls, infants, unisex; adult versus child sizes",
    "fiber_content": "textile fibers and their percentages: cotton, wool, silk, flax, man-made (synthetic or "
                     "artificial), elastomeric yarn such as spandex; fiber percentage thresholds",
    "construction": "how it is made: knit or woven, knit to shape, with or without fourchettes, welt, molded, lined, "
                    "quilted, pile, terry, jersey",
    "material": "non-textile materials, mainly for footwear and accessories: leather, pigskin, rubber, plastics, "
                "textile materials as a material category",
    "use": "intended use or activity: sports or athletic (tennis, soccer, ski), work, protective, house slippers, "
           "sleepwear, swimwear, hospital or surgical, water resistant",
    "garment_type": "what the article is: shirt, blouse, jacket, overcoat versus anorak, tights, underpants, sets, "
                    "and similar",
    "shape_coverage": "shape or coverage: covers the ankle, open toe or heel, sleeve length, garment length",
    "value": "price or value thresholds, such as valued over a stated amount per pair",
    "other": "none of the above",
}

SCHEMA = {
    "decision": "SELECT or NEED_INFO",
    "code": "one candidate code exactly as listed, or null when NEED_INFO",
    "deciding_attribute": {"dimension": f"one of {DIMENSIONS}",
                           "value": "a short phrase (1-6 words) copied exactly from the description that states "
                                    "the attribute, or null"},
    "runner_up": "the candidate whose schedule path shares the most levels with your chosen code, or null",
}

BASE_SYSTEM = (
    "You classify imported products under the Harmonized Tariff Schedule of the United States (HTSUS). "
    "You are given a product description and candidate 10-digit HTS codes with their schedule text. "
    "Choose the one candidate U.S. Customs would assign. The runner-up is the candidate whose schedule path shares "
    "the most levels with your choice, and the deciding attribute is the one on which their two paths first differ. "
    "If the description does not state that attribute, do not guess: answer NEED_INFO and name the missing "
    "attribute's dimension. A residual line (\"Other\") is chosen when the description lacks the attribute its "
    "sibling requires, so it is never a reason for NEED_INFO. Dimensions: "
    + "; ".join(f"{k} = {v}" for k, v in DIMENSION_DEFINITIONS.items())
    + ". Reply with one JSON object only, no prose, matching: " + json.dumps(SCHEMA)
)

COT_SYSTEM = BASE_SYSTEM + (
    " Work through these checks silently before answering: (1) read each candidate's full schedule path; "
    "(2) pick the most plausible candidate and its runner-up, the candidate sharing the most path levels with it; "
    "(3) find the first level where their paths differ and name that attribute's dimension from the definitions; "
    "(4) check whether the description states it and copy the exact words if so; (5) if it is not stated "
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
