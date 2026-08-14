---
name: plane-env-teardown
description: Destroy the Plane stack for the current checkout, including every volume and all of its data. Use when you finish work on a branch, when a stack is in a state that is not worth debugging, or before you delete a worktree. Removes containers, named volumes, host dev servers, and the generated .env files. This is destructive and cannot be undone. Pair it with plane-env-create.
user_invocable: true
---

# Tear down a Plane environment

Removes everything that `plane-env-create` made, and every row of data that the
stack collected since.

## Run it

```bash
.claude/skills/plane-env-teardown/scripts/env-teardown.sh
```

The script lists what it will destroy, then asks you to type the project name.
Any other answer aborts and destroys nothing.

For unattended use:

```bash
.claude/skills/plane-env-teardown/scripts/env-teardown.sh --yes
```

## What it destroys

| Order | Target | Command |
| --- | --- | --- |
| 1 | Containers, volumes, network | `docker compose -f docker-compose-local.yml -p {project} down -v` |
| 2 | The backend test project | `docker compose -f docker-compose-test.yml -p {test-project} down -v` |
| 3 | Frontend dev servers | `kill` on the PID that holds the web, admin, space, or live port |
| 4 | Generated files | `.env`, `apps/api/.env`, `apps/{web,admin,space,live}/.env`, `.plane-env.sh` |

The backend test suite runs in its own Compose project, named per branch, so step
1 does not reach it. Step 2 exists because nothing else removes it, and because
step 4 deletes `.plane-env.sh`, which is the only file that records the name.
The script reads the name before it deletes the file.

Volumes always go. There is no flag that keeps them.

Docker runs first on purpose. If it fails, the run stops and the dev servers
stay up, which is the state you can recover from.

The script signals the four frontend ports only. Docker publishes the API,
PostgreSQL, Valkey, and MinIO ports, and the process holding them is
`com.docker.backend`. Signalling that stops the Docker daemon, which leaves
every container and volume behind. The script also refuses to signal any PID
whose command name contains `docker`.

The four volumes are `<project>_pgdata`, `<project>_uploads`,
`<project>_redisdata`, and `<project>_rabbitmq_data`.

## The one thing that does not come back

`plane-env-create` reseeds workspaces, projects, and work items. It does not
reseed uploads.

`<project>_uploads` holds every file that anyone attached through this stack.
Copy anything you need out of it before you run this skill.

## Scope

The script reads `COMPOSE_PROJECT_NAME` from `.env` and acts on that project
only. Another worktree's stack is a different project, with different volumes,
and this skill does not touch it.

If `.env` is absent, the script falls back to the directory name, normalized the
way Docker Compose normalizes it: lower-cased, with every character outside
`[a-z0-9_-]` removed.

A raw `basename` is not enough. A checkout at `~/Development/Plane` yields
`Plane`, while the running project is `plane`. `down -v` then matches nothing and
exits 0, so the script reports success while every container and volume survives,
and the `.env` that named them is already gone.

## Related

- `plane-env-create` builds the environment again.
- `reset.sh` in the repository root is narrower. It drops the volumes and
  restores a seed dump, and it leaves the `.env` files alone.
