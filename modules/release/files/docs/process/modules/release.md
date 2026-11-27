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

- A release is a plan from `docs/process/templates/release.md`: audit, close the gaps, bump, check the package,
  hand over.
- The `release-auditor` prepares it: the version bump, the changelog section, the breaking changes found.
- The user decides; tagging and publishing are done only when the user asks, in that session.

## Checks

- **Each change**: a user-visible change has its line under "Unreleased" in the same commit (the reviewer checks it, "Review").
- **Each release**: the package as the registry receives it, installed in a clean folder and used the way the README
  says (the template's step 4). What it holds: `npm pack --dry-run`, `dotnet pack` then the `.nupkg` opened as a
  zip, `python -m build` then the wheel listed (`unzip -l`).

## Diagnosing

- **A user is broken by an upgrade**: `git diff <old tag>..<new tag>` over the public interface finds the change;
  it was breaking if the changelog did not warn them. Add the missing line and what to do, and decide with the user
  whether a fix release restores the old behaviour.
- **The published package differs from the repository**: list what was packed (above); the usual causes are the
  ignore or include rules of the packer (`files` in `package.json`, `.npmignore`, the project file, `MANIFEST.in`) and
  generated files not built before packing.

## Health

The tools for this module's ledger row, used by the `auditor`:

| Check | Tool |
|---|---|
| Releases | "Unreleased" in `CHANGELOG.md` against `git log <last tag>..HEAD`: user-visible changes without a line; deprecations past the release that was to remove them |

## Review

Beyond the principles, look for: a user-visible change without its line under "Unreleased", or a line written about
the code rather than for users; a change to the public interface (above) not marked as breaking, or one that could
have been made without breaking; a version bumped by hand outside a release; a deprecation without the release that
removes it.

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
