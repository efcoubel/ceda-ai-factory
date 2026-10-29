# The ticket chain: rules every step follows

```
1-frame ──▶ 2-code ──▶ 3-review ──▶ 4-test ──▶ 5-ship ──▶ (review) ──▶ 6-feedback ──▶ 7-staging
 ▲ plan       ▲           │                    ▲ ship                  ▲ answers      ▲ staging
              └─blocking──┘ (3 rounds max)
```

▲ marks a checkpoint: the step asks for approval (manual), stops the chain (`chain`), or queues
the action (`pilot`).

## Before anything

1. **Profile**: find `.ai-factory/profile.json` (`core/architecture.md`). None: stop and suggest
   `/ai-factory:onboarding`. Read `profile.json`, `repos.md`, `workflow.md`, and the lines of
   `learnings.md` and `state/learnings-pending.md` about the repositories involved.
2. **Doctor**: if `state/pilot/doctor.json` reports broken a check this step needs (ticketing,
   forge, the repository's commands), stop and say so.
3. **Key**: the argument; else the key found in the current branch name with
   `tools.ticketing.config.key.pattern` (or the tool's native key pattern). Resolve the ticket with
   the ticketing adapter (`find_by_key`).
4. **Ticket folder**: `.ai-factory/state/tickets/<KEY>/` (`core/ticket-folder.md`). Read `state.md`
   and every earlier step's file. A decision recorded there is not re-litigated.
5. **Language**: talk to the user, and write plans, test procedures and ticket comments, in
   `project.working_language`; write code, commits and MR/PR texts in the repository's
   `commit_language`.

## Arguments and modes

`<KEY> [chain | pilot [approved] [dry]]`

| Mode | At a checkpoint |
|---|---|
| none (manual) | Show what would be done and wait for the user's answer in the conversation |
| `chain` | Same as manual: the user is in the conversation; `ticket` resumes after the answer |
| `pilot` | Write the action in `actions.json` (`core/validation-queue.md`), update `state.md`, return. Never ask |
| `pilot approved` | The queued action was approved: do exactly what it said, then continue |
| `pilot dry` | Like `pilot`; delegated actions are queued too (`core/autonomy.md`) |

What a step cannot settle alone (dirty working tree, conflict, scope change, a check that cannot
run, a ticket taken by someone else) is written in `state.md` as `blocked: <reason>`; in manual mode
it is asked instead.

## Working in the repositories

- **Never touch the user's uncommitted work.** A dirty working tree in a repository the ticket
  needs: in manual mode show `git status --short` and ask; in pilot mode, work in a worktree of
  that repository under `.ai-factory/state/worktrees/<KEY>/<repo>` if the repository's commands can
  run there (`repos.md`), else `blocked:`.
- Branches start from a freshly fetched `origin/<default_branch>`, never from local HEAD or the
  staging branch, with `--no-track` (a bare `git push` must not target the default branch).
- Commits are local and free. Push only in `ticket-5-ship` and `ticket-6-feedback`, after approval.
  Never `--force`; `--force-with-lease` only when `ticket-6-feedback` rewrote the branch after
  approval of exactly that.
- Commands come from `repos.md`: run each where it says (host, container, emulator). In pilot mode,
  run only those marked `unattended: yes`; the others become steps for the user in `test.md`.
- A repository's own rules (`CLAUDE.md`, linters, "Conventions" in `repos.md`) win over anything
  general in these steps.

## Long commands

Emulators, end-to-end tests, builds: a command that may take more than a minute.

- **Announce it** before starting: what it runs and how long it should take (`repos.md`, "takes";
  otherwise your estimate). The user who sees nothing for ten minutes cannot tell a slow run from a
  stuck one.
- **Bound it** with the session's own command timeout or a background run checked later, never
  with the `timeout` command: macOS does not have it (`gtimeout` only with coreutils installed).
- **Never let it wait for an answer.** Close its input (`< /dev/null`) and use the tool's
  non-interactive flag. Output that ends on a question (`? Enter …`, `[y/N]`, `Password:`) means
  the command is stuck: stop it, find what it asks for (a missing variable, a login, a choice),
  and fix that cause instead of running it again. Note the cause in the learnings (`core/ticket-folder.md`).
- A command that failed is not run again unchanged: read the error first.

## The circuit breaker

Each step records its attempts in `state.md`. A step that fails three times in a row on the same
ticket writes `blocked: <step> failed 3 times — <last error>` and stops; only the user lifts it.
