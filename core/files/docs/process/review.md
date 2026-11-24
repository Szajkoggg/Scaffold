# Review

**Summary:** An independent reviewer (one that did not write the change and is not told what to expect) reads the
diff against the principles, the project's rules and the task's criteria. Asked for by the user, and offered at the
end of a plan. Skill: `review`; the role: `roles/reviewer.md`.

## Asking for a review

- Give the reviewer **what** to review (a commit range, files, a plan file) and **the criteria** (the plan's "Done
  when", the request), never your own conclusions or what you expect it to find.
- Run it as `roles/README.md`, "Calling a role", says: the `reviewer` subagent in Claude Code, a fresh session
  elsewhere.
- **Specialised reviews** come with modules and run beside the general one when a change is in their area: the
  `visual-critic` for changes to the look, the `security-reviewer` for changes to the attack surface.
- At most three rounds: review, fix, review again. After the third, report what remains.
- Report the findings to the user with what was done about each.
