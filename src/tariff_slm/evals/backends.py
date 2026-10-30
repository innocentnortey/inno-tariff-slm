"""Model backends behind one call: generate(messages) -> text. Selected by a prefix on --model."""
from __future__ import annotations

import os
from typing import Callable

Generate = Callable[[list[dict]], str]


def load(model: str, max_tokens: int = 512, temperature: float = 0.0) -> Generate:
    kind, _, name = model.partition(":") if ":" in model else ("auto", "", model)
    if kind == "auto":
        try:
            import mlx_lm  # noqa: F401
            kind = "mlx"
        except ImportError:
            kind = "hf"
    if kind == "mlx":
        from mlx_lm import generate, load as mlx_load
        from mlx_lm.sample_utils import make_sampler
        m, tok = mlx_load(name)
        sampler = make_sampler(temp=temperature)
        def run(msgs):
            prompt = tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False, enable_thinking=False)
            return generate(m, tok, prompt=prompt, max_tokens=max_tokens, sampler=sampler, verbose=False)
        return run
    if kind == "hf":
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(name)
        m = AutoModelForCausalLM.from_pretrained(name, torch_dtype="auto", device_map="auto")
        def run(msgs):
            ids = tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", enable_thinking=False).to(m.device)
            with torch.no_grad():
                out = m.generate(ids, max_new_tokens=max_tokens, do_sample=temperature > 0, temperature=temperature or None)
            return tok.decode(out[0, ids.shape[1]:], skip_special_tokens=True)
        return run
    if kind == "anthropic":
        import anthropic
        client = anthropic.Anthropic()
        def run(msgs):
            system = "\n".join(x["content"] for x in msgs if x["role"] == "system")
            rest = [x for x in msgs if x["role"] != "system"]
            r = client.messages.create(model=name, system=system, messages=rest, max_tokens=max_tokens, temperature=temperature)
            return "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
        return run
    if kind == "openai":
        from openai import OpenAI
        client = OpenAI(base_url=os.environ.get("OPENAI_BASE_URL"))
        def run(msgs):
            r = client.chat.completions.create(model=name, messages=msgs, max_completion_tokens=max_tokens)
            return r.choices[0].message.content or ""
        return run
    if kind == "baseline":
        from .baselines import BASELINES
        fn = BASELINES[name]
        return fn  # baselines take the item, not messages; eval.py handles this
    raise ValueError(f"unknown backend {kind!r}; use mlx:, hf:, anthropic:, openai: or baseline:")
