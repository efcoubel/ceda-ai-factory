# ai-factory

A Claude Code plugin that turns your tickets into an assembly line: Claude frames, codes, reviews,
tests and ships each ticket, and two pilots (support and dev) loop on their own. Every action that
leaves your machine — an answer to a requester, a status change, a push, a merge request — waits in
a validation queue until you approve it.

It works with the tools you already use. An onboarding discovers your repositories, stack,
ticketing, forge, chat, data and logs, asks only what it could not find, and writes a project
profile. The engine stays the same; the profile makes it yours.

> Status: **0.2, early**. The onboarding, the doctor, new projects and the ticket chain are
> written; the pilots are being ported from a production setup. See [the roadmap](#roadmap).

## What it does

- **`/ai-factory:onboarding`** — discovers the project, interviews you on the gaps, shows a recap,
  writes `.ai-factory/` in your project, creates the validation queue, runs the doctor.
- **`/ai-factory:doctor`** — checks every access the profile relies on, with the fix for each
  broken one.
- **`/ai-factory:dashboard`** — one claude.ai page with a tab per project of your machine: what
  waits for you, the tickets by step, open MRs/PRs, lead time, review rounds, health, a daily
  trend.
- **`/ai-factory:new-project`** — starts a project from an empty folder with you: frames the
  product (light, or `full` with personas, journeys and risks), chooses the stack together, creates
  the repositories with the stack's official generator, the remote, branch protection and CI, sets
  up the ticketing and seeds the backlog, then writes the profile. The onboarding offers it when
  the folder holds no repository.
- **The ticket chain** — `ticket-1-frame` → `ticket-2-code` → `ticket-3-review` (a fresh agent) →
  `ticket-4-test` → `ticket-5-ship` → `ticket-6-feedback` → `ticket-7-staging` (a staging branch,
  a release to testers or a staging deploy), or `/ai-factory:ticket <KEY>` end to end, stopping
  only at its checkpoints.
- **The pilots** *(coming)* — `support` triages and answers support requests; `dev` moves
  development tickets in priority order. Both run in a loop (`/loop 30m /ai-factory:dev pilot`).

## Supported tools

| Category | Tools |
|---|---|
| Ticketing | Jira · Notion · GitHub Issues · none (local tickets) |
| Forge | GitLab · GitHub |
| Chat | Microsoft Teams · Slack · Discord · none |
| Data | MySQL/MariaDB · PostgreSQL · Firestore · none |
| Logs | Grafana/Loki · Sentry · none |
| Validation queue | claude.ai artifact page · local markdown file |

Each tool is an adapter file in `plugins/ai-factory/adapters/`; adding one is a pull request.
Adapters marked `draft` have not run on a real project yet.

## Safety

- **Production data is never connected to.** Diagnosis runs on copies; fixes are scripts you run.
- **Protected branches are never merged or pushed to** by Claude: a hook blocks it.
- **Production is never deployed to or written** by Claude: a second hook blocks deploy and cloud
  commands that name a production project, alias or bucket from the profile.
- **Nothing leaves your machine without approval**, except the few *delegated* actions you can list
  and change (`core/autonomy.md`). New projects start in `dry` mode: even those wait.
- **No secret in the profile.** It names where secrets live (a file section, an env var), never
  their values, so it can be committed and shared.

## Install

```bash
claude plugin marketplace add efcoubel/ceda-ai-factory
claude plugin install ai-factory@ceda
```

Then, in your project's root folder — or in an empty folder for a new project:
`/ai-factory:onboarding`.

To try it without installing, from a clone:

```bash
claude --plugin-dir /path/to/ceda-ai-factory/plugins/ai-factory
```

## Roadmap

- 0.1 — onboarding, doctor, adapters, protected-branch hook, validation page; new projects (0.1.2).
- 0.2 — the ticket chain; the dashboard (0.2.3).
- 0.3 — the dev pilot and the review skills for teams.
- 0.4 — the support pilot.
- 0.5 — earned autonomy, with its figures on the dashboard.

## License

MIT
