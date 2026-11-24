# Playbook: scaffold an existing project

**Summary:** For a project with code but no `.scaffold/manifest.json`. A survey, one confirmation round with a
concrete proposal, then the scaffold is applied, existing files are merged rather than replaced, and the bootstrap
fills in the rest. Nothing of the project's is deleted or moved without the user's yes.

## Steps

1. **Survey** (a subagent for anything larger than a few folders), read-only:
   - `python <scaffold>/scaffold.py detect <folder>`: the modules whose signs the project shows, and fitting presets;
   - the stack, build and test commands, entry points, main modules and their dependencies;
   - existing agent files (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`,
     `.claude/`, `.codex/`, `.agents/`) and existing docs (README, `docs/`, ADRs, changelogs);
   - `git status`: uncommitted work. Scaffolding over uncommitted work is refused until the user decides.
2. **Dry run**: `python <scaffold>/scaffold.py apply <folder> --preset <p> [--modules ...] --dry-run`. Note every
   `?` (a seed file that exists, e.g. the project's own `AGENTS.md`) and `!` (an owned path that exists).
3. **Propose, in one message**:
   - the preset and modules, with the evidence for each, and the stubs named as such;
   - the files that will be added;
   - for each existing file that collides, how it will be merged (below);
   - existing docs: where each fits in the structure (`docs/README.md`'s map). Recommend linking them from the right
     index where they are; moving files is a separate proposal the user may decline;
   - what the bootstrap will fill in, with your guesses for the commands.
   Wait for the user's yes or corrections. This is the only question round unless something unexpected comes up.
4. **Apply**: the same command without `--dry-run`. If git is used, on the current branch (the user may ask for a
   branch).
5. **Merge** the colliding files, from the versions in `.scaffold/incoming/`:
   - `AGENTS.md`: the project's existing rules are kept and fitted into the scaffold's sections (what this is, who
     decides what, where things are, commands, how work is done, rules the code keeps); the scaffold's rules are
     added; contradictions are named for the user. Keep the Modules block markers.
   - `CLAUDE.md`: its rules move into `AGENTS.md`; it keeps the `@AGENTS.md` line (Claude-only settings may stay).
   - Other agent rule files (`.cursorrules`, ...): their rules move into `AGENTS.md`; the files stay unless the user
     says to remove them.
   - `.gitignore`, `.gitattributes`: the scaffold's lines added to the project's, never replacing them.
   - An owned file (`!`) the project already had, e.g. its own `.claude/agents/reviewer.md`: show both, recommend;
     the project's version can become a project rule or a module of its own.
   Then delete `.scaffold/incoming/` and run `scaffold.py update <folder>` once, so the manifest records the merged
   state.
6. **Bootstrap**: follow the project's `docs/process/bootstrap.md` (the survey is done: reuse it).
7. **Verify**: `python docs/process/tools/check_docs.py --strict` passes; existing docs the project keeps outside the
   scaffold's folders get their indexes or exclusions in `docs/check-docs.json`.
8. **Commit**: the scaffold files, then the merges, then the bootstrap, each its own commit with why. Never push.
9. **Report**: modules, files added, what was merged and how, the docs mapped, open questions, and the first
   health proposals the bootstrap found.
