# ai-factory architecture

ai-factory is an **engine** (this plugin, the same for every project) driven by a **profile** (one
per project, written by `/ai-factory:onboarding`). The engine never names a company, a repository,
a ticket key or a channel: everything project-specific lives in the profile.

## The three layers

| Layer | Where | What |
|---|---|---|
| Engine | this plugin | Skills, the autonomy rules, the ticket folder, the validation queue, the default priorities |
| Adapters | `adapters/<category>/<tool>.md` | How to do each contract operation with one tool (Jira, Notion, GitHub, Slack, PostgreSQL…) |
| Profile | `<project root>/.ai-factory/` | Which tools, which repos, which environments, which workflow statuses, which priorities, what was learned |

A skill reads the profile, picks the adapter the profile names for each category, and follows that
adapter's recipe for the contract operation it needs. A missing category (no chat, no database)
uses the `none` adapter: the operation is skipped and said so.

## Finding the profile

From the current directory, walk up until a directory contains `.ai-factory/profile.json`: that
directory is the **project root**. No profile found: stop and suggest `/ai-factory:onboarding`.
Several profiles can coexist on one machine, one per project root.

## The profile folder

```
<project root>/.ai-factory/
  profile.json        machine-readable core (tools, repos, branches, language, pilots)
  repos.md            one section per repository: purpose, stack, commands, conventions
  environments.md     environments, URLs, data access, logs, what is forbidden
  workflow.md         ticket statuses mapped to the engine's states, queues, transitions
  priorities.md       the dev pilot's order (copied from core/priorities.md, then edited)
  autonomy.md         overrides of core/autonomy.md (optional)
  learnings.md        what the pilots learned about this project, one line per finding
  state/              runtime state, never committed: tickets/, pilot/ (journal, cadences, queue)
```

`profile.json`, the `.md` files and `learnings.md` can be committed and shared with a team: they hold
**no secret**, only references to where secrets live (an env var name, a `~/.my.cnf` section, a
vault path). `state/` is git-ignored.

## The engine's ticket states

Every ticketing tool has its own status names; `workflow.md` maps them to these:

| State | Meaning |
|---|---|
| `new` | Not started by anyone |
| `in_progress` | Someone (or a pilot) is working on it |
| `in_review` | A merge/pull request is open and awaits review |
| `approved` | Every MR/PR has its approvals |
| `in_staging` | Merged into the staging branch or released to testers |
| `waiting` | Waiting for the requester, a third party or a decision |
| `done` | Released or closed |

## Skills

| Skill | Role | Status |
|---|---|---|
| `onboarding` | Discover the project, ask what is missing, write the profile | v0.1 |
| `doctor` | Check every access the profile relies on | v0.1 |
| `new-project` | Start a project from an empty folder: framing, stack, repositories, ticketing, backlog, profile | v0.1.2 |
| `ticket` and `ticket-1-frame` … `ticket-7-staging` | The development chain for one ticket | planned |
| `support` and `support-*` | The support pilot (N1): triage, answer, export, fix data, import, escalate | planned |
| `dev` | The development pilot (N2): runs the chain in priority order | planned |
| `review-peers`, `follow-reviews` | Review teammates' MRs/PRs; follow and nudge one's own | planned, team profiles only |

Skills are invoked with the plugin prefix: `/ai-factory:onboarding`.

## Modes

Every pilot and every chain step accepts the same modes:

- **manual** (default): stops at its checkpoints and asks in the conversation;
- `chain`: called by `/ai-factory:ticket`, runs until the next checkpoint;
- `pilot`: never asks; what needs approval goes to the validation queue;
- `pilot dry`: like `pilot`, but even delegated actions go to the queue.
