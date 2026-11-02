"""QLoRA fine-tuning and evaluation of the tariff specialist on a Modal H100.

  modal run train/modal_app.py --mode predict --adapter v4-rebal-2ep --subheading 6106.10 --description "..."   # live demo
  modal run train/modal_app.py --mode smoke                 # 64 examples, 20 steps, base + tuned on 30 dev items
  modal run train/modal_app.py --mode train --n 0           # full training set (n=0), 1 epoch, then eval on dev
  modal run train/modal_app.py --mode eval --adapter <run>  # evaluate a saved adapter (or --adapter base)
  modal run train/modal_app.py --mode train --n 0 --train-file train_v2.jsonl --name full-v2   # v2 data change
  modal run train/modal_app.py --mode eval --adapter <run> --dev-file test.jsonl --robust-file test_robust.jsonl  # sealed test

Written against transformers 5.x (`dtype`, and `warmup_steps` as a float ratio). Training uses the exact zero-shot prompt v2 the evals use, rendered by the model's chat template with thinking off,
and puts loss on the answer tokens only. Adapters, predictions and summaries go to the `tariff-slm` volume under
/vol/runs/<run>/ and are copied back to the local runs/ folder. Every run records the installed package versions.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import modal

BASE_MODEL = "Qwen/Qwen3-1.7B"
ROOT = Path(__file__).resolve().parents[1]

app = modal.App("tariff-slm")
vol = modal.Volume.from_name("tariff-slm", create_if_missing=True)
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("torch", "transformers", "peft", "bitsandbytes", "accelerate")
    .add_local_dir(ROOT / "data" / "processed", "/root/data")
    .add_local_dir(ROOT / "src", "/root/src")
    .add_local_dir(ROOT / "train", "/root/train")
    .add_local_file(ROOT / "data" / "raw" / "hts_current.json", "/root/hts_current.json")
)

HYPER = {"lora_r": 16, "lora_alpha": 32, "lora_dropout": 0.05, "lr": 2e-4, "epochs": 1, "batch": 8, "grad_accum": 2,
         "max_len": 3072, "warmup_ratio": 0.03, "seed": 7}


def _setup_path():
    import sys
    for p in ("/root/src", "/root/train"):
        if p not in sys.path:
            sys.path.insert(0, p)


def _versions() -> dict:
    import importlib.metadata as md
    return {p: md.version(p) for p in ("torch", "transformers", "peft", "bitsandbytes", "accelerate")}


def _load(adapter_dir: str | None, base_model: str = BASE_MODEL):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    tok = AutoTokenizer.from_pretrained(base_model)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16,
                             bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(base_model, quantization_config=bnb, dtype=torch.bfloat16,
                                                 device_map="auto")
    if adapter_dir:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter_dir)
    return tok, model


def _prompt_text(tok, msgs: list[dict]) -> str:
    return tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False, enable_thinking=False)


def _evaluate(tok, model, items: list[dict], run_dir: Path, tag: str, batch: int = 16) -> dict:
    """Greedy, batched generation with the same prompt as training; scored with the project's deterministic checks."""
    import torch
    from tariff_slm.evals.checks import score, summarise
    from tariff_slm.evals.prompts import messages
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model.eval()
    rows, t0 = [], time.time()
    for i in range(0, len(items), batch):
        chunk = items[i:i + batch]
        texts = [_prompt_text(tok, messages(it, "zero_shot")) for it in chunk]
        enc = tok(texts, return_tensors="pt", padding=True).to(model.device)
        with torch.no_grad():
            out = model.generate(**enc, max_new_tokens=256, do_sample=False, pad_token_id=tok.pad_token_id)
        for it, seq in zip(chunk, out):
            raw = tok.decode(seq[enc["input_ids"].shape[1]:], skip_special_tokens=True)
            rows.append(score(it, raw))
    s = summarise(rows)
    s.update(seconds=round(time.time() - t0, 1), tag=tag,
             by_kind={k: summarise([r for r in rows if r["kind"] == k]) for k in sorted({r["kind"] for r in rows})})
    with open(run_dir / f"predictions-{tag}.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump(s, open(run_dir / f"summary-{tag}.json", "w"), indent=1)
    return s


def _train(examples: list[dict], run_dir: Path, max_steps: int, hyper: dict, base_model: str = BASE_MODEL) -> dict:
    import torch
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import DataCollatorForSeq2Seq, Trainer, TrainingArguments, set_seed
    set_seed(hyper["seed"])
    tok, model = _load(None, base_model)
    tok.padding_side = "right"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    end = "<|im_end|>"

    feats, too_long = [], 0
    for ex in examples:
        p = tok(_prompt_text(tok, ex["prompt"]), add_special_tokens=False)["input_ids"]
        t = tok(ex["target"] + end, add_special_tokens=False)["input_ids"]
        if len(p) + len(t) > hyper["max_len"]:
            too_long += 1
            continue
        feats.append({"input_ids": p + t, "attention_mask": [1] * (len(p) + len(t)), "labels": [-100] * len(p) + t})

    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    model = get_peft_model(model, LoraConfig(
        r=hyper["lora_r"], lora_alpha=hyper["lora_alpha"], lora_dropout=hyper["lora_dropout"], task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]))
    args = TrainingArguments(
        output_dir=str(run_dir / "trainer"), per_device_train_batch_size=hyper["batch"],
        gradient_accumulation_steps=hyper["grad_accum"], learning_rate=hyper["lr"], num_train_epochs=hyper["epochs"],
        max_steps=max_steps if max_steps > 0 else -1, warmup_steps=hyper["warmup_ratio"], lr_scheduler_type="cosine",
        bf16=True, logging_steps=5, save_strategy="no", report_to=[], gradient_checkpointing=True,
        optim="paged_adamw_8bit", seed=hyper["seed"], remove_unused_columns=False)
    trainer = Trainer(model=model, args=args, train_dataset=feats,
                      data_collator=DataCollatorForSeq2Seq(tok, label_pad_token_id=-100, padding=True))
    t0 = time.time()
    result = trainer.train()
    model.save_pretrained(run_dir / "adapter")
    tok.save_pretrained(run_dir / "adapter")
    log = [h for h in trainer.state.log_history if "loss" in h]
    return {"examples": len(feats), "dropped_too_long": too_long, "train_seconds": round(time.time() - t0, 1),
            "train_loss": result.training_loss, "loss_log": log, "steps": trainer.state.global_step}


@app.function(image=image, gpu="H100", volumes={"/vol": vol}, timeout=4 * 3600)
def run(mode: str, n: int = 0, max_steps: int = 0, eval_limit: int = 0, adapter: str = "", name: str = "",
        train_file: str = "train.jsonl", dev_file: str = "dev.jsonl", robust_file: str = "dev_robust.jsonl",
        epochs: int = 1, base_model: str = BASE_MODEL, seed: int = 7) -> dict:
    _setup_path()
    from sft_data import example, load_items, nested_subset
    stamp = time.strftime("%Y%m%d-%H%M%S")
    run_name = name or f"{stamp}-{mode}-n{n or 'all'}"
    run_dir = Path("/vol/runs") / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    hyper = dict(HYPER, epochs=epochs, seed=seed)
    meta = {"run": run_name, "mode": mode, "base_model": base_model, "hyper": hyper, "versions": _versions(),
            "n_requested": n, "max_steps": max_steps, "train_file": train_file, "dev_file": dev_file,
            "robust_file": robust_file}
    dev = load_items(f"/root/data/{dev_file}")
    robust = load_items(f"/root/data/{robust_file}")
    if eval_limit:
        dev, robust = dev[:eval_limit], robust[:eval_limit]

    if mode in ("smoke", "train"):
        train_items = nested_subset(load_items(f"/root/data/{train_file}"), n or None, seed=HYPER["seed"])
        meta["train"] = _train([example(it) for it in train_items], run_dir, max_steps, hyper, base_model)
        vol.commit()
        adapter_dir = str(run_dir / "adapter")
    else:
        adapter_dir = None if adapter in ("", "base") else f"/vol/runs/{adapter}/adapter"

    tok, model = _load(adapter_dir, base_model)
    meta["eval"] = {"tuned" if adapter_dir else "base": {
        "dev": _evaluate(tok, model, dev, run_dir, "dev"), "robust": _evaluate(tok, model, robust, run_dir, "robust")}}
    if mode == "smoke":   # the smoke loop also scores the untuned base on the same items
        del model
        import torch
        torch.cuda.empty_cache()
        btok, bmodel = _load(None)
        meta["eval"]["base"] = {"dev": _evaluate(btok, bmodel, dev, run_dir, "base-dev"),
                                "robust": _evaluate(btok, bmodel, robust, run_dir, "base-robust")}
    json.dump(meta, open(run_dir / "meta.json", "w"), indent=1, default=str)
    vol.commit()
    return meta


@app.function(image=image, gpu="H100", volumes={"/vol": vol}, timeout=1800)
def predict(description: str, subheading: str, adapter: str, base_model: str = BASE_MODEL) -> dict:
    """Live demo: one description, candidates = the closest schedule lines under a subheading, base vs tuned."""
    _setup_path()
    import torch
    from tariff_slm.data.candidates import BM25
    from tariff_slm.data.schedule import load_schedule
    from tariff_slm.evals.checks import parse
    from tariff_slm.evals.prompts import messages
    sched = load_schedule("/root/hts_current.json")
    prefix = subheading.replace(".", "")
    lines = {c: l for c, l in sched.items() if c.startswith(prefix)}
    if not lines:
        return {"error": f"no schedule lines under {subheading}"}
    top = BM25({c: l.text for c, l in lines.items()}).search(description, 8)
    item = {"id": "live", "description": description,
            "candidates": [{"code": sched[c].dotted, "text": sched[c].text} for c in top]}
    out = {"description": description, "candidates": item["candidates"]}
    for label, adir in (("base", None), ("tuned", f"/vol/runs/{adapter}/adapter")):
        tok, model = _load(adir, base_model)
        text = _prompt_text(tok, messages(item, "zero_shot"))
        enc = tok(text, return_tensors="pt").to(model.device)
        with torch.no_grad():
            gen = model.generate(**enc, max_new_tokens=256, do_sample=False)
        raw = tok.decode(gen[0, enc["input_ids"].shape[1]:], skip_special_tokens=True)
        out[label] = {"raw": raw, "parsed": parse(raw)}
        del model
        torch.cuda.empty_cache()
    return out


@app.function(image=image.add_local_file(ROOT / "train" / "hf" / "MODEL_CARD.md", "/root/MODEL_CARD.md"),
              gpu="H100", volumes={"/vol": vol}, timeout=3600, secrets=[modal.Secret.from_name("huggingface")])
def publish(adapter: str, repo_name: str, base_model: str = BASE_MODEL) -> dict:
    """Merge a trained adapter into the bf16 base model and push it, with the model card, to a public HF repo."""
    import os
    import torch
    from huggingface_hub import HfApi
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer
    api = HfApi(token=os.environ["HF_TOKEN"])
    user = api.whoami()["name"]
    repo_id = f"{user}/{repo_name}"
    tok = AutoTokenizer.from_pretrained(base_model)
    model = AutoModelForCausalLM.from_pretrained(base_model, dtype=torch.bfloat16)
    model = PeftModel.from_pretrained(model, f"/vol/runs/{adapter}/adapter").merge_and_unload()
    out = Path("/tmp/merged")
    model.save_pretrained(out, safe_serialization=True)
    tok.save_pretrained(out)
    (out / "README.md").write_text(Path("/root/MODEL_CARD.md").read_text())
    api.create_repo(repo_id, private=False, exist_ok=True)
    info = api.upload_folder(repo_id=repo_id, folder_path=str(out), commit_message=f"Merged adapter {adapter}")
    return {"repo_id": repo_id, "commit": getattr(info, "oid", None) or str(info), "adapter": adapter}


@app.local_entrypoint()
def main(mode: str = "smoke", description: str = "", subheading: str = "", n: int = 0, max_steps: int = 0, eval_limit: int = 0, adapter: str = "", name: str = "",
         train_file: str = "train.jsonl", dev_file: str = "dev.jsonl", robust_file: str = "dev_robust.jsonl",
         epochs: int = 1, base_model: str = BASE_MODEL, seed: int = 7):
    if mode == "publish":
        print(json.dumps(publish.remote(adapter, name or "tariff-specialist-qwen3-1.7b", base_model), indent=1))
        return
    if mode == "predict":
        r = predict.remote(description, subheading, adapter, base_model)
        print(json.dumps({k: r[k] for k in ("description", "candidates") if k in r}, indent=1))
        for label in ("base", "tuned"):
            if label in r:
                print(f"\n=== {label.upper()} ===\n{json.dumps(r[label]['parsed'] or r[label]['raw'], indent=1)}")
        if "error" in r:
            print(r["error"])
        return
    if mode == "smoke":
        n, max_steps, eval_limit = n or 64, max_steps or 20, eval_limit or 30
    meta = run.remote(mode, n, max_steps, eval_limit, adapter, name, train_file, dev_file, robust_file, epochs,
                      base_model, seed)
    out = ROOT / "runs" / "modal" / meta["run"]
    out.mkdir(parents=True, exist_ok=True)
    json.dump(meta, open(out / "meta.json", "w"), indent=1, default=str)
    for k, v in meta["eval"].items():
        for split, s in v.items():
            print(f"{k:5s} {split:6s} n={s['n']} spec_pass={s['spec_pass']} exact10={s['code_exact10_on_select']} "
                  f"need_info_recall={s['need_info_recall']} over_asking={s['over_asking_rate']} "
                  f"valid_json={s['valid_json']}")
    if "train" in meta:
        t = meta["train"]
        print(f"train: {t['examples']} examples, {t['steps']} steps, loss {t['train_loss']:.4f}, {t['train_seconds']} s")
    print(f"versions: {meta['versions']}")
    print(f"local copy: {out}")
