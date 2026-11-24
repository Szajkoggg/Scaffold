# Playbook: scaffold a new project

**Summary:** For an empty folder. A short interview decides the preset and fills in what the bootstrap needs, one
confirmation, then the scaffold is applied and bootstrapped. Only the AI layer and the documents: the code skeleton
is the project's first plan, not part of the scaffolding.

## Steps

1. **Interview**, one question at a time, each with your recommended answer (the way `grill-me` does), and only
   what is needed:
   - the project's name, and in a sentence or two what it is and for whom;
   - the kind of project → a preset (`python <scaffold>/scaffold.py list` shows them), or modules picked by hand;
   - the stack (language, engine, frameworks) if the preset leaves it open;
   - anything in "Who decides what" that differs from the default;
   - performance budgets that matter from the start, if any;
   - git: initialise a repository here? (Recommend yes.) A remote is the user's to add.
2. **Confirm**: show in one message the preset and modules (say which are stubs), the name, and what will be created.
   Go on when the user agrees.
3. **Apply**: `python <scaffold>/scaffold.py apply <folder> --preset <preset> [--modules ...] --name "<name>"`.
   Run `git init` first if agreed.
4. **Bootstrap**: follow the project's `docs/process/bootstrap.md`, with the interview's answers in place of a
   survey (there is no code yet). Commands that cannot be known yet stay as a line in `docs/STATUS.md`, "Next",
   not as placeholders: write "none yet (set by the first plan)" in `AGENTS.md`.
5. **STATUS**: "Next" names the first plan to write: the project skeleton (the stack's own generator, the first
   check commands).
6. **Verify**: `python docs/process/tools/check_docs.py --strict` in the project passes.
7. **Commit** (if git was initialised): "Scaffold the project (preset <preset>)", with the manifest. Never push.
8. **Report**: preset and modules, the files created, and the proposed first plan.
