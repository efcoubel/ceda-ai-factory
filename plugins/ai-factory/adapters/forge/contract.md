# Forge contract (merge requests / pull requests)

| Operation | Input | Output |
|---|---|---|
| `open` | repo, source branch, target branch, title, description | MR/PR url |
| `find` | repo, ticket key | open MRs/PRs whose title or branch holds the key |
| `state` | MR/PR | draft, approvers, unresolved threads (with the last author of each), last commit |
| `reply` | thread, text | — |
| `resolve` | thread | — |
| `approve` | MR/PR | — |
| `list_open` | repo, since | open MRs/PRs with author, title, source branch, draft, created and updated dates |
| `diff` | MR/PR | the changed files and their diff, and the head commit |
| `file_at` | repo, commit, path | the file's content at that commit |
| `comment` | MR/PR, text, optional file and line (new or old side) | comment link; a line refused by the forge falls back to a general comment starting with `file:line` |
| `me` | — | the user's handle |
| `create_repo` | owner, name, visibility, description | remote URL (new projects only) |
| `protect_branch` | repo, branch | no direct push, status checks required (new projects only) |

## MR/PR options

`tools.forge.config.mr_options` holds two kinds of options, and the ship recap says which is which:

- **applied at opening** by `open`: `draft`, `reviewers`, `labels`;
- **applied at merge**, which belongs to the user: `squash`, `delete_branch`. A skill never
  promises them. The adapter says whether the forge applies them by itself (a repository or
  project setting); if it does not, the recap says "at merge, yours: squash, delete the branch",
  and the doctor reports the setting that differs.

Rules: the target of a MR/PR is the repo's `default_branch`, never a protected branch other than
that one, and never merged by a skill. Pushes go through `git` and are guarded by the hook.
