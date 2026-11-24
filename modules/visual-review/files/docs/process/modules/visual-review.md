# Module: visual-review

**Summary:** Changes to how something looks are judged by pictures: the same views before and after, taken under the
same conditions, judged by an independent critic, and shown to the user on a sheet readable on a phone.

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

| Agent | Role |
|---|---|
| `visual-critic` | [roles/visual-critic.md](../roles/visual-critic.md) |
