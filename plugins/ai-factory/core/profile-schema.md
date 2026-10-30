# The profile schema

`/ai-factory:onboarding` writes these files under `<project root>/.ai-factory/`. Templates are in
`templates/profile/`. Every skill reads them; only the onboarding (and the user) rewrites them.
`learnings.md` is the exception: pilots add findings to it, as "`learnings.md`" below says.

## `profile.json`

```json
{
  "schema": 1,
  "project": {
    "name": "Lima",
    "kind": "personal",
    "organization": null,
    "team": "solo",
    "members": [],
    "working_language": "fr"
  },
  "tools": {
    "ticketing": { "adapter": "notion", "config": {} },
    "forge": { "adapter": "github", "config": { "mr_options": { "squash": true, "delete_branch": true, "draft": false } } },
    "chat": { "adapter": "none", "config": {} },
    "database": { "adapter": "firestore", "config": {} },
    "logs": { "adapter": "none", "config": {} },
    "queue": { "adapter": "artifact", "config": { "url": null, "page_version": null } }
  },
  "repos": [
    {
      "name": "lima",
      "path": "lima",
      "remote": "git@github.com:<owner>/lima.git",
      "default_branch": "main",
      "staging": { "kind": "release", "build": "flutter build apk --release", "how": "firebase appdistribution:distribute …", "target": "testers", "unattended": false },
      "protected_branches": ["main"],
      "commit_language": "en",
      "commit_format": "conventional",
      "commit_examples": ["feat(US-3.2): Add offline queue", "fix: Keep the session after refresh"],
      "branch_format": "<KEY>-<slug>"
    }
  ],
  "pilots": {
    "support": { "enabled": false },
    "dev": { "enabled": true, "max_in_chain": 3, "notify": true, "quiet_hours": { "enabled": false, "from": "22:00", "to": "07:00" } }
  },
  "autonomy": { "start_mode": "dry" },
  "production_targets": ["lima-prod-ec"],
  "unattended": {
    "auto_plan": false,
    "low_risk": ["cause_proven", "single_repo", "no_data_migration", "no_dependency_change", "no_public_contract", "small", "type_allowed"],
    "types": ["bug", "task"],
    "max_files": 5,
    "max_ready": 5,
    "max_ticks_per_day": 30,
    "max_tickets_per_day": 6
  }
}
```

| Field | Values |
|---|---|
| `project.kind` | `company`, `client`, `personal`, `open-source` |
| `project.team` | `solo`, `team` ; `members` lists people with their handle per tool (`{"name", "ticketing", "forge", "chat"}`) |
| `project.working_language` | ISO code; language of answers, ticket comments, plans. Commits follow `repos[].commit_language` |
| `tools.<category>.adapter` | a file name in `adapters/<category>/` without `.md`, or `none` |
| `tools.<category>.config` | what that adapter's "Profile config" section asks for. **Never a secret**: secrets are named by reference (env var, file and section, vault path) |
| `repos[].path` | relative to the project root |
| `repos[].staging` | how a change reaches testers: `branch`, `release`, `deploy` or `none`, or a list of them run in order (`core/staging.md`) |
| `tools.forge.config.mr_options` | `draft`, `reviewers`, `labels` (applied at opening) and `squash`, `delete_branch` (at merge, by the user or the forge's settings; `adapters/forge/contract.md`) |
| `repos[].protected_branches` | branches no skill ever merges into or pushes to; the hook enforces it |
| `production_targets` | production project ids, aliases, clusters, apps or buckets that deploy and cloud CLIs (`firebase`, `gcloud`, `kubectl`, `fly`, `vercel`, `aws`…) must never name; the second hook blocks them, with the database's production projects and the `.firebaserc` aliases pointing to them. It covers those CLIs only: a production host reached any other way is protected by the rules, not the hook |
| `repos[].commit_format` | `conventional`, or the repository's own convention in words (`US-<epic>.<n>: <subject>, or Fix: <subject>`) |
| `repos[].commit_examples` | two or three real subjects from the history; the code step writes commits that look like them |
| `repos[].branch_format` | the branch name pattern, with `<KEY>` for the ticket key (`tools.ticketing.config.key`) |
| `tools.ticketing.config.key` | where a ticket's key lives and how new keys are numbered (`adapters/ticketing/contract.md`, "Ticket keys"); absent means `native` |
| `pilots.dev.notify` | `true` (default): one desktop notification per tick when something new waits for the user, pushed to the phone when Remote Control is connected; `false`: none |
| `pilots.dev.quiet_hours` | off by default; when `enabled`, between `from` and `to` (local time) a tick only carries out approved actions: nothing new starts, nothing is posted |
| `autonomy.start_mode` | `dry` (everything queued) or `normal` (delegated actions run) |
| `unattended.auto_plan` | `true`: the pilot approves its own plan for low-risk tickets and works them up to `tested` without waiting (`core/autonomy.md`, "Working while the user is away") |
| `unattended.low_risk` | the criteria a ticket must all meet to be low-risk, taken from the list in `core/autonomy.md`; dropping one makes the rule looser, and only listed criteria are understood |
| `unattended.types`, `max_files` | ticket types and plan size that can be low-risk |
| `unattended.max_ready` | tickets at `tested` waiting for shipping, beyond which nothing new starts |
| `unattended.max_ticks_per_day`, `max_tickets_per_day` | daily caps that bound the cost of a long absence; `null` means no cap on that count |

## `repos.md`

One `## <repo name>` section per repository:

- **Purpose**: what the repository is for, in business terms, two or three lines.
- **Stack**: language and version, framework, package manager, main libraries.
- **Talks to**: the other repositories or services it calls and is called by.
- **Commands**: install, run locally, unit tests, static analysis, lint, build. Each with where it
  runs (host, container name, emulator) and `unattended: yes` when a pilot can run it with nobody
  around (no device to plug, no login to type, no emulator to start by hand), and `takes:` for any
  command longer than a minute (`core/chain.md`, "Long commands").
- **Worktree**: what a fresh worktree needs before the commands run there: the ignored files to
  copy (dependencies, a local env file, a build the tests expect), the ignored folders to link, and
  the command that serves the branch, or "not possible". What holds code is copied: a link would
  run the main checkout's. A project with no pilot worktrees can leave it out.
- **Conventions**: what a reviewer would flag (from the repo's own rules files and history), and
  whether the repository follows its language's formatter (`dart format`, `prettier`, `black`…).

## `environments.md`

One `## <environment>` section (local, staging, preprod, production…): URLs, how data is read
(adapter and reference), how logs are read, what the data is (real copy, fixtures, yesterday's
production), and **what is forbidden** (production writes are always forbidden to Claude).

## `workflow.md`

- The ticketing **queues**: the query that lists support tickets and the one that lists dev
  tickets, in the tool's own query language.
- The **status map**: each tool status → engine state (`core/architecture.md`).
- The **transitions** the chain uses (start work, ask for review, mark approved, done), by target
  status name, never by id.
- The **fields** a transition requires and what to put in them.
- The **review rule**: how many approvals a MR/PR needs, who can approve (solo: a fresh-agent
  review replaces human approval, and zero approvals are needed).
- The **tester**: who tests in staging (a product owner, a client, the user), and where the test
  procedure and deployment notes go (a ticketing field, a comment, the MR/PR description).

## `priorities.md`

Starts as a copy of `core/priorities.md`; the user edits it. The dev pilot reads only this copy.

## `learnings.md`

`- <date> — <topic> : <finding>` lines, grouped under `## <topic>` headings. A pilot that finds
the table, screen, cause or convention behind a family of tickets adds one line.

When `.ai-factory/` lives inside a repository a ticket changes, a finding is **not** written there:
it would be committed on the ticket's branch and ship in a functional MR/PR. It goes to
`state/learnings-pending.md` (same format, ignored by git), which every skill reads with
`learnings.md`; the user moves its lines into `learnings.md` in a commit of their own (the ship
recap reminds them when it is not empty). Outside a repository, `learnings.md` is written directly.
