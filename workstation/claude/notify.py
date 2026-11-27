"""Claude Code hook: a desktop notification when a session needs you, so a chat in another window is not left waiting.

Registered by the workstation setup in ~/.claude/settings.json for three events:

- UserPromptSubmit: records when the turn started (<temp>/claude-context/<session>.turn); no notification.
- Stop: "finished", only when the turn ran at least SCAFFOLD_NOTIFY_AFTER seconds (default 30), so quick replies you
  are watching do not pop up.
- Notification: "needs your permission" when Claude Code asks for a permission; other notifications are ignored.

The title is the session's folder name. SCAFFOLD_NOTIFY=0 turns it off. Shown by a PowerShell toast on Windows,
osascript on macOS, notify-send on Linux. The hook waits for it (about 0.2 s): a detached process is killed with the
hook's process tree. Standard library only; any failure exits quietly so a session is never blocked.
"""
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

FOLDER = Path(tempfile.gettempdir()) / "claude-context"


def windows_toast(title: str, body: str) -> list[str]:
    """The PowerShell command that shows a toast, under PowerShell's own app id (no registration needed)."""
    quote = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("'", "''")
    script = (
        "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType=WindowsRuntime]"
        " | Out-Null;"
        "[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType=WindowsRuntime] | Out-Null;"
        "$x = New-Object Windows.Data.Xml.Dom.XmlDocument;"
        f"$x.LoadXml('<toast><visual><binding template=\"ToastGeneric\"><text>{quote(title)}</text>"
        f"<text>{quote(body)}</text></binding></visual></toast>');"
        r"$app = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe';"
        "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($app)"
        ".Show([Windows.UI.Notifications.ToastNotification]::new($x))"
    )
    encoded = base64.b64encode(script.encode("utf-16-le")).decode()
    return ["powershell", "-NoProfile", "-NonInteractive", "-EncodedCommand", encoded]


def show(title: str, body: str) -> None:
    quiet = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "timeout": 10}
    if sys.platform == "win32":
        subprocess.run(windows_toast(title, body), creationflags=subprocess.CREATE_NO_WINDOW, **quiet)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.run(["osascript", "-e", f"display notification {json.dumps(body)} with title {json.dumps(title)}"],
                       **quiet)
    else:
        subprocess.run(["notify-send", title, body], **quiet)


def main() -> None:
    if os.environ.get("SCAFFOLD_NOTIFY", "1") == "0":
        return
    data = json.load(sys.stdin)
    event = data.get("hook_event_name")
    session = str(data.get("session_id") or "")
    turn = FOLDER / f"{session}.turn"
    title = "Claude: " + (Path(data.get("cwd") or ".").resolve().name or "session")
    if event == "UserPromptSubmit" and session:
        FOLDER.mkdir(exist_ok=True)
        turn.write_text(str(time.time()), encoding="utf-8")
    elif event == "Stop" and session:
        try:
            started = float(turn.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return  # no recorded start: not a turn this hook saw begin
        turn.unlink(missing_ok=True)
        if time.time() - started >= float(os.environ.get("SCAFFOLD_NOTIFY_AFTER", "30")):
            show(title, "Finished")
    elif event == "Notification" and data.get("notification_type", "permission_prompt") == "permission_prompt":
        show(title, data.get("message") or "Needs your permission")


if __name__ == "__main__":
    try:
        main()
    except Exception:  # noqa: BLE001, S110 - a notification must never break the session
        pass
