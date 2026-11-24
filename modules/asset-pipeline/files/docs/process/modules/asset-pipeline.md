# Module: asset-pipeline

**Summary:** Producing assets (models, textures, generated images) for a consumer: an asset contract that says what a
delivery must be, requests and receipts that record the exchange, validation before delivery, and previews for the
user's review.

## The exchange

- **The contract** (its path is in `AGENTS.md`, "Where things are", like the requests and receipts folders) says what every delivered asset must be: units and scale, pivot and
  orientation, naming, levels of detail, materials and texture sizes, file formats, and how the consumer reads it.
  It has a version; a delivery names the version it meets.
- **A request** (one file per asset in the requests folder) says what is needed: purpose, references, constraints, priority.
- **A receipt** (one file per asset in the receipts folder) records what was delivered and what the consumer had to adjust.
  An adjustment the consumer had to make belongs in the next export, not in the consumer for ever.
- **Generated content is reproducible** (principle 5): the tool, model, prompt, seed and settings are recorded next
  to the output, so it can be made again.

## Provenance

Every asset that did not come from the project's own generators carries a record next to it (`<asset>.source.json`
or a line in the family's index): where it came from, who made it, its licence, the date, and for AI-generated
models the service, prompt and settings.

- **Licences decide use**: an asset whose licence needs credit (common on Sketchfab: CC BY) gets the credit wherever
  the project lists credits; one whose licence forbids commercial use or redistribution is not used in a product
  without the user's decision, and is not committed if it may not be redistributed.
- **CC0** (Poly Haven) needs no credit; record it anyway, so the question never has to be asked again.
- **Paid generation** (AI model services) is the user's decision each time; check the service's terms for
  commercial use when the asset is for a product.

## Checks

- **Validation**: the contract's script over a delivery before it is offered: the assets changed while working, all
  of them for the full check; its command in `AGENTS.md`, "Commands". The exit code decides; each failure names the
  asset, the rule, the value found and the one expected.
- **The validator reads the file as the consumer does**: the format first (for glTF the Khronos glTF Validator), then
  the contract's rules on top: scale, triangle counts, names, texture sizes (with the `blender` module, a script
  run headless: `"$BLENDER" -b -P <validate.py> -- <file>`).
- **Provenance**: every asset file has its record; a file without one is a failure.
- A new contract starts from `docs/process/templates/asset-contract.md`.

## Diagnosing

- **Wrong size or turned in the consumer**: units and axes on export against import (FBX: unit scale and applied
  transforms; glTF is metres and +Y up by its specification). Send one reference cube through the whole path.
- **Textures too dark, washed out or bumpy the wrong way**: colour space (normal, roughness and metal maps are
  non-colour data) and the normal-map convention (OpenGL or DirectX: the green channel is flipped).
- **Right in the preview, wrong in the consumer**: the preview is not the consumer's renderer; compare with a
  picture taken in the consumer.
- **A regenerated asset differs**: the record misses a setting (model version, seed, sampler); add it.

## Health

The tools for this module's ledger row, used by the `auditor`:

| Check | Tool |
|---|---|
| Assets | every delivered asset validated against the current contract version (those meeting an older one listed); files without provenance; credits the licences require; the largest assets and textures against their budgets |

## Review

- Every delivery is validated against the contract (a script where possible) before it is offered.
- Previews: the asset from the views the consumer uses, plus close-ups of the details the request names; judged by
  the `visual-critic` when the `visual-review` module is in use.

## Agents

| Agent | Role | Runs at |
|---|---|---|
| `asset-builder` | [roles/asset-builder.md](../roles/asset-builder.md) | main model, medium |
| `asset-integrator` | [roles/asset-integrator.md](../roles/asset-integrator.md) | smaller model, medium |
