# Health check: <checks chosen>

**Summary:** A survey of <checks> from the ledger in docs/HEALTH.md, then the fixes the user approves.

Status: draft
Mode: attended
Template: health-check
Created: YYYY-MM-DD

## Goal

Findings for each chosen check, with weight and size of fix; the approved fixes made; the ledger updated.

## Context

Chosen checks (delete the rest): principles, dead code, dependencies, tests, static analysis, documentation,
performance, security. Items from "Noticed" in docs/HEALTH.md that belong here: <list>.

## Open questions

<One per item: the question, then `Default:` the recommended answer. The user's answers go into the plan at approval;
empty once approved.>

## Steps

- [ ] 1. Survey
  - Do: for each chosen check, with the project's tool where there is one:
    - **Principles**: the code changed since the last audit (`git log` since its date), read against the signs in
      `docs/process/principles.md`; every `WORKAROUND:` marker, still needed or not; the ten largest and most
      complex files and functions (`code.md`, "Size triggers");
      synonyms of glossary terms in code and docs.
    - **Dead code**: unused files, exports, dependencies.
    - **Dependencies**: outdated (minor/patch vs major), known vulnerabilities, unused.
    - **Tests**: slowest, flaky, skipped; recent changes without tests.
    - **Static analysis**: warning count, rules that no longer fit; if none is set up, propose a setup.
    - **Documentation**: docs against the code (commands, paths, formats); files past their limit
      (`documentation.md`, "Growth rules").
    - **Performance**: the budgets in docs/WORKING.md, measured.
    - **Security**: secrets in the tree, risky input handling, over-broad permissions.
    Change nothing.
  - Done when: each finding listed in Notes with where, weight (high/medium/low) and fix size (small/large); or "none".
- [ ] 2. Agree the fixes
  - Do: show the findings with a recommendation of which to fix now, which to plan, which to leave.
  - Done when: the user has chosen.
- [ ] 3. Fix
  - Do: the chosen fixes, one commit each, checks passing. Large ones become their own plans.
  - Done when: done or planned; the rest in "Noticed".
- [ ] 4. Update the ledger
  - Do: "Last done" for each check run, with a link to this plan.
  - Done when: docs/HEALTH.md is current.

## Stop conditions

- A fix would change behaviour or a public interface (the user's decision).
- A dependency update needs a major version change: plan it separately.
- The same check fails three times after attempted fixes.

## Notes

## Outcome
