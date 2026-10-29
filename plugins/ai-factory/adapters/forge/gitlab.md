# GitLab (gitlab.com or self-hosted)

**Status**: tested.

## Detect

A remote on a GitLab host; the `glab` CLI (`glab auth status`).

## Profile config

`{"host": "<gitlab host>", "projects": {"<repo name>": "<namespace>/<project>"}}`

## Check

`glab auth status --hostname <host>`, then `glab api "projects/<url-encoded path>"` for each repo.

## Operations

- `open`: `glab mr create --source-branch … --target-branch … --title … --description "$(cat <file>)" --yes`.
  Fallback if the token is refused: `git push -o merge_request.create -o merge_request.target=<branch> -o "merge_request.title=…"`.
- `find` / `state`: `glab api "projects/<p>/merge_requests?state=opened&search=<KEY>"`, then
  `.../approvals` (`approved_by`) and `.../discussions?per_page=100` (skip system notes).
- `reply`: `POST .../discussions/<id>/notes` with a JSON body (`glab api --input <file> -H "Content-Type: application/json"`).
- `resolve`: `PUT .../discussions/<id>?resolved=true`, then check `resolved` is `true`.
- `approve`: `glab mr approve <n>`.
- `create_repo`: `glab repo create <namespace>/<name> --private|--public --description …`.
- `protect_branch`: `glab api -X POST "projects/<p>/protected_branches" -f name=main -f push_access_level=0 -f merge_access_level=40`.

## Pitfalls

- `approvals_left` is 0 when no approval rule is configured: count `approved_by` instead.
- `glab` returns intermittent 401s on some self-hosted instances: retry with `curl` and the same
  token in the `PRIVATE-TOKEN` header. DNS errors also happen: retry before concluding.
