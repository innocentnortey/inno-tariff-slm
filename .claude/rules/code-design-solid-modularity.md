<!-- Provenance: copied from Nortorious-Technologies/.claude/rules/code-design-solid-modularity.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
---
paths:
  - "**/docs/design/**"
  - "**/ARCHITECTURE.md"
  - "**/docs/plans/**"
  - "**/*.py"
  - "**/*.ts"
  - "**/*.tsx"
---

# Code Design → SOLID, and Look for the Seams Worth Modularizing

Recorded 2026-10-20 at Innocent's instruction: "We should always be using the SOLID framework and
striving for modularity in our design... That doesn't mean modularize everything. We should strive
to look for places where things should be modularized." Applies to every project under
Nortorious-Technologies whenever code is designed: zero-to-hero §6 (DO-3 code design and DO-4
component contracts), a fan-out planner's plan, and any refactor. Projects with their own
code-design rule override this one. File sizes are a separate rule (`code-structure.md`).

## What it looks like in practice

**Input:** a design draft says "`OrderService` validates the cart, prices it, charges the card,
writes the ledger and emails the receipt."

**Process:** ask the SOLID questions of it (below). "Validates *and* prices *and* charges..." fails
the one-sentence test. Ask which parts change for different reasons: pricing rules change when the
business changes them; the card processor changes when we switch vendors; the receipt changes when
marketing asks. Those are three different reasons to change, so they are three seams.

**Output:** `OrderService` sequences the steps and owns nothing else; `Pricer`, a `PaymentGateway`
interface with one adapter per vendor, and `ReceiptSender` each sit behind a small interface the
service receives (injected, not constructed inside). Swapping the card vendor now touches one
adapter file and no caller. Validation stays inline in the service because it is ten lines that
change only when the order shape changes — splitting it out would buy nothing yet.

The last sentence is the point: **look for the seams; cut only the ones that pay.**

## The SOLID questions, asked of every module in the code design

| Principle | Plain meaning | The question to ask |
|---|---|---|
| **S**ingle responsibility | A module has one reason to change. | Can I describe it in one sentence without "and" or "or"? Who would ask for it to change? |
| **O**pen/closed | Add new behaviour by adding code, not by editing working code. | When the next variant arrives (a second venue, vendor, document type), do I add a file or add an `if`? |
| **L**iskov substitution | Anything that claims to implement an interface can stand in for any other. | Does every implementation honour the same contract — same errors, same guarantees — or does a caller have to check which one it got? |
| **I**nterface segregation | Callers depend only on the methods they use. | Does this caller import a big interface to use one method? Split by what callers need. |
| **D**ependency inversion | Business logic depends on abstractions; adapters depend on them too. | Does the core import the database driver, the HTTP client or the LLM SDK directly? Put a small interface between them and inject it. |

In Python these interfaces are `typing.Protocol` classes (or ABCs where the project already uses
them); in TypeScript they are `interface` types. Injection is a constructor or function parameter,
not a framework.

## Where to look for seams (strive for these)

- **Every external system** (database, LLM provider, payment, email, a venue/vendor API) sits behind
  one adapter. This is also what makes tests fast and fakes honest.
- **Every place a second variant is already known or promised** (a roadmap venue, a second document
  type, a second model). Design the interface now; build one implementation.
- **Policy vs mechanism.** Rules that the business changes (pricing, scoring, routing thresholds)
  live apart from the plumbing that executes them.
- **Pure core, impure shell.** Calculations are pure functions over typed models; I/O happens at the
  edges. The money split, the score, the classifier's decision logic are all pure and unit-testable.
- **Things that change at different rates.** Put stable things where volatile things depend on them,
  never the reverse.

## Where not to (the counterweight)

- **Don't build an abstraction for a variant nobody has asked for.** One implementation and no known
  second one → no interface yet; note the seam in the design so it is cheap to add later.
- **Duplication is far cheaper than the wrong abstraction** (Sandi Metz, 2016). Wait for the second,
  ideally third, real case before extracting shared code. When a shared function has grown flags and
  conditionals for each caller, inline it back into the callers, keep what each one needs, delete the
  rest, then extract again if a real abstraction shows itself.
- **Don't split by layer for its own sake.** A module boundary must hide a decision that might
  change. Splitting a ten-line function into three files hides nothing.
- **Time-boxed builds** (1–2 day hiring-partner projects) still get adapters around external systems
  and a pure core; they skip speculative interfaces.

## Why modularity is also a speed decision

Clean module boundaries are what let §7 tickets run in parallel: two tickets that touch different
modules behind agreed interfaces can be built by two agents at once and collide on nothing
(`to-tickets` §2a, *collision map*). A design where every feature edits one god-module forces
every ticket into a single line. So DO-3 names each module's owner area and its interface, and §7
uses those boundaries to cut wide waves.

## How to apply

- **§6 code design (DO-3):** for each module, write its one-sentence responsibility, the interface it
  exposes, what it depends on (abstractions, not concretions) and which direction the dependency
  points. Mark each considered seam **cut** or **deferred** with one line of why.
- **Review:** `metz-code-design-agent` (`.claude/agents/`) reviews DO-3 before the Stage 6 page is
  built, and may be asked to review any plan or diff for design.
- **Builders and reviewers:** a fan-out plan names the interfaces a slice implements or consumes;
  `code-review-agent` flags a core module importing an adapter's concrete class or SDK directly.
- **Projects** get a copy at zero-to-hero Stage 0 (`ARTIFACT-MAP.md` §0, *Build loop* set). Change
  this original first, then re-copy.
