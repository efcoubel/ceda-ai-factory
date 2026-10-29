# GitHub

**Status**: draft.

## Detect

A `github.com` remote; the `gh` CLI (`gh auth status`).

## Profile config

`{"repos": {"<repo name>": "<owner>/<name>"}}`

## Check

`gh auth status`, then `gh repo view <owner>/<name> --json name` for each repo. Warning when a
merge-time option of `mr_options` does not match the repository's settings (see `open`).

## Operations

- `open`: `gh pr create --base <default_branch> --head <branch> --title … --body-file <file>`, plus
  `--draft` when `mr_options.draft`, `--reviewer <login>` per reviewer, `--label <name>` per label.
- **Merge-time options**: GitHub sets them per repository, not per PR. Read them with
  `gh repo view <owner>/<name> --json deleteBranchOnMerge,squashMergeAllowed,mergeCommitAllowed,rebaseMergeAllowed`:
  - `delete_branch: true` holds only if `deleteBranchOnMerge` is true;
  - `squash: true` holds only if `squashMergeAllowed` is true, and the user picks it when merging
    (it is the forced choice only when the other merge methods are off).

  The fix for a setting that differs is a repository setting (`gh repo edit <owner>/<name> --delete-branch-on-merge`,
  `--enable-squash-merge`, `--enable-merge-commit=false`): proposed to the user as a configuration
  change, never made on the way.
- `find`: `gh pr list -R <repo> --search "<KEY> in:title,head" --state open --json number,url,headRefName,isDraft`.
- `state`: `gh pr view <n> --json reviews,reviewDecision,isDraft,commits`; threads with
  `gh api graphql` (`reviewThreads { isResolved comments { author { login } body } }`).
- `reply`: `gh api repos/<owner>/<name>/pulls/<n>/comments/<id>/replies -f body=…`.
- `resolve`: GraphQL `resolveReviewThread`.
- `approve`: `gh pr review <n> --approve`.
- `list_open`: `gh pr list -R <owner>/<name> --state open --json number,url,title,author,headRefName,isDraft,createdAt,updatedAt`.
- `diff`: `gh pr diff <n> -R <owner>/<name>` and `gh pr view <n> --json files,headRefOid`.
- `file_at`: `gh api "repos/<owner>/<name>/contents/<path>?ref=<sha>" -H "Accept: application/vnd.github.raw"`.
- `comment`: general, `gh pr comment <n> --body-file <file>`; on a line, `gh api -X POST repos/<owner>/<name>/pulls/<n>/comments`
  with a JSON body `{body, commit_id: <head sha>, path, line, side: "RIGHT"}` (`"LEFT"` for a removed
  line). Write the body to a file: passed inline, newlines and backticks arrive escaped.
- `create_repo`: `gh repo create <owner>/<name> --private|--public --description … --source . --remote origin`
  (no `--push`: the push is its own step). Pushing through `gh` credentials without changing the
  user's global git config: `git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push`.
- `protect_branch`: `gh api -X PUT repos/<owner>/<name>/branches/main/protection` with required
  status checks and `enforce_admins: false` (the solo owner keeps the right to merge their own PRs).
  Private repositories on free plans may not offer protection: then say so and rely on the hook.

## Pitfalls

- A solo repository has nobody to approve: the profile's review rule replaces human approval with
  the fresh-agent review of `ticket-3-review`.
