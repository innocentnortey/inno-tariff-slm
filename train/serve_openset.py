"""Publish and serve the open-set tariff classifier (try 3) on Modal.

  modal run train/serve_openset.py --action publish-model     # merge the LoRA into the base, push to HF (public)
  modal run train/serve_openset.py --action publish-dataset   # push benchmark v2 files + card to HF (public)
  modal deploy train/serve_openset.py                          # live demo: web page + JSON API, key-protected
  modal run train/serve_openset.py --action bench --n 100      # single-request latency on a warm GPU

The demo runs the same pipeline that was evaluated: hybrid retrieval (TF-IDF + bge-base) over 27,841 earlier CBP
rulings and the HTSUS, then the prompt `openset-v1`, greedy decoding, the last `CODE:` line. The base model is the same
weights with the adapter switched off, so base vs tuned is a fair side-by-side. It scales to zero when idle; one
container at most. Every request needs the demo key (Modal secret `tariff-demo`, env `DEMO_KEY`).
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parents[1]
BASE_MODEL = "Qwen/Qwen3-4B-Instruct-2507"
BASE_REVISION = "cdbee75f17c01a7cc42f958dc650907174af0554"
ADAPTER_RUN = "try3-rationales-backfill-cont-b4"
ADAPTER = f"/vol/openset/{ADAPTER_RUN}/adapter"
MODEL_REPO = "tariff-classifier-qwen3-4b"
DATASET_REPO = "tariff-hts-openset-v2"

app = modal.App("tariff-classifier")
vol = modal.Volume.from_name("tariff-slm", create_if_missing=True)
base_image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("torch==2.9.0", "transformers==4.57.1", "peft==0.17.1", "accelerate==1.11.0", "scikit-learn==1.9.1",
                 "sentence-transformers==5.1.2", "huggingface_hub==0.36.2", "fastapi[standard]==0.121.0")
    .add_local_dir(ROOT / "src", "/root/src")
    .add_local_file(ROOT / "data/raw/hts_current.json", "/root/hts_current.json")
    .add_local_file(ROOT / "data/benchmark_try3/precedents.jsonl", "/root/precedents.jsonl")
    .add_local_file(ROOT / "data/benchmark/test.jsonl", "/root/test.jsonl")
    .add_local_dir(ROOT / "train/hf/openset", "/root/cards")
)
data_image = base_image.add_local_dir(ROOT / "data/benchmark", "/root/bench",
                                      ignore=["*_records.jsonl", "atlas_test_matches.jsonl", "train.jsonl"]) \
    .add_local_file(ROOT / "data/benchmark_try3/train.jsonl", "/root/try3/train.jsonl") \
    .add_local_file(ROOT / "data/benchmark_try3/train_mix.jsonl", "/root/try3/train_mix.jsonl")
hf_secret = modal.Secret.from_name("huggingface")


def _path():
    import sys
    if "/root/src" not in sys.path:
        sys.path.insert(0, "/root/src")


@app.function(image=base_image, gpu="H100", volumes={"/vol": vol}, secrets=[hf_secret], timeout=3600)
def publish_model() -> dict:
    import os
    import torch
    from huggingface_hub import HfApi
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer
    api = HfApi(token=os.environ["HF_TOKEN"])
    repo_id = f"{api.whoami()['name']}/{MODEL_REPO}"
    tok = AutoTokenizer.from_pretrained(BASE_MODEL, revision=BASE_REVISION)
    model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, revision=BASE_REVISION, torch_dtype=torch.bfloat16)
    model = PeftModel.from_pretrained(model, ADAPTER).merge_and_unload()
    out = Path("/tmp/merged")
    model.save_pretrained(out, safe_serialization=True)
    tok.save_pretrained(out)
    (out / "README.md").write_text(Path("/root/cards/MODEL_CARD.md").read_text())
    api.create_repo(repo_id, private=False, exist_ok=True)
    info = api.upload_folder(repo_id=repo_id, folder_path=str(out), commit_message=f"Merged adapter {ADAPTER_RUN}")
    return {"repo_id": repo_id, "commit": getattr(info, "oid", None) or str(info)}


@app.function(image=data_image, secrets=[hf_secret], timeout=3600)
def publish_dataset() -> dict:
    import hashlib
    import os
    import shutil
    from huggingface_hub import HfApi
    api = HfApi(token=os.environ["HF_TOKEN"])
    repo_id = f"{api.whoami()['name']}/{DATASET_REPO}"
    out = Path("/tmp/ds")
    out.mkdir()
    for f in ("dev.jsonl", "test.jsonl", "atlas_test.jsonl", "stats.json"):
        shutil.copy(f"/root/bench/{f}", out / f)
    shutil.copy("/root/try3/train.jsonl", out / "train.jsonl")
    shutil.copy("/root/try3/train_mix.jsonl", out / "train_mix.jsonl")
    sums = "".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in sorted(out.iterdir()))
    (out / "SHA256SUMS").write_text(sums)
    (out / "README.md").write_text(Path("/root/cards/DATASET_CARD.md").read_text())
    api.create_repo(repo_id, repo_type="dataset", private=False, exist_ok=True)
    info = api.upload_folder(repo_id=repo_id, repo_type="dataset", folder_path=str(out),
                             commit_message="Benchmark v2 (open-set) and the released model's training files")
    return {"repo_id": repo_id, "commit": getattr(info, "oid", None) or str(info), "sha256": sums}


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Tariff Classifier Demo</title>
<style>
:root{--bg:#fbfaf7;--surface:#fff;--text:#1d1f23;--muted:#5d6470;--line:#e3e0d8;--accent:#1f5f8b;--soft:#e7f0f6}
@media (prefers-color-scheme:dark){:root{--bg:#15171a;--surface:#1c1f23;--text:#e8e6e1;--muted:#a2a8b1;--line:#2e3238;
--accent:#7fb3d9;--soft:#1d2c38}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.5 system-ui,-apple-system,
"Segoe UI",sans-serif}main{max-width:900px;margin:0 auto;padding:28px 16px 60px}h1{font-size:24px;margin:0 0 4px}
p.sub{color:var(--muted);margin:0 0 20px}label{display:block;font-weight:600;font-size:14px;margin:14px 0 6px}
input,textarea{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:6px;background:var(--surface);
color:var(--text);font:inherit}textarea{min-height:140px}.row{display:flex;gap:16px;align-items:center;margin-top:14px;
flex-wrap:wrap}button{background:var(--accent);color:#fff;border:0;border-radius:6px;padding:10px 18px;font:inherit;
font-weight:600;cursor:pointer}button:focus-visible,input:focus-visible,textarea:focus-visible{outline:2px solid
var(--accent);outline-offset:2px}button[disabled]{opacity:.6;cursor:progress}.grid{display:grid;
grid-template-columns:1fr 1fr;gap:12px;margin-top:20px}.card{background:var(--surface);border:1px solid var(--line);
border-radius:8px;padding:14px}.card.t{border-color:var(--accent);background:var(--soft)}.code{font:600 22px/1.2
ui-monospace,Menlo,monospace}.muted{color:var(--muted);font-size:13px}table{width:100%;border-collapse:collapse;
font-size:13px;margin-top:8px}td{padding:5px 6px;border-bottom:1px solid var(--line);vertical-align:top}
td.c{font-family:ui-monospace,Menlo,monospace;white-space:nowrap}tr.hit td{font-weight:700}
@media (max-width:640px){.grid{grid-template-columns:1fr}}
</style></head><body><main>
<h1>Tariff classifier: 10-digit HTSUS code from a product description</h1>
<p class="sub">Fine-tuned Qwen3-4B with retrieval over earlier CBP rulings. Compare it with the same base model on the
same evidence.</p>
<form id="f"><label for="key">Demo key</label><input id="key" type="password" autocomplete="off" required>
<label for="product">Product name</label><input id="product" placeholder="e.g. a women's knit pullover" required>
<label for="description">Description</label><textarea id="description" required
placeholder="Material, construction, use, size... as an importer would describe the goods."></textarea>
<div class="row"><label style="margin:0"><input id="base" type="checkbox" checked style="width:auto"> Also run the
base model</label><button id="go" type="submit">Classify</button><span id="status" class="muted" aria-live="polite">
</span></div></form>
<div id="out"></div></main>
<script>
const f=document.getElementById('f'),out=document.getElementById('out'),st=document.getElementById('status'),
go=document.getElementById('go');
const kf=document.getElementById('key');try{kf.value=localStorage.getItem('demoKey')||''}catch(e){}
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
f.addEventListener('submit',async e=>{e.preventDefault();go.disabled=true;out.innerHTML='';
st.textContent='Classifying… the first request after idle loads the model (about 3 minutes).';
const body=x=>JSON.stringify(Object.assign({key:kf.value,product:document.getElementById('product').value,
description:document.getElementById('description').value},x));
const post=async x=>{const r=await fetch('api/classify',{method:'POST',headers:{'content-type':'application/json'},
body:body(x)});const d=await r.json();if(!r.ok){throw new Error(d.detail||r.statusText)}return d};
const card=(t,a,c,id)=>`<div class="card ${c}" id="${id}"><div class="muted">${t}</div><div class="code">${esc(a.code||'no code')}</div>
<div class="muted">${a.seconds}s · ${a.in_candidates?'in the search results':'not in the search results'}</div></div>`;
const wantBase=document.getElementById('base').checked;
try{const d=await post({compare_base:false});st.textContent='';try{localStorage.setItem('demoKey',kf.value)}catch(e){}
let h='<div class="grid">'+card('Fine-tuned',d.tuned,'t','tunedcard')+(wantBase?`<div class="card" id="basecard"><div class="muted">Base model</div>
<div class="code">…</div><div class="muted">running on the same evidence</div></div>`:'')+'</div>';
h+=`<p class="muted">Search ${d.retrieval_seconds}s · ${esc(d.device)}</p><div class="card"><div class="muted">HTSUS lines
found by search</div><table>${d.candidates.map(c=>`<tr class="${c.code===d.tuned.code?'hit':''}"><td class="c">
${esc(c.code)}</td><td>${esc(c.text)}</td></tr>`).join('')}</table></div>`;out.innerHTML=h;
if(wantBase){const b=await post({only_base:true});const el=document.getElementById('basecard');
el.outerHTML=card('Base model',b.base,'done','basecard')}}
catch(err){st.textContent='Could not classify: '+err.message+'. Check the key and try again.'}finally{go.disabled=false}});
</script></body></html>"""


@app.cls(image=base_image, gpu=["A10G", "L40S", "L4"], volumes={"/vol": vol},
         secrets=[modal.Secret.from_name("tariff-demo")], scaledown_window=300, max_containers=1, timeout=900)
class Demo:
    @modal.enter()
    def load(self):
        _path()
        import torch
        from peft import PeftModel
        from sentence_transformers import SentenceTransformer
        from transformers import AutoModelForCausalLM, AutoTokenizer
        from tariff_slm.data.schedule import load_schedule
        from tariff_slm.openset.retrieval import CONFIG, Retriever
        t0 = time.time()
        self.tok = AutoTokenizer.from_pretrained(BASE_MODEL, revision=BASE_REVISION)
        base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, revision=BASE_REVISION, torch_dtype=torch.bfloat16,
                                                    device_map="cuda")
        self.model = PeftModel.from_pretrained(base, ADAPTER).eval()
        self.sched = load_schedule("/root/hts_current.json")
        st = SentenceTransformer(CONFIG["dense_model"], device="cuda")
        embed = lambda xs: st.encode(xs, batch_size=256, normalize_embeddings=True,  # noqa: E731
                                     show_progress_bar=False, convert_to_numpy=True)
        prec = [json.loads(l) for l in open("/root/precedents.jsonl", encoding="utf-8")]
        self.retriever = Retriever(self.sched, prec, embed)
        self.device = torch.cuda.get_device_name(0)
        self.load_seconds = round(time.time() - t0, 1)

    def _generate(self, msgs, max_new: int, use_adapter: bool) -> tuple[str, float]:
        import contextlib
        import torch
        text = self.tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
        enc = self.tok(text, return_tensors="pt").to(self.model.device)
        ctx = contextlib.nullcontext() if use_adapter else self.model.disable_adapter()
        torch.cuda.synchronize()
        t = time.time()
        with torch.no_grad(), ctx:
            out = self.model.generate(**enc, max_new_tokens=max_new, do_sample=False,
                                      pad_token_id=self.tok.eos_token_id)
        torch.cuda.synchronize()
        return self.tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True), time.time() - t

    def _item(self, product: str, description: str) -> tuple[dict, float]:
        t = time.time()
        ctx = self.retriever.batch([{"product": product, "description": description}])[0]
        item = {"product": product, "description": description, "precedents": ctx.precedents,
                "candidates": [{"code": c, "text": self.sched[c].text} for c in ctx.candidates]}
        return item, time.time() - t

    def _answer(self, item: dict, use_adapter: bool) -> dict:
        from tariff_slm.openset.prompts import dotted, messages, parse
        raw, secs = self._generate(messages(item, "rag"), 32 if use_adapter else 768, use_adapter)
        code = parse(raw)["code"]
        return {"code": dotted(code) if code and len(code) == 10 else code, "raw": raw[-600:],
                "seconds": round(secs, 2), "valid": bool(code) and code in self.sched,
                "in_candidates": code in {c["code"] for c in item["candidates"]}}

    @modal.method()
    def classify(self, product: str, description: str, compare_base: bool = True) -> dict:
        return self._classify(product, description, compare_base)

    def _classify(self, product: str, description: str, compare_base: bool = True, only_base: bool = False) -> dict:
        _path()
        from tariff_slm.openset.prompts import dotted
        item, rsec = self._item(product.strip(), description.strip())
        if only_base:  # the page asks for the base answer separately, so the tuned answer shows as soon as it is ready
            return {"base": self._answer(item, False), "retrieval_seconds": round(rsec, 3), "device": self.device}
        out = {"tuned": self._answer(item, True), "retrieval_seconds": round(rsec, 3), "device": self.device,
               "candidates": [{"code": dotted(c["code"]), "text": c["text"]} for c in item["candidates"]],
               "precedents": [{"ruling_id": p["ruling_id"], "code": dotted(p["code"]), "product": p["product"]}
                              for p in item["precedents"]]}
        if compare_base:
            out["base"] = self._answer(item, False)
        return out

    @modal.method()
    def bench(self, n: int = 100) -> dict:
        """Single-request latency, one item at a time on a warm GPU: (a) model only, on the frozen test contexts the
        reported accuracy used; (b) end to end, live search + model. Also re-checks accuracy on those items."""
        _path()
        from tariff_slm.openset.prompts import messages, parse
        items = [json.loads(l) for l in open("/root/test.jsonl", encoding="utf-8")][:n]
        self._generate(messages(items[0], "rag"), 32, True)  # warm-up, not timed
        model_only, e2e, right = [], [], 0
        for it in items:
            raw, secs = self._generate(messages(it, "rag"), 32, True)
            model_only.append(secs)
            right += parse(raw)["code"] == it["code"]
            live, rsec = self._item(it["product"], it["description"])
            _, secs2 = self._generate(messages(live, "rag"), 32, True)
            e2e.append(rsec + secs2)
        pct = lambda xs, q: round(sorted(xs)[min(len(xs) - 1, int(q * len(xs)))], 3)  # noqa: E731
        return {"device": self.device, "n": n, "load_seconds": self.load_seconds,
                "model_only": {"p50": pct(model_only, .5), "p90": pct(model_only, .9), "mean": round(sum(model_only) / n, 3)},
                "end_to_end": {"p50": pct(e2e, .5), "p90": pct(e2e, .9), "mean": round(sum(e2e) / n, 3)},
                "exact_on_frozen_contexts": f"{right}/{n}"}

    @modal.asgi_app()
    def web(self):
        import hmac
        import os
        from fastapi import Body, FastAPI, HTTPException
        from fastapi.responses import HTMLResponse
        from pydantic import BaseModel, ConfigDict, Field, ValidationError
        api = FastAPI(title="Tariff classifier demo")

        class Req(BaseModel):
            model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
            key: str = Field(max_length=200)
            product: str = Field(min_length=1, max_length=300)
            description: str = Field(min_length=10, max_length=4000)
            compare_base: bool = True
            only_base: bool = False

        @api.get("/", response_class=HTMLResponse)
        def page():
            return PAGE

        @api.post("/api/classify")
        def classify(payload: dict = Body(...)):
            try:
                req = Req.model_validate(payload)
            except ValidationError as e:  # field names and constraint only, never the submitted values
                fields = sorted({".".join(map(str, err["loc"])) for err in e.errors()})
                raise HTTPException(status_code=422, detail=f"invalid fields: {', '.join(fields)}") from None
            if not hmac.compare_digest(req.key.encode(), os.environ["DEMO_KEY"].encode()):
                raise HTTPException(status_code=401, detail="wrong demo key")
            return self._classify(req.product, req.description, req.compare_base, req.only_base)

        return api


@app.local_entrypoint()
def main(action: str = "bench", n: int = 100, gpu: str = ""):
    if action == "publish-model":
        print(json.dumps(publish_model.remote(), indent=1))
    elif action == "publish-dataset":
        r = publish_dataset.remote()
        print(r["repo_id"], r["commit"])
        print(r["sha256"])
    elif action == "bench":
        demo = Demo.with_options(gpu=gpu) if gpu else Demo
        r = demo().bench.remote(n)
        print(json.dumps(r, indent=1))
        out = ROOT / "runs" / "latency"
        out.mkdir(parents=True, exist_ok=True)
        (out / f"bench-{r['device'].replace(' ', '_')}-n{n}.json").write_text(json.dumps(r, indent=1))
    else:
        raise SystemExit(f"unknown action {action}")
