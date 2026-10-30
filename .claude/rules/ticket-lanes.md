<!-- Provenance: copied from Nortorious-Technologies/.claude/rules/ticket-lanes.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
# Ticket Lanes → Only Tickets That Change Running Code Go Through the Build Loop

Recorded 2026-10-20 at Innocent's instruction: "each ticket needs to be labeled as to whether or not
it's actually something that needs to go through our build loop (or if it's just something that a
general agent can handle). Some of these tickets aren't real tickets, and they shouldn't be adding
bloat by having to go through our build loop." Applies to every project under Nortorious-Technologies
whenever work is cut into tickets (`to-tickets`, zero-to-hero §7, `tdd-swarm`, a project's
`plan-batch`) and whenever an orchestrator runs them.

## What it looks like in practice

A wave has four tickets:

| Ticket | What it changes | Lane | What runs |
|---|---|---|---|
| `[YAI-12] vault: encrypt session keys` | `src/vault/`, its tests | `lane::build-loop` + `risk::security` | plan → frozen failing tests → implement → code review → affected tests at merge → security review at the wave merge |
| `[YAI-16] report: redaction-count column` | `src/report/`, its tests | `lane::build-loop` | plan → implement (code + tests) → affected tests → code review → merge |
| `[YAI-13] docs: architecture section for the vault` | `docs/ARCHITECTURE.md` | `lane::direct` | one general agent writes it, checks it, commits it; no tests, no reviewers, no merge gate |
| `[YAI-14] ops: create the Railway project` | nothing in the repo | `lane::human` | Innocent does it from Claude's exact steps; Claude records the result |
| `[YAI-15] detector: Presidio vs regex recall` | throwaway branches + a decision record | `lane::spike` | `zero-to-hero` `references/spikes.md`: fan-out, light testing, nothing merged but the record |

Before this rule, YAI-13 would have got a worktree, a test-writer with nothing to test, two reviewers
and a 3–7 minute full-suite merge gate, all to land one Markdown section.

## The test that decides the lane

Ask: **does this ticket change anything that code or tests read?** That means source, tests,
schemas and migrations, prompts and templates the app loads, contracts (OpenAPI, CON cards that
generate code or mocks), settings and environment config, dependency and lock files, CI, and fixture,
seed or knowledge-base files the app or tests load, **whatever their file type**. A Markdown knowledge
base the RAG pipeline ingests is code-read; a Markdown design doc is not.

| Answer | Lane |
|---|---|
| Yes | `lane::build-loop` |
| No, and an agent can do it (docs, README, devlog, `SUBMISSION.md`, design and decision docs, diagrams, review pages, demo script, research notes, issue and label housekeeping, `.claude/` context files) | `lane::direct` |
| No, and only Innocent can do it (accounts, credentials, hosting projects, payments, recording, a sign-off) | `lane::human` |
| It decides between approaches; the output is a decision, not merged code | `lane::spike` |

**When unsure, it is `lane::build-loop`.** A ticket that mixes the two (a doc *and* the code it
describes) is split, or goes in the build loop whole.

## What each lane runs

- **`lane::build-loop`**: plan → implement → test → review per `build-loop-test-scope.md` (test-first and the
  wave-merge security review only for `risk::security` tickets),
  planner → implementer per `fanout-plan-then-implement.md` (or the project's own pair).
- **`lane::direct`**: **one** agent (`general-purpose`, or the orchestrating session itself), no
  worktree, no test-writer, no planner/implementer pair, no code or security review, no merge-gate
  suite. It still:
  - meets the ticket's acceptance criteria and posts the evidence on the issue (the page check passes,
    links resolve, the section exists);
  - stays inside the collision map's file ownership, so it never collides with a build ticket;
  - checks before committing that `git diff --name-only` touches nothing code or tests read; if it
    does, it stops, relabels the ticket `lane::build-loop` and reports;
  - commits with a clear message straight to the working branch (in `tdd-swarm`, the integration
    branch, between merges), or opens one small MR where the repo requires it (Werewood's `main` is
    PR-only; the project's rule wins).
- **`lane::human`**: Claude writes the exact steps on the issue (URL, account, click path), Innocent
  does them, Claude records the outcome. Blocks nothing it does not truly feed (`to-tickets` §2a puts
  these in wave 0). A *build* ticket that only waits on a human step keeps `lane::build-loop` and adds
  `gate::human`.
- **`lane::spike`**: `zero-to-hero` `references/spikes.md`. Light testing against the frozen scoring
  harness; branches are evidence, not merges; the deliverable is the `SP-N` decision record.

## How to apply

- **Whoever cuts tickets** gives every ticket exactly one lane label, shows the lane in the slice plan
  next to the wave, and states the lane split (e.g. "31 build-loop, 6 direct, 3 human, 1 spike") when
  asking for approval. In a `TICKETS.md` board the field is `Lane:`.
- **Orchestrators** route by the label: only `lane::build-loop` tickets enter the loop. Direct tickets
  in a ready wave are dispatched in the same message as that wave's build agents, so they finish in
  parallel and never take a build slot.
- **Projects** get a copy at zero-to-hero Stage 0 (`ARTIFACT-MAP.md` §0, *Build loop* set). Change this
  original first, then re-copy.

## What this rule does not change

Nothing merges on red affected tests and nothing deploys on a red full suite; the pre-deploy full suite
covers whatever direct tickets landed before it. Lanes change who does a ticket and which
gates it passes, never its acceptance criteria.
