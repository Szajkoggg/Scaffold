# Playbook: work through the proposals

**Summary:** In the scaffold repository: the open `proposal` issues (and any files waiting in `proposals/`) are read,
decided with the user, and either built into the scaffold or closed with the reason.

## Steps

1. **Collect**: `gh issue list --label proposal --state open`; files in `proposals/` are filed first (`propose.md`,
   step 4) or handled the same way and deleted.
2. **Sort** by area (core, a module, workstation, playbooks) and merge duplicates (close the later one, pointing to
   the earlier).
3. **Judge each one** against `AGENTS.md` (generic content only, one place for each workflow, the ownership
   contract) and the principles: recommend accept, change or decline, with the reason. Present them to the user
   together, the recommendations first.
4. **Accepted**: build it as any scaffold change (test it by applying to a throwaway folder: `AGENTS.md`, "Test a
   change"); the commit closes the issue (`Closes #<n>`). A change to an owned file reaches projects at their next
   update; say in the commit what they will see.
5. **Declined**: close the issue with the reason (`gh issue close <n> --reason "not planned" --comment "<why>"`), so
   the next project proposing the same finds the answer.
