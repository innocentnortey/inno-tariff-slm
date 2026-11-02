# Prompt-ceiling ablation

## Changed
Built the ablation: Opus 5.5 and GPT-5.6 Sol (high effort) x 3 strategies on 157 dev + 58 robustness items, Gemini 3.1 Pro judge, parallel and resumable runs. Prompt v2 defines dimensions and the runner-up. Label review round 3 fixed label-side failures and the "Other"-sibling contradiction (decision 5).

## Why
The brief's gate before any fine-tuning.

## Checked
Run 2: 0 API, judge or refusal errors after a resume (OpenRouter credit ran out; Innocent topped up). Best cell 86.0% spec, 87.9% robustness; 25 tests pass.

## Remaining
Absolute reliability bar; judge calibration; GPU choice.
