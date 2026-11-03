"""Run scripts/build_openset.py on a Modal CPU container instead of the laptop, and copy the outputs back.

  modal run train/modal_build.py [--test-n 500]

Inputs are the local raw files (HF corpus, HTSUS export, ATLAS test, fetched CROSS rulings). Outputs land in
data/benchmark_modal/ locally; compare their SHA256SUMS with data/benchmark/ before replacing anything.
"""
from pathlib import Path

import modal

ROOT = Path(__file__).resolve().parents[1]
app = modal.App("tariff-slm-build")
image = (modal.Image.debian_slim(python_version="3.12")
         .pip_install("scikit-learn==1.9.1", "numpy==2.5.4", "scipy==1.18.1", "torch==2.9.0",
                      "sentence-transformers==5.1.2")
         .add_local_dir(ROOT / "src", "/root/repo/src")
         .add_local_dir(ROOT / "scripts", "/root/repo/scripts")
         .add_local_file(ROOT / "data/raw/cross_rulings.json", "/root/repo/data/raw/cross_rulings.json")
         .add_local_file(ROOT / "data/raw/hts_current.json", "/root/repo/data/raw/hts_current.json")
         .add_local_file(ROOT / "data/raw/atlas/test.jsonl", "/root/repo/data/raw/atlas/test.jsonl")
         .add_local_file(ROOT / "data/benchmark/atlas_test_matches.jsonl",
                         "/root/repo/data/benchmark/atlas_test_matches.jsonl")
         .add_local_dir(ROOT / "data/raw/cross_recent_all", "/root/repo/data/raw/cross_recent_all"))


@app.function(image=image, gpu="H100", cpu=8, memory=32768, timeout=3600)
def build(test_n: int, extra: str = "") -> dict[str, bytes]:
    import glob
    import subprocess
    api = sorted(glob.glob("/root/repo/data/raw/cross_recent_all/*.jsonl"))
    cmd = ["python", "-I", "scripts/build_openset.py", "--out", "/tmp/out", "--test-n", str(test_n), "--dense", *extra.split(), "--api", *api]
    r = subprocess.run(cmd, cwd="/root/repo", capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-3000:])
    return {p.name: p.read_bytes() for p in Path("/tmp/out").iterdir()}


image_v3 = (image.add_local_file(ROOT / "data/benchmark_try2/train.jsonl", "/root/repo/data/benchmark_try2/train.jsonl")
            .add_local_file(ROOT / "data/benchmark/dev.jsonl", "/root/repo/data/benchmark/dev.jsonl")
            .add_local_file(ROOT / "data/benchmark/test.jsonl", "/root/repo/data/benchmark/test.jsonl")
            .add_local_dir(ROOT / "data/raw/cross_backfill_all", "/root/repo/data/raw/cross_backfill_all"))


@app.function(image=image_v3, gpu="H100", cpu=8, memory=65536, timeout=3600)
def build_v3() -> dict[str, bytes]:
    import glob
    import subprocess
    back = sorted(glob.glob("/root/repo/data/raw/cross_backfill_all/*.jsonl"))
    cmd = ["python", "-I", "scripts/build_train_v3.py", "--out", "/tmp/out3", "--dense", "--backfill", *back]
    r = subprocess.run(cmd, cwd="/root/repo", capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-3000:])
    return {p.name: p.read_bytes() for p in Path("/tmp/out3").iterdir()}


@app.local_entrypoint()
def main(test_n: int = 500, extra: str = "", out_name: str = "benchmark_modal", v3: bool = False):
    out = ROOT / "data" / out_name
    if v3:
        out.mkdir(parents=True, exist_ok=True)
        for name, data in build_v3.remote().items():
            (out / name).write_bytes(data)
        print((out / "stats.json").read_text())
        return
    out.mkdir(parents=True, exist_ok=True)
    for name, data in build.remote(test_n, extra).items():
        (out / name).write_bytes(data)
        print(f"{name}: {len(data):,} bytes")
    print((out / "SHA256SUMS").read_text())
