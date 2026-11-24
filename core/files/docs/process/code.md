# Code

**Summary:** How the principles (`principles.md`) are applied to code day to day: checking your own change before
committing, tidying, size triggers, performance work and static analysis. The stack's tools are named in
`docs/WORKING.md`; a project's own rules go in its `AGENTS.md`.

## Before every commit

Read your own diff once against the principles, briefly:

1. **Clean**: names, sizes, literals named once, no duplication introduced, comments true.
2. **Longevity**: boundaries kept, no swallowed errors, no unexplained type escapes, workarounds marked and listed.
3. **Scalability**: nothing blocking or unbounded added on a hot path.
4. **Anti-slop**: nothing without a reason: no impossible-case handling, speculative options, restating comments,
   leftovers; tests that would fail if the behaviour broke.
5. **Diagnosability**: new errors and log lines say what and where.
6. **One way**: the existing pattern, helper and names were used; new concepts are in `docs/GLOSSARY.md`.
7. **KISS**: the simplest version that works.

Fix what you find before committing; do not list it as a finding of your own work.

## Tidying

- **The files you touched**: tidy them as part of the work, in a separate commit. Behaviour unchanged; the checks
  pass before and after.
- **Beyond the files you touched**: do not fix it; add it to `docs/HEALTH.md`, "Noticed", naming the principle.
- **At the end of a plan that changed code**: review the plan's whole diff with fresh eyes against the principles
  and simplify what it introduced. If nothing is worth changing, say so with the reason.

## Size triggers

Sizes are **triggers for a second look, not limits**. Past one, look for a real seam: a separate responsibility,
step or case. If there is one, split there; if there is none, leave the code as it is and say why in the commit.
**Never split only to get under a number**: a helper called once, with many parameters and a name that restates its
body, is slop (principles 4 and 7), not clean code.

Defaults, adjusted per project in `docs/WORKING.md`, "Size triggers":

| What | Trigger | Notes |
|---|---|---|
| Function or method | ~50 lines, or more than 3 levels of nesting | Nesting is the stronger sign |
| Cognitive complexity | ~15 (warning in the linter); ~25 fails the check | The one size measure enforced by a tool; the stack modules set it up |
| Source file | ~500 lines | Tests, generated and data files are exempt |
| A module's public surface | What its callers need | Narrow it |

A file past a trigger that this change did not create goes to "Noticed" only when it is hard to work in; one this
change grows past a trigger is looked at now. The monthly Principles audit reports the ten largest and most complex
outliers, not every file past a trigger.

## Performance

- Measure before optimising, the same way before and after, and put the numbers in the commit message.
- Budgets for the hot paths are in `docs/WORKING.md`, "Performance budgets"; a change that touches a hot path says
  so and is measured against its budget.
- Larger work uses the `performance` plan template.

## Static analysis

- Correctness rules, not style: unhandled promises and errors, exhaustive switches, nullability, unused code, type
  escapes (principle 2), layering (`AGENTS.md`, "Rules the code keeps").
- A finding is fixed, not silenced. A rule that does not fit the code is changed in the configuration, with the
  reason, as its own commit.
- A project without static analysis gets it proposed (the `health-check` template); the stack modules name the
  tools.
