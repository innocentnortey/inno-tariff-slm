# Evaluating a RAG Pipeline — GP-145 to GP-155

GP-26 says retrieval deserves its own evaluation, and GP-38 – GP-55 say how to evaluate any agent. These say how to evaluate **a retrieval-augmented pipeline specifically**: which numbers to compute for the retriever, which for the answer, how to tell which half broke, and the cases a happy-path set never asks.

**Why this file exists.** Ash Tilawat, Slack, 2026-10-27 3:26 PM (`transcripts/2026-10-27-slack-ash-rag-evals.md`):

> *"Its RAG pipeline! Don't forget your RAG evals. Recall, precision, coverage, etc."*

Ash named the metrics, not the method. Everything below is **web research gathered 2026-10-27**, not a Gauntlet lecture, so the source discipline is different from the lecture files: cite the paper or doc, and treat vendor thresholds as rules of thumb, never as program requirements.

## Sources

| Code | Source | Kind |
|---|---|---|
| **W-RC** | Ru et al., *RAGChecker: A Fine-grained Framework for Diagnosing Retrieval-Augmented Generation*, NeurIPS 2024 — [arXiv 2408.08067](https://arxiv.org/abs/2408.08067) | Paper; 8 RAG systems, 4,162 queries, 10 domains; metrics validated against human judgement |
| **W-ALCE** | Gao et al., *Enabling Large Language Models to Generate Text with Citations* (ALCE), EMNLP 2023 — [arXiv 2305.14627](https://arxiv.org/abs/2305.14627) | Paper; citation recall and precision |
| **W-ARES** | Saad-Falcon et al., *ARES: An Automated Evaluation Framework for RAG Systems*, NAACL 2024 — [arXiv 2311.09476](https://arxiv.org/abs/2311.09476) | Paper; judges plus a small human-labelled set |
| **W-UA** | Peng et al., *Unanswerability Evaluation for Retrieval Augmented Generation* (UAEval4RAG), ACL 2025 — [arXiv 2412.12300](https://arxiv.org/abs/2412.12300) | Paper |
| **W-AB** | *AbstentionBench*, 2025 — [arXiv 2506.09038](https://arxiv.org/abs/2506.09038) | Paper; 20 datasets |
| **W-TR** | *Overview of the TREC 2025 RAGTIME Track* — [arXiv 2602.10024](https://arxiv.org/abs/2602.10024); AutoNuggetizer (TREC 2024 RAG) — [arXiv 2504.15068](https://arxiv.org/abs/2504.15068) | Shared-task overviews; nugget coverage |
| **W-RG** | Ragas docs, [context precision](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/context_precision/) and [context recall](https://docs.ragas.io/en/latest/concepts/metrics/available_metrics/context_recall/) | Framework docs (class names change between versions) |
| **W-TL** | TruLens, [the RAG triad](https://www.trulens.org/getting_started/core_concepts/rag_triad) | Framework docs |
| **W-HH** | Hamel Husain, [`evals-skills` → `evaluate-rag`](https://github.com/hamelsmu/evals-skills/blob/main/skills/evaluate-rag/SKILL.md) | Practitioner skill file (read via a summarising fetch, so cited as paraphrase) |
| **W-AN** | Anthropic, [*Introducing Contextual Retrieval*](https://www.anthropic.com/news/contextual-retrieval) | Engineering post; a worked retrieval eval |

Quotes are marked with quotation marks only where the source wording was seen verbatim; everything else is a paraphrase.

---

## The whole idea, in one example

A user asks the guideline assistant: *"What's the A1c target for an adult over 65 with frequent hypoglycaemia?"* The corpus has the answer in two passages: the general adult target, and the older-adult relaxation.

| Step | What we check | Number | Grader |
|---|---|---|---|
| Retrieval | Are both labelled passages in the top 5? | recall@5 = 1/2 = **0.5** | code, against labelled IDs |
| Ranking | How high is the first relevant one? | first relevant at rank 2 → reciprocal rank **0.5** | code |
| Context sent | Of the 5 passages sent, how many were relevant? | precision@5 = 1/5 = **0.2** | code |
| Answer coverage | Did the answer state both required facts (the general target *and* the relaxation for this patient)? | 1 of 2 nuggets → **0.5** | judge, per nugget |
| Faithfulness | Is every claim in the answer supported by a sent passage? | 3 of 3 claims supported → **1.0** | judge, per claim |
| Citations | Does each cited passage support its sentence, and is each citation needed? | recall 1.0, precision 0.5 | judge (NLI), per sentence and per citation |

Reading across: the answer is faithful but incomplete, and the reason is upstream: retrieval missed the older-adult passage. Tuning the prompt would not fix it. That is the diagnosis the numbers exist to give.

---

## GP-145 — Score the retriever, the generator and the answer separately

**Statement.** A single end-to-end correctness score tells you something is wrong but not where. Compute at least three families: **retrieval** (did the right passages come back?), **grounding** (is the answer supported by what came back?) and **answer relevance** (does it address the question?). Then read them together.

| Pattern | Where the fault is |
|---|---|
| Retrieval recall low | The retriever: missing content can't be recovered downstream |
| Recall fine, MRR / nDCG low | Ranking: the right passage arrives too far down |
| Context fine, faithfulness low | The generator: it ignored or contradicted the context |
| Faithful, but answer relevance low | The generator answered from the wrong section |

**Source.** W-TL: the triad scores context relevance, groundedness and answer relevance as separate stages so a failure can be located. W-RC splits every metric into retriever and generator diagnostics. W-HH lists *one end-to-end correctness metric* as an anti-pattern, and gives the diagnosis table above (paraphrased).

**Builds on.** GP-26 (retrieval is its own discipline), GP-38 and GP-52 (grade each step, upstream first).

**In practice.** The eval report has a retrieval table, a generation table and an end-to-end row, never one blended score. A regression is reported with the family it came from.

---

## GP-146 — Read the traces and label each failure retrieval, generation or both, then fix retrieval first

**Statement.** Before choosing metrics, read failing end-to-end traces and, for each one, compare what was retrieved with what the answer needed. Tag the failure *retrieval*, *generation* or *both*. Fix retrieval failures first, because no prompt can use a passage that never arrived.

**Source.** W-HH (paraphrased): start with error analysis on end-to-end traces; inspect what was retrieved against what the model needed; decide whether the problem is retrieval, generation or both; fix retrieval first. Choosing metrics before reading traces is listed as an anti-pattern. W-RC: retriever quality had the largest effect; the stronger retriever beat the weaker one under every one of the four generators.

**Builds on.** GP-44 (error analysis before graders) — this adds the RAG-specific first cut.

**In practice.** The error-analysis table gets a `stage` column (`retrieval` / `generation` / `both`) next to the failure tag. Work is ordered by it.

---

## GP-147 — Build a retrieval eval set: questions mapped to the passages that answer them

**Statement.** Retrieval metrics need labels: each question paired with the passage IDs that answer it. Build the set from three sources:
- **real questions**, mapped by hand;
- **synthetic questions** generated from one passage each, so the label is known by construction;
- **adversarial questions** that use a similar passage's vocabulary but are answerable only from the target.

Filter synthetic questions for realism, and check them against real user queries. Build the set before the corpus drifts, and freeze the corpus, chunker, embedding model and index settings alongside it.

**Source.** W-HH (paraphrased): a retrieval eval set of queries with ground-truth chunks, built manually, synthetically (extract one self-contained fact per chunk, write a question only it answers) or adversarially (find similar distractor chunks by embedding search, write a question that uses their terminology but only the target answers); keep synthetic questions an LLM rates 4–5 for realism; overfitting to synthetic data without validating on real queries is an anti-pattern. W-RG: ID-based context precision and recall take `retrieved_context_ids` and `reference_context_ids`.

**Builds on.** GP-34 – GP-37 (synthetic data), GP-45 (the set is a product artifact with a holdout).

**In practice.** Label relevance at the level that survives re-chunking: source document plus section, with chunk IDs resolved from it at eval time. If labels are raw chunk IDs, every chunking experiment silently invalidates them. *(This last point is our inference, not a cited source.)*

---

## GP-148 — Pick the retrieval metric for the stage and the question type

**Statement.**
- **First-stage retrieval: recall@k.** The generator can ignore a noisy passage; it cannot recover a missing one.
- **Reranker, or what actually reaches the model: precision@k, MRR or nDCG@k.**
- **Single-fact lookups: MRR** (how early the first relevant passage appears).
- **Multi-hop questions: two-hop recall@k** (both required passages in the top k), with misses classed as hop-1 miss, hop-2 miss or ranked beyond k.
- **k matches what the pipeline really sends.** Measuring recall@20 while the prompt gets 5 passages measures a pipeline that doesn't exist.

These metrics compare IDs, so they are deterministic, free and run in CI.

**Source.** W-HH (paraphrased): optimise recall@k for first-pass retrieval; precision@k, MRR or nDCG@k for reranking; MRR for single-fact lookups; two-hop recall@k for multi-hop; k of about 1–2 for factual lookups and 5–10 for synthesis; nDCG can favour weakly relevant passages ranked high over a highly relevant one ranked lower, so pair it with recall. W-RG: context precision *"evaluates the retriever's ability to rank relevant chunks higher than irrelevant ones for a given query"*. W-AN measured retrieval as *"1 minus recall@20"*, the share of relevant passages missing from the top 20.

**Builds on.** GP-41 (cheapest grader first): these need no model at all.

**In practice.** Tag each eval question with its type (fact, synthesis, multi-hop) and report the matching metric per type, not one average across all of them.

---

## GP-149 — Recall and precision pull against each other; report the trade

**Statement.** Retrieving more raises recall and also feeds the generator more noise, which can turn into wrong claims. Don't optimise one number. Sweep k (and reranker depth), report recall, precision and **noise sensitivity** at each setting, and pick the setting from the table.

**Source.** W-RC: as retrievers supplied more complete information (higher claim recall), generators became more susceptible to noise inside the relevant chunks; RAGChecker measures this as *relevant* and *irrelevant noise sensitivity* (incorrect claims traced to relevant vs irrelevant chunks). W-AN: top-20 chunks beat top-10 and top-5 in their tests, but more chunks can distract the model, and reranking more chunks costs latency and money. W-RG lists noise sensitivity as a metric where lower is better.

**Builds on.** GP-51 (one variable per experiment, with cost in the table).

**In practice.** The retrieval experiment table has one row per k: recall@k, precision@k, faithfulness, noise sensitivity, latency, cost.

---

## GP-150 — Faithfulness is checked claim by claim, and the model's own knowledge counts as a failure

**Statement.** Split the answer into atomic claims and check each one against the retrieved passages: supported or not. Faithfulness is supported claims ÷ all claims. In a RAG system a claim that is *true but not in the context* is still a failure, because the system promised answers from its sources. Track it separately as **self-knowledge**, so you can see the model filling gaps.

**Source.** W-RC defines faithfulness as the share of response claims entailed by the retrieved chunks, hallucination as incorrect claims supported by no chunk, and self-knowledge as correct claims found in no chunk. W-TL: groundedness splits the response into claims and looks for evidence for each. W-HH (paraphrased): correct facts from the model's own knowledge still count as hallucinations in RAG; ROUGE, BERTScore and cosine similarity should not be the primary generation metrics; use binary evaluators driven by error analysis.

**Builds on.** GP-47 (judges are binary and narrow): one yes/no per claim, not a 1–10 score per answer.

**In practice.** The faithfulness grader returns a list of `{claim, supported: bool, passage_id}`; the score is computed in code from that list, and the list goes into the trace so a reviewer can see which claim failed.

---

## GP-151 — Citations get two checks: is each sentence supported, and is each citation needed?

**Statement.** **Citation recall:** each sentence is fully supported by the passages it cites. **Citation precision:** each citation contributes; a citation that supports nothing is noise that makes the answer look better-sourced than it is. Both are scored per sentence and per citation, not per answer.

**Source.** W-ALCE: a statement scores 1 for citation recall only if it has at least one citation and the concatenated cited passages entail it (judged by an NLI model); citation precision flags a citation that cannot support the statement on its own and isn't needed by the others. Agreement with human annotation was 85.1% for recall and 77.6% for precision, and the NLI judge cannot detect *partial* support, so it over-credits. Even the best models lacked complete citation support about half the time on ELI5.

**Builds on.** GP-48 (a judge is trusted only after it agrees with humans): ALCE's own numbers show why.

**In practice.** Spot-check the partial-support case by hand: a sentence with two facts, only one of which the cited passage contains. That is where an automatic citation checker says "supported" and is wrong.

---

## GP-152 — Coverage: did the answer state every fact it needed, each one grounded?

**Statement.** For each question, write down the **nuggets**: the atomic facts a complete answer must contain. Coverage is the share of nuggets the answer states *and* supports with a citation. Pair it with a precision-side measure (the share of sentences supported by their citation), because coverage alone rewards stuffing in facts.

**Source.** W-TR: TREC 2025 RAGTIME's primary metrics are *nugget coverage*, "a recall-based metric that reports the proportion of the nuggets that are correctly mentioned and grounded in citations", and *sentence support*, the share of sentences supported by their citation, combined as their harmonic mean. The nugget method dates back to the TREC QA track (2003); TREC 2024 RAG automated it with LLMs (AutoNuggetizer) and found strong run-level agreement with human scoring, with per-question agreement still an open problem. One study in the same literature found high nugget recall can coincide with low groundedness, when the nuggets come from the model's own knowledge. Retrieval-side coverage (sub-topic recall) correlates with answer-side nugget coverage.

**Builds on.** GP-43 (tag every case and read the coverage matrix). That is the *other* meaning of coverage: how well the eval set covers question types, topics and edge cases. Ash's "coverage" could mean either; report both.

**In practice.** Each golden question carries its nugget list, written by a person once. The answer-coverage grader checks each nugget: present, grounded, cited. A nugget present but ungrounded counts as missing.

---

## GP-153 — Test the questions the corpus cannot answer

**Statement.** Include questions with no answer in the corpus: out of scope, a false premise, underspecified, or asking for information newer than the documents. The right behaviour is to abstain or ask, not to answer. Score correct abstention on these **and** wrong refusals on answerable questions, since a system that refuses everything passes the first test and fails the second.

**Source.** W-UA: most RAG evaluation frameworks assess only answerable questions; UAEval4RAG builds knowledge-base-specific unanswerable sets across six categories and found that *no single configuration consistently delivers optimal performance on both answerable and unanswerable requests*. General abstention benchmarks fit RAG poorly because a refusal there may just mean retrieval failed. W-AB: across 20 datasets (unknown answers, underspecification, false premises, subjective or outdated questions), abstention is unsolved, scaling models helps little, and reasoning fine-tuning degraded abstention by 24% on average.

**Builds on.** GP-18 (refusal), GP-85 (fall back to "no supporting evidence").

**In practice.** At least one eval category is unanswerable questions, built from the same corpus so they look plausible. The relevance floor from the retrieval rule is what should trigger the abstention; the eval proves it does.

---

## GP-154 — Judge-based RAG scores are trusted only after human calibration, with the judge pinned

**Statement.** Faithfulness, coverage, citation and context-relevance scores mostly come from a model judge. A judge's score moves when the judge model or prompt changes, and an uncalibrated judge can rank systems wrongly. Label a small human set covering each metric (positive and negative examples), measure the judge's agreement on it, pin the judge model and prompt version, and put a confidence interval on the reported score. Where labelled IDs exist, use the deterministic ID-based metric instead of a judge.

**Source.** W-ARES: a human validation set of about 150 or more labelled examples covering context relevance, answer faithfulness and answer relevance, used with prediction-powered inference to put confidence intervals on judge-based scores. A few hundred human labels were enough across eight tasks. W-RG: Ragas offers ID-based (non-LLM) variants of context precision and recall alongside the LLM-judged ones. W-ALCE: an NLI judge reached 85.1% / 77.6% agreement with humans, so it was usable but not exact.

**Builds on.** GP-48 (a judge earns trust by agreeing with humans), GP-39 (one run is an anecdote).

**In practice.** The report states, for each judged metric: the judge model and version, its agreement rate on the human set, and the score with its interval. Changing the judge is an experiment of its own.

---

## GP-155 — Chunking, k, embeddings and reranking are experiments decided by the retrieval eval

**Statement.** Every retrieval setting is a hypothesis, tested one at a time on the frozen eval set: chunk size and overlap, chunk boundaries, adding the document title and section heading to each chunk, the embedding model, BM25 fusion, the reranker and its depth. Re-index per configuration. Re-run the retrieval and generation evals whenever any of them, or the prompt, changes.

**Source.** W-AN is a worked example: retrieval failure rate (1 − recall@20) went 5.7% (embeddings only) → 3.7% (contextual embeddings) → 2.9% (+ contextual BM25) → 1.9% (+ reranking), a 67% reduction, measured across four domains with their own question sets. The post's advice is *"Always run evals"* on your own data, testing chunking and the number of retrieved chunks. W-HH (paraphrased): treat chunk size and overlap as hyperparameters, re-index per configuration, grid-search chunking before tuning generation, and prepend document titles and section headings to each chunk.

**Builds on.** GP-27 (let evals decide the rung), GP-28 (retrieval defaults), GP-51 (one variable per experiment).

**In practice.** The GP-28 defaults (~500-token recursive chunks, cosine, top-k) are the baseline row, not the answer. Each later row changes one setting and reports the retrieval and generation numbers next to cost and latency.

---

## Thresholds you will see quoted

Practitioner blogs suggest numbers such as precision@5 ≥ 0.7 for a narrow knowledge base or context precision above 80%. **None of them come from the papers above.** Set thresholds from your own baseline, before the first gated run (GP-50), and write down where each came from.

## Tools

| Tool | What it gives | Note |
|---|---|---|
| Ragas | Context precision / recall (LLM, string and ID-based), faithfulness, response relevancy, noise sensitivity, context entity recall | Class names change across versions; check the installed version's docs |
| RAGChecker (`pip install ragchecker`) | Claim-level retriever and generator diagnostics (claim recall, context utilisation, noise sensitivity, hallucination, self-knowledge, faithfulness) | Has a LlamaIndex integration |
| TruLens | The RAG triad as feedback functions on traces | Reference-free: needs no labelled answers |
| ARES (`pip install ares-ai`) | Fine-tuned judges plus confidence intervals from a human set | Heavier setup |
| Your own code | recall@k, precision@k, MRR, nDCG over labelled IDs | A few lines each; deterministic, the first thing to build |
