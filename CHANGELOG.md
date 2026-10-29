# Changelog

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
