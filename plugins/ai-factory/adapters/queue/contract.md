# Validation queue contract

| Operation | Input | Output |
|---|---|---|
| `pending_decisions` | pilot | actions in `ok`, `changed`, or `rejected` without `handled_at`, and ticked human tasks |
| `add` | actions | — (skips an action already pending for the same ticket, type and content) |
| `update` | action id, fields | — |
| `archive_old` | — | actions archived and removed (see `core/validation-queue.md`, "Cleanup") |

The action fields are in `core/validation-queue.md`.
