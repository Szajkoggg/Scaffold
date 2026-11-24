# Bootstrap

**Summary:** Makes a project fresh from the scaffold ready: fills in the placeholders from the codebase and the user,
and proposes the checks the project still lacks. Run once, by the first session. Skill: `bootstrap`.

The scaffolding playbook that applied the scaffold may already have done the survey, the merge of existing agent
rules and the questions: reuse them, do not repeat them.

## Steps

0. **Read the modules** listed in `AGENTS.md`, "Modules": their documents give the stack's default commands, tools
   and health checks. Use them as the proposals below, adjusted to what the project actually has. A module's
   "Repository setup" section (lines for `.gitignore`, `.gitattributes`, settings to verify) is applied once in
   step 4; from then on those files are the project's.
1. **Survey** the repository (a subagent for anything larger than a few folders): languages, frameworks, build and
   test tools, entry points, the main modules and how they depend on each other, existing docs and agent files
   (`CLAUDE.md`, `AGENTS.md`, `.cursorrules`, `.github/copilot-instructions.md`).
2. **Merge existing agent rules**: rules found in other agent files move into `AGENTS.md`; `CLAUDE.md` keeps only its
   `@AGENTS.md` line. Show the user what moved.
3. **Ask the user** in one message, with your guesses filled in for them to confirm or correct:
   - what the project is, for whom, in what state;
   - the quick check, the full check and how to run it (proposed from the survey);
   - anything in "Who decides what" that differs for this project;
   - the performance budgets that matter, if any.
4. **Fill in** `AGENTS.md` (every `{{placeholder}}`: what this is, where things are, commands, rules the code keeps),
   `docs/WORKING.md`, `docs/STATUS.md` and `docs/DESIGN.md` (a first topic file for the architecture, from the
   survey). In `docs/WORKING.md`, "Size triggers", note where the stack needs other triggers than `code.md`'s defaults.
   Start `docs/GLOSSARY.md` with the domain's main concepts from the survey; where the code already uses synonyms
   for one concept, list them under "Not" and add a line to "Noticed" (principle 6).
5. **Tune the health ledger** in `docs/HEALTH.md` to the stack: remove what does not apply, name the tool for each
   check.
6. **Propose what is missing**, one line each with a recommendation, and do only what the user accepts:
   - a quick and a full check command, if there are none;
   - static analysis with correctness rules (`code.md`);
   - a boundary check for "Rules the code keeps";
   - quieter output for checks that print too much;
   - module `AGENTS.md` files for large modules;
   - the worst breaches of the principles (`principles.md`) the survey saw, as a first `health-check` plan.
7. **Verify**: `python docs/process/tools/check_docs.py --strict` passes (no placeholders left, links and paths
   right); `CLAUDE.md` is `@AGENTS.md`; the check commands run. If the project keeps documents outside the scaffold's
   folders, add their indexes or exclusions to `docs/check-docs.json` (`documentation.md`, "Checking").
8. **Commit** the scaffold files and the filled-in documents, and wrap up (`session.md`).
