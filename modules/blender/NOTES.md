# blender: notes for the module

**Summary:** The module is written and its templates were run on Blender 5.2.2; these are the findings behind it and
the points left open.

Not delivered to projects.

## Tested (2026-11-24, Blender 5.2.2 LTS)

- A script raising an exception under `blender -b` exits with **0**; only `--python-exit-code 1` makes it 1.
  Generators run without that flag let their failures look like successes.
- Without `--factory-startup`, the user's add-ons load in headless runs ("BlenderMCP addon registered").
- `blender_script.py`: unfilled, it fails with exit 1 and writes `_failed.blend`; without `--out`, exit 2; a filled
  copy (seeded bmesh rocks, FBX export with the add-on enabled by the script) exits 0 with its outputs.
- `render_preview.py`: renders the views from a `.blend` and from an FBX. The first version framed only one of three
  objects (stale world matrices after loading); fixed with `view_layer.update()`, which is now a Rule.
- EEVEE renders headless (`-b`, an OpenGL context with no window; NVIDIA, Windows 11): `render_preview.py --engine
  eevee` exits 0; the first render takes about 14 s (shader compilation), later ones 1 to 3 s. Workbench about 0.7 s,
  Cycles on the CPU about 0.6 s at 16 samples. The engine enum's `enum_items` listed only `BLENDER_EEVEE`;
  `BLENDER_WORKBENCH` and `CYCLES` could still be assigned. Not run: a machine without a GPU, Remote Desktop.

## Taken from an earlier asset pipeline, left out

- The 100 KB `ASSET_STANDARDS.md` with dated rework sections: a standard should be short, its history in the log.
- Standards and contracts in the git-ignored `Dev/` folder: only large binaries belong outside git.
- Its families, palette and characters.

## Open

None.

## Out of scope (decided; revisit when a project asks)

- A geometry-nodes workflow (node groups as the generator) is not covered; scripts are.
- Whether a Blender extension (`blender_manifest.toml`) project needs more than this module (packaging, the
  extensions platform).
