---
name: follow-reviews
description: Follows the user's own MRs/PRs under review - reads approvals and threads on the forge, proposes moving the tickets whose MRs/PRs all have their approvals to the approved status, hands the ones with feedback to the feedback step, and nudges reviewers in the chat's review channel at most once per MR/PR per day. Team profiles only. Use for "/ai-factory:follow-reviews", "where are my MRs", "nudge my reviewers", "check my PRs under review".
argument-hint: "[pilot [dry] | pilot approved <queue id>]"
---

# /ai-factory:follow-reviews

**Plugin root**: two directories above this skill's base directory. Read `core/chain.md` ("Before
anything") first.

Only for `project.team: team`: on a solo profile the fresh-agent review stands in, and there is
nobody to nudge. Say so and stop.

This skill reads, proposes transitions and sends nudges. No comment, no thread resolved, no push.

Proposed actions: in `pilot` mode they go to `state/pilot/actions-follow-reviews.json`,
which the dev tick adds to the queue; alone, to the queue directly (queue adapter, `add`), or
asked in the conversation.

## 1. My MRs/PRs under review

The user's tickets in the "ask for review" status of `workflow.md` (ticketing adapter, `list`), and
the ticket folders at `shipped` or `feedback`. For each, its MRs/PRs: `ship.md` first, else the
forge adapter's `find` on the key; then `state` on each open one (approvals, draft, threads with
their last author).

## 2. Sort

First line that applies:

| Case | Condition | What follows |
|---|---|---|
| Approved | every open MR/PR has the approvals `workflow.md` requires, no thread to handle | step 3 |
| Feedback | a thread whose last message is not the user's | listed: the dev pilot runs `ticket-6-feedback` (alone: propose it) |
| Draft | a MR/PR is a draft | listed |
| No MR/PR | none open | listed |
| Waiting | the rest | step 4 |

## 3. Approved

The "Mark approved" transition of `workflow.md` (ticketing adapter, `statuses` then
`transition`, by target status name): a `transition` action in the queue, unless the profile's
`autonomy.md` loosened ticket transitions; then do it. A required field on its screen stops it:
report it. Add a journal line to the ticket's `state.md` if it has a folder, without changing its
state.

## 4. Nudge

At most **once per MR/PR per day**, whoever sent the previous nudge: the pilot, the user by hand,
or the announcement made at shipping. A MR/PR was already cited today if either says so:

1. `state/pilot/nudges.json` (`{"<MR/PR url>": "<ISO date of the last nudge>"}`);
2. the user's own messages of the day in the review channel (chat adapter, `my_messages_today`,
   full text: extract every MR/PR link).

**If the chat search fails, nudge nothing** and say so: a missed nudge is better than a duplicate.

One message per ticket, one line per MR/PR still missing approvals, in the channel's usual form
(`adapters/chat/<adapter>.md`), in `project.working_language`. `pilot dry`: a `nudge` action per
message instead. After each message sent, record its MRs/PRs in `nudges.json` with
today's date.

## 5. Report

| Ticket | MR/PR | Approvals | Threads to handle / waiting | Action |
|---|---|---|---|---|

"Action" says what was done: "transition queued", "feedback: for the pilot", "nudged", "already
cited at 10:12", "draft", "no MR/PR found". Then the link of each message sent.
