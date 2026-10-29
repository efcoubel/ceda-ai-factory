# The profile schema

`/ai-factory:onboarding` writes these files under `<project root>/.ai-factory/`. Templates are in
`templates/profile/`. Every skill reads them; only the onboarding (and the user) rewrites them.
`learnings.md` is the exception: pilots append to it.

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
    "forge": { "adapter": "github", "config": {} },
    "chat": { "adapter": "none", "config": {} },
    "database": { "adapter": "firestore", "config": {} },
    "logs": { "adapter": "none", "config": {} },
    "queue": { "adapter": "artifact", "config": { "url": null } }
  },
  "repos": [
    {
      "name": "lima",
      "path": "lima",
      "remote": "git@github.com:<owner>/lima.git",
      "default_branch": "main",
      "staging_branch": null,
      "protected_branches": ["main"],
      "commit_language": "en",
      "commit_format": "conventional",
      "branch_format": "<KEY>-<slug>"
    }
  ],
  "pilots": {
    "support": { "enabled": false },
    "dev": { "enabled": true, "max_in_chain": 3 }
  },
  "autonomy": { "start_mode": "dry" },
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
| `repos[].protected_branches` | branches no skill ever merges into or pushes to; the hook enforces it |
| `autonomy.start_mode` | `dry` (everything queued) or `normal` (delegated actions run) |
| `unattended.auto_plan` | `true`: the pilot approves its own plan for low-risk tickets and works them up to `tested` without waiting (`core/autonomy.md`, "Working while the user is away") |
| `unattended.low_risk` | the criteria a ticket must all meet to be low-risk, taken from the list in `core/autonomy.md`; dropping one makes the rule looser, and only listed criteria are understood |
| `unattended.types`, `max_files` | ticket types and plan size that can be low-risk |
| `unattended.max_ready` | tickets at `tested` waiting for shipping, beyond which nothing new starts |
| `unattended.max_ticks_per_day`, `max_tickets_per_day` | daily caps that bound the cost of a long absence |

## `repos.md`

One `## <repo name>` section per repository:

- **Purpose**: what the repository is for, in business terms, two or three lines.
- **Stack**: language and version, framework, package manager, main libraries.
- **Talks to**: the other repositories or services it calls and is called by.
- **Commands**: install, run locally, unit tests, static analysis, lint, build. Each with where it
  runs (host, container name, emulator) and `unattended: yes` when a pilot can run it with nobody
  around (no device to plug, no login to type, no emulator to start by hand).
- **Conventions**: what a reviewer would flag (from the repo's own rules files and history).

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
  review replaces human approval).

## `priorities.md`

Starts as a copy of `core/priorities.md`; the user edits it. The dev pilot reads only this copy.

## `learnings.md`

`- <date> — <topic> : <finding>` lines, grouped under `## <topic>` headings. A pilot that finds
the table, screen, cause or convention behind a family of tickets adds one line.
