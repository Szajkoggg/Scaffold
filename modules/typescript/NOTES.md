# typescript: notes for the module

**Summary:** The module is written and its templates were installed and tested; these are the findings behind it and
the points left open.

Not delivered to projects.

## Tested (2026-11-24)

With typescript 6.0.3, eslint 10.15.0, typescript-eslint 8.74.0, eslint-plugin-sonarjs 4.2.2,
@eslint-community/eslint-plugin-eslint-comments 4.8.1, dependency-cruiser 18.9.0, knip 6.48.0, Node 26:

- One planted violation per rule: floating promise, non-exhaustive switch, `any`, unsafe member access and return,
  `!`, object-literal cast, thrown string, `==`, an `eslint-disable` without a reason: all errors; cognitive
  complexity a warning; a justified disable passes; an import cycle and a devDependency imported from `src/` are
  dependency-cruiser errors; an unused local is a `tsc` error; knip finds unused files with no configuration.
- **Found on the way**: excluding `node_modules` in dependency-cruiser's `exclude` hides every package import, so a
  rule about packages never fires. The configuration this module was drawn from had that exclude, so package rules
  there would be blind. `doNotFollow` alone is right.
- **Vitest 5.1.1** (a minimal project, three modules, A importing B): `vitest related <files> --run --bail 1` runs the
  tests of the changed files and of their importers (B changed: A's and B's tests), accepts test files and Windows
  paths, needs no git repository; no matching tests or no files at all exit 0. `--bail 1` stops after the first
  failure. About 1.5 s a call, most of it start-up.

## Taken from an earlier TypeScript project, left out

- `scripts/test-lock.ts` (one full run per machine): needed by an orchestrator running many agents, not by a project.
- `scripts/test-files.mjs`: the idea (changed files, stop at the first failure) is in Checks; the script was that project's own.
- The `localeCompare` rule with that project's id names: kept as a rule in prose and a review item.

## Open

None.

## Out of scope (decided; revisit when a project asks)

- The React hooks rules (`rules-of-hooks`, `exhaustive-deps`, only those two) and JSX settings belong to `web-ui`.
- A schema validation library for boundaries (zod, valibot): not chosen by the module; the bootstrap asks if the
  project has none.
