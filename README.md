# Scaffold

**Summary:** The user's AI workflow scaffold for projects worked from console chats with Claude Code and Codex. It
sets up a workstation, scaffolds new and existing projects with working rules, a documentation structure and session
routines, and updates projects scaffolded earlier. Projects get the modules that fit them.

## Uses

| Use | How | Playbook |
|---|---|---|
| Set up a workstation | Clone this repository, open a chat in it, ask to set up the workstation | [playbooks/workstation.md](playbooks/workstation.md) |
| Scaffold a new project | In any chat: `/scaffold` (Codex: `$scaffold`) on an empty folder | [playbooks/new-project.md](playbooks/new-project.md) |
| Scaffold an existing project | `/scaffold` on a project without `.scaffold/manifest.json` | [playbooks/existing-project.md](playbooks/existing-project.md) |
| Update a scaffolded project | `/scaffold` on a project with a manifest | [playbooks/update.md](playbooks/update.md) |
| Propose an improvement from a project | `/scaffold-propose` in any project: a GitHub issue labelled `proposal` | [playbooks/propose.md](playbooks/propose.md) |
| Work through the proposals | In this repository: ask to go through the proposals | [playbooks/proposals.md](playbooks/proposals.md) |

The `scaffold` skill is installed by the workstation setup and knows where this repository lives; it picks the
playbook from the state of the folder. The agent does the judgement (modules, merges, questions); `scaffold.py` does
the file work, so the result is the same every time.

## Layout

```
scaffold.py           list / detect / apply / update / status / workstation
presets.json          named sets of modules (game-unity, webapp, asset-studio, ...)
playbooks/            what the agent does for each use
workstation/          the personal layer: skills, personal rules, status line, settings
core/                 what every project gets
modules/<name>/       stack modules (unity, dotnet, typescript, python, blender) and
                      concern modules (visual-review, web-ui, backend, release, asset-pipeline)
```

A module (and `core`) is a folder with:

| Path | Delivered to the project as |
|---|---|
| `module.json` | Not delivered: name, summary, kind, status, requires, suggests, detect (signs it fits), seed, health rows |
| `files/**` | The same path in the project |
| `skills/<name>/` | `.claude/skills/<name>/` and `.agents/skills/<name>/` (Claude Code and Codex) |
| `agents/<name>.md` | `.claude/agents/<name>.md` |
| `NOTES.md` | Not delivered: design notes while the module is a stub |

A module's rules go in `files/docs/process/modules/<name>.md`, listed in the project's `AGENTS.md` (Modules block);
its own agents' role files in `files/docs/process/roles/<agent>.md` with the Claude wrapper in `agents/`; its
docs-checker rules in `files/docs/process/check-docs.d/<name>.json`; its health checks in `module.json`'s `health`,
added to the project's ledger once. A module document never holds placeholders: it is owned and replaced on update,
so project-specific paths go in the project's `AGENTS.md`, "Where things are".

The core agents read named sections of every module document, so a stack module teaches them without agents of its
own:

| Section | Read by | Holds |
|---|---|---|
| `## Checks` | check-runner | The stack's quick and full checks, how to run them headless and quietly, their traps |
| `## Diagnosing` | investigator | Where the stack's logs are, how to reproduce and probe, its usual failure classes |
| `## Health` | auditor | The tools for each health check (outdated packages, dead code, complexity, audit) |
| `## Measuring` | measurer | How to build for timing, profile, and benchmark in this stack |
| `## Review` | reviewer, visual-critic | What to look for in this stack or area beyond the principles |
| `## Assets` | asset-builder, asset-integrator | How this tool or engine makes or imports assets |
| `## Sources` | researcher, everyone looking something up | Where the truth is for this stack: the installed version, the tool's help, the installed code, the documentation for that version |

Module status: `stub` (only `NOTES.md`), `partial` (delivers some of its content), `ready`.

## Who owns which file in a project

| Owner | Files | On update |
|---|---|---|
| The scaffold (owned) | Everything delivered that is not a seed: `docs/process/**`, skills, agents | Replaced while untouched; an edited one is offered for merging in `.scaffold/incoming/` |
| The project (seed) | `AGENTS.md`, `CLAUDE.md`, `docs/*.md`, the folder READMEs, `.gitignore`, ... (`core/module.json`, `seed`) | Copied once, never touched again; except the Modules block in `AGENTS.md` and new health rows |

A project's own rules go in its `AGENTS.md`, in a section named after the process document they extend (e.g.
"## Review"), never into owned files. The project records what it got in `.scaffold/manifest.json` (committed).

## Status

`core` is written, with seven agents. visual-review, backend, release and asset-pipeline are partial (their agents and main rules); the stack modules and web-ui are stubs (their `NOTES.md` says what each should bring). Workstation: personal
skills (`grill-me`, `scaffold`), personal rules, the status line.
