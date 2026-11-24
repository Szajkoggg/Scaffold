import sys, json, os, subprocess

try:
    data = json.load(sys.stdin)
except Exception:
    data = {}

raw_cwd = data.get("cwd") or (data.get("workspace") or {}).get("current_dir") or ""
home = os.path.expanduser("~")
cwd = raw_cwd
if raw_cwd and os.path.normcase(raw_cwd).startswith(os.path.normcase(home)):
    cwd = "~" + raw_cwd[len(home):]
cwd = cwd.replace("\\", "/")

branch = "(detached)"
if raw_cwd:
    try:
        out = subprocess.check_output(
            ["git", "-C", raw_cwd, "symbolic-ref", "--short", "HEAD"],
            stderr=subprocess.DEVNULL, text=True).strip()
        branch = out or "(detached)"
    except Exception:
        branch = "(detached)"

model = (data.get("model") or {}).get("display_name") \
    or (data.get("model") or {}).get("id") or "unknown"

cw = data.get("context_window") or {}
pct = cw.get("used_percentage")
context = "{}%".format(round(pct)) if isinstance(pct, (int, float)) else "-%"

sys.stdout.write("{} | {} | {} | {}".format(cwd, branch, model, context))
