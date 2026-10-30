# Changelog

## 0.3.6

- Dashboard banner: much smaller type, it no longer takes over the page.

## 0.3.5

From 76 real actions on three projects, and one approval given to a plan whose open question the
user never saw.

- Validation page rewritten: one reading column grouped by ticket, the question first, the detail on
  request and rendered instead of shown as raw text in a small scrolling box. The page speaks the
  working language, in English or French.
- Actions gain a layer written for the reader, apart from what the pilot runs: `summary` becomes the
  question asked, plus `why`, `effects`, `watch`, `ticket_title` and `ticket_url`. The rules are in
  `core/validation-queue.md`, "Written for the reader".
- Questions are answered on the card, one by one: `questions` carries the proposed answer and the
  options. Approval stays closed while a question needs an answer; an option goes with the approval,
  a free answer goes back to the pilot.
- A row that comes back shows the pilot's `reply` first. Before, a refused approval was stored in a
  note the page hid on pending rows.
- Approved rows stay visible with what they wait for, and an approval can be taken back. Before,
  they disappeared from the page until they were carried out.
- Status changes, assignments and clean-ups are grouped as routine steps with one button; a refusal
  asks for confirmation and takes a reason.
- A card being read or answered is no longer rebuilt when the queue changes elsewhere.
- `/ai-factory:onboarding update page` publishes the new page over an old one; the dev pilot and the
  doctor say when it is due (`tools.queue.config.page_version`).

## 0.3.4

- Dashboard banner for a screen left open: across all projects, in large type, what waits for
  validation and what is blocked, red until it is cleared, with a link to each validation page; one
  line per project says when the last tick finished, or that the pilot stopped or went silent.
- The dev tick records `last_tick_at` and always refreshes the page last, waiting for a refresh
  still running.

## 0.3.3

- Dashboard: a tick stopped by its cap, the circuit breaker or the doctor still refreshes the page;
  the `/ai-factory:ticket` chain refreshes it when it stops, outside pilot mode; the background
  agent gets a standalone prompt and leaves its error for the next report; a missing dashboard
  address is reported instead of skipped silently.

## 0.3.2

From nine real ticks on a solo Symfony site.

- Dashboard data: journal variants are read, unreadable lines and future dates become `journal`
  warnings in Health instead of a silently empty page; a block is a line starting with `blocked:`.
- Clock and format: every date comes from `date`, an exact journal example, and a doctor check.
- Queue: `requires` to order actions, absolute paths, `rewritten_at` so a rewritten row is notified
  again, and the queue as the only source of status (`actions.json` is emptied once queued).
- Open questions: each carries a proposed answer an `ok` accepts; a pilot never answers in the
  user's place.
- Merge gates in `plan.md`, stated in the MR/PR and checked at close-out; a `human_task` confirms
  the test on staging; a merge with either open raises a `human_task`, and undoes nothing.
- Staging: tests run on the merged tree before the push; what else a merge brings is listed, with
  its migrations and deployment notes.
- Tickets with no key or type are raised once in the queue; `key.fallback: native`.
- A profile older than the plugin is raised once; `onboarding update priorities` merges new lines.
- Close-out: Done transition, worktrees removed.
- Dashboard cost: the pilot refreshes at the start and the end of a tick, only when a dataset
  changed, in a small background agent that reads no tool; nothing changed costs nothing.
- Hook: heredoc bodies are data unless fed to a shell.
- Test: a worktree is not the local site; the step is run from the worktree or said not played.
- Dashboard wording: no plural to get wrong, lead time named after what it measures.

## 0.3.1

- The dev pilot refreshes the dashboard first, at every tick, in a background agent, instead of
  at the end and at most hourly: the dashboard shows the state the tick starts from without
  delaying the tickets.
- The dashboard uploads only the datasets that changed (hashes in `~/.ai-factory/dashboard.json`),
  writes all its documents in one batch, reads the projects' tools in parallel, and takes a lock
  so two refreshes never overlap. Called by the pilot, it asks nothing and never rewrites a page.

## 0.3.0

- The dev pilot, `dev`: one tick, made for `/loop 30m /ai-factory:dev`. It carries out the
  approved queue actions, runs the team appointments, then moves tickets forward in the order of
  `priorities.md` (feedback, staging, close-out of merged tickets, urgent, in progress, new bugs,
  tasks, features) by running the chain in pilot mode in agents, within its budget, the chain and
  ready limits and the daily caps. Guards: a lock, the doctor's report, the circuit breaker.
- Notifications: one per tick when something new waits (pending actions, a task for the user, a
  new block, the breaker), never twice for the same thing; pushed to the phone when Remote Control
  is connected. `pilots.dev.notify`, on by default.
- Quiet hours (`pilots.dev.quiet_hours`), off unless turned on by hand: only approved actions run.
- `review-peers` and `follow-reviews`, for team profiles only (`project.team`): review teammates'
  MRs/PRs in Conventional Comments in the working language and approve the clean ones; follow
  one's own, propose the approved transition, nudge reviewers at most once per MR/PR per day.
- Forge contract: `list_open`, `diff`, `file_at`, `comment` (GitHub and GitLab).
- The dashboard is refreshed by the pilot at most once an hour.

## 0.2.3

- New `dashboard` skill: one claude.ai Dashboard page, one tab per project registered on the
  machine, in the language of the onboarding. On top, the chain as a flow of steps (to do, framing,
  development, ready to ship, review, test, done) with a count per step and the blocked ones; pick
  a step to list its tickets. Then what waits for the user (pending actions, blocked tickets), open
  MRs/PRs, every ticket with its review rounds and lead time,
  health (doctor and pending learnings) and a daily trend.
- `scripts/dashboard-data.py` builds its datasets from local files only and keeps one snapshot per
  project and day in `~/.ai-factory/history/`; the onboarding registers each project in
  `~/.ai-factory/projects.json`.

## 0.2.2

From the second ticket run, shipped, staged and merged.

- A second hook blocks deploy and cloud commands (`firebase`, `gcloud`, `gsutil`, `kubectl`,
  `fly`, `vercel`, `aws`…) that name a production target: `production_targets`, the database's
  production projects and the `.firebaserc` aliases pointing to them; a `firebase` write without
  `--project` is blocked too. Read commands (logs, list, describe) stay allowed. The onboarding
  writes in `environments.md` exactly what the hooks guard.
- MR/PR options: `draft`, `reviewers`, `labels` applied at opening (GitHub and GitLab); `squash`
  and `delete_branch` are merge-time, shown with what really applies them (GitLab: the MR; GitHub:
  the repository's settings, checked by the adapter). The ship recap never promises an option
  nothing applies.
- Review: "blocking" now includes a criterion not proven, a contradiction with the plan and a
  user-facing rule broken; the severity is decided when sorting, and each change is recorded and
  reported.
- Chain: a `done` state and a close-out once the MR/PR is merged (local branch cleaned, outward
  clean-up proposed); with zero approvals needed, `shipped` goes on to staging, whose checkpoint
  asks.
- Staging lists what the command really deploys, and writes in the ticket only in the form
  `workflow.md` states.
- Doctor: the production hook is tested on each target; a commit convention in the README that
  contradicts the profile is reported.
- Test: `test-data.md` is written for seed accounts too; more Flutter web tips (modal sheets,
  physical pixels, the Auth emulator banner).

## 0.2.1

From the first ticket run end to end on a real project.

- Frame: the plan and every write that follows its approval (branches, assignment, transition)
  are shown in the conversation; answering the plan's questions is not approving it.
- Ship: the recap shows, word for word, everything that will leave the machine, automatic lines
  included; commits outside the ticket are listed apart; the MR/PR title describes the whole
  ticket; the ticket comment is a file of the ticket folder.
- Chain: a round of fixes invokes `ticket-2-code` then `ticket-3-review` again; long commands are
  announced, bounded without `timeout` (absent on macOS) and never left waiting on a prompt.
- Code: the formatter runs only where the repository follows it; a fix outside the ticket is
  asked for and committed on its own.
- Doctor: check 10b starts each unattended command that starts services, to catch prompts and
  busy ports.
- Firestore: `scripts/firestore-read.mjs`, which refuses production projects; pitfalls on
  parameters missing from `.env.local`, `setGlobalOptions` and the Auth emulator banner.
- Ticket keys: `legacy` key rules recognized when reading, epics carried by a label; a complete
  GitHub Project transition example.
- Staging: a list of entries per repository (deploy the backend, then release the app).
- Ticket folder: journal times from the clock; no file outside the listed ones; findings go to
  `state/learnings-pending.md` when the profile lives in a repository the ticket changes.
- Test: tips for Flutter web and two users in one browser, the build the tester needs in the first
  step, seed accounts in `test-data.md`.
- Onboarding: the language is kept in `onboarding.language` and never asked again; the profile's
  prose can be in the user's language; the formatter is checked during discovery.

## 0.2.0

- The ticket chain: `ticket` and `ticket-1-frame` to `ticket-7-staging`, with manual, chain, pilot
  and dry modes, checkpoints queued in pilot mode, low-risk plans approved by the pilot in
  unattended mode, a circuit breaker, and worktrees when the user's working tree is dirty.
- `core/chain.md` (rules every step follows), `core/review-rules.md`, `core/staging.md`.
- Staging per repository: a branch, a release to testers, a deploy, or none (`repos[].staging`
  replaces `staging_branch`); the onboarding asks how changes reach testers.
- MR/PR options in the forge config; the tester and where the test procedure goes in `workflow.md`.

## 0.1.3

- Ticket keys that are not the tool's own (`config.key`: native, title prefix or field, with a
  pattern and a numbering for new tickets); `find_by_key` and `next_key` in every adapter; doctor
  checks a branch's key leads to one ticket.
- The onboarding finds a backlog kept in files and offers to migrate it, keeping its ids.
- Commit format in the repository's own words, with real examples to imitate.
- GitHub Issues: statuses read and written in a GitHub Project's status field.
- Firestore: access through the Firebase CLI and an Admin SDK script, emulator project and seed.
- A daily cap set to `null` means no cap.

## 0.1.2

- New `new-project` skill: framing (light or full), stack choice, repositories from the official
  generator, remote, branch protection, CI, ticketing setup, backlog of epics and sub-issues,
  profile. The onboarding hands over to it when the folder holds no repository.
- Ticketing contract: `create` with a parent, `setup`. Forge contract: `create_repo`,
  `protect_branch`.

## 0.1.1

- Onboarding asks the conversation language first.

## 0.1.0

- Onboarding and doctor skills.
- Adapter contracts for ticketing, forge, chat, database, logs and the validation queue.
- Protected-branch hook, read-only MySQL client, CSV export, private-term leak check.
- Validation page template.
- Onboarding asks the conversation language first (guessed from Claude Code settings, then the system locale).
- Unattended mode: low-risk tickets approved by the pilot and worked up to `tested`, ready-to-ship limit, circuit breaker, daily caps; asked during onboarding.
