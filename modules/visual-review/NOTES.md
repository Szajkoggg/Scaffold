# visual-review: what this module should bring

**Summary:** Changes judged by pictures: before/after shots of the same views, an independent visual critic, review sheets readable on a phone.

Not delivered to projects: design notes for writing the module.

- Process: same views before and after, same conditions; pairs by view key; result for new screens.
- look-critic agent: judges against references and criteria, is not told what to expect; three rounds at most.
- Review sheet generator: one column, labelled, for a phone.
- Source: an earlier game project's review rule and look critic, and an orchestrator project's review-material standard.

## Open

- The review-sheet generator (one column, labelled, before above after, for a phone) waits for a project with a
  working capture: its input is the capture's output (file names by view key), so it is built against a real one.
  Both captures now run (`web-ui`'s browser capture; `unity`'s `HeadlessCapture.cs`, verified under URP).
- The module document has no `## Sources` yet: written with the first project, naming the capture tools' installed
  versions and help, the project's capture scripts, and the reference pictures.
