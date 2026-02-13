#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STEALTH_DIR="$ROOT_DIR/run/stealth"
WORK_DIR="/tmp/despesas-stealth-work"
COMPOSE_FILE="$STEALTH_DIR/docker-compose.yml"
ENV_FILE="$STEALTH_DIR/.env"

usage() {
  cat <<USAGE
Usage: run/run-despesas-api.sh [up|up-signoz|down|logs|ps|rebuild]

Commands:
  up         Prepare stealth workspace and start containers (local collector)
  up-signoz  Start SigNoz stack and then start stealth app exporting to SigNoz
  down       Stop and remove stealth containers
  logs       Tail logs for all stealth services
  ps         Show stealth services status
  rebuild    Recreate stealth workspace and rebuild containers
USAGE
}

copy_tree() {
  local src="$1"
  local dst="$2"
  shift 2
  local excludes=("$@")
  local rsync_excludes=()

  for pattern in "${excludes[@]}"; do
    rsync_excludes+=(--exclude "$pattern")
  done

  if command -v rsync >/dev/null 2>&1; then
    if ! rsync -a --delete "${rsync_excludes[@]}" "$src/" "$dst/"; then
      echo "[stealth] rsync failed for $src, recreating $dst and retrying without --delete"
      rm -rf "$dst"
      mkdir -p "$dst"
      rsync -a "${rsync_excludes[@]}" "$src/" "$dst/"
    fi
  else
    rm -rf "$dst"
    mkdir -p "$dst"
    cp -a "$src/." "$dst/"
  fi
}

prepare_workspace() {
  echo "[stealth] Preparing isolated workspace at $WORK_DIR"
  mkdir -p "$WORK_DIR/despesa-api-mvp" "$WORK_DIR/despesas-front-mvp"

  copy_tree "$ROOT_DIR/despesa-api-mvp" "$WORK_DIR/despesa-api-mvp" "target"
  copy_tree "$ROOT_DIR/despesas-front-mvp" "$WORK_DIR/despesas-front-mvp" "node_modules" ".next"

  cp "$STEALTH_DIR/Dockerfile" "$WORK_DIR/despesa-api-mvp/Dockerfile.stealth"
  cp "$STEALTH_DIR/instrumentation.ts" "$WORK_DIR/despesas-front-mvp/instrumentation.ts"
  cp "$STEALTH_DIR/next.config.ts" "$WORK_DIR/despesas-front-mvp/next.config.ts"
}

compose() {
  STEALTH_WORKDIR="$WORK_DIR" docker compose \
    --env-file "$ENV_FILE" \
    -f "$COMPOSE_FILE" "$@"
}

load_env() {
  if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$ENV_FILE"
    set +a
  fi
}

up_stack() {
  local otlp_endpoint="${1:-}"
  prepare_workspace
  if [ -n "$otlp_endpoint" ]; then
    OTEL_EXPORTER_OTLP_ENDPOINT="$otlp_endpoint" compose up -d --build
  else
    compose up -d --build
  fi
}

cmd="${1:-up}"
load_env

case "$cmd" in
  up)
    up_stack
    echo "[stealth] Stack running: frontend=http://localhost:3300 api=http://localhost:8180 db=localhost:5543 otlp-http=http://localhost:14318"
    ;;
  up-signoz)
    "$ROOT_DIR/run/run-signoz.sh" up
    up_stack "${SIGNOZ_OTLP_ENDPOINT:-http://host.docker.internal:4318}"
    echo "[stealth] Stack running with SigNoz: frontend=http://localhost:3300 api=http://localhost:8180 db=localhost:5543 signoz-ui=http://localhost:${SIGNOZ_UI_PORT:-18080} otlp-http=${SIGNOZ_OTLP_ENDPOINT:-http://host.docker.internal:4318}"
    ;;
  down)
    compose down
    ;;
  logs)
    compose logs -f --tail=200
    ;;
  ps)
    compose ps
    ;;
  rebuild)
    prepare_workspace
    compose up -d --build --force-recreate
    ;;
  *)
    usage
    exit 1
    ;;
esac
