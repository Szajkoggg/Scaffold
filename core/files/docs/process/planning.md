# Planning

**Summary:** Larger work gets a plan: one markdown file in `docs/plans/` with a goal, steps with "done when", and
stop conditions. Usually worked through together in chat; run unattended only when the user says so. Skill: `plan`.

## When a plan is needed

- **No plan**: a change that fits in one request and one commit or a few.
- **A plan**: work that spans sessions, several commits with checks between them, a decision the user should
  approve up front, or anything to be run unattended.

When unsure, ask in one line: "This is about N steps; shall I write a plan?"

## Writing one

1. Pick the closest template in `templates/` (feature, bugfix, refactor, spike, performance, health-check, and
   those the modules add, e.g. release); copy it to `docs/plans/YYYY-MM-DD-<slug>.md` and list it in
   `docs/plans/README.md`.
2. Read enough of the code to make the steps real: name files and modules, not intentions.
3. Steps are **small**: each ends with the checks passing and a commit, and could be reviewed on its own.
4. Each step has **Done when**: criteria someone else could check (a test, a measurement, a behaviour).
5. **Stop conditions** say when to stop and ask instead of going on. Every plan keeps the standard ones.
6. Recommend one approach; list rejected alternatives in one line each, with why.
7. **Open questions**: what you cannot settle goes there, each with `Default:` your recommended answer, so the user
   answers only where they disagree. A matter that is the user's by "Who decides what" (`AGENTS.md`) is asked
   outright, never left to a default.
8. **Length**: a plan is about 50-200 lines; past ~300, split it into plans that each deliver something on their own.
9. Show the plan to the user, offering a plan review if it is a larger one (`review.md`, "Reviewing a plan"). It is
   approved when the user says so; `Status:` becomes `approved`. Approval accepts the defaults the user did not
   answer: write every answer into the steps or "Context" (marked "decided by the user") and empty "Open
   questions".

## The format

```markdown
# <Title>

**Summary:** <one or two lines: what and why>

Status: draft | approved | in progress | stopped | done | abandoned
Mode: attended | unattended
Template: <name>
Created: YYYY-MM-DD

## Goal
<What is true when this is done, from the user's point of view.>

## Context
<Links to design topics, ideas, issues; the facts the steps rely on.>

## Open questions
- <Question?> Default: <the recommended answer>

## Steps
- [ ] 1. <Title>
  - Do: <what, naming files and modules>
  - Done when: <checkable criteria>
- [ ] 2. …

## Stop conditions
- A decision that belongs to the user comes up (AGENTS.md, "Who decides what").
- The work would grow beyond the plan.
- The same check fails three times after attempted fixes.
- A file to commit has changes this plan did not make.
- <plan-specific ones>

## Notes
<Dated notes while working: deviations, findings, decisions made on the way.>

## Outcome
<Filled in when done or abandoned: what was delivered, what differs from the plan, what follows.>
```

## Working through a plan

- Before each step, reread its "Done when" and the stop conditions.
- Tick the step and add a note when it differs from the plan; commit per step.
- In attended mode, report after each step in a line or two and continue unless the user stops you, or the step
  ended at a point the user should look at (a visible change, a decision).
- The last step of every plan that changed code is a tidy-up of what the plan changed (`code.md`, "Tidying").
