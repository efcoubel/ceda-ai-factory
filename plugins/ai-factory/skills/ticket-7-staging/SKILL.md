---
name: ticket-7-staging
description: Last step of the ai-factory chain - once the MRs/PRs are approved and no thread is left, puts the change in front of testers the way each repository does it (merge into a staging branch, a release to testers, a deploy to a staging environment, or nothing), after approval; then hands the user the merge into the default branch. Use for "/ai-factory:ticket-7-staging <KEY>", "send it to staging", "release to testers", "deploy to staging", "merge into staging".
argument-hint: "<KEY> [chain | pilot [approved] [dry]]"
---

# /ai-factory:ticket-7-staging

**Plugin root**: two directories above this skill's base directory. Read `core/chain.md` and
`core/staging.md` first.

## 1. Check it is ready

Read `state.md` and `ship.md`. For each MR/PR (forge adapter, `state`): the approvals required by
`workflow.md` ("Review rule"; zero on a solo project, where the fresh-agent review stood in), no
thread left to handle, no draft. Not ready: stop and say what is missing.

## 2. Prepare, per repository

From `repos[].staging` (one entry, or each entry of a list in order):

- `branch`: `git fetch origin <staging branch> <branch>`, then
  `git merge-tree --write-tree origin/<staging branch> origin/<branch>` to detect a conflict without
  touching anything. List what the merge brings besides this ticket, with its migrations and
  deployment notes;
- `release` / `deploy`: the exact `build` and `how` commands, the target, and a check that the
  target is not production. List **what the command deploys**, not only what the branch changed:
  `firebase deploy --only firestore` sends the rules and the indexes, `--only functions` every
  function of the codebase (unchanged ones are skipped). Each item says whether the branch changed
  it. If no item is something the branch changed, testers would get nothing of this ticket: the
  checkpoint opens with that (in pilot mode, `watch`), and with the entry `repos[].staging` lacks;
- `none`: nothing to do; skip to step 4.

## 3. Checkpoint

| Repo | Branch | Approvals | Open threads | Staging |
|---|---|---|---|---|
| `<repo>` | `<branch>` | `<names or "solo review">` | `0` | `<branch> → <staging branch>` / `release to <target>` / `deploy to <target>`, or "conflict" |

- manual / `chain`: **wait for approval**;
- `pilot`: add a `merge_staging` action to `actions.json` with this table and the exact commands
  as `content`, `summary`, `why` and `effects` as `core/validation-queue.md`, "Written for the
  reader", says, `effects` naming who will see it; a step marked `unattended: false` becomes a
  `human_task` with those commands instead. Return.
  Called again with `pilot approved`, go to step 4.

## 4. Stage

- `branch`: in a temporary worktree on `origin/<staging branch>` (never in the user's working
  tree): `git merge --no-ff origin/<branch>`; **run the repository's unit tests and static analysis
  on the merged tree** (`repos.md`, commands marked `unattended: yes`): each branch passed alone,
  the combination did not yet. A failure stops here, nothing pushed, `blocked:`. Then push to
  `<staging branch>` and remove the worktree. A
  conflict stops everything for that repository: show it, do not resolve it without approval.
- `release` / `deploy`: run `build` then `how` on the ticket's branch; keep the output's link or
  build number.
- Move the ticket to the testing status of `workflow.md` if there is one, and write what
  `workflow.md` asks for at that point (a label, a comment) in the form it states (part of the
  approved action). A form it does not state is asked, not guessed.

Set `state.md` to `staging`, write what was done in `ship.md`. Add a `human_task` "Confirm the
test on staging" with the tester's procedure: when the user ticks it, `ship.md` records the
confirmation. A chain that goes on through several tickets does not take a merged staging for a
tested one.

The merge into the **default branch** stays with the user: the hook blocks it. Give them the
command, or the MR/PR link to merge from the forge, with the merge gate and whether the test was
confirmed.
