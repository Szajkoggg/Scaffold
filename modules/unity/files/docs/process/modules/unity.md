# Module: unity

**Summary:** Unity projects: driven by the `unity` CLI, headless by default, never taking the user's focus; assets
moved only with their `.meta`; scenes changed by editor scripts; asmdef boundaries checked by a script. The sections
below are read by the core agents (check-runner, investigator, auditor, measurer, reviewer).

The Unity project's folder (the one holding `Assets/` and `ProjectSettings/`) is named in `AGENTS.md`, "Where things
are"; below it is `<project>`.

## Rules

- **The `unity` CLI first** (`unity --help`; core rule: `context.md`, "Tools"). The Editor's MCP server only for what
  no command can do, and say why. `unity command` drives a running Editor from the command line.
- **Never take the user's focus.** Batchmode runs and windowless pictures are the default. Opening a window, a
  windowed player or simulated input needs the user's yes first; then keyboard only (simulated mouse coordinates are
  wrong under display scaling).
- **The project lock**: batchmode cannot open a project that is open in the Editor. `unity status` shows open
  Editors. If the project is open: use the running Editor (`unity recompile`, `unity command`), or ask the user to
  close it. Never `unity close` without asking: it exits without saving.
- **Assets keep their GUIDs**: never move, rename or delete an asset through the file system without its `.meta`;
  better, move it through the Editor or an `AssetDatabase` editor script. A `.meta` is always committed with its
  asset.
- **Scenes and prefabs are changed by editor scripts** (`unity run --command`, or a static method run in batchmode),
  not by hand-editing their YAML, except a trivial value change. References break silently otherwise.
- **Tuning values live in ScriptableObjects or settings**, not literals in code (principle 1); the user tunes them.
- **The Editor version** is the one in `<project>/ProjectSettings/ProjectVersion.txt`; changing it is the user's
  decision. Never `--allow-install` (it downloads an Editor) without asking.
- **Packages**: `Packages/manifest.json` and `Packages/packages-lock.json` are committed.
- **Logic-heavy projects** (simulation, generation, rules) may keep that logic in a pure C# assembly
  (`noEngineReferences: true`) and test it with `dotnet test` in a separate .NET project that compiles the same
  sources: tests in seconds, without the Editor. Recommend it when the logic is large; for a small game, Unity's own
  test framework is enough (KISS).

## Repository setup

Applied once by the bootstrap (it belongs to the project after that), with `<project>` replaced by the project's
folder relative to the repository root (nothing when it is the root).

`.gitignore`:

```
<project>/[Ll]ibrary/
<project>/[Tt]emp/
<project>/[Oo]bj/
<project>/[Ll]ogs/
<project>/[Uu]ser[Ss]ettings/
<project>/[Bb]uild/
<project>/[Bb]uilds/
<project>/[Mm]emoryCaptures/
<project>/*.csproj
<project>/*.sln
<project>/*.slnx
<project>/.vsconfig
*.pidb.meta
*.pdb.meta
*.mdb.meta
crashlytics-build.properties
```

`.gitattributes`:

```
*.unity    text merge=unityyamlmerge eol=lf
*.prefab   text merge=unityyamlmerge eol=lf
*.asset    text merge=unityyamlmerge eol=lf
*.mat      text merge=unityyamlmerge eol=lf
*.anim     text merge=unityyamlmerge eol=lf
*.controller text merge=unityyamlmerge eol=lf
*.meta     text eol=lf
*.png  binary
*.jpg  binary
*.psd  binary
*.tga  binary
*.exr  binary
*.fbx  binary
*.blend binary
*.wav  binary
*.ogg  binary
*.mp3  binary
```

The bootstrap also verifies, and proposes fixing:

- **Project Settings > Editor**: Asset Serialization "Force Text", Version Control "Visible Meta Files".
- **Git LFS**: decided per project, not by default. Recommend it when binaries are large or change often (textures,
  audio, models over a few MB); the hosting service's LFS storage and bandwidth limits count. Without LFS, keep
  generated or large source art out of the repository.
- **asmdef rules**: `docs/asmdef-rules.json` written from the project's assemblies and "Rules the code keeps"
  (Checks, below).
- **A bookmark key** for games: one key saves a picture with the state needed to reproduce the view (scene, seed,
  camera, settings), so a remark like "this looks wrong" can be reproduced (principle 5). Propose it; build it
  when the user agrees.

## Checks

| Level | Command |
|---|---|
| Compile (Editor open) | `unity recompile <project> --strict` |
| Quick | `unity test <project> --mode EditMode --affected -o tmp/checks/editmode.xml --quiet` |
| Full | `unity test <project> --mode EditMode -o tmp/checks/editmode.xml`, then `--mode PlayMode -o tmp/checks/playmode.xml`, then a player build: `unity build <project> --target <target> -o tmp/build --log-file tmp/checks/build.log --no-tail` |
| Boundaries | `python docs/process/tools/unity/check_asmdef.py` |
| Pure C# core (if any) | `dotnet test <tests project> --filter <name>` quick, unfiltered full |

- Check `unity status` before a batchmode run (the project lock, Rules).
- A run ends when its command exits; read the results report (`-o`) for the counts and the first failure, not the
  streamed log.
- `--affected` runs the whole suite when it cannot tell what a change reaches; that is not a failure. It learns the
  tests from the last full run's report at the same `-o` path (run the full check first), writes its own report to
  `<name>.affected.xml`, and runs everything when nothing is uncommitted (`--since <ref>` compares with a branch).
  It narrows by assembly definition; on a small project the Editor's start-up dominates either way.
- `--retries` is for finding flaky tests (it reports them as flaky), never for making a run pass; a flaky test goes
  to `docs/HEALTH.md`, "Noticed".
- Long runs (PlayMode, builds) go in the background with `--timeout`; one batchmode run per project at a time.

## Diagnosing

- **Logs**: the Editor log of a CLI run is the `--log-file` given (always give one, under `tmp/`); the interactive
  Editor's is `%LOCALAPPDATA%\Unity\Editor\Editor.log`; a player's is `Player.log` under
  `%USERPROFILE%\AppData\LocalLow\<company>\<product>\`.
- **Compile errors first**: a batchmode run that fails early is usually a compile error; it is in the log before
  anything else.
- **Reproduce with the CLI**: a test with `unity test --filter <name>`; a scene or setup problem with an editor
  script run by `unity run --command` or a static method, so the reproduction is a command, not a sequence of
  clicks.
- **Usual failure classes**: an asset moved without its `.meta` (missing references, "Missing script"); a domain
  reload resetting static state; code that works in the Editor but not in a player (editor-only APIs, stripping,
  `Resources` paths); main-thread stalls from large synchronous work (NavMesh, asset loading).

## Health

The tools for the core ledger's rows (`docs/HEALTH.md`), used by the `auditor`:

| Check | Tool |
|---|---|
| Packages | `Packages/manifest.json` against the latest compatible versions. No CLI command for this is confirmed yet: with an Editor open, look for one with `unity command --query package`; otherwise ask the user to check the Package Manager's Updates list |
| Editor version | `ProjectVersion.txt` against the current LTS of its line (`unity releases`); upgrading is the user's decision |
| Compiler warnings | Count in a batchmode compile log; a rising count is a finding |
| Tests | Slowest tests from the results report; flaky ones from `--retries` runs |
| Boundaries | `check_asmdef.py` |

## Measuring

- **Measure in a player build**, not the Editor: the Editor's overhead distorts every number. Development build with
  the Profiler, or the Performance Testing package (`com.unity.test-framework.performance`) for repeatable
  measurements in PlayMode tests.
- **GPU-bound measurements need a window**: run them alone (nothing else using the GPU), and only with the user's
  yes (Rules). CPU-only measurements run headless.
- Record frame time as percentiles (median, 95th, 99th), not an average; a hitch hides in an average.

## Review

- **Pictures without a window**: a player run with `-batchmode` but not `-nographics` renders a camera into a
  texture and writes it (`docs/process/tools/unity/HeadlessCapture.cs` is a template). `ScreenCapture` gives a black
  picture in batchmode; with `-nographics` there is no graphics device and the picture comes out flat grey while the
  run exits 0 (the template refuses with exit 3). The same render into a texture works in an Editor batchmode static
  method.
- Views are fixed (scene, camera, seed, settings) so a before and an after are comparable (`visual-review`).
- Beyond the principles, review for: allocations in `Update` and other per-frame code; `Find`/`GetComponent` in
  per-frame code; editor-only APIs outside `#if UNITY_EDITOR` or an Editor assembly; serialized field renames
  without `FormerlySerializedAs` (they lose data in scenes and prefabs); `?.` and `??` on Unity objects (they skip
  Unity's own null check, so a destroyed object passes as alive).

## Assets

- **Importing**: files go into `Assets/` with import settings set by an `AssetPostprocessor` or a preset, not by
  hand, so a re-import gives the same result.
- **Generated content** (from scripts or the `asset-pipeline`): the generator, not the generated file, is the
  source; regenerate rather than edit the output.
- Large source files (`.blend`, `.psd`) stay outside `Assets/` unless Unity must import them directly.

## Sources

Where the truth is for this stack, nearest first (`docs/process/research.md`). Read by everyone looking something
up, and by the `researcher`.

- **The version**: `ProjectSettings/ProjectVersion.txt` in the Unity project; packages and their versions in
  `Packages/packages-lock.json`.
- **The tool**: `unity --help` and `unity <command> --help`.
- **The installed code**: each package's source, `CHANGELOG.md` and documentation folder under the project's
  `Library/PackageCache/<package>@<version>/`.
- **The documentation for that version**: the [Unity Manual and Scripting Reference](https://docs.unity3d.com/)
  (pick the version in the page's version menu); package documentation per package version
  ([docs.unity3d.com/Packages](https://docs.unity3d.com/Packages/)).
- **Changes between versions**: the [release notes](https://unity.com/releases/editor/archive) of the Editor version,
  and each package's `CHANGELOG.md`.
