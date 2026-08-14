---
name: plane-env-var
description: Add or change an environment variable in the Plane monorepo and make it actually reach the process that reads it. Use when a change needs a new config value, when a variable you set appears to have no effect, or when you need to know which of the six .env files owns a name. Covers why docker compose restart does not apply an env_file change.
user_invocable: true
---

# Add or change an environment variable

Six `.env` files. `setup.sh` copies each from the `.env.example` beside it and
**overwrites** it, so a variable that is not in the template disappears on the
next run.

| Template                              | Destination      | Read by                                    |
| ------------------------------------- | ---------------- | ------------------------------------------ |
| `.env.example`                        | `.env`           | Docker Compose                             |
| `apps/api/.env.example`               | `apps/api/.env`  | `api`, `worker`, `beat-worker`, `migrator` |
| `apps/{web,admin,space}/.env.example` | `apps/*/.env`    | each `vite.config.ts`                      |
| `apps/live/.env.example`              | `apps/live/.env` | `node --env-file=.env`                     |

`SECRET_KEY` is not in any template. `setup.sh` generates and appends a new one
to `apps/api/.env` on every run, which signs everyone out.

## `${VAR}` expands in half of them

| File                          | Expands                                                                                                                                                                                     |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.env`                        | Yes, Compose substitutes it                                                                                                                                                                 |
| `apps/api/.env`               | **Yes.** Compose reads it as `env_file`. The shipped `DATABASE_URL` is literally `postgresql://${POSTGRES_USER}:...` and the container sees `postgresql://plane:plane@plane-db:5432/plane`. |
| `apps/{web,admin,space}/.env` | **No.** Plain `dotenv`; `dotenv-expand` is not a dependency anywhere.                                                                                                                       |
| `apps/live/.env`              | **No.** `node --env-file` does not substitute.                                                                                                                                              |

Write literal values in the four frontend files.

## restart does not apply an env change

| Command                      | Picks up an `env_file` change |
| ---------------------------- | ----------------------------- |
| `docker compose restart api` | **No**                        |
| `docker compose up -d api`   | **Yes**                       |

`restart` reuses the existing container, and a container's environment is fixed
when it is created. Measured: after `restart api` the container still could not
see a variable added minutes before; after `up -d api` it could.

## How to apply, by file

| Changed                                     | Do this                                                                   |
| ------------------------------------------- | ------------------------------------------------------------------------- |
| `.env` used as `${VAR}` in the compose file | `docker compose -f docker-compose-local.yml up -d`                        |
| `apps/api/.env`                             | `docker compose -f docker-compose-local.yml up -d api worker beat-worker` |
| `apps/{web,admin,space}/.env`               | Stop `pnpm dev`, start it again. For production, `pnpm build`.            |
| `apps/live/.env`                            | Stop `pnpm dev`, start it again                                           |

## Only VITE\_ reaches the browser

`vite.config.ts` filters `process.env` to keys starting with `VITE_`, then
injects them through `define: { "process.env": JSON.stringify(viteEnv) }`. That
is a **textual substitution at transform time**, so the old value stays in the
bundle until the dev server restarts or you rebuild.

A name without the `VITE_` prefix never reaches the browser.

## Confirm it landed

```bash
docker compose -f docker-compose-local.yml exec -T api printenv YOUR_VAR
```

An empty line means the container was never recreated.

## Traps

| Symptom                                | Cause                                                     | Fix                                         |
| -------------------------------------- | --------------------------------------------------------- | ------------------------------------------- |
| Container cannot see it                | You used `restart`                                        | Use `up -d <service>`                       |
| Browser shows `${SOMETHING}` literally | `${VAR}` in a frontend `.env`                             | Write the literal value                     |
| Browser cannot see it at all           | Name lacks the `VITE_` prefix                             | Rename it                                   |
| Frontend keeps the old value           | `define` baked the old value into the bundle              | Restart `pnpm dev`, or `pnpm build`         |
| It vanished after `setup.sh`           | `setup.sh` overwrites each `.env` from its template       | Add it to the `.env.example`                |
| CI builds without it                   | CI has no `.env`, so the value comes from the environment | Add the name to `globalEnv` in `turbo.json` |

## Related

- `docs/sops/add-environment-variable-sop.md` is the human procedure.
- `plane-env-create` writes all six files for a worktree.
