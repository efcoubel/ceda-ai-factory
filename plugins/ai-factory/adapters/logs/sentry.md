# Sentry

**Status**: draft.

## Detect

`sentry_dart`, `@sentry/*` or `sentry/sentry` in dependencies; a Sentry MCP server.

## Profile config

`{"org": "<slug>", "projects": {"<repo>": "<project slug>"}, "token_ref": "env:SENTRY_TOKEN"}`

## Operations

- `errors_around`: issues and events of the project in the window.
- `errors_since`: unresolved issues first seen or regressed since the date, with event counts.
