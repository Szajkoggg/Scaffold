# Documentation

**Summary:** What goes where, the shape every document has, and the growth rule each kind of document follows, so
the documentation stays cheap to read as the project grows.

## What goes where

| Knowledge | Goes to |
|---|---|
| A rule every session must follow | `AGENTS.md` (one line; the detail in `docs/`) |
| A rule for one module | That module's `AGENTS.md` |
| Where things stand now | `docs/STATUS.md` |
| How the system is built and why | `docs/design/<topic>.md`, listed in `docs/DESIGN.md` |
| An idea, or the user's decision on one | `docs/ideas/<topic>.md` |
| Work being planned or done | `docs/plans/` |
| What was done or decided, when | `docs/log/<topic>.md` |
| A domain term and its name in code | `docs/GLOSSARY.md` |
| A quirk that cost time | `docs/GOTCHAS.md` |
| How to set up, run, verify, measure | `docs/WORKING.md` |
| Something noticed and not fixed | `docs/HEALTH.md`, "Noticed" |
| How the code is used by its users | `README.md` |

A change to behaviour, an interface or a command updates its documentation in the same commit.

**When a document and the code disagree**, change neither on your own: name the mismatch to the user and ask which
one is right. The code may have the bug, or the document may be ahead of it. A design topic says what is built and
what is planned (`Planned:` in front of what is not built yet); a planned part is never deleted to match the code.

## Shape

- Every document starts with its title and a `**Summary:**` line of one to three sentences. Indexes repeat it, so a
  reader can choose without opening the file.
- Headings that name their content, so a reader can jump by heading.
- Facts are checkable: name the file, symbol or commit. Cite a section as `file.md, "Heading"`, never by line number.
- Short sentences; tables for anything with the same fields per row.
- Rules and process text state what is true now, as if it had always been so. What was renamed, removed or done
  before belongs in `docs/log/` and commits: a session reads "X is no longer used" as a hint that X exists. A guard
  against what an agent would do anyway stays, written as a plain rule ("stage explicit paths, never `git add -A`").

## Growth rules

| Document | Grows by | Limit | Past the limit |
|---|---|---|---|
| `AGENTS.md` | Rules, one line each | ~150 lines | Move detail to `docs/`, module rules to the module's `AGENTS.md` |
| `STATUS.md` | Rewritten, never appended | ~60 lines | Detail goes to the plan or topic it links to |
| Indexes (`DESIGN.md`, READMEs) | One line per entry | ~100 entries | Group entries under headings, or add a sub-index |
| Topic files (`design/`, `ideas/`) | Edited in place | ~40 KB | Split along headings; update the index |
| `log/<topic>.md` | Appended | ~40 KB | Older entries to `log/<topic>/<year>.md` |
| `GOTCHAS.md` | Appended | ~40 KB | Split into `gotchas/<area>.md` with this file as index |
| `GLOSSARY.md` | One row per term | ~100 rows | Split by area into `glossary/<area>.md` with this file as index |
| `HEALTH.md`, "Noticed" | Appended, pruned | ~30 lines | Propose a health-check plan |
| Plans | One file each | — | Finished ones move to `plans/done/` |

Agents keep these limits when writing, and mention a file past its limit once (`health.md`).

## Checking

`python docs/process/tools/check_docs.py` (`--quiet` prints one line when clean; `--strict` fails on warnings too;
`--list-rules` names the rules). It finds every Markdown file itself (tracked and untracked-not-ignored), so a new file
is checked the moment it exists. What each rule applies to is set by path globs, not by a list of files.

| Rule | Level | What |
|---|---|---|
| `link` | error | A relative link points to a file or folder that does not exist |
| `anchor` | error | A link's `#anchor` matches no heading in the target |
| `path` | error | A backticked repository path (with a `/`, and a file extension or a trailing `/`) does not exist |
| `summary` | error | A document under `docs/`, or an `AGENTS.md`, has no `**Summary:**` line near the top |
| `index` | error | A file in an indexed folder is not linked from its index (`design/` → `DESIGN.md`, `ideas/`, `log/`, `plans/`, `process/` → their READMEs, top-level `docs/*.md` → `docs/README.md`, `process/modules/*.md` → `AGENTS.md`'s Modules list) |
| `limit` | warning | A file or section is past its limit in "Growth rules" |
| `placeholder` | warning | A `{{placeholder}}` is left in `AGENTS.md` or a top-level document |

Code blocks and HTML comments are not prose: links and paths in them are not checked.

**Run it** at wrap-up when documents changed, and in the Documentation health check. A project that has CI or a
pre-commit hook can add it there.

**A project adapts it** in `docs/check-docs.json` (project-owned; the defaults are in the script):

```json
{
  "exclude": ["vendor-docs/**"],
  "ignore_paths": [{"path": "config/local.yaml", "why": "created by setup, not in the repository"}],
  "indexes": [{"index": "docs/api/README.md", "files": "docs/api/*.md", "except": []}],
  "limits": [{"files": "docs/HEALTH.md", "section": "Noticed", "max_lines": 50}],
  "summary_exempt": ["docs/generated/**"]
}
```

Scaffold modules add their own rules in `docs/process/check-docs.d/<module>.json` (same format, owned by the
scaffold), read before the project's file. Lists are added to the defaults; an `indexes` or `limits` entry with the same `files` (and `section`) as a default
replaces it, and `"disabled": true` removes it. A path named on purpose although it does not exist goes into
`ignore_paths` with why, never around the check.
