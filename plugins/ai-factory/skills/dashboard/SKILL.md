---
name: dashboard
description: Refreshes the ai-factory dashboard - a private claude.ai page with one tab per project registered on this machine, showing what waits for the user (validation queue, blocked tickets, staging), the tickets by step of the chain, open MRs/PRs, lead time, review rounds, approvals accepted unchanged, health, and a daily trend. Reads local files and the tools in read-only mode; writes only the dashboard. Use for "/ai-factory:dashboard", "refresh the dashboard", "show me the factory", "where are my projects at".
argument-hint: "[register | page]"
---

# /ai-factory:dashboard

**Plugin root**: two directories above this skill's base directory.

Read-only toward the projects: this skill changes no ticket, MR/PR, branch or profile. It writes
the dashboard, `~/.ai-factory/` (the registry, the history, the dashboard's address) and the two
`dashboard-*.json` snapshots in each project's `state/pilot/`.

## 1. The projects

`~/.ai-factory/projects.json` lists the project roots of this machine. The current project (found
as in `core/architecture.md`) is added if missing: `python3 <plugin root>/scripts/dashboard-data.py --register <root> --out <tmp>`
(argument `register`: only that, then stop). A root that no longer holds a profile shows as a
broken health row; say so and offer to remove it from the registry.

## 2. Live snapshots, per project

What the script cannot read from files, written beforehand in `<root>/.ai-factory/state/pilot/`:

- `dashboard-backlog.json`: the tickets of the development queue (`workflow.md`, "Dev queue"; the
  ticketing adapter's `list`), as `[{key, title, type, priority, created_at}]`. The script drops
  those that already have a ticket folder: they are counted at their step of the chain.
- `dashboard-queue.json` (only for the `artifact` queue adapter; the `file` adapter is read by the
  script): every action of the validation queue (`adapters/queue/artifact.md`, `pending_decisions`
  without the status filter), as `[{id, ticket, pilot, type, status, summary, created_at, decided_at}]`.
- `dashboard-prs.json`: the open MRs/PRs of the project's repositories (forge adapter, `find` with
  no key, then `state`), as `[{id, ticket, repo, number, url, state, draft, opened_at, age_days,
  unresolved_threads, approvals, approvals_needed}]`; `id` is `<repo>#<number>` (GitHub) or
  `<repo>!<number>` (GitLab), `ticket` the key found in the branch name, `approvals_needed` from
  `workflow.md` ("Review rule").

A tool that fails leaves the previous snapshot in place: say which, and go on.

## 3. Build the datasets

```bash
python3 <plugin root>/scripts/dashboard-data.py --out <scratch dir>
```

It writes `projects.json`, `tickets.json`, `backlog.json`, `queue.json`, `prs.json`, `health.json` and
`history.json`, and records today's snapshot per project in `~/.ai-factory/history/<slug>.jsonl`
(one line a day, the last refresh of the day wins). Nothing in them is personal data beyond
ticket keys and titles; check the titles hold none before uploading.

## 4. The dashboard

The dashboard is an Artifact made from the **Dashboard** type. Its address is in
`~/.ai-factory/dashboard.json` (`{"url"}`). None there: list the user's artifacts of type
"Dashboard" and take the one titled "ai-factory"; none either: find the type with the Artifact
tool's quickstart (`intent: "other"`), create the dashboard from it titled "ai-factory", and save
its address. Follow the type's own instructions for everything below; this section only says what
goes where.

- **Datasets** `projects`, `tickets`, `backlog`, `queue`, `prs`, `health`, `history`: each an attached file.
  Upload each JSON file as an asset, then update its dataset document with the new `url`, `name`
  and `updated` (`{at: now, by: "ai-factory dashboard"}`), `schedule` and `staleAfterHours: 48`.
  The titles: "Projects", "Tickets", "Development queue", "Validation queue", "Open MRs/PRs", "Health checks", "Daily
  snapshots", each with a one-line description of its source. Then delete the asset each dataset
  pointed to before, if no other document names it.
- **Page** `files/index.html`: the text of `<plugin root>/templates/dashboard/index.html`. Written
  when the dashboard has no page, or when the page's `<meta name="ai-factory-dashboard">` version is
  older than the template's (argument `page`: rewrite it whatever its version). The user may have
  edited the page by hand: before replacing an older one, say so and ask, unless the argument is
  `page`.
- **Language**: the page speaks the language of the onboarding. `~/.ai-factory/dashboard.json`
  keeps it as `language`, set at creation from the current project's `onboarding.language` (else
  `project.working_language`); when registered projects use different languages, ask once which
  one the page uses. The template is in English: before writing it, translate every text a reader
  sees — the HTML's text and `aria-label`s, and the constants `STAGES[].label`, `STAGE_TEXT` and
  `TIP_TEXT` — and set `LOCALE` and the `data-lang` of its `<meta>` to the language code. Never
  translate code, classes, `data-*` attributes, dataset ids or column names, and leave data values
  (ticket states, statuses) as they are: the page shows them as stored. A page whose `data-lang`
  differs from `language` is rewritten like an older one.
- Then the type's check of the page, as its instructions say.

## 5. Report

In a few lines, per project: what waits for the user (pending actions, blocked tickets with their
reason, tickets in staging), and the dashboard's link. The link of one project's tab is the
dashboard's link followed by `#<slug>`.

Without the Artifact tool (a terminal with no claude.ai account): skip step 4 and give the report
alone, from the datasets.
