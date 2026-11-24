# Roles

**Summary:** The agents this project uses, one file each: what the agent does, what it is given, what it must not do,
and how it reports. The tools' agent files (`.claude/agents/`) are thin wrappers that point here, so every model
follows the same text.

## Core roles

| Role | Job | Writes |
|---|---|---|
| [reviewer](reviewer.md) | Independent review of a change against the principles, rules and criteria | Nothing |
| [check-runner](check-runner.md) | Runs the checks and returns a short verdict | Nothing |
| [investigator](investigator.md) | Finds the cause of one failure, with evidence; does not fix | Temporary probes only |
| [librarian](librarian.md) | Answers what was decided, built or measured, and where, with sources | Nothing |
| [scribe](scribe.md) | Writes the wrap-up documents and drafts the commit message | Documents only |
| [auditor](auditor.md) | Surveys the chosen health checks and returns findings | Nothing |
| [measurer](measurer.md) | Runs repeatable measurements and returns a table | Temporary harnesses only |
| [researcher](researcher.md) | Answers one question about tools, APIs or practice from the nearest sources, with versions and sources | Nothing (probes in a temporary folder) |

Modules add roles of their own; each is listed in its module's document (`AGENTS.md`, "Modules").

## Rules for every role

- **Do only the role.** A role that reports does not fix; a role that writes documents does not change code.
- **Stack knowledge comes from the modules.** Before working, read the section of each module document
  (`AGENTS.md`, "Modules") that your role names, e.g. "Checks" for the check-runner.
- **Report the conclusion, not the material**: the caller's context is the expensive one. Long output goes to `tmp/`
  and is named by path.
- **Say what you did not do or could not check**, and why.
- **Leave nothing running** and nothing behind except what the report lists.

## Calling a role

- **Claude Code**: the subagent of the same name (`.claude/agents/<role>.md`).
- **Codex, or any tool without subagents**: run the role in a fresh session, either a new chat or a non-interactive
  run of the tool (for Codex, `codex exec`) with the prompt "Follow `docs/process/roles/<role>.md`." and the inputs
  the role asks for. Read its report back from its output.
- **The brief** gives what the role's "Inputs" section asks for, and never the caller's own conclusions when the role
  is meant to judge independently (reviewer, critics).
