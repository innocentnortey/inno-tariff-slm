# Niche domains for a trainable SLM: research report

Researched 2026-10-29 for the Week 7 *Train Your Own Small Language Model* project
(`course-material/2026-10-27-week7-train-your-own-slm-brief.md`). Interactive version:
`docs/research/slm-domain-explorer.html`. The companion explorer from earlier the same day,
`docs/research/slm-idea-explorer.html`, ranks behavior-first ideas; this report is domain-first.
Cybersecurity candidates were removed at your request.

## The answer

I recommend **HTS tariff classification**. The model picks the 10-digit US tariff code for a
product from a retrieved shortlist, or asks for the one missing fact that decides it. It is the
only candidate that has all four things at once:

- **Recent, direct evidence that frontier models fail.** In ATLAS (2025), GPT-5-Thinking got
  25.0% of 10-digit codes fully right, and Gemini 2.5 Pro Thinking got 13.5%.
- **About 54,558 labelled public rulings, each with its full text.**
- **A live government API** that an agent can call for candidates and duty rates.
- **A business problem that 2025–26 tariff swings made expensive.**

The runners-up are **SMILES reaction-product prediction**, which has the strongest fine-tuning
evidence but a shrinking frontier gap, and **XBRL / US-GAAP tagging**, which has the biggest
finance dataset and an unlimited live test source.

One framing point applies to all of them. The brief grades a *behavior*, not a capability:
"This week is not about beating a frontier model." So each candidate is written as a pass/fail
behavior spec with a deterministic accuracy check underneath. For tariffs, the behavior is to
choose one code from the retrieved candidates, name the attribute that rules out the runner-up,
and say `NEED_INFO` when the description can't decide it. The published numbers suggest a gap.
Only your prompt-ceiling ablation proves one.

## Shortlist

Each dimension is scored 1–5, for a total out of 30. The reasons for each score are in the explorer.

| # | Candidate | Industry | Data | FT value | Business | Agentic | Evidence | Brief fit | Total |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Tariff Classifier: 10-digit HTS codes | Trade and logistics | 5 | 4 | 5 | 5 | 4 | 4 | **27** |
| 2 | Reaction Product Predictor (SMILES) | Chemistry and drug discovery | 5 | 5 | 4 | 4 | 3 | 3 | **24** |
| 3 | XBRL Tagger: US-GAAP concepts | Finance and accounting | 5 | 3 | 5 | 4 | 4 | 3 | **24** |
| 4 | Medical Coder: ICD-10-CM | Healthcare revenue cycle | 2 | 4 | 5 | 4 | 4 | 2 | 21 |
| 5 | Patent Router: CPC classification | Intellectual property | 4 | 3 | 4 | 4 | 3 | 3 | 21 |
| 6 | Log Template Parser | SRE and observability | 5 | 3 | 4 | 4 | 2 | 3 | 21 |
| 7 | Work-Order Failure-Mode Coder | Manufacturing and asset maintenance | 2 | 4 | 4 | 4 | 2 | 3 | 19 |
| 8 | Aviation Safety Report Coder (ASRS) | Aviation safety | 3 | 3 | 3 | 3 | 1 | 3 | 16 |
| 9 | Trial Eligibility Screener | Clinical research | 2 | 2 | 5 | 4 | 1 | 2 | 16 |
| 10 | Fed Stance Classifier | Finance and accounting | 3 | 2 | 3 | 4 | 2 | 2 | 16 |

**What the dimensions mean:**

- **Data:** size, labels, license and access.
- **FT value:** how likely a 1B–4B QLoRA model adds value over prompting plus retrieval.
- **Evidence:** how directly published results show frontier models failing at this task.
- **Brief fit:** whether the candidate can pass the prompt-ceiling gate, has a deterministic check and fits about four days.

## Top three in detail

### 1. Tariff Classifier: 10-digit HTS codes

**What it does.** An importer's product description goes in. The model returns the 10-digit
Harmonized Tariff Schedule (HTS) code that US Customs and Border Protection (CBP) would assign.

**Why frontier models struggle.** The last four digits turn on fine distinctions, such as knit
versus woven, percent by weight and value per unit. Classifiers apply those distinctions through
the General Rules of Interpretation. In ATLAS (arXiv 2509.18400, 2025), on a 200-ruling test set,
models got the full 10-digit code right at these rates:

| Model | 10-digit fully correct |
|---|---|
| GPT-5-Thinking | 25.0% |
| Gemini 2.5 Pro Thinking | 13.5% |
| DeepSeek-R1 | 2.5% |

At the 6-digit level, GPT-5-Thinking reached about 55%.

**What fine-tuning adds that retrieval can't.** A 4B model can't memorize 17,000+ schedule lines,
so retrieval stays in the system and supplies the candidate codes. Training adds the decision
pattern from past rulings: which attribute separates near-identical subheadings, and when the
description is too thin to decide. ATLAS fine-tuned a 70B model and moved it from 2.1% to 40.0%
at 10 digits. No 1B–4B result exists yet. Your project would be the first data point.

**Datasets:**

- [`orlandowhite/hts-cross-rulings`](https://huggingface.co/datasets/orlandowhite/hts-cross-rulings) holds
  54,558 unique CBP rulings (the viewer's 80,844 counts the full file plus a 26,286-row filtered subset of it;
  corrected 2026-10-30). Each has a short and full product description, the 10-digit code, the ruling's
  reasoning and the original ruling text. The card has no license tag. The source is US federal
  rulings, so confirm the terms before you republish.
- [ATLAS CROSS set (public mirror)](https://huggingface.co/datasets/Dayanand314Krishna/cross_rulings_hts_dataset_for_tariffs)
  holds 18,654 rows in chat format and carries an Apache-2.0 tag. Its 200-item test split lets you
  compare directly with the paper. The original `flexifyai` repo no longer answers anonymous requests.
- The [USITC HTS REST API](https://hts.usitc.gov/reststop/search?keyword=injection%20molding%20machine)
  is the agent's tool. A test on 2026-10-29 returned codes, descriptions and duty rates as JSON.

**Example.** This is a real ruling (NY I84264). The candidate list and the JSON reasoning fields
are illustrative.

```text
Input:  Decorative glass globe displaying an underwater scene with dolphins, incorporated before
        solidification, resting on a plastic base with illuminated miniature lights, used for
        indoor decoration.
        Candidates: 7013.99.10.00, 7013.99.50.00, 9405.50.40.00, 6913.90.50.00
Output: {"hts10": "7013.99.10.00",
         "deciding_attribute": "pictorial scene embedded in the glass before solidification",
         "runner_up": "9405.50.40.00",
         "why_not_runner_up": "lights are subordinate; essential character is the glass article (GRI 3(b))"}
```

**Agentic demonstration: a landed-cost and compliance agent for a cross-border seller.**

1. An intake agent reads a supplier invoice or product listing and extracts its attributes.
2. A retrieval tool queries the USITC API and a local index of CBP CROSS rulings (the agency's
   searchable rulings database) for candidate codes and similar past rulings.
3. The tariff model picks one code and names the deciding attribute. If the description can't
   decide it, the model returns `NEED_INFO`, and the agent emails the supplier the one question
   that settles it.
4. A duty tool reads the general and special rates for that code and computes landed cost.
5. A compliance agent attaches the closest ruling as precedent and sends low-confidence or
   high-duty lines to a licensed broker's queue.

**Evaluation.** All three model arms, base Qwen3, tuned Qwen3 and two frontier models, get the
same frozen candidate list. The deterministic checks are:

- exact match at 10, 8, 6 and 4 digits;
- `NEED_INFO` precision on deliberately thinned descriptions;
- valid JSON;
- the rate at which the chosen code is in the candidate list.

The LLM judge checks only that the deciding attribute is in the description and actually separates
the two codes.

**Risks:**

- **Code drift.** Old rulings cite codes that later changed, so filter to codes valid in the
  current schedule.
- **Contamination.** CROSS rulings are public and probably in frontier training data, so test on
  rulings issued after the models' cutoffs.
- **Retrieval caps accuracy.** If the right code isn't in the candidate list, no model can pick
  it, so report retrieval recall on its own.

### 2. Reaction Product Predictor (SMILES)

**What it does.** Reactant and reagent SMILES go in, and the major product comes out as one valid
SMILES string. SMILES is the standard one-line text notation for molecules.

**Evidence for a gap:**

- **The 2024 result.** In LlaSMol (arXiv 2402.09391), exact-match accuracy on forward synthesis was:

  | Model | Exact match |
  |---|---|
  | GPT-4 | 1.6% |
  | Claude 3 Opus | 3.7% |
  | Fine-tuned 7B model | 63.3% |

- **A newer small-model result.** A 2026 preprint reports a 4B model at about 78% exact match
  (BioMatrix, arXiv 2606.22138). I read this in a search summary, so it is unverified.

**Counterevidence.** Reasoning models read SMILES much better than GPT-4 did:

- On ChemIQ (arXiv 2505.07735), o3-mini-high answered 89% of canonical-SMILES questions correctly.
- GPT-5 is reported at 70.2% on ChemIQ.
- I found no published GPT-5- or Claude 4-class number for this exact task.

So the gate is the risk to check first.

**Data.** [`osunlp/SMolInstruct`](https://huggingface.co/datasets/osunlp/SMolInstruct) has 3M+
samples across 14 tasks, is licensed CC BY 4.0 and has no access gate. The labels are the products
themselves, so you need no teacher model. That sits a little awkwardly with the brief's
distillation framing, but a teacher could add short mechanism rationales.

**Example (illustrative).** The input `CC(=O)O.OCC>[H+]>` should produce `CCOC(C)=O`.

**Agentic demonstration: a med-chem assistant.**

1. A chemist names building blocks, and PubChem or OPSIN converts them to SMILES.
2. The model proposes products for each reagent set.
3. RDKit validates each SMILES, checks atom balance and computes drug-likeness properties.
4. A planner agent uses the model as the one-step predictor inside a short route search.
5. PubChem flags known compounds.

The privacy angle is real: pharma treats structures as core IP and prefers an on-prem model.

### 3. XBRL Tagger: US-GAAP concepts for numbers in filings

**What it does.** A sentence from a 10-K with one number marked goes in, along with up to ten
retrieved US-GAAP concepts. The model returns the concept the filer should use, or `NONE`, plus
the phrase that justifies it. For example, it separates `AmortizationOfIntangibleAssets` from
`DepreciationDepletionAndAmortization`.

**Evidence.** In FinTagging (arXiv 2505.20650, 2025), concept-linking accuracy across the full
taxonomy was:

| Model | Concept-linking accuracy |
|---|---|
| GPT-4o | 0.18 |
| DeepSeek-V3 | 0.19 |

On FiNER-139's 139 frequent tags, a fine-tuned encoder (SEC-BERT) already reaches 82 micro-F1. So
the generative model must earn its place through the candidate-choice framing and the cited
rationale. Raw tag accuracy won't do it.

**Data:**

- [`nlpaueb/finer-139`](https://huggingface.co/datasets/nlpaueb/finer-139) has 1.1M sentences and
  is licensed CC BY-SA 4.0 with no gate. ShareAlike applies when you republish the dataset.
- The [SEC EDGAR XBRL APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
  give you a held-out set from filings newer than any model's training data.

**Agentic demonstration: a filing-review agent.**

1. The agent splits a draft 10-Q into numeric spans.
2. A taxonomy retriever proposes candidate concepts for each span.
3. The model picks one concept and cites the phrase.
4. A validator cross-checks the choice against the company's earlier filings through the
   `companyfacts` API.
5. Any mismatch becomes a reviewer ticket with the suggested fix.

**Watch out for one thing.** The earlier explorer rejected XBRL tagging as "mostly missing
knowledge." The candidate-choice framing is the answer to that objection: retrieval supplies the
knowledge, and the model learns the choice. Run the SEC-BERT baseline so you can answer
"why not an encoder?"

## The smallest experiment that settles it

Spend about half a day on the top candidate before you commit to it. This plan uses tariffs. The
same shape works for the other two; their versions are in the explorer.

1. **Build a test set.** Take 200 rulings issued after 2025-01-01 from `hts-cross-rulings`.
   Post-cutoff rulings limit contamination. Keep only codes valid in the current schedule.
2. **Freeze retrieval.** Give each item 8 candidate codes: the gold code, its siblings under the
   same 6-digit subheading, and the top USITC search hits. Every arm sees the same list. Log how
   often the gold code is in it.
3. **Run the prompt-ceiling probe.** Use two frontier families × zero-shot, few-shot and
   structured-CoT prompts × the first 60 items. Record 10-digit exact match and `NEED_INFO`
   behavior. The brief requires at least 30 scenarios per cell, so 60 leaves room.
4. **Train once.** Run one QLoRA pass of Qwen3-1.7B on 2,000 older rulings. A teacher writes the
   rationale for each one, conditioned on the gold code, and you keep only rationales whose code
   matches. This takes about 30–60 minutes on an A100.
5. **Score all arms.** Run base, tuned and the best frontier prompt on all 200 items with the same
   harness.

**Decision rule.** Go if the best frontier prompt stays below about 70% at 10 digits with the
candidates provided, and the tuned 1.7B model gains at least 15 points over its base. Stop if a
frontier model with candidates already exceeds about 85%. In that case, the gap is retrieval, not
the decision. The probe costs well under $50 in API and GPU time.

This one run also produces the brief's early artifacts:

- the first rows of the prompt-ceiling table;
- a smoke-tested generate → train → eval loop;
- the first base-vs-tuned numbers;
- one point on the data-efficiency curve.

## How much opportunity is there in finance?

The finance opportunity is real but narrow. It sits in **taxonomy-heavy, high-volume,
regulated tagging and coding**, not in judging the tone of text.

- **The strongest finance candidate is XBRL / US-GAAP tagging (#3).** It has a million labelled
  sentences, frontier concept-linking accuracy below 20%, and SEC verification built in. FinBen
  (NeurIPS 2024) also reports near-zero scores on FNXL, its XBRL numeric-labeling task. That comes
  from the finance agent's reading, and I didn't re-check it.
- **Tariff classification (#1) is trade compliance,** the same buyer as trade finance, customs
  brokerage and landed-cost pricing. If you want a finance story, frame it as landed-cost risk for
  importers and their lenders.
- **Tone and stance tasks are weak.** FOMC hawkish/dovish (#10) has clean data. But the only
  frontier number is GPT-3.5, and a 2026 study found that prompted Qwen3-4B already beats the
  fine-tuned baseline on newer statements.
- **Contract extraction (MAUD) is close to solved.** Claude Opus 4.6 and GPT-5.4 sit within
  0.02–0.04 micro-F1 of a fine-tuned model on similar contract extraction.
- **TCFD climate-disclosure classification flips under source shift.** Prompted GPT-4o beats the
  supervised specialist on text from a new source.
- **Transaction and merchant categorization has no usable public data.** It has high business
  value, but no real labelled public dataset with LLM numbers exists; the public sets are
  synthetic.

**The companion explorer has finance options that fit the brief's behavior framing better.** Its
ideas are reliability behaviors, not taxonomy tasks:

- *Null Means Null*: grounded field extraction for accounts-payable invoices and loan intake.
- *Error Notice Spotter*: catching Reg E error notices in bank customer messages.
- *Hold the Verdict*: holding an expense-compliance decision under pushback.

Those ideas lack labelled public data, so the training set is teacher-generated. The trade-off:

- **Domain-first:** real labels, and a capability gap that might close.
- **Behavior-first:** synthetic labels, and a reliability gap that the brief explicitly rewards.

## What was set aside

- **Cybersecurity candidates:** removed at your request.
- **MAUD:** frontier models are close, as described in the finance section.
- **TCFD:** prompted GPT-4o wins under source shift.
- **Transaction categorization:** no real public data.
- **Numeric claim detection, 8-K item classification and covenant extraction:** the data isn't
  public, no head-to-head result exists, or the labels aren't public.
- **IUPAC-to-SMILES conversion:** deterministic tools already do it.
- **Log anomaly detection, crash-narrative coding and wind-turbine log labelling:** not researched
  in enough depth.
- **Predictive maintenance on sensor data:** tabular models win.

## Evidence limits

- **Old frontier numbers.** Several benchmarks tested GPT-4 or GPT-3.5-class models. Only ATLAS
  (GPT-5-Thinking) and FinTagging (GPT-4o, DeepSeek-V3) are recent, direct evidence for the top
  three.
- **How claims were checked.** Research agents fetched the sources on 2026-10-29. I spot-checked
  every cited arXiv ID (all resolve to the titles given), the Hugging Face dataset metadata and the
  USITC API. Items marked *unverified* in the explorer came from search summaries or pages that
  wouldn't open.
- **Licenses to confirm before you publish your dataset:**
  - `hts-cross-rulings` has no tag.
  - `finer-139` is ShareAlike.
  - FOMC and TCFD are non-commercial.
  - MIMIC needs PhysioNet credentialing.

## Files

- **Explorer:** `docs/research/slm-domain-explorer.html`. Open it with
  `open "/Users/innocentnortey/Desktop/Nortorious-Technologies/Gauntlet AI/docs/research/slm-domain-explorer.html"`.
- **Raw research and the scripts that build the explorer:** `docs/research/slm-domain-explorer-data/`.
  The folder holds `TF.json`, `SH.json`, `OP.json` and `FN.json`, plus `curate.py` for the scores
  and synthesis and `build.py` for the checks and HTML injection.
- **Rebuild:** `cd "docs/research/slm-domain-explorer-data" && python3 -I curate.py && python3 -I build.py curated.json template.html ../slm-domain-explorer.html`.
