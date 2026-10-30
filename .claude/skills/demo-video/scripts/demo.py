#!/usr/bin/env python3
"""
demo.py - mechanical half of the demo-video skill. Claude writes .demo/shotlist.yaml; this script does the rest.
Run from the project's repo root. Everything goes in .demo/ (build files in .demo/build/, git-ignored).

  demo.py setup                                        install Python deps + Chromium, check ffmpeg and keys
  demo.py context --url URL [--repo .] [--dev CMD]     repo inventory + live site map -> .demo/build/
  demo.py check   [--headed]                           dry-run every action; failures -> .demo/build/failures.json
  demo.py export                                       narration script -> .demo/build/script.md
  demo.py voice   [--own-audio DIR] [--force]          ElevenLabs narration per scene (cached by text)
  demo.py record  [--headed]                           browser recording timed to the narration
  demo.py assemble [--subs]                            final MP4 + .srt in .demo/
  demo.py render  [--subs]                             voice + record + assemble
  demo.py frames                                       stills per scene -> .demo/build/frames/
  demo.py voices | clone --name N --files a.mp3 | login --url URL
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urljoin, urlparse

VENV = Path.home() / ".cache" / "demo-video" / "venv"
try:
    import requests
    import yaml
    __import__("playwright")
except ImportError:
    # Use the private venv that `setup` creates, so system Python is never touched.
    _vpy = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if _vpy.exists() and Path(sys.prefix).resolve() != VENV.resolve():
        os.execv(str(_vpy), [str(_vpy), __file__, *sys.argv[1:]])
    if "setup" not in sys.argv:
        print("Missing packages. Run: python demo.py setup", file=sys.stderr)
        sys.exit(1)
    requests = yaml = None

BUILD = Path(".demo/build")       # set per shot list by set_workdir()
DEFAULT_SHOTLIST = ".demo/shotlist.yaml"
GLOBAL_ENV = Path.home() / ".config" / "demo-video" / ".env"
WPM = 150                 # narration pace used for estimates (target band below; see SKILL.md *Length and pace*)
WPM_LOW, WPM_HIGH = 140, 165   # measured pace outside this band gets a warning
LEN_FLOOR, LEN_TARGET, LEN_CAP = 210, 240, 300   # 3:30 minimum, 4:00 to 5:00 target, 5:00 ceiling (seconds)
AUDIO_LEAD = 0.25         # seconds of picture before the voice starts in each scene
SCENE_TAIL = 0.6          # seconds of picture held after the voice ends
FPS = 30
ELEVEN = "https://api.elevenlabs.io/v1"
DEFAULT_TTS_MODEL = "eleven_multilingual_v2"


# ───────────────────────────── helpers ─────────────────────────────

def die(msg: str) -> None:
    print(f"\n✖ {msg}", file=sys.stderr)
    sys.exit(1)


def load_dotenv() -> None:
    """Env vars win; then .demo/.env, ./.env, then ~/.config/demo-video/.env (keys shared by all repos)."""
    for p in (Path(".demo/.env"), Path(".env"), GLOBAL_ENV):
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def resolve_shotlist(path: str | None) -> str:
    if path:
        return path
    if Path(DEFAULT_SHOTLIST).exists() or not Path("shotlist.yaml").exists():
        return DEFAULT_SHOTLIST
    return "shotlist.yaml"


def set_workdir(shotlist_path: str) -> None:
    global BUILD
    BUILD = Path(shotlist_path).parent / "build"
    BUILD.mkdir(parents=True, exist_ok=True)


def load_shotlist(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        die(f"{path} not found. Run `demo.py plan ...` first.")
    sl = yaml.safe_load(p.read_text())
    if not isinstance(sl, dict) or not sl.get("scenes"):
        die(f"{path} has no scenes.")
    seen = set()
    for i, s in enumerate(sl["scenes"]):
        s.setdefault("id", f"scene{i+1}")
        if s["id"] in seen:
            die(f"duplicate scene id: {s['id']}")
        seen.add(s["id"])
        if not str(s.get("narration", "")).strip():
            die(f"scene {s['id']} has no narration")
    sl.setdefault("viewport", {"width": 1920, "height": 1080})
    return sl


def ffprobe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        die(f"could not read duration of {path}: {out.stderr}")
    return 0.0


def run_ffmpeg(args: list[str]) -> None:
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        die("ffmpeg failed:\n" + " ".join(cmd) + "\n" + r.stderr)


def words(text: str) -> int:
    return len(str(text).split())


def fmt_t(sec: float) -> str:
    return f"{int(sec // 60)}:{sec % 60:04.1f}"


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "demo"


def read_json(p: Path, default):
    return json.loads(p.read_text()) if p.exists() else default


# ───────────────────────────── repo context ─────────────────────────────

SKIP_DIRS = {"node_modules", ".git", "dist", "build", ".next", ".nuxt", "out", "coverage", "venv", ".venv",
             "env", "__pycache__", ".demo", ".turbo", ".cache", "target", "vendor", ".svelte-kit", ".vercel",
             ".idea", ".vscode", "public", "static", "assets"}
SKIP_FILES = re.compile(r"(lock\.json|\.lock|lock\.yaml|\.min\.js|\.map|changelog|license)", re.I)
DOC_EXT = {".md", ".mdx", ".txt", ".rst"}
DOC_STRONG = re.compile(r"(prd|requirement|users?\b|user[_-]|stor(y|ies)|key[_-]?metrics|metrics|architecture|spec|problem)", re.I)
DOC_DIRS = {"docs", "doc", "design", "specs", "spec", "prd", "planning", "notes"}
UI_EXT = {".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte", ".html", ".astro", ".erb", ".jinja", ".j2", ".hbs", ".php", ".py"}
UI_PATTERNS = {
    "testid": r"""data-(?:testid|test-id|test|cy)=["']([^"']+)""",
    "id": r"""\bid=["']([A-Za-z][\w:-]{1,40})["']""",
    "placeholder": r"""placeholder=["']([^"']{1,60})""",
    "aria": r"""aria-label=["']([^"']{1,60})""",
    "button": r"""<button\b[^>]*>\s*([^<>{}\n]{2,40}?)\s*<""",
    "route": r"""\bpath\s*[:=]\s*["'](/[^"']*)""",
    "api": r"""(?:@?(?:app|router|api|bp|server))\.(?:get|post|put|patch|delete|route)\(\s*["'](/[^"']*)""",
}
MANIFESTS = {"package.json", "pyproject.toml", "requirements.txt", "Cargo.toml", "go.mod", "docker-compose.yml",
             "docker-compose.yaml", "Dockerfile", "vite.config.ts", "next.config.js", "next.config.mjs"}


def repo_files(root: Path) -> list[str]:
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files", "-co", "--exclude-standard"],
                             capture_output=True, text=True, check=True).stdout.splitlines()
    except Exception:
        out = []
        for dp, dns, fns in os.walk(root):
            dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith(".")]
            out += [str(Path(dp, f).relative_to(root)) for f in fns]
    keep = []
    for f in out:
        parts = Path(f).parts
        if any(x in SKIP_DIRS for x in parts[:-1]) or SKIP_FILES.search(f):
            continue
        keep.append(f.replace("\\", "/"))
    return sorted(keep)


def next_routes(files: list[str]) -> list[str]:
    routes = set()
    for f in files:
        m = re.search(r"(?:^|/)app/(.*?)/?page\.(?:t|j)sx?$", f) or re.search(r"(?:^|/)app/()page\.(?:t|j)sx?$", f)
        if m:
            segs = [x for x in m.group(1).split("/") if x and not (x.startswith("(") and x.endswith(")"))]
            routes.add("/" + "/".join(segs))
            continue
        m = re.search(r"(?:^|/)pages/(.*)\.(?:t|j)sx?$", f)
        if m and not re.match(r"(_app|_document|_error|api/)", m.group(1)):
            r = "/" + re.sub(r"(^|/)index$", "", m.group(1))
            routes.add(r if r != "/" else "/")
    return sorted(routes)


def collect_repo(root: Path, prd: str | None) -> str:
    files = repo_files(root)
    print(f"  ✓ {len(files)} files in {root.resolve().name}")
    out = []

    # docs, design docs first
    def doc_rank(f):
        name, parts = Path(f).name, Path(f).parts
        if DOC_STRONG.search(name):
            return 0
        if len(parts) == 1 and name.lower().startswith("readme"):
            return 1
        if any(x.lower() in DOC_DIRS for x in parts[:-1]):
            return 2
        if name.upper() in ("CLAUDE.MD", "AGENTS.MD"):
            return 3
        return 9
    docs = sorted([f for f in files if Path(f).suffix.lower() in DOC_EXT and doc_rank(f) < 9], key=lambda f: (doc_rank(f), f))
    budget = 140_000
    out.append("<repo_docs>")
    if prd:
        out.append(f"<doc path='{prd}' note='the PRD passed with --prd'>\n{Path(prd).read_text(errors='ignore')[:40000]}\n</doc>")
    for f in docs:
        if prd and Path(f).resolve() == Path(prd).resolve():
            continue
        text = (root / f).read_text(errors="ignore")
        if len(text) > 30000:
            text = text[:30000] + "\n…[truncated]"
        if budget - len(text) < 0:
            out.append(f"<doc path='{f}' note='omitted, over budget'/>")
            continue
        budget -= len(text)
        out.append(f"<doc path='{f}'>\n{text}\n</doc>")
        print(f"    doc  {f}")
    out.append("</repo_docs>")

    # UI inventory from source
    inv, api = [], set()
    for f in files:
        ext = Path(f).suffix.lower()
        if ext not in UI_EXT:
            continue
        try:
            text = (root / f).read_text(errors="ignore")
        except Exception:
            continue
        if len(text) > 300_000:
            continue
        found = {}
        for k, rx in UI_PATTERNS.items():
            if k == "api":
                api.update(re.findall(rx, text))
                continue
            if ext == ".py" and k != "route":
                continue
            vals = sorted(set(v.strip() for v in re.findall(rx, text) if v.strip()))
            if vals:
                found[k] = vals[:25]
        if found:
            inv.append(f"{f}: " + "; ".join(f"{k}={json.dumps(v)}" for k, v in found.items()))
    inv_text = "\n".join(inv)[:50000]
    out.append(f"<ui_inventory note='selectable things found in source, per file'>\n{inv_text}\n</ui_inventory>")
    routes = next_routes(files)
    out.append(f"<routes>\nfrontend: {routes}\napi: {sorted(api)[:80]}\n</routes>")

    # manifests and tree
    for f in files:
        if Path(f).name in MANIFESTS and len(Path(f).parts) <= 3:
            out.append(f"<manifest path='{f}'>\n{(root / f).read_text(errors='ignore')[:4000]}\n</manifest>")
    out.append("<file_tree>\n" + "\n".join(files[:600]) + ("\n…" if len(files) > 600 else "") + "\n</file_tree>")
    print(f"  ✓ {len(docs)} docs, {len(inv)} UI files inventoried, {len(routes)} frontend routes")
    return "\n".join(out)


# ───────────────────────────── dev server ─────────────────────────────

def url_up(url: str) -> bool:
    try:
        return requests.get(url, timeout=3).status_code < 500
    except Exception:
        return False


@contextmanager
def dev_server(sl: dict):
    """Start the app's dev server if the shot list says how and it isn't already running."""
    dev = sl.get("dev") or {}
    url = dev.get("url") or sl.get("url")
    cmd = dev.get("command")
    if not cmd or (url and url_up(url)):
        yield
        return
    log_path = BUILD / "dev_server.log"
    print(f"  starting dev server: {cmd}  (log: {log_path})")
    kw = {"start_new_session": True} if os.name != "nt" else {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP}
    with open(log_path, "w") as log:
        proc = subprocess.Popen(cmd, shell=True, stdout=log, stderr=subprocess.STDOUT, **kw)
    try:
        deadline = time.time() + float(dev.get("ready_timeout", 120))
        while not url_up(url):
            if proc.poll() is not None:
                die(f"dev server exited early; see {log_path}")
            if time.time() > deadline:
                die(f"dev server not reachable at {url} after {dev.get('ready_timeout', 120)}s; see {log_path}")
            time.sleep(1)
        print(f"  ✓ {url} is up")
        yield
    finally:
        try:
            if os.name != "nt":
                import signal
                os.killpg(proc.pid, signal.SIGTERM)
            else:
                proc.terminate()
            proc.wait(timeout=10)
        except Exception:
            proc.kill()


# ───────────────────────────── plan ─────────────────────────────

SCRAPE_JS = r"""
() => {
  const vis = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const txt = el => (el.innerText || el.value || el.getAttribute('aria-label') || el.title || '')
    .trim().replace(/\s+/g, ' ').slice(0, 80);
  const take = (sel, f, n) => [...document.querySelectorAll(sel)].filter(vis).slice(0, n).map(f);
  return {
    title: document.title,
    headings: take('h1,h2,h3', e => e.tagName + ': ' + txt(e), 30),
    links: take('a[href]', e => ({text: txt(e), href: e.getAttribute('href')}), 60),
    buttons: take('button,[role=button],input[type=submit]',
      e => ({text: txt(e), id: e.id || null, testid: e.dataset.testid || null}), 40),
    inputs: take('input:not([type=hidden]):not([type=submit]),textarea,select', e => ({
      tag: e.tagName.toLowerCase(), type: e.type || null, id: e.id || null, name: e.name || null,
      placeholder: e.placeholder || null, aria: e.getAttribute('aria-label'),
      label: (e.labels && e.labels[0]) ? txt(e.labels[0]) : null, testid: e.dataset.testid || null}), 30),
    text_sample: (document.body ? document.body.innerText : '').replace(/\s+/g, ' ').slice(0, 1500)
  };
}
"""

def scrape_site(url: str, max_pages: int, storage_state: str | None) -> list[dict]:
    from playwright.sync_api import sync_playwright
    pages: list[dict] = []
    origin = urlparse(url).netloc
    with sync_playwright() as p:
        browser = p.chromium.launch()
        kw = {"viewport": {"width": 1440, "height": 900}}
        if storage_state and Path(storage_state).exists():
            kw["storage_state"] = storage_state
        ctx = browser.new_context(**kw)
        page = ctx.new_page()
        queue, seen = [url], set()
        while queue and len(pages) < max_pages:
            u = queue.pop(0)
            if u in seen:
                continue
            seen.add(u)
            try:
                page.goto(u, wait_until="domcontentloaded", timeout=30000)
                try:
                    page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
            except Exception as e:
                print(f"  ! could not load {u}: {e}")
                continue
            info = page.evaluate(SCRAPE_JS)
            info["url"] = page.url
            pages.append(info)
            print(f"  ✓ {page.url}  ({len(info['buttons'])} buttons, {len(info['inputs'])} inputs)")
            for link in info["links"]:
                full = urljoin(page.url, link["href"] or "").split("#")[0]
                if urlparse(full).netloc == origin and full not in seen and full.startswith("http"):
                    queue.append(full)
        browser.close()
    return pages


def ensure_demo_dir() -> None:
    d = Path(".demo")
    d.mkdir(exist_ok=True)
    gi = d / ".gitignore"
    if not gi.exists():
        gi.write_text("build/\n*.mp4\n*.srt\nauth.json\n.env\n")


def cmd_context(a):
    ensure_demo_dir()
    draft = {"url": a.url}
    if a.dev:
        draft["dev"] = {"command": a.dev, "url": a.url, "ready_timeout": 120}
    if a.repo:
        print(f"Reading repo {a.repo} ...")
        (BUILD / "context.md").write_text(collect_repo(Path(a.repo), a.prd))
    elif a.prd:
        (BUILD / "context.md").write_text(f"<prd path='{a.prd}'>\n{Path(a.prd).read_text(errors='ignore')}\n</prd>")
    with dev_server(draft):
        print(f"Mapping {a.url} ...")
        site = scrape_site(a.url, a.pages, a.auth)
    if not site:
        die("could not load any page of the site (is it running? pass --dev \"npm run dev\" to start it)")
    (BUILD / "site_map.json").write_text(json.dumps(site, indent=1))
    print(f"\n✓ {BUILD/'site_map.json'}" + (f"\n✓ {BUILD/'context.md'}" if (BUILD / 'context.md').exists() else ""))
    print("  Next: write .demo/shotlist.yaml (see references/shotlist.md), then run `check`.")


def print_summary(sl: dict, timing: dict | None = None):
    total_w = 0
    total_t = 0.0
    print()
    for s in sl["scenes"]:
        w = words(s["narration"])
        total_w += w
        t = (timing or {}).get(s["id"], w / WPM * 60) + AUDIO_LEAD + SCENE_TAIL
        total_t += t
        tag = s.get("type", "app")
        req = f"  [{s['requirement']}]" if s.get("requirement") else ""
        pace = ""
        if timing and timing.get(s["id"]):
            sw = w / timing[s["id"]] * 60
            pace = f"  {sw:3.0f} wpm" + ("  ⚠ uneven" if sw < 120 or sw > 185 else "")
        print(f"  {s['id']:<22} {tag:<5} {w:>4} words  ~{t:5.1f}s{pace}{req}")
    label = "measured" if timing else "estimated"
    print(f"  {'TOTAL':<22} {'':<5} {total_w:>4} words  {fmt_t(total_t)} ({label})")
    if timing:
        spoken = sum(timing.get(s["id"], 0.0) for s in sl["scenes"])
        if spoken > 0:
            wpm = total_w / spoken * 60
            print(f"  pace: {wpm:.0f} words per minute over {fmt_t(spoken)} of voice (target {WPM_LOW} to {WPM_HIGH})")
            if wpm < WPM_LOW:
                print("  ⚠ slow voice. Raise voice speed toward 1.05 or tighten pauses; don't pad words.")
            elif wpm > WPM_HIGH:
                print("  ⚠ fast voice. Lower voice speed toward 0.95, or cut words.")
    length_warning(total_t)


def length_warning(total: float):
    if total > LEN_CAP:
        print("  ⚠ over 5 minutes. Trim the technical segment first, then product scenes.")
    elif total < LEN_FLOOR:
        print("  ⚠ under 3:30, the minimum. Ask Codex for the technical-challenges segment (SKILL.md 4a).")
    elif total < LEN_TARGET:
        print("  ⚠ under the 4:00 to 5:00 target. Add the technical-challenges segment if the product is fully shown.")


# ───────────────────────────── export script ─────────────────────────────

def cmd_export(a):
    sl = load_shotlist(a.shotlist)
    BUILD.mkdir(exist_ok=True)
    md = [f"# {sl.get('project', 'Demo')} — narration script\n"]
    txt = []
    for i, s in enumerate(sl["scenes"], 1):
        head = s.get("requirement") or s.get("title") or s["id"]
        ev = s.get("evidence") or []
        ev_md = ("\n*Evidence:* " + ", ".join(f"`{e}`" for e in ev) + "\n") if ev else ""
        md.append(f"## {i}. {s['id']} — {head}\n\n{s['narration'].strip()}\n{ev_md}")
        txt.append(s["narration"].strip())
    (BUILD / "script.md").write_text("\n".join(md))
    (BUILD / "script.txt").write_text("\n\n".join(txt) + "\n")
    print_summary(sl)
    print(f"\n✓ wrote {BUILD/'script.md'} (to read from) and {BUILD/'script.txt'} (paste into ElevenLabs Studio)")
    print("  If you record yourself, save one file per scene as recordings/<scene id>.wav|mp3|m4a")


# ───────────────────────────── ElevenLabs ─────────────────────────────

def eleven(method: str, url: str, **kw):
    try:
        return requests.request(method, url, **kw)
    except requests.RequestException as e:
        die(f"could not reach ElevenLabs ({e.__class__.__name__}). Check your network connection.")


def eleven_key() -> str:
    k = os.getenv("ELEVENLABS_API_KEY")
    if not k:
        die("ELEVENLABS_API_KEY is not set: add it to .demo/.env (git-ignored)")
    return k


def cmd_voices(a):
    r = eleven("GET", f"{ELEVEN}/voices", headers={"xi-api-key": eleven_key()}, timeout=30)
    if r.status_code != 200:
        die(f"ElevenLabs {r.status_code}: {r.text[:300]}")
    for v in r.json().get("voices", []):
        print(f"  {v['voice_id']}  {v.get('category', ''):<12} {v['name']}")


def cmd_clone(a):
    files = [Path(f) for f in a.files]
    for f in files:
        if not f.exists():
            die(f"not found: {f}")
    payload = [("name", a.name), ("description", "Demo video narration voice"),
               ("remove_background_noise", "true")]
    handles = [("files", (f.name, f.open("rb"))) for f in files]
    try:
        r = eleven("POST", f"{ELEVEN}/voices/add", headers={"xi-api-key": eleven_key()},
                          data=payload, files=handles, timeout=180)
    finally:
        for _, (_, h) in handles:
            h.close()
    if r.status_code != 200:
        die(f"ElevenLabs {r.status_code}: {r.text[:300]}")
    vid = r.json()["voice_id"]
    print(f"✓ cloned voice '{a.name}': {vid}\n  Add ELEVENLABS_VOICE_ID={vid} to .env, or set voice.voice_id in your shotlist.")


def tts(text: str, voice: dict, prev_text: str | None, next_text: str | None) -> bytes:
    voice_id = voice.get("voice_id") or os.getenv("ELEVENLABS_VOICE_ID")
    if not voice_id or voice_id == "PASTE_VOICE_ID":
        die("no ElevenLabs voice id. Run `demo.py voices` and set voice.voice_id in the shotlist.")
    body = {
        "text": text,
        "model_id": voice.get("model", DEFAULT_TTS_MODEL),
        "voice_settings": {
            "stability": voice.get("stability", 0.5),
            "similarity_boost": voice.get("similarity_boost", 0.8),
            "style": voice.get("style", 0.15),
            "use_speaker_boost": True,
        },
    }
    if voice.get("speed"):
        body["voice_settings"]["speed"] = voice["speed"]
    if prev_text:
        body["previous_text"] = prev_text   # keeps intonation consistent across scenes
    if next_text:
        body["next_text"] = next_text
    url = f"{ELEVEN}/text-to-speech/{voice_id}"
    headers = {"xi-api-key": eleven_key(), "Accept": "audio/mpeg"}
    params = {"output_format": "mp3_44100_128"}
    r = eleven("POST", url, params=params, headers=headers, json=body, timeout=180)
    if r.status_code == 400 and ("previous_text" in body or "next_text" in body):
        body.pop("previous_text", None)
        body.pop("next_text", None)
        r = eleven("POST", url, params=params, headers=headers, json=body, timeout=180)
    if r.status_code != 200:
        die(f"ElevenLabs {r.status_code}: {r.text[:400]}")
    return r.content


def long_gaps(path: Path, longest: float = 1.0) -> list[tuple[float, float]]:
    """Silences longer than `longest` seconds inside a clip (not at its ends): ElevenLabs sometimes inserts one."""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", f"silencedetect=noise=-38dB:d={longest}",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    durs = [float(x) for x in re.findall(r"silence_duration: ([\d.]+)", out)]
    total = ffprobe_duration(path)
    return [(at, d) for at, d in zip(starts, durs) if at > 0.1 and at + d < total - 0.1]


def cmd_voice(a):
    sl = load_shotlist(a.shotlist)
    adir = BUILD / "audio"
    adir.mkdir(parents=True, exist_ok=True)
    manifest_p = BUILD / "audio_manifest.json"
    manifest = read_json(manifest_p, {})
    scenes = sl["scenes"]
    voice = sl.get("voice", {})
    for i, s in enumerate(scenes):
        sid, text = s["id"], s["narration"].strip()
        dst = adir / f"{sid}.mp3"
        if a.own_audio:
            src = next((Path(a.own_audio) / f"{sid}{ext}" for ext in (".wav", ".mp3", ".m4a", ".aac", ".flac")
                        if (Path(a.own_audio) / f"{sid}{ext}").exists()), None)
            if not src:
                die(f"missing recording for scene '{sid}' in {a.own_audio}/")
            # trim leading/trailing silence, normalize, mp3
            run_ffmpeg(["-i", str(src), "-af",
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                        "silenceremove=start_periods=1:start_threshold=-45dB,areverse",
                        "-ar", "44100", "-ac", "2", "-b:a", "192k", str(dst)])
            manifest[sid] = "own:" + str(src)
            print(f"  ✓ {sid:<22} from {src}")
            continue
        key = hashlib.sha256(json.dumps([text, voice], sort_keys=True).encode()).hexdigest()
        if manifest.get(sid) == key and dst.exists() and not a.force:
            print(f"  · {sid:<22} unchanged, reusing")
            continue
        prev_t = scenes[i - 1]["narration"].strip() if i > 0 else None
        next_t = scenes[i + 1]["narration"].strip() if i + 1 < len(scenes) else None
        dst.write_bytes(tts(text, voice, prev_t, next_t))
        gaps = long_gaps(dst)
        if gaps:
            print(f"  ⚠ {sid}: silence of {', '.join(f'{g:.1f}s at {at:.1f}s' for at, g in gaps)} inside the clip."
                  f" Likely a generation glitch: delete \"{sid}\" from {manifest_p} and re-run to regenerate this scene only.")
        manifest[sid] = key
        manifest_p.write_text(json.dumps(manifest, indent=1))
        print(f"  ✓ {sid:<22} {words(text)} words")
    manifest_p.write_text(json.dumps(manifest, indent=1))
    timing = {s["id"]: round(ffprobe_duration(adir / f"{s['id']}.mp3"), 3) for s in scenes}
    (BUILD / "timing.json").write_text(json.dumps(timing, indent=1))
    print_summary(sl, timing)


# ───────────────────────────── record ─────────────────────────────

CURSOR_JS = r"""
(() => {
  if (document.getElementById('__demo_cursor')) return;
  const mount = () => {
    if (document.getElementById('__demo_cursor')) return;
    const st = document.createElement('style');
    st.textContent = `
      #__demo_cursor{position:fixed;left:0;top:0;width:26px;height:26px;z-index:2147483647;pointer-events:none;
        transition:transform 40ms linear;filter:drop-shadow(0 2px 3px rgba(0,0,0,.35))}
      .__demo_ripple{position:fixed;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;
        border:3px solid rgba(255,196,0,.95);z-index:2147483646;pointer-events:none;animation:__demoR .55s ease-out forwards}
      @keyframes __demoR{from{transform:scale(.3);opacity:1}to{transform:scale(1.4);opacity:0}}
      .__demo_hl{position:fixed;z-index:2147483645;pointer-events:none;border:3px solid #ffc400;border-radius:10px;
        box-shadow:0 0 0 6px rgba(255,196,0,.25);animation:__demoH 1.6s ease-in-out forwards}
      @keyframes __demoH{0%{opacity:0}15%{opacity:1}85%{opacity:1}100%{opacity:0}}
      #__demo_badge{position:fixed;left:24px;bottom:24px;z-index:2147483644;pointer-events:none;
        font:600 18px/1.3 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#fff;
        background:rgba(17,17,27,.82);padding:10px 16px;border-radius:999px;max-width:60vw;
        box-shadow:0 4px 18px rgba(0,0,0,.25);border:1px solid rgba(255,255,255,.12)}
      #__demo_badge b{color:#7ee2a8;margin-right:8px}`;
    document.documentElement.appendChild(st);
    const c = document.createElement('div');
    c.id = '__demo_cursor';
    c.innerHTML = '<svg viewBox="0 0 24 24" width="26" height="26"><path d="M4 2l16 9.5-7 1.6-3.6 6.9z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    document.documentElement.appendChild(c);
    const place = (x, y) => { c.style.transform = `translate(${x - 4}px, ${y - 2}px)`; };
    let saved = null;
    try { saved = JSON.parse(sessionStorage.getItem('__demo_pos')); } catch (e) {}
    saved ? place(saved.x, saved.y) : place(innerWidth / 2, innerHeight / 2);
    document.addEventListener('mousemove', e => {
      place(e.clientX, e.clientY);
      try { sessionStorage.setItem('__demo_pos', JSON.stringify({x: e.clientX, y: e.clientY})); } catch (_) {}
    }, true);
    document.addEventListener('mousedown', e => {
      const r = document.createElement('div'); r.className = '__demo_ripple';
      r.style.left = e.clientX + 'px'; r.style.top = e.clientY + 'px';
      document.documentElement.appendChild(r); setTimeout(() => r.remove(), 600);
    }, true);
  };
  if (document.documentElement) mount(); else document.addEventListener('DOMContentLoaded', mount);
})();
"""

BADGE_JS = r"""
(text) => {
  let b = document.getElementById('__demo_badge');
  if (!text) { if (b) b.remove(); return; }
  if (!b) { b = document.createElement('div'); b.id = '__demo_badge'; document.documentElement.appendChild(b); }
  b.innerHTML = '<b>PRD ✓</b>' + text.replace(/[<>&]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;'}[c]));
}
"""

RIPPLE_JS = r"""
([x, y]) => {
  const r = document.createElement('div'); r.className = '__demo_ripple';
  Object.assign(r.style, {left: x + 'px', top: y + 'px'});
  document.documentElement.appendChild(r); setTimeout(() => r.remove(), 600);
}
"""

# A stand-in for the native dropdown: the select's options listed under it, the current one ticked. Answers the
# centre of the row to pick (matched by value or label, as select_option does).
SELECT_MENU_JS = r"""
(sel, want) => {
  const r = sel.getBoundingClientRect(), opts = [...sel.options], rowH = 34;
  const m = document.createElement('div'); m.className = '__demo_menu';
  const below = innerHeight - r.bottom > opts.length * rowH + 16;
  Object.assign(m.style, {position: 'fixed', left: r.left + 'px', width: r.width + 'px', zIndex: 2147483643,
    top: below ? (r.bottom + 4) + 'px' : Math.max(8, r.top - 4 - opts.length * rowH - 8) + 'px',
    background: '#fff', border: '1px solid rgba(0,0,0,.15)', borderRadius: '8px', padding: '4px 0',
    boxShadow: '0 10px 28px rgba(0,0,0,.18)', font: getComputedStyle(sel).font, fontSize: '15px'});
  const st = document.createElement('style');
  st.textContent = '.__demo_menu div{height:34px;line-height:34px;padding:0 12px 0 30px;position:relative;' +
    'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#1a1b1e}' +
    '.__demo_menu .__cur::before{content:"✓";position:absolute;left:10px}' +
    '.__demo_menu .__hover{background:#1e6fd9;color:#fff}';
  m.appendChild(st);
  let target = null;
  opts.forEach((o, i) => {
    const d = document.createElement('div'); d.textContent = o.label;
    if (o.disabled) d.style.color = '#999';
    if (i === sel.selectedIndex) d.classList.add('__cur');
    if (!target && (o.value === want || o.label === want)) { d.classList.add('__on'); target = d; }
    m.appendChild(d);
  });
  document.documentElement.appendChild(m);
  if (!target) return null;
  const t = target.getBoundingClientRect();
  return {target: {x: t.left + Math.min(120, t.width / 2), y: t.top + t.height / 2}};
}
"""

# Editorial overlays (a title, a metric caption, evidence captions): positioned boxes over the page, owned by the video,
# never by the app. Called with the full {id: spec} map after every action, so they survive client-side navigation.
OVERLAY_JS = r"""
(map) => {
  const css = {
    'top-left': 'top:28px;left:28px', 'top-right': 'top:28px;right:28px', 'top-center': 'top:28px;left:50%;transform:translateX(-50%)',
    'bottom-left': 'bottom:28px;left:28px', 'bottom-right': 'bottom:28px;right:28px', 'bottom-center': 'bottom:28px;left:50%;transform:translateX(-50%)',
    'center': 'top:50%;left:50%;transform:translate(-50%,-50%)'};
  if (!document.getElementById('__demo_ov_style')) {
    const st = document.createElement('style'); st.id = '__demo_ov_style';
    st.textContent = `.__demo_ov{position:fixed;z-index:2147483640;pointer-events:none;box-sizing:border-box;
      font:500 19px/1.35 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#f4f4fb;
      background:rgba(20,21,43,.92);border:1px solid rgba(255,255,255,.14);border-radius:14px;padding:14px 20px;
      box-shadow:0 10px 30px rgba(10,10,30,.28);animation:__demoOv .45s ease-out both}
      .__demo_ov b{color:#a5f0c5;font-weight:700}.__demo_ov .k{display:block;font-size:13px;letter-spacing:.12em;
      text-transform:uppercase;color:#b9bcf5;font-weight:700;margin-bottom:4px}.__demo_ov .big{font-size:40px;font-weight:800;letter-spacing:-.01em;line-height:1.1}
      @keyframes __demoOv{from{opacity:0;translate:0 8px}to{opacity:1;translate:0 0}}`;
    document.documentElement.appendChild(st);
  }
  const want = new Set(Object.keys(map));
  document.querySelectorAll('.__demo_ov').forEach(e => { if (!want.has(e.dataset.id)) e.remove(); });
  for (const [id, s] of Object.entries(map)) {
    let el = document.querySelector(`.__demo_ov[data-id="${id}"]`);
    const sig = JSON.stringify(s);
    if (el && el.dataset.sig === sig) continue;
    if (!el) { el = document.createElement('div'); el.className = '__demo_ov'; el.dataset.id = id; document.documentElement.appendChild(el); }
    el.dataset.sig = sig;
    el.setAttribute('style', (css[s.pos || 'top-right'] || s.pos) + ';' + (s.style || ''));
    el.innerHTML = s.html;
  }
}
"""

# `page_scroll: minimal`: after an element is scrolled into view, undo any page-level scroll that the element does not
# need (its own scroll container already shows it). Long pages keep their scroll, because the target would leave view.
MIN_SCROLL_JS = r"""
(el) => {
  const se = document.scrollingElement, prev = se.scrollTop;
  if (!prev) return;
  se.scrollTop = 0;
  const r = el.getBoundingClientRect();
  if (r.top < 0 || r.bottom > innerHeight) se.scrollTop = prev;
}
"""

HIGHLIGHT_JS = r"""
(el, ms) => {
  const r = el.getBoundingClientRect(); const pad = 6;
  const d = document.createElement('div'); d.className = '__demo_hl';
  Object.assign(d.style, {left: (r.left - pad) + 'px', top: (r.top - pad) + 'px',
    width: (r.width + pad * 2) + 'px', height: (r.height + pad * 2) + 'px'});
  d.style.animationDuration = ms + 'ms';
  document.documentElement.appendChild(d); setTimeout(() => d.remove(), ms + 100);
}
"""


def card_html(s: dict, sl: dict) -> str:
    if s.get("html_file"):   # a hand-made card (e.g. an architecture diagram); it should hide #__demo_cursor itself
        return Path(s["html_file"]).read_text()
    esc = lambda t: str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    theme = sl.get("card_theme", {})
    bg = theme.get("background", "radial-gradient(1200px 700px at 20% 10%, #2b2f77 0%, #0f1024 55%, #07070f 100%)")
    accent = theme.get("accent", "#7ee2a8")
    lines = "".join(f"<li>{esc(l)}</li>" for l in s.get("lines", []) or [])
    sub = f"<p class='sub'>{esc(s['subtitle'])}</p>" if s.get("subtitle") else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;height:100%;background:{bg};color:#f4f4fb;
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}}
.wrap{{height:100%;display:flex;flex-direction:column;justify-content:center;padding:0 9vw;box-sizing:border-box}}
.kicker{{color:{accent};font-weight:700;letter-spacing:.14em;text-transform:uppercase;font-size:1.6vw;margin:0 0 1.2vw}}
h1{{font-size:5.2vw;line-height:1.05;margin:0;font-weight:800;letter-spacing:-.02em;max-width:80vw}}
.sub{{font-size:2.1vw;color:#c9cbe6;margin:1.6vw 0 0;max-width:70vw;line-height:1.35}}
ul{{list-style:none;padding:0;margin:3vw 0 0;display:grid;gap:1.1vw}}
li{{font-size:1.8vw;color:#e6e7f5;padding-left:2.2vw;position:relative}}
li:before{{content:"";position:absolute;left:0;top:.62em;width:.9vw;height:.9vw;border-radius:50%;background:{accent}}}
.wrap>*{{opacity:0;transform:translateY(14px);animation:in .7s ease-out forwards}}
.wrap>*:nth-child(2){{animation-delay:.15s}}.wrap>*:nth-child(3){{animation-delay:.3s}}.wrap>*:nth-child(4){{animation-delay:.45s}}
@keyframes in{{to{{opacity:1;transform:none}}}}
#__demo_cursor{{display:none!important}}
</style></head><body><div class="wrap">
<p class="kicker">{esc(sl.get('project', ''))}</p><h1>{esc(s.get('title', ''))}</h1>{sub}<ul>{lines}</ul>
</div></body></html>"""


def _sub_run(v, run_id: str):
    """Replaces `{{run}}` in every string of an action, e.g. a fresh sign-up email for each take."""
    if isinstance(v, str):
        return v.replace("{{run}}", run_id)
    if isinstance(v, dict):
        return {k: _sub_run(x, run_id) for k, x in v.items()}
    if isinstance(v, list):
        return [_sub_run(x, run_id) for x in v]
    return v


class Director:
    """Runs scene actions with a visible, human-paced cursor."""

    def __init__(self, page, base_url: str, viewport: dict, show_req: bool):
        self.page, self.base, self.show_req = page, base_url, show_req
        self.pos = (viewport["width"] / 2, viewport["height"] / 2)
        self.badge = ""
        self.scene_t0 = 0.0
        self.min_scroll = False   # `page_scroll: minimal` in the shot list
        self.ov: dict = {}   # editorial overlays by id (the `overlay` action)
        self.run_id = time.strftime("%m%d%H%M%S")   # `{{run}}` in any action text: unique per check/record run

    def overlays(self):
        try:
            self.page.evaluate(CURSOR_JS)
            self.page.evaluate(BADGE_JS, self.badge if self.show_req else "")
            self.page.evaluate(OVERLAY_JS, self.ov)
        except Exception:
            pass  # page mid-navigation; next action re-applies

    def move_to(self, x: float, y: float):
        # Playwright's `steps` fires every point back to back, so the glide is timed here: 0.4-1.1 s by
        # distance, eased in and out, the way a hand moves a mouse.
        x0, y0 = self.pos
        dist = ((x - x0) ** 2 + (y - y0) ** 2) ** 0.5
        dur = min(1.1, 0.4 + dist / 1500)
        n = max(12, int(dur * 60))
        for i in range(1, n + 1):
            t = i / n
            e = t * t * (3 - 2 * t)
            self.page.mouse.move(x0 + (x - x0) * e, y0 + (y - y0) * e)
            self.page.wait_for_timeout(dur * 1000 / n)
        self.pos = (x, y)

    def target(self, sel: str):
        loc = self.page.locator(sel).first
        loc.wait_for(state="visible", timeout=15000)
        loc.scroll_into_view_if_needed(timeout=5000)
        if self.min_scroll:
            # `page_scroll: minimal`: an app card with its own scrolling thread can make the browser scroll the whole
            # page too, pushing the header off screen. Snap the page back to the top when the target stays in view.
            loc.evaluate(MIN_SCROLL_JS)
        box = loc.bounding_box()
        return loc, box

    def settle(self):
        try:
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass

    def run(self, act):
        p = self.page
        if isinstance(act, str):
            act = {act: None}
        act = _sub_run(act, self.run_id)
        (kind, arg), = act.items()
        if kind == "goto":
            p.goto(urljoin(self.base, str(arg)), wait_until="domcontentloaded", timeout=45000)
            try:
                p.wait_for_load_state("networkidle", timeout=6000)
            except Exception:
                pass
        elif kind == "click":
            loc, box = self.target(arg)
            if box:
                self.move_to(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                p.wait_for_timeout(350)
                p.mouse.click(*self.pos)
            else:
                loc.click()
            self.settle()
        elif kind == "double_click":
            # Two real clicks ~90 ms apart, each with a ripple: shows a double tap (e.g. an idempotent Pay button).
            loc, box = self.target(arg)
            if box:
                self.move_to(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                p.wait_for_timeout(350)
                p.mouse.click(*self.pos)
                p.wait_for_timeout(90)
                p.mouse.click(*self.pos)
            else:
                loc.dblclick()
            self.settle()
        elif kind == "hover":
            _, box = self.target(arg)
            if box:
                self.move_to(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        elif kind == "type":
            loc, box = self.target(arg["selector"])
            if box:
                self.move_to(box["x"] + min(40, box["width"] / 2), box["y"] + box["height"] / 2)
                p.wait_for_timeout(120)
                p.mouse.click(*self.pos)
            loc.fill("")
            p.keyboard.type(str(arg["text"]), delay=int(arg.get("delay_ms", 45)))
        elif kind == "press":
            p.keyboard.press(str(arg))
            self.settle()
        elif kind == "select":
            # Chromium draws a native <select> menu outside the page, so the screencast never shows it. Draw a
            # look-alike list under the field, glide to the option, light it up, then pick it for real.
            loc, box = self.target(arg["selector"])
            want = str(arg["value"])
            if box:
                self.move_to(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                p.wait_for_timeout(250)
                p.evaluate(RIPPLE_JS, [self.pos[0], self.pos[1]])
                rows = loc.evaluate(SELECT_MENU_JS, want)
                p.wait_for_timeout(450)
                if rows and rows.get("target"):
                    t = rows["target"]
                    self.move_to(t["x"], t["y"])
                    p.evaluate("() => document.querySelector('.__demo_menu .__on')?.classList.add('__hover')")
                    p.wait_for_timeout(350)
                    p.evaluate(RIPPLE_JS, [self.pos[0], self.pos[1]])
                    p.wait_for_timeout(200)
                p.evaluate("() => document.querySelector('.__demo_menu')?.remove()")
            loc.select_option(want)
        elif kind == "scroll":
            if isinstance(arg, dict):
                p.evaluate("y => window.scrollBy({top: y, behavior: 'smooth'})", int(arg.get("y", 500)))
            else:
                p.locator(arg).first.evaluate("e => e.scrollIntoView({behavior: 'smooth', block: 'center'})")
            p.wait_for_timeout(900)
        elif kind == "highlight":
            # `highlight: SEL` holds 2.5 s; `highlight: {selector: SEL, seconds: N}` holds N. The next action waits for it.
            sel, secs = (arg["selector"], float(arg.get("seconds", 2.5))) if isinstance(arg, dict) else (arg, 2.5)
            loc, _ = self.target(sel)
            loc.evaluate(HIGHLIGHT_JS, int(secs * 1000))
            p.wait_for_timeout(int(secs * 1000))
        elif kind == "wait":
            p.wait_for_timeout(int(float(arg) * 1000))
        elif kind == "wait_for":
            p.locator(arg).first.wait_for(state="visible", timeout=60000)
        elif kind == "wait_gone":
            # e.g. a typing indicator or spinner: wait until it is hidden or detached (up to 60 s)
            p.locator(arg).first.wait_for(state="hidden", timeout=60000)
        elif kind == "upload":
            # `upload: {selector: 'input[type=file]', file: path, click: 'button:has-text("Choose")'}`. The cursor glides to
            # and taps the visible picker button (`click`, optional), then the file is set on the input directly, so no
            # native file dialog ever opens (it would not be in the screencast anyway).
            if arg.get("click"):
                _, box = self.target(arg["click"])
                if box:
                    self.move_to(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                    p.wait_for_timeout(250)
                    p.evaluate(RIPPLE_JS, [self.pos[0], self.pos[1]])
                    p.wait_for_timeout(300)
            p.locator(arg["selector"]).first.set_input_files(str(arg["file"]), timeout=15000)
            self.settle()
        elif kind == "eval":
            # Off-camera setup only (put it in `before`): runs page JS and waits for a returned promise.
            p.evaluate(str(arg))
        elif kind == "overlay":
            # `overlay: {id: x, html: "...", pos: top-right|top-left|bottom-left|center|..., style: "css"}` shows or
            # replaces one; `overlay: {id: x, remove: true}` removes it; `overlay: clear` removes all.
            if arg == "clear":
                self.ov = {}
            elif arg.get("remove"):
                self.ov.pop(arg["id"], None)
            else:
                self.ov[arg["id"]] = {"html": arg["html"], "pos": arg.get("pos", "top-right"), "style": arg.get("style", "")}
        elif kind == "at":
            remaining = self.scene_t0 + AUDIO_LEAD + float(arg) - time.monotonic()
            if remaining > 0:
                p.wait_for_timeout(int(remaining * 1000))
        else:
            raise ValueError(f"unknown action '{kind}'")
        self.overlays()


def record(sl: dict, timing: dict, headed: bool, dry: bool) -> list[dict]:
    from playwright.sync_api import sync_playwright
    vp = sl["viewport"]
    base = sl.get("url") or die("shotlist has no url")
    cap_dir = BUILD / "capture"
    if not dry:
        shutil.rmtree(cap_dir, ignore_errors=True)
        cap_dir.mkdir(parents=True)
    failures = []
    marks = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=not headed)

        def open_page(auth: dict | None):
            kw = {"viewport": vp, "device_scale_factor": 1}
            st = (auth or {}).get("storage_state")
            if st:
                if not Path(st).exists():
                    die(f"auth storage_state {st} not found. Run `demo.py login --url ...`.")
                kw["storage_state"] = st
            c = browser.new_context(**kw)
            c.add_init_script(CURSOR_JS)
            return c, c.new_page()

        # One browser context per named page: "main" (the shot list's `auth`) plus any under `pages:`, e.g. a staff
        # session beside a family one. A scene picks its page with `page: <name>`; only the page on camera is cast.
        ctxs, pages = {}, {}
        ctxs["main"], pages["main"] = open_page(sl.get("auth"))
        for name, cfg in (sl.get("pages") or {}).items():
            ctxs[name], pages[name] = open_page((cfg or {}).get("auth"))
        frames: list = []
        casts = {} if dry else {n: Screencast(ctxs[n], pages[n], vp, cap_dir, frames) for n in pages}
        active = "main"
        if casts:
            casts[active].start()
        ctx, page = ctxs["main"], pages["main"]
        cast = casts.get("main")
        d = Director(page, base, vp, sl.get("show_requirement", True))
        d.min_scroll = sl.get("page_scroll") == "minimal"
        for s in sl["scenes"]:
            sid = s["id"]
            print(f"  ▶ {sid}")
            want = s.get("page", "main")
            if want not in pages:
                die(f"scene {sid}: page '{want}' is not defined under `pages:`")
            if want != active:
                if casts:
                    casts[active].stop()
                    casts[want].start()
                active, page = want, pages[want]
                d.page = page
                d.pos = (vp["width"] / 2, vp["height"] / 2)
            d.badge = ""
            broken = False
            for act in s.get("before", []) or []:
                try:
                    d.run(act)
                except Exception as e:
                    failures.append(failure(page, sid, "before", act, e))
                    print(f"    ✖ before {act}: {str(e).splitlines()[0]}")
                    broken = True
                    break
            if broken:
                if dry:
                    continue
                break
            if s.get("type") == "card":
                page.set_content(card_html(s, sl), wait_until="load")
            d.badge = s.get("requirement", "") or ""
            d.overlays()
            page.wait_for_timeout(250 if not dry else 0)
            d.scene_t0 = time.monotonic()
            start = time.time()
            for act in s.get("actions", []) or []:
                try:
                    d.run(act)
                except Exception as e:
                    failures.append(failure(page, sid, "action", act, e))
                    print(f"    ✖ {act}: {str(e).splitlines()[0]}")
                    break  # later actions in this scene depend on this one
            if failures and not dry:
                break
            if not dry:
                need = timing[sid] + AUDIO_LEAD + SCENE_TAIL
                left = d.scene_t0 + need - time.monotonic()
                if left > 0:
                    page.wait_for_timeout(int(left * 1000))
                elif left < -0.3:
                    print(f"    ⚠ actions ran {-left:.1f}s past the narration; that part will be silent")
            marks.append({"id": sid, "start": start, "end": time.time()})
        if casts:
            page.wait_for_timeout(300)
            casts[active].stop()
        for c in ctxs.values():
            c.close()
        browser.close()
        if not dry and not failures:
            if not frames:
                die("the browser produced no frames")
            frames.sort(key=lambda f: f[0])
            t_first = frames[0][0]
            until = marks[-1]["end"] + 0.5 if marks else None
            for m in marks:
                m["start"] = round(m["start"] - t_first, 3)
                m["end"] = round(m["end"] - t_first, 3)
            print(f"  encoding {len(frames)} captured frames ...")
            frames_to_video(frames, BUILD / "raw.mp4", vp, until)
            (BUILD / "marks.json").write_text(json.dumps(marks, indent=1))
    return failures


class Screencast:
    """Capture frames over the DevTools screencast. Every frame carries a wall-clock timestamp,
    so the rebuilt video shares a clock with the scene marks (Playwright's own recorder drifts)."""

    def __init__(self, ctx, page, vp: dict, out_dir: Path, frames: list | None = None):
        # `frames` may be shared by several pages' casts; only the page on camera is started at any moment.
        self.dir, self.frames, self.vp = out_dir, (frames if frames is not None else []), vp
        self.cdp = ctx.new_cdp_session(page)
        self.cdp.on("Page.screencastFrame", self._on_frame)

    def start(self):
        self.cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 90, "everyNthFrame": 1,
                                                "maxWidth": self.vp["width"], "maxHeight": self.vp["height"]})

    def _on_frame(self, p):
        path = self.dir / f"{len(self.frames):06d}.jpg"
        path.write_bytes(base64.b64decode(p["data"]))
        self.frames.append((p.get("metadata", {}).get("timestamp") or time.time(), path))
        try:
            self.cdp.send("Page.screencastFrameAck", {"sessionId": p["sessionId"]})
        except Exception:
            pass

    def stop(self):
        try:
            self.cdp.send("Page.stopScreencast")
        except Exception:
            pass


def frames_to_video(frames: list, out: Path, vp: dict, until: float | None = None) -> None:
    """Frames only arrive when the screen changes; hold each until the next one."""
    frames = sorted(frames, key=lambda f: f[0])
    lst = out.with_suffix(".frames.txt")
    lines = []
    for i, (ts, path) in enumerate(frames):
        dur = (frames[i + 1][0] - ts) if i + 1 < len(frames) else max(2.0, (until or 0) - ts)
        lines.append(f"file '{path.resolve()}'\nduration {max(dur, 0.001):.4f}\n")
    lines.append(f"file '{frames[-1][1].resolve()}'\n")
    lst.write_text("".join(lines))
    W, H = vp["width"] - vp["width"] % 2, vp["height"] - vp["height"] % 2
    run_ffmpeg(["-f", "concat", "-safe", "0", "-i", str(lst),
                "-vf", f"fps={FPS},scale={W}:{H}:flags=lanczos,format=yuv420p",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", str(out)])


def failure(page, sid, where, act, e) -> dict:
    snap = None
    try:
        snap = page.evaluate(SCRAPE_JS)
        snap["url"] = page.url
    except Exception:
        pass
    return {"scene": sid, "where": where, "action": act, "error": str(e).splitlines()[0][:300], "page_at_failure": snap}


def report(failures: list[dict]) -> None:
    print("\nProblems:")
    for f in failures:
        print(f"  ✖ [{f['scene']}] {f['where']} {f['action']}\n      {f['error']}")


def cmd_check(a):
    sl = load_shotlist(a.shotlist)
    print("Dry run:")
    with dev_server(sl):
        failures = record(sl, {}, a.headed, dry=True)
    out = BUILD / "failures.json"
    if not failures:
        out.unlink(missing_ok=True)
        print("\n✓ every action ran")
        return
    report(failures)
    out.write_text(json.dumps(failures, indent=1))
    print(f"\n{out} has each failure with the page's elements at that moment (page_at_failure).")
    sys.exit(1)


def cmd_record(a):
    sl = load_shotlist(a.shotlist)
    timing = read_json(BUILD / "timing.json", None)
    if not timing or any(s["id"] not in timing for s in sl["scenes"]):
        die("no audio timing for every scene. Run `demo.py voice` first.")
    print("Recording:")
    with dev_server(sl):
        failures = record(sl, timing, a.headed, dry=False)
    if failures:
        report(failures)
        die("recording stopped. Run `demo.py check`, fix the scenes, then record again")
    print(f"✓ {BUILD/'raw.mp4'}")


def cmd_frames(a):
    marks = read_json(BUILD / "marks.json", None)
    raw = BUILD / "raw.mp4"
    if not marks or not raw.exists():
        die("nothing recorded yet")
    fdir = BUILD / "frames"
    shutil.rmtree(fdir, ignore_errors=True)
    fdir.mkdir()
    for i, m in enumerate(marks):
        for label, frac in (("mid", 0.4), ("end", 0.9)):
            t = m["start"] + (m["end"] - m["start"]) * frac
            out = fdir / f"{i:02d}_{m['id']}_{label}.png"
            run_ffmpeg(["-ss", f"{t:.2f}", "-i", str(raw), "-frames:v", "1", "-vf", "scale=1280:-2", str(out)])
    print(f"✓ {len(marks) * 2} frames in {fdir}/  (one mid-scene, one at the end of each scene)")


# ───────────────────────────── assemble ─────────────────────────────

def srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def caption_chunks(text: str, max_words: int = 9) -> list[str]:
    out, cur = [], []
    for w in text.split():
        cur.append(w)
        if len(cur) >= max_words or (len(cur) >= 4 and w[-1] in ".,;:?!—"):
            out.append(" ".join(cur))
            cur = []
    if cur:
        out.append(" ".join(cur))
    return out


def ffmpeg_has_filter(name: str) -> bool:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    return any(len(l.split()) > 1 and l.split()[1] == name for l in out.splitlines())


CAPTION_HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:transparent;width:%dpx;height:%dpx;overflow:hidden}
.c{position:absolute;left:50%%;bottom:84px;transform:translateX(-50%%);max-width:72%%;text-align:center;
  font:500 26px/1.32 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#fff;
  background:rgba(10,16,24,.80);padding:8px 18px;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,.25)}
</style></head><body><div class="c"></div></body></html>"""


# With `caption_band` the app keeps the whole recorded frame and the captions live in a strip added below it,
# so they never cover the UI (chat composers and primary buttons sit at the bottom of most screens).
BAND_HTML = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:transparent;width:%dpx;height:%dpx;overflow:hidden}
.band{position:absolute;left:0;right:0;bottom:0;height:%dpx}
.c{position:absolute;left:50%%;top:50%%;transform:translate(-50%%,-50%%);max-width:74%%;text-align:center;white-space:nowrap;
  font:500 25px/1.3 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#f4f4fb}
.l{position:absolute;left:28px;top:50%%;transform:translateY(-50%%);font:700 13px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
  letter-spacing:.12em;text-transform:uppercase;color:%s;border:1px solid currentColor;border-radius:999px;padding:7px 12px;opacity:.9}
</style></head><body><div class="band"><span class="l">%s</span><div class="c"></div></div></body></html>"""


def caption_track(cues: list, W: int, H: int, out_dir: Path, band: dict | None = None) -> Path:
    """One transparent full-frame PNG per caption (plus a blank), sequenced by a concat list whose
    durations follow the cue times, so a single `overlay` burns them in. Captions sit above the PRD badge,
    or inside the caption band when the shot list has one (H is then the padded height)."""
    from playwright.sync_api import sync_playwright
    shutil.rmtree(out_dir, ignore_errors=True)
    out_dir.mkdir(parents=True)
    blank = out_dir / "blank.png"
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        if band:
            esc = lambda t: str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            pg.set_content(BAND_HTML % (W, H, int(band.get("height", 80)), band.get("label_color", "#a5f0c5"),
                                        esc(band.get("label", ""))))
            if not band.get("label"):
                pg.evaluate("() => document.querySelector('.l').remove()")
        else:
            pg.set_content(CAPTION_HTML % (W, H))
        pg.evaluate("() => document.querySelector('.c').style.display = 'none'")
        pg.screenshot(path=str(blank), omit_background=True)
        pg.evaluate("() => document.querySelector('.c').style.display = ''")
        for i, (_, _, text) in enumerate(cues):
            pg.evaluate("t => document.querySelector('.c').textContent = t", text)
            pg.screenshot(path=str(out_dir / f"{i:04d}.png"), omit_background=True)
        b.close()
    lines, clock = [], 0.0
    for i, (s, e, _) in enumerate(cues):
        if s > clock + 0.001:
            lines.append(f"file '{blank.resolve()}'\nduration {s - clock:.3f}\n")
        lines.append(f"file '{(out_dir / f'{i:04d}.png').resolve()}'\nduration {e - s:.3f}\n")
        clock = e
    tail = 600.0 if band else 1.0   # the band label must outlast the video; the output length is pinned with -t
    lines.append(f"file '{blank.resolve()}'\nduration {tail:.3f}\nfile '{blank.resolve()}'\n")
    lst = out_dir / "captions.txt"
    lst.write_text("".join(lines))
    print(f"  ✓ {len(cues)} caption frames drawn")
    return lst


def cmd_assemble(a):
    sl = load_shotlist(a.shotlist)
    marks = read_json(BUILD / "marks.json", None)
    timing = read_json(BUILD / "timing.json", None)
    raw = BUILD / "raw.mp4"
    if not marks or not raw.exists() or not timing:
        die("nothing recorded yet. Run `demo.py record` first.")
    W, H = sl["viewport"]["width"], sl["viewport"]["height"]
    W, H = W - W % 2, H - H % 2
    segdir = BUILD / "segments"
    shutil.rmtree(segdir, ignore_errors=True)
    segdir.mkdir()
    lead_ms = int(AUDIO_LEAD * 1000)
    seg_files, srt, cues, clock, n = [], [], [], 0.0, 1
    narr = {s["id"]: s["narration"].strip() for s in sl["scenes"]}
    for i, m in enumerate(marks):
        dur = m["end"] - m["start"]
        seg = segdir / f"{i:02d}_{m['id']}.mp4"
        run_ffmpeg([
            "-ss", f"{m['start']:.3f}", "-i", str(raw),
            "-i", str(BUILD / "audio" / f"{m['id']}.mp3"),
            "-t", f"{dur:.3f}", "-map", "0:v:0", "-map", "1:a:0",
            "-vf", f"fps={FPS},scale={W}:{H}:flags=lanczos,format=yuv420p",
            "-af", f"adelay={lead_ms}|{lead_ms},apad,aresample=44100",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k", "-ac", "2", str(seg)])
        seg_files.append(seg)
        # captions spread across the spoken part, weighted by length
        chunks = caption_chunks(narr[m["id"]])
        spoken = timing[m["id"]]
        total_chars = sum(len(c) for c in chunks) or 1
        t = clock + AUDIO_LEAD
        for c in chunks:
            d = spoken * len(c) / total_chars
            srt.append(f"{n}\n{srt_time(t)} --> {srt_time(t + d)}\n{c}\n")
            cues.append((t, t + d, c))
            n += 1
            t += d
        clock += dur
        print(f"  ✓ {m['id']:<22} {dur:5.1f}s")
    lst = segdir / "list.txt"
    lst.write_text("".join(f"file '{f.resolve()}'\n" for f in seg_files))
    joined = BUILD / "joined.mp4"
    run_ffmpeg(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(joined)])
    out = Path(a.out or sl.get("output") or BUILD.parent / f"{slug(sl.get('project', 'demo'))}_demo.mp4")
    srt_path = out.with_suffix(".srt")
    srt_path.write_text("\n".join(srt))
    afilter = "loudnorm=I=-16:TP=-1.5:LRA=11"
    band = sl.get("caption_band")
    if band:
        # Pad the recorded frame with a strip below it; captions (if --subs) and the band label are drawn into it.
        bh = int(band.get("height", 80))
        bg = band.get("background", "#14152b")
        caps = caption_track(cues if a.subs else [], W, H + bh, BUILD / "captions", band)
        run_ffmpeg(["-i", str(joined), "-f", "concat", "-safe", "0", "-i", str(caps),
                    "-filter_complex", f"[0:v]pad={W}:{H + bh}:0:0:color={bg}[p];[1:v]format=rgba[c];"
                                       f"[p][c]overlay=0:0:eof_action=pass:shortest=0,format=yuv420p[v]",
                    "-map", "[v]", "-map", "0:a", "-af", afilter, "-t", f"{ffprobe_duration(joined):.3f}",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS),
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
    elif a.subs and not ffmpeg_has_filter("subtitles"):
        # This ffmpeg has no libass (Homebrew's 8.x build ships without it): draw the captions as
        # transparent PNGs in Chromium and overlay them, which needs only the core `overlay` filter.
        print("  ffmpeg has no `subtitles` filter; drawing captions with Chromium + overlay")
        caps = caption_track(cues, W, H, BUILD / "captions")
        run_ffmpeg(["-i", str(joined), "-f", "concat", "-safe", "0", "-i", str(caps),
                    "-filter_complex", "[1:v]format=rgba[c];[0:v][c]overlay=0:0:eof_action=pass:shortest=0,format=yuv420p[v]",
                    "-map", "[v]", "-map", "0:a", "-af", afilter,
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS),
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
    elif a.subs:
        style = "FontName=Arial,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,BorderStyle=3,Outline=1,Shadow=0,MarginV=40"
        sub_arg = str(srt_path.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
        run_ffmpeg(["-i", str(joined), "-vf", f"subtitles='{sub_arg}':force_style='{style}'",
                    "-af", afilter, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
    else:
        run_ffmpeg(["-i", str(joined), "-af", afilter, "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(out)])
    total = ffprobe_duration(out)
    print(f"\n✓ {out}  ({fmt_t(total)})   captions: {srt_path}")
    length_warning(total)


def cmd_render(a):
    cmd_voice(a)
    cmd_record(a)
    cmd_assemble(a)


# ───────────────────────────── login ─────────────────────────────

def cmd_login(a):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=False)
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        page = ctx.new_page()
        page.goto(a.url)
        input("Log in in the browser window, then press Enter here to save the session... ")
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        ctx.storage_state(path=a.out)
        b.close()
    print(f"✓ saved {a.out}. Add to your shotlist:\nauth:\n  storage_state: {a.out}")


# ───────────────────────────── init / setup ─────────────────────────────

def cmd_setup(a):
    req = Path(__file__).with_name("requirements.txt")
    vpy = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not vpy.exists():
        print(f"Creating private environment {VENV} ...")
        VENV.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
    print("Installing Python packages ...")
    subprocess.run([str(vpy), "-m", "pip", "install", "-q", "--upgrade", "pip"], check=False)
    if subprocess.run([str(vpy), "-m", "pip", "install", "-q", "-r", str(req)]).returncode != 0:
        die("pip install failed (see above)")
    print("Installing Chromium for Playwright ...")
    subprocess.run([str(vpy), "-m", "playwright", "install", "chromium"], check=False)
    for tool in ("ffmpeg", "ffprobe"):
        print(f"  {'✓' if shutil.which(tool) else '✖ missing'} {tool}")
    if not shutil.which("ffmpeg"):
        print("    install: brew install ffmpeg | sudo apt install ffmpeg | winget install ffmpeg")
    ensure_demo_dir()
    has_key = bool(os.getenv("ELEVENLABS_API_KEY"))
    print(f"  {'✓' if has_key else '✖'} ELEVENLABS_API_KEY {'found' if has_key else 'missing: add it to .demo/.env'}")
    print(f"  {'✓' if os.getenv('ELEVENLABS_VOICE_ID') else '·'} ELEVENLABS_VOICE_ID "
          f"{'found' if os.getenv('ELEVENLABS_VOICE_ID') else '(optional here; or set voice.voice_id in the shot list)'}")
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", ".demo/.env"], capture_output=True)
    if tracked.returncode == 0:
        print("  ⚠ .demo/.env is tracked by git! Run: git rm --cached .demo/.env  (and rotate the key)")


def main():
    load_dotenv()
    ap = argparse.ArgumentParser(prog="demo.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("context", help="repo inventory + live site map for writing the shot list")
    p.add_argument("--url", required=True, help="where the app runs (local dev URL or deployed)")
    p.add_argument("--repo", help="repo root to inventory, usually .")
    p.add_argument("--prd", help="PRD file outside the repo (design docs inside --repo are found automatically)")
    p.add_argument("--dev", help='command that starts the app, e.g. "npm run dev" (started only if --url is down)')
    p.add_argument("--pages", type=int, default=8, help="max same-site pages to map")
    p.add_argument("--auth", help="storage_state json from `login`, for apps behind a login")
    p.set_defaults(fn=cmd_context)

    for name, fn, h in [("export", cmd_export, "narration script -> build/script.md + .txt"),
                        ("check", cmd_check, "dry-run all actions; failures -> build/failures.json"),
                        ("voice", cmd_voice, "generate narration audio per scene"),
                        ("record", cmd_record, "record the browser, timed to the audio"),
                        ("assemble", cmd_assemble, "cut, sync, and export the final MP4"),
                        ("render", cmd_render, "voice + record + assemble"),
                        ("frames", cmd_frames, "still frames per scene for review")]:
        p = sub.add_parser(name, help=h)
        p.add_argument("shotlist", nargs="?", default=None)
        p.add_argument("--headed", action="store_true", help="show the browser window")
        p.add_argument("--own-audio", help="folder of your own recordings named <scene id>.wav|mp3|m4a")
        p.add_argument("--force", action="store_true", help="regenerate audio even if unchanged")
        p.add_argument("--subs", action="store_true", help="burn captions into the video")
        p.add_argument("--out", help="output video path")
        p.set_defaults(fn=fn)

    p = sub.add_parser("setup", help="install deps + Chromium, check ffmpeg and keys")
    p.set_defaults(fn=cmd_setup)
    p = sub.add_parser("voices", help="list ElevenLabs voices")
    p.set_defaults(fn=cmd_voices)
    p = sub.add_parser("clone", help="ElevenLabs instant voice clone from samples")
    p.add_argument("--name", required=True)
    p.add_argument("--files", nargs="+", required=True)
    p.set_defaults(fn=cmd_clone)
    p = sub.add_parser("login", help="log in by hand and save the session for recording")
    p.add_argument("--url", required=True)
    p.add_argument("--out", default=".demo/auth.json")
    p.set_defaults(fn=cmd_login)

    a = ap.parse_args()
    if hasattr(a, "shotlist"):
        a.shotlist = resolve_shotlist(a.shotlist)
        set_workdir(a.shotlist)
    else:
        set_workdir(DEFAULT_SHOTLIST)
    a.fn(a)


if __name__ == "__main__":
    main()
