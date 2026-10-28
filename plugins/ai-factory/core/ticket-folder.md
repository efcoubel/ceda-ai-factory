# The ticket folder

Chain steps hand over through files, not through the conversation. Each ticket has a folder:
`<project root>/.ai-factory/state/tickets/<KEY>/`.

| File | Written by | Content |
|---|---|---|
| `state.md` | every step | First line: the step reached. Then a dated journal, one line per pass |
| `plan.md` | frame | Summary, decisions, repos and branch, acceptance criteria, steps |
| `review.md` | review | Findings per review round, with their outcome |
| `test.md` | test | Checks run, what the branch changes, test procedure, release notes |
| `ship.md` | ship | MR/PR links, values written in the ticketing tool |
| `feedback.md` | feedback | Review threads handled, with their outcome |
| `support.md` | support skills | Type, difficulty, diagnosis and evidence, proposed answer |
| `actions.json` | skills in pilot mode | Actions proposed for the validation queue |

Development states, in order: `framing`, `planned`, `coded`, `reviewed`, `tested`, `shipped`,
`feedback`, `staging`. Support states: `triaged`, `queued`, `human-task`, `waiting-requester`,
`escalated`, `closed`.

Rules:

- Before acting, a step reads `state.md` and the earlier steps' files. A decision recorded there is
  not re-litigated.
- At the end of a step: new state on the first line, one journal line
  `YYYY-MM-DD HH:MM — <step>: <outcome in one sentence>`.
- What a step cannot settle alone (dirty working tree, conflict, scope change, a check that cannot
  run) is written as `blocked: <reason>` without changing the state; in manual mode it is asked.
- Personal data never goes in these files beyond business identifiers (customer number, order id).
