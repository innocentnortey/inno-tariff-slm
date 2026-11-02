# SLM Domain Explorer: source data

Raw research behind `../slm-domain-explorer.html` and `../slm-domain-research.md` (built 2026-10-29).
Domain-first companion to `../slm-idea-explorer.html` (behavior-first).

- `BRIEF.md`: the shared brief the research agents worked from.
- `TF.json`, `SH.json`, `OP.json`, `FN.json`: each agent's candidates, evidence and rejections (trade/finance/IP, science/health, operations, financial industry). The cybersecurity file was deleted at Innocent's request.
- `curate.py`: the synthesis layer (scores with reasons, brief-fitted specs, agentic demos, top-3 experiments, set-aside list). Writes `curated.json`.
- `template.html` + `build.py`: injects `curated.json` into the page and checks it (scores in range, totals, every dataset has a URL, top three have experiments, no removed cyber topics).

To rebuild after editing scores or text:

```bash
cd "Gauntlet AI/docs/research/slm-domain-explorer-data"
python3 -I curate.py && python3 -I build.py curated.json template.html ../slm-domain-explorer.html
```
