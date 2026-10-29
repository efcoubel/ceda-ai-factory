---
name: doctor
description: Checks that every access an ai-factory profile relies on works right now - ticketing, forge, chat, data per environment, logs, validation queue, protected-branch hook, CLIs, token and certificate expiry - and reports each as OK, warning or broken with the fix. Read-only. Use for "/ai-factory:doctor", "check the setup", "why does the pilot fail", "is everything connected".
---

# /ai-factory:doctor

**Plugin root**: two directories above this skill's base directory.

Read-only: doctor writes nothing except `.ai-factory/state/pilot/doctor.json` (the last report).
Find the profile as in `core/architecture.md`; none found: suggest `/ai-factory:onboarding`.

## Checks

Run them in parallel where independent. For each tool in `profile.json` → `tools`, follow the
**Check** section of its adapter file in `<plugin root>/adapters/<category>/<adapter>.md`.

| # | Check | Broken when |
|---|---|---|
| 1 | Profile | `profile.json` missing a required field, an adapter file that does not exist, `onboarding.done` false |
| 2 | Repositories | a `repos[].path` missing, not a git repo, or its `remote` differs from `git remote get-url origin` |
| 3 | Ticketing | the adapter's check fails, or the dev queue query returns an error |
| 3b | Ticket keys | the key of the current branch, or of the last commit carrying one (matched with `config.key.pattern`), does not lead to exactly one ticket through `find_by_key`; or `next_key` cannot compute a next key |
| 4 | Forge | not authenticated, or a repo not reachable |
| 5 | Chat | a configured channel not found |
| 6 | Data | per non-production environment: the adapter's check fails; **and** a production environment is configured as reachable (that is broken, not a warning) |
| 7 | Logs | the adapter's check fails |
| 8 | Queue | the adapter's check fails; for an artifact, a `view`-level read returns rows |
| 9 | Hooks | the protected-branch hook does not block a dry `git push origin <protected>`, or the production hook does not block a dry deploy naming each of `production_targets` (`firebase deploy --project <target>`, `gcloud run deploy --project <target>`). Test them by feeding the hook scripts a command, never by running it |
| 9b | Conventions | a commit convention written in `README.md`, `CONTRIBUTING.md` or `CLAUDE.md` differs from `repos[].commit_format` and the recent history: a warning, so the user settles which one counts |
| 10 | CLIs and runtimes | a command used in `repos.md` (test, analyse, lint) is not on the machine or its container is not running |
| 10b | Unattended commands | a command marked `unattended: yes` that starts services (emulators, a local server, an end-to-end run) does not start and stop on its own: run it once with its input closed, its non-interactive flag and a short time limit (an emulator with `true` as its script); broken if it asks a question, cannot bind its ports, or does not return |
| 11 | Expiry | a token whose expiry is known expires within 30 days; a server certificate (TLS) used by a data or log access is expired or misnamed |

Warnings, not failures: a category set to `none`, an adapter still marked `draft`, a pending queue
action older than 7 days.

## Report

A table `# | Check | Status | Detail | Fix`, statuses ✅ ⚠️ ❌, broken first. A fix is a concrete
step ("run `gh auth login`", "renew the certificate of <host>; until then …"), never a workaround
that weakens security (disabling TLS verification, widening permissions): those are for the user to
decide, and doctor says so.

Write the same as JSON in `state/pilot/doctor.json` (`{"at", "checks": [{"id", "status", "detail", "fix"}]}`)
so pilots can refuse to run when a check they depend on is broken.
