# Asset contract: <family, e.g. props for the game client>

**Summary:** What every delivered <family> asset must be so <the consumer> can use it without adjusting it.
Version <1>; a delivery names the version it meets.

<!-- Copy to the path AGENTS.md, "Where things are", names for the contract (docs/process/modules/asset-pipeline.md).
Fill each section from the consumer's real import, not from habit; delete what does not apply. Every rule should be
checkable, by the validation script where possible. A changed rule raises the version and says what changed. -->

Version: 1
Consumer: <engine or program, its version, how it imports: e.g. a glTF importer, an FBX import preset>
Validated by: <script and command, or "by hand" until there is one>

## Units, scale and orientation

- Units: <1 unit = 1 metre>. Up axis: <+Y / +Z>. Forward: <-Z / +Y>.
- Size: <reference sizes: a door is 2 m high; a hand-held prop fits in 0.3 m>.
- Transforms applied: rotation 0, scale 1 on export.

## Pivot

- <Where the origin sits: bottom centre for things that stand; the hinge for doors; the grip for held items.>

## Naming

- Files: <`<family>_<name>_<variant>.<ext>`, lower case, ASCII, no spaces>.
- Inside the file: <mesh, material and collision names, and the prefixes the consumer reads, e.g. `UCX_` for
  collision>.

## Geometry

- Triangle budget: <per class: small prop ≤ N, large ≤ M>.
- Levels of detail: <none / LOD0..LODn, each about half the previous; the suffix the consumer expects>.
- Collision: <none / simple shapes / a convex hull, named as above>.
- Clean: no loose vertices, no zero-area faces, normals outward, no overlapping UVs where the consumer bakes.

## Materials and textures

- Materials: <count per asset; the shader model the consumer uses, e.g. metallic-roughness PBR>.
- Textures: <maps (base colour, normal, ORM…); sizes as powers of two up to N; format; colour space per map;
  normal-map convention (OpenGL or DirectX)>.
- Texture files beside the asset or embedded: <which>.

## Files

- Format: <glb / fbx / png…>, exporter and its settings: <a preset name or the settings listed>.
- Where a delivery goes: <folder>. Provenance next to it (`asset-pipeline.md`, "Provenance").

## Preview

- Views the consumer uses: <in-game camera distance and angle, lighting>, plus close-ups of what the request names.

## Changes

| Version | Date | What changed |
|---|---|---|
| 1 | YYYY-MM-DD | First version |
