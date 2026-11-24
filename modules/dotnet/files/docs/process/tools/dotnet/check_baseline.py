"""A warning baseline that can only shrink, for bringing an existing codebase under the analyzers
(docs/process/modules/dotnet.md, "Checks").

Reads the SARIF logs the build writes (`<ErrorLog>` in Directory.Build.props) and compares the findings, counted by
rule and file, with a committed baseline: `<rule>\t<file relative to the baseline's folder>\t<count>` per line.

    python check_baseline.py <baseline.tsv> <sarif>...            check: exit 1 on a new finding or a stale entry
    python check_baseline.py <baseline.tsv> <sarif>... --shrink   lower the entries to what is left (never raise one)
    python check_baseline.py <baseline.tsv> <sarif>... --init     write a first baseline (only if there is none)

New code adds no findings: a count above its baseline fails. A count below it fails too, as stale, until --shrink
lowers it, so a fixed finding can never come back unnoticed. Findings in files outside the baseline's folder
(generated code in obj/, packages) are not counted. Python 3.9+, standard library only.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

Key = tuple[str, str]  # (rule, file)


def file_of(uri: str) -> Path:
    parsed = urlparse(uri)
    return Path(url2pathname(unquote(parsed.path))) if parsed.scheme == "file" else Path(unquote(uri))


def findings(sarifs: list[str], root: Path) -> Counter:
    counts: Counter = Counter()
    seen = set()  # a file compiled by two projects (or two target frameworks) reports each finding twice
    for sarif in sarifs:
        if not Path(sarif).is_file():
            sys.exit(f"{sarif}: no such SARIF log; build first (<ErrorLog> in Directory.Build.props, and its folder "
                     "must exist: the compiler does not create it)")
        log = json.loads(Path(sarif).read_text(encoding="utf-8-sig"))
        for run in log.get("runs", []):
            for result in run.get("results", []):
                if result.get("level") not in ("warning", "error") or result.get("suppressions"):
                    continue
                location = result["locations"][0]["physicalLocation"]
                path = file_of(location["artifactLocation"]["uri"]).resolve()
                try:
                    rel = path.relative_to(root).as_posix()
                except ValueError:
                    continue
                region = location.get("region", {})
                where = (result["ruleId"], rel, region.get("startLine"), region.get("startColumn"))
                if where not in seen:
                    seen.add(where)
                    counts[(result["ruleId"], rel)] += 1
    return counts


def read_baseline(path: Path) -> Counter:
    base: Counter = Counter()
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                rule, rel, count = line.split("\t")
                base[(rule, rel)] = int(count)
            except ValueError:
                sys.exit(f"{path}:{number}: expected '<rule>\\t<file>\\t<count>', got {line!r}")
    return base


def write_baseline(path: Path, counts: Counter) -> None:
    lines = [f"{rule}\t{rel}\t{n}\n" for (rule, rel), n in sorted(counts.items()) if n > 0]
    path.write_text("".join(lines), encoding="utf-8")


def main(argv: list[str]) -> int:
    flags = {a for a in argv if a.startswith("--")}
    args = [a for a in argv if not a.startswith("--")]
    if len(args) < 2 or flags - {"--shrink", "--init"}:
        print(__doc__)
        return 2
    baseline, sarifs = Path(args[0]), args[1:]
    now = findings(sarifs, baseline.resolve().parent)

    if "--init" in flags:
        if baseline.exists():
            print(f"{baseline} exists; --init writes only a first baseline (use --shrink to lower it)")
            return 1
        write_baseline(baseline, now)
        print(f"baseline written: {len(now)} entries, {sum(now.values())} findings")
        return 0

    base = read_baseline(baseline)
    new = sorted(k for k in now if now[k] > base[k])
    stale = sorted(k for k in base if now[k] < base[k])
    for rule, rel in new:
        print(f"NEW   {rule} {rel}: {now[(rule, rel)]} (baseline {base[(rule, rel)]})")

    if "--shrink" in flags:
        if new:
            print("not shrunk: fix the new findings first")
            return 1
        write_baseline(baseline, Counter({k: min(base[k], now[k]) for k in base}))
        print(f"baseline shrunk: {len(stale)} entries lowered or removed")
        return 0

    for rule, rel in stale:
        print(f"STALE {rule} {rel}: {now[(rule, rel)]} (baseline {base[(rule, rel)]}); run with --shrink")
    print(f"{sum(now.values())} findings against a baseline of {sum(base.values())}: "
          f"{len(new)} new, {len(stale)} stale")
    return 1 if new or stale else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
