# Changelog

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
