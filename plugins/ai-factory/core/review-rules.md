# Review rules

Used by `ticket-3-review` (a fresh agent reviewing our branch) and by `review-peers` (teammates'
MRs/PRs). The project adds its own rules in `repos.md` ("Conventions") and `learnings.md`.

## 1. Bugs first

An inverted condition, an unhandled null or empty case, a query whose result changes, a call broken
by a rename outside the diff's lines, a long migration on a large table, an error behaviour changed
without its callers following, a race between two writers, a time zone or locale assumption, a
resource opened and not closed.

## 2. The project's own rules

Every rule of the repositories' `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md` and linters, and the
"Conventions" of each repository in `.ai-factory/repos.md`. For design principles, only what shows
in the diff: a class taking a second responsibility, a dependency created inline instead of
injected, a condition on a type where a strategy already exists.

## 3. What reviewers often ask

- Would an existing service, helper or component have done the job?
- Code made dead by the change: a field, a method, a parameter, an import, a feature flag.
- The error path: what happens when an expected value is missing, and do callers handle it?
- Comments: any added comment that is not strictly needed (paraphrase, history, a docblock repeating
  a typed signature) goes; only a business rule or a trap the code cannot say stays.
- No opportunistic refactoring in a bug fix.
- User-facing changes: a wait shows a loader and disables its trigger, every action ends with a
  clear success or error message, a destructive action asks for confirmation, an empty list or
  missing value shows a text instead of a blank, colours keep their meaning and their contrast —
  using the components the repository already has.
- Security: no secret, credential or personal data in the diff; no user input concatenated into a
  query, a shell command or a prompt; no new endpoint without its access check.
- Nothing generated, dumped or binary committed by mistake.

## 4. The project's traps

The pitfalls listed in `repos.md` ("Conventions") and the lines of `learnings.md` that concern the
files of the diff.

## Severity

- **Blocking**: a bug, a project rule broken, a security flaw, a likely regression, an acceptance
  criterion not met.
- **To consider**: a real improvement that is debatable.
- A nitpick that brings almost nothing is not reported. A review with no finding is a valid result.
