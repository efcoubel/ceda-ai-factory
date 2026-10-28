# No ticketing tool

**Status**: draft.

Tickets live as markdown files in `.ai-factory/state/tickets/<KEY>/ticket.md` (title, type, status,
description). `list` reads them, `transition` rewrites their status line, `comment` appends to
them. Keys are `T-<number>`. Useful for a solo project that tracks work nowhere else.
