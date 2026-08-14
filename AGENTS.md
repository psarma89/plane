# Agent Development Guide

Plane is a pnpm and Turbo monorepo. `apps/` holds the deployables. `packages/` holds the shared libraries.

## Gotchas

- Dev servers bind fixed ports. `web` takes 3000 and `admin` takes 3001. Storybook takes 6006 through `pnpm --filter=@plane/ui storybook`.
- Internal dependencies use `workspace:*`. External dependencies use `catalog:`. Neither one takes a version range.
- Per-app MobX stores live in `apps/web/core/store/`, `apps/admin/store/`, and `apps/space/store/`. `packages/shared-state` holds only the shared filter stores. `apps/web` takes one store from that package: `WorkItemFilterStore`.
- Build every shared component in `@plane/ui` with a Storybook story. Do not add one straight to an app.
- Components and hooks never import a service. Only `core/store/` imports one. A component reads state through a hook in `core/hooks/store/`. `no-restricted-imports` in `.oxlintrc.json` enforces this, and the pre-commit hook blocks the commit.

## Scoped conventions

- `apps/api/AGENTS.md` and `apps/web/AGENTS.md` hold the per-app rules and traps.
- `CONTEXT.md` maps the product names to the code names. Read it before you name anything.
- `docs/architecture/plane-patterns-census.md` holds every measured pattern count. `bin/check-agents-md` verifies every reference in the instruction files, and `bin/check-counts` verifies every count.

## Instruction files

The two files below hold the shell and TypeScript conventions. They carry Copilot `applyTo:` frontmatter, which only Copilot reads. The imports load them for every other agent.

@.github/instructions/bash.instructions.md
@.github/instructions/typescript.instructions.md

If your tool does not resolve `@` imports, open both paths directly. `bash.instructions.md` holds the pnpm, Turbo, and Docker conventions. `typescript.instructions.md` holds the TypeScript 5.0 to 5.8 patterns and the deprecated syntax to avoid.

## Backgrounds

Before you write any `bg-*`, `text-*`, or `border-*` class, use the `plane-backgrounds` skill. It carries the Canvas, Surface, and Layer rules that every app in `apps/` follows.

## Backend tests run in Docker

The `apps/api` pytest suite needs the stack in `docker-compose-test.yml` at the repo root. It does not run against a local Python environment.

Run `./setup.sh` once first. It generates `apps/api/.env` from `.env.example`.

Export `COMPOSE_PROJECT_NAME` before any test command, and never pass `--remove-orphans`. Both compose files resolve to the same project name, so one call against the test file deletes every container of the development stack.

For the commands, use the `plane-test-api` skill or read [`docs/sops/run-backend-tests-sop.md`](docs/sops/run-backend-tests-sop.md). For fixtures and conventions, read `apps/api/plane/tests/TESTING_GUIDE.md`.

## Documentation

Before you add or change any page under `docs/`, read `docs/INDEX.md` for the map and `docs/AGENTS.md` for the conventions. Each subdirectory under `docs/` carries its own `AGENTS.md` with narrower rules for that section.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:

- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
