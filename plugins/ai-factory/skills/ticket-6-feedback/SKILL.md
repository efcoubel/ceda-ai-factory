---
name: ticket-6-feedback
description: Step of the ai-factory chain that handles review feedback on a ticket's MRs/PRs - collects every open thread, checks each remark against the code, applies what is right, argues what is not with evidence, re-runs review and tests on the change, then after approval pushes, answers each thread and resolves the applied ones. Use for "/ai-factory:ticket-6-feedback <KEY>", "handle the review comments", "I got feedback on the MR", or when a MR/PR link is pasted.
argument-hint: "<KEY or MR/PR url> [chain | pilot [approved] [dry]]"
---

# /ai-factory:ticket-6-feedback

**Plugin root**: two directories above this skill's base directory. Read `core/chain.md` first.

A review remark is a hypothesis to check, not an order: the reviewer reads a diff out of context.
Apply what is right, argue what is not, with evidence.

## 1. Find the MRs/PRs

- From a URL: the repository is the one whose remote matches; the key comes from the source branch.
- From a key: `ship.md` lists them; otherwise the forge adapter's `find`.
- Each repository must be on its MR/PR's source branch (`core/chain.md`, "Working in the
  repositories"). `git fetch origin <branch>`: a reviewer may have pushed a suggestion commit.

## 2. Collect and examine the threads

Every thread of every MR/PR of the ticket, with all replies (forge adapter, `state`): a second
reviewer often qualifies the first. Line numbers date from the comment: find the place by content.

Sort each unresolved thread whose last message is not the user's:

| Category | Meaning |
|---|---|
| Apply | The remark is right |
| Apply differently | The intent is right, the proposed solution has a side effect |
| Do not apply | Checked: the premise is wrong, or the change would break something else |
| Question | The reviewer asks for information, not a change |

Check instead of assuming: a remark that changes an error behaviour means reading every caller;
"don't we already have a tool for this?" means looking for the tool.

## 3. Apply

Apply "Apply" and "Apply differently" right away: it is local work. Minimal changes: every extra
line touched is one more to review. Local commits, one per remark or coherent group, in the
repository's format. Then `ticket-3-review` on the delta and `ticket-4-test` (checks). Record all in
`feedback.md`.

## 4. Checkpoint

- the table `# | MR/PR | File:line | Remark | Category | What was done | Resolve`;
- for each thread, the proposed answer: short, in the language the reviewer wrote in, with the
  evidence for a remark not applied;
- the push of the new commits.

"Resolve" is "yes" for "Apply" and "Apply differently", "no" for a "Question" or a "Do not apply":
the reviewer must be able to answer before the thread closes.

- manual / `chain`: **wait for approval**;
- `pilot`: add a `review_answers` action to `actions.json` with the table, every answer and the
  push as `content`, `summary`, `why` and `effects` as `core/validation-queue.md`, "Written for the
  reader", says; return. Called again with `pilot approved`, carry it out below.

After approval: push each branch, answer each thread (forge adapter, `reply`), resolve the ones
marked "yes" (`resolve`) and check they are resolved. Set `state.md` to `feedback`. If the MRs/PRs
are approved, propose `ticket-7-staging`.
