# Notion (a database used as a task board)

**Status**: draft.

## Detect

The Notion MCP connector is available (`notion-search`, `notion-fetch`,
`notion-query-data-sources`). Ask which database holds the tasks.

## Profile config

`{"data_source": "<data source id or url>", "properties": {"title": "Name", "status": "Status", "type": "Type", "priority": "Priority", "assignee": "Assignee", "key": "ID"}, "key_prefix": "LIMA"}`
— the property names are read from the database schema during onboarding, not guessed.

## Check

`notion-fetch` on the data source; confirm every property in `properties` exists and list the
options of the status property.

## Operations

- `list`: `notion-query-data-sources` with a filter on the status property (the queue in
  `workflow.md` is written as that filter).
- `read`: `notion-fetch` on the page: properties, then the page body as the description;
  `notion-get-comments` for comments.
- `statuses`: the status property's options; Notion has no transition rules, any option is reachable.
- `transition`: `notion-update-page` setting the status property.
- `comment`: `notion-create-comment` on the page (there is no public/internal distinction).
- `assign`: `notion-update-page` on the people property; `notion-get-users` to find the person.
- `create`: `notion-create-pages` in the data source.
- `link`: a relation property if the database has one; otherwise a mention in the body.
- `me`: `notion-get-self`.

## Pitfalls

- Notion has no ticket keys by default: use the database's unique ID property if it exists
  (`key_prefix` + number); otherwise the onboarding proposes to add one, and keys are page ids
  until then.
