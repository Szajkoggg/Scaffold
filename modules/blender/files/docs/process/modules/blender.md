# Module: blender

**Summary:** Blender driven by scripts run headless, in one way that fails loudly and gives the same result every
time; the live Blender and its MCP server only for what needs the user's open scene or a paid service. Read by the
core agents and the asset agents for their sections below.

## Rules

- **Headless scripts first** (core rule: `context.md`, "Tools"). Building, exporting, rendering previews, validating
  and batch changes are scripts run with Blender's command line, not calls into a live Blender.
- **One way to run Blender**, always with both flags:

  ```
  "$BLENDER" -b --factory-startup --python-exit-code 1 -P <script>.py -- <arguments>
  ```

  - Without `--python-exit-code 1`, a script that raises an exception still exits with 0: the failure looks like a
    success to every check.
  - Without `--factory-startup`, the user's preferences and add-ons (the MCP add-on among them) load into the run, so
    its result depends on the machine. A script enables the add-ons it needs itself.
  - `BLENDER` is an environment variable holding the path of `blender.exe`, set by the workstation setup.
- **Scripts start from the template** `docs/process/tools/blender/blender_script.py`: arguments after `--`, the
  Blender version the project expects checked first, add-ons enabled, seeded randomness (`random.Random(seed)`, never
  the module-level `random`), a non-zero exit and a saved `_failed.blend` on failure, and a refusal to run inside an
  open Blender.
- **The generator is the source**: an asset made by a script is regenerated, not edited by hand; its definition
  (parameters, seed, version) is versioned, and the version goes up when the result changes.
- **Units and axes are stated** in each generator and exporter: Blender works in Z-up metres; say what the exported
  file uses (e.g. Y-up for Unity) and where the origin is. Transforms are applied before export.
- **bmesh and the data API before `bpy.ops`**: operators depend on the selection, the active object and the context,
  which a headless run does not have the way a user does.
- **Facts of the Python API** that agents get wrong:
  - shader nodes are found by `node.type`, never by name (names are translated);
  - enum identifiers are read (`bl_rna.properties[...].enum_items`) or tried, never assumed: they change between
    versions. Render engines are tried: their enum leaves out engines that work (5.2 listed only EEVEE);
  - a material's colour is set on its shader node's inputs; `material.diffuse_color` only changes the viewport;
  - imported models arrive at an arbitrary scale: size and place them from their bounding box;
  - objects just loaded or moved have stale world matrices until `bpy.context.view_layer.update()`.
- **The live Blender** belongs to the user. One session works in it at a time; background runs use their own input
  files and output folders.

### The MCP server: when it is justified

Use the Blender MCP server only in these cases, and say which:

1. **The user's open scene**: the user asks the agent to look at or change what they are working on. Ask before
   running code in it, have the user save first, and work in small steps.
2. **Interactive modelling** with the user watching, where seeing each step is the point.
3. **Paid AI model generation** (`generate_3d`): it costs credits, so each use is the user's decision; the service,
   prompt, settings and result are recorded with the asset (`asset-pipeline`, "Provenance").
4. **Asset libraries** (Poly Haven, Sketchfab, Poly Pizza): each imported asset's source, author and licence is
   recorded (`asset-pipeline`, "Provenance").

A preview is a headless render (`render_preview.py`), not a viewport screenshot. A call made twice becomes a script.

## Repository setup

Applied once by the bootstrap; the files are the project's afterwards.

- **The expected Blender version** (major.minor) in `docs/WORKING.md`, and in each script's `EXPECTED_BLENDER`.
- **Scripts in one folder** (for example a `blender` folder among the project's tools), with their shared helpers as
  a package next to them; the folder is named in `AGENTS.md`, "Where things are".
- **`.gitignore`** lines:

  ```
  *.blend1
  *.blend2
  __pycache__/
  ```

- **Linting the scripts**: with the `python` module, ruff runs on them too; the `fake-bpy-module` package (the
  version for the project's Blender) gives editors and type checkers the `bpy` API.
- **Large `.blend` files**: in Git LFS or outside the repository, decided per project (`unity.md` has the same
  question for its binaries).

## Checks

| Level | Command |
|---|---|
| Quick | The changed script on its smallest input: `"$BLENDER" -b --factory-startup --python-exit-code 1 -P <script> -- --out tmp/blender/<name> <small arguments>` |
| Full | Every generator on its standard inputs, then the outputs validated (the `asset-pipeline` validator when that module is used) |

- A run passed when it exited with 0 **and** wrote the outputs it names; both are checked.
- Blender's output is long: redirect it to `tmp/blender/<name>.log` and report the exit code, the outputs and the
  first error.
- Runs that share nothing may go in parallel; each uses its own output folder.

## Diagnosing

- **The traceback** is in the run's log; with `--python-exit-code 1` the exit code says that there is one.
- **`_failed.blend`** in the output folder holds the scene as it was when the script failed: open it (in a separate
  Blender, with the user's agreement if it opens a window) or inspect it headless.
- **Add-ons or preferences suspected**: the run already uses `--factory-startup`; if a result differs from a user's
  live Blender, their add-ons or preferences are the first suspect.
- **More output**: `--log "<category>"` (e.g. `--log "*mesh*"`) and `--debug-python`.

## Health

The tools for the core ledger's rows (`docs/HEALTH.md`), used by the `auditor`:

| Check | Tool |
|---|---|
| Dependencies | The Blender version against the current LTS (upgrading is the user's decision); the full check run on a new version before switching |
| Tests | Every generator's smoke run in the full check; the slowest generators |
| Static analysis | ruff on the scripts (with the `python` module) |

## Measuring

- **Time per generator** and per render, from the run's own timing (`time.perf_counter()` around `build()`), on the
  same inputs.
- **Asset budgets**: triangle and vertex counts, texture sizes, file sizes, measured from the outputs and compared
  with the asset contract's budgets.

## Review

- **Previews**: `docs/process/tools/blender/render_preview.py` renders fixed views (`front`, `three-quarter`,
  `side`, `top`) of a model framed by its bounding box, named `<model>@<view>.png` (the view key). Workbench by
  default: the same on every machine; `--engine eevee` for materials (needs a GPU; works headless; the first
  render compiles shaders, about 14 s).
- Beyond the principles, review scripts for: `bpy.ops` where the data API would do; node lookups by name; hard-coded
  enum identifiers; unseeded randomness; missing unit and axis statements; outputs written outside the given output
  folder; anything that would touch an open scene.

## Assets

- Generators write into an output folder given as an argument; publishing a version into the place the consumer
  reads from is a separate step (`asset-pipeline`, "The exchange").
- Exports state their format settings in code (axes, scale, apply modifiers, which objects), never relying on the
  exporter's defaults or the user's last-used settings.

## Sources

Where the truth is for this stack, nearest first (`docs/process/research.md`). Read by everyone looking something
up, and by the `researcher`.

- **The version**: `"$BLENDER" --version`; inside a script `bpy.app.version_string`.
- **The tool**: `"$BLENDER" --help`; the Python API of the running version itself:
  `"$BLENDER" -b --factory-startup --python-expr "import bpy; help(bpy.types.Mesh)"`.
- **The documentation for that version**: the [Python API reference](https://docs.blender.org/api/current/) (the
  version is part of the address: replace `current` with e.g. `5.2`) and the
  [manual](https://docs.blender.org/manual/en/latest/).
- **Changes between versions**: the [release notes](https://developer.blender.org/docs/release_notes/), especially
  their "Python API" pages, before moving scripts to a new version.
