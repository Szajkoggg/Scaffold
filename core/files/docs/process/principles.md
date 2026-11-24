# Principles

**Summary:** The nine principles every project holds its code, documents and agents to: clean, long-lived, scalable,
without slop, diagnosable, with one vocabulary, simple, cheap in tokens, with its context reachable. Each has its
rules and the signs that it is being broken. How they are applied day to day is in `code.md`.

The user decides what the product does; **the code is the agent's**. Keeping it to these principles is part of every
task, not a favour to be asked for. Within a task's scope the agent fixes what breaks them; beyond it, the agent
notes it in `docs/HEALTH.md`, "Noticed" (`code.md`, "Tidying").

## 1. Clean code

The code says what it does, simply.

- Names say what a thing is or does; a reader does not need the history to understand them.
- A function does one thing; a file holds one responsibility. Both stay small enough to hold in mind
  (triggers: `code.md`, "Size triggers").
- A value with a meaning is named once, in one place, not scattered as literals.
- Knowledge lives in one place: duplicated logic is merged when it changes for the same reason.
- Comments say why, never what; a comment the code contradicts is fixed or deleted in the same change.

**Signs**: duplication; files and functions too large to hold in mind; magic numbers and repeated literals; comments
that disagree with the code; names that need a comment to explain them.

## 2. Longevity

The code stays correct as it changes.

- The layering rules in `AGENTS.md`, "Rules the code keeps", are kept, and checked by a tool where the stack has one.
- Errors are handled where something can be done about them, otherwise passed on with context; never swallowed.
- Type safety is not worn away: escapes (`any`, casts, the non-null `!`, `dynamic`, `# type: ignore`, ...) need a
  reason in a comment, and are the exception a reviewer questions.
- A temporary workaround is marked where it lives, `WORKAROUND: <why> - remove when <condition>`, and listed in
  `docs/HEALTH.md`, "Noticed". An unmarked workaround is a bug.
- The code describes the present. Its history belongs in commits and `docs/log/`, not in comments ("was X before",
  "changed for ticket Y", "new version").
- Behaviour that matters is pinned by tests, so a later change that breaks it fails a check.

**Signs**: imports across a boundary; empty catch blocks or errors turned into `null` without a word; type escapes
without a reason; workarounds no one remembers; comments about what the code used to do.

## 3. Scalability

The code holds up as the data and the load grow.

- Hot paths do not block: no synchronous I/O, long computations or waits on the event loop, UI thread or frame loop
  where the stack is asynchronous.
- Work grows with the change, not with the whole: incremental updates where a full recomputation would repeat work.
- Everything that grows has a bound: caches, queues, lists, logs, retries, history. The bound and what happens at it
  are stated.
- Measure before optimising; budgets for the hot paths are in `docs/WORKING.md`, and a change on a hot path is
  measured against them (`code.md`, "Performance").

**Signs**: blocking calls on a hot path; recomputing everything after a small change; unbounded collections and
caches; queries or loops whose cost grows with total data instead of the request.

## 4. Anti-slop

Nothing is there without a reason.

- No defensive code for states that cannot happen; validate at the boundaries, trust the inside.
- No speculative generality: no parameters, options, layers or abstractions for needs that do not exist yet.
- No comments that repeat the code; no filler in documents, reports or commit messages.
- One pattern per task (principle 6): a new way of doing something replaces the old one, or is not added.
- Tests prove something: each would fail if the behaviour it names broke. No tests that only assert "not null",
  snapshot everything, or test the mocks.
- No leftovers: debug output, commented-out code, unused files, "v2" copies.

**Signs**: try/catch around code that cannot throw; null checks on values that are never null; config options no one
sets; wrappers that only forward; tests that pass whatever the code does; words like "enhanced", "robust",
"comprehensive" doing the work of facts.

## 5. Diagnosability and reproducibility

When something goes wrong, an error or a log line says what happened and where, and the failure can be made to
happen again.

- An error message names what failed, on what (the id, the path, the input that matters) and, where it helps, what
  to do. Not "failed" or "invalid input".
- Errors passed on keep their cause (wrapping, not replacing).
- Log lines carry context (operation, ids) at the right level; no secrets or personal data in them.
- What a failure depends on can be fixed: seeds for randomness, pinned versions, recorded inputs. A bug fix starts
  with a test or a command that reproduces it.

**Signs**: errors without context; a stack trace lost by re-throwing; logs that say something happened but not to
what; failures no one can repeat.

## 6. One vocabulary, one way

One name for one concept and one path for one task, in the code and the documents.

- Each domain concept has one name, used the same way in code, documents, UI text and conversation; the names are
  in `docs/GLOSSARY.md`. A new concept gets its entry when it is introduced.
- Each task has one way: one helper, one pattern, one command (`docs/WORKING.md`). A second way is a refactor
  proposal, not a quiet addition.
- Each fact has one place in the documents (`documentation.md`, "What goes where"); other places link to it.

**Signs**: synonyms for one thing ("user", "account", "member"); two helpers that do the same; two ways to run the
tests; the same fact written in two documents that have started to disagree.

## 7. KISS

The simplest thing that works, and nothing cleverer.

- The straightforward solution first; complexity is added when a real need or a measurement asks for it, with the
  reason stated.
- An abstraction waits for its second or third use.
- The standard library and the dependencies already there before a new dependency; boring technology before novel.
- A reader new to the code can follow it.

**Signs**: indirection that a reader has to trace through; generic frameworks for one case; clever one-liners;
a new dependency for a few lines of code.

## 8. Token usage care

Every token an agent reads is paid for again in every later turn.

- Documents are short and start with a summary; files stay within their limits (`documentation.md`, "Growth
  rules"; `code.md`, "Size triggers").
- Commands print failures, not successes; full output goes to `tmp/`.
- Agents read indexes and summaries first, search before reading whole files, and send broad sweeps to a subagent
  (`context.md`).

**Signs**: checks that print thousands of passing lines; documents read end to end to find one fact; files past
their limits; the same context rebuilt at every session.

## 9. Reachable context

Everything an agent needs is reachable from `AGENTS.md` in a few steps, and nothing important lives only in a chat.

- `AGENTS.md` points to everything; every folder of documents has an index; every document starts with a summary.
- Decisions are written down when they are made (design, ideas, plans, log), with checkable facts (file, symbol,
  commit).
- Modules with rules of their own have their own `AGENTS.md`.
- `check_docs.py` keeps links, indexes and summaries true (`documentation.md`, "Checking").

**Signs**: an agent asking what was already decided; knowledge only in someone's head or an old chat; documents no
index links to; links that lead nowhere.

## When principles pull apart

- **KISS before scalability**, until a measurement or a stated budget says otherwise.
- **Clean before short**: splitting a function to keep it clear is worth a few more lines.
- **Longevity before speed of delivery**: a workaround is allowed only marked and listed (principle 2).
- When a trade-off is not obvious, say which principles pull against each other and recommend one way.
