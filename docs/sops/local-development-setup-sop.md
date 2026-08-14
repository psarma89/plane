# Local Development Setup SOP

> **Last reviewed:** 2026-08-14
> **Owner role:** Contributor
> **Risk:** Low

## Purpose

Run the whole Plane stack on one machine, then sign in to the web app in a browser against seeded demo data.

## When to use

- **Trigger**: A contributor needs a working Plane development environment on a new machine.
- **Do not use this SOP when**: You only need the Django test suite. Read the "Backend tests run in Docker" section of [`../../AGENTS.md`](../../AGENTS.md) instead. That suite uses `docker-compose-test.yml` and needs no browser.

## Prerequisites

Complete every item before step 1.

| Item                                 | How to confirm                                  |
| ------------------------------------ | ----------------------------------------------- |
| Docker Engine with Compose v2        | `docker --version` and `docker compose version` |
| Docker memory limit of 12 GB or more | Docker Desktop, then Settings, then Resources   |
| Node.js 22.18.0 or later             | `node --version`                                |
| Corepack                             | `corepack --version`                            |
| Git                                  | `git --version`                                 |
| `curl`                               | `curl --version`                                |

`package.json` sets `engines.node` to `>=22.18.0`. `.mise.toml` pins Node 22.18.0, but you do not need `mise` to satisfy that floor. This SOP also ran on Node 24.18.0.

### Install the prerequisites

| Tool     | macOS                                                           | Debian or Ubuntu                                      |
| -------- | --------------------------------------------------------------- | ----------------------------------------------------- |
| Docker   | `brew install --cask docker`, then open Docker Desktop one time | Follow the Docker Engine apt guide at docs.docker.com |
| Node.js  | nvm. See below.                                                 | nvm. See below.                                       |
| Corepack | Ships with Node.js 22                                           | Ships with Node.js 22                                 |
| Git      | `xcode-select --install`                                        | `sudo apt install git`                                |

Docker Desktop must run before step 4. If `docker info` fails, Docker is not running.

### Install Node.js with nvm

nvm is the installer that nodejs.org lists first, and it works the same way on macOS and on Linux. Run these four commands one time.

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.6/install.sh | bash
export NVM_DIR="$HOME/.nvm"
\. "$NVM_DIR/nvm.sh"
nvm install 22
```

Expected result: the last command prints `Now using node v22.x.y`. A measured run installed Node v22.23.2 with npm 10.9.8, which clears the `>=22.18.0` floor.

Open a new terminal for every later step, and select the version again:

```bash
nvm use 22
node --version
corepack --version
```

Expected result: `v22.23.2` or later, then a corepack version. A measured run reported corepack 0.35.0.

Name the major version. This repository ships no `.nvmrc`, so a bare `nvm use` fails with `No .nvmrc file found`.

Check the version that nodejs.org lists today at https://nodejs.org/en/download. The pinned tag in the URL above moves with each nvm release. This SOP verified the commands with nvm 0.40.4.

## The automated path

The `plane-env-create` skill runs steps 3 to 13 of this procedure without a browser. Use it for a second checkout, a worktree, or any environment you plan to throw away.

```
/plane-env-create
```

It derives 9 ports from a hash of the branch name, so several checkouts run at the same time on one machine. It writes the six `.env` files, starts the stack, registers the instance admin, seeds the demo data, and prints the sign-in credentials. `plane-env-teardown` destroys the containers and the volumes again.

Read the rest of this page before you use the skill for your first environment. The skill hides the failure modes that this procedure teaches.

## Procedure

1. Clone the repository.

   ```bash
   git clone https://github.com/makeplane/plane.git
   cd plane
   ```

   Expected result: the directory holds `setup.sh` and `docker-compose-local.yml`.

   `CONTRIBUTING.md` shows `git clone https://github.com/makeplane/plane.git [folder-name]`. The bracketed value is an optional target directory name. The clone always contains the whole repository.

   Docker Compose derives the project name from the directory name. A clone into `plane/` names the containers `plane-api-1`, `plane-plane-db-1`, and so on.

2. Confirm that the nine published ports are free.

   ```bash
   lsof -nP -iTCP -sTCP:LISTEN | grep -E ':(3000|3001|3002|3100|5432|6379|8000|9000|9090) '
   ```

   Expected result: no output.

   If a line appears, you have two options. Stop the service that holds the port. A local PostgreSQL on port 5432 is the common case.

   ```bash
   brew services list | grep postgres
   brew services stop postgresql@18
   ```

   Or move Plane instead. Every published port reads from a variable with a default, so you never have to edit `docker-compose-local.yml`.

   | Variable                        | Default | Service       |
   | ------------------------------- | ------- | ------------- |
   | `PLANE_HOST_WEB_PORT`           | 3000    | `web`         |
   | `PLANE_HOST_ADMIN_PORT`         | 3001    | `admin`       |
   | `PLANE_HOST_SPACE_PORT`         | 3002    | `space`       |
   | `PLANE_HOST_API_PORT`           | 8000    | `api`         |
   | `PLANE_HOST_DB_PORT`            | 5432    | `plane-db`    |
   | `PLANE_HOST_REDIS_PORT`         | 6379    | `plane-redis` |
   | `PLANE_HOST_MINIO_PORT`         | 9000    | `plane-minio` |
   | `PLANE_HOST_MINIO_CONSOLE_PORT` | 9090    | `plane-minio` |

   Set the value in `.env` after step 3, then run step 4. `apps/live` reads `PORT` from `apps/live/.env`, which defaults to 3100.

   Changing a port does not change an application URL. `apps/api/.env` and the three frontend `.env` files carry literal ports, and `CORS_ALLOWED_ORIGINS` feeds `CSRF_TRUSTED_ORIGINS`. Read [`add-environment-variable-sop.md`](./add-environment-variable-sop.md) before you move a port by hand.

3. Run the setup script.

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   Expected result: the script prints `Environment setup completed successfully!`.

   `setup.sh` does four things. The script never starts a container.

   | Action                                                                     | Effect                                                                                    |
   | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
   | Copies six `.env.example` files to `.env`                                  | Creates the root file and one file for each of `api`, `web`, `admin`, `space`, and `live` |
   | Generates a 50 character value and appends `SECRET_KEY` to `apps/api/.env` | Django refuses to start without it                                                        |
   | Runs `corepack enable pnpm`                                                | Activates the pnpm version that `packageManager` pins in `package.json`                   |
   | Runs `pnpm install`                                                        | Installs the dependencies for all 20 workspace projects                                   |

   Verify the six files.

   ```bash
   ls .env apps/api/.env apps/web/.env apps/admin/.env apps/space/.env apps/live/.env
   ```

4. Build the images and start the containers.

   ```bash
   docker compose -f docker-compose-local.yml up -d --build
   ```

   Expected result: Docker creates and starts eight containers.

5. Confirm the containers.

   ```bash
   docker compose -f docker-compose-local.yml ps -a
   ```

   Expected result: seven containers report `Up`. The `migrator` container reports `Exited (0)`.

   `Exited (0)` is the correct end state for `migrator`. That container applies the migrations one time and stops. `docker-compose-local.yml` defines no health check, so no container ever reports `healthy`.

   The eight containers hold these roles.

   | Service       | Role                                           | Published port |
   | ------------- | ---------------------------------------------- | -------------- |
   | `plane-db`    | PostgreSQL, the primary datastore              | 5432           |
   | `plane-redis` | Valkey, the Django cache and the rate limiters | 6379           |
   | `plane-mq`    | RabbitMQ, the Celery broker                    | none           |
   | `plane-minio` | S3-compatible object storage for attachments   | 9000 and 9090  |
   | `migrator`    | Applies the Django migrations, then exits      | none           |
   | `api`         | The Django development server                  | 8000           |
   | `worker`      | The Celery worker for background tasks         | none           |
   | `beat-worker` | The Celery beat scheduler                      | none           |

6. Wait for the API.

   ```bash
   until curl -sf -o /dev/null http://localhost:8000/api/instances/; do sleep 3; done
   ```

   Expected result: the loop ends. The first start applies 87 migrations and takes about 60 seconds.

7. Build the shared packages one time.

   ```bash
   pnpm build
   ```

   Expected result: every Turbo task reports success.

   Do not skip this step. `pnpm dev` starts the `build` task and the `dev` task of `packages/propel` at the same time. Both tasks write to `packages/propel/dist`. On an empty `dist` they race, and the build fails with `EEXIST`. A completed `pnpm build` removes the race.

8. Start the frontends in a second terminal.

   ```bash
   pnpm dev
   ```

   Do not close this terminal. Expected result: the log prints one `Local:` line for each of ports 3000, 3001, and 3002. The log also prints `Express server has started at port 3100`.

9. Open `http://localhost:3001/god-mode/` in the browser, then reload the page one time.

   Expected result: the form "Setup your Plane Instance" appears.

   The reload is not optional on a first load. Vite optimises the dependencies during the first request and answers `504 Outdated Optimize Dep` for the modules that the page already requested. Without the reload the page shows only the loading spinner.

10. Register the instance admin.

    Fill every field. Clear the telemetry checkbox. Then select **Continue**.

    The password must meet five rules.
    - 8 characters or more
    - 1 upper-case letter
    - 1 lower-case letter
    - 1 number
    - 1 special character

    Store the email address and the password in a password manager. Step 11 and step 12 both need them. This SOP uses the email address `admin@plane.local`.

    Expected result: the browser opens `/god-mode/general/` and shows "Instance setup done!".

    One form submission creates both the user and the instance admin. No separate command is needed.

11. Seed the demo data.

    ```bash
    printf 'Plane Local\nplane-local\nadmin@plane.local\n\n2\n20\n2\n5\n4\n2\n20\n2\n5\n4\n2\n' \
      | docker compose -f docker-compose-local.yml exec -T api python manage.py create_dummy_data
    ```

    Expected result: the command prints `Data is pushed to the queue`.

    The command reads 5 workspace answers, then 5 answers for each project. The `printf` string above answers them in this order.

    | Prompt                  | Value               | Note                                         |
    | ----------------------- | ------------------- | -------------------------------------------- |
    | Workspace Name          | `Plane Local`       |                                              |
    | Workspace slug          | `plane-local`       | The command fails if the slug already exists |
    | Your email              | `admin@plane.local` | The user must exist, so step 10 comes first  |
    | Member emails           | empty               |                                              |
    | Number of projects      | `2`                 |                                              |
    | Number of issues        | `20`                |                                              |
    | Number of cycles        | `2`                 | The command creates 3                        |
    | Number of modules       | `5`                 | Do not go below 5. See Troubleshooting       |
    | Number of pages         | `4`                 |                                              |
    | Number of intake issues | `2`                 | The command adds these to the issue total    |

    The prompts never ask for a label count. `create_labels` in `apps/api/plane/bgtasks/dummy_data_task.py` always requests 50 labels, and duplicate colour names reduce the result to 40.

    Despite the message, the command runs the work in the foreground. It does not wait for a Celery worker.

12. Sign in to the web app.
    - Open `http://localhost:3000`.
    - Enter the email address from step 10, then select **Continue**.
    - Enter the password, then select **Go to workspace**.
    - Accept the name on the "Create your profile" step, then select **Continue**.

    Expected result: the browser opens `/plane-local/` and the sidebar lists both seeded projects.

13. Snapshot the seeded database.

    ```bash
    mkdir -p tmp
    docker compose -f docker-compose-local.yml exec -T plane-db \
      pg_dump -U plane -d plane --clean --if-exists > tmp/seed.sql
    ```

    Expected result: `tmp/seed.sql` is larger than 100 KB. This SOP measured 1.4 MB.

    `.gitignore` already excludes `tmp/`, so the snapshot never reaches a commit. The `--clean --if-exists` flags make the restore in `reset.sh` safe against a database that already holds tables.

## Verification

Prove the procedure worked. Do not rely on the absence of an error.

| Check                                        | Command                                                                          | Expected                                 |
| -------------------------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------- |
| Seven services run and the migrator finished | `docker compose -f docker-compose-local.yml ps -a`                               | 7 rows `Up`, `migrator` row `Exited (0)` |
| The API answers                              | `curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/instances/`    | `200`                                    |
| The instance is registered                   | `curl -s http://localhost:8000/api/instances/ \| grep -o '"is_setup_done":true'` | `"is_setup_done":true`                   |
| The web app answers                          | `curl -s -o /dev/null -w '%{http_code}' http://localhost:3000`                   | `200`                                    |
| The admin app answers                        | `curl -s -o /dev/null -w '%{http_code}' http://localhost:3001/god-mode/`         | `200`                                    |
| The space app answers                        | `curl -s -o /dev/null -w '%{http_code}' http://localhost:3002/spaces/`           | `200`                                    |
| The seed landed                              | see the command below                                                            | `2` projects and `44` issues             |
| The snapshot exists                          | `wc -c < tmp/seed.sql`                                                           | a number above `100000`                  |

```bash
docker compose -f docker-compose-local.yml exec -T api python manage.py shell -c \
  "from plane.db.models import Project, Issue; print(Project.objects.count(), Issue.objects.count())"
```

### The browser check that matters

The commands above prove that the services answer. They do not prove that the product works. Complete these four checks in the browser.

1. Open a seeded project, then confirm that the list layout shows 22 work items.
2. Open the layout menu, select **Board**, then confirm that the columns Backlog, Todo, and In Progress hold cards.
3. Open the layout menu, select **Timeline**, then confirm that the bars carry a duration. This layout replaces the older Gantt name.
4. Select **Add work item**, enter a title, then select **Save**. Confirm that the new item appears in the list. This item comes after the snapshot in step 13, so the next `./reset.sh` removes it.
5. Select any work item to open the peek view, then confirm that the header shows **Saved**.

Check 5 is the only browser check that exercises the `live` service on port 3100. That service runs under `pnpm dev`, not under Docker. **Saved** means the editor reached the collaboration server, and that the server reached Valkey. If the header never leaves **Saving**, read the `live:dev` lines in the `pnpm dev` log.

The seeded descriptions are long blocks of nonsense words. `create_issues` in `apps/api/plane/bgtasks/dummy_data_task.py` fills them from Faker. That output is correct, not corrupt data.

### Measured timings

Recorded on 2026-08-13 on Apple Silicon macOS, with Docker 29.6.2, 15 CPUs, and a 23 GiB Docker memory limit.

| Cold start measurement                                    | Run 1 | Run 2 |
| --------------------------------------------------------- | ----- | ----- |
| `docker compose build --no-cache`, all four Django images | 92 s  | 101 s |
| Build start to the API answering on port 8000             | 158 s | 191 s |

Both cold starts removed the four `plane-*` images and every volume first, and both passed `--no-cache`.

| Measurement                                          | Result        | Runs |
| ---------------------------------------------------- | ------------- | ---- |
| `./setup.sh` with a warm pnpm store                  | 13 s          | 1    |
| `pnpm build` from an empty `dist`, 16 Turbo tasks    | 31 s          | 1    |
| `pnpm dev` until port 3000 answers, after that build | 14 s          | 1    |
| `./reset.sh`, a full reset from the snapshot         | 52 s and 53 s | 2    |

A first install on a machine with an empty pnpm store adds download time that depends on the network. `setup.sh` takes longer than 13 s on that machine.

## Rollback

Two paths exist. Pick the first one for daily work.

1. Reset to the snapshot. The script drops the volumes, restores `tmp/seed.sql`, and restarts the stack.

   ```bash
   chmod +x reset.sh
   ./reset.sh
   ```

   Expected result: the script prints `Reset complete`, and the migrator log reports `No migrations to apply`.

   `pnpm dev` runs outside Docker, so a reset does not stop it. The reset removes the Valkey container, so the `live` service loses its connection. It reconnects on its own. The log reports `Redis client ready` about 3 seconds later.

2. Remove everything that this SOP created.

   > **Destructive:** This step deletes the seeded database, the uploaded files, and the built images. A later cold start then costs about 3 minutes.

   ```bash
   docker compose -f docker-compose-local.yml down -v --remove-orphans
   docker rmi -f plane-api plane-worker plane-beat-worker plane-migrator
   ```

   Then start the local PostgreSQL again, if step 2 of the procedure stopped it.

   ```bash
   brew services start postgresql@18
   ```

   The `plane-env-teardown` skill does the same work for an environment that `plane-env-create` built. It always destroys the volumes, and it prints the containers and the host processes it will stop before it stops them.

> **Destructive:** Never add `--remove-orphans` to a `docker compose` command in a checkout that also runs the test stack. Both compose files resolve to the same project name, so that flag removes all 8 development containers. Read [`run-backend-tests-sop.md`](./run-backend-tests-sop.md).

## Troubleshooting

| Failure                                                                                 | Cause                                                                                                                                                                   | Fix                                                                                                                              |
| --------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `Bind for 0.0.0.0:5432 failed: port is already allocated`                               | Another PostgreSQL holds port 5432.                                                                                                                                     | Stop it, then run step 4 again. `brew services stop postgresql@18`                                                               |
| `EEXIST: file already exists, mkdir '.../packages/propel/dist/styles'`                  | `pnpm dev` ran the propel `build` task and `dev` task at the same time on an empty `dist`.                                                                              | Run `pnpm build`, then `pnpm dev`.                                                                                               |
| The admin page shows only a spinner. The console reports `504 (Outdated Optimize Dep)`. | Vite re-optimised the dependencies during the first page load.                                                                                                          | Reload the page.                                                                                                                 |
| `Command errored out Sample larger than population or is negative`                      | `create_module_issues` in `apps/api/plane/bgtasks/dummy_data_task.py` samples up to 5 modules from the modules that exist. The command fails with fewer than 5 modules. | Answer 5 or more at the modules prompt. The failed run leaves a partial workspace, so pick a new slug or run `./reset.sh` first. |
| `Workspace already exists`                                                              | An earlier seed run created that slug.                                                                                                                                  | Use a new slug, or run `./reset.sh`.                                                                                             |
| `pnpm install` fails with HTTP 401                                                      | The default npm registry points at a private proxy that does not serve public packages.                                                                                 | Run `pnpm install --registry https://registry.npmjs.org`. Do not edit the tracked `.npmrc`.                                      |
| `api` restarts and logs `Waiting for database migrations to complete...`                | The `migrator` container still runs.                                                                                                                                    | Wait. Read the progress with `docker compose -f docker-compose-local.yml logs -f migrator`.                                      |
| The API answers, but the browser shows a blank page                                     | The frontends run outside Docker.                                                                                                                                       | Confirm that `pnpm dev` still runs in its terminal.                                                                              |
| A workspace delete leaves projects and issues behind                                    | Plane soft-deletes the child rows.                                                                                                                                      | Do not clean up through the ORM. Run `./reset.sh`.                                                                               |

## Related

| Page                                                                                   | Why it matters here                                                              |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| [System context](../architecture/c4/l1-context/01-system-context.md)                   | Names every surface that this SOP starts, and every external system it can reach |
| [Infrastructure index](../devops/infra/INDEX.md)                                       | Describes the services that `docker-compose-local.yml` runs                      |
| [Containers index](../architecture/c4/l2-containers/INDEX.md)                          | Explains how the API, the workers, and the queue interact                        |
| [`../../CONTRIBUTING.md`](../../CONTRIBUTING.md)                                       | The upstream five-step summary that this SOP expands                             |
| [`add-environment-variable-sop.md`](./add-environment-variable-sop.md)                 | What each of the six `.env` files owns, and how to apply a change                |
| [`drain-and-restart-celery-workers-sop.md`](./drain-and-restart-celery-workers-sop.md) | How to restart `worker` without losing a running task                            |
| [`clear-valkey-cache-sop.md`](./clear-valkey-cache-sop.md)                             | What shares the Valkey database that this stack starts                           |
| [`run-backend-tests-sop.md`](./run-backend-tests-sop.md)                               | The other stack, `docker-compose-test.yml`, and why its project name matters     |
