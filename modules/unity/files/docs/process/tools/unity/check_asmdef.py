#!/usr/bin/env python3
"""check_asmdef: checks the Unity assemblies' references against the project's rules.

Owned by the scaffold's unity module (docs/process/modules/unity.md, "Checks"). Python 3.9+, standard library only.

    python docs/process/tools/unity/check_asmdef.py [--root DIR] [--graph]

Rules are in docs/asmdef-rules.json (project-owned):

    {
      "Game.Core":   {"references": [], "noEngineReferences": true},
      "Game.Unity":  {"references": ["Game.Core", "Unity.*"]},
      "Game.Editor": {"references": ["Game.*", "Unity.*"]},
      "*.Tests":     {"references": ["*"]}
    }

Keys and reference entries are glob patterns over assembly names (* matches anything). For each assembly the first
matching key applies. Errors (exit 1): a reference no pattern allows; noEngineReferences different from the rule.
Warnings: an assembly with no rule. Without a rules file, --graph prints the assemblies and their references, to
start writing one.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from pathlib import Path

RULES = "docs/asmdef-rules.json"
SKIP = {".git", "Library", "Temp", "Obj", "obj", "Logs", "UserSettings", "PackageCache", "node_modules", "tmp"}


def load_json(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig")
    text = re.sub(r"^\s*//.*$", "", text, flags=re.M)  # asmdef files may carry comment lines
    return json.loads(text)


def find_assemblies(root: Path) -> dict[str, dict]:
    found: dict[str, dict] = {}
    guids: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for f in filenames:
            if not f.endswith(".asmdef"):
                continue
            path = Path(dirpath) / f
            data = load_json(path)
            name = data.get("name", path.stem)
            found[name] = {"path": path.relative_to(root).as_posix(), "data": data}
            meta = path.with_name(f + ".meta")
            if meta.exists():
                m = re.search(r"^guid:\s*([0-9a-f]+)", meta.read_text(encoding="utf-8", errors="replace"), re.M)
                if m:
                    guids[m.group(1)] = name
    for info in found.values():
        refs = []
        for r in info["data"].get("references", []):
            if r.startswith("GUID:"):
                refs.append(guids.get(r[5:], r))  # an unresolved GUID belongs to a package: keep it as it is
            else:
                refs.append(r)
        info["refs"] = refs
    return found


def rule_for(name: str, rules: dict):
    for pattern, rule in rules.items():
        if fnmatch.fnmatchcase(name, pattern):
            return pattern, rule
    return None, None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check Unity assembly references against docs/asmdef-rules.json.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--graph", action="store_true", help="print the assemblies and their references")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    assemblies = find_assemblies(root)

    if args.graph or not (root / RULES).exists():
        for name, info in sorted(assemblies.items()):
            flag = " (noEngineReferences)" if info["data"].get("noEngineReferences") else ""
            print(f"{name}{flag}  [{info['path']}]")
            for r in info["refs"]:
                print(f"    -> {r}")
        if not (root / RULES).exists():
            print(f"check_asmdef: no {RULES}; {len(assemblies)} assemblies listed above. Write the rules to check them.")
        return 0

    rules = load_json(root / RULES)
    errors, warnings = [], []
    for name, info in sorted(assemblies.items()):
        pattern, rule = rule_for(name, rules)
        if rule is None:
            warnings.append(f"{info['path']}: warning: assembly {name} has no rule in {RULES}")
            continue
        allowed = rule.get("references", [])
        for r in info["refs"]:
            if not any(fnmatch.fnmatchcase(r, a) for a in allowed):
                errors.append(f"{info['path']}: error: {name} references {r}, which rule '{pattern}' does not allow")
        if "noEngineReferences" in rule and bool(info["data"].get("noEngineReferences")) != bool(rule["noEngineReferences"]):
            errors.append(f"{info['path']}: error: {name} noEngineReferences should be {rule['noEngineReferences']}")
    for line in errors + warnings:
        print(line)
    print(f"check_asmdef: {len(assemblies)} assemblies; {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
