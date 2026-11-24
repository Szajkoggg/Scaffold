# Testing

**Summary:** Two levels of checks (quick while working, full before done), tests that pin behaviour rather than
implementation, and output kept short.

## Levels

- **Quick**: the checks of what changed (the tests of the touched files, the type check, the linter). Run while
  working and before each commit.
- **Full**: everything. Run before saying work is done, and at the end of every plan step. Long runs go in the
  background.
- Both commands are in `AGENTS.md`, "Commands"; details in `docs/WORKING.md`.
- Runs whose output would be long go to the `check-runner` (`roles/check-runner.md`), which returns the verdict
  only; a failure that is not obvious goes to the `investigator` (`roles/investigator.md`).

## Tests

- New behaviour gets a test; a bug fix starts with a test that fails because of the bug.
- Tests pin **behaviour**, not implementation: a refactor should not need them changed.
- Tests are deterministic: no real network, clock or randomness without a seed; no calls to AI models.
- A flaky test is a bug: note it in `docs/HEALTH.md` and do not retry it until it passes.
- A slow test is a cost every session pays: note it when it is past the budget in `docs/WORKING.md`. Slow tests are
  marked (a category or tag) so the quick level can leave them out and the full level runs them.
- **No wall-clock assertions in unit tests** ("finishes in under 50 ms"): they fail on a busy machine and get
  skipped, which hides them. Timings belong to the `measurer` and benchmarks.
- **Golden files** (a stored output a test compares against) are allowed for deterministic output: the update is an
  explicit mode (a flag or an environment variable), never automatic; the commit that updates them says what changed
  and how much; values that are floating-point compare on one platform or with a tolerance.

## Reporting

- Say what was run and the result ("full check: 412 passed"), never "tests pass" without having run them.
- A failure that is not yours: say so with the evidence (it fails on the base commit too), do not hide it.
- Check output stays short: failures only on screen, full logs in `tmp/`. If a check prints too much, propose making
  it quieter.
