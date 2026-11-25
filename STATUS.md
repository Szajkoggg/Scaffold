# Status

**Summary:** The scaffold is complete enough to use: core, six stack and UI modules, the workstation layer and the
proposal flow are built and tested in scratch folders. It has not yet been used on a real project; that is next.

<!-- A snapshot, rewritten at the end of each working session; history is in the git log. Under ~60 lines. -->

Updated: 2026-11-24

## Now

- **Core**: rules, nine principles, sessions, plans, research, documentation with its checker, health, eight
  agent roles with model and effort, six plan templates.
- **Modules ready** (templates run against real tools): `unity`, `dotnet`, `typescript`, `blender`, `web-ui`,
  `python`; and the concern modules `release` (with a release plan template) and `backend`, whose commands come
  from the stack modules. **Partial**: `visual-review` (no review-sheet generator) and `asset-pipeline` (a contract
  template, no validator); both wait for a project that needs them (their `NOTES.md`, "Open").
- **Workstation**: personal rules, skills (`scaffold`, `scaffold-propose`, `grill-me`), status line, Claude Code
  themes (Graphite, Paper, Honey, Vaporwave; pick one with `/theme`), environment variables; installed on two
  workstations.
- **Wrap-up guard**: a core hook (`.claude/hooks/wrap_up_guard.py`) tells the agent to wrap up at 90 % context,
  reading the fill the workstation status line writes to `<temp>/claude-context/`. Modules can ship a
  `settings.json`, merged into the project's settings on apply and update. Tested with synthetic readings; not yet
  seen firing in a live session.
- **Proposals**: GitHub issues labelled `proposal`, none yet.

## Next

1. **Use it on real projects**: scaffold a new project, align an existing one, run an update. Note every friction:
   fix it here, or let the project propose it (`playbooks/propose.md`).
   Watch the wrap-up guard fire in a live session.
2. **Build the waiting parts with the first project that needs them**: the review-sheet generator
   (`visual-review`) and an asset validator (`asset-pipeline`).
3. **Open points**: none left to probe. Settled on 2026-11-24: EEVEE headless, Unity capture under URP and HDRP,
   `unity test --affected`, the `unity` CLI's package listing and editor scripts, Lighthouse, Vitest `related`,
   analyzers inside Unity (not adopted), Microsoft.Testing.Platform. The .NET module ships a shrink-only
   warning baseline (`check_baseline.py`) for existing codebases.
4. **Ideas, not decided**:
   - a language-independent code check (source files past their size trigger, `WORKAROUND:` markers);
   - running subagents on the status line, through hooks (undocumented, so fragile);
   - CI templates per stack.

## Open questions

None.

## Health

- Every preset scaffolds into a scratch folder and passes `check_docs.py` (0 errors; the placeholder warnings are
  expected before a bootstrap).
- The scaffold's own Python scripts pass the `python` module's ruff rules.
- **Gap**: `scaffold.py` has no automated tests; it was tested by hand (apply, update with an edited file, status,
  detect, workstation into a scratch home). Worth a small test suite before larger changes to it.
