# Run Backend Tests SOP

> **Last reviewed:** 2026-08-13
> **Owner role:** Contributor
> **Risk:** Low

## Purpose

Run the `apps/api` pytest suite in Docker and read the result.

## When to use

- **Trigger**: A contributor changed Python code in `apps/api` and needs to know whether the suite still passes.
- **Do not use this SOP when**: You need a browser or seeded demo data. Read [`local-development-setup-sop.md`](./local-development-setup-sop.md) instead. That stack is `docker-compose-local.yml`, and it is a different stack from the one here.

## What a green run does and does not prove

`pytest.ini` sets `--nomigrations`. The suite builds tables from the models, so it never executes a migration. A green run does not prove that a migration exists, applies, or reverses.

Verify migrations separately.

## Prerequisites

Complete every item before step 1.

| Item                             | How to confirm                                               |
| -------------------------------- | ------------------------------------------------------------ |
| Docker is running                | `docker info --format '{{.ServerVersion}}'` prints a version |
| `apps/api/.env` exists           | `ls apps/api/.env` prints the path                           |
| The repository root holds `.env` | `ls .env` prints the path                                    |

If either `.env` file is absent, run `./setup.sh` once from the repository root. It writes both.

## Procedure

> **Destructive:** Never pass `--remove-orphans` to a `docker compose` call in this repository. Both compose files resolve to the same project name, so `--remove-orphans` on one file deletes every container of the other. It removes a running development stack without asking.

1. Set a project name for the test stack.

   ```bash
   export COMPOSE_PROJECT_NAME=plane-api-tests
   ```

   Expected result: The test stack no longer shares a project with the development stack.

2. Run the whole suite.

   ```bash
   docker compose -f docker-compose-test.yml up --build \
     --abort-on-container-exit --exit-code-from api-tests
   ```

   Expected result: `516 passed` and exit code 0. The run takes about 60 seconds of pytest, and about 95 seconds of wall clock on a warm image.

3. Stop the test stack.

   ```bash
   docker compose -f docker-compose-test.yml down
   ```

   Expected result: Five containers stop and are removed.

## Running less than the whole suite

Use `run --rm` for a subset. It starts the dependencies and removes the container afterwards.

| Scope    | Command                                                                           | Collects |
| -------- | --------------------------------------------------------------------------------- | -------- |
| Unit     | `docker compose -f docker-compose-test.yml run --rm api-tests pytest -m unit`     | 338      |
| Contract | `docker compose -f docker-compose-test.yml run --rm api-tests pytest -m contract` | 176      |
| Smoke    | `docker compose -f docker-compose-test.yml run --rm api-tests pytest -m smoke`    | 2        |

The three markers sum to 516, so every test carries exactly one of them.

One file:

```bash
docker compose -f docker-compose-test.yml run --rm api-tests \
  pytest plane/tests/unit/models/test_workspace_model.py -vv
```

One test:

```bash
docker compose -f docker-compose-test.yml run --rm api-tests \
  pytest "plane/tests/unit/models/test_workspace_model.py::TestWorkspaceModel::test_workspace_creation"
```

Coverage. The HTML report lands in `apps/api/htmlcov`:

```bash
docker compose -f docker-compose-test.yml run --rm api-tests \
  pytest --cov=plane --cov-report=term --cov-report=html
```

Quieter output. `pytest.ini` sets `addopts = -vs`, and `-s` disables capture for every test. A later argument wins:

```bash
docker compose -f docker-compose-test.yml run --rm api-tests pytest --capture=fd -q
```

## Verification

| Check                          | Command                                        | Expected                                         |
| ------------------------------ | ---------------------------------------------- | ------------------------------------------------ |
| The suite passed               | `echo $?` after step 2                         | `0`                                              |
| The count is right             | Read the last pytest line                      | `516 passed`                                     |
| No test stack is left          | `docker compose -f docker-compose-test.yml ps` | No rows                                          |
| The development stack survived | `docker compose ls`                            | The development project still reads `running(7)` |

## Rollback

No rollback. The suite reads code and writes only to a throwaway database inside the test stack. `docker compose -f docker-compose-test.yml down` returns the machine to its previous state.

To discard a test database that survived a run, add `-v`:

```bash
docker compose -f docker-compose-test.yml down -v
```

This is safe. `docker-compose-test.yml` declares no named volumes, so `-v` cannot reach the development stack's data.

## Troubleshooting

| Failure                                                                         | Cause                                                                                                 | Fix                                                                                                  |
| ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `env file .../apps/api/.env not found`                                          | `setup.sh` has not run in this checkout                                                               | Run `./setup.sh` from the repository root                                                            |
| The development stack disappeared                                               | A `docker compose` call used `--remove-orphans` while both files shared a project name                | Set `COMPOSE_PROJECT_NAME` before every test command, as step 1 does. Rebuild the development stack. |
| A schema error repeats across runs                                              | `pytest.ini` sets `--reuse-db`, so the test database survives                                         | Append `--create-db`, or run `down -v` and start again                                               |
| `fixture 'mock_redis' not found`                                                | `plane/tests/conftest_external.py` is not named `conftest.py`, and no `pytest_plugins` entry loads it | The fixture does not exist. Do not use it. See "Known defects".                                      |
| `ERROR: file or directory not found: plane/tests/unit/models/test_workspace.py` | The path in an older doc is wrong                                                                     | Use `test_workspace_model.py`                                                                        |
| A model change passes here and then fails in a running instance                 | `--nomigrations` means the suite never runs a migration                                               | Verify the migration separately                                                                      |

## Known defects in the repository

These are stated here so that a reader does not lose time on them. This SOP does not change them.

| Defect                                                                               | Effect                                                                                                                                                          |
| ------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `apps/api/run_tests.sh` runs `exec tests/run_tests.sh`, and that file does not exist | The wrapper fails immediately. Use the `docker compose` commands above.                                                                                         |
| `apps/api/plane/tests/conftest_external.py` is never loaded                          | The `mock_redis`, `mock_elasticsearch`, and `mock_celery` fixtures do not reach any test, although `plane/tests/README.md` line 128 tells a reader to use them. |
| `pytest.ini` declares a `slow` marker                                                | No test uses it, so it gates nothing.                                                                                                                           |

## Related

| Page                                                                                         | Why it matters here                                          |
| -------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| [`local-development-setup-sop.md`](./local-development-setup-sop.md)                         | The development stack, which is separate from the test stack |
| [`../../apps/api/plane/tests/TESTING_GUIDE.md`](../../apps/api/plane/tests/TESTING_GUIDE.md) | Marker and category conventions for writing a new test       |
| [`../../apps/api/plane/tests/README.md`](../../apps/api/plane/tests/README.md)               | The fixture list                                             |
