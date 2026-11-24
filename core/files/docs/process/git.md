# Git

**Summary:** Explicit staging, commits that say why, nothing touched that this session did not change, and nothing
pushed unless the user asks.

- **Stage explicit paths.** Never `git add -A` or `git add .`: other sessions and tools leave files in the tree.
- **Do not touch what you did not change.** Uncommitted changes you did not make are not reverted, tidied or
  committed; ask about them.
- **Commit messages**: a subject line in the imperative (about 70 characters at most) and a body that says why, and
  the key numbers where there are any (a measurement, a test count). The diff says what.
- **Commit granularity**: one logical change per commit; tidying and documentation in commits of their own. Each
  commit passes the quick check.
- **Branches**: experiments that may be thrown away go on a branch. Unfinished work that must wait goes on a
  `wip/<name>` branch with a note, not left uncommitted.
- **Never**: push, force-push, rebase shared history, amend a pushed commit, or skip hooks, unless the user asks
  for it in this session.
- **Secrets** never go into a commit. If one is found in the tree, stop and tell the user.
