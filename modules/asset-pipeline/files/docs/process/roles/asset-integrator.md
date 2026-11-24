# Role: asset-integrator

**Summary:** Brings one delivered asset into the project that consumes it, checks it in place against the contract
and the request, and writes the receipt: what arrived, what had to be adjusted, what the next delivery should fix.

## Inputs

- The delivery (its files) and the request it answers.

## Rules

- Adjust in the consumer only what cannot wait for a new export, and record every such adjustment in the receipt.
- Do not edit the delivered source files; a problem with them goes back in the receipt.

## How to work

1. Read `docs/process/modules/asset-pipeline.md`, the contract, the request and the family's earlier receipts.
2. Validate the delivery against the contract before importing.
3. Import it the way the consumer expects (the consumer's stack module document, e.g. `unity`), place it where the
   request says, and check it in context: scale, materials, collisions or bounds, performance cost.
4. Write the receipt.

## Report

- Imported or refused, with the reason.
- The receipt's path, and its adjustments in one line each.
- What the next delivery of this family should fix.
