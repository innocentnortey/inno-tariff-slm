#!/usr/bin/env python3
"""Drop Codex's narration blocks into the shot-list template, verbatim.

Usage: python3 .demo/build_shotlist.py
Reads docs/delivery/2026-10-30-concept-narration.md (blocks marked `<!-- scene: id -->` between the START/END markers)
and .demo/shotlist.template.yaml (scenes carry `narration: "@@id"`), writes .demo/shotlist.yaml.
"""
import re, sys, pathlib

root = pathlib.Path(__file__).resolve().parent.parent
narr = (root / "docs/delivery/2026-10-30-concept-narration.md").read_text()
body = narr.split("<!-- NARRATION START -->", 1)[1].split("<!-- NARRATION END -->", 1)[0]
blocks = {}
for m in re.finditer(r"<!-- scene: (\w+) -->(.*?)(?=<!-- scene:|\Z)", body, re.S):
    blocks[m.group(1)] = m.group(2).strip("\n").strip()
tmpl = (root / ".demo/shotlist.template.yaml").read_text()

def repl(m):
    indent, sid = m.group(1), m.group(2)
    if sid not in blocks:
        sys.exit(f"no narration block for scene {sid}")
    text = blocks[sid]
    lines = text.split("\n")
    out = [f"{indent}narration: |"]
    out += [(indent + "  " + l) if l.strip() else "" for l in lines]
    return "\n".join(out)

out = re.sub(r'^(\s*)narration: "@@(\w+)"', repl, tmpl, flags=re.M)
(root / ".demo/shotlist.yaml").write_text(out)
words = sum(len(re.findall(r"\b[A-Za-z]+(?:['’-][A-Za-z]+)*\b", t)) for t in blocks.values())
print(f"shotlist.yaml written: {len(blocks)} scenes, {words} narration words, ~{words/150*60:.0f}s at 150 wpm")

# --- inno-tariff-slm adaptation: `at: 0.4F` means 40% of the way through the scene's narration. ---
# Durations come from the measured voice clips once `demo.py voice/render` has run, else 150 words per minute.
import json
timing_path = root / ".demo/build/timing.json"   # written by `demo.py voice`: {scene id: seconds}
durs = {k: float(v) for k, v in json.loads(timing_path.read_text()).items()} if timing_path.exists() else {}
txt = (root / ".demo/shotlist.yaml").read_text()
parts = re.split(r"(?m)^(  - id: )", txt)
out2 = parts[0]
for i in range(1, len(parts), 2):
    chunk = parts[i] + parts[i + 1]
    sid = re.match(r"  - id: (\w+)", chunk).group(1)
    n = len(re.findall(r"\b[A-Za-z]+(?:['’-][A-Za-z]+)*\b", blocks.get(sid, "")))
    dur = durs.get(sid, n / 150 * 60)
    chunk = re.sub(r"at: ([0-9.]+)F", lambda m: f"at: {float(m.group(1)) * dur:.1f}", chunk)
    out2 += chunk
(root / ".demo/shotlist.yaml").write_text(out2)
print("at-fractions resolved from", "measured clips" if durs else "150 wpm estimates")
