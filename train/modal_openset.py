"""Benchmark v2 on a Modal H100: evaluate the small model (base or LoRA-tuned) and train LoRA adapters.

  modal run train/modal_openset.py --mode eval --adapter base --items dev.jsonl --prompt-mode rag
  modal run train/modal_openset.py --mode eval --adapter base --items atlas_test.jsonl --prompt-mode atlas
  modal run train/modal_openset.py --mode train --train-file train.jsonl --n 4000 --name pilot-n4000
  modal run train/modal_openset.py --mode eval --adapter pilot-n4000 --items dev.jsonl --prompt-mode rag

Same prompts (`tariff_slm.openset.prompts`) and scorer (`tariff_slm.openset.scoring`) as the API runs. bf16 LoRA on
all linear layers; loss on the answer tokens only; greedy decoding. Training items carry the same retrieval context
format as evaluation items (built leave-one-out by scripts/build_openset.py). Runs go to the `tariff-slm` volume under
/vol/openset/<run>/ and summaries plus predictions are copied to runs/openset-modal/<run>/.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import modal

BASE_MODEL = "Qwen/Qwen3-4B-Instruct-2507"
BASE_REVISION = "cdbee75f17c01a7cc42f958dc650907174af0554"
ROOT = Path(__file__).resolve().parents[1]

app = modal.App("tariff-slm-openset")
vol = modal.Volume.from_name("tariff-slm", create_if_missing=True)
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("torch==2.9.0", "transformers==4.57.1", "peft==0.17.1", "accelerate==1.11.0", "scikit-learn")
    .env({"PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"})
    .add_local_dir(ROOT / "data" / "benchmark", "/root/data", ignore=["*_records.jsonl", "atlas_test_matches.jsonl"])
    .add_local_dir(ROOT / "data" / "benchmark_try2", "/root/data/try2", ignore=["*_records.jsonl", "dev.jsonl",
                                                                              "test.jsonl", "atlas_test.jsonl"])
    .add_local_dir(ROOT / "data" / "benchmark_try3", "/root/data/try3", ignore=["train.jsonl"])
    .add_local_dir(ROOT / "src", "/root/src")
    .add_local_file(ROOT / "data" / "raw" / "hts_current.json", "/root/hts_current.json")
)

HYPER = {"lora_r": 16, "lora_alpha": 32, "lora_dropout": 0.05, "lr": 2e-4, "epochs": 1, "batch": 8, "grad_accum": 2,
         "max_len": 4096, "warmup_ratio": 0.03, "seed": 7}


def _versions() -> dict:
    import importlib.metadata as md
    return {p: md.version(p) for p in ("torch", "transformers", "peft", "accelerate")}


def _load(adapter_dir: str | None):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(BASE_MODEL, revision=BASE_REVISION)
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, revision=BASE_REVISION, torch_dtype=torch.bfloat16,
                                                 device_map="cuda", attn_implementation="sdpa")
    if adapter_dir:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter_dir)
    return tok, model


def _evaluate(tok, model, items: list[dict], mode: str, run_dir: Path, tag: str, max_new: int, batch: int = 16,
              prefill: str = "") -> dict:
    """`prefill`: text the answer starts with (e.g. "REASONING:" for a model trained to reason before the code)."""
    import sys
    import torch
    sys.path.insert(0, "/root/src")
    from tariff_slm.data.schedule import load_schedule
    from tariff_slm.openset.prompts import messages, parse
    from tariff_slm.openset.scoring import score_row, summarise
    valid = set(load_schedule("/root/hts_current.json"))
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model.eval()
    rows, t0 = [], time.time()
    order = sorted(range(len(items)), key=lambda i: -len(json.dumps(items[i])))  # similar lengths per batch
    out_rows: dict[int, dict] = {}
    for s in range(0, len(order), batch):
        idx = order[s:s + batch]
        texts = [tok.apply_chat_template(messages(items[i], mode), add_generation_prompt=True, tokenize=False) + prefill
                 for i in idx]
        enc = tok(texts, return_tensors="pt", padding=True).to(model.device)
        tb = time.time()
        with torch.no_grad():
            gen = model.generate(**enc, max_new_tokens=max_new, do_sample=False, pad_token_id=tok.pad_token_id)
        dt = (time.time() - tb) / len(idx)
        for i, seq in zip(idx, gen):
            raw = prefill + tok.decode(seq[enc["input_ids"].shape[1]:], skip_special_tokens=True)
            r = score_row(items[i], parse(raw), valid)
            r.update(raw=raw, latency_s=round(dt, 3), prompt_tokens=int(enc["attention_mask"][idx.index(i)].sum()))
            out_rows[i] = r
    rows = [out_rows[i] for i in range(len(items))]
    s = summarise(rows)
    s.update(seconds=round(time.time() - t0, 1), tag=tag, mode=mode, n_items=len(items),
             avg_prompt_tokens=round(sum(r["prompt_tokens"] for r in rows) / len(rows), 1))
    with open(run_dir / f"predictions-{tag}.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump(s, open(run_dir / f"summary-{tag}.json", "w"), indent=1)
    return s


def _train(items: list[dict], run_dir: Path, hyper: dict, max_steps: int, init_adapter: str = "") -> dict:
    import sys
    import torch
    sys.path.insert(0, "/root/src")
    from peft import LoraConfig, get_peft_model
    from transformers import DataCollatorForSeq2Seq, Trainer, TrainerCallback, TrainingArguments, set_seed
    from tariff_slm.openset.prompts import messages, target
    set_seed(hyper["seed"])
    tok, model = _load(None)
    tok.padding_side = "right"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    end = "<|im_end|>"
    feats, too_long = [], 0
    for it in items:
        p = tok(tok.apply_chat_template(messages(it, it.get("mode", "rag")), add_generation_prompt=True, tokenize=False),
                add_special_tokens=False)["input_ids"]
        t = tok(target(it) + end, add_special_tokens=False)["input_ids"]
        if len(p) + len(t) > hyper["max_len"]:
            too_long += 1
            continue
        feats.append({"input_ids": p + t, "attention_mask": [1] * (len(p) + len(t)), "labels": [-100] * len(p) + t})
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()
    if init_adapter:  # continue an earlier adapter's weights (fresh optimizer and schedule)
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, f"/vol/openset/{init_adapter}/adapter", is_trainable=True)
    else:
        model = get_peft_model(model, LoraConfig(
            r=hyper["lora_r"], lora_alpha=hyper["lora_alpha"], lora_dropout=hyper["lora_dropout"],
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]))
    args = TrainingArguments(
        output_dir=str(run_dir / "trainer"), per_device_train_batch_size=hyper["batch"],
        gradient_accumulation_steps=hyper["grad_accum"], learning_rate=hyper["lr"], num_train_epochs=hyper["epochs"],
        max_steps=max_steps if max_steps > 0 else -1, warmup_ratio=hyper["warmup_ratio"], lr_scheduler_type="cosine",
        bf16=True, logging_steps=10, save_strategy="steps", save_steps=150, save_total_limit=1, report_to=[],
        group_by_length=True, seed=hyper["seed"], remove_unused_columns=False)
    trainer = Trainer(model=model, args=args, train_dataset=feats,
                      data_collator=DataCollatorForSeq2Seq(tok, label_pad_token_id=-100, padding=True))
    # Checkpoints go to the volume every 150 steps; a rerun with the same name resumes from the latest one, so an
    # interrupted container (preemption, a workspace stop) loses at most 150 steps.
    from transformers.trainer_utils import get_last_checkpoint
    last = get_last_checkpoint(str(run_dir / "trainer")) if (run_dir / "trainer").exists() else None

    class _Commit(TrainerCallback):
        def on_save(self, args, state, control, **kw):
            vol.commit()

    trainer.add_callback(_Commit())
    t0 = time.time()
    result = trainer.train(resume_from_checkpoint=last)
    model.save_pretrained(run_dir / "adapter")
    tok.save_pretrained(run_dir / "adapter")
    return {"examples": len(feats), "dropped_too_long": too_long, "train_seconds": round(time.time() - t0, 1),
            "resumed_from": last,
            "train_loss": result.training_loss, "steps": trainer.state.global_step,
            "loss_log": [h for h in trainer.state.log_history if "loss" in h],
            "peak_gpu_gb": round(torch.cuda.max_memory_allocated() / 1e9, 1)}


def _subset(path: str, n: int, seed: int, ids_file: str = "") -> list[dict]:
    import random
    items = [json.loads(l) for l in open(path, encoding="utf-8")]
    random.Random(seed).shuffle(items)
    return items if n <= 0 else items[:n]


@app.function(image=image, gpu="H100", volumes={"/vol": vol}, timeout=6 * 3600)
def run(mode: str, adapter: str = "base", items: str = "dev.jsonl", prompt_mode: str = "rag", name: str = "",
        train_file: str = "train.jsonl", n: int = 0, epochs: int = 1, lr: float = 2e-4, max_steps: int = 0,
        limit: int = 0, max_new: int = 0, eval_after: str = "dev.jsonl", init_adapter: str = "", batch: int = 8,
        grad_accum: int = 2, prefill: str = "") -> dict:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    run_name = name or f"{stamp}-{mode}-{adapter}-{Path(items).stem}-{prompt_mode}"
    run_dir = Path("/vol/openset") / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    hyper = dict(HYPER, epochs=epochs, lr=lr, batch=batch, grad_accum=grad_accum)
    meta = {"run": run_name, "mode": mode, "base_model": BASE_MODEL, "revision": BASE_REVISION,
            "versions": _versions(), "hyper": hyper, "started": stamp}
    if mode == "train":
        tr = []
        for tf in train_file.split(","):  # several files are concatenated, then shuffled together
            tr += [json.loads(l) for l in open(f"/root/data/{tf}", encoding="utf-8")]
        import random
        random.Random(HYPER["seed"]).shuffle(tr)
        tr = tr if n <= 0 else tr[:n]
        meta["train_file"], meta["n_requested"] = train_file, n
        meta["train_init_adapter"] = init_adapter
        meta["train"] = _train(tr, run_dir, hyper, max_steps, init_adapter)
        vol.commit()
        adapter_dir, items, prompt_mode = str(run_dir / "adapter"), eval_after, "rag"
    else:
        adapter_dir = None if adapter == "base" else f"/vol/openset/{adapter}/adapter"
    if items:
        ev = [json.loads(l) for l in open(f"/root/data/{items}", encoding="utf-8")][: limit or None]
        tok, model = _load(adapter_dir)
        tuned = adapter_dir is not None
        mn = max_new or (32 if tuned and prompt_mode == "rag" else 768)
        tag = f"{Path(items).stem}-{prompt_mode}" + ("-prefill" if prefill else "")
        meta["eval"] = _evaluate(tok, model, ev, prompt_mode, run_dir, tag, mn, prefill=prefill)
        meta["prefill"] = prefill
        meta["eval_items"], meta["adapter"] = items, adapter if mode == "eval" else run_name
    json.dump(meta, open(run_dir / "meta.json", "w"), indent=1, default=str)
    vol.commit()
    return meta


@app.function(image=image, volumes={"/vol": vol}, timeout=600)
def fetch(run_name: str) -> dict[str, str]:
    """Return the small text files of a run (meta, summaries, predictions) for a local copy."""
    d = Path("/vol/openset") / run_name
    return {p.name: p.read_text() for p in d.glob("*.json*")}


@app.local_entrypoint()
def main(mode: str = "eval", adapter: str = "base", items: str = "dev.jsonl", prompt_mode: str = "rag",
         name: str = "", train_file: str = "train.jsonl", n: int = 0, epochs: int = 1, lr: float = 2e-4,
         max_steps: int = 0, limit: int = 0, max_new: int = 0, eval_after: str = "dev.jsonl", init_adapter: str = "",
         batch: int = 8, grad_accum: int = 2, prefill: str = ""):
    meta = run.remote(mode, adapter, items, prompt_mode, name, train_file, n, epochs, lr, max_steps, limit, max_new,
                      eval_after, init_adapter, batch, grad_accum, prefill)
    out = ROOT / "runs" / "openset-modal" / meta["run"]
    out.mkdir(parents=True, exist_ok=True)
    for fname, text in fetch.remote(meta["run"]).items():
        (out / fname).write_text(text)
    if "train" in meta:
        t = meta["train"]
        print(f"train: {t['examples']} examples, {t['steps']} steps, loss {t['train_loss']:.4f}, "
              f"{t['train_seconds']} s, peak {t['peak_gpu_gb']} GB")
    if "eval" in meta:
        print(json.dumps(meta["eval"], indent=1))
    print(f"local copy: {out}")
