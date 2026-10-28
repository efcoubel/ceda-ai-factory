# GitHub

**Status**: draft.

## Detect

A `github.com` remote; the `gh` CLI (`gh auth status`).

## Profile config

`{"repos": {"<repo name>": "<owner>/<name>"}}`

## Check

`gh auth status`, then `gh repo view <owner>/<name> --json name` for each repo.

## Operations

- `open`: `gh pr create --base <default_branch> --head <branch> --title … --body-file <file>`.
- `find`: `gh pr list -R <repo> --search "<KEY> in:title,head" --state open --json number,url,headRefName,isDraft`.
- `state`: `gh pr view <n> --json reviews,reviewDecision,isDraft,commits`; threads with
  `gh api graphql` (`reviewThreads { isResolved comments { author { login } body } }`).
- `reply`: `gh api repos/<owner>/<name>/pulls/<n>/comments/<id>/replies -f body=…`.
- `resolve`: GraphQL `resolveReviewThread`.
- `approve`: `gh pr review <n> --approve`.

## Pitfalls

- A solo repository has nobody to approve: the profile's review rule replaces human approval with
  the fresh-agent review of `ticket-3-review`.
