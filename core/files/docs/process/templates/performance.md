# Performance: <what is slow>

**Summary:** <What is slow, how slow, and the target.>

Status: draft
Mode: attended
Template: performance
Created: YYYY-MM-DD

## Goal

<The measure and the target, e.g. "startup under 2 s on the dev machine", "p95 request under 100 ms".>

## Context

<The budget in docs/WORKING.md; how it shows; the hot path suspected.>

## Open questions

<One per item: the question, then `Default:` the recommended answer. The user's answers go into the plan at approval;
empty once approved.>

## Steps

- [ ] 1. Measure
  - Do: a repeatable measurement (command, input, machine state, number of runs); a profile of where the time goes.
    The `measurer` (`docs/process/roles/measurer.md`) runs it, in its own worktree if needed.
  - Done when: the baseline and the profile are in Notes; the measurement can be rerun by command.
- [ ] 2. Change
  - Do: the change the profile points to, one at a time, measured after each. Behaviour unchanged.
  - Done when: the target is met, or Notes show each change's effect and why the next would not pay.
- [ ] 3. Keep it
  - Do: the budget in `docs/WORKING.md` updated; a benchmark or a test guarding the result where the stack allows.
  - Done when: a regression would be noticed.

## Stop conditions

- Meeting the target would need a design change or a new dependency (the user's decision).
- The measurement is too noisy to tell a change from noise: report, with what would make it steady.
- The same check fails three times after attempted fixes.

## Notes

## Outcome
