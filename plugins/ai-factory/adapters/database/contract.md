# Database contract

| Operation | Input | Output |
|---|---|---|
| `query` | environment name, read query | rows |
| `export` | environment name, read query | a CSV file in the ticket folder |
| `dry_check` | environment name, write script | the rows each write would touch, without writing |

Rules, enforced by every adapter:

- **Production is never connected to.** The adapter refuses an environment the profile marks as
  production. Diagnose on a copy (staging, preprod, emulator) and say how old its data is.
- Sessions are read-only. A write script is a deliverable for the user, run by the user.
- A write script runs inside a transaction that ends on `COMMIT` only if its own checks pass,
  `ROLLBACK` otherwise; it is idempotent (running it twice changes nothing more).
- Results quoted in a ticket carry business identifiers only, never names, emails or phones.
