---
name: ticket-1-frame
description: First step of the ai-factory chain - reads the ticket, finds and proves the cause or the place the change belongs, sets the scope of repositories, writes the plan with acceptance criteria, gets it approved (or approves it itself for a low-risk ticket in unattended mode), then creates the branches and moves the ticket to in progress. Use for "/ai-factory:ticket-1-frame <KEY>", "frame this ticket", "plan ticket X", "I'm taking ticket X".
argument-hint: "<KEY> [chain | pilot [approved] [dry]]"
---

# /ai-factory:ticket-1-frame

**Plugin root**: two directories above this skill's base directory. Read `core/chain.md` first.

This step decides most of the outcome: a wrong scope or an ambiguity left open is paid for at
every later step. Take the time here. A plan already approved is not redone unless asked.

## 1. Understand the ticket

Read the ticket (ticketing adapter, `read`): title, type, description, status, comments (they
often hold the real scope), links, the parent epic if any. Then read the code until you can explain
where the problem comes from, or where the change plugs in.

- For a **bug**, the root cause is found and **proven** in the code (`file:line`), not guessed. A
  defect that depends on state (a field of a long-lived object, a cache) is also proven by that
  object's lifecycle: who creates it, and for how many calls. Reproduce it when a test or a command
  can.
- For a **feature**, find the existing code it extends and the conventions it must follow.

## 2. Scope

- A branch for this key may already exist: `git branch -a` in each repository, matched with the
  key pattern.
- Follow the calls between repositories (`repos.md`, "Talks to"); a change in one may need its
  counterpart in another.
- If the ticket is assigned to someone else, stop: `blocked: assigned to <person>`.

## 3. Write the plan

`plan.md` in the ticket folder, in the working language:

- **Ticket**: link, and a summary in three lines.
- **Cause / need**: with the places in the code.
- **Repositories**: each with its reason; plausible ones left out, with why.
- **Branch**: from `repos[].branch_format`, the same in every repository.
- **Acceptance criteria**: checkable, from the point of view of the application's user.
  `ticket-3-review` and `ticket-4-test` judge the work against them.
- **Steps**: the changes, repository by repository, each with the test that will cover it.
- **Watch out**: data migration, a long operation on a large table, a deployment note to foresee,
  existing data to fix, an error behaviour that changes, a dependency change.
- **Questions**: what remains ambiguous, each with a proposed answer (`core/chain.md`, "Open
  questions").
- **Merge gate**, if the ticket must not reach the default branch as is: one line per condition,
  in words, and when it can be checked, `check: <command>` that prints nothing once it holds
  (`check: git grep -n a-completer`).
- **Risk**: for each criterion of `unattended.low_risk` (`core/autonomy.md`), "holds" or "does not
  hold: why". Compute it even when unattended mode is off: it tells the user how much to look.

## 4. Checkpoint: the plan

**Unattended, low-risk** — pilot mode, `unattended.auto_plan` on, every listed criterion holds,
the ticket type is in `unattended.types`, the plan has no open question, and `plan.md`'s "Risk"
section shows it: approve the plan yourself. Write `planned (auto)` in `state.md`, add to
`actions.json` an **information** action (`type: plan`, `status: done`, summary prefixed
"Approved by the pilot (low-risk)", the plan as `content`), and go to step 5. Any doubt on one
criterion: this is not the case.

**Otherwise**, before writing code or creating any branch:

- manual / `chain`, in the conversation itself (a file the user has not opened is not shown):
  1. **the plan**: the summary, the repositories, the acceptance criteria, the steps, "Watch out"
     and "Risk", in full or close to it;
  2. **what will be done after the go**, one line each: the branch created in each repository, the
     assignment (if the ticket has no assignee, and to whom), the transition to the "start work"
     status of `workflow.md`;
  3. the open questions, with `AskUserQuestion` if there are any.

  Answering the questions is **not** approval of the plan. Write the answers into `plan.md`, show
  what they changed in the plan, and wait for an explicit go on the plan and on the lines of point
  2. Nothing of point 2 is done before it;
- `pilot`: add a `plan` action to `actions.json` (`summary`, `why`, `effects`, `watch` as
  `core/validation-queue.md`, "Written for the reader", says: the decision, what the plan brings,
  and the lines of "Watch out" that need a person; `questions` as `core/chain.md` says; content: the
  plan, the assignment, the transition, the questions; files: `plan.md`), set `state.md` to
  `framing`, return. Called again with `pilot approved`, go to step 5; a `changed` action's
  instruction is in `plan.md` under "Validation feedback": redo the plan with it.

## 5. Create the branches

For each repository of the plan, following `core/chain.md` ("Working in the repositories"):

```bash
git -C <repo> fetch origin <default_branch>
git -C <repo> switch -c <branch> --no-track origin/<default_branch>
```

A branch that already exists: switch to it and report how far behind `origin/<default_branch>` it
is.

## 6. The ticket and the end

Assign the ticket to the user if it has no assignee, and move it to the "start work" status
(ticketing adapter, `assign`, `transition`), exactly as the approved checkpoint listed them; for a plan
approved by the pilot itself, they follow the matrix of `core/autonomy.md` ("Any other public
answer or ticket transition": queued, unless the profile loosened it).

Set `state.md` to `planned` (or keep `planned (auto)`). Alone, propose `ticket-2-code`; in a chain,
return.
