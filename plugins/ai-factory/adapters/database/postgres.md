# PostgreSQL

**Status**: draft.

## Detect

A `postgres://` DSN in env files or compose files; `psql` on the host; a `~/.pg_service.conf`.

## Profile config

`{"client": "docker:postgres:16", "credentials": "~/.pg_service.conf", "services": {"<app>": {"staging": "<service name>"}}}`

## Check

`SELECT current_database(), version();` per service.

## Operations

- `query`: `psql "service=<name>" -v ON_ERROR_STOP=1 -c "SET default_transaction_read_only = on;" -f query.sql`
  (in a throwaway container mounting the service file read-only if `psql` is not on the host).
- `export`: `\copy (<query>) TO 'export.csv' WITH CSV HEADER`.
- `dry_check`: same read-only session; the first write fails with "cannot execute … in a read-only transaction".
