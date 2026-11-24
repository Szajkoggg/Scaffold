# Scaffold: working rules

Rules for working on the scaffold itself. Rules for projects made from it are in `core/files/AGENTS.md`. The
layout and the ownership model are in `README.md`.

- **Generic content only.** Nothing in `core/` or a module may name a specific project, person or machine path
  outside `{{placeholders}}`. Examples name kinds of things, not the user's projects.
- **The text of a workflow lives once**: process documents in `core/files/docs/process/` (or a module's
  `files/docs/process/modules/`). Skills and agents are thin wrappers that point to them; a skill is written once
  under `skills/` and `scaffold.py` delivers it to both Claude Code and Codex.
- **Ownership is a contract.** Owned files are replaced in every project on update; seeds are never touched after
  the first copy. Moving a file between the two, renaming or removing an owned file affects every scaffolded
  project: say so in the commit message.
- **Personal versus project**: about the user (language, status line, personal skills) goes in `workstation/`;
  about a project goes in `core/` or a module.
- **Keep `core/files/AGENTS.md` under ~150 lines**: it is loaded into every session of every project.
- **Test a change** by applying to a throwaway folder in the scratchpad or `tmp/`:
  `python scaffold.py apply <dir> --preset <p>`, then `python <dir>/docs/process/tools/check_docs.py` there; for the
  workstation, `python scaffold.py workstation --home <dir>`. Never test against a real project or the real home
  folder without asking.
- **Proposals from projects** arrive as GitHub issues labelled `proposal` (or files in `proposals/`); they are
  decided with the user and built or closed with the reason (`playbooks/proposals.md`).
- **A module stays a stub** (`"status": "stub"`) until it delivers its process document; its `NOTES.md` collects the
  design meanwhile.
- Files in English; reply to the user in the language they write in.
