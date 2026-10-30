<!-- Provenance: copied from Gauntlet AI/.claude/rules/gauntlet-hosting-default.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
# Render Is the Default Host for Gauntlet Projects

Project-wide. Recorded 2026-10-22 at Innocent's instruction ("Render is the new default for all
Gauntlet projects, replacing Railway"). It replaces the 2026-10-10 rule that made Railway the default;
that history is kept at the end of this file.

**The rule.** When a Gauntlet project (weekly build or hiring-partner project) needs a deployed
runtime, deploy it on **Render** in Innocent's workspace (`tea-dbclmj0m7kps73c58b8g`, "My Workspace"),
region **Ohio**, as a Docker web service built from the repo's `Dockerfile`. Don't open a hosting
decision from scratch, and don't reach for Railway, Vercel or Netlify by default. Start at the
smallest paid size and size up only with Innocent's OK.

**Deployment flow: GitLab → GitHub mirror → Render.** Gauntlet's GitLab stays the source of truth
(`gauntlet-gitlab-versioning.md`). Each deployed project gets a GitHub repo under
`innocentnortey/<repo>` fed by a **GitLab push mirror** (all branches, keep divergent refs), and the
Render service builds from that GitHub repo's `main`. Never commit to the GitHub copy directly; a fix
made there is reconciled into GitLab first, then flows back out through the mirror. Example: the
HouseAccount start fix was committed on GitHub's `render-migration` branch during the move, then
fast-forwarded into GitLab `main` (2026-10-22) so the mirror, not a hand push, carries it.

**Why.**
- Railway paused platform builds on 2026-10-21 (incident QH8L8B3E) and every Gauntlet deployment was
  stopped; Innocent moved the live projects to Render the same day.
- A long-running Docker process keeps what the Railway rule valued: no per-request cold starts, a
  persistent database pool, one dashboard and one billing line.
- Paid instances never spin down, and a persistent disk gives SQLite or file-backed apps durable storage.

**Facts to cite (render.com/docs, read 2026-10-22; prices are the ones on Innocent's account for the
2026-10-21 migration, so check the pricing page before quoting them as current).**
- Web service Starter (0.5 CPU / 512 MB): **$7/month**. Free instances spin down after 15 minutes
  without traffic (about a minute to wake), have no persistent disk, shell or one-off jobs, and may be
  restarted at any time, so they are for throwaway previews only.
- Render Postgres Basic-256mb: **$6/month** plus **$0.30/GB-month** storage. Free Postgres expires
  30 days after creation (14-day grace, then deleted) and has no backups, so never use it for a demo
  that must survive a review.
- Persistent disk: **$0.25/GB-month**. A service with a disk runs one instance only and loses
  zero-downtime deploys; build and pre-deploy commands can't see the disk; snapshots are daily and kept
  at least 7 days.
- Logs: 7-day retention on the Hobby workspace plan; at most 6,000 application log lines per minute
  per instance (excess lines are dropped).

**How to apply.**
- In a project's PRD or decision record, the hosting decision reads "Render (Gauntlet default,
  `Gauntlet AI/.claude/rules/gauntlet-hosting-default.md`)" plus any project-specific reason.
- Spend ceilings name the actual monthly line items (instance, database, disk). Innocent's approved
  total for Render hosting is **$40/month across all projects** (2026-10-21); a new service that would
  push the total over it needs his OK first.
  **2026-10-25:** Innocent approved a workspace total of about **$67/month** to host Newsela Lesson Studio
  (3 Starter services + Render Postgres, +$27.30 on top of $39.80 after Riverside was removed): "yeah thats fine".
  This approval covers Newsela only; any further service still needs his OK.
- Secrets live in a Render **environment group** linked to the service, never committed and never in a
  Dockerfile `ENV`/`ARG`. Migrations run at app start or as the service's pre-deploy command.
- Postgres: Neon (free tier) stays acceptable, or the project uses Render Postgres so the deployment
  lives in one place (HouseAccount and Riverside do). Keep `ipAllowList: []` (no external access)
  unless a check needs it, and close it again afterwards.
- Version stamps read `RENDER_GIT_COMMIT` (set at build and run time); never invent a version.
- Auto-deploy follows the mirror (trigger `commit` on `main`) once a project is live; keep it off while
  a service is in maintenance mode for a data restore.
- If a brief *requires* another host, the brief wins; record the exception.

## Project-specific state and exceptions (kept)

| Project | Host | Note |
|---|---|---|
| HouseAccount (`inno-houseaccount`) | Render (moved 2026-10-21) | `srv-dbco0u3rjlhs73e4qalg`, Render Postgres, 5 GB disk at `/data`. Its `RAILWAY_PUBLIC_DOMAIN` variable is intentional: the app reads that name to allow its MCP host. |
| Riverside Onboarding (`inno-riverside-onboarding`) | Removed 2026-10-25 | Was on Render 2026-10-21 → 2026-10-25 (`srv-dbcnucbrjlhs73e4hss0` + its Postgres); both deleted at Innocent's instruction once the project was done. Fresh synthetic seed only, nothing restored. |
| AEA call center (`inno-aea-callcenter`) | Render (moved 2026-10-22) | `srv-dbcogjjrjlhs73e68vhg`, SQLite on a 1 GB disk at `/data`; the issued dataset in the image stays read-only. |
| Cerbo, Equinox, YourAI and other earlier builds | Railway (historical) | Their Railway deployments were stopped on 2026-10-21 with projects and volumes retained. Their docs describe Railway as it was; moving any of them is a separate decision. Cerbo's choice of the host's own Postgres (PRD §13 R-DB) is the precedent for the Postgres bullet above. |

Old `*.up.railway.app` URLs are historical, not live deployments.

## History: the Railway default (2026-10-10 → 2026-10-21)

Recorded 2026-10-10 ("we're already using Railway; that should be a default for all Gauntlet
projects"). Railway was already paid for (Equinox, Cerbo); its Hobby plan was $5/month including $5
of usage, with 7-day logs. Retired 2026-10-22 by this rule.
