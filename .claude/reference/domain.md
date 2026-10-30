# Domain reference — US tariff classification

> Extracted from: USITC HTS (hts.usitc.gov, export of 2026-10-30), CBP CROSS rulings (rulings.cbp.gov), ATLAS (arXiv 2509.18400), HF `orlandowhite/hts-cross-rulings` (files dated 2026-02-28).
> As of: 2026-10-30, inspected by Claude.
> Authority: the USITC schedule owns codes and rates; CBP rulings own classification decisions; the planning docs own our choices. Correct this extract against them.

| Term | Meaning here |
|---|---|
| HTS / HTSUS | Harmonized Tariff Schedule of the United States. 2-digit chapter → 4-digit heading → 6-digit subheading (international HS) → 8-digit US rate line → 10-digit statistical suffix. |
| CROSS ruling | A CBP binding ruling (`NY …` New York, `HQ …` Headquarters) answering an importer's classification request; our label source. |
| GRI | General Rules of Interpretation; GRI 1 (heading terms and notes) decides most cases, GRI 3(b) essential character for composites. |
| Sibling codes | 10-digit codes under the same 6-digit subheading (or 4-digit heading); our hard negatives. |
| Deciding attribute | The product fact that separates the gold code from its nearest sibling (fiber content, knit vs woven, gender, upper material, value band). |
| NEED_INFO | The specialist's answer when the description lacks the deciding attribute. |
| Candidate recall | Share of items whose gold code is in the retrieved shortlist; measured apart from model accuracy. |

**Source facts (measured 2026-10-30):** the full rulings file has 54,558 unique rulings (2000–2025); 22,540 carry a 10-digit code that is valid in today's schedule (19,949 ten-digit codes). The HF viewer's 80,844 count adds the 26,286-row filtered subset to the full file. The dataset has no card or licence; the `reasoning` and `full_description` fields are model-written summaries, not CBP text — only `hts_code` and `original_ruling_text` are trusted.

**Terms to check before publishing:** CROSS rulings are US government documents (likely public domain; confirm on rulings.cbp.gov). The HF copy has no licence, so publish our own derived dataset with provenance to CBP, not a re-upload of the copy.
