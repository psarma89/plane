# Add Environment Variable SOP

> **Last reviewed:** 2026-08-13
> **Owner role:** Contributor
> **Risk:** Low

## Purpose

Add a new environment variable, or change an existing one, and make it reach the process that needs it.

## When to use

- **Trigger**: A change needs a new configuration value, or an existing value is wrong in a local stack.
- **Do not use this SOP when**: You only need different ports for a second checkout. The `plane-env-create` skill writes those.

## The six files

`setup.sh` copies each `.env.example` to `.env` beside it. Nothing else creates them.

| Template                  | Destination       | Read by                                                       |
| ------------------------- | ----------------- | ------------------------------------------------------------- |
| `.env.example`            | `.env`            | Docker Compose                                                |
| `apps/api/.env.example`   | `apps/api/.env`   | The `api`, `worker`, `beat-worker`, and `migrator` containers |
| `apps/web/.env.example`   | `apps/web/.env`   | `apps/web/vite.config.ts`                                     |
| `apps/admin/.env.example` | `apps/admin/.env` | `apps/admin/vite.config.ts`                                   |
| `apps/space/.env.example` | `apps/space/.env` | `apps/space/vite.config.ts`                                   |
| `apps/live/.env.example`  | `apps/live/.env`  | `node --env-file=.env`                                        |

`setup.sh` overwrites the `.env` file every time it runs. Put a new variable in the `.env.example`, or the next run of `setup.sh` deletes it.

`SECRET_KEY` is the exception. `setup.sh` generates it and appends it to `apps/api/.env`, and it is not in the template. Each run appends a different one, which invalidates every existing session.

## `${VAR}` expands in some of these files and not others

This is the single most common mistake.

| File                                                  | `${VAR}` inside it                                                                                                                                                                                                               |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.env`                                                | Expanded. Docker Compose substitutes before it parses the compose file.                                                                                                                                                          |
| `apps/api/.env`                                       | **Expanded.** Compose reads it as an `env_file` and substitutes. `DATABASE_URL` in the shipped template is literally `postgresql://${POSTGRES_USER}:...`, and the container sees `postgresql://plane:plane@plane-db:5432/plane`. |
| `apps/web/.env`, `apps/admin/.env`, `apps/space/.env` | **Not expanded.** `vite.config.ts` calls plain `dotenv`. `dotenv-expand` is not a dependency of any workspace. A `${VAR}` reaches the browser as those literal characters.                                                       |
| `apps/live/.env`                                      | **Not expanded.** `node --env-file` does no substitution.                                                                                                                                                                        |

Write literal values in the four frontend files.

## Procedure

1. Add the variable to the matching `.env.example`, with a default that works.

2. Add it to the matching `.env`, so the running stack picks it up without a fresh `setup.sh`.

3. Read the variable where it is needed.

   For Django, in `apps/api/plane/settings/`. For a frontend, the name **must** start with `VITE_`. `vite.config.ts` filters `process.env` to keys starting with `VITE_` and injects only those.

4. Apply the change. Use the table below. Picking the wrong row is why a change appears not to work.

5. Confirm the process sees it.

   ```bash
   docker compose -f docker-compose-local.yml exec -T api printenv YOUR_VAR
   ```

   Expected result: The value. An empty line means the container was never recreated.

## How to apply a change

| Variable lives in                                               | To apply the change                                                           | Why                                                                                                |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `.env`, used as `${VAR}` in the compose file                    | `docker compose -f docker-compose-local.yml up -d`                            | Compose substitutes when it parses the file                                                        |
| `.env`, as `env_file` for `plane-db`, `plane-mq`, `plane-minio` | `docker compose -f docker-compose-local.yml up -d <service>`                  | The container environment is fixed at create time                                                  |
| `apps/api/.env`                                                 | `docker compose -f docker-compose-local.yml up -d api worker beat-worker`     | Same. All three read this file.                                                                    |
| `apps/web/.env`, `apps/admin/.env`, `apps/space/.env`           | Stop `pnpm dev` and start it again. For a production build, run `pnpm build`. | `vite.config.ts` reads the file once, then `define` substitutes the values into the bundle as text |
| `apps/live/.env`                                                | Stop `pnpm dev` and start it again                                            | `node --env-file` reads the file once at process start                                             |

> **Destructive:** `docker compose restart` does **not** apply an `env_file` change. It reuses the existing container, and the environment was fixed when that container was created. A measured run confirmed this: after `restart api` the container still could not see a variable added minutes earlier, and after `up -d api` it could.

## Verification

| Check                   | Command                                                 | Expected                 |
| ----------------------- | ------------------------------------------------------- | ------------------------ |
| A container sees it     | `... exec -T api printenv YOUR_VAR`                     | The value                |
| Compose expanded it     | `... exec -T api printenv DATABASE_URL`                 | A URL with no `${` in it |
| A frontend sees it      | Read `process.env.VITE_YOUR_VAR` in the browser console | The value                |
| The template carries it | `grep YOUR_VAR .env.example apps/*/.env.example`        | At least one match       |

## Rollback

1. Remove the variable from the `.env` and the `.env.example`.

2. Recreate the affected containers.

   ```bash
   docker compose -f docker-compose-local.yml up -d
   ```

3. Restart `pnpm dev` if a frontend file changed.

## Troubleshooting

| Failure                                    | Cause                                                                          | Fix                                                                               |
| ------------------------------------------ | ------------------------------------------------------------------------------ | --------------------------------------------------------------------------------- |
| The container cannot see the variable      | You ran `docker compose restart`                                               | Run `docker compose up -d <service>`                                              |
| The browser shows `${SOMETHING}`           | You wrote `${VAR}` in a frontend `.env`, and plain `dotenv` does not expand it | Write the literal value                                                           |
| The browser cannot see the variable at all | The name does not start with `VITE_`, so `vite.config.ts` filters it out       | Rename it                                                                         |
| A frontend still shows the old value       | `define` substituted the old value into the bundle as text                     | Stop `pnpm dev` and start it again, or `pnpm build`                               |
| The variable disappeared after `setup.sh`  | `setup.sh` overwrites each `.env` from its template                            | Add it to the `.env.example` too                                                  |
| Everyone is signed out after `setup.sh`    | `setup.sh` appends a fresh `SECRET_KEY` to `apps/api/.env` on every run        | Expected. Sign in again.                                                          |
| CI builds without the variable             | CI has no `.env` file, so the value must come from the environment             | Add the name to `globalEnv` in `turbo.json`, which already lists 22 `VITE_` names |

## Related

| Page                                                                 | Why it matters here                                    |
| -------------------------------------------------------------------- | ------------------------------------------------------ |
| [`local-development-setup-sop.md`](./local-development-setup-sop.md) | Where `setup.sh` runs in the first place               |
| [`run-static-checks-sop.md`](./run-static-checks-sop.md)             | Turbo's caching, which treats `.env*` as a build input |
