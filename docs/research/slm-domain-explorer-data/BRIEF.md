# Research brief — niche-domain SLM candidates (shared by all research agents)

Assignment context: Gauntlet AI Week 7 "Train Your Own Small Language Model" (full brief:
`/Users/innocentnortey/Desktop/Nortorious-Technologies/Gauntlet AI/course-material/2026-10-27-week7-train-your-own-slm-brief.md`).
QLoRA-fine-tune a 1B–4B open model (Qwen3 0.6B/1.7B/4B, Llama 3.2 1B/3B, Gemma 3, SmolLM3) to do ONE narrow
task reliably. Gate: a prompt-ceiling ablation (≥2 frontier families × zero-shot / few-shot / CoT × ≥30 scenarios)
must show prompting plateaus. Timebox ~4 days, single A100/H100 or 24 GB card.

This pass is DOMAIN-FIRST: find specialised tasks where (1) frontier LLMs are credibly unreliable even with good
prompting and where RAG alone would not fix it (the skill is a learned mapping/pattern, not a missing fact);
(2) labelled public datasets with ground truth exist (Hugging Face, Kaggle, GitHub, Zenodo, government data);
(3) the tuned model can be one component of an agentic workflow (tools, APIs, databases).

## Evidence rules (hard)
- Never fabricate a title, URL, number or licence. Only report a number you read on the fetched page. If you could
  not open a page, set `verified: false`.
- Prefer primary sources: arXiv/ACL/OpenReview, HF dataset cards, official GitHub. Record publication dates and which
  models were tested; say if the result predates GPT-5 / Claude 4.x / Gemini 2.5-class models.
- Classify each frontier-weakness item: `level` = demonstrated | plausible | hypothetical, and `directness` =
  direct (same task) | partial | analogous.
- Actively look for COUNTEREVIDENCE (newer models that fixed it, saturated benchmarks, deterministic tools that solve it).
- Look for SMALL-MODEL evidence: papers where a ≤8B (ideally ≤4B) fine-tuned model matched or beat frontier models.
- Licences: open the card/LICENSE; record the exact licence and any access gate (credentialing, DUA, NC).

## Output
Write ONE JSON file to the path in your task (UTF-8), then reply with a ≤12-line summary. Shape:

```json
{"area": "...", "candidates": [{
  "id": "kebab-case", "name": "", "industry": "",
  "task": "the narrow input→output mapping the SLM learns",
  "why_hard_for_llm": "", "business_value": "who pays and why",
  "datasets": [{"name": "", "url": "", "platform": "HF|Kaggle|GitHub|Zenodo|Gov|Other", "size": "as read", "labels": "", "license": "", "license_verified": true, "access_gate": "none|login|credentialed|DUA", "notes": ""}],
  "frontier_evidence": [{"source": "title", "url": "", "year": 2025, "models_tested": "", "finding": "numbers only if read", "directness": "", "level": "", "verified": true}],
  "counterevidence": [{"source": "", "url": "", "note": ""}],
  "small_model_evidence": [{"source": "", "url": "", "year": 2025, "finding": "", "verified": true}],
  "why_ft_beats_rag": "", "example_input": "", "example_output": "",
  "behavior_spec": "1–2 sentence falsifiable pass/fail spec",
  "agentic_demo": "tools/APIs/agents the SLM works with, step by step",
  "eval": "deterministic metric(s) vs ground truth + how to compare base/tuned/frontier",
  "risks": "", "qlora_feasibility": "fits 4 days? data prep effort?"
}], "rejected": [{"name": "", "reason": ""}]}
```
Keep text fields tight (1–3 sentences). Do not write any other files. Do not read any `.env` file.
