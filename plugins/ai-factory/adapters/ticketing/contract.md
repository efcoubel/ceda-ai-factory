# Ticketing contract

| Operation | Input | Output |
|---|---|---|
| `list` | a queue query from `workflow.md` | keys with title, type, status, priority, assignee, created, updated |
| `read` | key | title, description, type, status, priority, assignee, reporter, comments, links, attachments (names) |
| `statuses` | key | the transitions available now, by target status name, with their required fields |
| `transition` | key, target status name, fields | new status |
| `comment` | key, text, visibility (public to the requester, or internal) | comment id |
| `assign` | key, person | — |
| `create` | project, type, title, description | new key |
| `link` | key, key, link type | — |
| `me` | — | the user's identity in the tool |

Rules: a transition is chosen by its target status name, never by a hard-coded id. A comment the
requester can see is a public answer: it follows `core/autonomy.md`.
