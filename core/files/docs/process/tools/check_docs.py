#!/usr/bin/env python3
"""check-docs: keeps the project's Markdown documentation consistent as it grows.

Owned by the scaffold (docs/process/). Rules in docs/process/documentation.md, "Checking".
Python 3.9+, standard library only.

Usage:
    python docs/process/tools/check_docs.py [--root DIR] [--strict] [--quiet] [--list-rules]

Every Markdown file in the repository is checked (tracked and untracked-but-not-ignored files when the root is a
git repository, otherwise a walk that skips the excluded folders), so new files are covered without registering them.
What each rule applies to is set by path globs: the defaults below, extended by an optional project config,
docs/check-docs.json.

Errors (exit 1): broken links, missing anchors, backticked paths that do not exist, documents without a Summary
line, files missing from their index. Warnings (exit 0; exit 1 with --strict): size limits, unfilled {{placeholders}}.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import unquote

CONFIG_PATH = "docs/check-docs.json"
MODULE_CONFIG_DIR = "docs/process/check-docs.d"  # rules delivered by scaffold modules, merged before the project's

DEFAULTS: dict = {
    # Never checked, never counted as link targets' owners.
    "exclude": [
        ".git/**", ".scaffold/**", "**/node_modules/**", "tmp/**", "**/bin/**", "**/obj/**",
        "**/dist/**", "**/build/**", "**/.venv/**", "**/vendor/**",
    ],
    # Backticked paths that are named on purpose although they may not exist. Each: {"path", "why"}; a trailing
    # "/" or "/**" covers everything below.
    "ignore_paths": [
        {"path": "tmp/**", "why": "git-ignored scratch folder; may not exist on a fresh checkout"},
        {"path": "docs/check-docs.json", "why": "optional project config of this checker"},
        {"path": ".github/copilot-instructions.md", "why": "another tool's rules file, merged by the bootstrap if present"},
    ],
    # Files that must carry a **Summary:** line near the top.
    "summary_required": ["docs/**/*.md", "**/AGENTS.md"],
    "summary_exempt": [],
    # Every file matching "files" must be linked from "index".
    "indexes": [
        {"index": "docs/README.md", "files": "docs/*.md", "except": ["docs/README.md"]},
        {"index": "docs/DESIGN.md", "files": "docs/design/**/*.md"},
        {"index": "docs/ideas/README.md", "files": "docs/ideas/*.md", "except": ["docs/ideas/README.md"]},
        {"index": "docs/log/README.md", "files": "docs/log/*.md", "except": ["docs/log/README.md"]},
        {"index": "docs/plans/README.md", "files": "docs/plans/*.md", "except": ["docs/plans/README.md"]},
        {"index": "docs/process/README.md", "files": "docs/process/*.md", "except": ["docs/process/README.md"]},
        {"index": "AGENTS.md", "files": "docs/process/modules/*.md"},
        {"index": ["docs/process/roles/README.md", "docs/process/modules/*.md"], "files": "docs/process/roles/*.md"},
    ],
    # Size limits (warnings). "section" limits only the lines under that heading. A project entry with the same
    # "files" and "section" replaces the default.
    "limits": [
        {"files": "**/AGENTS.md", "max_lines": 150},
        {"files": "docs/STATUS.md", "max_lines": 60},
        {"files": "docs/HEALTH.md", "section": "Noticed", "max_lines": 30},
        {"files": "docs/**/*.md", "max_bytes": 40_000},
    ],
    # Files where a {{placeholder}} left in the prose is reported (warning; error with --strict).
    "placeholders": ["**/AGENTS.md", "docs/*.md"],
}

RULES = {
    "link": "a relative link points to a file or folder that does not exist",
    "anchor": "a link's #anchor matches no heading in its target",
    "path": "a backticked repository path does not exist (add it to ignore_paths with why, if on purpose)",
    "summary": "a document has no **Summary:** line in its first lines",
    "index": "a file is not linked from its index",
    "limit": "a file or section is past its size limit (documentation.md, \"Growth rules\")",
    "placeholder": "a {{placeholder}} is still unfilled",
}


# ---------------------------------------------------------------- helpers

def glob_to_regex(pattern: str) -> re.Pattern:
    """Glob with ** (any depth, including none), * and ? (not crossing '/')."""
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


class Globs:
    def __init__(self, patterns: list[str]):
        self.res = [glob_to_regex(p) for p in patterns]

    def match(self, rel: str) -> bool:
        return any(r.match(rel) for r in self.res)


def slugify(heading: str) -> str:
    """GitHub-style anchor for a heading."""
    text = re.sub(r"`([^`]*)`", r"\1", heading)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)  # links keep their text
    text = re.sub(r"<[^>]+>", "", text).strip().lower()
    out = []
    for ch in text:
        if ch in " -":
            out.append("-")
        elif ch == "_" or unicodedata.category(ch)[0] in "LN":
            out.append(ch)
    return "".join(out)


@dataclass
class Doc:
    rel: str
    text: str
    lines: list[str]
    prose: list[tuple[int, str]] = field(default_factory=list)  # (line no, text) outside fences and comments
    anchors: set[str] = field(default_factory=set)
    headings: list[tuple[int, int, str]] = field(default_factory=list)  # (line no, level, title)


INLINE_CODE = re.compile(r"`([^`\n]+)`")
LINK = re.compile(r"!?\[(?:[^\]\\]|\\.)*\]\(\s*<?([^)\s>]+)>?(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
REF_DEF = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s+.*)?$")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
EXPLICIT_ID = re.compile(r"""<a\s+(?:name|id)=["']([^"']+)["']""")
PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}")
PATHLIKE = re.compile(r"^(?:\./)?[\w.@~+-]+(?:/[\w.@~+-]+)*/?$")


def parse(rel: str, text: str) -> Doc:
    lines = text.splitlines()
    doc = Doc(rel, text, lines)
    fence = None
    in_comment = False
    seen: dict[str, int] = {}
    for no, line in enumerate(lines, 1):
        stripped = line.strip()
        if fence:
            if stripped.startswith(fence):
                fence = None
            continue
        m = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if m and not in_comment:
            fence = m.group(1)
            continue
        # HTML comments (may span lines): their content is not prose.
        visible = ""
        rest = line
        while rest:
            if in_comment:
                end = rest.find("-->")
                if end < 0:
                    rest = ""
                else:
                    in_comment = False
                    rest = rest[end + 3:]
            else:
                start = rest.find("<!--")
                if start < 0:
                    visible += rest
                    rest = ""
                else:
                    visible += rest[:start]
                    in_comment = True
                    rest = rest[start + 4:]
        if not visible.strip():
            continue
        doc.prose.append((no, visible))
        h = HEADING.match(visible)
        if h:
            title = h.group(2)
            doc.headings.append((no, len(h.group(1)), title))
            slug = slugify(title)
            n = seen.get(slug, 0)
            seen[slug] = n + 1
            doc.anchors.add(slug if n == 0 else f"{slug}-{n}")
        for a in EXPLICIT_ID.findall(visible):
            doc.anchors.add(a)
    return doc


# ---------------------------------------------------------------- the checker

@dataclass
class Finding:
    level: str  # "error" | "warning"
    rule: str
    rel: str
    line: int
    message: str


class Checker:
    def __init__(self, root: Path, config: dict):
        self.root = root
        self.cfg = config
        self.exclude = Globs(config["exclude"])
        self.ignore = [self._ignore_regex(e) for e in config["ignore_paths"]]
        self.findings: list[Finding] = []
        self.docs: dict[str, Doc] = {}
        self.all_files: set[str] = set()
        self.all_dirs: set[str] = {""}

    @staticmethod
    def _ignore_regex(entry) -> re.Pattern:
        p = entry["path"] if isinstance(entry, dict) else entry
        p = p.rstrip("/")
        if p.endswith("/**"):
            p = p[:-3]
        return re.compile("^" + glob_to_regex(p).pattern[1:-1] + "(?:/.*)?/?$")

    def add(self, level, rule, rel, line, message):
        self.findings.append(Finding(level, rule, rel, line, message))

    # -- discovery
    def discover(self):
        files = None
        if (self.root / ".git").exists():
            try:
                out = subprocess.run(
                    ["git", "ls-files", "-co", "--exclude-standard", "-z"],
                    cwd=self.root, capture_output=True, check=True,
                ).stdout.decode("utf-8", "replace")
                files = [f for f in out.split("\0") if f and (self.root / f).exists()]
            except (OSError, subprocess.CalledProcessError):
                files = None
        if files is None:
            files = []
            for dirpath, dirnames, filenames in os.walk(self.root):
                rel_dir = Path(dirpath).relative_to(self.root).as_posix()
                rel_dir = "" if rel_dir == "." else rel_dir
                dirnames[:] = [d for d in dirnames
                               if not self.exclude.match(f"{rel_dir}/{d}/x".lstrip("/"))]
                files += [f"{rel_dir}/{f}".lstrip("/") for f in filenames]
        for f in files:
            if self.exclude.match(f):
                continue
            self.all_files.add(f)
            parts = f.split("/")
            for i in range(1, len(parts)):
                self.all_dirs.add("/".join(parts[:i]))
        for f in sorted(self.all_files):
            if f.lower().endswith(".md"):
                text = (self.root / f).read_text(encoding="utf-8-sig", errors="replace")
                self.docs[f] = parse(f, text)

    def exists(self, rel: str) -> bool:
        rel = rel.rstrip("/")
        return rel in self.all_files or rel in self.all_dirs or (self.root / rel).exists()

    @staticmethod
    def norm(base_dir: str, target: str) -> str | None:
        parts = [] if not base_dir else base_dir.split("/")
        for seg in target.split("/"):
            if seg in ("", "."):
                continue
            if seg == "..":
                if not parts:
                    return None
                parts.pop()
            else:
                parts.append(seg)
        return "/".join(parts)

    # -- rules
    def check_links(self, doc: Doc):
        base = doc.rel.rsplit("/", 1)[0] if "/" in doc.rel else ""
        for no, text in doc.prose:
            plain = INLINE_CODE.sub("", text)
            targets = LINK.findall(plain)
            m = REF_DEF.match(plain)
            if m:
                targets.append(m.group(1))
            for raw in targets:
                if re.match(r"^[a-z][a-z0-9+.-]*:", raw, re.I) or PLACEHOLDER.search(raw):
                    continue  # http:, mailto:, ... ; or a template placeholder
                path, _, anchor = raw.partition("#")
                path = unquote(path)
                if not path:
                    target_rel = doc.rel
                else:
                    target_rel = self.norm(base, path)
                    if target_rel is None or not self.exists(target_rel):
                        self.add("error", "link", doc.rel, no, f"link target not found: {raw}")
                        continue
                if anchor and target_rel.lower().endswith(".md"):
                    target = self.docs.get(target_rel)
                    if target is not None and unquote(anchor).lower() not in target.anchors:
                        self.add("error", "anchor", doc.rel, no, f"no heading for anchor: {raw}")

    def check_paths(self, doc: Doc):
        base = doc.rel.rsplit("/", 1)[0] if "/" in doc.rel else ""
        for no, text in doc.prose:
            for code in INLINE_CODE.findall(text):
                cand = re.sub(r":\d+(?::\d+)?$", "", code.strip())  # file:line
                if "/" not in cand or not PATHLIKE.match(cand) or cand.startswith(("/", "~")):
                    continue
                last = cand.rstrip("/").rsplit("/", 1)[-1]
                if not cand.endswith("/") and "." not in last:
                    continue  # "origin/main", "and/or": not a file path
                cand = cand[2:] if cand.startswith("./") else cand
                if any(r.match(cand) for r in self.ignore):
                    continue
                bases = [""] + ([base] if base else []) + ["docs"]
                if any((r := self.norm(b, cand)) is not None and self.exists(r) for b in bases):
                    continue
                self.add("error", "path", doc.rel, no, f"path not found: {code}")

    def check_summary(self, doc: Doc, required: Globs, exempt: Globs):
        if not required.match(doc.rel) or exempt.match(doc.rel):
            return
        head = [t for _, t in doc.prose[:8]]
        if not any(t.lstrip().startswith("**Summary:**") for t in head):
            self.add("error", "summary", doc.rel, 1, "no **Summary:** line near the top")

    def check_indexes(self):
        for entry in self.cfg["indexes"]:
            # "index" is one path, or a list of paths and globs: a member must be linked from at least one of them.
            index_spec = entry["index"] if isinstance(entry["index"], list) else [entry["index"]]
            index_globs = Globs(index_spec)
            files = Globs([entry["files"]])
            indexes = [d for r, d in self.docs.items() if index_globs.match(r)]
            skip = set(entry.get("except", [])) | {d.rel for d in indexes}
            members = [r for r in self.docs if files.match(r) and r not in skip]
            if not members:
                continue
            named = " or ".join(index_spec)
            if not indexes:
                self.add("error", "index", index_spec[0], 1,
                         f"index missing, but {len(members)} file(s) match {entry['files']}")
                continue
            linked = set()
            for index in indexes:
                base = index.rel.rsplit("/", 1)[0] if "/" in index.rel else ""
                for _, text in index.prose:
                    for raw in LINK.findall(INLINE_CODE.sub("", text)):
                        p = self.norm(base, unquote(raw.partition("#")[0]))
                        if p:
                            linked.add(p)
            for m in sorted(members):
                if m not in linked:
                    self.add("error", "index", m, 1, f"not linked from its index {named}")

    def check_limits(self):
        for entry in self.cfg["limits"]:
            files = Globs([entry["files"]])
            for rel, doc in self.docs.items():
                if not files.match(rel):
                    continue
                section = entry.get("section")
                if section:
                    lines = self.section_lines(doc, section)
                    if lines is None:
                        continue
                    where = f'section "{section}"'
                else:
                    lines = doc.lines
                    where = "file"
                if "max_lines" in entry:
                    count = sum(1 for l in lines if l.strip())
                    if count > entry["max_lines"]:
                        self.add("warning", "limit", rel, 1,
                                 f"{where} has {count} non-empty lines, limit {entry['max_lines']}")
                if "max_bytes" in entry and not section:
                    size = len(doc.text.encode("utf-8"))
                    if size > entry["max_bytes"]:
                        self.add("warning", "limit", rel, 1,
                                 f"{size // 1000} KB, limit {entry['max_bytes'] // 1000} KB: split along headings")

    @staticmethod
    def section_lines(doc: Doc, title: str):
        for i, (no, level, text) in enumerate(doc.headings):
            if text.strip().lower() == title.lower():
                end = len(doc.lines)
                for no2, level2, _ in doc.headings[i + 1:]:
                    if level2 <= level:
                        end = no2 - 1
                        break
                body = set(n for n, _ in doc.prose)
                return [doc.lines[n - 1] for n in range(no + 1, end + 1) if n in body]
        return None

    def check_placeholders(self, doc: Doc, globs: Globs):
        if not globs.match(doc.rel):
            return
        # All lines, code blocks included (commands are placeholders too); inline code is an example, not one.
        hits = [no for no, line in enumerate(doc.lines, 1) if PLACEHOLDER.search(INLINE_CODE.sub("", line))]
        if hits:
            self.add("warning", "placeholder", doc.rel, hits[0],
                     f"{len(hits)} line(s) with unfilled {{{{placeholders}}}}, first here")

    def run(self):
        self.discover()
        required = Globs(self.cfg["summary_required"])
        exempt = Globs(self.cfg["summary_exempt"])
        placeholders = Globs(self.cfg["placeholders"])
        for doc in self.docs.values():
            self.check_links(doc)
            self.check_paths(doc)
            self.check_summary(doc, required, exempt)
            self.check_placeholders(doc, placeholders)
        self.check_indexes()
        self.check_limits()


# ---------------------------------------------------------------- config and main

def identity(entry: dict, keys: tuple) -> tuple:
    return tuple(str(entry.get(k)) for k in keys)


def merge_config(cfg: dict, extra: dict) -> None:
    for key in ("exclude", "ignore_paths", "summary_exempt", "placeholders"):
        cfg[key] += extra.get(key, [])
    if "summary_required" in extra:
        cfg["summary_required"] = extra["summary_required"]
    for key, ident in (("indexes", ("index", "files")), ("limits", ("files", "section"))):
        for entry in extra.get(key, []):
            same = identity(entry, ident)
            cfg[key] = [e for e in cfg[key] if identity(e, ident) != same]
            if not entry.get("disabled"):
                cfg[key].append(entry)


def load_config(root: Path) -> dict:
    """Defaults, then each module's rules (docs/process/check-docs.d/*.json), then the project's own config."""
    cfg = json.loads(json.dumps(DEFAULTS))
    module_dir = root / MODULE_CONFIG_DIR
    sources = sorted(module_dir.glob("*.json")) if module_dir.is_dir() else []
    sources.append(root / CONFIG_PATH)
    for path in sources:
        if path.exists():
            merge_config(cfg, json.loads(path.read_text(encoding="utf-8-sig")))
    return cfg


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check the project's Markdown documentation.")
    ap.add_argument("--root", default=".", help="repository root (default: current directory)")
    ap.add_argument("--strict", action="store_true", help="warnings fail too")
    ap.add_argument("--quiet", action="store_true", help="print only the summary line when there are no errors")
    ap.add_argument("--list-rules", action="store_true", help="print the rules and exit")
    args = ap.parse_args(argv)

    if args.list_rules:
        for rule, text in RULES.items():
            print(f"{rule:12} {text}")
        return 0

    root = Path(args.root).resolve()
    checker = Checker(root, load_config(root))
    checker.run()
    errors = [f for f in checker.findings if f.level == "error"]
    warnings = [f for f in checker.findings if f.level == "warning"]
    shown = checker.findings if not (args.quiet and not errors and not args.strict) else []
    for f in sorted(shown, key=lambda f: (f.level != "error", f.rel, f.line)):
        print(f"{f.rel}:{f.line}: {f.level} [{f.rule}] {f.message}")
    print(f"check-docs: {len(checker.docs)} documents; {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
