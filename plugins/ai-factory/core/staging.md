# Staging: putting a change in front of testers

What "staging" means differs per repository, so `repos[].staging` in `profile.json` says it:

```json
"staging": { "kind": "branch", "branch": "staging" }
"staging": { "kind": "release", "how": "firebase appdistribution:distribute build/app/outputs/flutter-apk/app-release.apk --app <app id> --groups testers", "build": "flutter build apk --release --flavor staging", "target": "Firebase App Distribution, group testers", "unattended": false }
"staging": { "kind": "deploy", "how": "firebase deploy --only functions,firestore:rules --project lima-staging-ec", "target": "lima-staging-ec", "unattended": false }
"staging": { "kind": "none" }
```

| Kind | What `ticket-7-staging` does, after approval |
|---|---|
| `branch` | Merges the ticket's branch into the staging branch in a temporary worktree (never in the user's working tree), pushes it, removes the worktree. The CI deploys it |
| `release` | Builds from the ticket's branch with `build`, then distributes with `how` to the testers |
| `deploy` | Deploys the ticket's branch to the staging environment with `how` |
| `none` | Nothing: the change is tested by the user from the MR/PR or after the merge into the default branch |

Rules:

- Staging is always a queued action (`core/autonomy.md`): it reaches testers or a shared
  environment. `unattended: false` (signing keys, a store login, a device) makes it a `human_task`
  with the exact commands instead.
- The target is never production. A `deploy` or `release` whose project, environment or channel the
  profile marks as production is refused.
- Merging into the **default branch** is not staging: it stays with the user (protected branch, the
  hook blocks it). After staging, the chain gives the user the merge command or link.
