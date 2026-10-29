# Cloud Firestore (Firebase)

**Status**: draft.

## Detect

`firebase.json`, `.firebaserc`, `pubspec.yaml` with `cloud_firestore`, or `firebase-admin` in
dependencies. The `firebase` CLI (`firebase projects:list`). A seed script or an emulator export in
the repository (`*seed*`, `emulator-data/`, `firestore-export/`).

## Profile config

```json
{
  "projects": {
    "local": "emulator",
    "dev": "<firebase project id>",
    "staging": "<firebase project id>",
    "production": "<firebase project id>"
  },
  "production_environments": ["production"],
  "access": "firebase-cli",
  "emulator_project": "demo-<name>",
  "emulator_seed": "<path to a seed script or an emulator export>"
}
```

| Field | Values |
|---|---|
| `access` | `firebase-cli` (the CLI picks the project or runs the emulator; reads go through a small Admin SDK script), `firebase-mcp` (the Firebase MCP server's Firestore tools) |
| `emulator_project` | the project id the emulator runs under. A `demo-` prefix keeps the emulator from ever reaching a real project |
| `emulator_seed` | how the emulator gets data: a script to run against it, or an export directory (`--import`) |

## Check

- `firebase projects:list` succeeds and lists every non-production project of `projects`.
- The emulator starts with the seed and one read returns documents:
  `firebase emulators:exec --project <emulator_project> --only firestore "<seed command> && <read script>"`.
- Every environment in `production_environments` is refused by the read script (it exits before
  connecting when asked for one).

## Operations

The Firebase CLI starts the emulator and selects projects, but has no command that reads
documents: reads go through a short Node script with `firebase-admin`, kept in the ticket folder.

- `query`:
  - **emulator** (the default for diagnosis): `firebase emulators:exec --project <emulator_project> --only firestore "<seed> && node read.mjs"`;
    the script sees `FIRESTORE_EMULATOR_HOST` and never reaches the cloud;
  - **a non-production project**: `GOOGLE_CLOUD_PROJECT=<project id> node read.mjs` with
    Application Default Credentials (`gcloud auth application-default login`, done once by the
    user). The script refuses any project id listed for a production environment.
  - Firestore has no query language: the script states the collection, the `where`, the order and
    the limit, and prints JSON.
- `export`: the same script writes CSV in the ticket folder.
- `dry_check`: a script that lists the documents a change would touch, then writes nothing.
- With `access: firebase-mcp`: the MCP server's Firestore read tools, on the emulator or a
  non-production project only.

## Pitfalls

- The emulator holds only what the seed puts in it: a defect that depends on real data cannot be
  reproduced there. Say so, and diagnose on the `dev` or `staging` project if it holds realistic
  data.
- Many solo Firebase apps have **only** a production project. Then there is no copy to diagnose
  on: the database category stays `none` for diagnosis, or the onboarding proposes the emulator
  with a seed.
