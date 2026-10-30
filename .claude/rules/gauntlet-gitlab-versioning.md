<!-- Provenance: copied from Gauntlet AI/.claude/rules/gauntlet-gitlab-versioning.md on 2026-10-30 (zero-to-hero Stage 0). Change the original first, then re-copy. -->
# Version Control Lives on Gauntlet's GitLab

Every code project that comes out of the Gauntlet program is versioned on **Gauntlet's GitLab at
`labs.gauntletai.com`**, over SSH, under Innocent's account `@innocentnortey`. Not GitHub, not Azure
DevOps. Decided 2026-09-14.

> **Reference, not an always-loaded rule (2026-09-19).** Most of this file is SSH troubleshooting
> that matters on two days out of a hundred — a new machine and an expired key. Spin-off repos should
> carry the *policy* (four lines: `origin` is Gauntlet GitLab, `upstream` is read-only, no GitHub
> mirror, push only when asked except in factory mode) in their entry point or a short provenance rule, and link here for
> the mechanics. `inno-agentforce` does this in `.claude/rules/project-provenance.md`.

**This is the original.** Spin-off repos carry a copy; change this one first, then re-copy.

## What it looks like in practice

A new Gauntlet repo has two remotes:

| Remote | Points at | Use |
|---|---|---|
| `origin` | `git@labs.gauntletai.com:innocentnortey/<repo>.git` | Where all work is pushed. |
| `upstream` | Gauntlet's starter repo, e.g. `https://github.com/Gauntlet-HQ/openemr-base-clean.git` | Read-only. Fetch from it; **never push to it.** |

Example — `inno-agentforce` (weeks 1–3 AgentForge):

```
origin    git@labs.gauntletai.com:innocentnortey/inno-agentforce.git
upstream  https://github.com/Gauntlet-HQ/openemr-base-clean.git
```

## Spin-off repos

| Repo | Created | `upstream` | `origin` status |
|---|---|---|---|
| `../inno-agentforce/` | 2026-09-14 | `Gauntlet-HQ/openemr-base-clean` | live on GitLab |
| `../inno-attackforge/` | 2026-09-29 | none (greenfield) | live on GitLab |
| `../inno-equinox/` | 2026-10-06 | none (greenfield) | live on GitLab (first push 2026-10-09) — PEAK6 hiring-partner project; private; `origin` = `innocentnortey/inno-equinox` |
| `../inno-cerbo/` | 2026-10-09 | none (greenfield) | **live on GitLab** (`innocentnortey/inno-cerbo`, created 2026-10-10; first push the same evening). Innocent approved (2026-10-09) a **GitHub mirror** for the submission if needed, since the brief requires a GitHub repo — a deliberate exception to rule 4 for this repo only |
| `../inno-aea-callcenter/` | 2026-10-14 (as `inno-aea-onboarding`; renamed 2026-10-20) | none (greenfield) | **not created yet** — local git only; snapshot commit `ed4ca89` (tag `project-1-onboarding-snapshot`) 2026-10-20. Intended `origin` `innocentnortey/inno-aea-callcenter`. The call-center brief asks for a "source repository" without naming GitHub; a mirror is **not approved** |
| `../inno-houseaccount/` | 2026-10-15 | none (greenfield) | **created by Innocent 2026-10-18** (`innocentnortey/inno-houseaccount`); `origin` added and SSH verified 2026-10-18; remote holds a GitLab-generated README commit; no local push yet |
| `../inno-houseaccount-data-layer/` | 2026-10-27 | none (greenfield) | **created by Innocent 2026-10-27** (`innocentnortey/inno-houseaccount-data-layer`); `origin` added and SSH verified the same day; not public (unauthenticated API 404); remote holds GitLab's README commit `fef751b`; no local push yet. Second HouseAccount hiring-partner project; due Wed 2026-10-28 midnight |
| `../inno-riverside-onboarding/` | 2026-10-15 | none (greenfield) | **not created yet** — local files only, no `git init` yet. Intended `origin` `innocentnortey/inno-riverside-onboarding`. The brief requires a GitHub repo, so a mirror will likely be requested; **not yet approved** (row added 2026-10-17) |
| `../inno-yourai-pipeline/` | 2026-10-17 | none (greenfield) | **created by Innocent 2026-10-19** (`innocentnortey/inno-yourai-pipeline`, **private**: confidential brief); `origin` added and SSH verified; GitLab issues #1–#38 hold the tickets; first push `7f2d01a` 2026-10-19 (fast-forward over GitLab's initial commit). **Found public right after that push and set private** (2026-10-19 08:08 UTC): check `visibility` via the API before any first push. The brief accepts GitLab, so no GitHub mirror |
| `../inno-newsela/` | 2026-10-24 | none (greenfield) | **created by Innocent 2026-10-25** (`innocentnortey/inno-newsela`, id 2346); it was **public on creation and was set private** before any push, the same lesson as YourAI. `origin` added on the VPS working copy; the remote holds GitLab's README commit. The two-phase VPS run pushes in factory mode. No GitHub mirror (the demo runs under local Docker Compose, PD-15 option D) |
| `../inno-goodleap/` | 2026-10-28 | none (greenfield) | **created by Innocent 2026-10-28** (`innocentnortey/inno-goodleap`); `origin` added and SSH verified the same day; private through the overnight build, **set public 2026-10-29** at Innocent's instruction for the submission; first push 2026-10-29 (built overnight on the VPS). **GitHub mirror approved 2026-10-29** (Innocent): `github.com/innocentnortey/inno-goodleap`, public, same history as GitLab; the submission URL. Confidential sources are git-ignored and absent from it |

Add a row here whenever a new spin-off is created.

## The SSH setup (already done on Innocent's Mac, 2026-09-14)

- **Key:** `~/.ssh/gauntlet_gitlab` (ed25519, labelled `innocent.nortey@challenger.gauntletai.com`), registered in GitLab → User Settings → SSH Keys, expires 2028-02-02.
- **`~/.ssh/config`** routes the host to that key **and port 22022**:
  ```
  Host labs.gauntletai.com
    HostName labs.gauntletai.com
    Port 22022
    User git
    IdentityFile ~/.ssh/gauntlet_gitlab
    IdentitiesOnly yes
  ```
- **Check it works:** `ssh -T git@labs.gauntletai.com` → `Welcome to GitLab, @innocentnortey!`

## ⚠️ The port is 22022, not 22

GitLab's web UI sits behind Cloudflare; its git SSH listens on **22022**. Port 22 on the same hostname is the server's own sshd — it answers, it accepts the key offer, and it always says `Permission denied (publickey)`, while GitLab shows the key as "Last used: Never". That cost an hour on 2026-09-14.

Because `~/.ssh/config` supplies the port, both URL forms work:

- `git@labs.gauntletai.com:innocentnortey/<repo>.git` (short form, relies on the config)
- `ssh://git@labs.gauntletai.com:22022/innocentnortey/<repo>.git` (explicit — use this on any machine without the config, e.g. CI)

## Rules

1. **New Gauntlet repo → `origin` on Gauntlet GitLab.** Create the project under `innocentnortey/` in the GitLab UI (repos are created by Innocent, not by Claude), then `git remote add origin git@labs.gauntletai.com:innocentnortey/<repo>.git`.
2. **Starter code from Gauntlet stays `upstream`**, fetch-only.
3. **Push and commit only when Innocent asks, except in factory mode.** This rule says *where* code goes, not *when*. **Factory mode** (a project's published tickets running through the build loop) has standing authorization to commit and push to that project's `origin` (Innocent, 2026-10-19: "you have my authorization to push when in factory mode"). Never to `upstream` or any other remote.
4. **Never add a GitHub `origin` for Gauntlet work** without Innocent's explicit say-so.
5. **`Gauntlet AI/` itself (these notes) has no remote.** Whether it goes to GitLab is undecided — it holds cohort transcripts and personal prep. Don't add one without asking.
6. **Auth fails? Check the port before touching the key.** Confirm with `ssh -G labs.gauntletai.com | grep '^port'` (should be `22022`). On a machine without the config, the real SSH address is readable without login from `https://labs.gauntletai.com/api/v4/projects?simple=true` → `ssh_url_to_repo`. Verify the host key against GitLab's published ED25519 fingerprint `SHA256:QXLFdV0nmOn54FOgD9b08oZdELkhfBclNehZCcsDh3s` (`/help/instance_configuration`). Don't retry port 22 repeatedly — it started timing out after a few failures.
7. **New machine or expired key:** `ssh-keygen -t ed25519 -C "innocent.nortey@challenger.gauntletai.com" -f ~/.ssh/gauntlet_gitlab`, add the `Host` block above, paste the `.pub` into GitLab with **Cmd+V from the clipboard** (`pbcopy < ~/.ssh/gauntlet_gitlab.pub`) — copying from a terminal or chat mangled the key once and GitLab rejected it as "Key type is forbidden".
