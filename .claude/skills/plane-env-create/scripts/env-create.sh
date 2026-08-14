#!/usr/bin/env bash
# Stand up an isolated Plane stack for one branch or worktree.
# Usage: env-create.sh [branch-name]
#   With a branch name, create the worktree first, then set it up.
#   With no argument, set up the current checkout.
set -euo pipefail

WORKTREE_ROOT="${PLANE_WORKTREE_ROOT:-$HOME/Development/worktrees/plane}"
COMPOSE_FILE="docker-compose-local.yml"
PASSWORD="plane-dev-local-2026"
BLOCK_COUNT=80
BLOCK_START=3200

red() { printf '\033[0;31m%s\033[0m\n' "$1"; }
green() { printf '\033[0;32m%s\033[0m\n' "$1"; }
bold() { printf '\033[1m%s\033[0m\n' "$1"; }
die() { red "Error: $1" >&2; exit 1; }

slugify() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' \
    | sed 's#[^a-z0-9]#-#g; s#--*#-#g; s#^-##; s#-$##'
}

# Deterministic: the same branch name always starts at the same block.
base_for_branch() {
  local h
  h=$(printf '%s' "$1" | cksum | cut -d' ' -f1)
  printf '%s' $(( BLOCK_START + (h % BLOCK_COUNT) * 10 ))
}

# One lsof for the whole machine, not one per candidate port. Probing 80 blocks
# of 9 ports each forks 720 processes, and every fork widens the window between
# the last probe and the bind in `docker compose up`.
LISTENING_PORTS=""
snapshot_listening_ports() {
  LISTENING_PORTS=$(lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null \
    | awk 'NR > 1 { n = split($9, parts, ":"); print parts[n] }' \
    | sort -u)
}

port_is_listening() {
  printf '%s\n' "$LISTENING_PORTS" | grep -qx "$1"
}

block_is_free() {
  local base=$1 i
  for i in 0 1 2 3 4 5 6 7 8; do
    if port_is_listening $(( base + i )); then
      return 1
    fi
  done
  return 0
}

# Start at the hashed block. If it is taken, step forward until one is free.
allocate_base() {
  local branch=$1 start base i
  start=$(base_for_branch "$branch")
  for i in $(seq 0 $(( BLOCK_COUNT - 1 ))); do
    base=$(( BLOCK_START + (( (start - BLOCK_START) / 10 + i ) % BLOCK_COUNT) * 10 ))
    if block_is_free "$base"; then
      printf '%s' "$base"
      return 0
    fi
  done
  die "no free port block in ${BLOCK_START}-$(( BLOCK_START + BLOCK_COUNT * 10 - 1 ))"
}

# Replace KEY=... in place, or append it when the key is absent.
set_var() {
  local file=$1 key=$2 value=$3
  if grep -q "^${key}=" "$file" 2>/dev/null; then
    awk -v k="$key" -v v="$value" \
      '{ if (index($0, k "=") == 1) print k "=" v; else print }' \
      "$file" > "$file.tmp" && mv "$file.tmp" "$file"
  else
    printf '%s=%s\n' "$key" "$value" >> "$file"
  fi
}

# ---------------------------------------------------------------- worktree

BRANCH_ARG="${1:-}"

if [ -n "$BRANCH_ARG" ]; then
  SLUG=$(slugify "$BRANCH_ARG")
  TARGET="$WORKTREE_ROOT/$SLUG"
  if [ -d "$TARGET" ]; then
    bold "Worktree already exists at $TARGET"
  else
    git rev-parse --git-dir >/dev/null 2>&1 || die "not inside a git repository"
    mkdir -p "$WORKTREE_ROOT"
    git fetch origin dev --quiet
    if git show-ref --verify --quiet "refs/heads/$BRANCH_ARG"; then
      git worktree add "$TARGET" "$BRANCH_ARG"
    else
      git worktree add "$TARGET" -b "$BRANCH_ARG" origin/dev
    fi
    green "Created worktree $TARGET"
  fi
  cd "$TARGET"
fi

[ -f "$COMPOSE_FILE" ] || die "run this from a Plane checkout root ($COMPOSE_FILE not found)"

BRANCH=$(git rev-parse --abbrev-ref HEAD)
SLUG=$(slugify "$BRANCH")
PROJECT="plane-$SLUG"
# A hyphen, not a plus. In form-encoded bodies a plus decodes to a space, which
# breaks the email in curl calls and in any tool that does not encode it.
EMAIL="dev-$SLUG@plane.local"

# Workspace.slug is a SlugField(max_length=48) in plane/db/models/workspace.py, so
# a long branch name overflows the column. Untruncated, create() raises DataError
# after the stack is already built and the failure looks unrelated to the branch.
WS_SLUG=$(printf '%s' "$SLUG" | cut -c1-48 | sed -E 's/-$//')

# ---------------------------------------------------------------- graphify

# graphify-out/ is gitignored, so `git worktree add` never brings it along. The
# two PreToolUse hooks in .claude/settings.json both guard on
# `[ -f graphify-out/graph.json ]`. That file is tracked, so a fresh worktree
# looks configured while the hooks silently do nothing. Copy the graph so the
# guard passes.
#
# Copy, do not symlink. `graphify update .`, `label`, and `export` all write
# into this directory and take no lock. Two worktrees sharing one directory
# interleave their writes into a graph that describes a mixture of branches.
# The copy also carries the extraction cache, which is keyed on file content
# plus the path relative to the scan root, so it still hits here.
MAIN_CHECKOUT=$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")
if [ ! -f graphify-out/graph.json ] && [ -f "$MAIN_CHECKOUT/graphify-out/graph.json" ]; then
  bold "Copying the graphify graph from $MAIN_CHECKOUT"
  cp -r "$MAIN_CHECKOUT/graphify-out" ./graphify-out
  green "Copied $(du -sh graphify-out | cut -f1). Run 'graphify update .' to match this branch."
fi

# ---------------------------------------------------------------- ports

HASHED=$(base_for_branch "$BRANCH")

# A rerun must keep the ports it already has. The skill tells you to rerun after
# a CORS failure, and a bookmarked URL depends on the block not moving.
#
# A free-port probe cannot decide this on its own. Once this branch's stack is
# up, Docker publishes its own api, postgres, valkey, and minio ports, so the
# probe sees the block as taken and steps to the next one. The stack is then
# rebuilt on new ports, the running `pnpm dev` talks to a dead API, and every
# rerun drifts again.
#
# So trust the recorded value over the probe, but only when .env belongs to this
# same project. A .env left behind by a different branch is not authoritative.
RECORDED_BASE=""
if [ -f .env ]; then
  recorded_project=$(grep -E '^COMPOSE_PROJECT_NAME=' .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' || true)
  recorded_web=$(grep -E '^PLANE_HOST_WEB_PORT=' .env 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"' || true)
  if [ "$recorded_project" = "$PROJECT" ] && [ -n "$recorded_web" ]; then
    RECORDED_BASE="$recorded_web"
  fi
fi

if [ -n "$RECORDED_BASE" ]; then
  BASE="$RECORDED_BASE"
else
  snapshot_listening_ports
  BASE=$(allocate_base "$BRANCH")
fi

WEB_PORT=$(( BASE + 0 ))
ADMIN_PORT=$(( BASE + 1 ))
SPACE_PORT=$(( BASE + 2 ))
LIVE_PORT=$(( BASE + 3 ))
API_PORT=$(( BASE + 4 ))
DB_PORT=$(( BASE + 5 ))
REDIS_PORT=$(( BASE + 6 ))
MINIO_PORT=$(( BASE + 7 ))
MINIO_CONSOLE_PORT=$(( BASE + 8 ))

bold "Branch:  $BRANCH"
bold "Project: $PROJECT"
if [ -n "$RECORDED_BASE" ]; then
  bold "Ports:   $BASE-$(( BASE + 8 ))  (reused, already recorded in .env)"
elif [ "$BASE" != "$HASHED" ]; then
  bold "Ports:   $BASE-$(( BASE + 8 ))  (hashed block $HASHED was taken)"
else
  bold "Ports:   $BASE-$(( BASE + 8 ))"
fi
echo

# ---------------------------------------------------------------- env files

if [ ! -f .env ] || [ ! -f apps/api/.env ]; then
  bold "Running setup.sh"
  ./setup.sh
fi

WEB_URL="http://localhost:$WEB_PORT"
ADMIN_URL="http://localhost:$ADMIN_PORT"
SPACE_URL="http://localhost:$SPACE_PORT"
LIVE_URL="http://localhost:$LIVE_PORT"
API_URL="http://localhost:$API_PORT"

bold "Writing port values into the .env files"

set_var .env PLANE_HOST_WEB_PORT "$WEB_PORT"
set_var .env PLANE_HOST_ADMIN_PORT "$ADMIN_PORT"
set_var .env PLANE_HOST_SPACE_PORT "$SPACE_PORT"
set_var .env PLANE_HOST_API_PORT "$API_PORT"
set_var .env PLANE_HOST_DB_PORT "$DB_PORT"
set_var .env PLANE_HOST_REDIS_PORT "$REDIS_PORT"
set_var .env PLANE_HOST_MINIO_PORT "$MINIO_PORT"
set_var .env PLANE_HOST_MINIO_CONSOLE_PORT "$MINIO_CONSOLE_PORT"
set_var .env COMPOSE_PROJECT_NAME "$PROJECT"

# The API sends these URLs to the browser. dotenv does not expand ${VAR}, so
# every one of them must hold a literal port.
set_var apps/api/.env CORS_ALLOWED_ORIGINS \
  "\"$WEB_URL,$ADMIN_URL,$SPACE_URL,$LIVE_URL\""
set_var apps/api/.env APP_BASE_URL "\"$WEB_URL\""
set_var apps/api/.env ADMIN_BASE_URL "\"$ADMIN_URL\""
set_var apps/api/.env SPACE_BASE_URL "\"$SPACE_URL\""
set_var apps/api/.env LIVE_BASE_URL "\"$LIVE_URL\""
set_var apps/api/.env AWS_S3_ENDPOINT_URL "\"http://localhost:$MINIO_PORT\""

for app in web admin space; do
  set_var "apps/$app/.env" VITE_API_BASE_URL "\"$API_URL\""
  set_var "apps/$app/.env" VITE_WEB_BASE_URL "\"$WEB_URL\""
  set_var "apps/$app/.env" VITE_ADMIN_BASE_URL "\"$ADMIN_URL\""
  set_var "apps/$app/.env" VITE_SPACE_BASE_URL "\"$SPACE_URL\""
  set_var "apps/$app/.env" VITE_LIVE_BASE_URL "\"$LIVE_URL\""
done

set_var apps/live/.env PORT "$LIVE_PORT"
set_var apps/live/.env API_BASE_URL "\"$API_URL\""
set_var apps/live/.env WEB_BASE_URL "\"$WEB_URL\""
set_var apps/live/.env LIVE_BASE_URL "\"$LIVE_URL\""
set_var apps/live/.env REDIS_PORT "$REDIS_PORT"
set_var apps/live/.env REDIS_URL "\"redis://localhost:$REDIS_PORT/\""

# pnpm and Turbo do not read the root .env, so the frontend ports need an
# export. Source this file before pnpm dev.
cat > .plane-env.sh <<EOF
# Generated by plane-env-create for branch $BRANCH. Do not commit.
#
# COMPOSE_PROJECT_NAME below names the DEVELOPMENT stack. The backend test stack
# must never share it. Both compose files resolve to one project when the
# variable is unset, so a test teardown then removes the development stack.
# A fixed test name is not enough either, because two worktrees would then share
# one test project and run two suites against one database.
#
# Before any backend test command, override it:
#
#   export COMPOSE_PROJECT_NAME="\$PLANE_TEST_PROJECT_NAME"
#
export COMPOSE_PROJECT_NAME=$PROJECT
export PLANE_TEST_PROJECT_NAME=plane-api-tests-$SLUG
export PLANE_HOST_WEB_PORT=$WEB_PORT
export PLANE_HOST_ADMIN_PORT=$ADMIN_PORT
export PLANE_HOST_SPACE_PORT=$SPACE_PORT
export PLANE_HOST_API_PORT=$API_PORT
export PLANE_HOST_DB_PORT=$DB_PORT
export PLANE_HOST_REDIS_PORT=$REDIS_PORT
export PLANE_HOST_MINIO_PORT=$MINIO_PORT
export PLANE_HOST_MINIO_CONSOLE_PORT=$MINIO_CONSOLE_PORT
EOF

green "Wrote .env, apps/api/.env, apps/{web,admin,space,live}/.env, .plane-env.sh"
echo

# ---------------------------------------------------------------- stack

# Confirm the compose file honours the port variables before anything starts.
# A checkout from before the port parameterization binds the literal ports, and
# the stack would then come up on the wrong ones and fail much later.
bold "Checking that the compose file honours the port variables"

# Two separate failures, two separate messages. Swallowing stderr here reported
# every docker fault as "this checkout predates the port parameterization", and
# the advice for that fault is to rebase, which cannot start a stopped daemon and
# loses work if followed.
if ! COMPOSE_CONFIG=$(docker compose -f "$COMPOSE_FILE" -p "$PROJECT" config 2>&1); then
  die "\`docker compose config\` failed, so nothing was started.

Docker is not running, or $COMPOSE_FILE cannot be parsed. Docker reported:

$COMPOSE_CONFIG"
fi

if ! printf '%s' "$COMPOSE_CONFIG" | grep -q "published: \"\?$API_PORT"; then
  die "$COMPOSE_FILE does not bind the API to port $API_PORT.
This checkout predates the host port parameterization, so it binds the fixed
ports and cannot run beside another stack. Rebase this branch onto a commit
that has \${PLANE_HOST_API_PORT} in $COMPOSE_FILE."
fi

# The api, worker, beat-worker, and migrator containers all bind-mount
# ./apps/api and all run `if not exists: makedirs(LOG_DIR)` when Django settings
# import (apps/api/plane/settings/local.py:37). logs/ is gitignored, so on a
# fresh worktree all four see it missing, all four call makedirs, and the losers
# die with FileExistsError. A dead migrator leaves the API waiting for
# migrations that never arrive. Creating the directory first removes the race.
mkdir -p apps/api/plane/logs

bold "Starting the Docker stack"
docker compose -f "$COMPOSE_FILE" -p "$PROJECT" up -d --build

bold "Waiting for the API on port $API_PORT"
for i in $(seq 1 60); do
  if curl -sf -o /dev/null "$API_URL/api/instances/"; then
    green "API is up"
    break
  fi
  [ "$i" = 60 ] && die "the API did not answer on $API_URL within 3 minutes"
  sleep 3
done

# ---------------------------------------------------------------- admin

# Every value reaches Django through the environment, never through string
# interpolation. The Python below is single quoted, so the shell expands nothing
# inside it.
#
# $BRANCH in particular arrives unfiltered. Git permits a single quote in a ref
# name, so a branch called `fix/dont-crash` interpolated into a Python string
# literal is a syntax error at best and arbitrary code execution at worst. Only
# $SLUG passes through slugify(), which strips to [a-z0-9-].
dc_exec() {
  docker compose -f "$COMPOSE_FILE" -p "$PROJECT" exec -T \
    -e PLANE_ADMIN_EMAIL="$EMAIL" \
    -e PLANE_ADMIN_PASSWORD="$PASSWORD" \
    -e PLANE_WS_SLUG="$WS_SLUG" \
    -e PLANE_WS_NAME="$BRANCH" \
    api "$@"
}

bold "Creating the instance admin"
# register_instance already ran in the API entrypoint. This creates the first
# user, makes it an instance admin, and flips is_setup_done. It is idempotent.
dc_exec python manage.py shell -c '
import os, uuid
from django.contrib.auth.hashers import make_password
from plane.db.models import User, Profile
from plane.license.models import Instance, InstanceAdmin

email = os.environ["PLANE_ADMIN_EMAIL"]
password = os.environ["PLANE_ADMIN_PASSWORD"]

user, created = User.objects.get_or_create(
    email=email,
    defaults=dict(username=uuid.uuid4().hex, first_name="Plane", last_name="Dev",
                  password=make_password(password), is_password_autoset=False,
                  is_active=True))
Profile.objects.get_or_create(user=user)

instance = Instance.objects.first()
if instance is None:
    raise SystemExit("no Instance row: register_instance did not run")

# role goes in defaults, not in the lookup. InstanceAdmin declares
# unique_together on (instance, user), so a role in the lookup misses an existing
# row that carries a different role and then trips the constraint on insert.
InstanceAdmin.objects.get_or_create(user=user, instance=instance, defaults={"role": 20})

instance.is_setup_done = True
instance.is_telemetry_enabled = False
instance.save()
print("admin ready, created" if created else "admin ready, already existed")
'

# ---------------------------------------------------------------- seed

bold "Seeding demo data"
# create_dummy_data reads every value from input() and swallows its own errors,
# so call the underlying function directly. module_count must be at least 5:
# the task samples random.randint(0, 5) modules and raises below that.
dc_exec python manage.py shell -c '
import os
from plane.db.models import User, Workspace, WorkspaceMember
from plane.bgtasks.dummy_data_task import create_dummy_data

email = os.environ["PLANE_ADMIN_EMAIL"]
slug = os.environ["PLANE_WS_SLUG"]
name = os.environ["PLANE_WS_NAME"]

user = User.objects.get(email=email)
if Workspace.objects.filter(slug=slug).exists():
    print("workspace {} already exists, skipping seed".format(slug))
else:
    workspace = Workspace.objects.create(slug=slug, name=name, owner=user)
    WorkspaceMember.objects.create(workspace=workspace, role=20, member=user)
    for _ in range(2):
        create_dummy_data(slug=slug, email=user.email, members=[],
                          issue_count=20, cycle_count=2, module_count=5,
                          pages_count=4, intake_issue_count=2)
    print("seeded 2 projects into workspace {}".format(slug))
'

# ---------------------------------------------------------------- report

echo
green "Environment ready for $BRANCH"
echo
bold "Sign in"
printf '  URL:      %s\n' "$WEB_URL"
printf '  Email:    %s\n' "$EMAIL"
printf '  Password: %s\n' "$PASSWORD"
echo
bold "Ports"
printf '  web %s   admin %s   space %s   live %s   api %s\n' \
  "$WEB_PORT" "$ADMIN_PORT" "$SPACE_PORT" "$LIVE_PORT" "$API_PORT"
printf '  postgres %s   valkey %s   minio %s   minio console %s\n' \
  "$DB_PORT" "$REDIS_PORT" "$MINIO_PORT" "$MINIO_CONSOLE_PORT"
echo
bold "Start the frontends"
echo '  source .plane-env.sh && pnpm build && pnpm dev'
echo
echo 'Run pnpm build before pnpm dev. On an empty packages/propel/dist the'
echo 'build and dev tasks race and fail with EEXIST.'
