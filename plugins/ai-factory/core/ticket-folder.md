# The ticket folder

Chain steps hand over through files, not through the conversation. Each ticket has a folder:
`<project root>/.ai-factory/state/tickets/<KEY>/`.

| File | Written by | Content |
|---|---|---|
| `state.md` | every step | First line: the step reached. Then a dated journal, one line per pass |
| `plan.md` | frame | Summary, decisions, repos and branch, acceptance criteria, steps |
| `review.md` | review | Findings per review round, with their outcome |
| `test.md` | test | Checks run, what the branch changes, test procedure, release notes |
| `ship.md` | ship, staging | MR/PR links, values written in the ticketing tool, what staging did |
| `ship-<repo>.md` | ship | The MR/PR description of one repository |
| `ship-comment.md` | ship | The ticket comment, as sent |
| `test-data.md` | test | The queries that found the accounts or records the test procedure uses |
| `feedback.md` | feedback | Review threads handled, with their outcome |
| `support.md` | support skills | Type, difficulty, diagnosis and evidence, proposed answer |
| `actions.json` | skills in pilot mode | Actions proposed for the validation queue |

Development states, in order: `framing`, `planned` (or `planned (auto)` when the pilot approved a
low-risk plan itself), `coded`, `reviewed`, `tested`, `shipped`, `feedback`, `staging`, `done`
(the MR/PR is merged into the default branch). Worktrees a
pilot needs live under `.ai-factory/state/worktrees/<KEY>/`.

Support states: `triaged`, `queued`, `human-task`, `waiting-requester`, `escalated`, `closed`.

Rules:

- Before acting, a step reads `state.md` and the earlier steps' files. A decision recorded there is
  not re-litigated.
- At the end of a step: new state on the first line, one journal line
  `YYYY-MM-DD HH:MM — <step>: <outcome in one sentence>`. The time comes from the clock
  (`date '+%Y-%m-%d %H:%M'`), never from memory.
- No other file in the folder: a working file a command needs (a body for `--body-file`) is one of
  the files above.
- A finding worth keeping goes to `learnings.md` or `state/learnings-pending.md`
  (`core/profile-schema.md`, "`learnings.md`").
- What a step cannot settle alone (dirty working tree, conflict, scope change, a check that cannot
  run) is written as `blocked: <reason>` without changing the state; in manual mode it is asked.
- Personal data never goes in these files beyond business identifiers (customer number, order id).
