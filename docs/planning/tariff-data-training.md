# Tariff specialist: data and training plan (proposed)

Status: **proposed** (2026-10-30). A first data-reality check was run; its numbers are marked *Measured* and will
change as cleaning rules are reviewed. Further data work is paused at the concept stage.

## Sources

| Source | Contents | Trust | Licence / terms |
|---|---|---|---|
| HF `orlandowhite/hts-cross-rulings` | 54,558 unique CBP rulings, 2000–2025: `hts_code`, `original_ruling_text`, plus model-written `full_description` and `reasoning` (*Measured*). The viewer's 80,844 adds a 26,286-row filtered subset to the full file. | Code and original text trusted; summaries are inputs, not labels | No card or licence. Publish our derived set with provenance to CBP; don't re-upload the copy |
| ATLAS CROSS set (public mirror `Dayanand314Krishna/…`) | 18,731 rulings, 2,992 codes, 200-item test split | Comparison with the paper | apache-2.0 tag on the mirror; original repo no longer public |
| USITC HTS export | 19,949 ten-digit lines with descriptions and general rates (*Measured*) | Authoritative for codes and rates | US government |
| CBP CROSS (rulings.cbp.gov) | Official rulings | Authoritative | US government; confirm terms before publishing |

## Subset choice: Chapters 61, 62 and 64

*Measured on 2026-10-30:* among all chapters, these hold the most rulings with currently valid codes, and their codes
split on attributes you can name. Footwear averages about 42 ten-digit siblings per 6-digit subheading.

| Step | Count |
|---|---|
| Single-code rulings loaded (any chapter) | 33,144 |
| In Chapters 61, 62, 64 | 9,566 |
| Dropped: code no longer in the schedule | 3,154 |
| Train rulings (2000–2022) | 6,064 |
| Dev rulings (2023) | 146 |
| Test rulings (2024–2025) | 202 |

## Building an example (proposed pipeline; a draft exists in `inno-tariff-slm`)

1. **Filter:** one 10-digit code, valid in today's schedule, in the chosen chapters. Drop descriptions that mention
   HTS, headings or code digits.
2. **Split by date:** train ≤2022, dev 2023, test 2024–2025. Remove any training description that duplicates a dev or
   test one. Test rulings postdate much frontier training data, which limits memorization.
3. **Candidates:** the gold code plus its seven nearest siblings in the schedule tree (same 8-digit, then 6, then 4),
   shuffled with a fixed seed.
4. **Deciding attribute:** the first level where the gold code's schedule path and its nearest sibling's path differ
   (for example "Of cotton" against "Of man-made fibers"), mapped to a dimension by a lexicon. No model is involved.
5. **NEED_INFO cases, without fabricating ambiguity:**
   - *natural:* the gold line names a positive attribute (such as "For women") that the description never states;
   - *ablated:* the attribute words are removed from a decidable dev or test item.

   A residual gold line ("Other") is decided by absence, so it is never NEED_INFO.
6. **Explanations (optional):** a teacher model writes a short rationale conditioned on the gold code. It is kept only
   if its code and attribute match the labels. Labels never come from the teacher.
7. **Leakage and drift checks:** exact-duplicate removal across splits; obsolete codes dropped; ruling IDs kept for
   provenance.

**Open risk:** the attribute lexicon decides dimensions and NEED_INFO labels, so 50 labels need a hand review before
training. The first draft already caught two lexicon bugs ("man-made" read as gender, "pigskin" as "ski").

## Model and training (proposed)

- **Base model:** Qwen3-1.7B Instruct first (fits a 24 GB card); Qwen3-4B if it underfits. Thinking mode off.
- **Method:** QLoRA with Unsloth or TRL, training on responses only, with the same chat template and system prompt at
  training and evaluation.
- **Starting hyperparameters (estimates, not measured):** LoRA rank 16, learning rate 2e-4, 1–2 epochs, sequence
  length about 1,024 tokens.
- **Data-efficiency sweep:** four nested subsets, for example 500, 1,000, 2,000 and 4,000 rulings, all scored on the
  same held-out set.
- **Compute (estimate until measured):** one A100 or H100 on Modal, RunPod or Colab; each 1.7B run is expected to take
  well under an hour at these sizes.
- **Publishing:** the dataset and checkpoint on Hugging Face with pinned commit hashes.
