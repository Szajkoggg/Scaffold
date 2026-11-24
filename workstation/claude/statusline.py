"""Claude Code status line: where you are, the model and effort, and fill bars for the context and the usage limits.

Reads the status line JSON on stdin (https://code.claude.com/docs/en/statusline.md) and prints two lines:

    ~/Code/project | main ●3 ↑1 | wt feature-x | Opus 5.5 · medium | cache 4m
    ctx ███░░░░░░░ 31%   5h █████│░░░░ 48% ↻2h05m   7d ██░│░░░░░░ 21% ↻3d4h

- Colours run evenly from green through yellow and orange to red in OKLCH (equally bright, readable on light and
  dark backgrounds): each bar cell has the colour of its position, the percentage the colour of its value.
- The │ in a limit bar is the pace marker: how much of the window's time has passed. Fill ahead of it means the
  limit is being used faster than it renews.
- ●n changed files, ↑n commits not pushed, ↓n commits not pulled. "wt" names the git worktree, if any.
- "cache" is the prompt cache: warm with the time until it expires, or cold (the next message re-reads the whole
  context at full price).
- Past 70 % of the context the bar says "wrap up?".

Truecolor where the terminal says so (COLORTERM, Windows Terminal), else the 256-colour cube;
STATUSLINE_COLORS=truecolor|256 overrides. Values that are missing are left out, never shown as zero. Standard
library only.
"""
import json
import math
import os
import subprocess
import sys
import time

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
            extra = f" {GREY}↻{duration(left)}{RESET}"
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


def cache_state(cache) -> str:
    if not isinstance(cache, dict) or "warm" not in cache:
        return ""
    expires = epoch(cache.get("expires_at"))
    if cache.get("warm") and expires is not None and expires > time.time():
        return f"{GREY}cache{RESET} {duration(expires - time.time())}"
    return f"{GREY}cache{RESET} {colour(80)}cold{RESET}"


def first_line(data: dict, short: bool = False) -> str:
    workspace = data.get("workspace") or {}
    raw = data.get("cwd") or workspace.get("current_dir") or ""
    home = os.path.expanduser("~")
    shown = "~" + raw[len(home):] if raw and os.path.normcase(raw).startswith(os.path.normcase(home)) else raw
    shown = shown.replace("\\", "/")
    if short and shown.count("/") > 2:
        shown = "…/" + "/".join(shown.rstrip("/").split("/")[-2:])
    parts = [shown]
    git = git_state(raw) if raw else ""
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
    first = first_line(data)
    if visible_length(first) > width:
        first = first_line(data, short=True)
    print(first)
    if second:
        print(second)


main()
