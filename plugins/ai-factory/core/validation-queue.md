# The validation queue

Where pilots put every action that waits for the user, and where the user answers. The profile's
`tools.queue.adapter` says where it lives (`adapters/queue/`): a private claude.ai artifact page
with buttons, or a local markdown file when artifacts are not available.

## An action

| Field | Content |
|---|---|
| `id` | `<KEY>-<type>-<YYYYMMDDHHMM>`: `<type>` is the `type` field, the time from the clock |
| `ticket` | Ticket key |
| `pilot` | `support` or `dev` |
| `type` | `comment`, `transition`, `assign`, `create_ticket`, `human_task`, `plan`, `ship`, `review_answers`, `merge_staging`, `cleanup`, `review_comments`, `nudge` |
| `summary` | One line: what will be done |
| `content` | Exactly what will be sent or run |
| `files` | Paths in the ticket folder worth reading |
| `requires` | Optional list of action ids that must be `done` first: the `human_task` before a merge, one ticket's merge before another's |
| `status` | `pending`; then `ok`, `rejected` or `changed` (set by the user); then `done` or `failed` (set by the pilot) |
| `note` | The user's instruction when `changed`; the error when `failed` |
| `created_at`, `decided_at`, `handled_at` | ISO dates |

## Rules

- A row whose `requires` is not all `done` is not run, even at `ok`: it stays `ok`, and the report
  says what it waits for. Say an order in `requires`, never only in the text.
- A path in `summary` or `content` is absolute, or says what it is relative to: the user reads it
  far from the ticket folder.
- A `plan` with open questions: see `core/chain.md`, "Open questions".
- `ok` runs exactly `content`, nothing more. Re-read the ticket first: if its status or assignee
  changed since `created_at` (other than by the pilot itself, or by an automation the tool chains
  on the pilot's action), the action becomes `failed` with the reason.
- `changed` is rewritten from `note` and goes back to `pending` with a new `rewritten_at`; it never runs directly. For a chain
  step (`plan`, `ship`, `review_answers`, `merge_staging`), the note goes to the step's file under
  "Validation feedback" and the step runs again in `pilot` mode.
- `rejected` is written at once in the ticket's `state.md` as `rejected: <type> — <note>` and gets
  `handled_at`. That line, not the queue, prevents proposing the same action again. A rejected
  `plan` takes the whole ticket out of the pilot until the user restarts it.
- A `human_task` becomes `done` when the user ticks it; the pilot then prepares what follows.
- No two pending actions for the same ticket, type and content.

## Cleanup

Once a day, on the first tick of either pilot (`state/pilot/cadences.json`, key `cleanup`):

1. append every `done`, `rejected` or `failed` action older than **7 days** to
   `state/pilot/archive/YYYY-MM.jsonl`, one JSON line each;
2. check each one is in the archive, then delete it from the queue;
3. never delete a `pending`, `ok` or `changed` action; report the ones pending for more than 7 days.
