"""Fetch CBP CROSS New York rulings issued after the HF corpus ends (last corpus ruling: NY N351545, 2025-08-01).

  uv run python -I scripts/fetch_cross_recent.py --start 351546 --stop 366000 --out data/raw/cross_recent

Uses the public single-ruling endpoint https://rulings.cbp.gov/api/ruling/N<number> (the search endpoint needs a
reCAPTCHA token per request and is not used). NY ruling numbers are sequential but sparse, so every number in the
range is tried. Polite and bounded: one request at a time, --delay seconds between requests, a hard --stop number,
and an early stop after --max-misses consecutive misses past --tail-from. Resumable: numbers already recorded in
rulings.jsonl or misses.txt are skipped. Raw records are stored unchanged (git-ignored with the rest of data/raw).
"""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

API = "https://rulings.cbp.gov/api/ruling/N{n}"


def fetch(n: int, tries: int = 3) -> dict | None:
    req = urllib.request.Request(API.format(n=n), headers={"User-Agent": "Mozilla/5.0 (research; tariff-slm)",
                                                           "Accept": "application/json"})
    for i in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read().decode("utf-8", "replace")
            if body.startswith("Ruling with number"):
                return None
            return json.loads(body)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(5 * (i + 1))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"N{n}: failed after {tries} tries")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--start", type=int, default=351546)
    ap.add_argument("--stop", type=int, default=366000, help="hard upper bound (exclusive)")
    ap.add_argument("--out", default="data/raw/cross_recent")
    ap.add_argument("--delay", type=float, default=0.25)
    ap.add_argument("--tail-from", type=int, default=361000)
    ap.add_argument("--max-misses", type=int, default=1500)
    ap.add_argument("--known", help="file of N-numbers to skip (one per line), e.g. rulings already in the HF corpus")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    hits_f, miss_f = out / "rulings.jsonl", out / "misses.txt"
    done = set()
    if hits_f.exists():
        done |= {int(json.loads(l)["rulingNumber"][1:]) for l in open(hits_f, encoding="utf-8")}
    if miss_f.exists():
        done |= {int(l) for l in open(miss_f) if l.strip()}
    if a.known:
        done |= {int(l) for l in open(a.known) if l.strip()}
    streak, hits = 0, 0
    with open(hits_f, "a", encoding="utf-8") as hf, open(miss_f, "a") as mf:
        for n in range(a.start, a.stop):
            if n in done:
                continue
            try:
                rec = fetch(n)
            except RuntimeError as e:  # transient failure: leave unrecorded so a rerun retries it
                print(f"error {e}", flush=True)
                time.sleep(30)
                continue
            if rec is None:
                mf.write(f"{n}\n")
                streak += 1
            else:
                hf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                hits, streak = hits + 1, 0
            if n % 100 == 0:
                hf.flush(); mf.flush()
                print(f"N{n} hits={hits} streak={streak}", flush=True)
            if n >= a.tail_from and streak >= a.max_misses:
                print(f"stopping: {streak} consecutive misses at N{n}", flush=True)
                break
            time.sleep(a.delay)
    print(f"done: {hits} new rulings", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
