# Module: typescript

**Summary:** TypeScript on Node: strict types with no escapes left unexplained, Node running `.ts` directly where it
can, ESLint with correctness rules only (all errors), dependency-cruiser for the boundaries, knip for dead code, one
test runner per project. Read by the core agents for their sections below.

## Rules

- **The CLIs** (`npm`, `npx tsc`, `npx eslint`, `npx depcruise`, `npx knip`, `node --test`) for everything (core rule:
  `context.md`, "Tools").
- **Strict, with the gaps closed**: `strict`, `noUncheckedIndexedAccess` (an index can be missing), unused locals and
  parameters are errors (an intentionally unused parameter starts with `_`).
- **No unexplained escapes** (principle 2): `any`, an object-literal cast, the non-null `!` are lint errors; where one
  is truly needed, the `eslint-disable` comment says why after `--`. Data from outside (`JSON.parse`, requests,
  files) is validated at the boundary, not cast with `as`.
- **Every promise is awaited or handed on**; one left alone on purpose says so with `void`. A `switch` over a union
  names every member; `default` does not count as handling them.
- **Errors are `Error` objects**, wrapped with `new Error(message, { cause })` so the original stays (principle 5).
- **Node code runs as `.ts` without a build** (Node 24+ strips the types): `erasableSyntaxOnly` keeps out the syntax
  that needs a compiler (`enum`, `namespace`, parameter properties); use union types and plain objects. Code a
  bundler builds uses the bundler's settings instead.
- **ESM only** (`"type": "module"`); `engines.node` and a `.node-version` file pin Node's major version.
- **One test runner per project**: `node:test` for Node code (built in, nothing to install); Vitest when the project
  already builds with Vite. Never both.
- **Ids are compared by code unit, never by locale**: `localeCompare` follows the machine's language, and in some
  (Hungarian: "ZS" after "ZT") it reorders ids and timestamps with letters.
- **A monorepo** uses npm workspaces; packages depend on each other only as `AGENTS.md`, "Rules the code keeps",
  allows, checked by dependency-cruiser.

## Repository setup

Applied once by the bootstrap; the files are the project's afterwards. Templates in `docs/process/tools/typescript/`.

- **`tsconfig.json`** (or the monorepo's base config) from `tsconfig.node.json`, or `tsconfig.bundler.json` for code a
  bundler builds.
- **`eslint.config.js`** from `eslint.config.js`, with these devDependencies: `eslint`, `typescript-eslint`,
  `@eslint-community/eslint-plugin-eslint-comments`, `eslint-plugin-sonarjs`.
- **`.dependency-cruiser.cjs`** from `dependency-cruiser.cjs`, with one rule per boundary in "Rules the code keeps";
  devDependency `dependency-cruiser`.
- **knip** (devDependency `knip`) starts without a configuration; a `knip.json` is added only for entries it cannot
  find itself (scripts run by path, files loaded by name).
- **`package.json` scripts**, one way per task (principle 6): `typecheck`, `lint` (ESLint then dependency-cruiser),
  `test`, `knip`.
- **`.gitignore`** lines:

  ```
  node_modules/
  dist/
  coverage/
  *.tsbuildinfo
  ```

- **An existing codebase**: run the checks once; findings that cannot be fixed now go to the tools' baselines, which
  can only shrink: ESLint's bulk suppressions (`eslint --suppress-all`, then the file `eslint-suppressions.json`) and
  dependency-cruiser's known violations (`depcruise-baseline`, then `--ignore-known`). Each baseline gets a line in
  `docs/HEALTH.md`, "Noticed". `noUnusedLocals` and `noUnusedParameters` may start off and be turned on in a plan.

## Checks

| Level | Command |
|---|---|
| Quick | `npx tsc -p <tsconfig> --noEmit`, `npx eslint <changed files>`, the changed tests: `node --test <test files>` (Vitest: `npx vitest related <changed files> --run --bail 1`) |
| Full | `npm run typecheck`, `npm run lint`, `npm test` |
| Tidy step, health | `npm run knip` |

- **ESLint without `--cache`**: with type information, a change in one file can create a finding in another.
- **knip is not a check of every change**: an export added for the next step is not dead yet. It runs in the tidy
  step of a plan and in the health check.
- The one warning is cognitive complexity: report the count, do not fail on it (`code.md`, "Size triggers").
- `node --test` prints every passing test; pass `--test-reporter=dot` (or Vitest's `--reporter=dot`) and keep the
  full report in `tmp/checks/`.

## Diagnosing

- **One test**: `node --test --test-name-pattern "<name>" <file>` (Vitest: `npx vitest run <file> -t "<name>"`).
- **A hang**: an unawaited promise or an open handle (a server, a timer, a child process) keeps Node alive;
  `node --test --test-timeout=<ms>` makes it fail instead of hang; `why-is-node-running` names the handle.
- **Unhandled rejections** end the process in Node by default: the stack shows where the promise was created only
  if errors are `Error` objects with their `cause`.
- **Order-dependent failures**: a sort by `localeCompare` on ids; `Date` parsing of strings without a format; a
  `Map` iteration order assumed to be sorted.

## Health

The tools for the core ledger's rows (`docs/HEALTH.md`), used by the `auditor`:

| Check | Tool |
|---|---|
| Dependencies | `npm outdated`, `npm audit --omit=dev`; `package-lock.json` committed, installs with `npm ci` |
| Dead code | `npm run knip` |
| Static analysis | Cognitive complexity warnings: the ten most complex functions; baseline sizes (they only shrink) |
| Tests | The slowest test files: `node --test --test-reporter=spec` durations, or Vitest's `--reporter=verbose` |

## Measuring

- **CPU**: `node --cpu-prof <script>` writes a `.cpuprofile` to open in a browser's DevTools.
- **The event loop** (principle 3): `monitorEventLoopDelay()` from `node:perf_hooks` around the workload; report the
  delay's percentiles. A blocked loop shows there before it shows in response times.
- **Micro-benchmarks**: `tinybench`, in its own script, never in the test suite.

## Review

Beyond the principles, look for: promises not awaited or passed where a callback returns `void`; `as` on data from
outside instead of validation; `any` passed on; synchronous `fs` or `child_process` calls in request handlers or
other hot paths; `Map`s and arrays used as caches without a bound; `localeCompare` on ids; `==`; `Date` parsing
without a format; `JSON.stringify` of large objects on hot paths.

## Sources

Where the truth is for this stack, nearest first (`docs/process/research.md`). Read by everyone looking something
up, and by the `researcher`.

- **The version**: `npm ls <package>`, or the `version` in `node_modules/<package>/package.json`; Node's with
  `node --version`.
- **The tool**: `npx <tool> --help`.
- **The installed code**: the package's type definitions (`.d.ts`) and source in `node_modules/<package>/`, its
  `CHANGELOG.md`.
- **The documentation for that version**: [Node.js API](https://nodejs.org/docs/latest/api/) (per major version),
  [TypeScript handbook and release notes](https://www.typescriptlang.org/docs/),
  [typescript-eslint rules](https://typescript-eslint.io/rules/), [ESLint](https://eslint.org/docs/latest/),
  [MDN](https://developer.mozilla.org/) for web platform APIs.
- **Changes between versions**: the package's changelog or GitHub releases; TypeScript's release notes.
