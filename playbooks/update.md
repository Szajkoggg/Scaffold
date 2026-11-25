# Playbook: update a scaffolded project

**Summary:** Brings a project scaffolded earlier up to the scaffold's current version: untouched scaffold files are
replaced, files edited in the project are merged by hand, new modules are offered. No questions unless a merge or a
new module needs one.

## Steps

1. **Status**: `python <scaffold>/scaffold.py status <folder>`: the modules, the versions, owned files edited in
   the project. `git status` in the project: uncommitted work is left alone; if it touches scaffold files, ask first.
2. **Update**: `python <scaffold>/scaffold.py update <folder>`. Outcomes:
   - `+` added, `~` updated, `-` removed: done by the script.
   - `!` an owned file edited in the project: its new version is in `.scaffold/incoming/`. Merge it: take the
     scaffold's version, and carry the project's change over to where project rules belong (a section of the
     project's `AGENTS.md` named after the process document, e.g. "## Review"), not back into the owned file. If the
     change is an improvement every project should have, propose it (`propose.md`).
   - `?` a seed file the scaffold changed: seeds belong to the project; mention noteworthy changes only.
   - `i` something to do by hand with nothing in `.scaffold/incoming/` (a file the script expected is missing, an
     environment variable it could not set): do it or tell the user.
3. **After merging**: delete `.scaffold/incoming/` and run `update` again, until it reports no conflicts.
4. **New modules**: run `scaffold.py detect <folder>`; if it finds modules the project does not use, or a module
   in use is no longer a stub, mention it in one line with a recommendation. Adding one is
   `scaffold.py apply <folder> --modules <name>`, on the user's yes.
5. **Verify**: `python docs/process/tools/check_docs.py` in the project; fix what the update broke.
6. **Commit**: "Update the scaffold to <version>", the merges in the same or a following commit. Never push.
7. **Report**: from which version to which, what changed in the process (read the scaffold's git log between the two
   versions if available, in a few lines), what was merged.
