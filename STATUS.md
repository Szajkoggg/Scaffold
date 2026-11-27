# Status

**Summary:** The scaffold is complete enough to use: core, the stack and concern modules, the workstation layer and
the proposal flow are built and tested in scratch folders. It has not yet been used on a real project; that is next.

<!-- A snapshot, rewritten at the end of each working session; history is in the git log. Under ~60 lines. -->

Updated: 2026-11-27

## Now

- **Core**: rules, nine principles, sessions, plans (open questions with defaults, a length guide), research,
  documentation with its checker, health, eight agent roles with model and effort, six plan templates.
- **Review**: the reviewer reads a change by a method (whole functions, deletions, peers, inputs), checks it against
  its plan (missing, different, extra), reviews plans before approval on offer, raises the bar on later rounds, and
  labels every finding fix or decision; the module reviewers label theirs the same way. A second reviewer from the
  other model family (`codex exec`, `claude -p`) is offered for risky changes.
- **Modules ready**: `unity`, `dotnet`, `typescript`, `blender`, `web-ui`, `python`, `release`, `backend`.
  **Partial**: `visual-review` (no review-sheet generator) and `asset-pipeline` (no validator); both wait for a
  project that needs them (their `NOTES.md`, "Open").
- **Workstation**: personal rules, skills (`scaffold`, `scaffold-propose`, `grill-me`), status line, desktop
  notifications (`notify.py`: a permission prompt, or a turn over 30 s finished), Claude Code themes with matching
  Windows Terminal schemes, the Codex footer, environment variables. Installed on two workstations; notifications
  on one so far.
- **scaffold.py** stops when the clone is behind its upstream (apply, update, workstation) and when a project was
  updated from a scaffold commit the clone lacks (update; `status` warns). `--stale-ok` goes on.
- **Wrap-up guard**: tells the agent to wrap up at 90 % context and shows the user a one-line notice;
  `WRAP_UP_GUARD_LOG=1` logs every run. Tested with synthetic readings; not yet seen firing live.
- **Proposals**: GitHub issues labelled `proposal`, none yet.

## Next

1. **Use it on real projects**: scaffold a new project, align an existing one, run an update. Note every friction:
   fix it here, or let the project propose it (`playbooks/propose.md`). Watch live: the wrap-up guard firing, a
   plan review, a permission-prompt notification (the hook filters on `notification_type`, unconfirmed live).
2. **Install the workstation on the second computer** (pulls the clone first, by the new freshness check).
3. **Build the waiting parts with the first project that needs them**: the review-sheet generator
   (`visual-review`) and an asset validator (`asset-pipeline`).
4. **Ideas, not decided** (from a review of others' Claude Code repos; wait for real use to show the need):
   - a review offered at commit time, for larger unplanned diffs;
   - tagging a plan's key decisions (reuses, extends, new, diverges, breaking);
   - a list of owed follow-ups raised when their area is touched, unless `STATUS.md` "Next" already does it;
   - on update, offering the rules a project's `AGENTS.md` lacks from the current template;
   - a language-independent code check (files past their size trigger, `WORKAROUND:` markers);
   - CI templates per stack; git-describe versioning in `release`.
5. **Decided against splitting the scaffold into one repository per skill**: shared text would be copied or need a
   contract repository, versions would drift, and owned files, the manifest and `scaffold.py update` assume one
   repository.

## Open questions

None.

## Health

- Every preset scaffolds into a scratch folder and passes `check_docs.py` (0 errors; the placeholder warnings are
  expected before a bootstrap).
- The scaffold's Python scripts pass the `python` module's ruff rules (`uvx ruff`; tools started by name carry
  `noqa: S603, S607`). Two lines from before 2026-11-27 are past 120 characters (`scaffold.py`, the status line's
  docstring).
- Audited 2026-11-27: agent wrappers match their roles and "Runs at" tables, skills cite existing sections, no
  personal names in delivered content. Open from it: `release` has no `## Review`; `visual-review` and
  `asset-pipeline` have no `## Sources`.
- **Gap**: `scaffold.py` has no automated tests; it was tested by hand (apply, update, status, detect, workstation
  into a scratch home, the freshness and downgrade checks against throwaway clones). Worth a small test suite
  before larger changes to it.
