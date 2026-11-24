# Health

**Summary:** The ledger of periodic code-health checks and the list of things noticed but not yet fixed. Agents
read it at the start of a session and bring up what is overdue; they add to "Noticed" at wrap-up. How:
`process/health.md`.

## Ledger

<!-- Every: a period, or a trigger ("after each feature plan"). Last done: a date and a link to the plan or log
entry, or "never". Tune the list to the project; remove what does not apply and say why under the table. -->

| Check | What it covers | Every | Last done |
|---|---|---|---|
| Principles | Recent changes against `process/principles.md`: signs of each; `WORKAROUND:` markers still needed | 1 month | never |
| Dead code | Unused files, exports, dependencies | 1 month | never |
| Dependencies | Outdated and vulnerable packages, minor and patch updates | 1 month | never |
| Tests | Slow, flaky or skipped tests; coverage of what changed lately | 1 month | never |
| Static analysis | Warnings count, rules still fitting the code | 2 months | never |
| Documentation | `check_docs.py --strict`; docs against the code | 1 month | never |
| Performance | The budgets in WORKING.md, measured | 2 months | never |
| Security | Secrets in the tree, risky inputs, permissions | 3 months | never |

## Noticed

<!-- One line each: date, where, what, why it matters. Newest at the bottom. Remove a line when it is fixed (the fix's
commit says so) or turned into a plan (link the plan). Over ~30 lines: propose a health-check plan. -->

- None yet.
