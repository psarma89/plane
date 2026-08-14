---
name: plane-env-create
description: Stand up a complete, isolated Plane stack for one branch or git worktree. Use when you start work on a new feature branch, when you need a second Plane stack that runs beside an existing one, or when a checkout has no .env files and no running containers. Allocates a free port block from the branch name, writes every .env file, boots Docker, creates an admin user, and seeds demo data. Pair it with plane-env-teardown.
user_invocable: true
---

# Create a Plane environment

One command takes a branch from nothing to a working sign-in page. Every branch
gets its own port block, its own Docker volumes, and its own login.

## Run it

From inside a Plane checkout, to set up the current branch:

```bash
.claude/skills/plane-env-create/scripts/env-create.sh
```

To create the worktree first, then set it up:

```bash
.claude/skills/plane-env-create/scripts/env-create.sh feat/gantt-drag
```

The script creates the worktree under `~/Development/worktrees/plane/`. Set
`PLANE_WORKTREE_ROOT` to use a different directory. If the branch does not
exist, the script branches from `origin/dev`.

The script takes 5 to 10 minutes on a cold Docker cache, and about 2 minutes on
a warm one.

## Port calculation

Nine ports, allocated as one block of ten.

```
base = 3200 + (cksum(branch_name) % 80) * 10        range 3200-3990

  base+0  web            base+5  postgres
  base+1  admin          base+6  valkey
  base+2  space          base+7  minio
  base+3  live           base+8  minio console
  base+4  api
```

The hash makes this deterministic: the same branch name always starts at the
same block, so a rerun keeps the ports it had and any URL you bookmarked still
works. If a port in that block is already bound, the script steps to the next
block and reports the move. The default block, 3200, never collides with the
stock ports 3000, 3001, 3002, 3100, 5432, 6379, 8000, 9000, and 9090.

## What it writes

| File                                                  | Contents                                                          |
| ----------------------------------------------------- | ----------------------------------------------------------------- |
| `.env`                                                | The eight `PLANE_HOST_*` ports and `COMPOSE_PROJECT_NAME`         |
| `apps/api/.env`                                       | `CORS_ALLOWED_ORIGINS`, the four base URLs, `AWS_S3_ENDPOINT_URL` |
| `apps/web/.env`, `apps/admin/.env`, `apps/space/.env` | The five `VITE_*_BASE_URL` values                                 |
| `apps/live/.env`                                      | `PORT`, `API_BASE_URL`, `WEB_BASE_URL`, `REDIS_PORT`, `REDIS_URL` |
| `.plane-env.sh`                                       | `export` lines for the same ports                                 |
| `graphify-out/`                                       | A copy of the knowledge graph from the main checkout              |

Every URL is written as a literal. These files load through dotenv, which does
not expand `${VAR}`.

`CORS_ALLOWED_ORIGINS` also feeds `CSRF_TRUSTED_ORIGINS`. If it does not match
the port that the browser uses, the stack starts and then every sign-in fails.

## The graphify graph

`graphify-out/` is gitignored, so `git worktree add` never brings it. Both
PreToolUse hooks in `.claude/settings.json` guard on
`[ -f graphify-out/graph.json ]`, and `.claude/settings.json` is tracked. A
fresh worktree therefore looks configured while the hooks do nothing, and
`graphify query` fails with `graph file not found`.

This skill copies the graph from the main checkout when the worktree has none.
The copy takes about 5 seconds and 42 MB.

Copy, do not symlink. `graphify update .`, `label`, and `export` all write into
this directory and take no lock, so two worktrees sharing one directory
interleave their writes into a graph that describes a mixture of branches. Reads
are safe either way, but the writes are not.

The copy carries the extraction cache, which is keyed on file content plus the
path relative to the scan root. The cache still hits in the new worktree, so the
first `graphify update .` pays only for the files that this branch changed.

Run `graphify update .` once the branch has commits, to match the graph to it.

## Sign in

```
URL:      http://localhost:<web port>
Email:    dev-<branch-slug>@plane.local
Password: plane-dev-local-2026
```

The email carries the branch slug, so you can tell which stack a browser tab
belongs to. The script prints all three values when it finishes.

## Start the frontends

The Docker stack runs the API, the workers, PostgreSQL, Valkey, and MinIO. The
four frontends run on the host.

```bash
source .plane-env.sh && pnpm build && pnpm dev
```

Source the file first. pnpm and Turbo do not read the root `.env`, and Turbo
runs in strict env mode, so the port variables reach the dev task only as
exports.

Run `pnpm build` before `pnpm dev`. On an empty `packages/propel/dist` the two
tasks race and fail with `EEXIST`.

## Traps

| Symptom                                                                                                                      | Cause                                                                                                    | Fix                                                                                                                                                                    |
| ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Sign-in fails with a CORS error                                                                                              | `CORS_ALLOWED_ORIGINS` does not list the web port                                                        | Rerun this skill. Do not hand-edit the port.                                                                                                                           |
| `pnpm dev` binds 3000 instead of the allocated port                                                                          | `.plane-env.sh` was not sourced                                                                          | `source .plane-env.sh`, then start again                                                                                                                               |
| `EEXIST` in `packages/propel/dist`                                                                                           | `pnpm dev` ran the propel build and dev tasks together                                                   | Run `pnpm build`, then `pnpm dev`                                                                                                                                      |
| The admin page shows only a spinner, console reports `504 Outdated Optimize Dep`                                             | Vite reoptimised dependencies during the first load                                                      | Reload the page                                                                                                                                                        |
| Seeding fails with `Sample larger than population`                                                                           | `module_count` is below 5                                                                                | Not reachable through this skill, which pins 5                                                                                                                         |
| The API logs `Waiting for database migrations to complete...` forever, and `docker ps -a` shows the migrator as `Exited (1)` | The four API containers raced to create `apps/api/plane/logs` and the losers died with `FileExistsError` | This skill creates the directory before it starts the stack. If you hit it by running `docker compose up` by hand, run `mkdir -p apps/api/plane/logs` and start again. |

## Related

- `plane-env-teardown` destroys what this skill creates.
- `docs/sops/local-development-setup-sop.md` covers the same ground by hand,
  including the one-time prerequisites.
