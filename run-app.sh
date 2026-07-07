#!/usr/bin/env bash
#
# Runs YOUR app with the fabric-local shim loaded, so any Fabric connection your
# app opens to localhost:1433 is auto-redirected to the local mock — with zero
# changes to your app source.
#
# Configure via env vars (or export them in your shell first):
#   APP_DIR   directory to run your app from            (default: current dir)
#   APP_CMD   command that starts your app              (default: "uv run python server.py")
# Plus whatever secrets your app needs, e.g. OPENAI_API_KEY / ANTHROPIC_API_KEY.
#
# Example:
#   APP_DIR=/path/to/app OPENAI_API_KEY=sk-... ANTHROPIC_API_KEY=sk-... ./run-app.sh
#
# (Make sure the mock is up first:  ./fabric-local.sh run)
#
set -euo pipefail

FABRIC_LOCAL_DIR="$(cd "$(dirname "$0")" && pwd)"

# --- fabric-local shim env (SA password comes from fabric-local/.env) ---------
[ -f "$FABRIC_LOCAL_DIR/.env" ] && { set -a; . "$FABRIC_LOCAL_DIR/.env"; set +a; }
export PYTHONPATH="$FABRIC_LOCAL_DIR/shim:${PYTHONPATH:-}"
export FABRIC_LOCAL_MOCK=1
export FABRIC_LOCAL_SA_PASSWORD="${SA_PASSWORD:-LocalFabric_123!}"

# --- your app (override with env vars) ----------------------------------------
APP_DIR="${APP_DIR:-.}"
APP_CMD="${APP_CMD:-uv run python server.py}"

cd "$APP_DIR"
echo "[run-app] launching in $APP_DIR: $APP_CMD (fabric shim active)"
exec ${APP_CMD}
