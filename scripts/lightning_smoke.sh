#!/usr/bin/env zsh
set -euo pipefail

# Source interactive shell config so local runs pick up LIGHTNING_* credentials.
if [[ -f "$HOME/.zshrc" ]]; then
  source "$HOME/.zshrc" >/dev/null 2>&1 || true
fi

if [[ -z "${LIGHTNING_USER_ID:-}" || -z "${LIGHTNING_API_KEY:-}" ]]; then
  echo "Missing LIGHTNING_USER_ID or LIGHTNING_API_KEY. Add them to ~/.zshrc and rerun." >&2
  exit 2
fi

export LIGHTNING_USER_ID LIGHTNING_API_KEY

if ! command -v lightning >/dev/null 2>&1; then
  echo "Missing lightning CLI. Install with: uv tool install lightning-sdk" >&2
  exit 3
fi

echo "lightning_cli=$(command -v lightning)"
echo "auth_env=present"
lightning machine list
