# Playbook: propose a change to the scaffold

**Summary:** From any project, an agent proposes an improvement to the scaffold as a GitHub issue on the scaffold's
repository, labelled `proposal`. Only generic improvements: what would help every project of its kind. The scaffold
itself is never edited from a project; proposals are worked through in the scaffold repository
(`proposals.md`).

## Is it generic?

Propose it only if all of these hold; otherwise it belongs in the project's own `AGENTS.md`:

- **It would help another project** of a different kind, or of the same stack (then it targets that stack's module).
- **It names nothing of this project**: no project name, path, domain term, person or private detail. The evidence is
  described in general terms ("a Unity project whose generators run headless"), never pasted from private code.
- **It is about the scaffold's material**: a principle, a process document, a role, a skill, a template, a module's
  rules or sources, a script, the playbooks.

Good candidates: a process document that misled the agent; a template or script bug; a rule the agent had to work
around; a missing gotcha or source in a module; a project's edit to a scaffold-owned file that every project should
have; a tool fact found by research that is true for every project using that tool.

## Steps

1. **Find the repository**: `git -C <scaffold> remote get-url origin` (the scaffold's folder is in the `scaffold`
   skill). No remote, or `gh` not installed or not logged in (`gh auth status`): write the proposal as a file in
   `<scaffold>/proposals/` named `YYYY-MM-DD-<slug>.md`, and tell the user it waits to be filed.
2. **Look for an existing proposal**: `gh issue list -R <owner/repo> --label proposal --state all --search "<words>"`.
   If one covers it, add a comment with the new evidence instead of a new issue.
3. **Ask the user** in one line before filing: the title and the one-sentence why. Filing publishes to GitHub.
4. **File it**: `gh issue create -R <owner/repo> --label proposal --title "<area>: <what>" --body-file <file>`, the
   body written to a temporary file in this form:

   ```markdown
   ## What
   The change, in a few sentences.

   ## Why
   What happened that shows it is needed, in general terms; how often it is likely to happen elsewhere.

   ## Where
   The scaffold files it touches (e.g. `core/files/docs/process/testing.md`, `modules/unity/...`), and whether they
   are owned (replaced in every project) or seeds.

   ## Draft
   The proposed text or diff, as far as it is clear.

   ## Generic check
   Why it holds for other projects; what it deliberately leaves to projects.
   ```

   If the label is missing in the repository: `gh label create proposal -R <owner/repo> --description "A change
   proposed from a project"` first.
5. **Report**: the issue's link, in one line.
