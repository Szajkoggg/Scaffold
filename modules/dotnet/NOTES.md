# dotnet: notes for the module

**Summary:** The module is written and its templates were built and measured; these are the findings behind it and
the points left open.

Not delivered to projects.

## Measured (2026-11-24)

- The templates on a small library with planted bugs: `throw ex;`, a nullable dereference, `.Result` and `async void`
  fail the build; unused members, `async void` duplicates from Sonar and complexity are warnings. S3776 fires once
  `.editorconfig` raises it.
- On a Unity project's pure C# core (37,700 lines, read-only, built in a scratch folder):
  - With `AnalysisLevel` "latest-recommended" and Sonar's defaults: ~900 distinct findings, dominated by design and
    naming rules (CA1051, CA1716, S1104). That is why the template uses `latest` and only raises chosen rules, and
    why not all warnings fail the build.
  - With the final templates: 12 errors (6 × S2234 arguments possibly swapped, 6 × S2681 missing braces), worth a
    look in that project; the largest warning groups are S1104 (public fields, Unity convention: set to none for
    Unity-shared code), S3776 (190 methods over 15), S3358 (nested ternaries).

## Open

- Analyzers inside Unity itself (Roslyn analyzer DLLs labelled `RoslynAnalyzer` in `Assets/`) so the Editor reports
  the same rules: not covered yet; the .NET project of a pure C# core covers the shared code.
- Microsoft.Testing.Platform (the new `dotnet test` runner): check how `--logger trx` and `--blame-hang-timeout`
  change when a project moves to it.
- A baseline that can only shrink (as ESLint's bulk suppressions and dependency-cruiser's known violations do, see the typescript module) would beat lowering errors to warnings on an existing codebase. Roslyn has no built-in one; candidates to evaluate: a checked-in list of suppressed diagnostics with a check that fails when an entry no longer matches.

## Out of scope (decided; revisit when a project asks)

- `dotnet format` stays out (no formatter by default); revisit if a project asks for one.
