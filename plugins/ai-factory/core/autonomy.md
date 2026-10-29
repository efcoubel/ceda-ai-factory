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
| Approve one's own plan for a *low-risk* ticket, then code, review and test it locally | Delegated if `unattended.auto_plan` is on, else Queue | yes |
| Approve the plan of any other ticket | Queue | no |
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

## Working while the user is away

Without answers, a pilot would frame tickets, queue their plans, reach its limit and idle. The
profile's `unattended` section (chosen at onboarding) lets it keep going on what is safe to do
alone. Everything it produces stays **local** until the user approves the shipping.

### Low-risk ticket

A ticket is low-risk only if **every** criterion the profile lists in `unattended.low_risk` holds,
checked against the written plan (not guessed):

| Criterion | Holds when |
|---|---|
| `cause_proven` | a bug whose cause is shown in the code (`file:line`) and reproduced or explained |
| `single_repo` | the plan touches one repository |
| `no_data_migration` | no schema change, no data migration, no script on existing data |
| `no_dependency_change` | no dependency added, removed or upgraded |
| `no_public_contract` | no change to an API, an event, a file format or a screen flow another system or user relies on |
| `small` | at most `unattended.max_files` files changed in the plan |
| `type_allowed` | the ticket type is in `unattended.types` (for example `bug`, `task`) |

A low-risk plan is approved by the pilot itself (`state.md`: `planned (auto)`), and the plan is
added to the queue as **information** (`type: plan`, `status: done`) so the user can read it later.
Any doubt on one criterion makes the plan a normal one, queued for approval.

### What the pilot does alone, and where it stops

- Frames, codes, reviews (fresh agent) and tests the low-risk tickets up to `tested`, on their
  own local branches.
- Runs only the checks marked `unattended: yes` in `repos.md`; the others become test steps for
  the user in `test.md`.
- Stops each ticket at shipping: push and MR/PR stay in the queue.
- Stops starting new work when `unattended.max_ready` tickets wait for shipping: more branches
  would only conflict with each other.

### Guards

- **Circuit breaker**: a ticket that fails the same step 3 times in a row gets `blocked:` and is
  left alone; 3 failed ticks in a row, or a doctor check the pilot depends on turning broken, stop
  the pilot until the user restarts it.
- **Daily cap**: at most `unattended.max_ticks_per_day` ticks and `unattended.max_tickets_per_day`
  tickets started per day. A cap set to `null` does not apply; the other caps and the circuit breaker
  still do.
- **Return report**: the first view of the validation page sums up what happened since the user's
  last decision: tickets ready to ship, plans approved by the pilot, tickets blocked and why,
  plans waiting for the user.

## Earned autonomy

The queue archive records, per action type, how often the user approved without changes. After
**20 consecutive approvals without modification** of one action type, the pilot proposes (once, in
its report) to move that type one level up. Only the user changes the profile's `autonomy.md`.

## The validation queue

See `core/validation-queue.md`.
