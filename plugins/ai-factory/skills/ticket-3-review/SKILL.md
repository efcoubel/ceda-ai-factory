---
name: ticket-3-review
description: Step of the ai-factory chain where a fresh agent, without the author's context, reviews the ticket's branch - bugs, the project's rules, what reviewers usually ask, the acceptance criteria - and the findings are checked and recorded in the ticket folder; blocking ones send the ticket back to coding. Use for "/ai-factory:ticket-3-review <KEY>", "review my branch", "is it ready for the MR", "review before pushing".
argument-hint: "<KEY> [chain | pilot [dry]]"
---

# /ai-factory:ticket-3-review

**Plugin root**: two directories above this skill's base directory. Read `core/chain.md` first.

The agent that wrote the code does not review it: it would defend its choices. The review goes to
a subagent that sees only the diff, the plan and the rules. On a solo project, this review is the
one that counts before shipping (`workflow.md`, "Review rule").

## 1. Prepare

Read `state.md` and `plan.md`. List the repositories carrying the ticket's branch, each with its
default branch.

## 2. Launch the reviewer

`Agent` tool, `subagent_type: "general-purpose"`, **never `fork`**: a fork would inherit the
author's context. One reviewer for the whole ticket: a bug often hides between two repositories.

Its prompt stands alone and holds:

- the ticket folder's path (read `plan.md`, and `review.md` if it exists: do not raise again a
  finding already set aside);
- the repositories and their default branches, with the instruction to read
  `git diff origin/<default>...HEAD` and uncommitted changes, then **every changed file in full**;
- the rules: `<plugin root>/core/review-rules.md`, the repositories' `CLAUDE.md` and linters'
  config, `.ai-factory/repos.md` ("Conventions") and `.ai-factory/learnings.md`;
- the instruction to check every acceptance criterion of the plan against the code;
- the instruction to verify before asserting (callers, an existing helper), to modify nothing, and
  not to re-open a decision recorded in `plan.md`;
- the answer format: a table `Severity | File:line | Finding | Evidence | Proposed fix`, then the
  acceptance criteria, each "covered" or "not covered: why".

## 3. Sort and record

Check each finding against the code: drop those whose evidence does not hold, saying so. Findings
that only matter for a topic the plan explicitly excluded go under "Watch out" in `plan.md`, never
into a fix. Append to `review.md` a "Round N" block with the table kept and the outcome of each
finding.

## 4. Next

- **No blocking finding**: set `state.md` to `reviewed`. "To consider" findings stay in `review.md`
  and are listed at shipping.
- **Blocking findings**: in a chain, the next step is `ticket-2-code` for a fixing round, then a new
  review. On the third round that still finds blocking issues, stop the loop: something does not
  converge (`blocked:` in pilot mode, explained to the user otherwise).
- Alone: present the findings and propose `ticket-2-code` to fix them.
