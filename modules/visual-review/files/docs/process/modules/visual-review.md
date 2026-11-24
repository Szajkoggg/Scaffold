# Module: visual-review

**Summary:** Changes to how something looks are judged by pictures: the same views before and after, taken under the
same conditions, judged by an independent critic, and shown to the user on a sheet readable on a phone.

## Checks

The look has no command check: pictures are judged (Review). What can be checked before they are:

- Every view the change touches has a pair with the same key, the "before" taken from the base commit.
- Both pictures of a pair have the same pixel size; a pair that differs in size is taken again, not compared.
- The pictures come from the stack module's capture command (e.g. `web-ui`'s browser capture, `unity`'s headless
  capture, `blender`'s render), run in one go for the whole set.

## Diagnosing

- **A pair differs where nothing changed**: the conditions differ: data, seed, time of day, an animation frame, fonts
  not loaded yet, window scale or display scaling, GPU or driver. Take both again in one run before believing it.
- **Two runs on one commit differ**: unseeded randomness, animations not paused, content loaded after the picture was
  taken. Fix the capture, not the judgement.
- **The critic and the user disagree**: the user decides; the reason goes into the look guide (`LOOK.md`) so the next
  round knows it.

## Health

The tools for this module's ledger row, used by the `auditor`:

| Check | Tool |
|---|---|
| Visual references | the look guide and reference pictures against what the user accepted lately; pictures of views that no longer exist removed; two capture runs on one commit give the same pictures |

## Review

- **Every change to the look** gets pictures of fixed views, before and after. A view has a **key** naming what it
  shows, in which state, at which size (`settings-panel@390`, `cliff-close@1440`); only pictures with the same key
  are compared.
- **The kind of comparison is named**: `before` (the old state), `mockup` (the design), `variant-a`/`variant-b`
  (alternatives), `result` (a new view with nothing to compare against).
- **Same conditions**: the same data, seed, size and settings for both pictures of a pair; the "before" is taken
  from the base commit, not remembered.
- **References**: the user's targets per topic live in the folder `AGENTS.md`, "Where things are" names, with a look guide (`LOOK.md`: what
  the user accepts and rejects, and why) where there is one.
- **Rounds**: build, take the pictures, have them judged by the `visual-critic` (not told what to expect), fix,
  repeat; three rounds at most. Show the user the result when nothing is open, or after the third round with what
  remains listed.
- **Variants** when no answer is clearly better: two or three versions side by side for the user to choose; when one
  is justifiably better, build that one and say why.
- **The sheet**: one column, labelled, before above after, for a phone; with what the critic found and what was done.

## Agents

| Agent | Role | Runs at |
|---|---|---|
| `visual-critic` | [roles/visual-critic.md](../roles/visual-critic.md) | main model, high |
