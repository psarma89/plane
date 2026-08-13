#!/bin/bash

# Plane Local Reset Script
# Drops every container volume, restores the seeded snapshot, and restarts the stack.
# The snapshot comes from the local development setup SOP:
# docs/sops/local-development-setup-sop.md

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

COMPOSE=(docker compose -f docker-compose-local.yml)
SNAPSHOT="tmp/seed.sql"

cd "$(dirname "$0")"

if [ ! -f "$SNAPSHOT" ]; then
    echo -e "${RED}Error: $SNAPSHOT does not exist.${NC}"
    echo -e "Create it first. Read the Snapshot section of docs/sops/local-development-setup-sop.md."
    exit 1
fi

echo -e "${BOLD}${YELLOW}Removing containers and volumes...${NC}"
"${COMPOSE[@]}" down -v --remove-orphans

echo -e "${BOLD}${YELLOW}Starting the data services...${NC}"
"${COMPOSE[@]}" up -d plane-db plane-redis plane-mq plane-minio

echo -e "${BOLD}${YELLOW}Waiting for PostgreSQL...${NC}"
until "${COMPOSE[@]}" exec -T plane-db pg_isready -U plane -d plane > /dev/null 2>&1; do
    sleep 1
done

echo -e "${BOLD}${YELLOW}Restoring $SNAPSHOT...${NC}"
"${COMPOSE[@]}" exec -T plane-db psql -q -v ON_ERROR_STOP=1 -U plane -d plane < "$SNAPSHOT"

echo -e "${BOLD}${YELLOW}Starting the API, the workers, and the migrator...${NC}"
"${COMPOSE[@]}" up -d

echo -e "${BOLD}${YELLOW}Waiting for the API...${NC}"
until curl -sf -o /dev/null http://localhost:8000/api/instances/; do
    sleep 2
done

echo -e "\n${GREEN}✓${NC} Reset complete. The API answers on http://localhost:8000."
echo -e "The frontends run outside Docker. If ${BOLD}pnpm dev${NC} is not running, start it."
