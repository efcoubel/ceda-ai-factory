---
name: ticket
description: Takes one ticket through the whole chain - frame, code, review, test, ship, feedback, staging - running the steps back to back and stopping only at their checkpoints (plan approval, shipping, review answers, staging); resumes a ticket where it stopped. In pilot mode it never asks and queues each checkpoint for approval. Use for "/ai-factory:ticket <KEY>", "do this ticket end to end", "resume the ticket", "take ticket X".
argument-hint: "<KEY> [pilot [approved] [dry]]"
---

# /ai-factory:ticket

**Plugin root**: two directories above this skill's base directory. Read `core/chain.md` first:
profile, key, ticket folder, modes.

You orchestrate; the steps do the work. Invoke each with the `Skill` tool:
`ai-factory:ticket-<n>-<verb>` with `<KEY> chain`, or `<KEY> pilot` (and `dry` if given) when this
skill runs in pilot mode.

## 1. Where the ticket is

From `state.md` (no folder: framing):

| State | Next step |
|---|---|
| absent, `framing` | `ticket-1-frame` |
| `planned`, `planned (auto)` | `ticket-2-code` |
| `coded` | `ticket-3-review` |
| `reviewed` | `ticket-4-test` |
| `tested` | `ticket-5-ship` |
| `shipped` | read the MR/PR state (forge adapter, `state`): a thread to handle → `ticket-6-feedback`; approved per `workflow.md` → `ticket-7-staging`; else stop: it waits for review |
| `feedback` | approved → `ticket-7-staging`; else stop: it waits for review |
| `staging` | read the MR/PR state: merged → the close-out below; else stop: testing, then the merge into the default branch, are the user's |
| `done` | nothing |

Say in one line where you resume from.

**Close-out**, once every MR/PR of the ticket is merged (forge adapter, `state`):

1. Set `state.md` to `done`, with a journal line giving each merge commit and the ticket's status.
   A merge gate still open (its `check` prints something on the default branch, or a condition in
   words not confirmed) or a test not confirmed: add a `human_task` saying so, once, and go on:
   the merge is the user's call and nothing is undone.
2. Propose, as one recap, the outward clean-up: the ticket's transition to the "Done" status of
   `workflow.md` if the forge's automation did not make it, the testing label left on a closed
   ticket, the remote branches the forge did not delete. Done after the user's go
   (`pilot`: a `cleanup` action).
3. Locally, free: remove the ticket's worktrees: first `rm` the links listed in the repository's
   **Worktree** entry (`rm <worktree>/node_modules`, no trailing slash), which `git worktree remove`
   counts as untracked files, then `git worktree remove`, without `--force`. If it still refuses,
   leave the worktree and say what is in it. Switch each repository back to its default branch,
   pull it, and delete the ticket's local branch if `git branch -d` accepts it (merged). Never `-D`.

## 2. Run the steps

After each step, read `state.md` again and go on without asking. Outside `pilot` mode, whenever
the chain stops or a close-out ends, run the dashboard refresh of `skills/dev/SKILL.md`, section 0c,
if `~/.ai-factory/dashboard.json` exists. Stop, saying why, when:

- a step reached its checkpoint (manual or `chain`: it asked the user; `pilot`: it queued);
- `state.md` has a new `blocked:` line;
- `ticket-3-review` still finds blocking issues on its third round;
- the chain reaches `shipped` and `workflow.md` needs approvals: what follows depends on the
  reviewers. With zero approvals needed and no thread open, go on to `ticket-7-staging`: its own
  checkpoint asks before anything reaches testers.

In manual or `chain` mode, once the user answers a checkpoint, resume the chain.

A round of fixes after a review with blocking findings is two invocations, not a shortcut: call
`ticket-2-code` (it handles only those findings), then `ticket-3-review` again with a fresh agent.
The same after `ticket-4-test` committed a fix beyond a few lines. Following the steps' rules from
memory instead skips what they check.

In **pilot mode with `unattended.auto_plan`**, `ticket-1-frame` may approve its own plan for a
low-risk ticket (`planned (auto)`): continue to `ticket-2-code` in the same run, up to `tested`.

## 3. Report

At each stop: the state reached, what was done since the last stop (one line per step), what is
expected from the user (or, in pilot mode, what was queued).
