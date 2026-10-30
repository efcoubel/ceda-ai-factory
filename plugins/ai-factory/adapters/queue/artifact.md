# Queue on a claude.ai artifact page

**Status**: tested.

## Detect

The `Artifact` and `ArtifactData` tools are available (Claude desktop app or claude.ai).

## Profile config

`{"url": "https://claude.ai/artifact/<id>", "page_version": "<version>"}` — created by the
onboarding from `templates/validation-page.html`, private, database readable and writable by the
owner only (`rules: [{path: "", read: "owner", write: "owner"}]`). `page_version` is the version of
the page last published (`/ai-factory:onboarding update page`).

## Check

`ArtifactData` `list` on `actions` with `limit: 1`, and the same with `as_level: "view"`, which must
return nothing.

## Operations

- `pending_decisions`: `ArtifactData` `query` on `actions`, `where` on `pilot` and `status`.
- `add`: `batch` of `set` writes, `doc_id` = the action id.
- `update`: `update` with `if_version` from the last read.
- `archive_old`: `query` the old handled rows, append them to the archive file, then `batch` of
  `delete` with `if_version`.

## Pitfalls

- The page must load pending actions without a limit and only cap the history; otherwise old
  pending actions silently disappear from view.
- `ok` rows stay on the page until they are carried out: the user sees what they wait for and can
  take a validation back. Read a row's status again before running it, not only at the start of the
  tick; an `update` that fails on `if_version` means the user changed the row: leave it.
