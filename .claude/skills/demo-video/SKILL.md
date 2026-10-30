---
name: demo-video
description: Create a narrated demo video (MP4, four to five minutes, never under three and a half) of a web app for hiring partners, recruiters, or a portfolio. It reads the repo's PRD, design docs, and code, has Codex write a product-focused, story-driven narration, drives the running app in a browser with a visible cursor, voices the narration with ElevenLabs, and assembles it with ffmpeg, captions and title cards included. Use this whenever the user wants a demo video, product walkthrough, screen recording with voiceover, project showcase video, or a video for a job application, hiring partner, or Gauntlet-style project submission, even if they just say "record my project" or "make a video of this app".
compatibility: Needs shell access on a machine that can reach the app (Claude Code or Cowork, not claude.ai chat). Requires Python 3.10+, ffmpeg, the Codex CLI (`codex`), and an ElevenLabs API key in .demo/.env.
---

# Demo video

> **This project's copy (inno-tariff-slm, adapted 2026-10-30).** Copied from `Gauntlet AI/.claude/skills/demo-video/`
> and adapted for a **concept-stage** early-submission video (Gauntlet Week 7). There is no running app yet: the
> "app" is the vision page `Gauntlet AI/docs/research/tariff-compliance-vision.html`, served with
> `python3 -m http.server 8811 --directory "../Gauntlet AI/docs/research"` at
> `http://127.0.0.1:8811/tariff-compliance-vision.html` (no login). Design docs to read in step 2:
> `Gauntlet AI/docs/planning/tariff-*.md` (PRD, behavior and evals, data and training, architecture, execution plan,
> concept-video outline) and `docs/data/README.md`. The video goes to `docs/artifacts/2026-10-30-concept-video.mp4`
> and the narration to `docs/delivery/2026-10-30-concept-narration.md`. Follow **Concept-stage mode** below wherever it
> differs from the product-demo defaults.

## Concept-stage mode (this project, 2026-10-30)

Use it while nothing is trained or built, at Innocent's instruction ("this is more of a conceptual introduction").

- **Length:** the brief asks for 3 to 5 minutes. Aim for **4:00 to 4:40** (about 600 to 650 words at 150 words per
  minute); 3:30 is still the floor.
- **Story arc, in this order:** hook card (the importer's moment) → the problem (page §1) → the product vision (§2) →
  the mock walkthrough (§3, told as hand-written target outputs, never as a running model) → why a trained small model
  and the behavior spec (§5) → the training data (§6) → the proposed architecture (§7) → the evaluation plan (§8) →
  roadmap and honest status (§9–§10) → outro card. The page's own diagrams replace hand-made overview and architecture
  cards. No technical-challenges segment: nothing is built yet, so there are no solved challenges to tell.
- **Claim rule, stricter than product videos:** every claim keeps its page label. Published or measured facts are said
  as facts; the specialist's ability is a hypothesis; the architecture and pipeline are proposed; experiments are not run
  yet; the mock's outputs are hand-written; the business value is unmeasured. The narration must say plainly that no
  model is trained and that this package doesn't yet meet the early-submission evidence bar.
- **Picture:** turn on the page's **Present** mode in the first page scene; scroll to section ids; drive the mock with
  `#scen button >> nth=N` and `#steps button >> nth=N`; select architecture nodes with `#arch g.node[data-id="…"]`.
- **Evidence fields** point at the planning docs and `docs/data/README.md` instead of app source files.


You plan the video, Codex writes the narration, and the script `scripts/demo.py` produces it. You decide what to show, brief Codex and check its narration (step 4a), choose the clicks, verify every claim against the code, and review the result. The script crawls the app, dry-runs your clicks, generates the voice, records the browser in sync with the voice, and cuts the MP4.

Call the script by its absolute path from the **repo root**: `python <this skill's dir>/scripts/demo.py <command>`. Below, `demo.py` means that full command. Everything it writes goes in `.demo/`. `.demo/shotlist.yaml` is the reviewable source of the video and is meant to be committed. Build output, audio, video, and keys are git-ignored.

The human stays in the loop at two points. They approve the narration script before any audio is generated, because ElevenLabs costs credits and the words are theirs. And you ask before changing app source code, such as adding a `data-testid`. Everything else you can do on your own.

## 0. Gauntlet: the original, and how each project adapts it

This is the **original** (`Gauntlet AI/.claude/skills/demo-video/`). A project copies the whole folder into its own `.claude/skills/demo-video/` and adapts the copy (workspace rule 3: copy-and-adapt, not shared mutable state). `inno-cerbo` made the first recording from it (2026-10-11). Improve the original first, then re-copy; never edit one project's copy and expect the others to follow.

What to change in a project's copy, and what to leave alone:

| Leave alone | Adapt per project |
|---|---|
| `scripts/demo.py` and `requirements.txt` (the engine knows nothing about any project) | The first paragraph of this file: add the project's dev command, URL, login, and where the video must go (`docs/artifacts/YYYY-MM-DD-demo-video.mp4`) |
| The setup, key, verify, dry-run, approval and render steps | Section 2's doc list (the project's own PRD, brief, design doc names) |
| `references/shotlist.md` format and actions | The story structure in `references/shotlist.md` §1 if the partner's brief fixes a different shape or length |

**Before writing any narration on a hiring-partner project**, read `Gauntlet AI/.claude/rules/hiring-partner-framing.md` (*Demo video* section) and follow it over this skill's default story structure wherever they differ:

1. **The brief's own limit and required topics come first** (AEA: 3 to 4 minutes, "design reasoning, not a feature tour"; check the project's `docs/source/` brief).
2. **Product working first, four to five minutes in all** (*Length and pace* below). The product story is never cut for anything else. Time left after the product is fully shown goes to the hardest technical challenges and how they were solved, from the dev log and the architecture.
3. **Build `docs/delivery/YYYY-MM-DD-demo-decision-inventory.md` first** (dev logs → decision records → research → framing doc and `SUBMISSION.md`). It feeds Codex's brief in step 4a: decisions ride inside the product beats as one-clause reasons, and the technical-challenges segment draws on its technical rows.
4. **Open on layer 2 (the business value and its metric), prove layer 1 (the brief's problem), close on how the system drives the metric.**
5. Respect the project's brief-conformance rule: nothing on screen or in the narration claims what the brief does not ask for or what is stubbed. Say what is stubbed, as the brief usually requires.

The ElevenLabs key lives in the project's own `.demo/.env`; never in the workspace root `.env` (that file is for dev-tool keys and is read-only to Claude).

## 1. Setup and the ElevenLabs key

Run `demo.py setup`. It installs Python packages and Chromium, checks ffmpeg, creates `.demo/.gitignore`, and reports whether the keys are present.

The key lives in **`.demo/.env`**, which is git-ignored:
```
ELEVENLABS_API_KEY=...
ELEVENLABS_VOICE_ID=...        # optional
```
If the user put the key somewhere else in the repo, move it into `.demo/.env`, and confirm with `git check-ignore -v .demo/.env` that it is ignored. If a key file is tracked by git, stop and tell the user. A committed key should be rotated. Never print the key or paste it into chat, a commit, or the shot list.

If no voice is chosen, run `demo.py voices` and ask which voice to use. If the user wants their own voice, they can record one to three minutes of clean speech, and then you run `demo.py clone --name "<name>" --files sample.mp3`. Put the resulting id in `.demo/.env`.

## 2. Understand what to show

Read the design docs before anything else: PRD, USERS, REQUIREMENTS, KEY_METRICS, ARCHITECTURE, stories, the README, and CLAUDE.md or AGENTS.md. From them, work out:
- the problem and who has it, which becomes the intro;
- the demoable requirements or stories, and the single user workflow that connects them, which becomes the app scenes;
- the primary metric, if one exists, so you can show it on screen;
- how to run the app locally (the dev command and URL) and whether it needs a login.

If the run command or URL is unclear, ask. For a login, have the user run `demo.py login --url <login page>` and log in by hand. That saves `.demo/auth.json`.

If the user gives only a deployed URL and a PRD with no repo, that works too. Skip the evidence fields and the code checks.

## 3. Gather context

```
demo.py context --repo . --url <url> [--dev "<dev command>"] [--auth .demo/auth.json]
```
This writes two files:
- `.demo/build/site_map.json` covers each page the crawler reached: headings, links, buttons, inputs, and visible text. This is the ground truth for selectors.
- `.demo/build/context.md` holds the repo inventory: design docs, per-file UI selectors found in source (test ids, ids, placeholders, aria-labels, button text), frontend and API routes, dependency manifests, and the file tree.

The inventory is a map, not a substitute for reading. Open the actual components and handlers behind each scene you plan, so the narration describes what the code really does.

## Length and pace (Innocent, 2026-10-28)

**Length:** aim for **4:00 to 5:00** finished. **3:30 is the minimum and 5:00 the ceiling.** A partner brief with a shorter hard limit wins (AEA: 3 to 4 minutes).

How the time fills, in this order:

1. **The product story** gets all the time it needs to show the product fully: one user, one real task, end to end.
2. **If time remains** before 4:00 to 5:00, add a **technical-challenges segment** after the product: the one to three hardest problems in the build and how they were solved. Pick them from the dev log (`.claude/reference/dev-log.md`, `docs/devlog/`) and the architecture or system design (`docs/design/`, ARCHITECTURE). Rank by how hard the problem was and how clearly the fix shows engineering judgment. Each one is told as: the problem, why it was hard, what we did, and the evidence it worked.
3. **Never pad the product** to reach 4:00, and never cut the product to make room for the technical segment. Over 5:00, trim the technical segment first.

**Pace:** narration runs at **about 150 words per minute**, measured on the real voice, within **140 to 165**. Below about 120 viewers drift and above about 180 they tire. Retention is decided early, so the voice starts in the first second and the user's problem is stated within the first ten seconds. No silent title card at the open.

**Structure** (`references/shotlist.md` §1): hook → overview of how the product meets the customer need → technical architecture with its agentic design → the product story → the weak answer if the brief asks for one → technical challenges if time remains → outro. The overview and architecture scenes are fixed parts of every video (Innocent, 2026-10-28); keep them short so the product keeps its time.

**Word budget** at 150 words per minute, leaving about 20 seconds for screen holds:

| Finished length | Spoken words |
|---|---|
| 3:30 (minimum) | about 475 |
| 4:00 | about 550 |
| 4:30 | about 625 |
| 5:00 (ceiling) | about 700 |

Aim for **600 to 700 words**. The hook, overview and architecture take about 200, the product story usually 350 to 450, and the technical-challenges segment fills what is left, about 35 to 45 words per challenge.

`demo.py export` and `render` print the measured pace and warn outside the band, under 3:30, under 4:00 and over 5:00. The render summary also shows each scene's pace and flags any scene under 120 or over 185 words per minute as uneven. Fix pace with the voice settings or by changing words, never by padding.

**Voice settings.** Always set a `voice:` block in the shot list; the engine defaults (speed 1.0, stability 0.5, style 0.15) let a fast voice run away. Measure first, then tune with the controls ElevenLabs actually supports:
- `speed` (0.7 to 1.2): the Riverside voice reads at about 180 words per minute at 1.0; 0.9 brought it to 151 to 155 (HouseAccount data layer, 2026-10-29).
- `stability` 0.45: a little more natural variation than 0.5. `style` 0.2. Don't push style high; it destabilizes pace.
- The engine already sends the previous and next scene's text with each request, so intonation carries across scene joins. Keep scenes as coherent spoken units so that works.
Changing any voice setting regenerates every clip (the cache key includes the settings).

**Listening checks you can run** (do them after every voice generation; say which ones a human still has to do):
1. The render summary: total pace in band, no scene flagged uneven.
2. The gap check: `voice` warns when a fresh clip has a silence over one second inside it. That is a generation glitch, not a pause; delete that scene's entry from `.demo/build/audio_manifest.json` and re-run to regenerate only that scene.
3. Loudness per clip with `ffmpeg -af ebur128`: scenes within about 1.5 LU of each other.
4. Captions: cues in order without overlap, the last one inside the video, and the caption word count equal to the narration's.
What you can't check by tooling, and must hand to Innocent: pronunciation of names and addresses, whether emphasis lands on the right word, and whether the voice sounds natural.

Basis for the numbers (searched 2026-10-28): explainer and narration guides converge on 130 to 160 words per minute with 150 as the default, AI voiceover for short-form social video at 140 to 160, and viewer disengagement below about 120 and listening fatigue above about 180. A 2022 UCLA study found comprehension holds up even at much faster playback when visuals support the speech, so pace is about holding attention, not about comprehension. Speech in the first three seconds lifted ten-second retention by about a quarter in a 2025 Emplifi study of social video. Sources: syllaby.io voiceover pacing, CapCut explainer voiceovers, FlowShorts words-per-minute guide, ScienceDaily (UCLA, 2022), Social Media Today (Emplifi). These are guides and one study, not a controlled test of demo videos, so re-measure if retention data from our own videos says otherwise.

## 4a. Narration: Codex writes it

Codex writes the narration; you brief it and check it. Don't write the narration yourself, and don't reword Codex's text beyond the mechanical speech fixes listed below. Precedent: the first HouseAccount video (VPS `inno-houseaccount/docs/devlog/2026-10-23-narration-story-rewrite-codex-01a16821.md`).

**The voice it must have.** Product-focused and story-driven, told by the engineer to an interviewer; the full spoken-delivery rules are in `references/shotlist.md` §2 and go into the brief:
- Follow **one user through one real task**, in the order they'd do it. Open on their moment ("Imagine you're a field rep with two hours in Ramsey…"), not on the product or the stack.
- Each product beat says what the user does, what they see, and why it matters to them. A decision appears as a one-clause reason ("so the rep never knocks on a door we can't explain"), not as architecture.
- No stack names, model names, acronyms or internal IDs (D-12, R-4, CON-3) in the product story. Plain words, about a sixth- to eighth-grade reading level, adult tone, connected sentences.
- The technical-challenges segment, if there is one, stays in plain words too. Name a technology only when the fix depends on it.
- First person throughout, as the engineer ("I built…", "I chose…"). Confident and specific, never salesy. Vary sentence length; never repeat "the assistant finds / explains" or "they ask".

**Steps:**

1. **Write the story outline** at `.demo/build/story-outline.md`: the user and their moment; the overview facts (the customer need and the parts of the build that serve it, from the data model or PRD); the architecture facts (components and where a model decides, from the system design and decision log, with source paths); the scenes in workflow order, each with what is on screen, its requirement, its evidence files and its decision-inventory rows; the primary metric; the ranked technical-challenge candidates with source paths; the brief's limit and the word budget from *Length and pace*. Use the scene ids you will use in the shot list.
2. **Write the brief** at `.demo/build/codex-narration-brief.md`. It contains: who the viewer is (a hiring partner deciding in a few minutes whether the builder can ship); the voice rules above; the outline (paste it in); the word budget (product story first, the technical segment only for the remaining words); the speech rules from `references/shotlist.md` §2 (numbers spelled out, no symbols or markdown in spoken text); the claim rule (state only what the outline's evidence and inventory rows support; stubbed or proposed things are said as such); and the output contract below.
3. **Output contract** Codex must meet: write `docs/delivery/YYYY-MM-DD-demo-narration.md` with a short header (word count, estimated length at 150 words per minute, reading grade if it can measure one), then the spoken text between `<!-- NARRATION START -->` and `<!-- NARRATION END -->`. Before each paragraph, put `<!-- scene: <scene id> -->` using the outline's ids, so you can split it across scenes without rewording. Shot notes, if any, go outside the markers.
4. **Run Codex** from the repo root on **Sol**, the newest Sol the CLI lists (`gpt-6.1-sol` as of 2026-10-28; Sol is also the Codex default on the Mac and the VPS), with high reasoning. Not Astra (Innocent, 2026-10-28). If the CLI rejects the Sol id, `brew upgrade codex` (Mac) or update the VPS CLI, then pick the newest `*-sol` in `~/.codex/models_cache.json`. Feed the brief on stdin:
   ```bash
   codex exec --skip-git-repo-check -C "$PWD" -m gpt-6.1-sol --sandbox workspace-write -c model_reasoning_effort=high - < .demo/build/codex-narration-brief.md
   ```
   Run it in the background and wait for it to finish. On the VPS, a non-interactive shell may not have `codex` on `PATH`; run it through `bash -lc` or use its full path. If Codex is unavailable (not installed, not signed in, allowance used up), stop and tell Innocent. Don't write the narration yourself instead.
5. **Check it, don't rewrite it.** Count the words between the markers and confirm they are inside the budget. Confirm that every scene id in the outline has a block, that every claim traces to an evidence file or inventory row, and that the product story has no jargon. If a check fails, send Codex numbered notes in a new `codex exec` run that points at the file, at most two rounds, then show Innocent what is still off. You may make mechanical speech fixes yourself (spelling out a number, expanding a symbol); list each one you made.
6. **Copy each scene's block verbatim** into that scene's `narration:` in the shot list (step 4). If a scene needs different words to fit the picture, change the picture or ask Codex. Don't edit the words. A small builder that splits the narration file by `<!-- scene: id -->` into a shot-list template keeps this mechanical (HouseAccount data layer: `.demo/build_shotlist.py`).
7. **Revisions.** When Innocent asks for a change, save the current file as `.demo/build/<model>-vN-narration.md`, append a numbered "Revision request" section to the brief that names what to keep word for word, what to add and the new word budget, and run Codex again. Then diff the new version against the saved one and show Innocent only the scenes that changed. If he asks who wrote it, the answer is Codex; you wrote the brief and the cards.

## 4. Write `.demo/shotlist.yaml`

Read `references/shotlist.md` first. It has the story structure, the text-to-speech narration rules, the file format, every action, selector guidance, and timing advice. Then write the file.

Each scene's `narration:` is Codex's block for that scene id, copied verbatim (step 4a). Give every app scene an `evidence:` list of one to three repo files that implement it. This is how the user, and you, check that the video doesn't overclaim.

## 5. Verify claims against the code

Before running anything, reread each scene and confirm three things:
- the feature works the way the narration says, and the `evidence` files exist and implement it;
- numbers in the narration match what the UI will show;
- technical claims are backed by the docs, the manifests, or code you've read.

Fix anything that doesn't hold up. Cutting a claim beats an inaccurate video.

## 6. Dry-run until every action works

Run `demo.py check`, with `--headed` if you need to watch. On failure, it writes `.demo/build/failures.json`, which records each failed action, the error, and `page_at_failure` (the elements actually on the page at that moment). Use that to fix the scene:
- **Wrong selector:** pick one that exists in `page_at_failure` or in the source.
- **Element not there yet:** add a `wait_for` before it.
- **Wrong page:** fix the earlier `goto` or the scene's `before`.

Repeat until `check` passes. If the same scene still fails after about four attempts, show the user the error and ask. Something may be broken in the app itself, which is worth telling them.

## 7. Approval gate

Run `demo.py export`, then show the user a table:

| # | scene | requirement | evidence | est. time |
|---|---|---|---|---|

Add the estimated total, the word count against the budget, and whether a technical-challenges segment is included. Point them to `.demo/build/script.md` and Codex's `docs/delivery/YYYY-MM-DD-demo-narration.md` to read the full narration. **Stop here and wait** for approval or edits. Apply their edits verbatim to the narration, keeping the rules in `references/shotlist.md` (for example, spelled-out numbers). If they ask for a different story rather than word edits, send it back to Codex with their notes.

## 8. Render

```
demo.py render --subs
```
This voices each scene (cached by text, so re-renders after small edits cost little), records the browser timed to the audio, and writes `.demo/<project>_demo.mp4` and `.srt`. Watch the output for two things:
- **`actions ran Xs past the narration`** means part of a scene will be silent. Lengthen the narration, trim waits, or move navigation into `before`, then re-render.
- **The pace line:** the measured words per minute must sit between 140 and 165. Adjust the voice `speed` (0.95 to 1.05) first.
- **A total over 5:00:** trim the technical segment first, then the product narration, and re-render.
- **A total under 4:00:** if the product is fully shown, ask Codex for the technical-challenges segment (step 4a) and re-render. Under 3:30 is never delivered.

If the user would rather speak the narration themselves, they record one file per scene as `recordings/<scene id>.wav`. Then run `demo.py render --own-audio recordings --subs`.

## 9. Review the cut

Run `demo.py frames` and look at every image in `.demo/build/frames/`. You get one frame from the middle of each scene and one from its end. For each scene, check:
- the screen shows what the narration says at that point;
- there are no error pages, stuck spinners, empty states, cookie banners, or dev overlays such as the Next.js error toast or the React Query devtools;
- the PRD badge and captions don't cover the important UI;
- the cards are readable.

Fix the problems you find, re-render, and look again. Only changed scenes regenerate audio.

## 10. Deliver

Give the user:
- the video path;
- its duration and the measured pace in words per minute;
- a one-line summary per scene;
- anything you cut or couldn't show, and why.

Mention that `.demo/shotlist.yaml` is worth committing, so the video can be regenerated after the app changes.

## A product with no screens: replay a real agent run (added 2026-10-28, HouseAccount data layer)

An MCP server, an API or a pipeline has no UI to record. Don't fake a chat. Show a **real recorded agent run**:
1. Take the run records the project already has (an eval run's per-question tool calls and answers), or record a fresh run of a real assistant connected to the server.
2. Generate a local replay page from them: one section per question with the question, the tool calls as chips, a pass/weak badge and the answer rendered from Markdown. Give each section an id (`#q1`, `#q1-answer`) so scenes can scroll and highlight, and mark redactions or other evidence with their own class so the technical segment can point at them.
3. Label it on screen and in the narration as a recording of that run (run id, model, date). Serve it with `python3 -m http.server` as the shot list's `dev:` command.
4. Diagram cards (overview, architecture) are hand-made `html_file` cards at the video viewport; screenshot each at that size and check nothing overflows.

Never show a run whose answers have personal-data hits; check the run's PII count first.

## Two sessions, overlays and caption band (added 2026-10-22, Riverside)

A demo that crosses roles (a family app and a staff console) uses `pages:` and a per-scene `page:`; only the session on camera is screencast, and the cut between them is a normal scene boundary. Editorial captions that belong to the video, not the app (a proposed metric, an evidence line), use the `overlay` action. When the app's primary controls sit at the bottom of the screen, set `caption_band` so burned-in captions sit in a strip below the app. Details and syntax: `references/shotlist.md` §3–4.

## Troubleshooting

| symptom | fix |
|---|---|
| `could not load any page` | The app isn't running. Pass `--dev`, or ask the user how to start it. |
| A login page appears in the recording | Use `demo.py login`, then set `auth: {storage_state: .demo/auth.json}`. |
| ElevenLabs 401 | Wrong key in `.demo/.env`. |
| ElevenLabs 404 | Wrong voice id. Run `demo.py voices`. |
| Voice sounds flat or rushed | Raise `style` to 0.3, or set `speed: 0.95` in `voice:`. |
| `codex exec` hangs with no output | It is waiting on stdin. Feed the brief with `- < brief.md` as in step 4a, or append `</dev/null` when passing the prompt as an argument. |
| Text is soft in the video | Use a 1280×720 `viewport`. Larger UI text survives encoding better. |
| ffmpeg `subtitles` filter error | Drop `--subs`. The `.srt` is still written next to the video. |
| A highlight pushes the app's header off screen (chat thread scrolls inside a fixed card) | Set `page_scroll: minimal` in the shot list (added 2026-10-22, AEA). |
| Mid-scene frames show the top of the page instead of the scrolled-to section (a long page that scrolls as a whole, such as a run replay) | Remove `page_scroll: minimal`; it snaps the page back to the top. Always check the mid frames of scroll scenes (HouseAccount data layer, 2026-10-28). |
