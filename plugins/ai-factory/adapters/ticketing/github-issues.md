# GitHub Issues

**Status**: draft.

## Detect

A `github.com` remote and the `gh` CLI (`gh auth status`).

## Profile config

`{"repo": "<owner>/<name>", "labels": {"bug": "bug", "task": "task", "feature": "enhancement"}, "project": null}`
— types and statuses are labels (or a GitHub Project's status field if `project` is set).

## Check

`gh auth status`, then `gh issue list -R <repo> --limit 1`.

## Operations

- `list`: `gh issue list -R <repo> --search "<query>" --json number,title,labels,state,assignees,createdAt,updatedAt`.
- `read`: `gh issue view <n> -R <repo> --json title,body,labels,state,assignees,comments`.
- `statuses` / `transition`: open/closed plus status labels; `gh issue edit --add-label/--remove-label`, `gh issue close`.
- `comment`: `gh issue comment <n> --body-file <file>`.
- `assign`: `gh issue edit <n> --add-assignee <login>`.
- `create`: `gh issue create --title … --body-file … --label …`. With a `parent`: create the issue,
  then `gh api -X POST repos/<owner>/<name>/issues/<parent>/sub_issues -F sub_issue_id=<id>` where
  `<id>` is the new issue's numeric `id` (not its number: `gh api repos/<owner>/<name>/issues/<n> --jq .id`).
- `link`: a `Refs #n` line in the body.
- `me`: `gh api user --jq .login`.
- `setup`: labels for types (`gh label create bug|task|feature --force`), then a Project:
  `gh project create --owner <owner> --title <name>`, its "Status" field options matching the
  status map, and `gh project link` to each repository. Issue types (instead of labels) exist only
  on organizations; on a personal account, labels are the types.
