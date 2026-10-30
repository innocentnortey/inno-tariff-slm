"""LLM-as-judge: two narrow yes/no questions per SELECT answer. Runs only when a judge model is named."""
from __future__ import annotations

import json

RUBRIC = (
    "You check one tariff-classification answer. Reply with JSON only: "
    '{"attribute_stated": "yes|no", "attribute_separates": "yes|no", "reason": "<one sentence>"}. '
    "attribute_stated: does the product description itself state the cited deciding attribute value? "
    "attribute_separates: does that attribute explain why the chosen code's schedule text fits and the runner-up's does not? "
    "Judge only from the text given. Do not use outside knowledge of the correct code."
)


def judge_messages(item: dict, answer: dict) -> list[dict]:
    text = {c["code"]: c["text"] for c in item["candidates"]}
    body = (f"Description: {item['description']}\n\nChosen: {answer.get('code')}: {text.get(answer.get('code'), '?')}\n"
            f"Runner-up: {answer.get('runner_up')}: {text.get(answer.get('runner_up'), '?')}\n"
            f"Cited attribute: {json.dumps(answer.get('deciding_attribute'))}")
    return [{"role": "system", "content": RUBRIC}, {"role": "user", "content": body}]
