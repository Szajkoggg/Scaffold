"""Claude Code hook: when the context passes WRAP_UP_GUARD_AT percent (default 90), tell the agent once to finish the
step in hand and run the wrap-up (docs/process/session.md), before compaction or a full context loses the session.

Registered in .claude/settings.json for UserPromptSubmit and PostToolUse. Hooks are not told how full the context
is; the status line is. The workstation status line writes `used_percentage` for each session to
<temp>/claude-context/<session_id>.json, and this hook reads it. Without that file (another status line, or none)
the hook does nothing. Codex has no equivalent: its hooks see no context fill.

The warning is given once per session and armed again when the context drops 10 points below the threshold
(after a compaction). Standard library only; any failure exits quietly so a session is never blocked.
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

STALE_AFTER = 15 * 60  # seconds: an older reading is from a session no longer updating its status line


def main() -> None:
    data = json.load(sys.stdin)
    session = data.get("session_id")
    if not session:
        return
    folder = Path(tempfile.gettempdir()) / "claude-context"
    reading = folder / f"{session}.json"
    marker = folder / f"{session}.warned"
    state = json.loads(reading.read_text(encoding="utf-8"))
    used = state.get("used_percentage")
    if used is None or time.time() - state.get("at", 0) > STALE_AFTER:
        return
    threshold = float(os.environ.get("WRAP_UP_GUARD_AT", "90"))
    if used < threshold:
        if used < threshold - 10 and marker.exists():
            marker.unlink()
        return
    if marker.exists():
        return
    marker.write_text(str(used), encoding="utf-8")
    message = (
        f"The context is {used:.0f}% full. Finish the step in hand, take on nothing new, and run the wrap-up now "
        "(docs/process/session.md, \"Wrap-up\"): tell the user in one line, verify, write back, commit. Then "
        "suggest a fresh session to continue."
    )
    print(json.dumps({"hookSpecificOutput": {"hookEventName": data.get("hook_event_name", "PostToolUse"),
                                             "additionalContext": message}}))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001 - a guard must never break the session
        pass
