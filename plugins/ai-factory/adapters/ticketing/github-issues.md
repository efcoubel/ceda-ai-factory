# GitHub Issues

**Status**: draft.

## Detect

A `github.com` remote and the `gh` CLI (`gh auth status`).

## Profile config

```json
{
  "repo": "<owner>/<name>",
  "labels": { "bug": "bug", "task": "task", "feature": "enhancement" },
  "project": { "owner": "<owner>", "number": 1, "status_field": "Status" },
  "key": { "source": "native" }
}
```

- **Types** are labels on a personal account (`labels` maps the engine's types to the label
  names), issue types on an organization.
- **Statuses**: with `project` set, the status is the value of `status_field` on the issue's item in
  that GitHub Project, and the status map in `workflow.md` uses those option names. Without
  `project`, statuses are open/closed plus labels.
- **Keys**: `native` uses the issue number (`#42`); `title_prefix` uses a key at the start of the
  title (`US-3.2 — Offline mode`), see "Ticket keys" in `contract.md`.

## Check

`gh auth status`, then `gh issue list -R <repo> --limit 1`.

## Check (keys)

With `title_prefix`: `find_by_key` on the key of the current branch (or of the last commit that
carries one) returns exactly one issue.

## Operations

- `list`: with `project`, `gh project item-list <number> --owner <owner> --format json --limit 500`
  (each item carries its fields, `Status` among them; keep items whose content is an issue of
  `repo`); without, `gh issue list -R <repo> --search "<query>" --json number,title,labels,state,assignees,createdAt,updatedAt`.
- `read`: `gh issue view <n> -R <repo> --json title,body,labels,state,assignees,comments`.
- `statuses`: with `project`, the options of `status_field`: `gh project field-list <number> --owner <owner> --format json`
  (keep the field id and each option id); without, open/closed plus status labels.
- `transition`: with `project`, four calls:

  ```bash
  PROJECT_ID=$(gh project view <number> --owner <owner> --format json --jq .id)
  FIELD=$(gh project field-list <number> --owner <owner> --format json --jq '.fields[] | select(.name=="<status_field>")')
  FIELD_ID=$(jq -r .id <<<"$FIELD"); OPTION_ID=$(jq -r '.options[] | select(.name=="<target status>") | .id' <<<"$FIELD")
  ITEM_ID=$(gh project item-list <number> --owner <owner> --format json --limit 500 --jq '.items[] | select(.content.number==<n> and .content.repository=="<owner>/<name>") | .id')
  gh project item-edit --project-id "$PROJECT_ID" --id "$ITEM_ID" --field-id "$FIELD_ID" --single-select-option-id "$OPTION_ID"
  ```

  An issue not yet in the project is added first (`gh project item-add <number> --owner <owner> --url <issue url>`).
  Close the issue too when the target maps to `done`. Without
  `project`, `gh issue edit --add-label/--remove-label` and `gh issue close`.
- `comment`: `gh issue comment <n> --body-file <file>`.
- `assign`: `gh issue edit <n> --add-assignee <login>`.
- `create`: `gh issue create --title … --body-file … --label …`. With a `parent`: create the issue,
  then `gh api -X POST repos/<owner>/<name>/issues/<parent>/sub_issues -F sub_issue_id=<id>` where
  `<id>` is the new issue's numeric `id` (not its number: `gh api repos/<owner>/<name>/issues/<n> --jq .id`).
- `link`: a `Refs #n` line in the body.
- With `key.parent: label`, the epic of an issue is its label matching `label_pattern`; `create`
  adds that label instead of a sub-issue link.
- `me`: `gh api user --jq .login`.
- `find_by_key`: `native`: the number; `title_prefix`: `gh issue list -R <repo> --state all --search "\"<key>\" in:title" --json number,title`,
  then the issue whose title starts with the key followed by ` — `, `: ` or a space.
- `next_key`: list all titles (`--state all --limit 1000`), extract keys with `pattern`, take the
  highest under the parent (`per_parent`) or overall (`sequential`), add one.
- `setup`: labels for types (`gh label create bug|task|feature --force`), then a Project:
  `gh project create --owner <owner> --title <name>`, its "Status" field options matching the
  status map, and `gh project link` to each repository. Issue types (instead of labels) exist only
  on organizations; on a personal account, labels are the types.
