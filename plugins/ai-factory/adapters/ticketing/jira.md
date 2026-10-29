# Jira (Cloud, Software or Service Management)

**Status**: tested.

## Detect

The Atlassian MCP connector is available (tools such as `searchJiraIssuesUsingJql`,
`getJiraIssue`). Ticket keys like `ABC-123` in branch names or commit messages.

## Profile config

`{"cloud_id": "<uuid>", "site": "<name>.atlassian.net", "projects": ["ABC"], "custom_fields": {"<purpose>": "customfield_10xxx"}}`
— get `cloud_id` from `getAccessibleAtlassianResources`.

## Check

`atlassianUserInfo`, then one `searchJiraIssuesUsingJql` on the dev queue with `maxResults: 1`.

## Operations

- `list`: `searchJiraIssuesUsingJql`, `responseContentFormat: "markdown"`, only the fields needed
  (avatars make results huge); page with `nextPageToken`.
- `read`: `getJiraIssue` with `fields` listed; `expand: "names"` to resolve custom field names.
- `statuses`: `getTransitionsForJiraIssue` with `expand: "transitions.fields"`; pick by `to.name`.
- `transition`: `transitionJiraIssue`. Long-text fields want ADF; many custom text areas render only
  `paragraph` nodes with plain `text`.
- `comment`: `addCommentToJiraIssue` (`contentFormat: "markdown"`). On Service Management projects
  a plain comment is public to the requester.
- `assign`: `editJiraIssue` with `assignee`; `lookupJiraAccountId` to find the account.
- `create`: `getJiraProjectIssueTypesMetadata` for the type, then `createJiraIssue`.
- `link`: `getIssueLinkTypes`, then `createIssueLink`.
- `create` with `parent`: an epic link or a sub-task, depending on the project's hierarchy
  (`getJiraProjectIssueTypesMetadata` tells which types exist).
- `setup`: Jira projects and workflows are created in the Jira UI, not through the connector: a
  task for the user, with the statuses and types to create.

## Pitfalls

- Service Management automations may change the status on assignment: an expected status change
  right after the pilot's own action is not a conflict.
- Attachments cannot be uploaded or downloaded through the MCP connector: a file to attach is a
  `human_task`, unless an API token is configured (by reference) in the profile.
