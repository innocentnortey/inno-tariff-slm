"""The training examples must use the evaluation prompt verbatim and targets the scorer accepts."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "train"))
from sft_data import example, nested_subset  # noqa: E402
from tariff_slm.evals.checks import score  # noqa: E402
from tariff_slm.evals.prompts import messages  # noqa: E402

ITEM = {"id": "X1", "kind": "decide", "description": "Women's blouse of 100% cotton knit fabric, short sleeves",
        "candidates": [{"code": "6106.10.00.10", "text": "Blouses > Of cotton > Women's"},
                       {"code": "6106.10.00.20", "text": "Blouses > Of cotton > Girls'"}],
        "gold_code": "6106.10.00.10", "nearest_sibling": "6106.10.00.20", "gold_value": "Women's",
        "expected": {"decision": "SELECT", "code": "6106.10.00.10", "dimension": "gender_age"}}


def test_prompt_is_the_eval_prompt():
    assert example(ITEM)["prompt"] == messages(ITEM, "zero_shot")


def test_target_passes_the_scorer():
    r = score(ITEM, example(ITEM)["target"])
    assert r["spec_pass"] and json.loads(example(ITEM)["target"])["runner_up"] == "6106.10.00.20"


def test_subsets_are_nested():
    items = [dict(ITEM, id=f"X{i}") for i in range(50)]
    assert [x["id"] for x in nested_subset(items, 10)] == [x["id"] for x in nested_subset(items, 30)[:10]]
