#!/usr/bin/env bash
# jq is not installed on this machine; parse the status-line JSON with Python.
exec python "$HOME/.claude/statusline.py"
