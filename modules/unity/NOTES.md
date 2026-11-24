# unity: notes for the module

**Summary:** The module is written; these are the points to verify on its first real project and the ideas left out.

Not delivered to projects.

## Verify on first use

None: the points listed here were settled by the probes below.

## Verified (2026-11-24, Unity 6000.6.10f1, URP and HDRP 17.6, D3D12, `unity` CLI 1.0.1)

- `unity projects create <name> --template 3d --no-cloud` makes a URP project in about 80 s (and adds it to the
  Hub's list). `unity build . --target StandaloneWindows64` about 70 s.
- `HeadlessCapture.cs` in a `-batchmode` player: a correct picture in about 7 s, exit 0. With `-nographics` the
  device is Null, the picture flat grey, the exit code 0 and a Render Graph NullReferenceException in the log:
  hence the template's guard (exit 3).
- `unity test --affected` with three assembly definitions (Core, Game using Core, Util), five tests each: a change
  in Util ran 5 of 15, in Core 10 (Core and Game), in Game 5. Without a previous full report, or with nothing
  uncommitted, it runs everything. 11.7 s against 11.4 s for the full run: the Editor's start-up dominates.
- `-quit` is refused by `unity run` as a reserved flag; the run exits on its own.
- **HDRP 17.6** (`--template com.unity.template.hdrp-blank`, 103 s; first build 206 s for shaders, then about 20 s):
  the first template (one `camera.Render()` after waiting) wrote a pure white picture with exit 0 at any frame count:
  auto-exposure only adapts while the camera renders, and a batchmode player renders no camera by itself (a target
  set without `Render()` stays black). Rendering every settle frame fixes it: mean brightness 250 after 30 frames,
  237 after 120, 96 (right) after 600, 91 after 2000. Hence the template renders each frame, waits 600 frames under
  HDRP, and fails with exit 4 on a flat picture (a near-white one had values 254 to 255, so the check uses a
  tolerance).
- `unity build -o <path>` names the executable, not a folder: `-o build/Game.exe`.
- **No CLI command lists package updates.** `unity run . --command package.list --format json -- --scope all` works
  without an Editor (19 s) and gives the installed versions only; `package.search` too.
- **Editor scripts**: `unity run . --command <name>` (a `[CliCommand]` static method) runs with or without an open
  Editor (19 s cold, 1 s handed to an open one); `unity run . -- -executeMethod Class.Method` with the Editor
  closed (20 s). Both exit 0 on success and 6 when the method throws. `unity command <name>` needs an open Editor.
- A project under a long path (about 260 characters) logs a harmless `DirectoryNotFoundException` under
  `Library/PackageCache`.

## Left out on purpose

- An earlier project's list of known check mismatches: tolerated failures become permanent (principle 2).
- Hash-based rebuild skipping from an earlier project: a project's own optimisation, not a default (KISS).
- An earlier project's world rules, probes and checks: specific to that project.

## Ideas

- A health row for "Missing script" and missing references, found by an editor script run in batchmode.
- A CI template from `unity ci` once a project needs CI.
