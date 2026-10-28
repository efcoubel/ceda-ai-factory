# Adapters

Each category has a `contract.md` (the operations the engine needs, their inputs and outputs) and
one file per tool. A tool file has always the same sections:

- **Status**: `tested` (used on a real project) or `draft` (written, not yet exercised).
- **Detect**: how the onboarding recognizes the tool on this machine or in the repos.
- **Profile config**: what goes in `profile.json` → `tools.<category>.config`. Never a secret.
- **Check**: what `/ai-factory:doctor` runs to prove the access works.
- **Operations**: how to do each contract operation with this tool.
- **Pitfalls**: what bit someone before.

`none.md` exists in every category where the engine can live without the tool: operations are
skipped and reported as skipped.

Adding a tool: copy the closest tool file, keep the sections, mark it `draft`, and open a pull
request. A file moves to `tested` once a real project ran the pilots on it for a week.
