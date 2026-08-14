---
name: plane-test-api
description: Run the apps/api pytest suite in Docker. Use when Python code under apps/api changed, when a reviewer asks whether the backend tests pass, or when you need to run one test file, one test, a marker subset, or a coverage report. Handles the compose project name that otherwise lets a test command delete the running development stack.
user_invocable: true
---

# Run the backend tests

516 tests, in Docker, against `docker-compose-test.yml`.

## Always set the project name first

```bash
export COMPOSE_PROJECT_NAME=plane-api-tests
```

Both compose files in this repository resolve to the same project name. Without
this variable the test stack joins the development stack's project. A later
`docker compose ... --remove-orphans` then deletes every container of the other
stack. Confirmed with `docker compose --dry-run -f docker-compose-test.yml down
--remove-orphans`, which listed the development `api`, `worker`, `plane-db`,
`plane-mq`, `plane-minio`, and `migrator` containers for removal.

Never pass `--remove-orphans` in this repository.

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
