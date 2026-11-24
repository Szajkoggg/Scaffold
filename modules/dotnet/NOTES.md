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
- **The templates' `Directory.Build.props` did not load** (MSB4024): its comment held a command with two hyphens in a
  row, which XML comments forbid. Fixed; every XML file in the scaffold now parses.
- **Analyzers inside Unity** (the same core in a clone of its Unity project, Unity 6000.4, SDK 11.0.100): analyzer
  DLLs labelled `RoslynAnalyzer` in the core's asmdef folder run on that assembly and on every assembly referencing
  it (+77 warnings elsewhere). Shared files give the same counts for the rules both report (S2234, S2681, S3358,
  S3887); several Sonar rules never fire in Unity. Microsoft.VisualStudio.Threading.Analyzers 18.x needs Roslyn 4.11
  against Unity's 4.3 (CS9057) and does not run. Unity ignores `.editorconfig`; a `*.globalconfig` beside the asmdef
  sets severities for that assembly, and errors stop the batchmode compile. **Not adopted**: Unity finds nothing
  the .NET build misses, and adds noise and a version trap.
- **Microsoft.Testing.Platform** (NUnit3TestAdapter 6.3.1 with `EnableNUnitRunner`, the TrxReport and HangDump
  extensions 2.5.3): the commands in the module's Checks and Diagnosing. Without the `global.json` runner entry,
  SDK 10 and later refuse a project switched to it.
- **Shrink-only baseline**, shipped as `tools/dotnet/check_baseline.py`: a ~50-line script reading the build's SARIF (`<ErrorLog>...sarif,version=2.1</ErrorLog>`;
  csc does not create the folder) into rule, file and count, compared with a committed TSV: 258 lines for 877
  findings (173 with S1104 off and S3776 left out); a planted warning shows as new, a fixed one as stale. The shipped script was then tested on a
  build of the templates (Sonar 10.37, VS Threading 18.12.1): init, new, stale, shrink, a shrink refused while a new
  finding exists, and a fixed finding coming back.

## Open

None.

## Out of scope (decided; revisit when a project asks)

- `dotnet format` stays out (no formatter by default); revisit if a project asks for one.
