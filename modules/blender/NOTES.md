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

## Taken from an earlier asset pipeline, left out

- The 100 KB `ASSET_STANDARDS.md` with dated rework sections: a standard should be short, its history in the log.
- Standards and contracts in the git-ignored `Dev/` folder: only large binaries belong outside git.
- Its families, palette and characters.

## Open

- EEVEE rendering headless was not run here (Workbench only).
- A geometry-nodes workflow (node groups as the generator) is not covered; scripts are.
- Whether a Blender extension (`blender_manifest.toml`) project needs more than this module (packaging, the
  extensions platform).
