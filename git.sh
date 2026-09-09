#!/bin/bash
# already done by claude (stopped short of push):
#   git init -b main ; git add . ; git commit ; git remote add origin <url>

# ── PUSH when ready ─────────────────────────────────────────────────────────
# if the github repo does not exist yet:
#   gh repo create helper_runtime_env --public --source=. --remote=origin --push
# if it already exists (remote is set):
#   git push -u origin main

git remote -v
gh repo view --web
