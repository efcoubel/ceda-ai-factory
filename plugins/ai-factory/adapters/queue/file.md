# Queue in a local markdown file

**Status**: draft.

For terminals without artifacts. `state/pilot/queue.md` holds one `## <id>` section per action,
fields as `- field: value` lines, `content` in a fenced block. The user decides by editing the
`status:` line (`ok`, `rejected`, `changed` with a `note:` line). The archive works the same.
