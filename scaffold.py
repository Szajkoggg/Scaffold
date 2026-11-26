#!/usr/bin/env python3
"""scaffold.py: the file work of the scaffold. The judgement (which modules, merging, questions) is the agent's,
following playbooks/; this script only copies, records and updates, so the result is the same every time.

Python 3.9+, standard library only.

    python scaffold.py list                                  modules and presets
    python scaffold.py detect   <project>                    modules whose signs the project shows
    python scaffold.py apply    <project> [--preset P] [--modules a,b] [--name NAME] [--dry-run] [--force]
    python scaffold.py update   <project> [--dry-run] [--force]
    python scaffold.py status   <project>
    python scaffold.py workstation [--home DIR] [--dry-run] [--force]

A project records what it got in .scaffold/manifest.json (commit it). Files the scaffold owns are replaced on update
while untouched; a file edited in the project is never overwritten: the new version is written to
.scaffold/incoming/<path> for the agent to merge. Seed files (AGENTS.md, STATUS.md, ...) are copied once and belong to
the project from then on.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path(__file__).resolve().parent
MANIFEST = ".scaffold/manifest.json"
INCOMING = ".scaffold/incoming"
WORKSTATION_MANIFEST = ".scaffold/workstation.json"
PYTHON = Path(sys.executable).as_posix()  # the interpreter the workstation records for the status line and hooks
SKIP_DIRS = {".git", "node_modules", "Library", "Temp", "obj", "bin", "tmp", ".venv", "venv", "__pycache__",
             "Logs", "UserSettings", ".scaffold", "dist", "build"}
BLOCK = "<!-- scaffold:{name} -->"
BLOCK_END = "<!-- /scaffold:{name} -->"


# ---------------------------------------------------------------- small helpers

def glob_to_regex(pattern: str) -> re.Pattern:
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?"); i += 3
        elif pattern.startswith("**", i):
            out.append(".*"); i += 2
        elif pattern[i] == "*":
            out.append("[^/]*"); i += 1
        elif pattern[i] == "?":
            out.append("[^/]"); i += 1
        else:
            out.append(re.escape(pattern[i])); i += 1
    return re.compile("^" + "".join(out) + "$")


def matches(rel: str, patterns) -> bool:
    return any(glob_to_regex(p).match(rel) for p in patterns)


def digest(data: bytes) -> str:
    """Hash with line endings normalised, so git's autocrlf does not make a file look edited."""
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()[:16]


def scaffold_version() -> str:
    try:
        return subprocess.run(["git", "-C", str(HOME), "describe", "--always", "--dirty", "--tags"],
                              capture_output=True, text=True, check=True).stdout.strip() or "unversioned"
    except (OSError, subprocess.CalledProcessError):
        return "unversioned"


def today() -> str:
    return dt.datetime.now().astimezone().date().isoformat()  # the local date, explicitly


def files_under(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for f in sorted(filenames):
            p = Path(dirpath) / f
            yield p.relative_to(root).as_posix(), p


# ---------------------------------------------------------------- modules

class Module:
    def __init__(self, path: Path):
        self.path = path
        self.meta = json.loads((path / "module.json").read_text(encoding="utf-8"))
        self.name = self.meta["name"]

    def __getattr__(self, key):
        defaults = {"summary": "", "kind": "concern", "status": "stub", "requires": [], "suggests": [],
                    "detect": [], "seed": [], "health": []}
        if key in defaults:
            return self.meta.get(key, defaults[key])
        raise AttributeError(key)

    def deliveries(self):
        """(destination, source, kind) for every file the module delivers."""
        out = []
        files = self.path / "files"
        if files.is_dir():
            for rel, src in files_under(files):
                if rel.endswith("/.DS_Store"):
                    continue
                out.append((rel, src, "seed" if matches(rel, self.seed) else "owned"))
        skills = self.path / "skills"
        if skills.is_dir():
            for rel, src in files_under(skills):
                out.append((f".claude/skills/{rel}", src, "owned"))
                out.append((f".agents/skills/{rel}", src, "owned"))
        agents = self.path / "agents"
        if agents.is_dir():
            for rel, src in files_under(agents):
                out.append((f".claude/agents/{rel}", src, "owned"))
        return out


def all_modules() -> dict[str, Module]:
    mods = {"core": Module(HOME / "core")}
    for d in sorted((HOME / "modules").iterdir()):
        if (d / "module.json").exists():
            m = Module(d)
            mods[m.name] = m
    return mods


def presets() -> dict:
    return json.loads((HOME / "presets.json").read_text(encoding="utf-8"))


def resolve(names, mods) -> list[str]:
    """core first, then the named modules with everything they require, in dependency order."""
    order, seen = [], set()

    def visit(n, chain=()):
        if n not in mods:
            sys.exit(f"unknown module: {n} (see: scaffold.py list)")
        if n in chain:
            sys.exit(f"module dependency cycle: {' -> '.join(chain + (n,))}")
        if n in seen:
            return
        for r in mods[n].requires:
            visit(r, chain + (n,))
        seen.add(n)
        order.append(n)

    visit("core")
    for n in names:
        visit(n)
    return order


# ---------------------------------------------------------------- the sync engine

class Sync:
    def __init__(self, root: Path, manifest_rel: str, incoming_rel: str, dry: bool, force: bool,
                 substitutions: dict[str, str]):
        self.root, self.dry, self.force = root, dry, force
        self.manifest_path = root / manifest_rel
        self.incoming = root / incoming_rel
        self.incoming_rel = incoming_rel
        self.subs = substitutions
        self.old = json.loads(self.manifest_path.read_text(encoding="utf-8")) if self.manifest_path.exists() else None
        self.files: dict[str, dict] = {}
        self.report: list[tuple[str, str, str]] = []  # (mark, path, note)

    def note(self, mark, path, text=""):
        self.report.append((mark, path, text))

    def content(self, src: Path, kind: str) -> bytes:
        data = src.read_bytes()
        if self.subs:
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                return data
            for k, v in self.subs.items():
                if kind == "seed" or k == "SCAFFOLD_HOME":
                    text = text.replace("{{" + k + "}}", v)
            data = text.encode("utf-8")
        return data

    def write(self, rel: str, data: bytes, base: Path | None = None):
        if self.dry:
            return
        p = (base or self.root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def deliver(self, deliveries):
        old_files = (self.old or {}).get("files", {})
        if not self.dry and self.incoming.exists():
            shutil.rmtree(self.incoming)
        seen = {}
        for dest, src, kind, module in deliveries:
            if dest in seen:
                sys.exit(f"two modules deliver {dest}: {seen[dest]} and {module}")
            seen[dest] = module
            data = self.content(src, kind)
            new_hash = digest(data)
            target = self.root / dest
            record = {"module": module, "kind": kind}
            if not target.exists():
                self.write(dest, data)
                self.note("+", dest)
                if kind == "owned":
                    record["hash"] = new_hash
            elif kind == "seed":
                if dest not in old_files:
                    self.note("?", dest, "exists already: merge the scaffold's version by hand "
                                         f"(written to {self.incoming_rel}/{dest})")
                    self.write(dest, data, self.incoming)
            else:
                current = digest(target.read_bytes())
                recorded = old_files.get(dest, {}).get("hash")
                if current == new_hash:
                    pass
                elif current == recorded or self.force:
                    self.write(dest, data)
                    self.note("~", dest, "updated" if current == recorded else "overwritten (--force)")
                else:
                    self.write(dest, data, self.incoming)
                    why = "edited in the project" if recorded else "exists, not from the scaffold"
                    self.note("!", dest, f"{why}: kept; the scaffold's version is in {self.incoming_rel}/{dest}")
                    new_hash = recorded or current  # keep the old baseline until merged
                record["hash"] = new_hash
            self.files[dest] = record
        for dest, rec in old_files.items():
            if dest in self.files:
                continue
            target = self.root / dest
            if rec.get("kind") == "owned" and target.exists():
                if digest(target.read_bytes()) == rec.get("hash") or self.force:
                    if not self.dry:
                        target.unlink()
                    self.note("-", dest, "no longer in the scaffold")
                else:
                    self.note("!", dest, "no longer in the scaffold but edited in the project: kept, decide by hand")

    def save(self, extra: dict):
        data = dict(extra)
        data["files"] = dict(sorted(self.files.items()))
        if self.dry:
            return
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        gi = self.manifest_path.parent / ".gitignore"
        if not gi.exists():
            gi.write_text("incoming/\n", encoding="utf-8")

    def print(self, title: str):
        # "!" and "?" have a version in the incoming folder to merge; "i" needs the user's attention but has none.
        order = {"!": 0, "?": 1, "i": 2, "-": 3, "~": 4, "+": 5, "*": 6}
        for mark, path, text in sorted(self.report, key=lambda r: (order.get(r[0], 9), r[1])):
            print(f"{mark} {path}" + (f"  {text}" if text else ""))
        counts = {m: sum(1 for r in self.report if r[0] == m) for m in "+~-!?*i"}
        attention = f", {counts['i']} to do yourself" if counts["i"] else ""
        print(f"{title}{' (dry run, nothing written)' if self.dry else ''}: {counts['+']} added, "
              f"{counts['~']} updated, {counts['-']} removed, {counts['!']} conflicts, "
              f"{counts['?']} to merge by hand, {counts['*']} existing files edited{attention}")
        if counts["!"] or counts["?"]:
            print(f"Merge each file listed above with its version in {self.incoming_rel}/, delete that folder, "
                  "then run the same command again.")


def set_block(text: str, name: str, body: str, heading: str | None = None) -> tuple[str, bool]:
    """Replace the content between the block markers; append the block (under heading) when missing."""
    start, end = BLOCK.format(name=name), BLOCK_END.format(name=name)
    new_block = f"{start}\n{body}{end}"
    if start in text and end in text:
        i, j = text.index(start), text.index(end) + len(end)
        return text[:i] + new_block + text[j:], False
    sep = "" if text.endswith("\n") or not text else "\n"
    head = f"## {heading}\n\n" if heading else ""
    if text.strip():
        head = "\n" + head
    return text + sep + head + new_block + "\n", True


def edit_file(sync: Sync, rel: str, fn, what: str):
    p = sync.root / rel
    if not p.exists():
        sync.note("i", rel, f"missing: {what} not written")
        return
    raw = p.read_bytes()
    text = raw.decode("utf-8-sig")
    crlf = b"\r\n" in raw
    text = text.replace("\r\n", "\n")
    new, msg = fn(text)
    if new != text:
        if crlf:
            new = new.replace("\n", "\r\n")
        if not sync.dry:
            p.write_bytes(new.encode("utf-8"))
        sync.note("*", rel, msg)


def drop_stale(base: dict, old: dict, new: dict, path="") -> list[str]:
    """Remove from base the list items an earlier merge added (old) that the scaffold no longer ships (new)."""
    changed = []
    for k, v in old.items():
        key = f"{path}{k}"
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            changed += drop_stale(base[k], v, new.get(k) if isinstance(new.get(k), dict) else {}, key + ".")
        elif isinstance(v, list) and isinstance(base.get(k), list):
            keep = new.get(k) if isinstance(new.get(k), list) else []
            stale = [item for item in v if item not in keep and item in base[k]]
            if stale:
                base[k] = [item for item in base[k] if item not in stale]
                changed.append(key)
    return changed


def merge_settings(sync: Sync, rel: str, fragments: list[Path]) -> dict:
    """Merge the modules' settings fragments into the project's settings; returns what the scaffold now ships, recorded
    in the manifest so the next update can remove entries it no longer ships."""
    shipped: dict = {}
    for f in fragments:
        deep_merge(shipped, json.loads(f.read_text(encoding="utf-8")))
    target = sync.root / rel
    try:
        current = json.loads(target.read_text(encoding="utf-8-sig")) if target.exists() else {}
    except ValueError as e:
        sync.note("!", rel, f"not valid JSON ({e}): scaffold settings not merged")
        return (sync.old or {}).get("settings", {})
    removed = drop_stale(current, (sync.old or {}).get("settings", {}), shipped)
    added = deep_merge(current, shipped)
    if removed or added:
        if not sync.dry:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
        what = [f"merged {', '.join(sorted(set(added)))}"] if added else []
        what += [f"removed old entries from {', '.join(sorted(set(removed)))}"] if removed else []
        sync.note("*", rel, "settings " + "; ".join(what))
    return shipped


# ---------------------------------------------------------------- project commands

def project_sync(root: Path, names: list[str], args, title: str):
    mods = all_modules()
    order = resolve(names, mods)
    subs = {"PROJECT_NAME": args.name} if getattr(args, "name", None) else {}
    sync = Sync(root, MANIFEST, INCOMING, args.dry_run, args.force, subs)
    deliveries = [(d, s, k, n) for n in order for d, s, k in mods[n].deliveries()]
    sync.deliver(deliveries)

    # The Modules block in AGENTS.md.
    lines = []
    for n in order:
        if n == "core":
            continue
        m = mods[n]
        doc = f"docs/process/modules/{n}.md"
        if any(d == doc for d, *_ in deliveries):
            lines.append(f"- [{n}]({doc}): {m.summary}\n")
        else:
            lines.append(f"- {n}: {m.summary} (No rules yet: the module is a stub.)\n")
    body = "".join(lines) or "- None: core only.\n"
    edit_file(sync, "AGENTS.md",
              lambda t: (lambda r: (r[0], "Modules section added" if r[1] else "Modules list updated"))(
                  set_block(t, "modules", body, heading="Modules")),
              "the Modules list")

    # Claude Code settings the modules bring (hooks, permissions): merged into the project's seed settings on every
    # apply and update, appending what is missing and keeping the project's own entries.
    fragments = [m.path / "settings.json" for m in (mods[n] for n in order) if (m.path / "settings.json").exists()]
    shipped_settings = merge_settings(sync, ".claude/settings.json", fragments) if fragments else {}

    # Health ledger rows the modules bring (added once; the project owns them after).
    rows = [(n, h) for n in order for h in mods[n].health]
    if rows:
        def add_rows(text):
            added = []
            out = text
            for _module, h in rows:
                if re.search(rf"^\|\s*{re.escape(h['check'])}\s*\|", out, re.M):
                    continue
                row = f"| {h['check']} | {h['covers']} | {h['every']} | never |\n"
                m = re.search(r"## Ledger\n(?:.*\n)*?(\|.*\|\n)+", out)
                if not m:
                    continue
                out = out[:m.end()] + row + out[m.end():]
                added.append(h["check"])
            return out, f"health rows added: {', '.join(added)}"
        edit_file(sync, "docs/HEALTH.md", add_rows, "health rows")

    old_modules = (sync.old or {}).get("modules")
    sync.save({
        "scaffold": {"version": scaffold_version(), "applied": (sync.old or {}).get("scaffold", {}).get("applied", today()),
                     "updated": today()},
        "modules": order,
        "settings": shipped_settings,
    })
    stubs = [n for n in order if mods[n].status == "stub"]
    sync.print(title)
    if old_modules and old_modules != order:
        print(f"modules: {', '.join(old_modules)} -> {', '.join(order)}")
    if stubs:
        print(f"stub modules (no content yet, recorded for later updates): {', '.join(stubs)}")
    suggested = sorted({s for n in order for s in mods[n].suggests} - set(order))
    if suggested:
        print(f"modules suggested by these: {', '.join(suggested)}")


def cmd_apply(args):
    root = Path(args.project).resolve()
    if not args.dry_run:
        root.mkdir(parents=True, exist_ok=True)
    names = []
    if args.preset:
        p = presets().get(args.preset)
        if p is None:
            sys.exit(f"unknown preset: {args.preset} (see: scaffold.py list)")
        names += p["modules"]
    if args.modules:
        names += [m.strip() for m in args.modules.split(",") if m.strip()]
    if (root / MANIFEST).exists():
        old = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
        names = old.get("modules", []) + names
    project_sync(root, names, args, "apply")


def cmd_update(args):
    root = Path(args.project).resolve()
    if not (root / MANIFEST).exists():
        sys.exit(f"{root} has no {MANIFEST}: use apply")
    old = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    print(f"scaffold {old.get('scaffold', {}).get('version', '?')} -> {scaffold_version()}")
    project_sync(root, old.get("modules", []), args, "update")


def cmd_status(args):
    root = Path(args.project).resolve()
    mp = root / MANIFEST
    if not mp.exists():
        print(f"not scaffolded: no {MANIFEST}")
        return
    man = json.loads(mp.read_text(encoding="utf-8"))
    sc = man.get("scaffold", {})
    print(f"modules: {', '.join(man.get('modules', []))}")
    print(f"scaffold: {sc.get('version')} (applied {sc.get('applied')}, updated {sc.get('updated')}); "
          f"available: {scaffold_version()}")
    edited, missing = [], []
    for rel, rec in man.get("files", {}).items():
        p = root / rel
        if rec.get("kind") != "owned":
            continue
        if not p.exists():
            missing.append(rel)
        elif digest(p.read_bytes()) != rec.get("hash"):
            edited.append(rel)
    for rel in edited:
        print(f"! {rel}  edited in the project (an update keeps it and offers the new version to merge)")
    for rel in missing:
        print(f"- {rel}  deleted in the project (an update brings it back)")
    if (root / INCOMING).exists():
        print(f"waiting to be merged: files in {INCOMING}/")
    print(f"owned files: {sum(1 for r in man.get('files', {}).values() if r.get('kind') == 'owned')}, "
          f"edited: {len(edited)}, deleted: {len(missing)}")


def cmd_detect(args):
    root = Path(args.project).resolve()
    rels = [rel for rel, _ in files_under(root)]
    mods = all_modules()
    found = {}
    for n, m in mods.items():
        for d in m.detect:
            rx = glob_to_regex(d["glob"])
            hit = next((r for r in rels if rx.match(r)), None)
            if hit:
                found[n] = hit
                break
    print(f"{len(rels)} files looked at in {root}")
    for n, hit in found.items():
        print(f"{n:16} {mods[n].kind:8} evidence: {hit}")
    if not found:
        print("no module signs found (core only, or ask)")
    for pname, p in presets().items():
        if p["modules"] and all(m in found or mods[m].kind == "concern" for m in p["modules"]) \
                and any(m in found for m in p["modules"]):
            print(f"preset fits: {pname}: {p['summary']} ({', '.join(p['modules'])})")
    man = root / MANIFEST
    if man.exists():
        print(f"already scaffolded with: {', '.join(json.loads(man.read_text(encoding='utf-8')).get('modules', []))}")


def cmd_list(args):
    mods = all_modules()
    print("modules:")
    for n, m in mods.items():
        req = f" (requires {', '.join(m.requires)})" if m.requires else ""
        print(f"  {n:16} {m.kind:8} {m.status:6} {m.summary}{req}")
    print("presets:")
    for n, p in presets().items():
        print(f"  {n:18} {p['summary']} [{', '.join(['core'] + p['modules'])}]")


# ---------------------------------------------------------------- workstation

def deep_merge(base: dict, add: dict, path="") -> list[str]:
    """Merge add into base: dicts recursively, lists by appending the items base lacks (so a project's own
    permissions and hooks stay), other values replaced. Returns the keys changed."""
    changed = []
    for k, v in add.items():
        key = f"{path}{k}"
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            changed += deep_merge(base[k], v, key + ".")
        elif isinstance(v, list) and isinstance(base.get(k), list):
            missing = [item for item in v if item not in base[k]]
            if missing:
                base[k].extend(missing)
                changed.append(key)
        elif base.get(k) != v:
            base[k] = v
            changed.append(key)
    return changed


def install_codex_footer(sync: Sync, items: list[str]):
    """Seed the native footer once, preserving choices made later with /statusline."""
    rel = ".codex/config.toml"
    path = sync.root / rel
    original = path.read_bytes() if path.exists() else b""
    newline = "\r\n" if b"\r\n" in original else "\n"
    entry = "status_line = " + json.dumps(items) + newline
    text = original.decode("utf-8")
    section = "[tui]" + newline + entry
    if text:
        try:
            import tomllib
        except ImportError:
            sync.note("i", rel, "use Python 3.11+ to merge the footer into existing TOML")
            return
        try:
            config = tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            sync.note("i", rel, f"could not read TOML: {exc}")
            return
        tui = config.setdefault("tui", {})
        if "status_line" in tui:
            sync.note("=", rel, "existing Codex footer kept")
            return
        tui["status_line"] = items
        # Validate the complete result before writing, including for quoted or inline tables.
        proposals = [text + newline + section, "tui." + entry + text]
        for header in re.finditer(r"""(?m)^[ \t]*\[[ \t]*(?:tui|"tui"|'tui')[ \t]*\][ \t]*(?:#[^\r\n]*)?\r?$""", text):
            pos = header.end()
            pos += int(text[pos:pos + 1] == "\n")
            prefix = text[:pos]
            proposals.append(prefix + ("" if prefix.endswith("\n") else newline) + entry + text[pos:])
        for proposal in proposals:
            try:
                if tomllib.loads(proposal) == config:
                    section = proposal
                    break
            except tomllib.TOMLDecodeError:
                continue
        else:
            sync.note("i", rel, "could not safely insert the footer; select it with /statusline")
            return
    sync.write(rel, section.encode("utf-8"))
    sync.note("*", rel, "Codex footer preset added")


def cmd_workstation(args):
    home = Path(args.home).expanduser().resolve() if args.home else Path.home()
    ws = HOME / "workstation"
    conf = json.loads((ws / "workstation.json").read_text(encoding="utf-8"))
    sync = Sync(home, WORKSTATION_MANIFEST, ".scaffold/incoming-workstation", args.dry_run, args.force,
                {"SCAFFOLD_HOME": HOME.as_posix()})
    install_codex_footer(sync, conf["codex_footer"])
    if args.codex_footer_only:
        sync.print("workstation")
        return
    deliveries = []
    for rel, src in files_under(ws / "skills"):
        for skills_dir in conf["skills_dirs"]:
            deliveries.append((f"{skills_dir}/{rel}", src, "owned", "workstation"))
    for item in conf.get("files", []):
        deliveries.append((item["to"], ws / item["from"], "owned", "workstation"))
    sync.deliver(deliveries)

    personal = (ws / "personal.md").read_text(encoding="utf-8")
    for rel in conf["personal_files"]:
        p = home / rel
        if not p.exists():
            sync.write(rel, b"")
            p_exists = False
        else:
            p_exists = True
        if args.dry_run and not p_exists:
            sync.note("*", rel, "would be created with the personal rules")
            continue
        edit_file(sync, rel, lambda t: (set_block(t, "personal", personal)[0], "personal rules written"),
                  "personal rules")

    for item in conf.get("settings", []):
        target = home / item["to"]
        text = (ws / item["from"]).read_text(encoding="utf-8")
        fragment = json.loads(text.replace("{{HOME}}", home.as_posix()).replace("{{PYTHON}}", PYTHON))
        current = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
        changed = deep_merge(current, fragment)
        if changed:
            if not args.dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
            sync.note("*", item["to"], f"settings set: {', '.join(changed)}")

    set_environment(conf.get("env", {}), sync, args)
    extra = {}
    if "terminal_schemes" in conf:
        extra["terminal_schemes"] = merge_terminal_schemes(sync, ws, conf["terminal_schemes"])

    sync.save({"scaffold": {"version": scaffold_version(), "home": HOME.as_posix(), "updated": today()}, **extra})
    sync.print("workstation")


def merge_terminal_schemes(sync: Sync, ws: Path, spec: dict) -> list[str]:
    """Windows Terminal colour schemes into each settings.json found: a scheme of the same name is replaced, one an
    earlier run shipped and the scaffold no longer does is removed, the user's own are kept. The file is never created
    (Windows Terminal writes it on its first start); returns the names shipped, for the manifest."""
    schemes = json.loads((ws / spec["from"]).read_text(encoding="utf-8"))
    names = [s["name"] for s in schemes]
    stale = set((sync.old or {}).get("terminal_schemes", [])) - set(names)
    found = [rel for rel in spec["to"] if (sync.root / rel).exists()]
    if not found:
        if os.name == "nt":
            sync.note("i", "Windows Terminal", "no settings.json found: colour schemes not added "
                                               "(start Windows Terminal once, then run this again)")
        return names
    for rel in found:
        target = sync.root / rel
        try:
            data = json.loads(target.read_text(encoding="utf-8-sig"))
        except ValueError as e:
            sync.note("i", rel, f"not plain JSON ({e}): colour schemes not added; copy them from "
                                f"workstation/{spec['from']} by hand")
            continue
        current = data.get("schemes", [])
        kept = [s for s in current if s.get("name") not in set(names) | stale]
        if kept + schemes == current:
            continue
        data["schemes"] = kept + schemes
        if not sync.dry:
            target.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n", encoding="utf-8")
        sync.note("*", rel, f"colour schemes set: {', '.join(names)}")
    return names


def find_newest(patterns: list[str]) -> str | None:
    """The newest existing match of the patterns (version-aware sort of the paths), or None."""
    import glob

    def key(path: str):
        return [int(p) if p.isdigit() else p for p in re.split(r"(\d+)", path)]

    found = sorted({p.replace("\\", "/") for pattern in patterns for p in glob.glob(pattern)}, key=key)
    return found[-1] if found else None


def user_env_get(name: str) -> str | None:
    if os.name != "nt":
        return os.environ.get(name)
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            return winreg.QueryValueEx(key, name)[0]
    except OSError:
        return None


def set_environment(env: dict, sync: Sync, args) -> None:
    """User environment variables: on Windows written for the user (setx); elsewhere printed for the shell profile."""
    for name, spec in env.items():
        value = spec["value"].replace("{{PYTHON}}", PYTHON) if "value" in spec else find_newest(spec.get("find", []))
        if value is None:
            sync.note("i", f"env {name}", f"not set: nothing found ({spec.get('why', '')})")
            continue
        if args.home:
            sync.note("*", f"env {name}", f"skipped with --home (would be {value})")
            continue
        if user_env_get(name) == value:
            continue
        if os.name != "nt":
            sync.note("i", f"env {name}", f"add to your shell profile: export {name}=\"{value}\"")
            continue
        if not args.dry_run:
            subprocess.run(["setx", name, value], check=True, capture_output=True)
        sync.note("*", f"env {name}", f"set to {value} ({spec.get('why', '')}); new terminals and tools see it")


# ---------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description="Scaffold projects and workstations.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(fn=cmd_list)
    p = sub.add_parser("detect"); p.add_argument("project"); p.set_defaults(fn=cmd_detect)
    p = sub.add_parser("status"); p.add_argument("project"); p.set_defaults(fn=cmd_status)
    for name, fn in (("apply", cmd_apply), ("update", cmd_update)):
        p = sub.add_parser(name)
        p.add_argument("project")
        if name == "apply":
            p.add_argument("--preset")
            p.add_argument("--modules", help="comma-separated, added to the preset's")
            p.add_argument("--name", help="fills {{PROJECT_NAME}} in seed files")
        p.add_argument("--dry-run", action="store_true")
        p.add_argument("--force", action="store_true", help="overwrite owned files edited in the project")
        p.set_defaults(fn=fn)
    p = sub.add_parser("workstation")
    p.add_argument("--home", help="home folder to install into (default: yours)")
    p.add_argument("--codex-footer-only", action="store_true", help="install only the native Codex CLI footer")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_workstation)
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
