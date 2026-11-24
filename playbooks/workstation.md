# Playbook: set up a workstation

**Summary:** Installs the user's personal layer on this computer: personal skills (`grill-me`, `scaffold`) for
Claude Code and Codex, the personal rules, the status line and settings. Safe to rerun: it updates what it installed
and never overwrites what the user changed.

What is installed is listed in `workstation/workstation.json`; the personal rules are `workstation/personal.md`.

## Steps

1. **Check prerequisites**: Python 3.9+ (`python --version`, on Windows also `py --version`), Git, and which tools
   are installed (`~/.claude`, `~/.codex`). Say what is missing; a tool that is not installed can still get its
   files.
2. **Dry run**: `python <scaffold>/scaffold.py workstation --dry-run`. Show the user the list in a few lines: what
   is added, updated, what conflicts.
3. **Ask once** whether to go ahead, naming any conflict. A conflict (`!`) is a file that exists but did not come
   from the scaffold, or was edited since: recommend per file which version to keep, after reading both.
4. **Install**: the same command without `--dry-run`. Then resolve conflicts the user decided: copy the chosen
   version from `~/.scaffold/incoming-workstation/` over the file, or keep it; rerun the command so the manifest
   (`~/.scaffold/workstation.json`) records the result.
5. **Personal rules** are written between `<!-- scaffold:personal -->` markers in `~/.claude/CLAUDE.md` and
   `~/.codex/AGENTS.md`; whatever else is in those files stays as it is.
   **Environment variables** (`env` in `workstation.json`) are set for the user: fixed values (`DISABLE_TELEMETRY`)
   and paths found on this machine (`BLENDER`: the newest Blender install). On Windows the script sets them with
   `setx`; elsewhere it prints the line for the shell profile. A path not found is reported, not guessed: ask the
   user where the tool is, or leave it unset if the machine does not need it.
6. **Report**: what was installed, what was kept, and that a new chat (or a restart of the tool) is needed for skills,
   settings and environment variables to load; MCP servers started by a tool see a new variable only after that
   tool restarts.

## When the user wants something added

A personal setting, skill or rule the user wants on every computer goes into `workstation/` in the scaffold
repository (not only into this computer's files), then this playbook is rerun. Remind the user to commit and push the
scaffold repository.
