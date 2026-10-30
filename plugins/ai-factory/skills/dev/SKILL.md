---
name: dev
description: The development pilot of ai-factory - one tick that carries out what the user approved in the validation queue, runs the due team appointments (reviewing teammates' MRs/PRs, following one's own), then moves tickets forward in the order of the profile's priorities (review feedback, staging, close-out, urgent, in progress, new bugs, tasks, features) by running the ticket chain in pilot mode, each checkpoint going to the validation queue; it notifies the user when something new waits for them. Never asks. Made for /loop. Use for "/ai-factory:dev", "run a dev tick", "move my tickets forward", "/loop 30m /ai-factory:dev".
argument-hint: "[dry | normal] [<KEY>]"
---

# /ai-factory:dev

**Plugin root**: two directories above this skill's base directory. Read `core/architecture.md`,
`core/autonomy.md`, `core/validation-queue.md`, `core/chain.md` and the profile's `priorities.md`
first.

A tick moves each ticket to its next checkpoint, writes what it did, and stops. It never asks a
question: what needs the user goes to the validation queue. Run it in a loop:

```
/loop 30m /ai-factory:dev
```

Arguments: `dry` queues even the delegated actions (`core/autonomy.md`); `normal` runs them; with
neither, `autonomy.start_mode` decides. A key limits the tick to that ticket.

State, in `.ai-factory/state/pilot/`: `dev.json` (counters and the circuit breaker),
`cadences.json` (last run of each appointment and daily job), `journal.md`, `notified.json`.

## 0. May the tick run

Stop at the first that holds, with one line saying why (and nothing in the journal but that line).
A tick stopped by 2, 4 or 5 still runs the dashboard refresh of section 0c first: the page must not
freeze because the pilot paused.

1. No profile, or `pilots.dev.enabled` is not true.
2. `dev.json` has `stopped` (the circuit breaker tripped): repeat its reason; only the user clears
   it, by removing the field.
3. Another tick is running: `dev.lock` exists and is less than two hours old. Otherwise write it
   with the current time; remove it at the end, whatever happens.
4. The daily cap `unattended.max_ticks_per_day` is reached (`dev.json` → `ticks_today`).
5. `doctor.json` is older than 24 hours: run `/ai-factory:doctor` first. A check the pilot depends on
   (ticketing, forge, queue, the repositories' commands) is broken: stop, and add a `human_task`
   to the queue with the doctor's fix (once: not if the same task is already pending).

**Quiet hours** (`pilots.dev.quiet_hours`, off unless the user turned it on): inside the window,
the tick only carries out approved actions (section 1) and stops. Nothing new starts, nothing is
posted in chat.

## 0b. Is the profile up to date

`onboarding.plugin_version` older than the plugin's version, and `priorities.md` lacking lines of
`core/priorities.md`: add one `human_task` proposing `/ai-factory:onboarding update priorities`
(once per plugin version). The tick goes on with the profile's copy.

## 0c. Dashboard first

If `~/.ai-factory/dashboard.json` exists, before touching any ticket, quiet hours included, run
the **dashboard refresh** below. It runs again at the end of the tick, so the page shows both the
user's latest decisions and the tick's work. If it does not exist, nothing is refreshed: say so in
the report, with `/ai-factory:dashboard` as the fix.

1. Write this project's `dashboard-queue.json` (`skills/dashboard/SKILL.md`, step 2) from the rows
   of the queue; the tick needs them anyway.
2. `python3 <plugin root>/scripts/dashboard-data.py --out .ai-factory/state/pilot/dashboard-out --changed`.
3. It prints nothing: stop, no agent, no cost. Otherwise, unless `~/.ai-factory/dashboard.lock` is
   less than 15 minutes old, start a **background** agent (`Agent` tool,
   `subagent_type: "general-purpose"`, `model: "haiku"`, `run_in_background: true`). Do not wait for
   it. Its prompt stands alone:

   ```
   In <project root>, invoke with the Skill tool `ai-factory:dashboard` with the arguments
   "pilot <printed datasets>". Ask no question. If it fails, write the error to
   .ai-factory/state/pilot/dashboard-error.txt, otherwise delete that file.
   ```

   `dashboard-error.txt` present at the start of a tick: repeat it in the report, once per error.

## 1. Carry out what the user decided

Queue rows `pilot = dev` in `ok` or `changed`, and `rejected` ones without `handled_at`
(`core/validation-queue.md`). Re-read the ticket first: if its status or assignee changed since
`created_at` (other than by the pilot or an automation its own action triggered), the row becomes
`failed` with the reason.

| Type | `ok` | `changed` |
|---|---|---|
| `plan` | `ticket-1-frame <KEY> pilot approved`, then `ticket <KEY> pilot` to the next checkpoint (counts in the code budget) | the note goes to `plan.md` under "Validation feedback", then `ticket-1-frame <KEY> pilot` |
| `ship` | `ticket-5-ship <KEY> pilot approved` | note to `ship.md`, then `ticket-5-ship <KEY> pilot` |
| `review_answers` | `ticket-6-feedback <KEY> pilot approved` | note to `feedback.md`, then `ticket-6-feedback <KEY> pilot` |
| `merge_staging` | `ticket-7-staging <KEY> pilot approved` | note to `state.md`, then `ticket-7-staging <KEY> pilot` |
| `review_comments`, `nudge` | `review-peers` / `follow-reviews` with `approved <id>` | rewritten from the note, back to `pending` |
| other | run `content` exactly | rewrite the action from the note, back to `pending` |

A `rejected` row is written in the ticket's `state.md` and gets `handled_at` (a rejected `plan`
takes the ticket out of the pilot). A row carried out becomes `done` with `handled_at`; a step that
fails makes it `failed` with the error. An `ok` row whose `requires` is not all `done` is left as it
is. An `ok` on a `plan` with a question marked "needs your answer": back to `pending`, asking for
it (`core/chain.md`, "Open questions"). Dates come from the clock (`core/ticket-folder.md`).

## 2. Take stock

In parallel:

- the dev queue of `workflow.md` (ticketing adapter, `list`);
- `state.md` of every ticket folder, and the pending rows of the queue;
- for tickets at `shipped`, `feedback` or `staging`: their MRs/PRs (forge adapter, `state`):
  approvals, threads whose last message is not the user's, merged or not;
- `cadences.json`, `dev.json`.

Write what was read as `dashboard-backlog.json` and `dashboard-prs.json`
(`skills/dashboard/SKILL.md`, step 2), so the refresh reads no tool itself.

A ticket of the dev queue the pilot cannot take because it has no key (no `key.fallback`) or no
type: one `human_task` per ticket, once, saying what to fix; it never just stays aside.

Rank each ticket on the first line of `priorities.md` that applies. Leave out a ticket with a
pending queue action, a rejected plan, or a `blocked:` line with nothing changed on it since. A
ticket started by hand (no folder, but past `new`) is listed in the report, never taken over.

## 3. Appointments

Only when `project.team` is `team` (a solo profile has nobody to review or nudge): the due slots of
block D in `priorities.md`, each in an agent, `review-peers pilot[ dry]` and
`follow-reviews pilot[ dry]`; note the start time in `cadences.json`, then add the actions of
`state/pilot/actions-review-peers.json` and `actions-follow-reviews.json` to the queue (as in
section 4) and empty those files. Review threads that `follow-reviews` reports join line 2 on the
next tick. Not in quiet hours.

## 4. Move forward, in order

Blocks A, B, then C of `priorities.md`, top to bottom, within the budget there (code tickets and
tickets in all per tick), the limits of block C (`pilots.dev.max_in_chain`,
`unattended.max_ready`) and the daily `unattended.max_tickets_per_day` for new tickets.

Each ticket runs in an agent (`Agent` tool, `subagent_type: "general-purpose"`), two at a time at
most, so the pilot's own context stays light. Its prompt stands alone:

```
In <project root>, invoke with the Skill tool `ai-factory:<skill>` with the arguments
"<KEY> pilot[ approved][ dry]". Ask no question: follow the pilot mode of the steps
(<plugin root>/core/chain.md). Do not write to the validation queue: proposed actions go to
.ai-factory/state/tickets/<KEY>/actions.json.
Every date you write comes from `date '+%Y-%m-%d %H:%M'`, and journal lines follow
<plugin root>/core/ticket-folder.md exactly.
Answer in five lines at most: the state reached in state.md, the actions added to actions.json,
any blocked: line, the commits made.
```

Without the `Agent` tool, run the ticket in the tick itself, one code ticket per tick.

After each ticket, add to the queue (queue adapter, `add`) the actions of its `actions.json` not
yet there (same ticket, type and content), with `pilot: dev`, `status: pending`, then empty the
file. A ticket that
failed the same step three times in a row is `blocked:` by the circuit breaker (`core/chain.md`).

## 5. Close the tick

1. **Cleanup**, once per calendar day (`cadences.json` → `cleanup`): archive then delete the handled rows
   older than 7 days (`core/validation-queue.md`, "Cleanup").
2. **Counters** in `dev.json`: `ticks_today` (`{date, n}`), `tickets_started_today`,
   `last_tick_at` (ISO time, from the clock), `failed_ticks` (reset by a tick that ends without an error). Three failed ticks in a row:
   set `stopped` with the last error, and say so in the report and the notification.
3. **Journal**: one line per action in `journal.md`, `YYYY-MM-DD HH:MM — <KEY> — <action> — <outcome>`,
   the time from the clock.
4. **Notify**, if `pilots.dev.notify` is not `false`: when this tick added pending actions or
   `human_task`s, newly blocked a ticket, or tripped the circuit breaker, send **one**
   `PushNotification` for the tick, under 200 characters, leading with what to act on:
   `Lima: 2 to approve (plan #21, ship #19), #14 blocked`. The ids already notified are in
   `notified.json` (a rewritten row is `<id>@<rewritten_at>`, so it counts as new): never notify
   twice for the same row or block. Nothing new: no notification. If the tool answers that the
   phone was not reached (Remote Control inactive), say it once in the report and in
   `notified.json`, so the user knows a long absence will not reach them.
5. **Dashboard**: the refresh of section 0c, always, last of all before the report: its banner is
   how the user learns the tick ended and what waits for them. A refresh still running blocks this
   one, so first wait for `~/.ai-factory/dashboard.lock` to go, five minutes at most.
6. **Report**, short: approvals carried out; tickets moved with the state reached; what waits in
   the queue (its link); blocks with their reason; tickets started by hand; what was left for the
   next tick for lack of budget. Remove `dev.lock`.
