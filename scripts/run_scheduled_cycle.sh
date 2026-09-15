#!/usr/bin/env zsh
set -e

# Source shell environment so credentials from ~/.zshrc are active
if [ -f "$HOME/.zshrc" ]; then
    source "$HOME/.zshrc" 2>/dev/null || true
fi

SCRIPT_DIR="${0:A:h}"
PROJECT_ROOT="${SCRIPT_DIR:h}"

# Ensure default environment variables if not exported
export ENVIRONMENT="${ENVIRONMENT:-demo}"
export TRADING212_CACHE_DIR="${PROJECT_ROOT}/../trading212-mcp-server/.cache/trading212-v3"
export PYTHONPATH="${PROJECT_ROOT}/src:${PYTHONPATH}"
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

cd "${PROJECT_ROOT}"

exec "${PROJECT_ROOT}/.venv/bin/trading-bot" run-cycle
