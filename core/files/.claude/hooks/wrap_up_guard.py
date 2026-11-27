"""Claude Code hook: when the context passes WRAP_UP_GUARD_AT percent (default 90), tell the agent once to finish the
step in hand and run the wrap-up (docs/process/session.md), before compaction or a full context loses the session.

Registered in .claude/settings.json for UserPromptSubmit and PostToolUse, run by $SCAFFOLD_PYTHON (set by the
workstation setup) or else `python`. Hooks are not told how full the context is; the status line is. The workstation
status line writes `used_percentage` for each session to <temp>/claude-context/<session_id>.json, and this hook
reads it. Without that file (another status line, or none)
the hook does nothing. Codex has no equivalent: its hooks see no context fill.

The warning is given once per session and armed again when the context drops 10 points below the threshold
(after a compaction). When it fires, the user sees a one-line notice in the chat as well. WRAP_UP_GUARD_LOG=1 appends
every run's reading and decision to <temp>/claude-context/guard.log (kept under 1 MB), to see why it stayed quiet.
Standard library only; any failure exits quietly so a session is never blocked.
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

STALE_AFTER = 15 * 60  # seconds: an older reading is from a session no longer updating its status line
FOLDER = Path(tempfile.gettempdir()) / "claude-context"
LOG_LIMIT = 1_000_000  # bytes: past this the log is moved to guard.log.1 and started again


def decide(data: dict) -> str:
    """Warn if due, and say what was decided, for the log."""
    session = data.get("session_id")
    if not session:
        return "no session_id"
    reading = FOLDER / f"{session}.json"
    marker = FOLDER / f"{session}.warned"
    if not reading.exists():
        return "no reading (the workstation status line has not written one)"
    state = json.loads(reading.read_text(encoding="utf-8"))
    used = state.get("used_percentage")
    if used is None:
        return "reading has no used_percentage"
    age = time.time() - state.get("at", 0)
    if age > STALE_AFTER:
        return f"used={used:.0f}% stale ({age / 60:.0f} min old)"
    threshold = float(os.environ.get("WRAP_UP_GUARD_AT", "90"))
    seen = f"used={used:.0f}% threshold={threshold:.0f}"
    if used < threshold:
        if used < threshold - 10 and marker.exists():
            marker.unlink()
            return f"{seen} below, armed again"
        return f"{seen} below"
    if marker.exists():
        return f"{seen} already warned"
    marker.write_text(str(used), encoding="utf-8")
    message = (
        f"The context is {used:.0f}% full. Finish the step in hand, take on nothing new, and run the wrap-up now "
        "(docs/process/session.md, \"Wrap-up\"): tell the user in one line, verify, write back, commit. Then "
        "suggest a fresh session to continue."
    )
    print(json.dumps({
        "systemMessage": f"wrap-up guard: context {used:.0f}% full, asked the agent to wrap up",
        "hookSpecificOutput": {"hookEventName": data.get("hook_event_name", "PostToolUse"),
                               "additionalContext": message},
    }))
    return f"{seen} WARNED"


def log(data: dict, decision: str) -> None:
    if os.environ.get("WRAP_UP_GUARD_LOG", "") in ("", "0"):
        return
    try:
        FOLDER.mkdir(exist_ok=True)
        path = FOLDER / "guard.log"
        if path.exists() and path.stat().st_size > LOG_LIMIT:
            path.replace(FOLDER / "guard.log.1")
        line = (f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {str(data.get('session_id', '?'))[:8]}  "
                f"{data.get('hook_event_name', '?'):<16}  {decision}\n")
        with path.open("a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass


def main() -> None:
    data = {}
    try:
        data = json.load(sys.stdin)
        decision = decide(data)
    except Exception as error:  # noqa: BLE001 - a guard must never break the session
        decision = f"error: {type(error).__name__}: {error}"
    log(data if isinstance(data, dict) else {}, decision)


if __name__ == "__main__":
    main()
