# Release <version>

**Summary:** <What this release brings its users, in one sentence.> Prepared by the agent; tagged and published only
by the user.

Status: draft
Mode: attended
Template: release
Created: YYYY-MM-DD

## Goal

Version <version> is ready to publish: the version bump, the changelog section, the documentation and the checks all
agree; the user tags and publishes it.

## Context

Last release: <tag>. What is going out: <plans, features, fixes>. Registry: <npm, NuGet, PyPI, a download page>.

## Open questions

<One per item: the question, then `Default:` the recommended answer. The user's answers go into the plan at approval;
empty once approved.>

## Steps

- [ ] 1. Audit
  - Do: run the `release-auditor` from the last tag (`docs/process/modules/release.md`, "Releasing").
  - Done when: the proposed version, the breaking changes and the changelog section are in Notes, and the user
    agrees with the version.
- [ ] 2. Close the gaps
  - Do: what the audit listed: changelog lines missing, documentation not updated, tests missing for new public
    behaviour. Each its own commit.
  - Done when: the auditor's gaps are fixed or listed in Notes as accepted by the user.
- [ ] 3. Bump and write the changelog
  - Do: set the version in every place the project keeps it (the manifest, a version constant, the docs); move
    "Unreleased" to a dated `<version>` section.
  - Done when: a search for the old version finds only history; one commit, "Release <version>".
- [ ] 4. Check the package
  - Do: the full check; build the package as the registry receives it and install it in a clean folder (a scratch
    project, a fresh virtual environment), then use it the way the README says.
  - Done when: the clean install works; the package holds what it should and nothing more (no tests, secrets, local
    paths).
- [ ] 5. Hand over
  - Do: give the user the commands to tag, push and publish, in order, and the changelog section for the release
    notes. Run them only if the user asks, in this session.
  - Done when: the user has published, or decided to wait; Outcome says which.

## Stop conditions

- A decision that belongs to the user comes up (AGENTS.md, "Who decides what"): above all a breaking change, or the
  version number.
- The audit finds a breaking change not named as such in the changelog.
- The same check fails three times after attempted fixes.
- A file to commit has changes this plan did not make.

## Notes

## Outcome
