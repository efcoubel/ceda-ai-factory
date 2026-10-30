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
| `actions.json` | skills in pilot mode | Actions proposed, waiting to be added to the validation queue. The pilot empties it once they are queued: the queue is the only source for their status |

Development states, in order: `framing`, `planned` (or `planned (auto)` when the pilot approved a
low-risk plan itself), `coded`, `reviewed`, `tested`, `shipped`, `feedback`, `staging`, `done`
(the MR/PR is merged into the default branch). Worktrees a
pilot needs live under `.ai-factory/state/worktrees/<KEY>/`.

Support states: `triaged`, `queued`, `human-task`, `waiting-requester`, `escalated`, `closed`.

Rules:

- Before acting, a step reads `state.md` and the earlier steps' files. A decision recorded there is
  not re-litigated.
- At the end of a step: new state on the first line, one journal line, exactly:
  `2026-10-30 14:05 — ship: PR #52 opened`, with no bullet, and for `<step>` one of `frame`, `code`,
  `review`, `test`, `ship`, `feedback`, `staging`, `close-out`. The dashboard and the doctor read
  this format. Every date a skill writes (journal, queue ids, `handled_at`) comes from running
  `date '+%Y-%m-%d %H:%M'` at that moment, never from memory or an estimate.
- No other file in the folder: a working file a command needs (a body for `--body-file`) is one of
  the files above.
- A finding worth keeping goes to `learnings.md` or `state/learnings-pending.md`
  (`core/profile-schema.md`, "`learnings.md`").
- What a step cannot settle alone (dirty working tree, conflict, scope change, a check that cannot
  run) is written as a line starting with `blocked: <reason>`, without changing the state; in
  manual mode it is asked. A later journal line lifts it. Elsewhere in a sentence the word means
  nothing.
- Personal data never goes in these files beyond business identifiers (customer number, order id).
