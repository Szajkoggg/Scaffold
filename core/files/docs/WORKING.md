# Working on {{PROJECT_NAME}}

**Summary:** How to set up, run, verify and measure the project. `AGENTS.md` lists the three commands used most;
everything else is here.

## Setup

{{Prerequisites and their versions; first-time setup steps.}}

## Running

{{How to start the project, its options and where output goes.}}

## Verifying

| Level | Command | Takes | When |
|---|---|---|---|
| Quick | {{command}} | {{time}} | While working: the checks of what changed |
| Full | {{command}} | {{time}} | Before calling work done |

Output is kept short: the checks print failures only and write full logs to `tmp/`. {{Say how, or what still prints
too much.}}

## Static analysis

{{Tools, what they check, how to run them. Correctness rules, not style.}}

## Size triggers

<!-- The defaults are in process/code.md, "Size triggers". Note here only where this project differs, and why. -->

The defaults of `process/code.md`, "Size triggers". {{Differences for this stack, with the reason, or "none".}}

## Performance budgets

<!-- What "fast enough" means here, as numbers, and how to measure each. Empty until the project has a hot path. -->

| What | Budget | How to measure |
|---|---|---|
| {{e.g. startup, request p95, frame time}} | {{number}} | {{command or method}} |
