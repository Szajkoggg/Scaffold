# Fix: <the bug, as it shows>

**Summary:** <What goes wrong, where, since when if known.>

Status: draft
Mode: attended
Template: bugfix
Created: YYYY-MM-DD

## Goal

<The correct behaviour, and a test that keeps it.>

## Context

<How it shows: input, steps, environment, error output. The area where it shows.>

## Steps

- [ ] 1. Reproduce and find the cause
  - Do: a test that fails because of the bug, and only because of it. Find the cause; do not fix yet.
    The `investigator` (`docs/process/roles/investigator.md`) can do this step in its own context.
  - Done when: the failing test exists; the cause is named in Notes with the code and the evidence.
- [ ] 2. Fix
  - Do: the smallest change that removes the cause. Look for the same mistake elsewhere; fix it only where it is the
    same bug, note the rest in `docs/HEALTH.md`.
  - Done when: the test of step 1 passes; the full check passes; Notes say what else was checked.
- [ ] 3. Record
  - Do: a log entry if the cause teaches something; a gotcha if it was a trap.
  - Done when: written, or Notes say why not needed.

## Stop conditions

- The fix would change behaviour beyond the bug (the user's decision).
- The cause lies outside the area and fixing it would change something else.
- The same check fails three times after attempted fixes.
- A file to commit has changes this plan did not make.

## Notes

## Outcome
