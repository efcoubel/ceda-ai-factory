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
| `ticket_title`, `ticket_url` | The ticket's title, as its tool shows it, and its link |
| `summary` | The question put to the user, one sentence (see "Written for the reader") |
| `why` | Why it reaches the user now, two sentences at most |
| `effects` | Up to three lines: what happens on an `ok`, who sees it |
| `watch` | Up to three lines: what deserves the user's judgement. Empty when nothing does |
| `questions` | The open questions of a `plan` (`core/chain.md`, "Open questions"): `[{id, text, why, proposed, options}]` |
| `content` | Exactly what will be sent or run: the full detail, read on request |
| `files` | Paths in the ticket folder worth reading |
| `requires` | Optional list of action ids that must be `done` first: the `human_task` before a merge, one ticket's merge before another's |
| `status` | `pending`; then `ok`, `rejected` or `changed` (set by the user); then `done` or `failed` (set by the pilot) |
| `note` | The user's instruction when `changed`; the error when `failed` |
| `answers` | Set by the page with an `ok` or a `changed`: `[{id, question, answer}]`, the questions the user answered otherwise than proposed |
| `reply` | The pilot's message when a row comes back to `pending`: what it changed, or why the `ok` was not applied |
| `created_at`, `decided_at`, `handled_at` | ISO dates |

## Written for the reader

The queue is read in a few seconds, often far from the code, and a validation the user cannot
follow protects nothing. `content` is for the pilot and for whoever wants the detail; the fields
above it are the card, and they stand on their own. In `project.working_language`:

- **`summary`** asks one thing, under 90 characters, in the words of the product and of the person
  deciding: `Publish the new sign-in screen for review?`, not `push feat/42-sign-in, open the PR to
  main`. No branch, commit, repository, action id or tool name. The ticket's key and title are already above it. A `human_task` says what to do, in the
  imperative. If the row exists for one question, the summary is that question.
- **`why`** says what the user does not know yet: what led here, what it brings.
- **`effects`** are concrete and say the reach: on this machine, on the forge, in front of testers,
  in production. Say what stays untouched when that is the reassuring part.
- **`watch`** is the short list a careful reviewer would want read before deciding: a risk, a product
  choice left open, a conflict to come. Nothing routine, and nothing the criteria of "Risk" already
  settled. An empty list is a signal: this one can go fast.
- **Never** an action id, a field name, a skill name or a type name (`human_task`, `needs your
  answer`), never the label of a button: pages change, and each language has its own.

`plan`, `ship`, `review_answers`, `merge_staging`, `comment`, `create_ticket` and `review_comments`
carry `summary`, `why` and `effects`. An `assign`, `transition` or `cleanup` carries a one-line
`summary`: the page lists them as routine steps to approve together, unless `content` is long or
`watch` is set, so a transition that posts a comment stays a card. A `human_task` puts its steps in
`content`, in order, each command on its own line.

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
- A row that comes back to `pending` carries a `reply`, and its `summary`, `why`, `effects` and
  `questions` are written anew. The user sees the reply first: it says what changed, or why the
  `ok` was not applied, and what is expected now.
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
