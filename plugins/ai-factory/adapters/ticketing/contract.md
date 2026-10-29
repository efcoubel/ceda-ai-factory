# Ticketing contract

| Operation | Input | Output |
|---|---|---|
| `list` | a queue query from `workflow.md` | keys with title, type, status, priority, assignee, created, updated |
| `read` | key | title, description, type, status, priority, assignee, reporter, comments, links, attachments (names) |
| `statuses` | key | the transitions available now, by target status name, with their required fields |
| `transition` | key, target status name, fields | new status |
| `comment` | key, text, visibility (public to the requester, or internal) | comment id |
| `assign` | key, person | — |
| `create` | project, type, title, description, optional `parent` key | new key (a sub-issue of `parent` when given) |
| `link` | key, key, link type | — |
| `me` | — | the user's identity in the tool |
| `setup` | project name, statuses, types | a board/project ready for the dev queue (new projects only) |

Rules: a transition is chosen by its target status name, never by a hard-coded id. A comment the
requester can see is a public answer: it follows `core/autonomy.md`.

## Ticket keys

The **key** is what branches, commits and ticket folders carry (`ABC-123`, `US-3.2`, `#42`). It is
not always the tool's own identifier: a project that numbered its stories in a file before using
a ticketing tool keeps those numbers. Every adapter reads `config.key`:

```json
"key": {
  "source": "native",
  "pattern": "US-\\d+(\\.\\d+)?",
  "numbering": "per_parent",
  "prefix": "US-"
}
```

| Field | Values |
|---|---|
| `source` | `native` (the tool's key or number), `title_prefix` (the title starts with the key, then ` — ` or `: `), `field` (a custom field or property, named in `field`) |
| `pattern` | the regular expression a key matches, used to find it in a title, a branch or a commit |
| `numbering` | for new tickets when `source` is not `native`: `sequential` (next free number after `prefix`) or `per_parent` (an epic is `US-<n>`, its sub-issues `US-<n>.<m>`) |
| `prefix` | the fixed start of new keys |

Two operations every adapter provides on top of the table above, built from `config.key`:

- `find_by_key`: key → the tool's ticket (for `title_prefix`, a title search on the key, then an
  exact match on the title's start);
- `next_key`: parent key or none → the next free key, from the highest existing one.

`create` writes the key where `source` says (at the start of the title for `title_prefix`).

