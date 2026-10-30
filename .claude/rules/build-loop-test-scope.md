<!-- Provenance: copied from Nortorious-Technologies/.claude/rules/build-loop-test-scope.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
# Build Loop → Plan, Implement, Test, Review; Test-First and Security Review Only for Security Work; Only Affected Tests

Recorded 2026-10-19 at Innocent's instruction, after the YourAI factory build ("is it necessary to
run test that arent actually relevant to the changes"). Revised 2026-10-20 at his instruction: "we
should only be using tdd when its for something intensley security related, most of our build loop
should be our typical plan implement test review ... we should only be running test on test that
would have been affected and we should also only run the security agent at wave merges if one of the
things we're merging is a security issue." Applies to every project under Nortorious-Technologies,
whenever agents build `lane::build-loop` tickets or slices in a loop (`tdd-swarm`, the `fanout-*`
pair, the `cerbo-*` / `equinox-*` pairs, or a workflow script that runs them). Which tickets enter the
loop at all is `ticket-lanes.md`.

**What went wrong.** YourAI's suite is ~2,200 tests and takes 3–7 minutes. Nothing said how much
each role should test, so every role ran everything: worktree setup ran a baseline, the test-writer,
the implementer, both reviewers and the merge agent each ran it again. That was 5–6 full runs per
ticket, about half an hour of each ticket spent re-proving what the last merge gate had already
proven, and with several tickets in parallel the runs competed for the same CPUs. Every ticket also
paid for a separate test-writer and a security audit, though most of them (a map popup, a report
column) had no security surface at all.

## The loop, by ticket kind

**Default: plan → implement → test → review.** The planner writes the plan with the tests it names
(the ticket's WP-N worked pair is one of them). The implementer writes the code **and** those tests
together, runs the affected tests, and commits. `code-review-agent` reviews. The merge runs the
affected tests. No test-writer, no frozen-test manifest, no security agent.

**`risk::security` tickets: test-first, and the security agent at the wave merge.** A ticket gets the
`risk::security` label when a bug in it could leak data, grant access, expose a secret or open the
system to an attacker: auth and authorization, secrets and credentials, encryption and keys, PII/PHI
storage or redaction, untrusted input reaching a model, query, shell or file path, network exposure
(ports, binds, CORS, security groups), deployment and infrastructure config, money movement. For these:
`test-writer-agent` freezes failing tests from the acceptance criteria **before** the implementer
starts (the frozen-test manifest and tamper check apply), and the ticket's diff goes to
`security-privacy-agent` at its wave merge.

**The security agent runs once per wave merge, and only if the wave contains a `risk::security`
ticket.** It reviews those tickets' diffs and the seams they touch, not the whole wave. A wave with no
security ticket has no security review. If `code-review-agent` finds a security surface in an
unlabelled ticket, it says so, the orchestrator adds `risk::security`, and the wave-merge review
covers it. When unsure whether a ticket is security work, ask "would a bug here leak data, grant
access or expose a secret?"; yes means label it.

Example: a wave of five merges. `S-07 door popup`, `S-08 score legend`, `S-09 route export` and
`S-10 seed loader` ran plan → implement → test → review. `S-11 MCP API key check` carried
`risk::security`: frozen tests first, then the same loop, then at the wave merge
`security-privacy-agent` read S-11's diff only. The merge ran the tests affected by all five diffs.

## Only affected tests, at every step

**"Affected" means:** the test folders that mirror the changed packages, plus any test file that
imports a changed module (`grep -rl "<module>" tests/`). At a merge, it is the union over every
ticket in the merge.

| Role | Runs |
|---|---|
| Worktree setup | No baseline suite: main was proven green by its last merge. An import check is enough. |
| Planner | No suite. Read the code; prototype in a scratch copy only when a design choice is genuinely uncertain. |
| Test-writer (`risk::security` only) | Its new or changed test files (red for the right reason), plus the suite's collect-only command to prove everything still collects. |
| Implementer | The affected tests while iterating; once before the final commit, the affected tests plus the project's fast gates (type check, lint, format), with the result in its report. |
| Code reviewer | Type check, lint, and the tests the diff affects. |
| Security reviewer (wave merge, only with a `risk::security` ticket) | No shell, so no tests; reads the security tickets' diffs. |
| Merge agent | On main after the merges: lint and format, type check, then the tests affected by everything merged in the batch (see *Merge in batches, in tree order*). If red, bisect: reset main, re-merge one ticket at a time, send back only the ticket that fails (and its dependants). |

**The full suite runs only in two places:**

1. **When a change reaches everything:** a shared fixture (`conftest.py`), settings or configuration,
   a dependency or lockfile change, a module imported across the codebase, or a seam fix that crosses
   several packages. Say which of these applies.
2. **Before every deploy or release** (tdd-swarm's lesson `learnings/never-deploy-on-a-red-suite.md`):
   nothing deploys on a red full suite.

**Make the gates fast.** Run them cheapest first and stop at the first red: lint and format, then the
type check, then the tests. Run a full suite in parallel (`pytest-xdist`, `-n` about CPUs − 2; with uv,
`uv run --with pytest-xdist pytest -n 6` adds it without a dependency change) only while a trial shows the
same result as the serial run, and **re-check whenever a session-wide plugin lands**. Measured on YourAI,
2026-10-19: 2,689 tests in 4:56 on 6 workers vs 9:46 serial, identical results, until YAI-33 added
end-of-run checks that total results across the whole session; each xdist worker sees only its own slice,
so 4 of them failed in parallel and passed serially. Projects with session-wide checks either run the
suite serially or run those checks in a separate serial step. A YAI-30 merge spent 6.5 minutes on the
suite before failing on three blank lines that lint would have caught in seconds.

**Which tickets enter the loop.** Only `lane::build-loop` tickets (`ticket-lanes.md`). A `lane::direct`
ticket (docs, trackers, review pages: nothing code or tests read) is one general agent with no roles, no
worktree and no merge tests; `lane::spike` follows zero-to-hero's `references/spikes.md`;
`lane::human` is Innocent's.

## Merge in batches, in tree order (never one ticket at a time)

Recorded 2026-10-21 at Innocent's instruction, after the AEA build ran a merge gate per ticket: "we shouldnt be
merging 1 ticket at a time, we should merge in accordance to the tree." Each merge took 3 to 5 minutes and they
queued behind one another while reviewed tickets waited.

**The rule.** Every `lane::build-loop` ticket that has passed review and is waiting goes into **one batch**, and the
merge agent merges the whole batch in dependency order (a ticket's blockers first), one `--no-ff` merge commit per
ticket so history stays per ticket. It runs the gates **once** on the union (lint and format, type check, the tests
and journeys affected by everything in the batch), pushes once, then closes each ticket's issue with its evidence,
removes the worktrees and writes the ledger in one commit.

- **Red gate:** reset to the start of the batch and bisect: re-merge one ticket at a time with that ticket's own cheap
  gates; the ticket that goes red is reset out and sent back, along with its dependants in the batch. Every ticket that
  stays green stays merged. Nothing merges on red.
- **Shared context files** (area map, ICM progress, the code-design "Built" lines, the build ledger) are append-style:
  a conflict confined to them is resolved by keeping both sides' rows. It is never a reason to send a ticket back. Any
  other conflict aborts that ticket's merge only and skips its dependants.
- **Do not wait to fill a batch.** The first merge may be a batch of one. Tickets that finish while a batch runs form
  the next batch. A deeper tree level needs no separate gate; the dependency order inside the batch is enough.
- **One writer on main:** a single merge agent holds the main checkout, and nothing else edits tracked files there
  while it runs (commit plan files and refreshed docs first).
- **Parallelism limits belong on test runs, not on thinking.** Cap implementers that run tests (about CPUs − 2, each
  `pytest -n 2` or less). Do not let planners and reviewers, which wait on the model, take those slots; give them their
  own allowance. Check agents are actually writing: an agent silent for 10 minutes with no test processes is dead and
  holds a slot, so stop and resume the run.

**Example.** Wave 2 has AEA-26 (ledger), AEA-27 (identity) and AEA-28 (scheduling), each reviewed at a different
time, all depending only on merged wave-1 work. Old: three merge agents, three gate runs, three pushes. Now: the
first reviewed ticket merges alone; the two that finish while it runs merge together as the next batch, one gate
run, one push.

## How to apply

- **Orchestrators** merge through one batch merge agent per round (*Merge in batches, in tree order*), not one
  merge agent per ticket. They also dispatch the
  test-writer only for `risk::security` tickets, the security agent only at a wave merge that includes
  one, and never tell a role to "run the full suite" except where this rule says so. This rule overrides
  any such line that slips through.
- **Ticket cutters** (`to-tickets`, zero-to-hero §7) add `risk::security` where it applies and show the
  count in the slice plan next to the lane split.
- **Projects** get a copy at zero-to-hero Stage 0 (`ARTIFACT-MAP.md` §0, *Build loop* set) so
  sessions launched inside one repo load it too. Change this original first, then re-copy.
- **Agent definitions** (`test-writer-agent`, `fanout-planner`, `fanout-implementer`,
  `code-review-agent`, `security-privacy-agent`) each carry one line pointing their role here.

## What this rule does not change

- Nothing merges on red affected tests or red fast gates; nothing deploys on a red full suite.
- For `risk::security` tickets: frozen-test manifests, red-for-the-right-reason and the tamper check.
- Fail-closed checks and every project rule about values, secrets and live calls.
