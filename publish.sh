#!/usr/bin/env bash
# 兼容入口：转到 site 统一发布脚本（只推 research）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
SITE="${SITE_DIR:-$ROOT/../site}"
MSG="${1:-}"
export RESEARCH_DIR="$ROOT"
if [[ -n "$MSG" ]]; then
  export MSG
fi
exec bash "$SITE/scripts/publish.sh" research
