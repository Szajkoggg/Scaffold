# Context and tokens

**Summary:** Context is built from the files, from the general to the specific, and only as far as the task needs.
Every token read is paid for again in every later turn of the session.

## Building context

- Start from `docs/STATUS.md`, then the plan, then the one topic the task needs (`session.md`, "Start").
- Read **indexes and summaries first**; open a file only when its summary says it is needed.
- **Search before reading**: find the symbol or heading, then read that part of the file, not the whole file.
- Logs are read by their entry list, never end to end.
- A sweep across many files (where is X used, how is Y done everywhere) goes to a subagent that returns the
  conclusion, not the file contents.
- A question about the project's history (what was decided, tried, measured, and where it is) goes to the
  `librarian` (`roles/librarian.md`) rather than being answered by reading the records in the session.

## Keeping it small

- Command output is short: quiet flags, failures only, full logs to `tmp/` and read from there when needed.
- Do not re-read a file you just wrote, or re-derive what is already established in the conversation.
- Long sessions drift: when the task changes, wrap up and suggest a fresh session rather than carrying a long history.

## Tools

Use a command-line tool or a script before an MCP server, for engines and editors too (Unity, Blender, browsers,
databases).

- **Why**: a command can be rerun, written into `docs/WORKING.md` and a plan, and reproduces a result (principles 5
  and 9); it runs headless without taking the user's focus; it works the same for every agent tool and in CI; its
  output can be kept short, while MCP tool lists and image-heavy replies cost tokens on every turn (principle 8).
- **MCP is for what no command can do**: inspecting a live, interactive session, or a tool with no CLI. Say in a line
  why the MCP server was needed. If the same MCP call recurs, turn it into a script.
- **Documentation MCP servers are the standing exception**: they only read, change nothing, and searching a
  vendor's documentation has no CLI. Use them freely for lookups (`research.md`).
- **A script is the better answer to a repeated MCP call**: what an agent did once through an MCP server becomes a
  command the next session can run.
- The stack modules name each tool's CLI (e.g. `unity`, `blender -b`).

## Making the project cheap to read

These are the project's side of the bargain; propose them when missing:

- Summaries at the top of every document; indexes that repeat them.
- Small files (`code.md`, "Size triggers"; `documentation.md`, "Growth rules").
- Module `AGENTS.md` files, so module rules load only where they apply.
- Checks with quiet output.
