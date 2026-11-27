# Sessions

**Summary:** Every chat starts with a short routine that builds context from the files, and ends with a wrap-up that
writes back what the next session needs. Skills: `start`, `wrap-up`.

## Start

Do this at the start of a session, before the first change. Keep it cheap: summaries and indexes, not whole folders.

1. Read `docs/STATUS.md`.
2. Read `docs/HEALTH.md`'s ledger. If a check is overdue, or "Noticed" has grown past ~30 lines, say so in **one
   line** in your first reply, with a proposal (`health.md`). Do not repeat it later in the session.
3. If the task belongs to an active plan, read that plan. Then read only the design topic, log topic or gotcha the
   task needs (from the indexes: `docs/DESIGN.md`, `docs/log/README.md`, headings of `docs/GOTCHAS.md`).
4. `git status` and `git log --oneline -5`: other sessions may have left work. Do not revert or tidy what you did not
   write; ask about it.
5. Reply with a short orientation only when the user asked for one or something is off (uncommitted work, failing
   health, a plan that disagrees with STATUS). Otherwise get on with the task.

## During

- One task at a time; say when the request has grown beyond what was asked and propose how to split it.
- Facts learned the hard way go to `docs/GOTCHAS.md` when they happen, not at the end.
- Decisions the user makes in chat are written down when made: in the plan, the design topic, or the ideas file.

## Wrap-up

When the user ends the session, asks for a wrap-up, a plan or task is finished, or the context is nearly full (the
`wrap_up_guard` hook says so at 90 %, once per session, with the workstation status line, and shows the user a
one-line notice; `WRAP_UP_GUARD_AT` changes the threshold, `WRAP_UP_GUARD_LOG=1` logs every run to
`<temp>/claude-context/guard.log`):

1. **Verify**: the full check passes, or what fails is named (the `check-runner` keeps its output out of the
   session).
2. **Tidy** what this session touched (`code.md`, "Tidying"), as its own commit.
3. **Write back**. After a long session, hand this step to the `scribe` (`roles/scribe.md`) with a brief of the
   decisions, results, things dropped and noticed; check what it wrote. Otherwise write it yourself:
   - `docs/STATUS.md`: rewrite Now, Next, Open questions, Health. Keep it a snapshot.
   - The active plan: tick what is done, note deviations; move it to `plans/done/` with its outcome if finished.
   - `docs/log/<topic>.md`: an entry if something was decided or finished.
   - `docs/HEALTH.md`: things noticed and not fixed, under "Noticed"; update "Last done" for any check run.
   - Design or ideas topics: decisions not yet written down.
   - If documents changed: `python docs/process/tools/check_docs.py --quiet`, and fix its errors
     (`documentation.md`, "Checking").
4. **Scaffold feedback**: did a process document mislead, a template or script fail, a rule need working around, or
   a module lack a fact this session found? If it would help every project of its kind, offer it in one line, and
   on the user's yes propose it with the `scaffold-propose` skill (generic only; project rules go to `AGENTS.md`).
5. **Commit** (`git.md`): the work, then the documentation, each with a message that says why.
6. **Report** in a few lines: what changed, how it was verified (and what is only assumed), what is left or differs
   from the request, what comes next.
