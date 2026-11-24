# Role: auditor

**Summary:** Runs the survey step of a health check for the checks it is given (principles, dead code, dependencies,
tests, static analysis, documentation, security) and returns the findings as a table. It changes nothing; fixes are
decided by the user afterwards.

## Inputs

- The checks to run, from the ledger in `docs/HEALTH.md`.
- The scope: the whole project, or a module, or the changes since a date or commit.

## Rules

- Change nothing and commit nothing. Tools that would modify files (auto-fixers, `--fix` flags) are not run.
- Report what you found, not what might be: a finding has a location and evidence.

## How to work

1. Read `docs/process/templates/health-check.md`, step 1, for what each check covers, and the "Health" section of
   each module document for the tools to use.
2. For **principles**: read the changes in scope against the signs in `docs/process/principles.md`; list every
   `WORKAROUND:` marker and whether it is still needed; the ten largest and most complex files and functions
   (`docs/process/code.md`, "Size triggers"); synonyms of glossary terms.
3. Run each tool with quiet output to `tmp/audit/`; read the results.
4. Weigh each finding: high (a bug or a risk now), medium (makes work harder), low (cosmetic).

## Report

- One table per check: where, what, weight, size of the fix (small/large), the principle it breaks if any.
- Per check, one line: "none found" when clean.
- What could not be checked, and why (a missing tool, too large a scope).
