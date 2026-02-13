#!/usr/bin/env bash
set -euo pipefail

SIGNOZ_ROOT="${SIGNOZ_ROOT:-/tmp/signoz}"
SIGNOZ_REPO="${SIGNOZ_REPO:-https://github.com/SigNoz/signoz.git}"
SIGNOZ_REF="${SIGNOZ_REF:-main}"
COMPOSE_DIR="$SIGNOZ_ROOT/deploy/docker"
SIGNOZ_UI_PORT="${SIGNOZ_UI_PORT:-18080}"
SIGNOZ_OTLP_GRPC_PORT="${SIGNOZ_OTLP_GRPC_PORT:-4317}"
SIGNOZ_OTLP_HTTP_PORT="${SIGNOZ_OTLP_HTTP_PORT:-4318}"
COMPOSE_FILE="$COMPOSE_DIR/docker-compose.yaml"

usage() {
  cat <<USAGE
Usage: run/run-signoz.sh [up|down|ps|logs|refresh]

Commands:
  up       Clone/update SigNoz deploy and start stack
  down     Stop SigNoz stack
  ps       Show SigNoz services status
  logs     Tail SigNoz logs
  refresh  Git pull (fast-forward) to SIGNOZ_REF in local clone
USAGE
}

ensure_repo() {
  if [ ! -d "$SIGNOZ_ROOT/.git" ]; then
    echo "[signoz] Cloning $SIGNOZ_REPO into $SIGNOZ_ROOT"
    git clone --depth 1 -b "$SIGNOZ_REF" "$SIGNOZ_REPO" "$SIGNOZ_ROOT"
  fi

  if [ ! -f "$COMPOSE_DIR/docker-compose.yaml" ]; then
    echo "[signoz] Repository checkout incomplete, repairing..."
    git -C "$SIGNOZ_ROOT" fetch --depth 1 origin "$SIGNOZ_REF"
    git -C "$SIGNOZ_ROOT" checkout -f "$SIGNOZ_REF"
  fi
}

patch_ports() {
  if [ ! -f "$COMPOSE_FILE" ]; then
    echo "[signoz] Missing compose file at $COMPOSE_FILE"
    exit 1
  fi

  sed -i \
    -e "s/\"[0-9]\\+:8080\" # signoz port/\"${SIGNOZ_UI_PORT}:8080\" # signoz port/" \
    -e "s/\"[0-9]\\+:4317\" # OTLP gRPC receiver/\"${SIGNOZ_OTLP_GRPC_PORT}:4317\" # OTLP gRPC receiver/" \
    -e "s/\"[0-9]\\+:4318\" # OTLP HTTP receiver/\"${SIGNOZ_OTLP_HTTP_PORT}:4318\" # OTLP HTTP receiver/" \
    "$COMPOSE_FILE"
}

refresh_repo() {
  ensure_repo
  echo "[signoz] Refreshing repository at $SIGNOZ_ROOT ($SIGNOZ_REF)"
  git -C "$SIGNOZ_ROOT" checkout "$SIGNOZ_REF"
  git -C "$SIGNOZ_ROOT" pull --ff-only origin "$SIGNOZ_REF"
  patch_ports
}

compose() {
  (cd "$COMPOSE_DIR" && docker compose "$@")
}

cmd="${1:-up}"

case "$cmd" in
  up)
    ensure_repo
    patch_ports
    compose up -d --remove-orphans
    echo "[signoz] Running. UI: http://localhost:${SIGNOZ_UI_PORT}"
    echo "[signoz] OTLP endpoints: grpc=localhost:${SIGNOZ_OTLP_GRPC_PORT} http=localhost:${SIGNOZ_OTLP_HTTP_PORT}"
    ;;
  down)
    ensure_repo
    compose down
    ;;
  ps)
    ensure_repo
    compose ps
    ;;
  logs)
    ensure_repo
    compose logs -f --tail=200
    ;;
  refresh)
    refresh_repo
    ;;
  *)
    usage
    exit 1
    ;;
esac
