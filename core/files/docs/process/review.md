# Review

**Summary:** An independent reviewer (one that did not write the change and is not told what to expect) reads a
change, or a plan before it is approved, against the principles, the project's rules and the task's criteria. Asked
for by the user, offered at the end of a plan, and offered for a larger plan before approval. Skill: `review`; the
role: `roles/reviewer.md`.

## Asking for a review

- Give the reviewer **what** to review (a commit range, files, or a plan before approval) and **the criteria** (the
  plan the change carries out, the request), never your own conclusions or what you expect it to find.
- **Uncommitted work**: `git diff` leaves out new files, so name them too (`git ls-files --others
  --exclude-standard` lists them). Read-only: do not stage them for the review.
- Run it as `roles/README.md`, "Calling a role", says: the `reviewer` subagent in Claude Code, a fresh session
  elsewhere.
- **Specialised reviews** come with modules and run beside the general one when a change is in their area: the
  `visual-critic` for changes to the look, the `security-reviewer` for changes to the attack surface.
- **A second reviewer from another model family**, offered for a change to security, data or a public interface
  when the other tool is installed: the same role and brief through `codex exec` from Claude Code, or `claude -p`
  from Codex. Models of one family share blind spots.

## Reviewing a plan

Offered in the message that shows a plan for approval (`planning.md`, "Writing one") when the plan spans sessions
or changes data, a public interface or the architecture; for any plan on the user's request. On a yes, the reviewer
gets the plan file alone; its fix findings are made in the plan, and its decisions go into the plan's "Open questions"
with the reviewer's recommendation as the default.

## Acting on the findings

- **fix** findings: make them, and list them in a line each.
- **decision** findings: put them to the user with the options and the reviewer's recommendation; nothing is changed
  until the user answers.
- Before acting on a finding, open its file and line: the problem is there as described. A finding that is not, or
  that you think is wrong: say why in the report; never drop it silently.
- At most three rounds: review, fix, review again, each new round given the previous findings and what was done
  about them. Later rounds raise the bar (`roles/reviewer.md`, "Later rounds"). After the third, report what remains.
- Report the findings to the user with what was done about each, and the reviewer's "Noticed" lines (to
  `docs/HEALTH.md`, "Noticed", if they are worth keeping).
