"""Claude Code status line: where you are, the model and effort, and fill bars for the context and the usage limits.

Reads the status line JSON on stdin (https://code.claude.com/docs/en/statusline.md) and prints two or three lines:

    ~/Code/project | main ●3 ↑1 | wt feature-x | Opus 5.5 · medium | cache 48m · 608k
    ctx ███░░░░░░░ 31%   5h █████│░░░░ 48% ↻ 2h05m   7d ██░│░░░░░░ 21% ↻ 3d4h
    plan offline-mode 3/7 | health 2 due | scaffold ↑3

- Colours run evenly from green through yellow and orange to red in OKLCH (equally bright, readable on light and
  dark backgrounds): each bar cell has the colour of its position, the percentage the colour of its value.
- The │ in a limit bar is the pace marker: how much of the window's time has passed. Fill ahead of it means the
  limit is being used faster than it renews.
- ●n changed files, ↑n commits not pushed, ↓n commits not pulled. "wt" names the git worktree, if any.
- "cache" is the prompt cache: warm with the time until it expires, or cold (the next message re-reads the whole
  context at full price).
- Past 70 % of the context the bar says "wrap up?". The fill is also written to <temp>/claude-context/<session>.json
  for a project's wrap-up guard hook, which hooks cannot learn otherwise.
- In a project made with the scaffold, a third line: the active plan and its ticked steps, the health checks due
  (docs/HEALTH.md), and how many scaffold commits the project has not taken yet (scaffold ↑n). The scaffold's folder
  comes from SCAFFOLD_HOME or the workstation setup's record (~/.scaffold/workstation.json).

Truecolor where the terminal says so (COLORTERM, Windows Terminal), else the 256-colour cube;
STATUSLINE_COLORS=truecolor|256 overrides. Values that are missing are left out, never shown as zero. Standard
library only.
"""
import json
import math
import os
import re
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

RESET = "\033[0m"
BAR_WIDTH = 10
WINDOWS = {"5h": 5 * 3600, "7d": 7 * 86400}  # length of each limit window, for the pace marker
WRAP_UP_AT = 70


def truecolor() -> bool:
    forced = os.environ.get("STATUSLINE_COLORS", "").lower()
    if forced:
        return forced in ("truecolor", "24bit")
    return os.environ.get("COLORTERM", "").lower() in ("truecolor", "24bit") or bool(os.environ.get("WT_SESSION"))


TRUECOLOR = truecolor()
# One lightness for any background: the status line's background follows the terminal, not Claude Code's theme.
# OKLCH 0.62 keeps every colour of the sweep at >= 3.4:1 on white and >= 5:1 on near-black; grey 128 likewise.
LIGHTNESS = 0.62
HUE_GREEN, HUE_RED, CHROMA = 145.0, 27.0, 0.17
GREY = "\033[38;2;128;128;128m" if TRUECOLOR else "\033[38;5;244m"  # labels, separators, empty cells


def oklch_to_rgb(lightness: float, chroma: float, hue: float) -> tuple[int, int, int]:
    """OKLCH to sRGB (0-255); chroma is reduced until the colour fits in sRGB."""
    while True:
        a, b = chroma * math.cos(math.radians(hue)), chroma * math.sin(math.radians(hue))
        lc = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
        mc = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
        sc = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
        linear = (4.0767416621 * lc - 3.3077115913 * mc + 0.2309699292 * sc,
                  -1.2684380046 * lc + 2.6097574011 * mc - 0.3413193965 * sc,
                  -0.0041960863 * lc - 0.7034186147 * mc + 1.7076147010 * sc)
        if all(-1e-4 <= c <= 1 + 1e-4 for c in linear) or chroma <= 0:
            break
        chroma -= 0.005
    srgb = [12.92 * c if c <= 0.0031308 else 1.055 * max(c, 0) ** (1 / 2.4) - 0.055 for c in linear]
    return tuple(round(max(0.0, min(1.0, c)) * 255) for c in srgb)


def colour(percent: float) -> str:
    """An even sweep from green (0 %) through yellow and orange to red (100 %), equally bright throughout."""
    t = max(0.0, min(100.0, percent)) / 100
    r, g, b = oklch_to_rgb(LIGHTNESS, CHROMA, HUE_GREEN + (HUE_RED - HUE_GREEN) * t)
    if TRUECOLOR:
        return f"\033[38;2;{r};{g};{b}m"
    return f"\033[38;5;{16 + 36 * round(r / 255 * 5) + 6 * round(g / 255 * 5) + round(b / 255 * 5)}m"


def epoch(value) -> float | None:
    """A time field (resets_at, expires_at): Unix epoch seconds, or None when absent or null."""
    return float(value) if isinstance(value, (int, float)) else None


def duration(seconds: float) -> str:
    seconds = int(seconds)
    days, rest = divmod(seconds, 86400)
    hours, rest = divmod(rest, 3600)
    minutes = rest // 60
    return f"{days}d{hours}h" if days else f"{hours}h{minutes:02d}m" if hours else f"{max(minutes, 1)}m"


def bar(label: str, percent, resets_at=None) -> tuple[str, str]:
    """The bar with its label, and an extra (countdown or hint) that is dropped first when space is short."""
    if not isinstance(percent, (int, float)):
        return "", ""
    p = max(0.0, min(100.0, float(percent)))
    filled = round(p / 100 * BAR_WIDTH)
    cells = [f"{colour((i + 0.5) / BAR_WIDTH * 100)}█" if i < filled else f"{GREY}░" for i in range(BAR_WIDTH)]
    extra = ""
    reset = epoch(resets_at)
    if label in WINDOWS and reset is not None:
        left = reset - time.time()
        if left > 0:
            passed = 1 - min(1.0, left / WINDOWS[label])
            cells.insert(round(passed * BAR_WIDTH), f"{RESET}│")  # the pace marker: the time already passed
            extra = f" {GREY}↻ {duration(left)}{RESET}"
    if label == "ctx" and p >= WRAP_UP_AT:
        extra = f" {colour(p)}wrap up?{RESET}"
    return f"{GREY}{label}{RESET} {''.join(cells)}{RESET} {colour(p)}{p:.0f}%{RESET}", extra


def git_state(cwd: str) -> str:
    """Branch, changed files, commits ahead and behind, from one git call."""
    try:
        out = subprocess.run(["git", "-C", cwd, "status", "--porcelain=v1", "--branch"],
                             capture_output=True, text=True, timeout=2, check=True).stdout.splitlines()
    except (OSError, subprocess.SubprocessError):
        return ""
    if not out or not out[0].startswith("## "):
        return ""
    head = out[0][3:]
    branch = head.split("...")[0].split(" ")[0]
    if branch.startswith("HEAD"):
        branch = "(detached)"
    elif branch.startswith("No"):  # "No commits yet on main"
        branch = head.rsplit(" ", 1)[-1]
    marks = []
    changed = len(out) - 1
    if changed:
        marks.append(f"{colour(60)}●{changed}{RESET}")
    for word, arrow in (("ahead", "↑"), ("behind", "↓")):
        if f"{word} " in head:
            count = head.split(f"{word} ")[1].split("]")[0].split(",")[0]
            marks.append(f"{GREY}{arrow}{count}{RESET}")
    return branch + ("" if not marks else " " + " ".join(marks))


def tokens(count: float) -> str:
    return f"{count / 1e6:.1f}M" if count >= 1e6 else f"{max(1, round(count / 1000))}k"


def cache_state(cache) -> str:
    """Warm: the time until it goes cold (orange under 10 min, red under 3) and the tokens a cold start would
    rebuild. Cold: what the next message rebuilds."""
    if not isinstance(cache, dict) or "warm" not in cache:
        return ""
    rebuild = cache.get("recache_tokens_if_cold")
    rebuild = rebuild if isinstance(rebuild, (int, float)) and rebuild > 0 else None
    expires = epoch(cache.get("expires_at"))
    if cache.get("warm") and expires is not None and expires > time.time():
        left = expires - time.time()
        tone = colour(100) if left < 180 else colour(75) if left < 600 else ""
        size = f" {GREY}·{RESET} {tokens(rebuild)}" if rebuild else ""
        return f"{GREY}cache{RESET} {tone}{duration(left)}{RESET}{size}"
    size = f" {GREY}·{RESET} {tokens(rebuild)} to rebuild" if rebuild else ""
    return f"{GREY}cache{RESET} {colour(80)}cold{RESET}{size}"


# ---------------------------------------------------------------- the scaffold's project files (third line)

def project_root(data: dict) -> Path | None:
    """The scaffolded project the session is in: the nearest folder upwards with .scaffold/manifest.json."""
    start = (data.get("workspace") or {}).get("project_dir") or data.get("cwd")
    if not start:
        return None
    folder = Path(start)
    for candidate in (folder, *folder.parents):
        if (candidate / ".scaffold" / "manifest.json").is_file():
            return candidate
    return None


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def plan_state(root: Path) -> str:
    """The active plan (approved, in progress or stopped) and its ticked steps."""
    active = []
    for plan in sorted((root / "docs" / "plans").glob("*.md")):
        if plan.name == "README.md":
            continue
        text = read(plan)
        status = re.search(r"^Status:\s*(.+?)\s*$", text, re.M)
        status = status.group(1).lower() if status else ""
        if not status.startswith(("approved", "in progress", "stopped")):
            continue
        steps = re.search(r"^## Steps\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
        boxes = re.findall(r"^- \[([ xX])\]", steps.group(1) if steps else "", re.M)
        done = sum(1 for box in boxes if box != " ")
        name = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", plan.stem)
        active.append((name, done, len(boxes), status.startswith("stopped")))
    if not active:
        return ""
    name, done, total, stopped = active[0]
    progress = f" {colour(100 * done / total if total else 0)}{done}/{total}{RESET}" if total else ""
    flag = f" {colour(90)}stopped{RESET}" if stopped else ""
    more = f" {GREY}+{len(active) - 1}{RESET}" if len(active) > 1 else ""
    return f"{GREY}plan{RESET} {name}{progress}{flag}{more}"


def health_state(root: Path, applied: date | None) -> str:
    """Health checks past their period (docs/HEALTH.md, the ledger); "never" counts from when the scaffold came."""
    ledger = re.search(r"^## Ledger\s*$(.*?)(?=^## |\Z)", read(root / "docs" / "HEALTH.md"), re.M | re.S)
    if not ledger:
        return ""
    unit_days = {"day": 1, "week": 7, "month": 30, "year": 365}
    due = 0
    for row in re.findall(r"^\|(.+)\|\s*$", ledger.group(1), re.M):
        cells = [c.strip() for c in row.split("|")]
        if len(cells) < 4:
            continue
        period = re.match(r"(\d+)\s*(day|week|month|year)s?\b", cells[2].lower())
        if not period:
            continue  # the header, the separator, or a trigger instead of a period
        last = re.search(r"\d{4}-\d{2}-\d{2}", cells[3])
        since = date.fromisoformat(last.group(0)) if last else applied
        if since and since + timedelta(days=int(period.group(1)) * unit_days[period.group(2)]) < date.today():
            due += 1
    return f"{GREY}health{RESET} {colour(75)}{due} due{RESET}" if due else ""


def scaffold_home() -> str | None:
    """Where the scaffold repository is: SCAFFOLD_HOME, or what the workstation setup recorded."""
    if os.environ.get("SCAFFOLD_HOME"):
        return os.environ["SCAFFOLD_HOME"]
    try:
        with open(os.path.expanduser("~/.scaffold/workstation.json"), encoding="utf-8") as f:
            return json.load(f).get("scaffold", {}).get("home")
    except (OSError, ValueError):
        return None


def scaffold_state(version: str) -> str:
    """How many scaffold commits the project has not taken yet (scaffold.py update brings them)."""
    version = version.removesuffix("-dirty")
    home = scaffold_home()
    if not version or version == "unversioned" or not home:
        return ""
    try:
        count = int(subprocess.run(["git", "-C", home, "rev-list", "--count", f"{version}..HEAD"],
                                   capture_output=True, text=True, timeout=2, check=True).stdout.strip())
    except (OSError, subprocess.SubprocessError, ValueError):
        return ""
    return f"{GREY}scaffold{RESET} {colour(60)}↑{count}{RESET}" if count else ""


def third_line(data: dict) -> str:
    root = project_root(data)
    if root is None:
        return ""
    try:
        manifest = json.loads(read(root / ".scaffold" / "manifest.json"))
    except ValueError:
        manifest = {}
    scaffold = manifest.get("scaffold") or {}
    try:
        applied = date.fromisoformat(scaffold.get("applied", ""))
    except ValueError:
        applied = None
    parts = [plan_state(root), health_state(root, applied), scaffold_state(str(scaffold.get("version", "")))]
    return f" {GREY}|{RESET} ".join(p for p in parts if p)


def first_line(data: dict, git: str, short: bool = False) -> str:
    workspace = data.get("workspace") or {}
    raw = data.get("cwd") or workspace.get("current_dir") or ""
    home = os.path.expanduser("~")
    shown = "~" + raw[len(home):] if raw and os.path.normcase(raw).startswith(os.path.normcase(home)) else raw
    shown = shown.replace("\\", "/")
    if short and shown.count("/") > 2:
        shown = "…/" + "/".join(shown.rstrip("/").split("/")[-2:])
    parts = [shown]
    if git:
        parts.append(git)
    worktree = (data.get("worktree") or {}).get("name") or workspace.get("git_worktree")
    if worktree:
        parts.append(f"{GREY}wt{RESET} {worktree}")
    model = (data.get("model") or {}).get("display_name") or (data.get("model") or {}).get("id") or "?"
    effort = (data.get("effort") or {}).get("level")
    parts.append(model + (f" {GREY}·{RESET} {effort}" if effort else ""))
    cache = cache_state(data.get("prompt_cache"))
    if cache:
        parts.append(cache)
    return f" {GREY}|{RESET} ".join(parts)


def visible_length(text: str) -> int:
    length, escape = 0, False
    for ch in text:
        if ch == "\033":
            escape = True
        elif escape and ch == "m":
            escape = False
        elif not escape:
            length += 1
    return length


def share_context(data: dict) -> None:
    """Write the context fill for the session where hooks can read it: hooks are not told it, the status line is.
    A project's wrap-up guard (.claude/hooks/wrap_up_guard.py) reads <temp>/claude-context/<session_id>.json."""
    session = data.get("session_id")
    window = data.get("context_window") or {}
    if not session or window.get("used_percentage") is None:
        return
    import tempfile
    try:
        folder = Path(tempfile.gettempdir()) / "claude-context"
        folder.mkdir(exist_ok=True)
        (folder / f"{session}.json").write_text(json.dumps({
            "used_percentage": window["used_percentage"],
            "context_window_size": window.get("context_window_size"),
            "at": time.time(),
        }), encoding="utf-8")
    except OSError:
        pass


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        data = {}
    capture = os.path.expanduser("~/.claude/statusline-capture")
    if os.path.exists(capture):  # debugging aid: create this file, read statusline-last.json, delete the file
        with open(os.path.expanduser("~/.claude/statusline-last.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    share_context(data)
    limits = data.get("rate_limits") or {}
    five, seven = limits.get("five_hour") or {}, limits.get("seven_day") or {}
    bars = [b for b in (
        bar("ctx", (data.get("context_window") or {}).get("used_percentage")),
        bar("5h", five.get("used_percentage"), five.get("resets_at")),
        bar("7d", seven.get("used_percentage"), seven.get("resets_at")),
    ) if b[0]]
    width = int(os.environ.get("COLUMNS", "120")) - 4
    second = "   ".join(text + extra for text, extra in bars)
    if visible_length(second) > width:
        second = "   ".join(text for text, _ in bars)
    cwd = data.get("cwd") or (data.get("workspace") or {}).get("current_dir") or ""
    git = git_state(cwd) if cwd else ""  # once: the short form below reuses it
    first = first_line(data, git)
    if visible_length(first) > width:
        first = first_line(data, git, short=True)
    print(first)
    if second:
        print(second)
    third = third_line(data)
    if third:
        print(third)


main()
