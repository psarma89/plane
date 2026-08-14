---
name: plane-test-api
description: Run the apps/api pytest suite in Docker. Use when Python code under apps/api changed, when a reviewer asks whether the backend tests pass, or when you need to run one test file, one test, a marker subset, or a coverage report. Handles the compose project name that otherwise lets a test command delete the running development stack.
user_invocable: true
---

# Run the backend tests

516 tests, in Docker, against `docker-compose-test.yml`.

## Always set the project name first

If the checkout has a `.plane-env.sh`, which `plane-env-create` writes, use the
name that file already records:

```bash
source .plane-env.sh
export COMPOSE_PROJECT_NAME="$PLANE_TEST_PROJECT_NAME"
```

Otherwise derive the same name. Use `git rev-parse`, not `git branch
--show-current`, so that the result matches what `plane-env-create` wrote:

```bash
export COMPOSE_PROJECT_NAME="plane-api-tests-$(git rev-parse --abbrev-ref HEAD \
  | tr '[:upper:]' '[:lower:]' | tr -c 'a-z0-9' '-' | sed -E 's/-+/-/g; s/^-|-$//g')"
```

`git branch --show-current` prints nothing on a detached HEAD, mid-rebase, and
mid-bisect, which collapses the name to `plane-api-tests-` and puts every
detached checkout on the machine into one project. `git rev-parse --abbrev-ref
HEAD` prints `HEAD` in the same states, which is what `plane-env-create` uses.

Two reasons this variable matters, and both are load-bearing.

**It protects the development stack.** Both compose files in this repository
resolve to the same project name. Without this variable the test stack joins the
development stack's project. A later `docker compose ... --remove-orphans` then
deletes every container of the other stack. Confirmed with `docker compose
--dry-run -f docker-compose-test.yml down --remove-orphans`, which listed the
development `api`, `worker`, `plane-db`, `plane-mq`, `plane-minio`, and
`migrator` containers for removal.

**The branch suffix keeps two worktrees apart.** A fixed name gives every
checkout one project, so a second worktree that starts a test run joins the
first run's containers and the two suites share one database.
`docker-compose-test.yml` publishes no host port and declares no named volume,
so the project name is the only thing that couples two runs. Scope it and the
runs are independent.

Never pass `--remove-orphans` in this repository.

> **Destructive:** the hazard is `.env`, not `.plane-env.sh`. Docker Compose
> auto-loads `.env` from the working directory on every invocation, and
> `plane-env-create` writes `COMPOSE_PROJECT_NAME` into it. So a brand-new
> terminal that sources nothing is exposed as well. Verified: with only
> `COMPOSE_PROJECT_NAME=dev-stack-xyz` in `.env`, `docker compose -f
> docker-compose-test.yml config` reports `name: dev-stack-xyz`.
>
> Export the test project name in every shell that runs a test command. Sourcing
> `.plane-env.sh` is not the trigger, and skipping it is not a defence.

Every command below assumes that this variable is exported in the current shell.

## Whole suite

```bash
docker compose -f docker-compose-test.yml up --build \
  --abort-on-container-exit --exit-code-from api-tests
docker compose -f docker-compose-test.yml down
```

Expect `516 passed` and exit code 0. About 60 seconds of pytest, about 95
seconds of wall clock on a warm image.

`--exit-code-from api-tests` is what makes the shell exit code follow pytest.
Without it a failing suite still exits 0.

## Subsets

| Scope    | Command tail                                                                                    | Collects |
| -------- | ----------------------------------------------------------------------------------------------- | -------- |
| Unit     | `pytest -m unit`                                                                                | 338      |
| Contract | `pytest -m contract`                                                                            | 176      |
| Smoke    | `pytest -m smoke`                                                                               | 2        |
| One file | `pytest plane/tests/unit/models/test_workspace_model.py -vv`                                    | 1 file   |
| One test | `pytest "plane/tests/.../test_workspace_model.py::TestWorkspaceModel::test_workspace_creation"` | 1        |
| Coverage | `pytest --cov=plane --cov-report=term --cov-report=html`                                        | 516      |
| Quiet    | `pytest --capture=fd -q`                                                                        | 516      |

Prefix each with:

```bash
docker compose -f docker-compose-test.yml run --rm api-tests
```

The three markers sum to 516, so every test carries exactly one.

`pytest.ini` sets `addopts = -vs`. The `-s` disables output capture for all 516
tests, which buries a failing assertion. `--capture=fd -q` overrides it, because
a later argument wins.

## What a green run does not prove

`pytest.ini` sets `--nomigrations`. The suite builds tables from the models and
never runs a migration. A green run says nothing about whether a migration
exists, applies, or reverses. Check that separately.

## Traps

| Symptom                                              | Cause                                                              | Fix                                                                        |
| ---------------------------------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| `env file .../apps/api/.env not found`               | `setup.sh` has not run here                                        | `./setup.sh` from the repository root                                      |
| The development stack vanished                       | A compose call used `--remove-orphans` under a shared project name | Export `COMPOSE_PROJECT_NAME` first. Never use `--remove-orphans`.         |
| A schema error repeats every run                     | `--reuse-db` keeps the test database                               | Append `--create-db`, or `down -v` first                                   |
| `fixture 'mock_redis' not found`                     | `plane/tests/conftest_external.py` never loads                     | The fixture does not exist, whatever `plane/tests/README.md` line 128 says |
| `file or directory not found: .../test_workspace.py` | An older doc cites a path that does not exist                      | Use `test_workspace_model.py`                                              |

`down -v` is safe here. `docker-compose-test.yml` declares no named volumes, so
it cannot reach the development stack's data.

Do not run `apps/api/run_tests.sh`. It calls `exec tests/run_tests.sh`, and that
file does not exist.

## Related

- `docs/sops/run-backend-tests-sop.md` is the same procedure for a human.
- `apps/api/plane/tests/TESTING_GUIDE.md` covers writing a new test.
