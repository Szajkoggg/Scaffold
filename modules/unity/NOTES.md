# unity: notes for the module

**Summary:** The module is written; these are the points to verify on its first real project and the ideas left out.

Not delivered to projects.

## Verify on first use

- `HeadlessCapture.cs` has not run yet: camera rendering into a texture in a `-batchmode` player under URP and HDRP.
- `unity test --affected` behaviour on a project with asmdefs (does it narrow, how long it takes).
- Whether a CLI command lists package updates (`unity command --query package` with an Editor open); if so, put it
  in the Health table.
- `unity run --command` versus a static method in batchmode for editor scripts: which works without an open Editor.

## Left out on purpose

- An earlier project's list of known check mismatches: tolerated failures become permanent (principle 2).
- Hash-based rebuild skipping from an earlier project: a project's own optimisation, not a default (KISS).
- An earlier project's world rules, probes and checks: specific to that project.

## Ideas

- A health row for "Missing script" and missing references, found by an editor script run in batchmode.
- A CI template from `unity ci` once a project needs CI.
