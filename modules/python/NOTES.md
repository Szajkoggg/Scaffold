# python: notes for the module

**Summary:** Written from current practice (no Python project on the machine to learn from); its template was tested
with planted violations. The findings and the open points.

Not delivered to projects.

## Tested (2026-11-24)

With uv 0.13.4, ruff 0.17.6, mypy 2.4.1, pytest, import-linter 2.17, complexipy 9.0.0, vulture 2.16, Python 3.12:

- ruff with the template's selection, on a file with planted problems: mutable default (B006), raise without from
  (B904), shell=True (S602, S607), bare except and try-except-pass (E722, S110), `Any` (ANN401), blanket type ignore
  (PGH003), naive datetime (DTZ005), `time.sleep` in async (ASYNC251), dangling task (RUF006): each found.
- mypy strict: the untyped function; an unneeded ignore is reported too.
- import-linter: the forbidden import breaks its contract.
- pytest: the probe test is deselected by default.
- complexipy fails (exit 1) on a function over the limit; with `--failed --ignore-complexity` it lists only those
  and exits 0, which is how the module uses it (a trigger, not a limit).
- vulture finds unused functions; at 60 % confidence it also lists functions only tests or entry points use, so the
  module uses 80.

## Choices

- mypy over pyright and ty: mypy is the reference checker and strict mode is well understood; pyright is a fine
  alternative a project may choose (one per project); ty was 0.0.109, not stable yet. Revisit ty when it is.
- No formatter (as in core); no ruff style rules (E1-E5, W, I, Q, COM, D...).

## Open

- Notebooks (Jupyter): not covered.
- Data and ML projects (data versioning, experiment tracking, GPU notes) would be a concern module of their own.
