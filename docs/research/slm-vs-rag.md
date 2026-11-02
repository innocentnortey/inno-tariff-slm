# SLM versus RAG: evidence and open questions

Recorded 2026-11-01 from the project discussion and review of the original research. This note clarifies the evidence; it does not change the behavior spec or authorize training.

## Current conclusion

Fine-tuning a small tariff specialist is a hypothesis worth testing. The evidence does not yet establish that a well-built RAG system cannot solve the target behavior, or that a 1.7B–4B model is necessary. Retrieval remains part of the proposed system.

RAG supplies relevant schedule text, notes, and past rulings to a model that can reason over them. Fine-tuning would try to improve the model's choice between close candidates, its use of stated evidence, and its response when a deciding fact is missing. A general model with good retrieval and prompting may already perform these behaviors reliably.

## What the original research supports

The [domain report](slm-domain-research.md) recommends tariffs because of published classification difficulty, available ruling labels, a retrieval source, and a concrete business workflow. It explicitly calls for a prompt-ceiling experiment before committing to fine-tuning.

The [ATLAS paper](https://arxiv.org/html/2509.18400v1), checked during this discussion, reports 25% exact 10-digit accuracy for GPT-5-Thinking and 40% for its fine-tuned LLaMA-3.3-70B on 200 test examples. That is evidence that domain adaptation can help on that benchmark. It is not a controlled demonstration that fine-tuning beats a strong RAG baseline: retrieval augmentation is listed as future work (§3.3). Smaller models are also future work. The paper does not test this project's eight-candidate SELECT/NEED_INFO contract.

The concept page's claims about learned decision patterns, cost, latency, and consistency are hypotheses for this project until measured. Fine-tuning alone does not guarantee deterministic answers or correctness.

## Comparison needed

Use the same held-out products, eight candidates, schedule context, and any retrieved rulings for all decision-model comparisons:

1. A well-prompted general model, using the frontier families and prompting strategies in the evaluation plan.
2. The proposed small model before training.
3. The same small model after training.

Measure behavior-spec pass rate, exact code accuracy, unsupported selections, NEED_INFO recall, over-asking, grounding, cost, and latency. Evaluate realistic retrieval separately: forcing the gold code into a shortlist isolates decision quality but cannot establish end-to-end performance.

The [evaluation plan](../planning/tariff-behavior-and-evals.md) owns acceptance thresholds. If good prompting already meets the behavior bar, narrow or reconsider the training target. A cost or privacy argument may still justify a small deployment, but cost must include hosting and utilization, and privacy does not itself require fine-tuning.

## Real-world interpretation

A matching precedent may make classification straightforward for RAG. A simple numeric threshold may be best checked in code. The stronger training hypothesis concerns unfamiliar products with several plausible candidates, where the model must identify controlling facts and request missing information. Whether training improves that judgment is what the experiment must establish.
