"""Codex (OpenAI) judges Opus (Anthropic) rationales: grounded in the stated facts, and actually supporting the code.

  uv run python -I scripts/judge_rationales.py --rationales runs/rationales/pilot.jsonl \
      --items data/benchmark_try2/rationale_pool.jsonl --out runs/rationales/pilot.judged.jsonl [--controls 10]

Two yes/no questions per rationale, from a narrow input (product facts, CBP's code with its HTSUS text, the
rationale). `--controls N` adds N broken copies (a real rationale paired with another item's description) that a
working judge must reject; their rejection rate is reported, so the judge is checked before its verdicts are used.
The judge never sees or changes the label; it only decides whether a rationale is kept.
"""
from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tariff_slm.data.schedule import load_schedule  # noqa: E402
from tariff_slm.openset.prompts import dotted  # noqa: E402

SCHEMA = {"type": "object", "additionalProperties": False,
          "required": ["goods_facts", "rules_consistent", "deciding_distinction", "why"],
          "properties": {"goods_facts": {"type": "boolean"}, "rules_consistent": {"type": "boolean"},
                         "deciding_distinction": {"type": "boolean"}, "why": {"type": "string"}}}
CHECKS = ("goods_facts", "rules_consistent", "deciding_distinction")
PROMPT = """You are checking one piece of tariff-classification reasoning. Do not use tools or files; answer from the text.

PRODUCT FACTS (the only facts the reasoning may rely on about the goods):
Product: {product}
Description: {description}

TARIFF LINE THE REASONING MUST SUPPORT: {code} — {line}
NEIGHBOURING LINES:
{siblings}

REASONING TO CHECK:
{rationale}

Answer three yes/no questions:
1. goods_facts: Is every property the reasoning asserts about the goods stated in the PRODUCT FACTS or validly derived
   from them (arithmetic, a definition)? Answer no if it adds a property, or argues a property is absent only
   because it is not mentioned.
2. rules_consistent: Are the schedule claims it makes (headings, notes, thresholds, what a line covers) consistent with
   the tariff line and neighbouring lines shown?
3. deciding_distinction: Does it explain why the facts select THIS tariff line over its neighbours, down to the
   statistical suffix where it claims one?
Return JSON with the three booleans and a one-sentence why."""


def judge(row: dict, it: dict, code: str, sched, model: str, effort: str) -> dict:
    near = [c for c in sched if c[:6] == code[:6] and c != code] or [c for c in sched if c[:4] == code[:4] and c != code]
    sib = "\n".join(f"- {dotted(c)}: {sched[c].text}" for c in near[:10]) or "(none)"
    prompt = PROMPT.format(product=it["product"] or "(not named)", description=it["description"],
                           code=dotted(code), line=sched[code].text, siblings=sib, rationale=row["rationale"])
    with tempfile.TemporaryDirectory() as d:
        sp, op = Path(d) / "schema.json", Path(d) / "out.json"
        sp.write_text(json.dumps(SCHEMA))
        cmd = ["codex", "exec", "--ephemeral", "--skip-git-repo-check", "--ignore-rules", "-s", "read-only",
               "-C", d, "-m", model, "-c", f"model_reasoning_effort={effort}", "--output-schema", str(sp),
               "-o", str(op), prompt]
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return json.loads(op.read_text())
        except Exception as e:  # noqa: BLE001 - a failed judgment keeps nothing
            return {k: False for k in CHECKS} | {"why": f"__error__ {type(e).__name__}"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rationales", required=True)
    ap.add_argument("--items", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--schedule", default=str(ROOT / "data/raw/hts_current.json"))
    ap.add_argument("--kinds", default="hinted,unhinted,direct,repaired")
    ap.add_argument("--controls", type=int, default=0)
    ap.add_argument("--model", default="gpt-6.1-sol")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    sched = load_schedule(a.schedule)
    items = {json.loads(l)["id"]: json.loads(l) for l in open(a.items, encoding="utf-8")}
    rows = [r for r in map(json.loads, open(a.rationales, encoding="utf-8")) if r["kind"] in a.kinds.split(",")]
    jobs = [(r, items[r["id"]], r["code"], False) for r in rows]
    rng = random.Random(3)
    for r in rng.sample(rows, min(a.controls, len(rows))):  # gross control: another product's facts
        other = items[rng.choice([x for x in items if x != r["id"] and items[x]["code"][:4] != r["code"][:4]])]
        jobs.append((r, other, r["code"], "unrelated"))
    for r in rng.sample(rows, min(a.controls, len(rows))):  # close control: the same reasoning, a neighbouring line
        near = [c for c in sched if c[:6] == r["code"][:6] and c != r["code"]] or \
               [c for c in sched if c[:4] == r["code"][:4] and c != r["code"]]
        if near:
            jobs.append((r, items[r["id"]], rng.choice(near), "neighbour"))

    def run(job):
        r, it, code, control = job
        v = judge(r, it, code, sched, a.model, a.effort)
        ok = all(v.get(k) for k in CHECKS)
        return r | {"control": control, "judged_code": code, "judge": v, "keep": ok and not control}

    # Stream verdicts to --out as they finish and resume from it, so an interruption loses nothing.
    done = {}
    if Path(a.out).exists():
        for line in open(a.out, encoding="utf-8"):
            x = json.loads(line)
            if not x["judge"]["why"].startswith("__error__"):
                done[(x["id"], x["control"], x["judged_code"])] = x
    todo = [j for j in jobs if (j[0]["id"], j[3], j[2]) not in done]
    from concurrent.futures import as_completed
    import threading
    lock = threading.Lock()
    with open(a.out, "a", encoding="utf-8") as f, ThreadPoolExecutor(max_workers=a.workers) as ex:
        for fut in as_completed([ex.submit(run, j) for j in todo]):
            r = fut.result()
            with lock:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                f.flush()
                done[(r["id"], r["control"], r["judged_code"])] = r
    out = list(done.values())
    real = [r for r in out if not r["control"]]
    ctl = [r for r in out if r["control"]]
    summary = {"judged": len(real), "errors": sum(r["judge"]["why"].startswith("__error__") for r in out)}
    for k in a.kinds.split(","):
        ks = [r for r in real if r["kind"] == k]
        if ks:
            summary[f"{k}_kept"] = f"{sum(r['keep'] for r in ks)}/{len(ks)}"
    for kind in ("unrelated", "neighbour"):
        cs = [r for r in ctl if r["control"] == kind]
        if cs:
            summary[f"{kind}_controls_rejected"] = f"{sum(not all(r['judge'].get(k) for k in CHECKS) for r in cs)}/{len(cs)}"
    for k in CHECKS:
        summary[f"{k}_yes"] = f"{sum(bool(r['judge'].get(k)) for r in real)}/{len(real)}"
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
