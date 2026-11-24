# Module: web-ui

**Summary:** Web interfaces, whatever the framework: logic in plain tested modules and thin components, colours from
tokens only, texts in one catalogue, every view checked at fixed widths for layout faults and accessibility by a
headless capture, phones treated as a first-class layout. Read by the core agents and the visual critic.

## Rules

- **Logic out of components.** What a view decides (layout, filtering, state transitions, formatting) is plain
  functions in their own modules, unit tested without a browser; components render and wire events. A framework
  change then rewrites the thin part only.
- **Colours come from design tokens** (CSS custom properties in the token files) and nowhere else: no colour literal
  in components or styles. Themes (light, dark, others) set the same tokens. Checked by stylelint (Repository setup).
- **Never colour alone**: a status or kind is a word or a symbol with its colour, so it reads without colour and for
  colour-blind users. Text keeps a contrast of at least 4.5:1 (3:1 for large text and controls).
- **Interface texts live in one catalogue**, keyed by where they are used, with typed keys where the language allows.
  Numbers, dates, plurals and lists are formatted with `Intl` (`NumberFormat`, `DateTimeFormat`, `PluralRules`,
  `ListFormat`), not by string concatenation. A library only when the catalogue outgrows a lookup and `Intl` (KISS).
- **Every overlay closes the way the platform expects**: Escape, the browser's Back on a phone, a close button; and
  the URL restores what is shown, so a reload or a shared link opens the same view.
- **Keyboard first**: every action is reachable and visible with the keyboard; focus is never hidden; focus moves
  into a dialog when it opens and back when it closes.
- **The phone is a layout, not a squeeze**: from the narrowest supported width (390 px by default) up, no horizontal
  page scroll, no text cut short, targets at least 24 by 24 px (44 for primary actions).
- **No HTML from data**: inserting HTML from strings (`innerHTML`, the frameworks' raw-HTML escapes) only with
  sanitised content, and the reason in a comment (principle 2).
- **The framework's own correctness rules only**, never its style presets: see Checks.

## Repository setup

Applied once by the bootstrap; the files are the project's afterwards. Templates in `docs/process/tools/web/`.

- **Token files**: one place for the colours, spacing and type scale (e.g. `tokens.css`, `theme-dark.css`), named in
  `AGENTS.md`, "Where things are". A utility framework (Tailwind and the like) has its default palette switched off,
  so only the tokens produce colours.
- **`stylelint.config.mjs`** from the template, with `TOKEN_FILES` set; devDependency `stylelint`.
- **The capture**: devDependencies `playwright-core` and `axe-core`; a `views.json` (or one per area) with the views
  that matter, kept next to the UI's tests, its place named in `AGENTS.md`. Playwright drives the installed Edge
  or Chrome, so no browser download is needed.
- **Widths**: 390 (phone), 768 (tablet or a narrow window), 1440 (desktop), unless the project's breakpoints say
  otherwise (`docs/WORKING.md`, "Size triggers", or a "Widths" line there).
- **Budgets** in `docs/WORKING.md`, "Performance budgets": the largest JavaScript and CSS bundles (compressed), and
  the Core Web Vitals the project holds (largest contentful paint, interaction to next paint, layout shift).
- **Browser support** stated once (a browserslist entry or the build's target), so tools agree on it.

## Checks

| Level | Command |
|---|---|
| Quick | The stack's quick checks, plus `npx stylelint <changed style files>` |
| Full | The stack's full checks, `npx stylelint "**/*.css"`, the build, and the capture of the standard views: `node docs/process/tools/web/capture.mjs <views.json> --base-url <dev server> --axe --out tmp/capture` |

- **The capture** writes one picture per view (`<key>.png`, the view key, e.g. `settings@390`) and `report.json`,
  and prints one line per view. Exit 0: no problems; 1: faults or accessibility violations found; 3: a view could not
  be taken (the server is not running, a selector is wrong).
- **Faults it finds**: horizontal page scroll; text cut short (including fractions of a pixel); overlapping elements
  marked `[data-box]` (or the selector given as `boxes`); interactive targets under 24 by 24 px (links in running
  text are exempt). **With `--axe`**: WCAG 2.2 A and AA violations from axe-core (contrast, names, labels, structure).
- An element meant to scroll is marked `data-scroll`, so its hidden overflow is not a fault.
- **Framework correctness rules**, added to the stack's linter, nothing else of the plugin:

  | Framework | Rules |
  |---|---|
  | React | `react-hooks/rules-of-hooks`, `react-hooks/exhaustive-deps` |
  | Vue | `eslint-plugin-vue`'s "essential" set |
  | Svelte | `eslint-plugin-svelte`'s recommended correctness rules (no stylistic ones) |
  | Angular | `angular-eslint`'s template rules for accessibility and correctness |

## Diagnosing

- **One view**: `capture.mjs <views.json> --only <key>`; `report.json` names each fault's element.
- **A fault only at one width or theme**: add the view at that width or `colorScheme` and compare the pictures.
- **Works in the dev server, not in the build**: an environment variable, a base path, or a dynamic import the build
  splits differently; reproduce against the built files served locally.
- **Flicker or layout shift**: images and embeds without dimensions, fonts swapping late, content inserted above
  what the user reads.

## Health

The tools for the core ledger's rows (`docs/HEALTH.md`), used by the `auditor`:

| Check | Tool |
|---|---|
| Principles | The capture of the standard views at every width: faults and accessibility violations by count |
| Static analysis | stylelint (colour literals outside the tokens) |
| Performance | The bundle sizes from the build against their budgets; Lighthouse (`npx lighthouse <url> --only-categories=performance,accessibility --output=json --output-path=tmp/lighthouse.json --quiet --chrome-flags="--headless=new"`) |
| Dependencies | The stack's tools (npm for the `typescript` module) |

## Measuring

- **Bundles**: the build's output sizes, compressed, per entry; a change that adds more than a few kilobytes says why.
- **The page**: Lighthouse in the CLI, three runs, the median; on the built site served locally, not the dev server.
- **Interactions**: the browser's Performance panel or a Playwright script with `performance.mark` around the action;
  long tasks over 50 ms on the main thread are the usual cause of a slow interaction.

## Review

- **Pictures**: the capture's views, before and after (`visual-review`). The "before" is the same `views.json` run
  against the base commit's build, served on another port: same data, same widths, same theme.
- **The visual critic** reads this section too. Beyond the principles, look for: colour literals or one-off styles;
  a status shown by colour alone; text that does not fit at 390 px or in a longer language; missing empty, loading
  and error states; focus that disappears or is trapped; layout shift when data arrives; HTML inserted from strings;
  logic inside components that a plain function should hold.

## Sources

Where the truth is for this stack, nearest first (`docs/process/research.md`). Read by everyone looking something
up, and by the `researcher`.

- **The versions**: the framework's and the build tool's installed versions (see the stack module); the browsers the
  project supports (its browserslist or build target).
- **Web platform**: [MDN](https://developer.mozilla.org/) for HTML, CSS and browser APIs, with their browser
  support and Baseline status.
- **Accessibility**: [WCAG 2.2 Understanding](https://www.w3.org/WAI/WCAG22/Understanding/) for what a criterion
  asks; [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/) for widget patterns; each axe finding links its
  own rule page.
- **Tools**: [Playwright](https://playwright.dev/docs/intro), [stylelint rules](https://stylelint.io/user-guide/rules/),
  [Lighthouse](https://developer.chrome.com/docs/lighthouse/).
- **The framework's documentation** for the installed major version.
