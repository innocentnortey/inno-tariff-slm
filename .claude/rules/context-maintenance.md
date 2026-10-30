# Context maintenance (project-wide; read on any task that moves code, data, an eval or an owner)

Made by `icm-project` 1.6.1 on 2026-10-30. Applies to every task in this repo; it is not path-scoped.

- **Same-task reconciliation.** When a meaning, boundary, contract, location, workflow or recurring lesson changes, update its owning record (planning doc, `docs/data/README.md`, eval docs) and the affected router row and rule in the same task.
- **Evidence over memory.** Link each conclusion to its source or run output. Keep *planned*, *built* and *verified* distinct; a scaffold proves nothing works.
- **Status in place.** A status cell (router, ICM checklist, area map) holds one current account; replace it, never append. History goes to the dev log.
- **The entry is not a map.** The entry file changes only when identity, a boundary or a route changes; maps, status and decisions live in their owners (router, checklist, planning docs).
- **Dev log.** Write `docs/devlog/YYYY-MM-DD-<topic>-<run-id>.md` at the first meaningful outcome of a run; one entry per milestone (Changed / Why / Checked / Remaining), 50–100 words.
- **ICM rows.** When a code design, scaffold, slice or test changes what a route can be checked against, update the affected row in `.claude/state/icm-progress.md` with its evidence link.
- **Eval sets are frozen artifacts.** Changing an expected label takes its own commit with a reason; never edit an expected output to turn a run green.
- **Hand-off.** Leave `.claude/state/resume.md` naming the next action; live status stays in `PROJECT-CHECKLIST.md` and `SUBMISSION.md`.
- **Reopen intake** when a change invalidates the behavior spec or the data plan.
