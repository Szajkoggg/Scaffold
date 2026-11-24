# Module: release

**Summary:** For libraries and tools other people install: semantic versioning, a changelog kept with the changes,
and a release prepared by the `release-auditor` and published only by the user.

## Versioning

- **Semantic versioning**: major for a breaking change to the public interface, minor for a new feature, patch for a
  fix. Before 1.0, a minor bump may break, and says so.
- **The public interface** is what the project's users can reach: exported API, command-line options, file formats,
  configuration keys, documented behaviour. Changing any of it in a way that breaks a user is breaking.

## Changelog

- `CHANGELOG.md`, newest first, an "Unreleased" section at the top; each user-visible change gets a line in the same
  commit, under Added, Changed, Deprecated, Removed, Fixed or Security.
- Lines are written for the users: what changed for them, not how it was built.

## Releasing

- The `release-auditor` prepares it: the version bump, the changelog section, the breaking changes found.
- The user decides; tagging and publishing are done only when the user asks, in that session.

## Agents

| Agent | Role | Runs at |
|---|---|---|
| `release-auditor` | [roles/release-auditor.md](../roles/release-auditor.md) | smaller model, medium |

## Sources

Where the truth is for this stack, nearest first (`docs/process/research.md`). Read by everyone looking something
up, and by the `researcher`.

- [Semantic Versioning](https://semver.org/) for what each version number means.
- [Keep a Changelog](https://keepachangelog.com/) for the changelog's form.
- The package registry's own documentation for publishing (npm, NuGet, PyPI).
