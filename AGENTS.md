# Agent Development Guide

Plane is a pnpm and Turbo monorepo. `apps/` holds the deployables. `packages/` holds the shared libraries.

## Gotchas

- Dev servers bind fixed ports. `web` takes 3000 and `admin` takes 3001. Storybook takes 6006 through `pnpm --filter=@plane/ui storybook`.
- Internal dependencies use `workspace:*`. External dependencies use `catalog:`. Neither one takes a version range.
- Per-app MobX stores live in `apps/web/core/store/`, `apps/admin/store/`, and `apps/space/store/`. `packages/shared-state` holds only the shared filter stores. `apps/web` takes one store from that package: `WorkItemFilterStore`.
- Build every shared component in `@plane/ui` with a Storybook story. Do not add one straight to an app.
- The files in `.github/instructions/` use Copilot `applyTo:` frontmatter. Claude Code does not read that frontmatter, so nothing in there loads on its own. Read `bash.instructions.md` for pnpm, Turbo, and Docker conventions. Read `typescript.instructions.md` for the TypeScript 5.0 to 5.8 patterns and the deprecated syntax to avoid.

## Backgrounds

Before you write any `bg-*`, `text-*`, or `border-*` class, use the `plane-backgrounds` skill. It carries the Canvas, Surface, and Layer rules that every app in `apps/` follows.

## Backend tests run in Docker

The `apps/api` pytest suite needs the stack in `docker-compose-test.yml` at the repo root. It does not run against a local Python environment.

Run `./setup.sh` once first. It generates `apps/api/.env` from `.env.example`.

For the commands, read `apps/api/tests/RUNNING_TESTS.md`. For fixtures and conventions, read `apps/api/tests/TESTING_GUIDE.md`.

## Documentation

Before you add or change any page under `docs/`, read `docs/INDEX.md` for the map and `docs/AGENTS.md` for the conventions. Each subdirectory under `docs/` carries its own `AGENTS.md` with narrower rules for that section.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:

- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
