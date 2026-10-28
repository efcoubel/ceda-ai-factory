# MySQL / MariaDB

**Status**: tested.

## Detect

`composer.json` or env files naming a `mysql`/`mariadb` DSN; a `~/.my.cnf` with
`[client_<app>_<env>]` sections.

## Profile config

`{"credentials": "~/.my.cnf", "sections": {"<app>": {"staging": "client_<app>_staging"}}, "production_environments": ["production"]}`
— one `~/.my.cnf` section per base and environment, `chmod 600`; no bare `[client]` section, so
nothing connects by default.

## Check

`SELECT DATABASE(), VERSION()` on each configured section, through the script below.

## Operations

- `query`: `scripts/db-mysql.sh <app> <env> < query.sql` — a throwaway client container mounting
  `~/.my.cnf` read-only, `--init-command="SET SESSION TRANSACTION READ ONLY"`, refusing any
  environment the profile marks as production. `tsv` as third argument for raw output.
- `export`: `query` with `tsv`, then `scripts/tsv-to-csv.py` (`;` separator, UTF-8 BOM for Excel).
- `dry_check`: rewrite each `UPDATE`/`DELETE` as a `SELECT` on the same `WHERE`; run the whole
  script in the read-only session: it must stop on error 1792 at its first write.

## Pitfalls

- MariaDB 11.4 clients verify the server certificate by default. An expired or misnamed server
  certificate fails with "unable to get local issuer certificate": that is for the user to fix in
  `~/.my.cnf` (or better, get the certificate renewed); Claude never weakens TLS itself.
