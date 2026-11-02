"""Build the demo's replay page from recorded runs (no live model on camera). Every answer shown is a saved run:
the two live predict runs of 2026-11-01 (train/modal_app.py --mode predict) and sealed-test predictions."""
import json, re, glob, html
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
L = lambda p: {json.loads(l)['id']: json.loads(l) for l in open(ROOT / p)}
def parse(raw):
    m = re.search(r"\{.*\}", raw or "", re.S)
    try: return json.loads(m.group(0))
    except Exception: return {}
items = L('data/processed/test.jsonl')
tuned = L('runs/modal/test2-v4-rebal-2ep/predictions-dev.jsonl')
base = L('runs/modal/step10-test-base/predictions-dev.jsonl')
opus = L(sorted(glob.glob(str(ROOT / 'runs/prompt-ceiling-20261102-032602/cells/*-clean')))[-1].replace(str(ROOT) + '/', '') + '/predictions.jsonl')
LIVE = [
  {"id": "live1", "title": "Live run 1 — the description says who wears it", "desc": "Women's short sleeve blouse made of 100% cotton knit fabric, loose fitting, crew neckline, extends below the waist",
   "cands": [("6106.10.00.10", "Women's or girls' blouses and shirts, knitted > Of cotton > Women's"), ("6106.10.00.30", "… Of cotton > Girls' > Other"), ("6106.10.00.20", "… Of cotton > Girls' > Imported as parts of playsuits")],
   "base": {"decision": "SELECT", "code": "6106.10.00.10", "deciding_attribute": {"dimension": "gender_age", "value": "Women's"}, "runner_up": None},
   "tuned": {"decision": "SELECT", "code": "6106.10.00.10", "deciding_attribute": {"dimension": "gender_age", "value": "Women's"}, "runner_up": "6106.10.00.20"}},
  {"id": "live2", "title": "Live run 2 — same blouse, the wearer left out", "desc": "Short sleeve blouse made of 100% cotton knit fabric, loose fitting, crew neckline, extends below the waist",
   "cands": [("6106.10.00.10", "… Of cotton > Women's"), ("6106.10.00.30", "… Of cotton > Girls' > Other"), ("6106.10.00.20", "… Of cotton > Girls' > Imported as parts of playsuits")],
   "base": {"decision": "SELECT", "code": "6106.10.00.10", "deciding_attribute": {"dimension": "material", "value": "Of cotton"}, "runner_up": None},
   "tuned": {"decision": "NEED_INFO", "code": None, "deciding_attribute": {"dimension": "gender_age", "value": None}, "runner_up": None}},
]
CASES = [("case1", "NYN340850", "Sealed test — ballet shoes, wearer never stated"), ("case2", "NYN345906", "Sealed test — chest waders, wearer never stated"), ("weak", "NYN349574", "Where it still loses — a flocked rain boot")]
def cut(t, n=230):
    return t if len(t) <= n else t[:n].rsplit(' ', 1)[0].rstrip(',;:') + ' …'
def ans(label, a, cls):
    if not a: a = {}
    dec = a.get('decision', '—'); da = a.get('deciding_attribute') or {}
    badge = 'ask' if dec == 'NEED_INFO' else 'pick'
    body = (f"<b>Asks:</b> missing <i>{html.escape(str(da.get('dimension')))}</i>" if dec == 'NEED_INFO'
            else f"<b>Picks</b> <code>{html.escape(str(a.get('code')))}</code> · cites <i>{html.escape(str(da.get('dimension')))}</i>: " + (f"“{html.escape(str(da.get('value')))}”" if da.get('value') else "<i>no words quoted</i>"))
    return f"<div class='ans {cls}'><span class='who'>{label}</span><span class='badge {badge}'>{'ASKS' if badge=='ask' else 'PICKS'}</span><div>{body}</div></div>"
secs = []
for lv in LIVE:
    c = "".join(f"<li><code>{k}</code> {html.escape(t)}</li>" for k, t in lv['cands'])
    secs.append(f"<section id='{lv['id']}'><h2>{html.escape(lv['title'])}</h2><p class='desc'>“{html.escape(lv['desc'])}”</p><ul class='cands'>{c}</ul><div class='row'>{ans('Base Qwen3-1.7B', lv['base'], 'b')}{ans('Tuned (this project)', lv['tuned'], 't')}</div><p class='src'>Recorded run · train/modal_app.py --mode predict · 2026-11-01</p></section>")
for sid, iid, title in CASES:
    it = items[iid]; gold = it['gold_code']
    c = "".join(f"<li class='{'gold' if x['code']==gold else ''}'><code>{x['code']}</code> {html.escape(x['text'].split(' > ')[-1][:70])}</li>" for x in it['candidates'][:8])
    note = (f"<p class='note'>CBP's code: <code>{gold}</code> ({html.escape(it['gold_node'][:40])}). The description never says who wears them, so the right move is to ask.</p>" if sid != 'weak'
            else f"<p class='note'>CBP's code: <code>{gold}</code> — <i>Other</i> materials. A legal rule about how the leather-flocked surface counts decides it; the model never sees that rule.</p>")
    secs.append(f"<section id='{sid}'><h2>{html.escape(title)}</h2><p class='desc'>“{html.escape(cut(it['description']))}”</p><ul class='cands'>{c}</ul><div class='row three'>{ans('Base Qwen3-1.7B', parse(base[iid]['raw']), 'b')}{ans('Claude Opus 5.5', parse(opus[iid]['raw']), 'o')}{ans('Tuned (this project)', parse(tuned[iid]['raw']), 't')}</div>{note}<p class='src'>Sealed test item {iid} · 2024–2025 CBP ruling · recorded predictions</p></section>")
results = """<section id='results'><h2>Sealed test — 221 items from 2024–2025 rulings</h2><table>
<tr><th></th><th>Base 1.7B</th><th>Tuned 1.7B</th><th>Opus 5.5 (best prompt)</th></tr>
<tr><td>Spec adherence</td><td>6.3%</td><td class='hi'>80.1%</td><td>84.6%</td></tr>
<tr><td>Robustness (60 perturbed)</td><td>10.0%</td><td class='hi'>75.0%</td><td>75.0%</td></tr>
<tr class='star'><td>Asks when the deciding fact is missing</td><td>0%</td><td class='hi big'>84–89%</td><td>73.0%</td></tr>
<tr class='star'><td>Natural missing-fact cases</td><td>—</td><td class='hi big'>11 of 13</td><td>6 of 13</td></tr>
<tr><td>Asks when it shouldn't</td><td>0%</td><td class='hi'>1.6%</td><td>3.3%</td></tr></table>
<p class='src'>80.1% = grader one-command check on the published weights · 84–89% = full-precision and 4-bit runs · docs/evals/step10-head-to-head-2026-11-01.md</p></section>"""
curve = """<section id='curve'><h2>How the asking behavior was learned</h2><div class='bars'>
<div class='bar'><span style='height:61%'></span><b>61%</b><i>v1 · 6% ask examples</i></div>
<div class='bar on'><span style='height:94%'></span><b>94%</b><i>v2 · +678 ask examples</i></div></div>
<p class='desc small'>Same training settings — only the data changed. Then rebalancing toward rare tariff branches plus a second pass lifted dev accuracy to 136 of 157 and 51 of 58 robust, averaged over two seeds, matching the frontier model's dev scores.</p>
<p class='src'>runs/modal/full-n5865-v1, full-n6543-v2, v4-rebal-2ep, v4-rebal-2ep-seed8</p></section>"""
plan = """<section id='plan'><h2>What didn't go as planned — and what it opened up</h2><div class='grid'>
<div class='card'><h3>The plan</h3><p>Show a small model beating frontier models at tariff classification, where research found GPT-5-Thinking right 25% of the time on the full search.</p></div>
<div class='card'><h3>What happened</h3><p>With eight close candidates handed over, the frontier model reads them well: 84.6%. The specialist reaches 80.1% — close, but not ahead on picking the code.</p></div>
<div class='card hi'><h3>What it does better</h3><p>It refuses to guess. When the deciding fact is missing it asks, more reliably than the frontier model, and rarely asks when it shouldn't.</p></div>
<div class='card'><h3>Next</h3><p>The full search the research measured: better retrieval of candidates, then the same specialist deciding — or asking.</p></div></div></section>"""
CSS = """body{margin:0;background:#0f1418;color:#e8eef0;font:20px/1.45 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
section{min-height:820px;box-sizing:border-box;padding:48px 72px}h2{font-size:34px;margin:0 0 14px;color:#fff}
.desc{font-size:23px;color:#cfe3e0;max-width:1300px}.small{font-size:20px}.cands{list-style:none;padding:0;margin:10px 0 18px;columns:2;font-size:17px;color:#9fb3b2}
.cands li{margin:3px 0}.cands li.gold{color:#e8eef0}code{font-family:ui-monospace,Menlo,monospace;color:#5fc2b6}
.row{display:grid;grid-template-columns:1fr 1fr;gap:18px}.row.three{grid-template-columns:1fr 1fr 1fr}
.ans{border:1px solid #2a3940;border-radius:12px;padding:16px 18px;background:#152027;font-size:19px}.ans.t{border-color:#5fc2b6;background:#11272a}
.who{display:block;font-size:14px;letter-spacing:.06em;text-transform:uppercase;color:#9fb3b2;margin-bottom:8px}
.badge{display:inline-block;font-size:13px;font-weight:700;padding:2px 9px;border-radius:999px;margin-bottom:8px}.badge.pick{background:#2a3940;color:#e8eef0}.badge.ask{background:#5fc2b6;color:#0f1418}
.note{font-size:19px;color:#cfe3e0;margin-top:16px}.src{font-size:14px;color:#6f8584;margin-top:16px}
table{border-collapse:collapse;font-size:24px;margin-top:10px}td,th{padding:12px 26px;border-bottom:1px solid #2a3940;text-align:left}th{color:#9fb3b2;font-size:17px}
td.hi{color:#5fc2b6;font-weight:700}td.big{font-size:30px}tr.star td:first-child{color:#fff;font-weight:600}
.bars{display:flex;gap:80px;align-items:flex-end;height:420px;margin:30px 0}.bar{width:220px;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center}
.bar span{display:block;width:100%;background:#2a3940;border-radius:10px 10px 0 0}.bar.on span{background:#5fc2b6}.bar b{font-size:34px;margin-top:10px}.bar i{color:#9fb3b2;font-style:normal;font-size:17px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:18px}.card{border:1px solid #2a3940;border-radius:14px;padding:22px 26px;background:#152027}.card.hi{border-color:#5fc2b6}.card h3{margin:0 0 8px;color:#5fc2b6;font-size:20px;letter-spacing:.04em;text-transform:uppercase}.card p{margin:0;font-size:21px}"""
page = f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>Tariff specialist replay</title><style>{CSS}</style></head><body>{''.join(secs[:2])}{''.join(secs[2:4])}{curve}{secs[4]}{results}{plan}</body></html>"
(ROOT / '.demo/replay/index.html').write_text(page)
print('wrote', len(page), 'bytes;', 'sections:', re.findall(r"<section id='(\w+)'", page))
