# Project Checklist — inno-tariff-slm (Tariff Specialist SLM)

Sequence: `zero-to-hero` v2.0.0 (`Nortorious-Technologies/.claude/skills/zero-to-hero/`).
Artifact paths: that skill's `ARTIFACT-MAP.md` (§ numbers below match).

| Field | Value |
|---|---|
| Project | inno-tariff-slm: a fine-tuned 1B–4B tariff-classification specialist inside an AI trade-compliance analyst |
| Kind | Gauntlet weekly (Week 7, Train Your Own SLM) |
| Mode | light (four-day weekly build) |
| Started | 2026-10-30 |
| Deadline / internal cutoff | Early: Thu 2026-10-29 midnight (passed at scaffold time) · Final: Sun 2026-11-01 noon / Sat 2026-10-31 evening |
| Layout substitutions | PRD and planning docs live in `Gauntlet AI/docs/planning/tariff-*.md`, and the vision page in `Gauntlet AI/docs/research/tariff-compliance-vision.html`, at Innocent's instruction (2026-10-30). Repo `docs/` holds data reality, evals and code docs. |
| Context system | [ICM progress checklist](.claude/state/icm-progress.md) — tracks `.claude/` maturity; its rows are not copied here |

**How to use.** Tick an item when its artifact exists at the mapped path. A gate line is passed
only with evidence, and a ★ gate only with `Innocent ✓ YYYY-MM-DD`. Up to the fork, the first
unticked gate is where the project is. After it there is one current gate per marked track (headings
ending **— UX track**, **— Joint track** and **— System track**). §7 readiness is **per ticket**, not
"both tracks closed": run `python3 scripts/ticket_readiness.py check <ticket.json> --root <repo>` from the
`zero-to-hero` skill before a ticket starts; it names each missing condition.
A stage skipped goes under *Skips* with its reason.

**Ownership after the fork (two sessions):** the UX session ticks the UX-track rows; the System session
ticks the §5–§6 rows. The contract files in `docs/contracts/` (`INTERFACE.md`, `interface.openapi.yaml`,
`CHANGES.md`) are **jointly owned**: the UX side owns the needs, the System side owns the support, both
review every card, and Innocent decides product behaviour. Either session ticks a Joint-track row once both
reviews are recorded. An agreed card changes only through the change procedure (`CHG-N`).

---

## 0 · Scaffold  (§0)
- [x] `PROJECT-CHECKLIST.md` (this file) filled in
- [x] `CLAUDE.md` entry point (+ `AGENTS.md` if Codex works here)
- [x] Principles pack, both halves: `Gauntlet AI/principles/` → `docs/principles/` (incl. `system-design.md`), and rules → `.claude/rules/` with a provenance line each: general (incl. `system-design-conversation`, `system-design-questioning`, `problem-framing`, `business-metrics`) · Gauntlet policy · hiring partner · legacy (OpenEMR only)
- [x] Context system bootstrapped by **invoking** `icm-project` (Phases 1 and 3; version recorded in `icm-progress.md`): `CLAUDE.md` from its entry template, `.claude/README.md` router, `rules/context-maintenance.md`, dev-log home, `.claude/state/icm-progress.md`; `CLAUDE.md` and the router both link the ICM checklist
- [x] Remote and host set per policy: GitLab `origin` `innocentnortey/inno-tariff-slm` (created by Innocent, private, SSH verified 2026-10-30; nothing pushed). No host needed yet.
- [x] `SUBMISSION.md` opened (Gauntlet)
- **Gate:** ☑ pack present, checklist filled, `icm-progress.md` exists and is linked from `CLAUDE.md`, `check_context.py` reports no FAIL (2026-10-30; remote pending)

## 1 · Frame  (§1)
- [ ] Sources converted and ranked in `docs/source/`
- [ ] Brief audit: traps, real problem, real guideline — `docs/analysis/…-brief-audit.md`
- [ ] Problem behind the brief: why-chain, assumptions marked, each metric's hop chain to money, north star named (GP-120 – GP-130)
- [ ] Metrics chosen: health vs value groups, leading + lagging pair per branch, decision line / denominator / baseline / aspiration / hard gate per metric (GP-131 – GP-144)
- [ ] Two-layer success framing + metrics tree
- [ ] PRD draft — `docs/prd/<project>-prd.md`
- [ ] Stage 1 **visual** review page — `docs/artifacts/YYYY-MM-DD-<project>-prd.html`, built after the Markdown (problem, journey, metrics chain, scope and cuts, evidence limits, approval request); `check_review_page.py` passes; inspected at laptop and phone width; linked from `.claude/README.md`
- **Gate:** ☐ audit + framing signed off — Innocent ✓ ____

## 2 · Data reality ★  (§2)
- [ ] Samples in `docs/data/samples/` (full 20–50 · light ~10)
- [ ] Selection matrix: every source, every type, the strange ones — `docs/data/README.md`
- [ ] Worked pairs `WP-1…` in `docs/data/worked-pairs.md` (full 5–10 · light 3), each marked easy/hard and sure/uncertain
- [ ] Synthetic stand-ins labelled with their assumption
- [ ] Stage 2 **visual** review page — `docs/artifacts/YYYY-MM-DD-data-reality.html` (coverage matrix + side-by-side worked pairs), built after both Markdown files; check passes; inspected at both widths; linked from `.claude/README.md`
- **Gate:** ☐ every core workflow has pairs; every uncertain pair checked — Innocent ✓ ____

## 3 · Hard problems ★  (§3)
- [ ] Register `docs/design/hard-problems.md`: HP-1 orchestration + one card per hard problem + *Handled by default* list
- [ ] Every `hard` worked pair maps to a card
- [ ] Each card: evidence pairs, why hard, options with diagrams, recommendation, principles, success measure
- [ ] `docs/principles/system-design.md` questions walked; open ones are cards or interview options
- [ ] Stage 3 **visual** review page — `docs/artifacts/…-hard-problems.html` (HP cards with option diagrams, recommendation, consequences), built after the register; check passes; inspected at both widths; linked from `.claude/README.md`
- **Gate:** ☐ Innocent has worked through the page — Innocent ✓ ____

## 4 · Interview ★  (§4)
- [ ] `prd-interview` run *after* §3, fed the register (page choices recorded, not re-asked)
- [ ] Every HP choice in the decision record
- **Gate:** ☐ PRD approved — Innocent ✓ ____

## 4b · UX-1 (fork)  (§4b) — starts once the PRD is approved; Claude closes the gate (no sign-off)
*Via the `ux-pipeline` (UX-1); projects outside it use `ARTIFACT-MAP.md` §4b's list.*
- [ ] User stories `US-1…` (`docs/ux/01-planning/USER_STORIES.md`): As a <who> I need <what> so that <why>; each links its PRD requirement, WP-N and screen; every core flow covered
- [ ] Flows (`USER_FLOWS.md`) with each step's **states, permissions and recovery paths**, and a draft `CON-N` on every data step; sitemap (`SITEMAP.md`); `trace_check --upto FLOW` passes
- [ ] Unresolved behaviour questions listed where they can be seen (`UXP-N`), each routed to the UX-3a card it affects
- [ ] UX-1 review page built (journeys, flows, sitemap as diagrams + the CON list + the open UXP list); `check_review_page.py` passes; path given to Innocent
- **Gate:** ☐ UX-1 checks pass — Claude ✓ ____ (no sign-off: Innocent, 2026-10-20; he reads the page when he chooses, and anything he raises reopens UX-1)

> **▶ FORK — open a second session for the System track now (§5 spikes → §6 design).**
> Launch it on the same machine or VPS as this project's working copy, on the same model as this session
> (`~/.claude/rules/match-model-on-vps.md`). It reads first: the PRD, `docs/ux/01-planning/USER_STORIES.md`,
> the flows with their states and draft CONs in `USER_FLOWS.md`, the open `UXP-N` list,
> `docs/design/hard-problems.md`, `docs/data/worked-pairs.md`. Its first gate is §5's.
> The Joint track (UX-3a) starts now too. This session continues with UX-2.

## UX-2 · Visual direction ★  (§4b) — UX track
- [ ] Feel brief `docs/ux/02-concepts/FEEL_BRIEF.md` (feel, interaction shape, analogous products; style searches never use the industry name)
- [ ] Reference research with live-captured images and a reference → product mapping table
- [ ] A look sheet for each of **4 directions** that differ at a glance (credited references, light + dark swatches with computed contrast, 3–4 static mockups on real flow copy) — `docs/artifacts/YYYY-MM-DD-<direction>-look-sheet.html`
- [ ] Representative screens in the picked direction (lightweight linked screens only if they help the choice; never a full application)
- **Gate:** ☐ direction picked: ____ (his words) — Innocent ✓ ____

## UX-3a · Shared contracts ★  (§4b) — Joint track
- [ ] `docs/contracts/INTERFACE.md`: one `CON-N` card per data step, each with operations, fields, states, permissions, named errors, recovery, guarantees, timing, the screens and stories that need it, the backend owner, and a status (`draft` → `proposed` → `agreed`, or `changing`)
- [ ] `docs/contracts/interface.openapi.yaml`: the same promises in machine form; each operation names its `CON-N`; lints; the Prism mock starts from it; types are generated from it
- [ ] `docs/contracts/CHANGES.md` opened; every change to an agreed card is a `CHG-N` with its aspect and presentation-only/behavioural, even when the OpenAPI file is unchanged
- [ ] Each card reviewed by both sides (UX needs, System support), each review named and dated; every `UXP-N` and product-behaviour question in it decided by Innocent
- [ ] Older layout only: `docs/ux/03-structure/UI_CONTRACTS.md` is a pointer to `docs/contracts/` (or migrated)
- [ ] `trace_check --upto CON` passes for the agreed cards
- **Gate:** ☐ every card that something relies on is `agreed` (both reviews recorded; product behaviour decided) — Innocent ✓ ____ (repeat per card set; cards still `draft` or `proposed` listed: ____)

## UX-3b · Screens and tokens ★  (§4b) — UX track
- [ ] IA `docs/ux/03-structure/IA.md`
- [ ] Screen specs `SCR-N` with every state (`docs/ux/03-structure/SCREEN_SPECS.md`); each names the `CON-N` it uses
- [ ] `docs/design/design.md` (UI-2 template) in the chosen direction, with the design tokens
- **Gate:** ☐ screen specs signed for wave ____ (per wave is allowed; list the `SCR-N`) — Innocent ✓ ____

## FW · Early frontend foundation wave  (§4b) — UX track
- [ ] Preconditions: UX-2 direction picked and `design.md` tokens written (the §6 gate is **not** needed: presentation only)
- [ ] Readiness record `docs/plans/foundation-wave.md`: stack and the decision it comes from, owned files, bounded scope, dependencies, one ticket spec per ticket, review requirements (code review, accessibility, visual check against the look sheet and `design.md`, and the shell and layout primitives passing `look_compare.mjs --gate`)
- [ ] Scope only from the eligible list (tokens, typography, basic accessible components, layout primitives); nothing behaviour-dependent (permissions, autosave, resumability, booking or job state, data fetching, backend error recovery, real-time collaboration)
- [ ] Each FW ticket's acceptance examples are presentation examples (`PE-N`), not invented backend pairs
- [ ] Each FW ticket passes `ticket_readiness.py` before it starts; built and reviewed like any §8 ticket (lane, plan → implement → test → review, affected tests)
- **Gate:** ☐ FW tickets merged with their review evidence, including `look_compare.mjs --gate` PASS for the app shell (nav form and width, top bar, column widths) — Claude ✓ ____

## 5 · Spikes  (§5) — System track
- [ ] `SP-N` record for every card not yet `chosen`: brief + pass line first, frozen scoring harness, options built **in parallel by fan-out agents**, harness re-run by the orchestrator on each branch (`references/spikes.md`)
- [ ] Innocent has read each SP result
- [ ] Any spike result that changes what a screen needs or what the backend can promise logged as a `CHG-N` and run through the change procedure
- **Gate:** ☐ no HP card is `open`

## 6 · Design  (§6) — System track
- [ ] **Foundation questions answered by Innocent before DO-1** (`.claude/rules/system-design-questioning.md`): SD-3.1 load target + scale path, SD-3.4 peak/concurrency, SD-7.2 failure to survive, SD-1.6 spend ceiling, SD-1.9 hardest uncertainty. Each recorded with date and his words in the readiness report and the PRD decision table; none filled by a test load, default or public count
- [ ] `system-design-readiness` READY
- [ ] DO-1…DO-7 written at their mapped locations; DO-4 links every internal contract to the `CON-N` it serves in `docs/contracts/INTERFACE.md`, adds internal signatures only, and never repeats or contradicts a card's promise
- [ ] Code design recorded: `.claude/reference/area-map.md` with planned paths labelled planned; router rows added; ICM "code design" row updated with evidence
- [ ] Entry rebuilt: `icm-project` Phase 3 re-run so `CLAUDE.md` and the router follow the entry template against the area map; fresh-context walkthrough done and its ICM row verified; `check_context.py` reports no FAIL
- [ ] DO-3 code design to `code-design-solid-modularity`: each module's one-sentence job, interface and dependency direction; each seam cut or deferred with why
- [ ] `metz-code-design-agent` review `docs/design/reviews/YYYY-MM-DD-code-design-review.md` — verdict PASS (Blocking findings fixed or put to Innocent)
- [ ] DO-5 eval plan: worked pairs as the first dev set, HP success measures as criteria, error-analysis-first rule
- [ ] Stage 6 visual review page `docs/artifacts/YYYY-MM-DD-system-design.html`: a story-first study guide with every DO-1/DO-2 finding (`check_review_page.py` passes; inspected at laptop and phone width)
- [ ] Questions raised while designing: each new choice is an `SDQ-N` (asked, or drawn as a labelled proposal with a `data-ask` card); any answer the numbers undercut was put back to Innocent, not changed silently; pre-gate sweep leaves no foundation item proposed or defaulted
- [ ] Signature completeness: every cross-area call in DO-3's build-areas table has a DO-4 signature with field-level result types; every service and adapter has its constructor; every OpenAPI error code maps to a DO-4 error type; every DO-6 record has a storage location; every typed settings field consumers need is named
- [ ] Signature check run: `signature_check.py --code-design … --contracts … --observability … --openapi docs/contracts/interface.openapi.yaml` exits 0 (command in `ARTIFACT-MAP.md` §6) — evidence: result line ____ , date ____
- [ ] Spec dry run: one agent wrote testable acceptance criteria for three representative tickets (a service, a route, a graph node); every gap it hit closed in DO-3/DO-4
- [ ] Spec dry run filed: `docs/design/spec-dry-run.md` (from `templates/SPEC-DRY-RUN.md`) holds the three sample specs and each could-not-write item with its missing fact, every one marked closed
- [ ] Coverage requirements sweep (`to-tickets` mandatory-requirements table against DO-6's workflow registry): every entry point has a `WF-n`, every DO-7 metric is inherited by a workflow
- **Gate:** ☐ `design_outputs.py check … --gate tickets` passes; `signature_check.py` exits 0 (result line + date recorded); `docs/design/spec-dry-run.md` filed with no open gap; signature check, spec dry run and coverage sweep clean; DO-4 links and agrees with the agreed `CON-N` cards; code-design review PASS; Innocent reviewed DO-1/DO-2 and the current Stage 6 page ✓ ____ (the gate every backend, frontend and integration feature ticket needs)

## 7 · Tickets — four passes ★  (§7)
- [ ] Readiness per ticket (`ARTIFACT-MAP.md` §7): backend = §6 + its CONs agreed; frontend = §6 + its `SCR-N` signed + its CONs agreed; integration = planned any time, executed once its FE and BE tickets are merged against the same agreed CON; foundation = UX-2 pick + tokens + readiness record
- [ ] 7a–7c run on Opus with `to-tickets` invoked explicitly; Haiku only for fast evidence sweeps; Sonnet only from §8
- [ ] 7a **Product-wide** slice plan `docs/plans/slice-plan.md`, cut along DO-3's module boundaries; every ticket has a kind (backend / frontend / integration / foundation) and its `CON-N` and `SCR-N` links; every integration ticket names the tickets it joins — Innocent ✓ ____
- [ ] 7a parallelism audit in the slice plan (`to-tickets` §2a): edges removed and why, human gates in wave 0, critical-path length, widest wave, collision map per wave; re-run after 7c repairs
- [ ] Every ticket has exactly one lane (`ticket-lanes`: build-loop / direct / human / spike); lane split stated in the slice plan; `risk::security` on every security ticket (count stated)
- [ ] 7b Spec one wave at a time; each issue opens with its user story (US-N), has an example pair (WP-N, or PE-N for presentation work), cites its `CON-N` and (UI work) its signed `SCR-N`, and links its HP card
- [ ] Each ticket passes `ticket_readiness.py check <ticket.json> --root <repo>` before it is marked ready
- [ ] 7c Coverage audit clean (product-wide: every story, screen and agreed CON covered)
- [ ] 7d Published to GitLab, waves, kinds and lanes labelled
- **Gate:** ☐ all four passes done for the waves cut so far — Innocent ✓ ____ (slice plan)

## 8 · Build  (§8)
- [ ] Frontend tickets built from signed `SCR-N` and `design.md` tokens, on Prism mocks generated from `docs/contracts/interface.openapi.yaml`, while the backend is built alongside
- [ ] Backend contract tests run against the same `interface.openapi.yaml`
- [ ] Integration tickets point the frontend at the real backend once both sides are merged against the same agreed `CON-N`
- [ ] UX-5a per frontend slice: `docs/ux/05-verify/TRACEABILITY.md` updated, axe at 1280/390 light and dark, visual check with `look_compare.mjs` (each screen beside its look-sheet mockup, structural checks answered pass/fail, default theme as `design.md` names it), behavioural checks against the CON cards (rerun against the real backend after integration)
- [ ] Each wave's ready build-loop tickets built at the same time (one planner → implementer pair each), inside the collision map; its direct tickets done by one general agent each alongside, no build-loop gates
- [ ] Each ticket's WP-N (or PE-N) is one of its tests, written with the code (plan → implement → test → review); frozen first by `test-writer-agent` only for `risk::security` tickets
- [ ] Only affected tests per role and per merge; full suite only when a change reaches everything and before each deploy
- [ ] Each slice reconciles `.claude/` in the same change: area map (each row's status replaced in place, planned → built, one clause per ticket; never both sides of a merge conflict), area routes if used (durable facts later tickets need), router rows, rule `paths:`, and ICM rows (scaffold, routes verified) with dated evidence
- [ ] `code-review-agent` per ticket; seam audit per wave; `security-privacy-agent` at a wave merge only when the wave has a `risk::security` ticket
- [ ] No merged work left marked `reconcile: CHG-N`
- **Gate:** ☐ waves merged, seam audits clean, UX-5a evidence for every frontend slice, `look_compare.mjs --gate` PASS for every screen with a mockup (no visual row `NOT_RUN` or `NEEDS_HUMAN_REVIEW`), area map matches the checkout — Claude ✓ ____

## UX-4 · Focused interaction prototype (optional)  (§4b)
*Only for a named interaction uncertainty; never a prerequisite for tickets. Otherwise record `n/a` with the reason.*
- [ ] Named question: ____ — or `n/a — <reason>`
- [ ] If run: `docs/ux/04-prototype/PROTOTYPE_PLAN.md` (question, what is built to answer it, how it is judged) and the focused prototype in `docs/ux/04-prototype/`
- **Gate:** ☐ Innocent judged the named question — Innocent ✓ ____ — or `n/a — ____` recorded

## UX-5b · Final acceptance ★  (§4b)
- [ ] Walkthrough of the connected application (real backend, not mocks); Lighthouse; `docs/ux/05-verify/QA_REPORT.md`
- [ ] Every UX-5a slice's evidence linked from `TRACEABILITY.md`
- **Gate:** ☐ final acceptance signed (before §9 and §10) — Innocent ✓ ____

## 9 · Experiment ★  (§9)
- [ ] Kickoff page generated from code (flow, prompts with versions, approach, failure types)
- [ ] Error-analysis round: ~20 traces, first failure each, `FT-N` taxonomy, models × failures table — Innocent ✓ ____
- [ ] Every `XP-N` targets one `FT-N`, one change, scored on the frozen set
- **Gate:** ☐ no tuning change without a named failure type

## 10 · Ship & defend  (§10)
- [ ] `SUBMISSION.md` walked; every row's evidence at the expected path
- [ ] Demo script (two-layer order) and interview prep
- [ ] Hiring-partner demo: decision inventory from dev logs + decision records + research (`docs/delivery/…-demo-decision-inventory.md`); video = product under 5 min, then decisions (`hiring-partner-framing` → *Demo video*)
- [ ] ICM progress checklist reconciled: no row left provisional without a named reason
- [ ] Area map and any area routes current: one status account per row, no path labelled planned that exists, route facts re-checked or marked stale; `check_context.py` no FAIL (shape and pointers only; behaviour evidence is the test runs already linked)
- [ ] Retro written; lessons fed back to `Gauntlet AI/principles/` and `zero-to-hero`
- **Gate:** ☐ shipped — Innocent ✓ ____

---

## Skips

| Stage | Reason | Decided by | Date |
|---|---|---|---|
| (pause) Stages 1–8 implementation | Concept-stage video first; implementation paused, existing results preserved. Planning docs in `Gauntlet AI/docs/planning/tariff-*.md` are drafts, not signed gates. | Innocent ("Stop implementation work") | 2026-10-30 |

## ID registers (quick index)

| Prefix | Where | Count |
|---|---|---|
| WP | `docs/data/worked-pairs.md` | |
| HP | `docs/design/hard-problems.md` | |
| US | `docs/ux/01-planning/USER_STORIES.md` (or `docs/prd/user-stories.md`) | |
| UXP | the open `UXP-N` list in `docs/ux/01-planning/` | |
| SCR | `docs/ux/03-structure/SCREEN_SPECS.md` | |
| CON | `docs/contracts/INTERFACE.md` (older projects: `docs/ux/03-structure/UI_CONTRACTS.md` as a pointer) | |
| CHG | `docs/contracts/CHANGES.md` | |
| FW | `docs/plans/foundation-wave.md` | |
| PE | the FW and presentation ticket specs | |
| SP | `docs/analysis/spikes/` | |
| FT | `docs/testing/error-analysis/` | |
| XP | `docs/testing/experiments/` | |
