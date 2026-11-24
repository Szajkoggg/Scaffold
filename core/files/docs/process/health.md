# Health

**Summary:** Code health is kept by two things in `docs/HEALTH.md`: a ledger of periodic checks, which agents bring
up when overdue, and a Noticed list, which agents add to at wrap-up. The user decides when to act on either. Skill:
`health`.

## Bringing it up

- **At the start of a session** (`session.md`): an overdue check, or a Noticed list past ~30 lines, is mentioned in
  one line with a proposal ("Dependencies last reviewed 3 months ago; shall I run a health-check plan for them?").
  Once per session, not again.
- **When a plan is finished**: if the plan touched an area with Noticed items, propose fixing those that are cheap.
- **When a limit is passed** (a file over its size limit, a slow test past its budget): add it to Noticed and
  mention it once.

The user may decline; then nothing more is said about it in that session.

## Running checks

- A check is run as a plan from `templates/health-check.md`, choosing which checks it covers. Small ones (a single
  dead-code sweep in one module) can be done without a plan when the user asks.
- A check first **surveys** and reports findings (the `auditor`, `roles/auditor.md`, does the survey); fixes follow only for what the user approves, except clear,
  mechanical fixes the plan names in advance.
- After a check, update its "Last done" with the date and a link to the plan.

## Noticed

- One line per item: date, where (file or module), what, why it matters.
- Remove the line when it is fixed (the commit names it), or replace it with a link when it becomes a plan.
- Do not add what is already in an active plan.
