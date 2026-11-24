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

## Review

- Every delivery is validated against the contract (a script where possible) before it is offered.
- Previews: the asset from the views the consumer uses, plus close-ups of the details the request names; judged by
  the `visual-critic` when the `visual-review` module is in use.

## Agents

| Agent | Role | Runs at |
|---|---|---|
| `asset-builder` | [roles/asset-builder.md](../roles/asset-builder.md) | main model, medium |
| `asset-integrator` | [roles/asset-integrator.md](../roles/asset-integrator.md) | smaller model, medium |
