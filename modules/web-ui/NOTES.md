# web-ui: notes for the module

**Summary:** The module is written; its capture script and stylelint template were tested; these are the findings
behind it and the points left open.

Not delivered to projects.

## Tested (2026-11-24)

- `capture.mjs` with playwright-core 1.65.1 and axe-core, on the installed Edge: a page with six planted problems
  (horizontal scroll, text cut by an ellipsis, two overlapping boxes, a 16 px button, low contrast, an image without
  alt) gives each exactly once; an inline link in text is not counted; a clean page passes in light and dark; a
  missing page is "not taken" with exit 3; `--only` works.
- `stylelint.config.mjs` with stylelint 17: hex, named and function colours are errors in `app.css` and allowed in
  `tokens.css`.

## Taken from an earlier web project, changed or left out

- Its capture tool's idea (views as data, keys with the width, the before from the base commit, never blocking) is
  kept; its hand-written DevTools driver for Edge and the 492 px frame (Edge's narrowest window) are replaced by
  Playwright, which sets any viewport.
- Its layout-fault rules (cut text with fractions, overlaps) are in the capture; "a line through a box" is specific
  to diagrams and left to projects that draw them.
- Theme tokens with the utility framework's palette switched off: kept, without the Tailwind specifics.
- Texts in one catalogue with `Intl` and no library: kept as the default.
- Back closing the topmost layer: kept as a rule; the history mechanics were that project's own.

## Open

- Lighthouse in the CLI was not run here.
- Orchestrating the "before" (a worktree at the base commit, its build, a second server) is described, not scripted;
  a script may come once a project needs it often.
- Visual comparison by pixels (a diff image) is not included: the critic compares; add it if projects want it.
