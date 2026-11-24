# {{PROJECT_NAME}}: working rules

**Summary:** Rules and pointers for every person and AI tool working here. The details are in `docs/`; this file
stays under ~150 lines because it is loaded into every session.

> **Not bootstrapped yet?** If this file still contains `{{` placeholders, follow `docs/process/bootstrap.md` before
> anything else.

## What this is

{{One paragraph: what the project is, who it is for, and what state it is in.}}

## Who decides what

| Matter | Decided by |
|---|---|
| What the product does, how it looks and behaves | The user |
| What to work on next; approving plans | The user |
| Adding a dependency, changing the architecture or a public interface | Proposed by the agent, approved by the user |
| Pushing, releasing, deploying, anything outside this repository | The user |
| Code structure, naming, tests and refactors inside the task | The agent doing the work, said in its report |

Suggestions on anything are welcome, including on matters that are the user's to decide.

## Where things are

| Path | What |
|---|---|
| `docs/STATUS.md` | Now, next, open questions. Read first |
| `docs/HEALTH.md` | Code-health ledger and things noticed |
| `docs/README.md` | Map of the documentation |
| `docs/process/` | How work is done (owned by the scaffold; extend it here, not there) |
| `docs/process/roles/` | The agents (reviewer, check-runner, investigator, librarian, researcher, scribe, auditor, measurer, and the modules') |
| {{path}} | {{what}} |

A module with rules of its own has its own `AGENTS.md` (with a `CLAUDE.md` holding `@AGENTS.md` beside it).

## Commands

```sh
{{quick check: the fast checks to run while working}}
{{full check: everything, before calling work done}}
{{run: how to start the project}}
```

The rest (environment, setup, performance budgets and how to measure them) is in `docs/WORKING.md`.

## Principles

The code is the agent's: keeping it to these is part of every task. Rules and signs: `docs/process/principles.md`.

1. **Clean code**: the code says what it does, simply.
2. **Longevity**: the code stays correct as it changes.
3. **Scalability**: the code holds up as the data and the load grow.
4. **Anti-slop**: nothing is there without a reason.
5. **Diagnosability**: an error or a log line says what happened and where; failures can be reproduced.
6. **One vocabulary, one way**: one name per concept (`docs/GLOSSARY.md`), one path per task.
7. **KISS**: the simplest thing that works.
8. **Token care**: short documents, quiet output, read only what the task needs.
9. **Reachable context**: everything reachable from this file; nothing important only in a chat.

## How work is done

- **Sessions** start and end with a routine: `docs/process/session.md` (skills `start` and `wrap-up`).
- **Language**: every file (code, comments, docs, commit messages) in English.
- **Small tasks need no plan**; larger work gets one in `docs/plans/` (`docs/process/planning.md`). A plan runs
  unattended only when the user says so (`docs/process/unattended.md`).
- **Look it up rather than guess** (`docs/process/research.md`): the installed version, the tool's help, the docs
  for that version, the web, or a quick probe; say what is verified and what is assumed.
- **Recommend one option** and say why, rather than surveying many.
- **Stop and ask** when a decision is the user's (the table above), or when the work would grow beyond what was
  asked. Work that turns up on the way goes to `docs/HEALTH.md` ("Noticed") or a proposal, not silently into the
  change.
- **A refused action** is not worked around with another tool that reaches the same end. One retry in a simpler form
  is fine; then say what was needed and why.
- **Code**: `docs/process/code.md`. Check your diff against the principles before committing; tidy the files you
  touched (in its own commit); note anything wider in `docs/HEALTH.md`.
- **Verify**: the quick check while working, the full check before saying something is done. Never report done while
  a check fails; say what failed.
- **Git**: `docs/process/git.md`. Stage explicit paths, never `git add -A`; commit bodies say why; never revert or
  tidy changes you did not make; never push unless asked.
- **Documentation**: what goes where and how each document grows: `docs/process/documentation.md`.
- **The scaffold improves from projects**: a generic improvement found here (a process document that misled, a
  template bug, a missing tool fact) is proposed with the `scaffold-propose` skill; project rules stay here.
- **Context and tokens**: `docs/process/context.md`.
- **Tools: a CLI or a script before an MCP server.** MCP only for what no command can do, and say why
  (`docs/process/context.md`, "Tools").

## Modules

The scaffold modules this project uses, each with its rules. Kept by `scaffold.py`; do not edit between the markers.

<!-- scaffold:modules -->
<!-- /scaffold:modules -->

## Rules the code keeps

{{The architecture's boundaries and invariants, one line each, e.g. "core/ imports nothing from ui/". Name the tool
that checks each one, if any.}}

## Project rules

{{Sections that extend a process document carry its name, e.g. "## Review" adds to docs/process/review.md. None yet.}}
