#!/usr/bin/env bash
# 本地改完 posts/ 后：build → push research → 空提交触发 site 重新拉仓部署
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SITE="${SITE_DIR:-$ROOT/../site}"
MSG="${1:-update research notes}"

cd "$ROOT"

echo "==> build"
python3 build.py

echo "==> push research"
git add -A posts static build.py README.md publish.sh 2>/dev/null || true
if git diff --cached --quiet && git diff --quiet; then
  # 工作区干净：仍 push 一下（可能本地已 commit 未推）
  if [[ -n "$(git log origin/main..HEAD --oneline 2>/dev/null || true)" ]]; then
    git push origin main
  else
    echo "research: nothing new to commit"
  fi
else
  # 老 git 没有 --trailer；直接 -m
  git commit -m "$MSG" || true
  git push origin main
fi

if [[ ! -d "$SITE/.git" ]]; then
  echo "site repo not found at $SITE — set SITE_DIR=... or skip trigger" >&2
  exit 0
fi

echo "==> trigger site rebuild"
cd "$SITE"
git commit --allow-empty -m "chore: rebuild site (research)"
git push origin main

echo "done. wait for site CI → https://shippingwang.com/research/"
