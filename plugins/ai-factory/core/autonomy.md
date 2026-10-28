# Autonomy

What a skill does on its own, what goes to the validation queue, what it never does. The profile's
`autonomy.md` may override a row; it can tighten freely, and loosen only rows marked *loosenable*.

## Levels

| Level | Meaning |
|---|---|
| **Free** | Done without asking |
| **Delegated** | Done without waiting, written to the journal |
| **Queue** | Prepared in full and added to the validation queue; executed on the tick after an "OK" |
| **Human** | Only the user can do it; the skill prepares everything and queues it as a task to do |
| **Never** | Neither a pilot nor a skill |

In manual mode, *Queue* means: show the action and wait for the user's answer in the conversation.
In `pilot dry` mode, *Delegated* becomes *Queue*.

## Matrix

| Action | Level | Loosenable |
|---|---|---|
| Read tickets, MRs/PRs, chat, logs; read non-production data | Free | — |
| Write in `.ai-factory/state/`, create a branch, commit locally | Free | — |
| Support: answer a *safe case* and close it | Delegated | — |
| Support: assign oneself an unassigned ticket | Queue | yes |
| Any other public answer or ticket transition | Queue | yes |
| Create a dev ticket from a support ticket, link them | Queue | yes |
| Push a branch, open a MR/PR, answer review threads | Queue | yes |
| Merge into the staging branch | Queue | yes |
| Review a teammate's MR/PR and approve it (team profiles) | Delegated | — |
| Nudge reviewers in chat (at most once per MR/PR per day) | Delegated | — |
| Write to any non-production data | Queue | no |
| Write to production data, run a production script | Human | no |
| Merge or push to a protected branch; connect to production data | Never | no |

## Safe case (support)

A support answer is published without approval only if **all** hold: the ticket is assigned to
the user; the answer promises nothing and asks nobody to act; and it is one of:

- a **figure** computed on non-production data that mirrors production, given with its query and
  the date of the data;
- a **verified finding**: the reported problem no longer exists in data newer than the ticket;
- a **duplicate** of a ticket already done, which the answer cites.

When in doubt, it is not a safe case.

## Earned autonomy

The queue archive records, per action type, how often the user approved without changes. After
**20 consecutive approvals without modification** of one action type, the pilot proposes (once, in
its report) to move that type one level up. Only the user changes the profile's `autonomy.md`.

## The validation queue

See `core/validation-queue.md`.
