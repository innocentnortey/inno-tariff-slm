# Concept video outline (3–5 minutes)

Screen-record `docs/research/tariff-compliance-vision.html`. Turn on **Present** for larger type. Press `]` to jump
to the next section, and use the arrow keys inside the mock. These are talking points, not a script.

| # | Time | Show | Say |
|---|---|---|---|
| 1 | 0:00–0:25 | Hero | Importers must put a 10-digit tariff code on every product, and they're liable for it. We propose a human-supervised analyst that knows when to ask. Point at the labels: this is a concept, and nothing is trained yet. |
| 2 | 0:25–0:55 | §1 Problem: code ladder and silk split | One attribute moves the duty: 70% silk is 1.2%, other silk is 3.9% (CBP ruling NY N346508). ATLAS: GPT-5-Thinking gets 25% of 10-digit codes right. |
| 3 | 0:55–1:15 | §2 Vision: eight capabilities | The analyst does the reading, lookup and maths; a licensed person decides. The workflow is the product, not a code generator. |
| 4 | 1:15–2:05 | §3 Journey: shrug (steps 1–4, 6), then shoe step 4 | Real rulings, codes and rates; hand-written outputs. Shrug: the last split is gender, and the description says "Woman's". Shoe: the gender is missing, so it asks the supplier instead of guessing. Mention the China additional-duty note on step 6. |
| 5 | 2:05–2:20 | §4 Value | Less research, fewer preventable errors, cost visibility, defensible records. All hypotheses to measure with pilots. |
| 6 | 2:20–2:55 | §5 Why an SLM: spec, pass and fail, comparison | We train one behavior. RAG brings the facts; the decision pattern lives in thousands of rulings. Small means cost, latency, privacy and consistency. |
| 7 | 2:55–3:25 | §6 Data: sources, subset numbers, pipeline | 54,558 rulings profiled; apparel and footwear subset; labels from CBP and the schedule, never from a teacher; NEED_INFO built without inventing ambiguity. |
| 8 | 3:25–3:50 | §7 Architecture: click the specialist, then the duty engine | What each component owns and must never do. Numbers stay in code. |
| 9 | 3:50–4:25 | §8 Evals: ceiling grid, bars, curve, thresholds | Same candidates for every model; prompt ceiling first; baselines measured so far are non-model only; four-checkpoint curve; failure condition. |
| 10 | 4:25–4:50 | §9 Roadmap, §10 Status | Nine stages; this package doesn't yet meet the early-submission evidence bar; next is the prompt-ceiling ablation. |

## Points to state plainly

- **The mock is hand-written.** No model runs on the page.
- **The only measurements are data facts and non-model baselines.**
- **The value claims are hypotheses.**

## Unresolved decisions to mention

- **Base model:** 1.7B or 4B.
- **Frontier families for the ablation:** proposed Anthropic and OpenAI.
- **NEED_INFO label review:** 50 hand checks before training.
- **Dataset publishing terms:** confirm CBP terms.
