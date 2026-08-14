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
| 3 | Frontend dev servers of this checkout | `kill` on a PID whose working directory is this checkout |
| 4 | Generated files | `.env`, `apps/api/.env`, `apps/{web,admin,space,live}/.env`, `.plane-env.sh` |

The backend test suite runs in its own Compose project, named per branch, so step
1 does not reach it. Step 2 exists because nothing else removes it, and because
step 4 deletes `.plane-env.sh`, which is the only file that records the name. The
script reads the name before it deletes the file.

Step 2 reads that name only from `.plane-env.sh`. It never derives it. A branch
called `api/tests/foo` derives `plane-api-tests-foo`, which is the same name a
`foo` worktree uses for its own development project. If a step 2 teardown fails,
the script stops before step 4, so the record of the name survives.

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

If `.env` is absent, the script guesses in this order, and it verifies every guess
before it destroys anything.

| Order | Candidate | Why |
| --- | --- | --- |
| 1 | `COMPOSE_PROJECT_NAME` in `.env` | Authoritative |
| 2 | `plane-{slugified branch}` | The name `plane-env-create` builds |
| 3 | The directory name, normalized | What Compose itself defaults to |

A candidate counts only when it still has a container, or a `{project}_pgdata`
volume. If none of the three qualifies, the script refuses and tells you to run
`docker compose ls`.

The refusal matters more than the guessing. `down -v` against a project that does
not exist exits 0 and prints nothing, so without the check the script deleted the
`.env` files and reported success while every container and all four volumes
survived with their name gone.

Candidate 3 alone is never enough. `plane-env-create` names the worktree directory
after the slug and names the project `plane-{slug}`, so the normalized directory
name is always short by the `plane-` prefix and never matches a project that this
tooling built.

## It only signals dev servers that belong to this checkout

The script reads the frontend ports from `.env`, and `.env.example` ships 3000,
3001, 3002, and 3100. In a checkout bootstrapped by plain `./setup.sh`, those are
the ports of the main checkout's dev servers.

So a port match is not sufficient. The script signals a process only when the
working directory of that process is this checkout. It reads the working directory
with `lsof -a -p {pid} -d cwd`. It still refuses to signal any process whose
command name contains `docker`.

The port list is also re-read after the confirmation prompt, not before. The
prompt blocks for as long as you take, and a process can exit and have its PID
reused in that window.

## Related

- `plane-env-create` builds the environment again.
- `reset.sh` in the repository root is narrower. It drops the volumes and
  restores a seed dump, and it leaves the `.env` files alone.
