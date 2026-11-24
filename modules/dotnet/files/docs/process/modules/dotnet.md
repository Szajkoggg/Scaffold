# Module: dotnet

**Summary:** C# and .NET: nullable on, correctness analyzers whose bug-finding rules fail the build and whose other
findings are counted, NUnit as the test framework, quiet test runs judged by exit code and results file. Also the
rules for C# shared with Unity (`netstandard2.1`, C# 9). Read by the core agents for their sections below.

## Rules

- **The `dotnet` CLI** for everything: build, test, package queries, tools (core rule: `context.md`, "Tools").
- **Nullable reference types are on.** `!` (the null-forgiving operator) needs a reason in a comment, like every type
  escape (principle 2). Existing code without nullable turns it on per project or per file (`#nullable enable`), new
  code always has it.
- **New code adds no warnings.** Rules marked `error` fail the build; the others are warnings the project counts; a
  change that raises the count is fixed before it is committed.
- **Errors keep their cause**: `throw;` not `throw ex;`; wrapping exceptions pass the inner one; no empty `catch`
  (principle 5).
- **No blocking on async code** (`.Result`, `.Wait()`, `GetAwaiter().GetResult()`), no `async void` except event
  handlers that must be (principle 3). Cancellation tokens are passed on.
- **Time and randomness are injected** (`TimeProvider`, a seeded `Random`), not read from `DateTime.Now` or a shared
  `Random` inside logic, so tests are deterministic (principle 5).
- **Tests use NUnit**, the framework Unity's test runner uses, so C# tests read the same everywhere (principle 6).
  Tests run in parallel; a test that shares state says so with `[NonParallelizable]`.
- **Measurement harnesses** (probes that print tables) are `[Explicit, Category("Probe")]` tests: never in the
  suite, run by name by the `measurer`.
- **Changing the target framework or the SDK major version** is the user's decision (an architecture change).

### C# shared with Unity

Code compiled both by Unity and by a .NET project (a pure C# core, `unity.md`, "Rules"):

- The .NET project targets `netstandard2.1` with `LangVersion` 9.0, the language Unity compiles; otherwise code
  passes `dotnet test` and fails in Unity.
- Public fields are Unity's convention for serialized data: set Sonar's S1104 to `none` there, with that reason.
- The sources have one home (the Unity package or the Unity project's Assets folder); the .NET project includes them
  (`<Compile Include="..." />`), never a copy.

## Repository setup

Applied once by the bootstrap; the files are the project's afterwards.

- **`Directory.Build.props`** from `docs/process/tools/dotnet/Directory.Build.props`, at the repository root or the
  solution's folder, with the analyzer versions filled in (`dotnet package search <package> --exact-match`).
- **`.editorconfig`**: `docs/process/tools/dotnet/analyzers.editorconfig` appended (with `root = true` at the top
  if the file is new).
- **`global.json`** pinning the SDK major version the project uses, with `"rollForward": "latestFeature"`.
- **Central package management** (`Directory.Packages.props`, `ManagePackageVersionsCentrally`) when the solution
  has more than one project: one version per package (principle 6).
- **`.gitignore`** lines:

  ```
  bin/
  obj/
  TestResults/
  *.user
  .vs/
  ```

- **First build**: build once, count the warnings by rule, and settle the noisy ones with the user: a rule that
  clashes with a convention of the project goes to `none` under "Project decisions" in `.editorconfig`, with the
  reason; a rule that finds real problems stays, and its findings go to `docs/HEALTH.md`, "Noticed". Record the
  warning count in the health ledger's "Static analysis" row. An existing codebase is never flooded with new errors: rules marked `error`
  that fire on old code are listed and fixed in a plan, or lowered to `warning` until then.

## Checks

| Level | Command |
|---|---|
| Quick | `dotnet build <solution> -nologo -v q`, then `dotnet test <tests project> --no-build -nologo -v q --filter "<the changed area>"` |
| Full | `dotnet test <solution> -nologo -v q --logger "trx;LogFileName=tests.trx" --results-directory tmp/checks` |

- **Pass or fail is the exit code**, and the counts come from the `.trx` results file, not from console text (its
  format changes between SDK versions). A bare `--logger trx` names the file after the user and machine; give it a
  fixed name.
- **On Microsoft.Testing.Platform** (the newer runner; `global.json` holds `"test": {"runner":
  "Microsoft.Testing.Platform"}`, the test project `OutputType` Exe and its framework's runner, e.g. NUnit's
  `EnableNUnitRunner`): `dotnet test --project <tests project> --results-directory tmp/checks --report-trx
  --report-trx-filename tests.trx` (package `Microsoft.Testing.Extensions.TrxReport`). A path needs `--project`;
  `--filter` keeps its syntax; exit 8 means no test matched, 7 a hang.
- Slow tests carry `[Category("Slow")]`; the quick level adds `&Category!=Slow` to its filter, the full level runs
  them.
- Warnings: report the count; a rise is a finding (Rules).

## Diagnosing

- **"The file is locked by another process"** on build or test: a leftover `testhost` or `dotnet` process from an
  earlier or parallel run holds the DLL. Say so; wait for the other run, or ask before ending processes.
- **A hung test**: `dotnet test --blame-hang-timeout 5m` names the test and writes a dump to the results folder. On
  Microsoft.Testing.Platform: `--hangdump --hangdump-timeout 5m --hangdump-type Mini` (package
  `Microsoft.Testing.Extensions.HangDump`; the default is a full dump of hundreds of MB, and the `.trx` stays empty
  after a hang).
- **One test, with its output**: `dotnet test --filter "FullyQualifiedName~<Class>.<Test>" --logger
  "console;verbosity=detailed"`.
- **Results that differ between machines**: floating-point maths can differ across operating systems, CPUs and
  runtimes; golden files holding floats compare on one platform or with a tolerance (`testing.md`).

## Health

The tools for the core ledger's rows (`docs/HEALTH.md`), used by the `auditor`:

| Check | Tool |
|---|---|
| Dependencies | `dotnet list package --outdated`, `--vulnerable --include-transitive`, `--deprecated` |
| Warnings | The build's warning count by rule, against the count in the ledger |
| Complexity | S3776 findings: the ten most complex methods (`code.md`, "Size triggers") |
| SDK | `dotnet --list-sdks` and `global.json` against the current LTS |

## Measuring

- **BenchmarkDotNet** in its own project, built in Release, run alone; never part of the test suite.
- A running process: `dotnet-counters monitor` (CPU, GC, allocations), `dotnet-trace collect` (a trace to
  profile), installed as .NET tools.
- Allocations matter as much as time in hot paths: BenchmarkDotNet's `[MemoryDiagnoser]`.

## Review

Beyond the principles, look for: `throw ex;`; empty `catch`; `async void`; blocking on async code; `DateTime.Now`
or a shared `Random` in logic; `IDisposable` not disposed; `new HttpClient()` per call; `!` without a reason; LINQ
in hot loops; string concatenation in loops; exceptions used for control flow.

## Sources

Where the truth is for this stack, nearest first (`docs/process/research.md`). Read by everyone looking something
up, and by the `researcher`.

- **The version**: `dotnet --info` (SDKs and runtimes), `global.json`, each project's `TargetFramework`; package
  versions in the project files or `Directory.Packages.props`.
- **The tool**: `dotnet <command> --help`.
- **The installed code**: a package's XML documentation and assemblies under `~/.nuget/packages/<id>/<version>/`.
- **The documentation for that version**: [Microsoft Learn](https://learn.microsoft.com/dotnet/) (the API browser
  has a version selector; the Microsoft Learn MCP server searches it); analyzer rules: CA rules on Microsoft Learn,
  [Sonar's C# rules](https://rules.sonarsource.com/csharp/),
  [VSTHRD rules](https://github.com/microsoft/vs-threading/tree/main/docfx/analyzers).
- **Changes between versions**: the "What's new" pages of .NET and C#, and the breaking changes list per version.
