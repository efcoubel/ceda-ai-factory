---
name: onboarding
description: Sets ai-factory up on a project - discovers the repositories, stacks, conventions, ticketing, forge, chat, data and logs already in reach, asks only what it could not find (context, team, repo purposes, environments, what is forbidden, autonomy), shows a recap to confirm, then writes the project profile in .ai-factory/, creates the validation queue and runs the doctor. Resumable. Use for "/ai-factory:onboarding", "set up ai-factory here", "onboard this project", "configure the pilots", "update the profile".
argument-hint: "[update <section>]"
---

# /ai-factory:onboarding

**Plugin root**: two directories above this skill's base directory. Read
`<plugin root>/core/architecture.md` and `core/profile-schema.md` first.

Write the profile files in English, except free text the user dictates. Everything said to the
user follows the language chosen in step 0.

## 0. Language

Before anything else, settle the language of the conversation. Guess it, in this order: the
`language` setting of Claude Code (`~/.claude/settings.json`, then the project's
`.claude/settings.json`), the language of the user's message if they wrote more than the command,
the system locale (`$LANG`, `$LC_ALL`, or `defaults read -g AppleLanguages` on macOS). Then ask one
question with `AskUserQuestion`, in that guessed language: "Which language should we use?", the
guess first marked "(Recommended)", English second if different, the user can type another.

Use the answer for every message, question and recap from then on, and propose it as
`project.working_language` in block 1 (the language pilots use for plans, answers and ticket
comments); the user may choose a different working language there, for a team that writes tickets
in another language. Save it in `onboarding.answers.language`, so a resumed onboarding does not ask
again.

## 1. Where am I

- From the current directory, look for `.ai-factory/profile.json` upwards (`core/architecture.md`).
  - **Found, complete**: say what it covers and offer to update one section (`update repos`,
    `update tools`, `update environments`, `update workflow`, `update autonomy`) or to start over.
  - **Found, with `"onboarding": {"done": false, …}`**: resume at the recorded phase; with
    `"path": "new-project"`, hand over to `/ai-factory:new-project`, which resumes itself.
  - **Not found**: the project root is the current directory, unless it is inside a git repository
    whose parent holds sibling repositories; then propose the parent. Confirm the root in one
    question before writing anything.
- **No repository yet**: no git repository at the root or up to two levels below, and the folder
  is empty or holds only notes (text, markdown, PDFs, images). Say so, and ask: start a new project
  together (recommended), or point to where the existing repositories are. For a new project,
  invoke `/ai-factory:new-project` with the `Skill` tool, after saving the chosen language in
  `onboarding.answers.language`; this onboarding stops there.
- Keep progress in `.ai-factory/profile.json` → `"onboarding": {"done": false, "phase": "<n>", "answers": {…}}`
  after each phase, so a stop loses nothing.

## 2. Discover, without asking

Gather silently, in parallel where possible. Record what you found and where (file and line), so
the recap can show its evidence.

1. **Repositories**: every git repository at the root or up to two levels below. For each:
   remotes (forge and host), default branch (`git symbolic-ref refs/remotes/origin/HEAD`), branches
   that look protected or for staging (`main`, `master`, `prod`, `production`, `develop`, `staging`,
   `recette`), last 50 commit subjects (language, format, ticket keys and their pattern; keep two
   or three real subjects as examples), branch name pattern of the last 30 branches.
2. **Stack**: manifests (`package.json`, `composer.json`, `pubspec.yaml`, `pyproject.toml`,
   `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`, `Gemfile`, `*.csproj`), language versions,
   frameworks, test and lint tools in dependencies, `Dockerfile*`, `docker-compose*.yml`, CI files
   (`.gitlab-ci.yml`, `.github/workflows/`), `Makefile` targets. From CI and scripts, infer the
   commands to install, test, analyse, lint, build.
3. **Conventions**: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `.editorconfig`, linters'
   config. Note the rules a reviewer would enforce.
4. **Tools in reach**: the MCP connectors available in this session (by their tool names:
   Atlassian, Notion, Linear, GitHub, Slack, Microsoft 365, Sentry, Grafana, Firebase…) and the CLIs
   on the machine (`gh`, `glab`, `docker`, `psql`, `mysql`, `mariadb`, `firebase`, `gcloud`,
   `flutter`, `node`, `php`). Check each adapter's "Detect" section in `<plugin root>/adapters/`.
5. **Data and environments**: env files' variable names (never their values), compose services,
   `~/.my.cnf` section names, `~/.pg_service.conf` service names, `.firebaserc` projects, URLs in
   README files.
6. **Ticketing details**, if a ticketing tool is in reach and the user's identity resolves: the
   projects or databases the user's recent tickets belong to, their types, their statuses and the
   transitions between them.
7. **A backlog kept in files**: markdown, YAML, CSV or spreadsheet files whose lines look like
   tickets or user stories (`US-3.2`, `#12`, `- [ ] …`, headings with an id and a title, a
   `backlog`, `roadmap`, `stories` or `todo` file name). For each, note its path, how many items it
   holds, their id pattern, whether ids are hierarchical (epic `US-3`, story `US-3.2`), and whether
   the same ids already appear in branches, commits or ticket titles in the tool.

Never print secrets, env values or personal data from what you read.

## 3. Ask what is missing

Use the `AskUserQuestion` tool, at most four questions per call, each with your best guess as the
first option marked "(Recommended)" when discovery suggests one. Skip any question discovery
already answered with confidence; confirm it in the recap instead. Ask in this order, one block per
call:

1. **Context**: company, client work, personal or open source; the organization's name if any;
   solo or team (and who, with their handle in each tool); working language.
2. **Repositories**: for each repo, its purpose in business terms (open answer, one call per two or
   three repos), and which repos talk to which. Confirm the inferred stack and commands only where
   discovery was unsure.
3. **Tickets**: which tool and which project/board/database; is there a support queue (requests
   from users) distinct from development work; which statuses mean "new", "in progress", "in
   review", "done"; what is "urgent". **Keys**: if the ids that branches and commits carry are not
   the tool's own (a file backlog's `US-3.2` against GitHub's `#42`), say which ones were found and
   ask where the key lives from now on: at the start of the ticket title (recommended when the
   tool has no custom key field), in a custom field, or the tool's own number for new tickets only.
   This fills `tools.ticketing.config.key` (`adapters/ticketing/contract.md`, "Ticket keys").
   **A backlog in files**, when step 2 found one: migrate it to the tool, keeping its ids as keys
   (recommended), keep the file as the ticketing (`none` adapter pointed at it), or leave it as an
   archive and start fresh in the tool.
4. **Review and chat**: how many approvals a MR/PR needs and who gives them (solo: the fresh-agent
   review stands in, zero approvals); the MR/PR options (squash, delete the branch); which chat
   tool and which channels announce reviews, if any.
5. **Testing and environments**: per repository, how a change reaches testers (`core/staging.md`:
   a staging branch, a release to testers with its build and distribution commands, a deploy to a
   staging environment, or nothing), and whether that runs unattended; who tests and where the
   test procedure goes. Then: which environments exist, their URLs, where non-production data lives and how
   old it is, where logs are; confirm that **production data is never connected to** (not
   negotiable) and which branches are protected.
6. **Pilots and autonomy**: enable the support pilot, the dev pilot, or both; scope of the dev
   pilot (which projects, which are background only); start in `dry` mode (recommended: everything
   waits for approval) or `normal`; validation queue on an artifact page (if available) or a local
   file.
7. **When you are away** (only if the dev pilot is enabled). Explain in two sentences that without
   answers the pilot would stop at the plans, and that local work (branch, code, review, tests)
   never leaves the machine. Then ask:
   - may the pilot approve its own plan for **low-risk** tickets and take them up to `tested`
     (`unattended.auto_plan`; recommended: yes for solo projects, no for team projects until the
     earned-autonomy figures say so);
   - which criteria define low-risk: show the list of `core/autonomy.md` as a multi-select, all
     checked by default, and which ticket types qualify (recommended: bug, task);
   - how many tested tickets may wait for shipping before it stops starting new ones
     (`max_ready`, recommended 5), and the daily caps (`max_ticks_per_day` 30,
     `max_tickets_per_day` 6);
   - for each test command found in step 2, whether it can run with nobody around
     (`unattended: yes/no` in `repos.md`); propose `yes` for unit tests and static analysis, and
     ask for anything that needs a device, an emulator or a login.

Save the answers after each block (step 1, "keep progress").

## 4. Recap and confirm

Write the recap as a single message (or, if the `Artifact` tool exists, offer it as a private
page): one table per profile file, each value with its source ("found in `pubspec.yaml`", "your
answer"). Then the list of what will be written and where, including any change outside
`.ai-factory/`. Ask for a go, or for corrections; apply corrections and show only what changed.

## 5. Migrate a file backlog

Only if the user chose to migrate. Read every item of the file; map each to a ticket: its key
(written where `config.key.source` says), title, type (from its wording or the file's sections),
status (done items are created closed, or skipped if the user prefers), description, parent
(an epic for a hierarchical id). Skip items whose key already exists in the tool (`find_by_key`).
Show the mapping as a tree with counts (to create, already in the tool, skipped), then create the
tickets **as one outward batch** after the user's go, parents first. Add to the file, at its top,
one line saying where its items now live; never delete it.

## 6. Write the profile

From `<plugin root>/templates/profile/`:

- `.ai-factory/profile.json`, `repos.md`, `environments.md`, `workflow.md`, `learnings.md`;
- `.ai-factory/priorities.md`: a copy of `core/priorities.md` with the dev queue and the background
  scope filled in;
- `.ai-factory/state/tickets/` and `.ai-factory/state/pilot/`, and the template `gitignore` as
  `.ai-factory/.gitignore`;
- set `"onboarding": {"done": true, "at": "<ISO date>", "plugin_version": "<plugin.json version>"}`.

Touch nothing outside `.ai-factory/` unless the recap listed it and the user agreed (for example a
short "ai-factory" section in a root `CLAUDE.md` that points to `.ai-factory/`).

## 7. Create the validation queue

- `artifact` adapter: publish `<plugin root>/templates/validation-page.html` as a new private
  artifact titled "<project name> validation", with `capabilities: {db: {rules: [{path: "", read:
  "owner", write: "owner"}]}, user: {}}`; save its URL in `tools.queue.config.url`. Run the check of
  `adapters/queue/artifact.md`.
- `file` adapter: create `state/pilot/queue.md` with its header.

## 8. Check and hand over

Run `/ai-factory:doctor`. Then tell the user, in a few lines:

- what was written, and that the profile can be committed (no secrets) while `state/` is ignored;
- what doctor found broken, with the fix;
- how to start: one ticket by hand with `/ai-factory:ticket <KEY>`, then a pilot in a loop, for
  example `/loop 30m /ai-factory:dev pilot dry`.
