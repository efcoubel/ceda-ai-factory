# Cloud Firestore (Firebase)

**Status**: draft.

## Detect

`firebase.json`, `.firebaserc`, `pubspec.yaml` with `cloud_firestore`, or `firebase-admin` in
dependencies. The `firebase` CLI (`firebase projects:list`).

## Profile config

`{"projects": {"local": "emulator", "staging": "<firebase project id>", "production": "<firebase project id>"}, "access": "firebase-mcp", "emulator_seed": "<path to an export, if any>"}`

## Check

List collections on the non-production project (or the emulator); confirm the production project is
recorded as production, so the adapter refuses it.

## Operations

- `query`: on the emulator or a non-production project only, through the Firebase MCP server
  (`firebase mcp`, Firestore read tools) or the Admin SDK in a throwaway script with read-only
  credentials. Firestore has no query language: write the filter (collection, where, order, limit)
  in the ticket folder.
- `export`: the same read, written to CSV.
- `dry_check`: a script that lists the documents a change would touch, then writes nothing.

## Pitfalls

- Many solo Firebase apps have **only** a production project. Then there is no copy to diagnose
  on: the database category stays `none` for diagnosis, or the onboarding proposes the emulator
  with a seed export.
