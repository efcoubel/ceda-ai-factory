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
- **Title**: the main commit's subject, in the repository's format.
- **Options**: the forge's MR/PR options of the profile (`tools.forge.config`: squash, delete the
  source branch, draft, reviewers, labels).
- **Ticket**: the transition to the "ask for review" status of `workflow.md` and its required
  fields (test procedure, deployment notes, links), in the format each field expects.
- **Announcement**: if a chat tool is configured, the message for the review channel
  (`adapters/chat/<adapter>.md`), one line per MR/PR.

## 3. Checkpoint: the recap

| Repo | Branch | Commits | Push | MR/PR |
|---|---|---|---|---|
| `<repo>` | `<branch>` | one subject per line | `origin <branch>` | `<branch> → <default>` |

Then, below: the review's open "to consider" findings, the test procedure, the deployment notes,
the ticket transition with the value of each field, and the announcement with its channel.

- manual / `chain`: **wait for approval.** It covers exactly this recap. A requested change is
  made, then the recap is shown again.
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
the transition screen). Then the announcement (chat adapter, `post`), and record each announced
MR/PR in `state/pilot/nudges.json` with today's date, so nobody nudges for it again today.

Write `ship.md` (links, values written to the ticket, the announcement link), set `state.md` to
`shipped`. End with the links. What follows: `ticket-6-feedback` when review threads come in, then
`ticket-7-staging` once approved (`workflow.md`, "Review rule"; with zero approvals needed, at
once).
