# Module: python

**Summary:** Python with uv: a locked environment, ruff with correctness rules only, mypy in strict mode with no
unexplained escapes, pytest with slow tests and probes marked, import-linter for the boundaries. Also the rules for
helper scripts in other projects. Read by the core agents for their sections below.

## Rules

- **uv for everything** (core rule: `context.md`, "Tools"): `uv sync` for the environment, `uv run` to run anything
  in it, `uv add` for dependencies, `uvx` for tools used now and then. `uv.lock` is committed; checks run with
  `uv sync --frozen` so the lock is never changed silently. `.python-version` and `requires-python` pin the version.
- **Typed, strictly** (principle 2): mypy `strict`. `Any` in an annotation, a blanket `# type: ignore` or `# noqa`
  are errors; a needed suppression names its code and says why after it (`# type: ignore[attr-defined]  # stub
  lacks it`). Data from outside (JSON, files, requests) is validated at the boundary, not passed on as `Any` or `dict`.
- **Errors keep their cause**: `raise NewError(...) from err`; no bare `except`, no `except Exception: pass`
  (principle 5).
- **No blocking in async code**: no `time.sleep`, synchronous HTTP or file I/O in `async def`; tasks are kept
  (principle 3).
- **Time zones are explicit**: `datetime.now(tz=...)`, never naive datetimes in logic; time and randomness are
  passed in (a clock, a seeded `random.Random`) so tests are deterministic.
- **Validation never by `assert`**: `python -O` removes asserts.
- **`pathlib` for paths**, one way (principle 6).
- **Security defaults**: no `eval`/`exec`, no `shell=True`, `yaml.safe_load`, no `pickle` from outside, SQL with
  parameters, a timeout on every network call; tokens and keys from `secrets`, never `random`.
- **Tests with pytest**: plain functions and `assert`; fixtures for setup; `@pytest.mark.slow` for tests the quick
  check leaves out; `@pytest.mark.probe` for measurement harnesses, never in the suite (run with `-m probe` by the
  `measurer`). Warnings fail tests, so deprecations are found while they are warnings.
- **Untrusted data** (downloaded files, archives) is read by scripts run in isolated mode, `python -I`, from a
  folder of their own: Python imports from the script's folder and the current folder first.

### Helper scripts in other projects

A project in another stack may keep tools in Python (the scaffold's own `check_docs.py`, Blender scripts):

- **Standard library only** where possible, so they run with any Python 3.9+ and no environment.
- With dependencies: inline script metadata (PEP 723, a `# /// script` block naming them) and `uv run <script>.py`,
  so the script carries its own environment.
- The same rules as above; ruff runs on them with this module's configuration.

## Repository setup

Applied once by the bootstrap; the files are the project's afterwards.

- **`pyproject.toml`**: the tables of `docs/process/tools/python/pyproject.template.toml` merged in, with the
  project's name, Python version and package filled in, and one import-linter contract per boundary in "Rules the
  code keeps" (the template's example contract replaced or removed).
- **Layout**: the package in `src/<package>/`, tests in a `tests` folder beside it.
- **`uv sync`**, then commit `uv.lock` and `.python-version`.
- **`.gitignore`** lines:

  ```
  .venv/
  __pycache__/
  .pytest_cache/
  .mypy_cache/
  .ruff_cache/
  *.egg-info/
  ```

- **An existing codebase**: run ruff and mypy once. Findings that cannot be fixed now: ruff's `--add-noqa` writes a
  `# noqa` with the rule on each line (each one is then a visible item to remove, and `RUF100` flags them once
  fixed); mypy's strictness may start per module (`[[tool.mypy.overrides]]` with `strict = false` for the old ones,
  listed in `docs/HEALTH.md`, "Noticed"). Never `--fix` or `--unsafe-fixes` across the codebase without review.

## Checks

| Level | Command |
|---|---|
| Quick | `uv run ruff check <changed files>`, `uv run mypy <changed files>`, `uv run pytest -x -m "not slow and not probe" <test files>` |
| Full | `uv sync --frozen`, `uv run ruff check .`, `uv run mypy`, `uv run lint-imports`, `uv run pytest` |

- ruff never runs with `--fix` as a check: a check reports, it does not change code.
- pytest is quiet by default (`-q` in the configuration); its exit code decides.
- **Cognitive complexity** is a size trigger, reported, never failing a check (`code.md`, "Size triggers"):
  `uvx complexipy src --max-complexity-allowed 15 --failed --ignore-complexity` lists the functions over it.

## Diagnosing

- **One test, verbose**: `uv run pytest -vv -k "<name>"`; the last failures again: `uv run pytest --lf -x`.
- **A hang**: `python -X faulthandler` (or `faulthandler.dump_traceback_later`) prints every thread's stack;
  the `pytest-timeout` plugin turns a hung test into a failure with its stack.
- **Async problems**: `python -X dev` (or `PYTHONASYNCIODEBUG=1`) reports slow callbacks, never-awaited coroutines and
  unclosed resources.
- **Works here, not there**: compare `uv run python -VV` and `uv tree`; the lock should make them equal, so a
  difference points to something outside it (an environment variable, a system library, a path).

## Health

The tools for the core ledger's rows (`docs/HEALTH.md`), used by the `auditor`:

| Check | Tool |
|---|---|
| Dependencies | `uv tree --outdated`; known vulnerabilities with `uv export --format requirements-txt --no-hashes > tmp/requirements.txt` then `uvx pip-audit -r tmp/requirements.txt` |
| Dead code | `uvx vulture src --min-confidence 80` (lower confidence lists more and needs judging; public APIs and framework entry points are false positives to whitelist) |
| Static analysis | ruff and mypy counts; the number of `noqa` and `type: ignore` comments (they only shrink); complexipy's list |
| Tests | `uv run pytest --durations=10`: the slowest tests |

## Measuring

- **Where the time goes**: `uv run python -m cProfile -o tmp/profile.prof <script>` and a viewer (`snakeviz`), or the
  sampling profiler `pyinstrument` for a readable tree with little overhead.
- **Micro-benchmarks**: `timeit`, or `pytest-benchmark` in tests marked `probe`; repeated runs, the spread reported.
- **Memory**: `tracemalloc` snapshots before and after the workload, compared by line.

## Review

Beyond the principles, look for: mutable default arguments; `except` that hides the error or drops the cause;
`Any`, `cast()` or `dict[str, Any]` carrying data inward from the boundary; naive datetimes; blocking calls in async
code; validation by `assert`; string-built SQL or shell commands; network calls without a timeout; module-level state
that tests share; `os.path` where the code uses `pathlib`.

## Sources

Where the truth is for this stack, nearest first (`docs/process/research.md`). Read by everyone looking something
up, and by the `researcher`.

- **The version**: `uv run python -VV`, `uv tree` (every package and its version), `.python-version`.
- **The tool**: `uv <command> --help`, `uv run <tool> --help`; `uv run python -m pydoc <module>` for an installed
  module's documentation.
- **The installed code**: the package's source in the environment's `site-packages` folder inside `.venv`.
- **The documentation for that version**: [Python](https://docs.python.org/3/) (choose the version at the top),
  [ruff rules](https://docs.astral.sh/ruff/rules/), [mypy](https://mypy.readthedocs.io/),
  [pytest](https://docs.pytest.org/), [uv](https://docs.astral.sh/uv/); a package's documentation linked from its
  PyPI page.
- **Changes between versions**: Python's "What's New" per version; a package's changelog or releases.
