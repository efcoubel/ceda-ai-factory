---
name: review-peers
description: Reviews the teammates' MRs/PRs that still wait for approvals - found on the forge and in the chat's review channel - reads each diff and the changed files in full, publishes only verified findings as Conventional Comments in the project's working language, approves the ones with no blocking finding, and proposes moving the ticket to its approved status when the last approval needed is given. Team profiles only. Use for "/ai-factory:review-peers", "review my teammates' MRs", "do the code reviews", "which PRs should I review".
argument-hint: "[pilot [dry] | pilot approved <queue id>] [<hours>]"
---

# /ai-factory:review-peers

**Plugin root**: two directories above this skill's base directory. Read `core/chain.md` ("Before
anything") and `core/review-rules.md` first.

Only for `project.team: team`: on a solo profile, say there is nobody to review and stop.

Comments are published under the user's name. A wrong or vague one costs them more than a missing
one: publish only what you checked in the code. Beyond comments, this skill only approves and
proposes the ticket's transition; it resolves no thread, changes no MR/PR, posts nothing in chat.

Proposed actions: in `pilot` mode they go to `state/pilot/actions-review-peers.json`,
which the dev tick adds to the queue; alone, to the queue directly (queue adapter, `add`), or
asked in the conversation.

## 1. Collect

From the last 24 hours (or the hours given):

- the forge (adapter, `list_open`): open MRs/PRs of the profile's repositories, not by the user;
- the chat's review channel, if any (adapter, `find_links`): MRs/PRs posted by others. A message
  whose text is cut short is read in full. Several messages about one MR/PR count once, the latest.

Keep for each: its link, author, ticket key (from the title, branch or message), and the message's
link if it came from chat.

## 2. Keep those waiting for a review

Leave out a MR/PR that is not open, already has the approvals `workflow.md` requires ("Review
rule"), was already approved by the user, is the user's own (whoever posted the link), or that the
user already commented with no commit since their last comment (then review only what the new
commits change). A draft is reviewed, and said to be one.

## 3. Review

Never touch the user's working trees. Read through the forge (`diff`, and `file_at` the MR/PR's
head for **every changed file in full**: a call broken by a rename hides outside the changed
lines), or in a local repository without switching branch (`git show <sha>:<path>`,
`git grep … origin/<default>`).

The rules: `core/review-rules.md`, bugs first, then the repository's own rules (`repos.md`,
"Conventions", its `CLAUDE.md`) and `learnings.md`. Read the threads already open: do not repeat
what another reviewer said; with one more argument, answer in their thread. No finding, no
comment: a clean MR/PR is a valid result.

## 4. Write the comments

[Conventional Comments](https://conventionalcomments.org): the label and decoration in English, the
rest in `project.working_language`, addressed to the author the way the team speaks (`workflow.md`
may say "tutoiement", "first names"…).

```
**<label> (<decoration>):** <subject in one sentence>

<two or three sentences: the problem, why it is one, what to do; the evidence in one line>
```

- `(blocking)` for what must change before merging (a bug, a project rule broken), `(non-blocking)`
  otherwise; a `nitpick` is always non-blocking, and said once with every place it applies.
- A finding on lines the MR/PR did not change says so.
- One remark per comment, on its line when it has one (forge adapter, `comment` with file and
  line); a short fix as the forge's suggestion block.
- A `praise` only when something deserves it, never to soften.

## 5. Publish and approve

- `pilot dry`: one `review_comments` action per MR/PR, whose content is every comment with its
  place, and whether it
  will be approved; stop. Called with `pilot approved <id>`, publish exactly that content.
- Otherwise (delegated, `core/autonomy.md`): publish (forge adapter, `comment`, or `reply` in an
  existing thread), then **approve** each MR/PR with no blocking comment from you (`approve`), and
  re-read its approvals.
- When the user's approval is the last one `workflow.md` requires, and every MR/PR of that ticket
  now has its approvals: add a `transition` action to the queue (the "Mark approved" transition of
  `workflow.md`), unless the profile's `autonomy.md` loosened ticket transitions; then do it.

## 6. Report

| MR/PR | Author | Ticket | Approvals | Result | Approval |
|---|---|---|---|---|---|

Every MR/PR of step 1, the ones left out with why ("already 2 approvals", "reviewed, no commit
since"). Then the comments posted, per MR/PR: link, `file:line`, first line. A comment the forge
refused is reported with its error. For chat messages that should get a reaction ("seen"), list
them with their link when the chat adapter cannot react.
