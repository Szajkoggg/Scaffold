# Refactor: <target>

**Summary:** <What is restructured, and what will be better afterwards.>

Status: draft
Mode: attended
Template: refactor
Created: YYYY-MM-DD

## Goal

<The structure afterwards, and the measure of better: fewer lines, less duplication, a boundary kept, a file split.>
Behaviour stays exactly as it is.

## Context

<The code involved; who depends on it; why now.>

## Steps

- [ ] 1. Pin the behaviour
  - Do: tests for the behaviour of <target> where existing tests leave it open, especially where code will move.
  - Done when: new tests pass on the code as it is now; Notes say what they cover.
- [ ] 2. Restructure
  - Do: small commits, each with the checks passing. The tests of step 1 stay untouched.
  - Done when: the tests of step 1 pass unchanged; the full check passes; Notes give the measure from the Goal,
    before and after.
- [ ] 3. Update the documentation
  - Do: design topic, `AGENTS.md` "Where things are" or module `AGENTS.md` if paths or boundaries moved.
  - Done when: no document names a path or structure that no longer exists.

## Stop conditions

- Keeping behaviour unchanged turns out impossible (a bug the refactor would fix, a behaviour others rely on).
- A public interface would change (the user's decision).
- The same check fails three times after attempted fixes.
- A file to commit has changes this plan did not make.

## Notes

## Outcome
