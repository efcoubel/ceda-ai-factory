---
name: ticket-4-test
description: Step of the ai-factory chain that verifies the ticket's branch - the repository's static analysis, unit tests and lint, then the changed screens or flows run for real (browser, emulator, command) when that can be done unattended, and the acceptance criteria covered one by one - then writes what the branch changes, the test procedure for the tester and the deployment notes. Use for "/ai-factory:ticket-4-test <KEY>", "test the branch", "write the test procedure", "explain my branch", "what needs doing at deployment".
argument-hint: "<KEY> [chain | pilot [dry]]"
---

# /ai-factory:ticket-4-test

**Plugin root**: two directories above this skill's base directory. Read `core/chain.md` first.

## 1. Automated checks

Read `state.md`, `plan.md`, `review.md`. For each repository of the ticket, run the commands of
`repos.md`: static analysis, unit tests (those of the changed code, then the whole suite if it is
reasonable), lint, build if cheap, end-to-end tests if `repos.md` has them (`core/chain.md`,
"Long commands"). In pilot mode, only those marked `unattended: yes`. A command not run again since
the last commit that touches what it covers is said in `test.md`, with why.

A failure clearly due to the branch is fixed on the spot with a local commit; a fix beyond a few
lines goes back through `ticket-3-review`. A pre-existing failure (it also fails on
`origin/<default>`) is reported, not fixed.

For each acceptance criterion of `plan.md`: which test covers it (automated, or a step played for
real below), or why none can.

## 2. Run it for real

When the branch changes something a user sees or triggers, play the test procedure (section 4,
write it first) on the local environment of `environments.md`:

- **web**: with the browser tools of the session, if any. Compare each screen to the expected
  result; collect console errors and failed network calls. Set the window to a fixed size first,
  so screenshot coordinates stay the same. Two users at once: two origins (`localhost` and
  `127.0.0.1`) keep two separate sessions in one browser;
- **Flutter web** draws on a canvas: the page tools see nothing until the accessibility tree is
  on (click the hidden `flt-semantics-placeholder` element, or start the app with semantics
  enabled). A download may stop the page from repainting in the session's browser: what follows a
  download is checked again after a reload, or left for the tester;
- **mobile**: integration tests on an emulator or simulator (`repos.md`), only if marked
  `unattended: yes` or the user is in the conversation; the backend on its emulator
  (`adapters/database/<adapter>.md`), never a production project;
- **no interface** (job, command, consumer, function): run it locally, or its test harness.

- **Logins**: you have no passwords. In manual mode, ask the user to log in where needed, then go
  on; in pilot mode, the steps that need a login stay for the user.
- **Shared data**: if the local environment points to data other people use (`environments.md`),
  anything that writes there is listed and waits for the user's go; read-only steps come first;
  what you created is put back.
- A gap due to the branch is fixed like a failed check (section 1). A step impossible locally
  (missing data, an external service, a real device) is said, with why: it stays for the tester.

## 3. What the branch changes

Read the code around the diff (callers, callees) and write, for a developer who did not write each
line:

- in one sentence, what the branch does as seen from the application;
- the path from the trigger (screen, route, command, event, schedule) to the final effect (data,
  outgoing call, notification, file), marking where the branch steps in and which repository calls
  which;
- what it touches beyond the ticket: other callers, existing data, error behaviour, a counterpart
  repository not changed;
- what reading the code cannot confirm (real behaviour in staging, volumes, configuration).

## 4. Test procedure

The tester is the person named in `workflow.md` (a product owner, a client, the user themselves).
Write for them, in the working language, as a user manual:

- **Describe only what the code really does.** Each expected result traces back to a line of the
  diff; a procedure that describes the ticket's wish instead sends the tester after something that
  does not exist.
- **As short as possible, missing nothing.** One step groups the actions of one screen; an expected
  result fits on one line; the obvious (logging in works, a page opens) is not written.
- Labels shown on screen in straight quotes; never a class, table, field or constant name, nor a
  local URL: use the staging URL of `environments.md`.
- What the tester needs to replay it (which account, in which state, **which build** and where to
  get it) is in the first step. When no build reaches testers yet (`repos[].staging` is `none` or
  not in place), the first step says how the tester runs the branch. An account in a given state
  is looked up in non-production data (database adapter); its business identifier goes in the
  procedure, the query that found it in `test-data.md`. Accounts from a seed: `test-data.md` names
  the seed file and the accounts used, no query.
- Steps truly out of the tester's reach (a command to run, a date to simulate) start with "A
  developer …".
- Format for where it will be pasted (`workflow.md`, "Transitions": a ticketing field, a comment, a
  PR description). Plain text by default:

```
STEPS
1. …

EXPECTED
1. … (same numbering as the steps)

NON-REGRESSION
- …

EDGE CASES
- …
```

## 5. Deployment notes

What the person deploying must do beyond the standard deployment, deduced from the diff: a one-off
command, a cache purge, an environment variable or secret to add, data to fix by hand, a store
submission. Nothing if the diff needs nothing: do not invent an action to fill the field. Never
what the CI already does (`repos.md`). A long migration on a large table goes to `test.md` as a
warning for the user, not here.

## 6. End

Write everything in `test.md`: raw results of the checks (and what did not run, and why), the real
run (steps played, results, gaps, steps not played and why), criteria coverage, then sections 3 to
5. Set `state.md` to `tested`.

Alone, present it all and propose `ticket-5-ship`; in a chain, return.
