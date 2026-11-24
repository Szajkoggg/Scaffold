# unity: notes for the module

**Summary:** The module is written; these are the points to verify on its first real project and the ideas left out.

Not delivered to projects.

## Verify on first use

- `HeadlessCapture.cs` under HDRP (URP is verified, below).
- Whether a CLI command lists package updates (`unity command --query package` with an Editor open); if so, put it
  in the Health table.
- `unity run --command` versus a static method in batchmode for editor scripts: which works without an open Editor.

## Verified (2026-11-24, Unity 6000.6.10f1, URP 17.6, D3D12, `unity` CLI 1.0.1)

- `unity projects create <name> --template 3d --no-cloud` makes a URP project in about 80 s (and adds it to the
  Hub's list). `unity build . --target StandaloneWindows64` about 70 s.
- `HeadlessCapture.cs` in a `-batchmode` player: a correct picture in about 7 s, exit 0. With `-nographics` the
  device is Null, the picture flat grey, the exit code 0 and a Render Graph NullReferenceException in the log:
  hence the template's guard (exit 3).
- `unity test --affected` with three assembly definitions (Core, Game using Core, Util), five tests each: a change
  in Util ran 5 of 15, in Core 10 (Core and Game), in Game 5. Without a previous full report, or with nothing
  uncommitted, it runs everything. 11.7 s against 11.4 s for the full run: the Editor's start-up dominates.
- `-quit` is refused by `unity run` as a reserved flag; the run exits on its own.
- A project under a long path (about 260 characters) logs a harmless `DirectoryNotFoundException` under
  `Library/PackageCache`.

## Left out on purpose

- An earlier project's list of known check mismatches: tolerated failures become permanent (principle 2).
- Hash-based rebuild skipping from an earlier project: a project's own optimisation, not a default (KISS).
- An earlier project's world rules, probes and checks: specific to that project.

## Ideas

- A health row for "Missing script" and missing references, found by an editor script run in batchmode.
- A CI template from `unity ci` once a project needs CI.
