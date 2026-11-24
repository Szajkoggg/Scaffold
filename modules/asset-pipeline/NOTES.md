# asset-pipeline: what this module should bring

**Summary:** Producing assets (models, textures, generated images) for a consumer: asset contract, requests and receipts, validation, previews for review.

Not delivered to projects: design notes for writing the module.

- An asset contract document: what a delivered asset must contain (scale, pivots, LODs, materials, naming, texture sizes).
- Requests (what is needed) and receipts (what was delivered, overrides the consumer applied) as docs.
- Validation script per contract; previews rendered for review by the user.
- Texture generation: tool choice, seeds and prompts recorded with the output so it can be regenerated.
- Agents to consider: asset-builder, asset-integrator. Source: an earlier game project's asset contract, request and receipt documents and agents.
