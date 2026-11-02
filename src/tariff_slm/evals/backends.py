"""Model backends behind one call: generate(messages) -> text. Selected by a prefix on --model.

API backends record each call's token usage on `run.last_usage` so eval.py can report measured cost. Frontier
backends run at a fixed reasoning effort (`effort`) so every prompt strategy is compared at the same setting.
"""
from __future__ import annotations

import os
import threading
from typing import Callable

Generate = Callable[[list[dict]], str]

OPENROUTER_URL = "https://openrouter.ai/api/v1"


def load(model: str, max_tokens: int = 512, temperature: float = 0.0, effort: str = "high") -> Generate:
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
        local = threading.local()

        # Current Claude models think adaptively and reject sampling parameters, and thinking tokens count against
        # max_tokens, so give room and fix the effort. No refusal fallback: a different model answering would
        # contaminate the measurement, so a refusal is recorded as an empty (failed) answer.
        def run(msgs):
            system = "\n".join(x["content"] for x in msgs if x["role"] == "system")
            rest = [x for x in msgs if x["role"] != "system"]
            r = client.messages.create(model=name, system=system, messages=rest, max_tokens=max(max_tokens, 16000),
                                       output_config={"effort": effort})
            u = r.usage
            local.usage = {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                           "stop_reason": r.stop_reason}
            if r.stop_reason == "refusal":
                return ""
            return "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
        run.local = local
        return run
    if kind in ("openai", "openrouter"):
        from openai import OpenAI
        if kind == "openrouter":
            client = OpenAI(base_url=OPENROUTER_URL, api_key=os.environ["OPENROUTER_API_KEY"])
            extra = {"reasoning": {"effort": effort}, "usage": {"include": True}}
        else:
            client = OpenAI(base_url=os.environ.get("OPENAI_BASE_URL"))
            extra = {}
        local = threading.local()

        def run(msgs):
            r = client.chat.completions.create(model=name, messages=msgs, max_completion_tokens=max(max_tokens, 16000),
                                               extra_body=extra or None)
            u = r.usage
            local.usage = {"input_tokens": getattr(u, "prompt_tokens", None),
                           "output_tokens": getattr(u, "completion_tokens", None),
                           "cost_usd": getattr(u, "cost", None), "stop_reason": r.choices[0].finish_reason}
            return r.choices[0].message.content or ""
        run.local = local
        return run
    if kind == "baseline":
        from .baselines import BASELINES
        fn = BASELINES[name]
        return fn  # baselines take the item, not messages; eval.py handles this
    raise ValueError(f"unknown backend {kind!r}; use mlx:, hf:, anthropic:, openrouter:, openai: or baseline:")


def last_usage(gen: Generate) -> dict | None:
    """Token usage of the calling thread's last API call, or None for local models and baselines."""
    local = getattr(gen, "local", None)
    return getattr(local, "usage", None) if local is not None else None
