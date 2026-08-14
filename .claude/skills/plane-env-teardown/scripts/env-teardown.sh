#!/usr/bin/env bash
# Destroy the Plane stack for this checkout, including every volume and all data.
#
# Why this exists:
#   A stack left running holds nine ports and four volumes. A worktree deleted
#   with its stack still up leaks all of them, and the next branch that hashes to
#   the same port block then steps elsewhere for no visible reason.
#
# Usage:
#   env-teardown.sh          # list the targets, then ask for the project name
#   env-teardown.sh --yes    # unattended
#
# This is destructive and cannot be undone.
set -euo pipefail

COMPOSE_FILE="docker-compose-local.yml"
TEST_COMPOSE_FILE="docker-compose-test.yml"

red() { printf '\033[0;31m%s\033[0m\n' "$1"; }
green() { printf '\033[0;32m%s\033[0m\n' "$1"; }
bold() { printf '\033[1m%s\033[0m\n' "$1"; }
die() { red "Error: $1" >&2; exit 1; }

[ -f "$COMPOSE_FILE" ] || die "run this from a Plane checkout root ($COMPOSE_FILE not found)"

REPO_ROOT="$PWD"
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)

read_var() { grep "^$2=" "$1" 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' || true; }

slugify() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' \
    | sed 's#[^a-z0-9]#-#g; s#--*#-#g; s#^-##; s#-$##'
}

# Docker Compose derives a default project name from the directory by lower-casing
# it and dropping every character outside [a-z0-9_-].
normalize_project_name() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9_-]//g; s/^[^a-z0-9]+//'
}

# A project is real when it still has a container, or when its database volume
# survives. Either one is enough to act on.
project_exists() {
  local p="$1"
  [ -n "$(docker compose -f "$COMPOSE_FILE" -p "$p" ps -aq 2>/dev/null || true)" ] && return 0
  docker volume inspect "${p}_pgdata" >/dev/null 2>&1 && return 0
  return 1
}

# ---------------------------------------------------------------- the project

# .env is authoritative. When it is gone, guess in the order that can actually be
# right, and verify the guess before destroying anything.
#
# A normalized directory name is NOT a sufficient fallback on its own.
# plane-env-create names the worktree directory after the slug and names the
# project `plane-<slug>`, so the directory name is always short by the `plane-`
# prefix and never matches a project this tooling built.
PROJECT=$(read_var .env COMPOSE_PROJECT_NAME)

if [ -z "$PROJECT" ] && [ "$BRANCH" != "unknown" ] && [ "$BRANCH" != "HEAD" ]; then
  candidate="plane-$(slugify "$BRANCH")"
  project_exists "$candidate" && PROJECT="$candidate"
fi

if [ -z "$PROJECT" ]; then
  candidate=$(normalize_project_name "$(basename "$REPO_ROOT")")
  [ -n "$candidate" ] && project_exists "$candidate" && PROJECT="$candidate"
fi

[ -n "$PROJECT" ] || die "could not determine which Compose project belongs to this
checkout, and refusing to guess. .env is absent or carries no COMPOSE_PROJECT_NAME,
and neither \"plane-$(slugify "$BRANCH")\" nor the directory name matches a project
that has containers or a pgdata volume.

List the projects, then set the name by hand:

  docker compose ls
  COMPOSE_PROJECT_NAME=<name> $0"

# Destroying nothing while reporting success is the failure this guards. `down -v`
# on a project that does not exist exits 0 and prints nothing.
project_exists "$PROJECT" || die "project \"$PROJECT\" has no container and no
${PROJECT}_pgdata volume, so there is nothing here to destroy. Refusing to delete
the .env files, because that would remove the only record of the real name."

# The backend test suite runs in its own project. Read the name only from
# .plane-env.sh, which is where plane-env-create records it. Do not derive it: a
# branch called `api/tests/foo` derives `plane-api-tests-foo`, which is the same
# name a `foo` worktree would use for its own DEVELOPMENT project.
TEST_PROJECT=$(grep '^export PLANE_TEST_PROJECT_NAME=' .plane-env.sh 2>/dev/null \
  | head -1 | cut -d= -f2- | tr -d '"' || true)

# ---------------------------------------------------------------- report

# `docker compose ps` exits 0 when a project holds no container, so an empty
# result and a failed lookup look identical. On the last screen before an
# irreversible `down -v`, "none running" must mean it, so keep the status.
list_containers() {
  local out
  # The assignment sits in an `if` condition on purpose. Written as a bare
  # assignment followed by `status=$?`, `set -e` aborts the whole script on a
  # failed lookup before the status is ever read.
  if ! out=$(docker compose -f "$COMPOSE_FILE" -p "$1" ps --format '    {{.Name}} ({{.State}})' 2>&1); then
    printf '    lookup FAILED, so this list is not trustworthy:\n    %s\n' "$out"
    return 0
  fi
  if [ -n "$out" ]; then printf '%s\n' "$out"; else echo '    none running'; fi
}

# Signal a frontend dev server only when it runs from THIS checkout.
#
# The port list comes from .env, and .env.example ships 3000, 3001, 3002, and
# 3100. In a checkout bootstrapped by plain ./setup.sh those are the MAIN
# checkout's dev-server ports, so --yes would kill them with no prompt.
# is_docker_process cannot catch that, because the local compose file publishes
# only the redis, minio, db, and api ports and never holds these four.
pid_cwd() {
  lsof -a -p "$1" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | head -1
}

is_docker_process() {
  case "$(ps -p "$1" -o comm= 2>/dev/null)" in
    *docker*|*Docker*) return 0 ;;
    *) return 1 ;;
  esac
}

frontend_ports() {
  local key value
  for key in PLANE_HOST_WEB_PORT PLANE_HOST_ADMIN_PORT PLANE_HOST_SPACE_PORT; do
    value=$(read_var .env "$key")
    [ -n "$value" ] && printf '%s\n' "$value"
  done
  value=$(read_var apps/live/.env PORT)
  [ -n "$value" ] && printf '%s\n' "$value"
  return 0
}

# ours_pids -- PIDs listening on this checkout's frontend ports, whose working
# directory is this checkout, and which are not Docker.
ours_pids() {
  local port pid cwd
  for port in $(frontend_ports); do
    for pid in $(lsof -ti tcp:"$port" -sTCP:LISTEN 2>/dev/null || true); do
      is_docker_process "$pid" && continue
      cwd=$(pid_cwd "$pid")
      case "$cwd" in
        "$REPO_ROOT"|"$REPO_ROOT"/*) printf '%s %s\n' "$port" "$pid" ;;
      esac
    done
  done
  return 0
}

bold "This will destroy the following. It cannot be undone."
echo
printf '  Branch:  %s\n' "$BRANCH"
printf '  Project: %s\n' "$PROJECT"
echo
echo '  Containers:'
list_containers "$PROJECT"
echo
if [ -n "$TEST_PROJECT" ]; then
  printf '  Backend test project (%s):\n' "$TEST_PROJECT"
  list_containers "$TEST_PROJECT"
else
  echo '  Backend test project: no .plane-env.sh, so none is recorded and none is touched'
fi
echo
echo '  Volumes, with every row of data in them:'
for volume in pgdata uploads redisdata rabbitmq_data; do
  name="${PROJECT}_${volume}"
  docker volume inspect "$name" >/dev/null 2>&1 && printf '    %s\n' "$name"
done
echo
echo '  Frontend dev servers of THIS checkout:'
FOUND=$(ours_pids)
if [ -n "$FOUND" ]; then
  printf '%s\n' "$FOUND" | while read -r port pid; do
    printf '    port %s  pid %s  %s\n' "$port" "$pid" "$(ps -p "$pid" -o comm= 2>/dev/null || echo '?')"
  done
else
  echo '    none'
fi
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

# Docker first. If this step fails, the run stops here and the frontend processes
# stay up, which is the recoverable order.
#
# Never pass --remove-orphans. Root AGENTS.md forbids it repo-wide, because both
# compose files resolve to the same project name when COMPOSE_PROJECT_NAME is
# unset. The flag then reads the other file's containers as orphans of this
# project and removes them. `down -v` alone removes everything this project
# declares.
bold "Removing containers, volumes, and the network"
docker compose -f "$COMPOSE_FILE" -p "$PROJECT" down -v \
  || die "docker compose down failed. The dev servers are still up, so nothing else was touched."

if [ -n "$TEST_PROJECT" ] && [ "$TEST_PROJECT" != "$PROJECT" ]; then
  bold "Removing the backend test project $TEST_PROJECT"
  # Report a real failure. Masking it here and then deleting .plane-env.sh below
  # leaks the project permanently, because that file holds the only record of the
  # name.
  if ! test_out=$(docker compose -f "$TEST_COMPOSE_FILE" -p "$TEST_PROJECT" down -v 2>&1); then
    red "  could not remove $TEST_PROJECT, so it is left in place:"
    printf '  %s\n' "$test_out"
    die "stopping before the generated files are deleted, so that $TEST_PROJECT keeps a record of its name"
  fi
fi

# Re-scan after the confirmation. The earlier list was taken before a `read` that
# blocks for as long as the user takes, and a PID can exit and be reused in that
# window. A dead PID also reads as "not docker", because empty ps output falls
# through the case.
bold "Stopping the frontend dev servers of this checkout"
ours_pids | while read -r port pid; do
  if kill "$pid" 2>/dev/null; then
    printf '  stopped pid %s on port %s\n' "$pid" "$port"
  else
    printf '  pid %s on port %s was already gone\n' "$pid" "$port"
  fi
done

bold "Removing generated files"
rm -f .env apps/api/.env apps/web/.env apps/admin/.env apps/space/.env apps/live/.env .plane-env.sh

echo
green "Teardown complete for $PROJECT"
echo
echo 'graphify-out/ was left in place. It is a copy of the knowledge graph, not'
echo 'stack state, and rebuilding it costs more than keeping it.'
echo
echo 'Run the plane-env-create skill to build it again, or remove the worktree:'
echo
printf '  git worktree remove %s\n' "$REPO_ROOT"
echo
