---
name: new-project
description: Starts a project from an empty folder with the user - frames the product (light by default, full on request), chooses the stack together, creates the repositories with the stack's official generator, the remote, branch protection and a minimal CI, sets up the ticketing tool and seeds the backlog with epics and ticket-sized sub-issues, then writes the ai-factory profile so the pilots can take over. Every outward creation waits for approval, batch by batch. Use for "/ai-factory:new-project", "start a new project", "bootstrap this project", "set up a project from scratch"; called by the onboarding when the folder holds no repository.
argument-hint: "[full]"
---

# /ai-factory:new-project

**Plugin root**: two directories above this skill's base directory. Read
`<plugin root>/core/architecture.md`, `core/profile-schema.md` and `core/autonomy.md` first.

Converse in the language chosen at onboarding step 0 (ask it the same way if this skill is called
directly). Write `vision.md` in the project's working language, code and repository files in the
commit language chosen in step 2.

The project root is the current folder. Keep progress in `.ai-factory/profile.json` →
`"onboarding": {"done": false, "path": "new-project", "phase": "<n>", "answers": {…}}` after each
phase, so a stop loses nothing.

## 1. Frame the product

Read what is already in the folder (notes, a README, sketches, a brief) and do not ask again what
it says. Then, with `AskUserQuestion` and open questions, settle:

**Light framing** (default, about ten questions):

- what the product does, in one sentence; for whom; which problem it solves;
- the first version (MVP): the three to seven things a user must be able to do;
- what is explicitly **not** in the first version;
- constraints: platforms, deadline, budget for hosting and services, data that is sensitive
  (health, payments, minors);
- how success will be seen (a number, a behaviour, a date).

**Full framing** (argument `full`, or the user's choice at the end of the light one): add personas
(two or three, with their context and goal), the main user journeys step by step, the success
criteria per journey, the risks (technical, legal, market) with a mitigation each, and the
assumptions to check first.

Write `vision.md` at the project root from `<plugin root>/templates/vision.md`. Show it, ask for
corrections, apply them.

## 2. Choose the stack together

From the framing, propose **two or three options**, never one. For each: the stack (front, back,
data, hosting, auth), why it fits this product, its monthly cost at MVP scale, its limits, and what
it would cost to leave it later. Recommend one and say why; the user decides.

Then settle, in one `AskUserQuestion` call:

- one repository or several (a mobile app and its backend often stay apart; a web app and its API
  can share one);
- the forge (GitHub, GitLab…), the account or organization, public or private;
- the commit language and format (default: English, conventional commits), the branch format
  (default: `<KEY>-<slug>`);
- the ticketing tool (`adapters/ticketing/`), and whether a chat tool is used.

## 3. Create the foundations

Local work first, free (`core/autonomy.md`):

1. For each repository: generate the skeleton **with the stack's official tool**
   (`flutter create`, `npm create vite@latest`, `composer create-project`, `rails new`,
   `cargo new`…), with the options agreed in step 2. Check the tool is installed; if not, give the
   install command and wait.
2. `git init -b main`, a `.gitignore` from the generator (or the stack's standard one), a
   `README.md` (what it is, how to run it), a `CLAUDE.md` with the conventions chosen, a minimal CI
   file (install, static analysis, unit tests) for the chosen forge.
3. Run the generator's own checks once (the analysis and the generated test) and commit:
   `chore: Bootstrap <repo> with <generator>`.

Then the **outward batch**, shown as one recap and created only after the user's go:

| Creation | How |
|---|---|
| Remote repository, visibility | forge adapter, `create_repo` |
| Push of `main` | `git push -u origin main` |
| Protection of `main` (no direct push, CI required) | forge adapter, `protect_branch` |
| Ticketing board, statuses, types | ticketing adapter, `setup` |

Anything that needs a console, a payment method or a legal acceptance (a cloud project, a store
account, a domain) is **not** created by the skill: it becomes a step-by-step task for the user in
the recap, and the profile records it as pending.

## 4. Seed the backlog

From the MVP list of `vision.md`:

- one **epic** per capability (title, the user value, the acceptance criteria at product level);
- under each, **sub-issues** sized for the chain: one repository, one reviewable change, clear
  acceptance criteria, typed (`task`, `feature`; a known defect of the skeleton is a `bug`);
- a first sub-issue per repository for the plumbing the others need (configuration, navigation,
  authentication skeleton), so the chain does not start with a feature that has no ground.

Show the backlog as a tree (epic → sub-issues, with type and one-line scope), let the user cut,
merge or reorder, then create it **as one outward batch** after their go (ticketing adapter,
`create` with `parent`). Record the created keys in `vision.md` under "Backlog".

## 5. Write the profile and hand over

Write `.ai-factory/` exactly as the onboarding's step 6 does, from what this skill decided (no
discovery needed: the skill knows the repos, commands, branches and tools it created), including
the onboarding's question block 7 (working while the user is away) and `tools.ticketing.config.key`
(`native` unless the user wants their own key format). Create the validation queue (onboarding
step 7) and run `/ai-factory:doctor`.

Close with: what was created and where (links), what remains for the user (the pending console
tasks), and how to start: the first plumbing ticket by hand with `/ai-factory:ticket <KEY>`, then
the dev pilot in a loop.
