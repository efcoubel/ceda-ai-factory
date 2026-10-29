# Default dev priorities

The onboarding copies this file to `.ai-factory/priorities.md`; the dev pilot reads only that copy.
A tick runs the due appointments (D), then blocks A to C top to bottom until its budget is spent.

## Scope

Edit the query in `workflow.md` ("dev queue") to say which projects, boards or labels the pilot
works on. Tickets the user started by hand (no ticket folder, but already past `new`) are listed,
never taken over.

## A. Unblock, every tick

| # | What | How to recognize it | Skill |
|---|---|---|---|
| 1 | Approved queue actions | queue rows `pilot = dev` in `ok` or `changed` | the step that queued them |
| 2 | Review feedback on my MRs/PRs | a thread whose last message is not mine | `ticket-6-feedback` |
| 3 | Approved MRs/PRs | every MR/PR has its approvals (`workflow.md`), no thread to handle | `ticket-7-staging` |
| 3b | Merged | every MR/PR of a ticket at `staging` (or `shipped` with no staging) is merged | `ticket` (close-out) |

## B. Finish before starting

| # | What | How to recognize it | Skill |
|---|---|---|---|
| 4 | Urgent | linked to a support ticket, or tool priority at or above the profile's "urgent" level | `ticket` |
| 5 | In progress | `state.md` at `planned`, `coded`, `reviewed` or `tested`; most advanced first | `ticket` |

## C. Start, if fewer than `pilots.dev.max_in_chain` tickets are in the chain

A ticket is "in the chain" from framing to `tested`, plans waiting for approval included. A ticket
at `tested` waiting for shipping approval counts against `unattended.max_ready` instead; at that
limit nothing new starts either (`core/autonomy.md`, "Working while the user is away").

With `unattended.auto_plan` on, a low-risk ticket goes past its plan without waiting and continues
to `tested` in the same tick (it counts in the code budget). Other tickets stop at the plan.

| # | What | How to recognize it | Skill |
|---|---|---|---|
| 6 | Bugs | type bug, state `new`, no ticket folder | `ticket`, up to the plan |
| 7 | Tasks | type task or sub-task, same conditions | `ticket`, up to the plan |
| 8 | Features | type feature or story, same conditions | `ticket`, up to the plan |

Equal rank: tool priority, then oldest first. Projects or boards listed as "background" in
`workflow.md` are started only when lines 2 to 8 have nothing at all.

## D. Appointments, outside the ranking

| What | Skill | When |
|---|---|---|
| Review teammates' MRs/PRs | `review-peers` | 09:00 and 14:00 |
| Follow my MRs/PRs, nudge reviewers | `follow-reviews` | every 2 hours |

Block D runs only when `project.team` is `team`: on a solo profile there is nobody to review or
nudge, and the fresh-agent review of the chain stands in.

The pilot has no clock: a slot is **due** when the tick time is past the slot and the last run in
`state/pilot/cadences.json` is earlier. A due slot runs once on the next tick, even if several were
missed. No slot on Saturday or Sunday.

## Rules

- A ticket with a pending queue action waits for the user.
- A ticket whose `state.md` has a `blocked:` line waits until something changes on it.
- Budget: at most 2 tickets writing code and 4 tickets in all per tick, plus due appointments.
