# Forge contract (merge requests / pull requests)

| Operation | Input | Output |
|---|---|---|
| `open` | repo, source branch, target branch, title, description | MR/PR url |
| `find` | repo, ticket key | open MRs/PRs whose title or branch holds the key |
| `state` | MR/PR | draft, approvers, unresolved threads (with the last author of each), last commit |
| `reply` | thread, text | — |
| `resolve` | thread | — |
| `approve` | MR/PR | — |
| `me` | — | the user's handle |
| `create_repo` | owner, name, visibility, description | remote URL (new projects only) |
| `protect_branch` | repo, branch | no direct push, status checks required (new projects only) |

Rules: the target of a MR/PR is the repo's `default_branch`, never a protected branch other than
that one, and never merged by a skill. Pushes go through `git` and are guarded by the hook.
