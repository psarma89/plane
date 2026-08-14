#!/usr/bin/env bash
# Destroy the Plane stack for the current checkout, including its data.
# Usage: env-teardown.sh [--yes]
set -euo pipefail

COMPOSE_FILE="docker-compose-local.yml"

red() { printf '\033[0;31m%s\033[0m\n' "$1"; }
green() { printf '\033[0;32m%s\033[0m\n' "$1"; }
bold() { printf '\033[1m%s\033[0m\n' "$1"; }
die() { red "Error: $1" >&2; exit 1; }

[ -f "$COMPOSE_FILE" ] || die "run this from a Plane checkout root ($COMPOSE_FILE not found)"

read_var() { grep "^$2=" "$1" 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' || true; }

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)
PROJECT=$(read_var .env COMPOSE_PROJECT_NAME)
[ -n "$PROJECT" ] || PROJECT=$(basename "$PWD")

# Frontend ports only. The API, PostgreSQL, Valkey, and MinIO ports are
# published by Docker, and the process that holds them is com.docker.backend.
# Killing that stops the Docker daemon itself, which then leaves the containers
# and volumes in place. `docker compose down` is what removes those.
PORTS=""
for key in PLANE_HOST_WEB_PORT PLANE_HOST_ADMIN_PORT PLANE_HOST_SPACE_PORT; do
  value=$(read_var .env "$key")
  [ -n "$value" ] && PORTS="$PORTS $value"
done
LIVE_PORT=$(read_var apps/live/.env PORT)
[ -n "$LIVE_PORT" ] && PORTS="$PORTS $LIVE_PORT"

# Never signal Docker itself, whatever a port lookup returns.
is_docker_process() {
  case "$(ps -p "$1" -o comm= 2>/dev/null)" in
    *docker*|*Docker*) return 0 ;;
    *) return 1 ;;
  esac
}

# ---------------------------------------------------------------- report

bold "This will destroy the following. It cannot be undone."
echo
printf '  Branch:  %s\n' "$BRANCH"
printf '  Project: %s\n' "$PROJECT"
echo
echo '  Containers:'
docker compose -f "$COMPOSE_FILE" -p "$PROJECT" ps --format '    {{.Name}} ({{.State}})' 2>/dev/null \
  || echo '    none running'
echo
echo '  Volumes, with every row of data in them:'
for volume in pgdata uploads redisdata rabbitmq_data; do
  name="${PROJECT}_${volume}"
  if docker volume inspect "$name" >/dev/null 2>&1; then
    printf '    %s\n' "$name"
  fi
done
echo
echo '  Frontend dev servers on these ports:'
FOUND_PIDS=""
for port in $PORTS; do
  pids=$(lsof -ti tcp:"$port" -sTCP:LISTEN 2>/dev/null || true)
  for pid in $pids; do
    is_docker_process "$pid" && continue
    printf '    port %s  pid %s  %s\n' "$port" "$pid" "$(ps -p "$pid" -o comm= 2>/dev/null || echo '?')"
    FOUND_PIDS="$FOUND_PIDS $pid"
  done
done
[ -z "$FOUND_PIDS" ] && echo '    none'
echo
echo '  Generated files: .env, apps/api/.env, apps/{web,admin,space,live}/.env, .plane-env.sh'
echo
red 'The uploads volume holds every file uploaded through this stack. Seeding'
red 'does not recreate those files. Copy anything you need before you continue.'
echo

if [ "${1:-}" != "--yes" ]; then
  printf 'Type the project name (%s) to confirm: ' "$PROJECT"
  read -r answer
  [ "$answer" = "$PROJECT" ] || die "aborted, nothing was destroyed"
fi

# ---------------------------------------------------------------- destroy

# Docker first. If this step fails, the run stops here and the frontend
# processes stay up, which is the recoverable order.
#
# Never pass --remove-orphans. Root AGENTS.md forbids it repo-wide, because
# docker-compose-local.yml and docker-compose-test.yml resolve to the same
# project name unless COMPOSE_PROJECT_NAME is set. The flag then treats the
# other file's containers as orphans of this project and removes them, so one
# teardown deletes a stack that nobody asked it to touch.
#
# `down -v` alone removes every container, volume, and network that this project
# declares, which is the whole target of this script.
bold "Removing containers, volumes, and the network"
docker compose -f "$COMPOSE_FILE" -p "$PROJECT" down -v

bold "Stopping the frontend dev servers"
for pid in $FOUND_PIDS; do
  is_docker_process "$pid" && continue
  kill "$pid" 2>/dev/null || true
done

bold "Removing generated files"
rm -f .env apps/api/.env apps/web/.env apps/admin/.env apps/space/.env apps/live/.env .plane-env.sh

echo
green "Teardown complete for $PROJECT"
echo 'Run the plane-env-create skill to build it again.'
