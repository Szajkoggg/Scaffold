---
name: scaffold
description: Scaffold a project with the user's AI workflow scaffold - a new project, an existing one, or update one scaffolded earlier - or set up this workstation. Use when the user asks to scaffold, set up, align or update a project's AI workflow, or to set up the workstation.
---

The scaffold lives at `{{SCAFFOLD_HOME}}`. Its script is `python {{SCAFFOLD_HOME}}/scaffold.py`.

1. Decide which case this is, from the folder the user named (default: the current folder) and what they asked:
   - **workstation**: the user asked to set up or update this computer.
   - **update**: the folder has `.scaffold/manifest.json`.
   - **new project**: the folder is empty or does not exist (a README, a license or `.git` alone count as empty).
   - **existing project**: anything else.
2. Read and follow the playbook for that case, every step:
   `{{SCAFFOLD_HOME}}/playbooks/workstation.md`, `update.md`, `new-project.md` or `existing-project.md`.
3. If `{{SCAFFOLD_HOME}}` does not exist, say so and ask where the scaffold repository is now.
4. If `scaffold.py` stops because the scaffold clone is behind: when it says to run `pull --ff-only`, run it, say so
   in one line, and run the command again; when it names local changes or a diverged clone, tell the user and stop.
