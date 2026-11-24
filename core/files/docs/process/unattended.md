# Unattended runs

**Summary:** A plan the user has approved with `Mode: unattended` runs step after step without asking in between,
stops at a stop condition, and leaves a report the user can read when back.

## Before starting

- The plan's `Status` is `approved` and `Mode` is `unattended`, set by the user. Never switch a plan to unattended
  yourself.
- Every step has checkable "Done when" criteria; the stop conditions are written down. If not, ask now, not later.
- The working tree is clean, or the user has said what to do with what is there.

## While running

- Steps run in order, each finished properly (checks, commit, tick, note) before the next.
- **Nothing waits for a human prompt.** When a decision would be needed, it is a stop condition: stop and report.
- No pushing, no installs of new dependencies, no changes outside the repository, unless the plan says so.
- Long checks run in the background; nothing is skipped to save time.

## Stopping

On a stop condition, or when the plan is done:

1. Leave the tree clean: commit finished work; unfinished work goes on a `wip/<plan-slug>` branch with a note, never
   left uncommitted.
2. Set `Status` to `stopped` or `done` and write the reason or the outcome in the plan.
3. Write the report at the end of the plan's Notes and in the final message:
   - what was done (steps, commits);
   - how it was verified;
   - why it stopped, and the question for the user with options and a recommendation;
   - what comes next.
4. Wrap up (`session.md`).
