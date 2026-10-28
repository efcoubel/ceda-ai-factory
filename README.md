# ai-factory

A Claude Code plugin that turns your tickets into an assembly line: Claude frames, codes, reviews,
tests and ships each ticket, and two pilots (support and dev) loop on their own. Every action that
leaves your machine — an answer to a requester, a status change, a push, a merge request — waits in
a validation queue until you approve it.

It works with the tools you already use. An onboarding discovers your repositories, stack,
ticketing, forge, chat, data and logs, asks only what it could not find, and writes a project
profile. The engine stays the same; the profile makes it yours.

> Status: **0.1, early**. The onboarding and the doctor are written; the ticket chain and the
> pilots are being ported from a production setup. See [the roadmap](#roadmap).

## What it does

- **`/ai-factory:onboarding`** — discovers the project, interviews you on the gaps, shows a recap,
  writes `.ai-factory/` in your project, creates the validation queue, runs the doctor.
- **`/ai-factory:doctor`** — checks every access the profile relies on, with the fix for each
  broken one.
- **The ticket chain** *(coming)* — `ticket-1-frame` → `ticket-2-code` → `ticket-3-review` →
  `ticket-4-test` → `ticket-5-ship` → `ticket-6-feedback` → `ticket-7-staging`, or `ticket <KEY>`
  end to end, stopping only at its checkpoints.
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
- **Nothing leaves your machine without approval**, except the few *delegated* actions you can list
  and change (`core/autonomy.md`). New projects start in `dry` mode: even those wait.
- **No secret in the profile.** It names where secrets live (a file section, an env var), never
  their values, so it can be committed and shared.

## Install

```bash
claude plugin marketplace add <github owner>/ceda-ai-factory
claude plugin install ai-factory@ceda
```

Then, in your project's root folder: `/ai-factory:onboarding`.

To try it without installing, from a clone:

```bash
claude --plugin-dir /path/to/ceda-ai-factory/plugins/ai-factory
```

## Roadmap

- 0.1 — onboarding, doctor, adapters, protected-branch hook, validation page.
- 0.2 — the ticket chain.
- 0.3 — the dev pilot and the review skills for teams.
- 0.4 — the support pilot.
- 0.5 — earned autonomy and a dashboard of what the pilots did.

## License

MIT
