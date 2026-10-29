# GitLab (gitlab.com or self-hosted)

**Status**: tested.

## Detect

A remote on a GitLab host; the `glab` CLI (`glab auth status`).

## Profile config

`{"host": "<gitlab host>", "projects": {"<repo name>": "<namespace>/<project>"}}`

## Check

`glab auth status --hostname <host>`, then `glab api "projects/<url-encoded path>"` for each repo.

## Operations

- `open`: `glab mr create --source-branch … --target-branch … --title … --description "$(cat <file>)" --yes`,
  plus `--draft`, `--reviewer <user>`, `--label <name>`, and the merge-time options, which GitLab
  stores on the MR itself: `--remove-source-branch` for `delete_branch`, `--squash-before-merge`
  for `squash`.
  Fallback if the token is refused: `git push -o merge_request.create -o merge_request.target=<branch> -o "merge_request.title=…"`.
- `find` / `state`: `glab api "projects/<p>/merge_requests?state=opened&search=<KEY>"`, then
  `.../approvals` (`approved_by`) and `.../discussions?per_page=100` (skip system notes).
- `reply`: `POST .../discussions/<id>/notes` with a JSON body (`glab api --input <file> -H "Content-Type: application/json"`).
- `resolve`: `PUT .../discussions/<id>?resolved=true`, then check `resolved` is `true`.
- `approve`: `glab mr approve <n>`.
- `list_open`: `glab api "projects/<p>/merge_requests?state=opened&updated_after=<ISO>&per_page=100"`.
- `diff`: `glab api "projects/<p>/merge_requests/<n>/diffs?per_page=100"`, and `diff_refs` from the MR.
- `file_at`: `glab api "projects/<p>/repository/files/<url-encoded path>/raw?ref=<sha>"`.
- `comment`: `POST .../merge_requests/<n>/discussions` with a JSON body; on a line, with
  `position: {position_type: "text", base_sha, start_sha, head_sha, new_path, old_path, new_line | old_line}`
  from `diff_refs`. Sent as `-f "position[...]"` fields the position is silently ignored and a
  general comment is created: send JSON (`--input <file> -H "Content-Type: application/json"`) and
  check the created note is a `DiffNote`.
- `create_repo`: `glab repo create <namespace>/<name> --private|--public --description …`.
- `protect_branch`: `glab api -X POST "projects/<p>/protected_branches" -f name=main -f push_access_level=0 -f merge_access_level=40`.

## Pitfalls

- `approvals_left` is 0 when no approval rule is configured: count `approved_by` instead.
- `glab` returns intermittent 401s on some self-hosted instances: retry with `curl` and the same
  token in the `PRIVATE-TOKEN` header. DNS errors also happen: retry before concluding.
