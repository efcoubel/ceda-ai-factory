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
- `create_repo`: `gh repo create <owner>/<name> --private|--public --description … --source . --remote origin`
  (no `--push`: the push is its own step). Pushing through `gh` credentials without changing the
  user's global git config: `git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push`.
- `protect_branch`: `gh api -X PUT repos/<owner>/<name>/branches/main/protection` with required
  status checks and `enforce_admins: false` (the solo owner keeps the right to merge their own PRs).
  Private repositories on free plans may not offer protection: then say so and rely on the hook.

## Pitfalls

- A solo repository has nobody to approve: the profile's review rule replaces human approval with
  the fresh-agent review of `ticket-3-review`.
