# Queue in a local markdown file

**Status**: draft.

For terminals without artifacts. `state/pilot/queue.md` holds one `## <id>` section per action,
fields as `- field: value` lines, `content` in a fenced block. The user decides by editing the
`status:` line (`ok`, `rejected`, `changed` with a `note:` line). The archive works the same.
A section opens with the fields written for the reader (`core/validation-queue.md`), then
`questions`, one `- <id>: <text> — proposed: <answer>` line each, then `content` last. An answer
other than the proposed one is written in `note:` with the status `changed`.
