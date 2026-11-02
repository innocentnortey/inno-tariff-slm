"""Turn reviewed dataset items into supervised fine-tuning examples, with the exact prompt the evals use.

Pure functions, no ML imports, so the example shape is testable on any machine. The model is trained on the
assistant answer only; the prompt is the zero-shot prompt v2 (`tariff_slm.evals.prompts`), rendered by the same chat
template at training and evaluation time.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from tariff_slm.evals.prompts import PROMPT_VERSION, messages, target_json  # noqa: E402

TRAINABLE_KINDS = ("decide", "decide_residual", "decide_unlabelled", "need_info_natural", "need_info_ablated")


def load_items(path: str | Path) -> list[dict]:
    return [json.loads(line) for line in open(path, encoding="utf-8")]


def nested_subset(items: list[dict], n: int | None, seed: int = 7) -> list[dict]:
    """The first n items of one fixed shuffle, so smaller training sets are subsets of larger ones (the data-efficiency
    sweep needs nested subsets)."""
    pool = [it for it in items if it["kind"] in TRAINABLE_KINDS]
    random.Random(seed).shuffle(pool)
    return pool if n is None else pool[:n]


def example(item: dict) -> dict:
    """One training example: the prompt messages (system + user) and the target JSON the model must produce."""
    return {"id": item["id"], "kind": item["kind"], "prompt": messages(item, "zero_shot"), "target": target_json(item),
            "prompt_version": PROMPT_VERSION}
