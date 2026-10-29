---
name: ticket-2-code
description: Step of the ai-factory chain that implements an approved plan - code, unit tests, static analysis as it goes, local commits in the repository's own format on the ticket's branch - or fixes the blocking findings of the review. Never pushes. Use for "/ai-factory:ticket-2-code <KEY>", "implement the plan", "code the ticket", "fix the review findings".
argument-hint: "<KEY> [chain | pilot [dry]]"
---

# /ai-factory:ticket-2-code

**Plugin root**: two directories above this skill's base directory. Read `core/chain.md` first.

## 1. Pick up the context

Read `state.md` and `plan.md`. No approved plan (`planned` or `planned (auto)`): stop and propose
`ticket-1-frame` — an unframed ticket is not coded.

If `review.md` holds blocking findings not yet handled, this is a fixing round: handle those, and
nothing else.

Check every repository of the plan is on the ticket's branch.

## 2. Implement

- Follow the plan's steps, in order. A deviation (another approach, one more repository) goes in
  `plan.md` under "Decisions", with its reason. A deviation that changes the scope or an acceptance
  criterion stops the step: ask in manual mode, `blocked:` in pilot mode. For a plan approved by
  the pilot itself, a deviation that breaks one of its low-risk criteria also stops it.
- Before writing a service, a function, a constant or a component: look for the existing one.
- Write the unit tests of what you change, in the style of the neighbouring tests. For a bug, the
  test that reproduces it comes first and fails before the fix.
- After each change, run the repository's static analysis (and the formatter, if it has one) on the
  changed files (`repos.md`). Fix before moving on.
- No refactoring outside the plan, no comment that paraphrases the code.
- A user-facing change follows the user-facing rules of `core/review-rules.md`, with the
  components the repository already has.

## 3. Commit

Local commits on the ticket's branch are free: one commit per intent, not per file.

- The repository's format (`repos[].commit_format`), looking like `repos[].commit_examples`, in
  `repos[].commit_language`, with the ticket key where the format puts it.
- Add the commit trailers the session's instructions require, unless the repository's history or
  rules say otherwise.
- Never a filled `.env`, a credential, a dump or a build artefact: check `git status --short` and
  the staged diff before each commit.
- No push: it belongs to `ticket-5-ship`, after approval.

## 4. End

Run the unit tests of the changed code (`repos.md`). Set `state.md` to `coded`, with a journal line
saying what was done and what departs from the plan.

Alone, propose `ticket-3-review`; in a chain, return.
