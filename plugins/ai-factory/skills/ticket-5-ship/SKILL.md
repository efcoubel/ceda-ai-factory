---
name: ticket-5-ship
description: Shipping step of the ai-factory chain - checks the branch is ready, prepares the MR/PR texts, the ticket's review transition and its fields, the test procedure and deployment notes, and the review announcement, shows them as one recap, then after approval pushes, opens the MRs/PRs, updates the ticket and announces the review. Use for "/ai-factory:ticket-5-ship <KEY>", "ship the ticket", "open the MR", "open the pull request", "push the ticket".
argument-hint: "<KEY> [chain | pilot [approved] [dry]]"
---

# /ai-factory:ticket-5-ship

**Plugin root**: two directories above this skill's base directory. Read `core/chain.md` first.

Nothing leaves the machine without approval: no push, no MR/PR, no ticket update, no chat message.

## 1. Check it is ready

Read `state.md`, `plan.md`, `review.md`, `test.md`. Stop, saying why, if:

- `review.md` holds a blocking finding not handled;
- a check in `test.md` is red because of the branch;
- commits came after the last pass of `ticket-3-review` or `ticket-4-test`: run them again first.

For each repository: `git fetch origin <default_branch>`; is the branch up to date with it (report
a foreseeable conflict); `git status --short` clean; no secret, credential or filled `.env` in
`git diff origin/<default>...HEAD`.

## 2. Prepare

- **MR/PR description**, per repository, in markdown, in the repository's language: `## Ticket`
  (link and title), `## Context` (two or three lines), `## Changes` (by intent), `## Related` (the
  sibling MRs/PRs). On a forge that closes tickets from the description (GitHub: `Closes #<n>`),
  add that line when the ticketing tool is the same forge. File: `ship-<repo>.md` in the ticket
  folder.
- **Merge gate**: the conditions of `plan.md`, copied to `ship.md` and stated at the top of the
  description.
- **What else the branch brings**: commits that are not this ticket's (a branch built on another
  ticket's), with their migrations and deployment notes. The notes written here cover all of it.
- **Title**: what the ticket delivers as a whole, in the repository's commit format (often the
  ticket's title, rephrased), not the subject of whichever commit came first.
- **Options**: those of `tools.forge.config.mr_options` the adapter applies at opening (draft,
  reviewers, labels), and apart, the merge-time ones (squash, delete the branch) with what really
  applies them: the MR itself, the repository's settings (read them), or the user when merging
  (`adapters/forge/contract.md`, "MR/PR options"). Never show as done what nothing will do.
- **Ticket**: the transition to the "ask for review" status of `workflow.md` and its required
  fields (test procedure, deployment notes, links), in the format each field expects.
- **Ticket comment**, if `workflow.md` puts the test procedure or the notes in a comment: its
  text, in `ship-comment.md`. They are posted here, at shipping, unless `workflow.md` says another
  moment. A link known only after opening (the MR/PR's) is written as
  `<MR/PR link>` and filled in at sending time.
- **Announcement**: if a chat tool is configured, the message for the review channel
  (`adapters/chat/<adapter>.md`), one line per MR/PR.
- **Outside the ticket**: the commits whose files the plan did not foresee — a tooling or
  configuration fix the work needed, the profile (`.ai-factory/`), another feature. List them with
  their reason; the user may keep them in the MR/PR or move them to their own.

## 3. Checkpoint: the recap

| Repo | Branch | Commits | Push | MR/PR |
|---|---|---|---|---|
| `<repo>` | `<branch>` | one subject per line | `origin <branch>` | `<branch> → <default>` |

Then, below: the commits outside the ticket, the lines waiting in `state/learnings-pending.md` (for
the user to commit on their own, never in this MR/PR), the review's open "to consider" findings, and **the
full text of everything that will be written outside the machine**, exactly as it will be sent: each
MR/PR title and description, the ticket comment, each field value of the transition, the
announcement and its channel. Lines added automatically (an attribution trailer the session
requires, a link) are part of that text and are shown. A summary of a text is not that text.

- manual / `chain`: **wait for approval.** It covers exactly this recap: nothing is sent that it did
  not show, word for word. A requested change is made, then the recap is shown again.
- `pilot`: add a `ship` action to `actions.json` whose content is this recap and everything below
  it, as is; return. Called again with `pilot approved`, go to step 4 without changing anything of
  the approved content.

## 4. Ship

For each repository:

1. `git -C <repo> push -u origin <branch>`. Never `--force`: if the remote branch diverged, stop and
   show it.
2. Open the MR/PR (forge adapter, `open`) with the prepared title, description and options.
3. Once all are open, fill in "Related" in each (forge adapter).

Then the ticket (ticketing adapter: `transition` with its fields, then any field that is not on
the transition screen, then the comment of `ship-comment.md` with its link filled in). Then the announcement (chat adapter, `post`), and record each announced
MR/PR in `state/pilot/nudges.json` with today's date, so nobody nudges for it again today.

Write `ship.md` (links, values written to the ticket, the announcement link), set `state.md` to
`shipped`. End with the links. What follows: `ticket-6-feedback` when review threads come in, then
`ticket-7-staging` once approved (`workflow.md`, "Review rule"; with zero approvals needed, at
once).
