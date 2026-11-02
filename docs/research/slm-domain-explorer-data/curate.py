"""Synthesis layer for the domain-first SLM explorer.

Reads the research agents' files (TF.json, SH.json, OP.json), keeps their dataset and evidence
entries, and adds the curated layer: scores with reasons, brief-fitted behavior specs, agentic
demos and, for the top three, the smallest experiment. Writes curated.json.

Cybersecurity candidates were removed at Innocent's request on 2026-10-29.

Usage: python3 -I curate.py
"""
import json

AREAS = ["TF", "SH", "OP", "FN"]

RUBRIC = [
    {"key": "data", "label": "Training data", "help": "Size, labels, licence and access of public data with ground truth."},
    {"key": "ft", "label": "Fine-tuning value", "help": "How likely a 1B–4B QLoRA model adds value over prompting plus retrieval."},
    {"key": "business", "label": "Business value", "help": "Who pays for the capability and how much the error costs them."},
    {"key": "agentic", "label": "Agentic demo", "help": "Real tools, APIs and agents the model can sit inside."},
    {"key": "evidence", "label": "Frontier-weakness evidence", "help": "How directly published results show frontier models failing this task."},
    {"key": "fit", "label": "Brief fit", "help": "Passes the prompt-ceiling gate, has a deterministic check and fits about four days."},
]

# Datasets and sources I added or corrected after spot-checking (2026-10-29).
EXTRA_DATASETS = {
    "hts-tariff-classification": [
        {"name": "orlandowhite/hts-cross-rulings (CBP CROSS rulings with full ruling text)",
         "url": "https://huggingface.co/datasets/orlandowhite/hts-cross-rulings", "platform": "HF",
         "size": "54,558 unique rulings (corrected 2026-10-30: the viewer's 80,844 adds a 26,286-row filtered subset to the full file); fields: ruling_id, date, short and full description, hts_code, reasoning, original ruling text",
         "labels": "10-digit HTS code per ruling, plus the ruling's reasoning",
         "license": "No licence tag on the card. Source is CBP rulings, US federal government works; confirm before republishing.",
         "license_verified": False, "access_gate": "none",
         "notes": "Largest public copy found. Rulings date back to the 2000s, so filter to codes still valid in the current HTS revision."},
        {"name": "ATLAS CROSS rulings set (public mirror of flexifyai's dataset)",
         "url": "https://huggingface.co/datasets/Dayanand314Krishna/cross_rulings_hts_dataset_for_tariffs", "platform": "HF",
         "size": "18,654 rows in chat format (card: 18,731 rulings, 2,992 codes, splits 18,254 / 200 / 200)",
         "labels": "HTS code plus a reasoning path, in user/assistant messages",
         "license": "apache-2.0 tag on the mirror card; the original flexifyai repo is no longer public (HF API refused anonymous access on 2026-10-29)",
         "license_verified": False, "access_gate": "none",
         "notes": "Use its 200-item test split to compare directly with the ATLAS paper's numbers."},
        {"name": "USITC HTS REST search (agent tool)", "url": "https://hts.usitc.gov/reststop/search?keyword=injection%20molding%20machine",
         "platform": "Gov", "size": "Live schedule; returns htsno, description, general/special/other duty rates",
         "labels": "Tool, not training data", "license": "US government", "license_verified": False, "access_gate": "none",
         "notes": "Tested 2026-10-29: keyword search returns JSON with duty rates. Keyword matching is loose, so the agent needs its own candidate ranking."},
    ],
    "smiles-reaction-and-name-conversion": [
        {"name": "RDKit (agent tool and validator)", "url": "https://www.rdkit.org/docs/", "platform": "Other",
         "size": "Open-source cheminformatics library", "labels": "Tool: canonicalise SMILES, validity, atom balance",
         "license": "BSD-3-Clause", "license_verified": False, "access_gate": "none",
         "notes": "Canonical-SMILES exact match is the deterministic metric."},
    ],
    "xbrl-us-gaap-tagging": [
        {"name": "SEC EDGAR XBRL APIs (companyfacts, frames)", "url": "https://www.sec.gov/search-filings/edgar-application-programming-interfaces",
         "platform": "Gov", "size": "Every XBRL fact filed since 2009", "labels": "Filed concept per value: fresh ground truth for held-out tests",
         "license": "US government; SEC fair-access rules (declared User-Agent, rate limit)", "license_verified": False, "access_gate": "none",
         "notes": "Lets you build a held-out set from filings newer than any model's training data."},
    ],
}
DROP_DATASET_URLS = {"https://huggingface.co/datasets/flexifyai/cross_rulings_hts_dataset_for_tariffs"}

EXTRA_EVIDENCE = {
    "smiles-reaction-and-name-conversion": {
        "counterevidence": [
            {"source": "Assessing the Chemical Intelligence of LLMs (ChemIQ, arXiv 2505.07735)", "url": "https://arxiv.org/abs/2505.07735",
             "note": "Reasoning models read SMILES far better than 2024 models: o3-mini-high 89% on canonical-SMILES questions; reasoning models 50–57% overall vs 3–7% for non-reasoning models (search summary of the paper, not re-read). GPT-5 reported at 70.2% on ChemIQ (blog summary). The GPT-4 1.6% figure overstates today's gap."},
        ],
        "small_model_evidence": [
            {"source": "BioMatrix (arXiv 2606.22138)", "url": "https://arxiv.org/abs/2606.22138", "year": 2026,
             "finding": "Search summary: a 4B model reaches 77.94% exact match on SMolInstruct forward synthesis, near the 78.7 task-specific state of the art. Not read on the page.", "verified": False},
        ],
    },
}

CURATED = {
    "hts-tariff-classification": {
        "rank": 1, "name": "Tariff Classifier: 10-digit HTS codes from product descriptions", "industry": "Trade and logistics",
        "verdict": "Best overall: fresh, direct evidence that GPT-5-class models miss most 10-digit codes, 54,558 labelled rulings, and a live government API for the agent.",
        "task": "Given a product description and a short list of candidate HTS subheadings from the USITC schedule, pick the one 10-digit code CBP would assign, or ask for the one missing attribute that separates the top two.",
        "why_hard": "The last four digits turn on fine distinctions (knit vs woven, percent by weight, for retail sale, value per unit) applied through the General Rules of Interpretation. ATLAS (2025) measured GPT-5-Thinking at 25.0% fully correct at 10 digits and Gemini 2.5 Pro Thinking at 13.5%, on a 200-ruling test set.",
        "business": "Importers, customs brokers and cross-border e-commerce sellers. A wrong code means a wrong duty rate, penalties under 19 USC 1592 or overpayment, and in 2025–26 tariff swings make the code far more expensive to get wrong. Brokers search CROSS rulings by hand today.",
        "ft_vs_rag": "Retrieval supplies the candidate codes and their legal text; a 4B model cannot memorise 17,000+ schedule lines, so retrieval stays. What fine-tuning adds is the decision pattern from 54,558 past rulings: which attribute decides between near-identical subheadings and when the description is too thin to decide. ATLAS shows fine-tuning lifted a 70B model from 2.1% to 40.0% at 10 digits; no 1B–4B result exists yet.",
        "behavior_spec": "Given a product description and N retrieved candidate subheadings, the model returns one JSON object naming exactly one candidate 10-digit code and the product attribute that rules out the runner-up, or NEED_INFO naming the missing attribute when the description cannot separate the top two. Pass = valid JSON, code from the candidate list, and (when the ruling decides it) exact match to the CBP code.",
        "example_input": "Decorative glass globe displaying an underwater scene with dolphins, incorporated before solidification, resting on a plastic base with illuminated miniature lights, used for indoor decoration. Candidates: 7013.99.10.00, 7013.99.50.00, 9405.50.40.00, 6913.90.50.00.",
        "example_output": "{\"hts10\": \"7013.99.10.00\", \"deciding_attribute\": \"pictorial scene embedded in the glass before solidification\", \"runner_up\": \"9405.50.40.00\", \"why_not_runner_up\": \"lights are subordinate; essential character is the glass article (GRI 3(b))\"}",
        "example_note": "Real row from orlandowhite/hts-cross-rulings (ruling NY I84264, 2002). The candidate list and the JSON reasoning fields are illustrative; build them with the USITC search tool.",
        "agentic_demo": [
            "Intake agent reads a supplier invoice or Shopify listing and extracts product attributes (material, construction, use, value).",
            "Retrieval tool queries the USITC HTS REST API and a local index of CROSS rulings for candidate headings and similar past rulings.",
            "Tariff SLM picks one 10-digit code from the candidates, names the deciding attribute, or returns NEED_INFO with the attribute to ask the supplier for.",
            "Duty tool reads the general, special and Section 301/232 rates for that code and computes landed cost for the shipment.",
            "Compliance agent attaches the closest CROSS ruling as precedent and routes low-confidence or high-duty lines to a licensed broker queue.",
        ],
        "eval": "Deterministic: exact match at 10, 8, 6 and 4 digits against the ruling code, NEED_INFO precision on deliberately thinned descriptions, JSON validity, code-in-candidate-list rate. LLM judge: does the deciding attribute appear in the description and actually separate the two codes. Compare Qwen3 base, tuned, and two frontier models with the same retrieved candidates.",
        "risks": "Code drift: old rulings cite codes that later changed, so filter to codes valid in the current schedule. Contamination: CROSS rulings are public and probably in frontier training data, so test on rulings issued after the models' cutoffs. Retrieval quality caps accuracy: if the right code is not in the candidate list, no model can pick it, so report retrieval recall separately.",
        "feasibility": "Good. Data is clean and already paired; teacher distillation only adds the deciding-attribute rationale, conditioned on the gold code and filtered by exact match. A Qwen3-1.7B QLoRA run on 2–5k examples fits a single A100 in under an hour.",
        "scores": {"data": 5, "ft": 4, "business": 5, "agentic": 5, "evidence": 4, "fit": 4},
        "score_notes": {
            "data": "54,558 public rulings with full text; licence tag missing but the source is US government.",
            "ft": "Same-task evidence that fine-tuning helps (70B, 2.1% → 40%); no small-model result yet.",
            "business": "Tariff exposure is a board-level cost in 2025–26; brokers already pay for classification tools.",
            "agentic": "Live USITC API, duty maths, precedent lookup and a broker hand-off make a real workflow.",
            "evidence": "Direct and recent (GPT-5-Thinking, 2025); a 2026 deterministic pipeline narrows the 6-digit gap.",
            "fit": "Deterministic metric plus a judged rationale; the retrieval step must be identical across arms.",
        },
    },
    "smiles-reaction-and-name-conversion": {
        "rank": 2, "name": "Reaction Product Predictor (SMILES)", "industry": "Chemistry and drug discovery",
        "verdict": "Strongest fine-tuning evidence and the cleanest open data, but reasoning-era frontier models have improved, so the prompt-ceiling gate is a real risk.",
        "task": "Given reactant and reagent SMILES, return the major product as one valid SMILES string.",
        "why_hard": "Exact product prediction needs learned reaction patterns, not facts a document could supply. In LlaSMol (2024) GPT-4 scored 1.6% and Claude 3 Opus 3.7% exact match on forward synthesis, against 63.3% for a fine-tuned 7B model. Reasoning models read SMILES much better than GPT-4 did, and no published GPT-5 or Claude 4-class number for this exact task was found.",
        "business": "Medicinal and process chemists, CROs and electronic lab notebook vendors. Pharma treats structures as core IP, so an on-prem small model that never sends molecules to an external API is a selling point by itself.",
        "ft_vs_rag": "Retrieval can find a similar past reaction, but applying the transformation to new reactants and writing a valid product string is a learned mapping. That is exactly what supervised examples teach and what a document cannot hand over.",
        "behavior_spec": "Given reactant and reagent SMILES, the model returns exactly one RDKit-parsable SMILES for the major product and nothing else. Pass = parses, and canonical SMILES equals the dataset's product.",
        "example_input": "CC(=O)O.OCC>[H+]>",
        "example_output": "CCOC(C)=O",
        "example_note": "Illustrative Fischer esterification in SMolInstruct's forward-synthesis format (reactants > reagents >). Pull real rows from the dataset files.",
        "agentic_demo": [
            "A chemist names target building blocks; a name-to-structure tool (PubChem or OPSIN) converts them to SMILES.",
            "The reaction SLM proposes the product for each candidate reagent set.",
            "RDKit validates each SMILES, checks atom balance and computes properties (molecular weight, logP, rule-of-five).",
            "A planner agent runs the SLM as the one-step model inside a short forward-enumeration loop and ranks routes by property targets.",
            "PubChem lookup flags known compounds and returns names and safety data for the chemist's review.",
        ],
        "eval": "Deterministic: SMILES validity rate and canonical exact match against SMolInstruct's held-out forward-synthesis split; top-k match if sampling several. Compare base Qwen3, tuned Qwen3 and two reasoning frontier models with zero-shot, few-shot and CoT prompts.",
        "risks": "Frontier reasoning models may clear a higher bar than 2024 numbers suggest, which would fail the gate. The brief warns against capability benchmarks, so frame the spec as reliability (always one valid SMILES, never prose) as well as accuracy. Data-efficiency curve may need tens of thousands of examples to show strong accuracy.",
        "feasibility": "Medium. Data needs no teacher at all (labels are the products), which conflicts a little with the brief's distillation framing; a teacher could add short mechanism rationales. Tokenising SMILES on a general tokenizer works but trains slowly.",
        "scores": {"data": 5, "ft": 5, "business": 4, "agentic": 4, "evidence": 3, "fit": 3},
        "score_notes": {
            "data": "3M+ samples, 14 tasks, CC BY 4.0, no gate (HF API checked).",
            "ft": "7B tuned 63.3% vs GPT-4 1.6%; a 4B result near 78% reported in a 2026 preprint (unverified).",
            "business": "High-value users with a real privacy reason to run models on-prem.",
            "agentic": "RDKit and PubChem make the outputs checkable and the loop tangible.",
            "evidence": "Direct but dated (GPT-4, Claude 3); newer reasoning models improved on SMILES reading.",
            "fit": "Perfect deterministic check, but it is a capability task and the gate is uncertain.",
        },
    },
    "xbrl-us-gaap-tagging": {
        "rank": 3, "name": "XBRL Tagger: US-GAAP concepts for numbers in filings", "industry": "Finance and accounting",
        "verdict": "Huge open dataset and an unlimited live held-out source (EDGAR); an earlier review rejected it as knowledge-bound, so it only works if framed as choosing among retrieved candidates.",
        "task": "Given a sentence from a 10-K or 10-Q with one numeric value marked, return the US-GAAP element that value should be tagged with, chosen from retrieved candidates.",
        "why_hard": "Concepts differ by subtle accounting meaning (for example, RevenueFromContractWithCustomer vs Revenues, or amortization of intangibles vs depreciation). FinTagging (2025) measured concept-linking accuracy of 0.18 for GPT-4o and 0.19 for DeepSeek-V3 across the full taxonomy.",
        "business": "Filers, filing agents (Workiva, Toppan Merrill, DFIN), auditors and data vendors. SEC comment letters cite tagging errors, and investors' data feeds inherit them.",
        "ft_vs_rag": "Retrieval narrows 17,000+ concepts to a short list, but choosing among near-synonyms is a pattern learned from millions of filed examples. On FiNER-139's 139 frequent tags a fine-tuned encoder already reaches 82 micro-F1, so the generative SLM must show its value on the rationale and the candidate-choice framing, not raw tag accuracy.",
        "behavior_spec": "Given a sentence, a marked numeric span and up to 10 retrieved US-GAAP candidates, the model returns one JSON object with one candidate element (or NONE when no candidate fits) and the phrase in the sentence that justifies it. Pass = valid JSON, element from the list, and match with the filer's tag.",
        "example_input": "Sentence: 'Amortization expense for intangible assets was $4.2 million for the year ended December 31, 2023.' Marked span: 4.2. Candidates: AmortizationOfIntangibleAssets, Depreciation, DepreciationDepletionAndAmortization, FiniteLivedIntangibleAssetsAccumulatedAmortization.",
        "example_output": "{\"concept\": \"AmortizationOfIntangibleAssets\", \"evidence\": \"Amortization expense for intangible assets\"}",
        "example_note": "Illustrative, in the style of FiNER-139 (token-level tags over 10-K sentences).",
        "agentic_demo": [
            "A filing-review agent pulls a draft or recent 10-Q and splits it into sentences with numeric spans.",
            "A taxonomy retriever proposes candidate US-GAAP elements for each span.",
            "The tagging SLM picks one element or NONE and cites the phrase.",
            "A validator cross-checks against the SEC companyfacts API: same company, same period, same element and value in earlier filings.",
            "Mismatches become a reviewer queue with the suggested fix, the evidence phrase and the precedent filing.",
        ],
        "eval": "Deterministic: micro- and macro-F1 against filer tags on FiNER-139's test split, plus a held-out set built from EDGAR filings newer than the models. LLM judge checks that the cited phrase supports the concept. Same retrieved candidates for every arm.",
        "risks": "Encoders already do well on the 139-tag set, so a reviewer may ask why not BERT. The full-taxonomy gap may be mostly knowledge, which retrieval fixes. Filers' own tags are noisy ground truth.",
        "feasibility": "Good on data (1.1M rows, CC BY-SA 4.0, ShareAlike applies to a republished dataset). Candidate construction from the taxonomy takes a day.",
        "scores": {"data": 5, "ft": 3, "business": 5, "agentic": 4, "evidence": 4, "fit": 3},
        "score_notes": {
            "data": "1.1M labelled sentences, CC BY-SA 4.0, no gate (HF API checked); EDGAR gives endless fresh data.",
            "ft": "Encoders already strong on 139 tags; generative SLM value must come from the candidate-choice framing.",
            "business": "Regulated, recurring, high-volume work with paying vendors.",
            "agentic": "EDGAR companyfacts verification makes a credible review loop.",
            "evidence": "Direct (GPT-4o 0.18 concept linking, 2025), but partly knowledge-bound.",
            "fit": "Deterministic metric; the earlier explorer's rejection is the risk to answer up front.",
        },
    },
    "icd10-coding-from-clinical-text": {
        "rank": 4, "name": "Medical Coder: ICD-10-CM from clinical notes", "industry": "Healthcare revenue cycle",
        "verdict": "Classic SLM case (privacy, volume, documented frontier failures), but MIMIC-IV credentialing takes days and the open alternative is small and Spanish.",
        "task": "Given a discharge summary, return the ICD-10-CM codes it supports, each with the supporting phrase.",
        "why_hard": "Over 70,000 codes with specificity rules (laterality, episode, combination codes). Soroush et al. (NEJM AI, 2024) found GPT-4 at 33.9% exact match on ICD-10-CM code descriptions, and all models below 50%.",
        "business": "Hospitals, coding vendors and payers. Coding drives reimbursement and audit risk, and PHI makes an on-prem small model attractive.",
        "ft_vs_rag": "The code table can be retrieved, but which codes a note supports, at what specificity, follows coding guidelines learned from coded notes.",
        "behavior_spec": "For each note, the model returns JSON listing only codes from the candidate set with a quoted supporting span; it never emits a code without a span. Pass = valid codes, each span present in the note, and F1 against coder labels.",
        "example_input": "Discharge summary excerpt: 'Admitted with acute exacerbation of COPD; type 2 diabetes, well controlled on metformin.'",
        "example_output": "[{\"code\": \"J44.1\", \"span\": \"acute exacerbation of COPD\"}, {\"code\": \"E11.9\", \"span\": \"type 2 diabetes, well controlled\"}]",
        "example_note": "Illustrative.",
        "agentic_demo": [
            "The SLM proposes codes with spans from a note.",
            "A code-table tool validates each code and fetches descriptions and Excludes notes.",
            "A rules tool flags missing specificity and conflicts.",
            "The agent writes a coder query back to the clinician and posts the claim draft.",
        ],
        "eval": "Micro/macro F1 on MIMIC-IV ICD-10 labels (top-50 codes subset for a short project); span-grounding rate.",
        "risks": "PhysioNet credentialing plus CITI training before any data; MIMIC data cannot go to external APIs under its licence, which blocks frontier-model ablation on the real notes.",
        "feasibility": "Poor for this week: access gate and the licence's limits on sending notes to hosted frontier models.",
        "scores": {"data": 2, "ft": 4, "business": 5, "agentic": 4, "evidence": 4, "fit": 2},
        "score_notes": {
            "data": "MIMIC-IV credentialed; CodiEsp is 1,000 Spanish cases.",
            "ft": "Fine-tuned models clearly beat prompted ones in published work, though mostly above 4B.",
            "business": "Large, recurring spend with PHI constraints.",
            "agentic": "Code tables, edits and clinician queries make a real loop.",
            "evidence": "GPT-4 33.9% (2024), on code lookup rather than note coding.",
            "fit": "Access gate and data-use rules clash with the frontier ablation.",
        },
    },
    "patent-cpc-classification": {
        "rank": 5, "name": "Patent Router: CPC subclass from claims", "industry": "Intellectual property",
        "verdict": "Good data and a clear routing use case; evidence says encoders already beat LLMs here, which weakens the generative-SLM story.",
        "task": "Given a patent application's abstract and first claim, return its main CPC subclass and group.",
        "why_hard": "Thousands of groups with fine technical boundaries. IPBench (2025) measured exact CPC accuracy of 3.3% for GPT-4o and 9.5% for DeepSeek-V3, but subclass accuracy of 62–65%.",
        "business": "Patent offices, law firms and IP analytics vendors use it to route applications and scope prior-art searches.",
        "ft_vs_rag": "Scheme definitions are retrievable; which group examiners actually assign is a learned pattern.",
        "behavior_spec": "Model returns one CPC group from the official scheme plus two alternates, as JSON; pass = valid codes and exact match on the main group.",
        "example_input": "Abstract and claim 1 of a lithium-ion cell with a ceramic-coated separator.",
        "example_output": "{\"main\": \"H01M 50/446\", \"alternates\": [\"H01M 10/0525\", \"H01M 50/431\"]}",
        "example_note": "Illustrative.",
        "agentic_demo": ["SLM proposes CPC groups.", "CPC scheme tool confirms and fetches titles.", "Prior-art agent searches patents in those groups.", "Router assigns the art unit and drafts a search report."],
        "eval": "Exact and hierarchical accuracy on HUPD held-out years.",
        "risks": "HUPD licence statements conflict (CC BY-SA vs NC); encoder baselines may beat a generative SLM.",
        "feasibility": "Medium: 125 GB raw data needs subsetting.",
        "scores": {"data": 4, "ft": 3, "business": 4, "agentic": 4, "evidence": 3, "fit": 3},
        "score_notes": {
            "data": "Millions of applications; licence conflict unresolved.",
            "ft": "A 2026 study found encoders beat a fine-tuned 9B LLM.",
            "business": "Routing and prior-art search are paid workflows.",
            "agentic": "Natural search-and-route loop.",
            "evidence": "Exact-group failure is real; subclass level is decent already.",
            "fit": "Deterministic metric; encoder baseline invites the 'why an LLM' question.",
        },
    },
    "log-template-parsing": {
        "rank": 6, "name": "Log Template Parser", "industry": "SRE and observability",
        "verdict": "Excellent open data, but frontier and classic parsers already do well, so the gate is hard to pass.",
        "task": "Given a raw log line, return its event template with every variable masked.",
        "why_hard": "Deciding which tokens are variables needs system-specific conventions. ChatGPT reached PA 84.2 in LLMParser (2023); newer papers report GPT-3.5 near 88 PA on Loghub-2.0.",
        "business": "Observability vendors and platform teams: templates drive alert grouping, cost control and anomaly detection at high volume, where a small local model saves money.",
        "ft_vs_rag": "Retrieving similar lines helps (LILAC); tuning teaches the masking convention consistently.",
        "behavior_spec": "Model returns only the template, with every variable replaced by <*> and constants unchanged. Pass = exact template match with the Loghub-2.0 annotation.",
        "example_input": "081109 203615 148 INFO dfs.DataNode$PacketResponder: PacketResponder 1 for block blk_38865049064139660 terminating",
        "example_output": "PacketResponder <*> for block <*> terminating",
        "example_note": "HDFS line in Loghub style; illustrative.",
        "agentic_demo": ["Collector streams logs.", "SLM templates each new line shape.", "Counter flags new or spiking templates.", "Incident agent pulls related deploys and drafts a summary."],
        "eval": "Grouping accuracy and parsing accuracy on Loghub-2.0's 14 systems.",
        "risks": "Drain and LLM-with-cache parsers are strong baselines; the earlier explorer already covered a similar 'Template Lock' idea.",
        "feasibility": "Good on data; weak on the gate.",
        "scores": {"data": 5, "ft": 3, "business": 4, "agentic": 4, "evidence": 2, "fit": 3},
        "score_notes": {
            "data": "14 systems, millions of annotated lines, CC BY 4.0.",
            "ft": "Small tuned models are competitive, not clearly better.",
            "business": "Real volume and cost pressure.",
            "agentic": "Incident triage loop is natural.",
            "evidence": "Frontier models already score in the high 80s.",
            "fit": "Deterministic metric; plateau likely too high.",
        },
    },
    "maintenance-failure-mode-coding": {
        "rank": 7, "name": "Work-Order Failure-Mode Coder", "industry": "Manufacturing and asset maintenance",
        "verdict": "Strong business story and early evidence that fine-tuning helps, but the labelled data is tiny.",
        "task": "Given a technician's terse work-order note, return the ISO 14224-style failure mode.",
        "why_hard": "Notes are abbreviated shop-floor shorthand ('pmp brg hot, rplcd'). Fine-tuned GPT-3.5 reached F1 0.80 vs 0.46 out of the box (2023).",
        "business": "Plants and utilities use failure codes for reliability analytics; most notes are uncoded.",
        "ft_vs_rag": "Shorthand and code conventions are learned from examples, not looked up.",
        "behavior_spec": "Model returns one failure-mode code from the fixed list; pass = exact match.",
        "example_input": "pump 3 brg running hot, replaced brg",
        "example_output": "Overheating",
        "example_note": "Illustrative.",
        "agentic_demo": ["CMMS export feeds notes.", "SLM codes each note.", "Reliability tool computes failure rates per asset.", "Agent proposes PM schedule changes."],
        "eval": "Accuracy and macro-F1 on FMC-MWO2KG (62-item test).",
        "risks": "Only about 600 labelled items; tests that small cannot separate models by a few points.",
        "feasibility": "Needs heavy teacher-generated data with weak ground truth.",
        "scores": {"data": 2, "ft": 4, "business": 4, "agentic": 4, "evidence": 2, "fit": 3},
        "score_notes": {
            "data": "Hundreds of examples; MaintIE has entities, not failure codes.",
            "ft": "GPT-3.5 tuned 0.80 vs 0.46.",
            "business": "Clear reliability-engineering buyer.",
            "agentic": "CMMS loop is practical.",
            "evidence": "GPT-3.5 only.",
            "fit": "Small test set limits the statistics.",
        },
    },
    "aviation-safety-report-coding": {
        "rank": 8, "name": "Aviation Safety Report Coder (NASA ASRS)", "industry": "Aviation safety",
        "verdict": "Interesting narratives and real taxonomy, but no frontier evidence and unclear bulk access and licence.",
        "task": "Given an ASRS narrative, return the phase of flight and contributing-factor codes.",
        "why_hard": "Multi-label coding of long narratives against an expert taxonomy; no GPT-4-or-newer study was found.",
        "business": "Airlines' safety departments, regulators and MRO safety teams.",
        "ft_vs_rag": "The taxonomy is short; applying it consistently is learned.",
        "behavior_spec": "Model returns JSON with codes only from the ASRS taxonomy; pass = label F1 against analyst codes.",
        "example_input": "Narrative excerpt about a runway incursion during taxi.",
        "example_output": "{\"phase\": \"Taxi\", \"factors\": [\"Human Factors\", \"Airport\"]}",
        "example_note": "Illustrative.",
        "agentic_demo": ["Intake receives a report.", "SLM codes it.", "Validator checks the taxonomy.", "Trend tool updates a safety dashboard."],
        "eval": "Micro/macro F1 per field.",
        "risks": "NASA gives no licence statement; the HF copy lacks factor labels.",
        "feasibility": "Medium; data assembly is the bottleneck.",
        "scores": {"data": 3, "ft": 3, "business": 3, "agentic": 3, "evidence": 1, "fit": 3},
        "score_notes": {
            "data": "47.7k-row HF copy with limited labels.",
            "ft": "Encoders reach 0.75–0.87 per field.",
            "business": "Real but narrow buyer.",
            "agentic": "Dashboard loop is modest.",
            "evidence": "None found for modern frontier models.",
            "fit": "The ablation itself would be the first evidence.",
        },
    },
    "patient-to-trial-eligibility": {
        "rank": 9, "name": "Trial Eligibility Screener", "industry": "Clinical research",
        "verdict": "High value, but GPT-4 already reaches 87% criterion-level accuracy, so the prompt ceiling is too high.",
        "task": "Given a patient summary and one trial criterion, return met / not met / insufficient information with a quote.",
        "why_hard": "Temporal and negated clinical facts; but TrialGPT (2024) shows GPT-4 at 87.3% criterion accuracy, close to experts.",
        "business": "Trial sites and sponsors spend heavily on screening; privacy favours local models.",
        "ft_vs_rag": "Weak case: the frontier baseline is already strong.",
        "behavior_spec": "Model returns one of three labels with a quote from the note; pass = label match and quote present.",
        "example_input": "Patient: 64F, HbA1c 8.1% last month. Criterion: HbA1c between 7% and 10%.",
        "example_output": "{\"label\": \"met\", \"quote\": \"HbA1c 8.1% last month\"}",
        "example_note": "Illustrative.",
        "agentic_demo": ["ClinicalTrials.gov tool finds trials.", "SLM labels each criterion.", "Rules flag missing labs.", "Agent drafts a coordinator review."],
        "eval": "Criterion-level accuracy against TREC/TrialGPT annotations.",
        "risks": "Small annotated sets; strong frontier baseline.",
        "feasibility": "Feasible, but likely fails the gate.",
        "scores": {"data": 2, "ft": 2, "business": 5, "agentic": 4, "evidence": 1, "fit": 2},
        "score_notes": {
            "data": "About 1,000 annotated patient-criterion pairs.",
            "ft": "No small-model advantage shown.",
            "business": "Expensive screening process.",
            "agentic": "ClinicalTrials.gov API makes a good loop.",
            "evidence": "Counterevidence: GPT-4 near expert level.",
            "fit": "Prompt ceiling likely too high.",
        },
    },
    "fomc-stance-hawkish-dovish": {
        "rank": 10, "name": "Fed Stance Classifier (hawkish / dovish / neutral)", "industry": "Finance and accounting",
        "verdict": "Clean finance data and a natural rates-desk workflow, but it is close to sentiment, the only frontier number is GPT-3.5, and prompted small open models already beat the fine-tuned baseline on newer statements.",
        "task": "Given one sentence from an FOMC statement, minutes, speech or press conference, label its monetary-policy stance as hawkish, dovish or neutral.",
        "why_hard": "Stance depends on Fed-specific conventions (\"balance of risks\", \"some further policy firming\"). Shah et al. (ACL 2023) report fine-tuned RoBERTa-large at weighted F1 0.717 against zero-shot GPT-3.5 at 0.587. No 2025-26 frontier result was found.",
        "business": "Rates desks, macro funds and research teams track the Fed's tone across every speech; a local model scores each new sentence within seconds of release.",
        "ft_vs_rag": "Weak: the label is a judgment over a short sentence, so retrieval adds little, and prompting with definitions already goes a long way.",
        "behavior_spec": "Given one FOMC sentence, the model returns exactly one of hawkish, dovish or neutral as JSON with the phrase that decided it. Pass = valid label matching the annotation.",
        "example_input": "The Committee judges that some further policy firming may be appropriate in order to return inflation to 2 percent over time.",
        "example_output": "{\"stance\": \"hawkish\", \"cue\": \"some further policy firming may be appropriate\"}",
        "example_note": "Sentence in the style of a 2023 FOMC statement; the label is illustrative.",
        "agentic_demo": [
            "A watcher pulls a new FOMC statement or Fed speech the minute it is published.",
            "The stance SLM labels every sentence and cites the deciding phrase.",
            "A diff tool compares the stance mix with the previous statement and highlights changed sentences.",
            "A market-data tool pulls the 2-year Treasury yield and fed funds futures from FRED and the desk's feed.",
            "A research agent drafts a one-paragraph note: what changed, how hawkish, how the market moved.",
        ],
        "eval": "Weighted F1 against the gtfintechlab test split (496 sentences), plus a held-out set from 2024-26 statements labelled by hand.",
        "risks": "Close to the generic sentiment tasks the brief warns against. Labels drift with Fed language (a 2026 study saw the RoBERTa baseline fall to 0.43 accuracy on 2003-2025 statements). CC BY-NC licence limits republishing the dataset.",
        "feasibility": "Easy to train (2k rows), hard to pass the prompt-ceiling gate.",
        "scores": {"data": 3, "ft": 2, "business": 3, "agentic": 4, "evidence": 2, "fit": 2},
        "score_notes": {
            "data": "2,480 labelled sentences; CC BY-NC 4.0.",
            "ft": "Prompted Qwen3-4B beat the fine-tuned baseline on newer statements (arXiv 2603.14313).",
            "business": "Real but narrow audience; signal value is contested.",
            "agentic": "FRED and statement diffs make a tidy research loop.",
            "evidence": "Only GPT-3.5 (2023) measured.",
            "fit": "Sentiment-like; plateau likely too high.",
        },
    },
}

EXPERIMENTS = {
    "hts-tariff-classification": {
        "question": "Does a tuned Qwen3-1.7B, given the same retrieved candidates as a frontier model, choose the right 10-digit code more often than the prompted base model, and does any frontier prompt plateau below a reliability bar?",
        "steps": [
            "Build a fixed test set of 200 rulings issued after 2025-01-01 from orlandowhite/hts-cross-rulings (post-cutoff, to limit contamination), keeping only codes valid in the current schedule.",
            "Build a candidate list of 8 codes per item: the gold code, its siblings under the same 6-digit subheading, and the USITC search's top hits. Freeze it, so every arm sees identical retrieval, and log how often the gold code is in the list.",
            "Prompt-ceiling probe: two frontier families (for example Claude and GPT) × zero-shot, few-shot and structured-CoT prompts × the first 60 items. Record 10-digit exact match and NEED_INFO behavior.",
            "Train one QLoRA run of Qwen3-1.7B on 2,000 older rulings with teacher rationales conditioned on the gold code and filtered by exact match (about 30–60 minutes on an A100).",
            "Score base, tuned and the best frontier prompt on all 200 items with the same harness.",
        ],
        "go": "Go if the best frontier prompt stays below about 70% at 10 digits with candidates provided, and the tuned 1.7B gains at least 15 points over its base. Stop if frontier plus candidates already exceeds about 85%.",
        "cost": "About half a day and well under $50 of API and GPU time.",
    },
    "smiles-reaction-and-name-conversion": {
        "question": "Do current reasoning frontier models, with the best of three prompting strategies, still miss most forward-synthesis products, and does a tuned Qwen3-1.7B beat its base at returning one valid, correct SMILES?",
        "steps": [
            "Sample 200 forward-synthesis items from SMolInstruct's test split.",
            "Prompt-ceiling probe on 60 items: two reasoning frontier models × zero-shot, few-shot and CoT. Score RDKit validity and canonical exact match.",
            "Train Qwen3-1.7B with QLoRA on 5,000 training items (1 epoch).",
            "Score base, tuned and best frontier on all 200.",
        ],
        "go": "Go if the best frontier prompt stays below about 50% exact match and the tuned model beats base by 20+ points. Stop if a frontier model already exceeds about 70%.",
        "cost": "About half a day; data needs no teacher.",
    },
    "xbrl-us-gaap-tagging": {
        "question": "With identical retrieved candidates, does a tuned Qwen3-1.7B pick the filer's concept more often than its base, and do frontier models plateau below a bar on the confusable pairs?",
        "steps": [
            "Take 200 FiNER-139 test sentences, focused on the most confusable tag pairs, plus 50 sentences from 2026 EDGAR filings tagged by the filer.",
            "Build 10 candidates per item from the taxonomy (gold plus nearest labels by embedding) and freeze them.",
            "Prompt-ceiling probe on 60 items across two frontier families × three strategies.",
            "Train Qwen3-1.7B with QLoRA on 5,000 training sentences reformatted to the candidate-choice JSON.",
            "Score all arms; also run a fine-tuned SEC-BERT baseline to answer 'why not an encoder'.",
        ],
        "go": "Go if frontier stays below about 75% on confusable pairs and the tuned model beats base by 15+ points while matching the encoder.",
        "cost": "About a day, including candidate construction.",
    },
}

REJECTED = [
    {"name": "Cybersecurity candidates", "reason": "Removed at your request on 2026-10-29."},
    {"name": "IUPAC-to-SMILES name conversion as a standalone task", "reason": "Deterministic tools (OPSIN, PubChem) already convert names; kept only as an agent tool."},
    {"name": "ICD-10 coding trained on MIMIC-III (PLM-ICD style)", "reason": "Same access gate as ICD-10 above, and the published numbers could not be read."},
    {"name": "Log anomaly detection on Loghub labels", "reason": "Not researched in this pass; anomaly labels are sparse and tabular methods are strong baselines."},
    {"name": "Traffic crash narrative coding", "reason": "Surfaced in search but not opened; candidate for a later pass."},
    {"name": "Wind-turbine maintenance log labelling", "reason": "2026 paper surfaced in search but not opened; overlaps the maintenance candidate."},
    {"name": "Merger-agreement deal points (MAUD)", "reason": "Open data (152 agreements, CC BY 4.0), but a 2026 study puts Claude Opus 4.6 and GPT-5.4 within 0.02-0.04 micro F1 of a fine-tuned model on similar contract extraction, and agreements are long."},
    {"name": "TCFD climate-disclosure classification", "reason": "Under source shift, prompted GPT-4o beats the supervised ClimateBERT (macro-F1 0.707 vs 0.648); dataset is CC BY-NC-SA."},
    {"name": "Bank-transaction and merchant-descriptor categorisation", "reason": "High business value, but no real labelled public dataset with LLM numbers was found; public sets are synthetic."},
    {"name": "Numeric claim detection, 8-K item classification, covenant extraction", "reason": "Dataset not public, no frontier head-to-head, or no public labels."},
    {"name": "Predictive maintenance from sensor data", "reason": "Tabular time-series problem; gradient-boosted trees beat a language model."},
]


def main():
    found = {}
    for area in AREAS:
        for c in json.load(open(f"{area}.json", encoding="utf-8"))["candidates"]:
            found[c["id"]] = c
    ideas = []
    for cid, cur in CURATED.items():
        src = found[cid]
        datasets = EXTRA_DATASETS.get(cid, [])[:1] + [d for d in src["datasets"] if d["url"] not in DROP_DATASET_URLS] + EXTRA_DATASETS.get(cid, [])[1:]
        extra = EXTRA_EVIDENCE.get(cid, {})
        idea = dict(cur)
        idea["id"] = cid
        idea["datasets"] = datasets
        idea["frontier_evidence"] = src.get("frontier_evidence", [])
        idea["counterevidence"] = src.get("counterevidence", []) + extra.get("counterevidence", [])
        idea["small_model_evidence"] = src.get("small_model_evidence", []) + extra.get("small_model_evidence", [])
        idea["total"] = sum(cur["scores"].values())
        if cid in EXPERIMENTS:
            idea["experiment"] = EXPERIMENTS[cid]
        ideas.append(idea)
    ideas.sort(key=lambda i: i["rank"])
    out = {
        "meta": {"title": "SLM Domain Explorer", "built": "2026-10-29",
                 "brief": "course-material/2026-10-27-week7-train-your-own-slm-brief.md",
                 "companion": "docs/research/slm-idea-explorer.html (behavior-first ideas, same day)",
                 "caveat": ("<b>Read this first.</b> The Week 7 brief grades a <i>behavior</i>, not a capability: "
                            "&ldquo;This week is not about beating a frontier model,&rdquo; and it warns against chasing capability benchmarks. "
                            "So each candidate is written as a pass/fail behavior spec (choose from retrieved candidates, return one valid answer, "
                            "ask when the input can't decide it) with a deterministic accuracy check underneath. The frontier-weakness numbers come "
                            "from published benchmarks, several of them on older models; your own prompt-ceiling ablation is what proves the gap. "
                            "Cybersecurity candidates were removed at your request."),
                 "footer": ("Sources were read on the live web on 2026-10-29 by research agents and spot-checked (arXiv titles, Hugging Face API "
                            "metadata, the USITC HTS API). Items marked <i>unverified</i> came from search summaries or pages that could not be opened. "
                            "Raw research and rebuild scripts: <code>docs/research/slm-domain-explorer-data/</code>.")},
        "rubric": RUBRIC, "ideas": ideas, "rejected": REJECTED,
    }
    json.dump(out, open("curated.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for i in ideas:
        print(i["rank"], i["total"], i["id"])


if __name__ == "__main__":
    main()
