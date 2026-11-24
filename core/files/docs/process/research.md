# Research

**Summary:** Look it up rather than guess. When a fact is not already certain, take it from the source closest to
the truth: the project, the tool's own help, the installed code, the documentation for the installed version, then
the web; a quick run settles what reading cannot. Facts found are written down, with their source, so no one looks
them up twice.

## When to look something up

- An API, a command-line flag, a setting or a file format not already confirmed in this session.
- Anything that depends on a version, or changes fast: tools, frameworks, cloud services, model APIs. Your training
  data is older than the tools installed; assume newer versions exist.
- An error message you do not recognise.
- Before recommending a library, a version, a tool or a pattern as current practice.
- Security-relevant behaviour.
- Any claim you would hedge with "I think" or "usually".

## Where to look, nearest to the truth first

1. **The project**: the installed versions (lock files, `ProjectVersion.txt`, `--version`), its code, its documents
   (`docs/`, the module documents' "Sources"), the librarian for what was decided before (`roles/librarian.md`).
2. **The tool itself**: `--help`, subcommand help, `--list-*` options, the CLI's own introspection.
3. **The installed code**: type definitions, the package's source, its changelog, in the version the project uses.
4. **The official documentation for that version**: the documentation the module documents name; documentation MCP
   servers (`context.md`, "Tools"); the vendor's reference and release notes.
5. **The web**: official sources and release notes first, then issue trackers and discussions, forums and blog posts
   last. Note the date: an answer for an older major version can be wrong for this one.
6. **A probe**: the smallest run that answers the question (a scratch project, one command, a test), in a temporary
   folder. A one-minute run beats an hour of reading, and it is the only proof that the answer holds here.

A question that needs several pages or searches goes to the `researcher` (`roles/researcher.md`), so the pages stay
out of the session and only the answer comes back.

## Writing it down

- **Reports say what is verified**: "verified: ran it", "verified: docs for 5.2", or "assumed: not checked". An
  assumption is never presented as a fact.
- **A fact that cost time** goes where the next session finds it: `docs/GOTCHAS.md` for a trap, the design topic
  for a decision, a comment at the code for a non-obvious API behaviour; with the source (link, version, date).
- **Generic findings about a tool or stack** (true for every project using it) are proposed to the scaffold with the
  `scaffold-propose` skill, so every project's module documents get them.
