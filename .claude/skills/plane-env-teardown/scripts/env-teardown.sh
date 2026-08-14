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

# Docker Compose derives a default project name from the directory name by
# lower-casing it and dropping every character outside [a-z0-9_-]. A raw
# `basename` does not match that, so a checkout at ~/Development/Plane produced
# `Plane` while the real project was `plane`. `down -v` then matched nothing,
# exited 0, and this script reported success while every container survived.
normalize_project_name() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9_-]//g; s/^[^a-z0-9]+//'
}

PROJECT=$(read_var .env COMPOSE_PROJECT_NAME)
[ -n "$PROJECT" ] || PROJECT=$(normalize_project_name "$(basename "$PWD")")

# The backend test suite runs in its own project, named per branch so that two
# worktrees do not share one test database. Nothing else removes it, and this
# script deletes .plane-env.sh, which is the only file that records the name. So
# read it before that happens and tear it down too.
# .plane-env.sh writes `export KEY=value`, so read_var's `^KEY=` pattern misses it.
TEST_PROJECT=$(grep '^export PLANE_TEST_PROJECT_NAME=' .plane-env.sh 2>/dev/null \
  | head -1 | cut -d= -f2- | tr -d '"' || true)
if [ -z "$TEST_PROJECT" ] && [ -n "$PROJECT" ]; then
  TEST_PROJECT="plane-api-tests-${PROJECT#plane-}"
fi

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
# `docker compose ps` exits 0 when the project holds no container, so a `||`
# fallback never fires and the heading was followed by a blank line. On the one
# screen that stands between the user and an irreversible `down -v`, a blank line
# reads as a failed lookup rather than "there is nothing to remove".
list_containers() {
  docker compose -f "$COMPOSE_FILE" -p "$1" ps --format '    {{.Name}} ({{.State}})' 2>/dev/null || true
}

echo '  Containers:'
CONTAINER_LIST=$(list_containers "$PROJECT")
if [ -n "$CONTAINER_LIST" ]; then
  printf '%s\n' "$CONTAINER_LIST"
else
  echo '    none running'
fi
echo
echo "  Backend test project ($TEST_PROJECT):"
TEST_CONTAINER_LIST=$(list_containers "$TEST_PROJECT")
if [ -n "$TEST_CONTAINER_LIST" ]; then
  printf '%s\n' "$TEST_CONTAINER_LIST"
else
  echo '    none running'
fi
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

# The test project is a separate Compose project, so the call above does not
# reach it. Without this, every branch that ever ran the backend suite leaks one
# test project, and the name is gone as soon as .plane-env.sh is deleted below.
if [ -n "$TEST_PROJECT" ] && [ "$TEST_PROJECT" != "$PROJECT" ]; then
  bold "Removing the backend test project $TEST_PROJECT"
  docker compose -f docker-compose-test.yml -p "$TEST_PROJECT" down -v 2>/dev/null \
    || bold "  nothing to remove for $TEST_PROJECT"
fi

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
