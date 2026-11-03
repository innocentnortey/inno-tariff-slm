"""Opus rationales for training rulings. The label is always CBP's code; Opus only writes the reasoning.

  ../bin/with-provider-env -- uv run --extra api --extra bench python -I scripts/make_rationales.py \
      --items data/benchmark_try2/train.jsonl --n 40 --out runs/rationales/pilot.jsonl [--max-cost 5]

For each sampled training item (half where retrieval missed the gold code, half where it was retrieved but not
ranked first), Opus first answers the item exactly as an eval item (`rag` prompt) and gives a short rationale.
  * Its code matches CBP's -> kept as `unhinted`.
  * It does not -> a second call shows CBP's code and the line's HTSUS text and asks for the reasoning from the
    stated facts, including why the listed candidates fail. Kept as `hinted`, pending the Codex judge.
Nothing here can change a label. Output rows: id, kind, rationale, code (CBP's), opus_first_code, cost.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tariff_slm.data.schedule import load_schedule  # noqa: E402
from tariff_slm.evals import backends  # noqa: E402
from tariff_slm.openset.facts import analysis_text  # noqa: E402
from tariff_slm.openset.prompts import dotted, messages, parse  # noqa: E402

MODEL = "anthropic:claude-opus-5-5"
PRICE = (4.0, 20.0)  # USD per million tokens, Claude API list price 2026-10

ASK = ("\n\nAnswer in this form: a line starting `REASONING:` with at most 120 words that names the deciding facts "
       "from the description and why they select this line over the closest alternatives, then the `CODE:` line.")
HINT = ("\n\nCBP's ruling classified these goods under {code} ({text}). Write the reasoning a careful classifier "
        "would give for that line, using only facts stated in the description and the reference material above. "
        "If the line is not among the HTSUS lines listed, say briefly why the closest listed ones do not fit. Do not "
        "mention CBP's ruling, a hint or being told the answer. Answer with a line starting `REASONING:` (at most 120 "
        "words), then `CODE: {code}`.")


DIRECT = ("\n\n--- TEACHER-ONLY EVIDENCE (the classifier being trained will not see this) ---\n"
          "CBP classified these goods under {code}: {text}\n"
          "Neighbouring HTSUS lines:\n{siblings}\n"
          "CBP's own analysis in the ruling:\n{analysis}\n"
          "--- END ---\n\n"
          "Write the explanation a careful classifier would give from the Product and Description above. In 40-70 "
          "words: the decisive stated facts, how they meet this provision, and one competing provision (heading, "
          "subheading or statistical line) and why it does not fit. Use only facts stated in the Product and "
          "Description; never add a property they do not state, and never argue that a property is absent because it "
          "is not mentioned. You may cite legal notes or definitions from the evidence. Do not mention CBP, a ruling, "
          "this evidence or being told the answer. Answer with a line starting `REASONING:` then `CODE: {code}`.")
REPAIR = ("\n\nA reviewer rejected this explanation:\n{rationale}\nObjection: {why}\nRewrite it in 40-70 words: delete "
          "or correct what the objection names, keep only claims supported by the Product and Description and the "
          "schedule, add no new facts. Do not mention CBP, a ruling or the reviewer. Answer with `REASONING:` then "
          "`CODE: {code}`.")


def siblings(code: str, sched) -> str:
    near = [c for c in sched if c[:6] == code[:6] and c != code] or [c for c in sched if c[:4] == code[:4] and c != code]
    return "\n".join(f"- {dotted(c)}: {sched[c].text}" for c in near[:10]) or "(none)"


def call(gen, msgs) -> tuple[str, float]:
    for i in range(3):
        try:
            raw = gen(msgs)
            u = backends.last_usage(gen) or {}
            return raw, ((u.get("input_tokens") or 0) * PRICE[0] + (u.get("output_tokens") or 0) * PRICE[1]) / 1e6
        except Exception as e:  # noqa: BLE001
            err = f"__error__: {type(e).__name__}: {str(e)[:200]}"
            time.sleep(3 * (i + 1))
    return err, 0.0


def rationale(raw: str) -> str:
    m = re.search(r"REASONING:\s*(.+?)(?:\n\s*(?:MISSING:|CODE:)|$)", raw, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--items", required=True)
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--out", required=True)
    ap.add_argument("--schedule", default=str(ROOT / "data/raw/hts_current.json"))
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--max-cost", type=float, default=5.0)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--skip", help="earlier output file: items already done are skipped")
    ap.add_argument("--direct", action="store_true", help="always give CBP's code + evidence packet (one call)")
    ap.add_argument("--rulings", default=str(ROOT / "data/raw/cross_rulings.json"), help="original ruling texts")
    ap.add_argument("--effort", default="high")
    ap.add_argument("--repair", help="judged file: rewrite rejected rationales once, using the judge's objection")
    a = ap.parse_args()
    sched = load_schedule(a.schedule)
    items = [json.loads(l) for l in open(a.items, encoding="utf-8")]
    done = set()
    if a.skip and Path(a.skip).exists():
        done = {json.loads(l)["id"] for l in open(a.skip, encoding="utf-8")}
    items = [it for it in items if it["id"] not in done and it.get("mode", "rag") == "rag"]
    rng = random.Random(a.seed)
    miss = [it for it in items if it["gold_rank"] is None]
    hard = [it for it in items if it["gold_rank"] not in (None, 1)]
    rng.shuffle(miss)
    rng.shuffle(hard)
    pick = miss[: a.n // 2] + hard[: a.n - a.n // 2]
    gen = backends.load(MODEL, max_tokens=4000, effort=a.effort)
    spent = [0.0]
    texts = {}
    if a.direct or a.repair:
        texts = {r["ruling_id"]: r.get("original_ruling_text") or "" for r in json.load(open(a.rulings, encoding="utf-8"))}

    if a.repair:
        by_id = {it["id"]: it for it in items} | {json.loads(l)["id"]: json.loads(l)
                                                  for l in open(a.items, encoding="utf-8")}
        checks = ("goods_facts", "rules_consistent", "deciding_distinction")
        todo = [r for r in map(json.loads, open(a.repair, encoding="utf-8"))
                if not r["control"] and not r["keep"] and r["rationale"]
                and sum(not r["judge"].get(k) for k in checks) == 1  # one failed check: the likeliest to be fixable
                and not r["judge"]["why"].startswith("__error__")][: a.n]

        def fix(r: dict) -> dict | None:
            if spent[0] >= a.max_cost:
                return None
            it = by_id[r["id"]]
            msgs = messages(it, "rag")
            extra = REPAIR.format(rationale=r["rationale"], why=r["judge"]["why"], code=dotted(it["code"]))
            raw, c = call(gen, [msgs[0], {"role": "user", "content": msgs[1]["content"] + extra}])
            spent[0] += c
            ok = parse(raw)["code"] == it["code"] and rationale(raw)
            return {"id": it["id"], "code": it["code"], "gold_retrieved": it["gold_rank"] is not None,
                    "kind": "repaired" if ok else "failed", "rationale": rationale(raw), "cost_usd": c}

        with ThreadPoolExecutor(max_workers=a.workers) as ex:
            rows = [x for x in ex.map(fix, todo) if x]
        with open(a.out, "a", encoding="utf-8") as f:
            for x in rows:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
        print(json.dumps({"repaired": sum(x["kind"] == "repaired" for x in rows), "rows": len(rows),
                          "cost_usd": round(spent[0], 3)}))
        return 0

    def one(it: dict) -> dict | None:
        if spent[0] >= a.max_cost:
            return None
        msgs = messages(it, "rag")
        if a.direct:
            rid = it["ruling_id"]
            extra = DIRECT.format(code=dotted(it["code"]), text=sched[it["code"]].text,
                                  siblings=siblings(it["code"], sched),
                                  analysis=analysis_text(texts.get(rid, "")) or "(not available)")
            raw, c = call(gen, [msgs[0], {"role": "user", "content": msgs[1]["content"] + extra}])
            spent[0] += c
            ok = parse(raw)["code"] == it["code"] and rationale(raw)
            return {"id": it["id"], "code": it["code"], "gold_retrieved": it["gold_rank"] is not None,
                    "opus_first_code": None, "cost_usd": c, "kind": "direct" if ok else "failed",
                    "rationale": rationale(raw)}
        first_msgs = [msgs[0], {"role": "user", "content": msgs[1]["content"] + ASK}]
        raw, c = call(gen, first_msgs)
        spent[0] += c
        first = parse(raw)["code"]
        row = {"id": it["id"], "code": it["code"], "gold_retrieved": it["gold_rank"] is not None,
               "opus_first_code": first, "cost_usd": c}
        if first == it["code"] and rationale(raw):
            return row | {"kind": "unhinted", "rationale": rationale(raw)}
        hint = HINT.format(code=dotted(it["code"]), text=sched[it["code"]].text)
        raw2, c2 = call(gen, [msgs[0], {"role": "user", "content": msgs[1]["content"] + hint}])
        spent[0] += c2
        row["cost_usd"] = c + c2
        ok = parse(raw2)["code"] == it["code"] and rationale(raw2)
        return row | {"kind": "hinted" if ok else "failed", "rationale": rationale(raw2)}

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        rows = [r for r in ex.map(one, pick) if r]
    with open(a.out, "a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    kinds: dict[str, int] = {}
    for r in rows:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    print(json.dumps({"rows": len(rows), "kinds": kinds, "cost_usd": round(spent[0], 3),
                      "unhinted_when_missed": sum(r["kind"] == "unhinted" and not r["gold_retrieved"] for r in rows),
                      "unhinted_when_retrieved": sum(r["kind"] == "unhinted" and r["gold_retrieved"] for r in rows)},
                     indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
