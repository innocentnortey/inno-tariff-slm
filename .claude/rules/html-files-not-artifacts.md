<!-- Provenance: copied from Gauntlet AI/.claude/rules/html-files-not-artifacts.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
# HTML Means a File, Never a Claude Artifact

Innocent makes and shares HTML pages himself. This mirrors the workspace-wide rule in `Nortorious-Technologies/.claude/rules/html-files-not-artifacts.md`, kept here so it also holds when a session is launched inside `Gauntlet AI/`.

## Rules

1. **Never publish.** Do not call the `Artifact` tool for any action, and do not load `artifact-design`, `artifact-capabilities`, `artifact-diagramming` or `design`. "Make an HTML", "a briefing", "a page" means write a local file.
2. **Complete, standalone document.** `<!doctype html>`, `<html lang="en">`, a `<head>` with charset, viewport and `<title>`, then `<body>`. It must open correctly by double-clicking.
3. **Self-contained.** Inline CSS and JS; any external font or script needs a working fallback.
4. **Location.** `artifacts/YYYY-MM-DD-[name].html` in this project. HTML *renders* of existing prep docs live alongside them in `artifacts/` with the same date and name as the source doc.
5. **Report the path** and the command to open it: `open "/Users/innocentnortey/Desktop/Nortorious-Technologies/Gauntlet AI/artifacts/<file>.html"`.
6. **Design quality still matters** — hierarchy, palette, both themes, phone width. Only the delivery changes.
