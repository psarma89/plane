---
name: runtime-logs
description: Use when a request fails against the local stack, a page shows an error, a test passes but the app misbehaves, or the user asks what went wrong at runtime. Reads the real traceback instead of guessing. Do not use for test failures, which print their own output through plane-test-api or plane-test-live.
argument-hint: "{service name, or blank for api and worker}"
user_invocable: true
---

# Runtime logs

Read what the running stack actually did. The output is filtered and capped, so it does not flood the context.

`bin/logs` reads `COMPOSE_PROJECT_NAME` from this checkout's `.env`, so it follows the stack of this branch. Every branch runs its own Compose project. If `.env` is absent, no environment was created here. Run the `plane-env-create` skill first.

## Process

### 1. Get the filtered tail

```bash
bin/logs
```

It reads the last 200 lines of `api` and `worker`, filtered to tracebacks and 4xx and 5xx responses, capped at 25 lines. For one service: `bin/logs api`. Any service name from `docker-compose-local.yml` works, for example `beat-worker`.

### 2. If the filter hid the answer

```bash
bin/logs --raw
```

Use this only after the filtered view came back empty or irrelevant. The raw tail is mostly 200 responses, and it costs context for little return.

### 3. Name the failing layer before you propose a fix

| Symptom in the log                                 | Layer                                                           |
| -------------------------------------------------- | --------------------------------------------------------------- |
| Django traceback with a serializer or view frame   | `apps/api/plane/app/`                                           |
| `IntegrityError`, or `relation ... does not exist` | Migrations. Use the `plane-db-upgrade` skill                    |
| Celery traceback in `worker`                       | `apps/api/plane/bgtasks/`. See the `plane-celery-restart` skill |
| A 4xx with no traceback                            | Permissions or validation, not a crash                          |
| Nothing at all                                     | The request never reached the API                               |

An empty result is information. It means the failure is in the frontend. Stop reading server logs and check the browser console instead.

## Done when

- [ ] The failing layer is named
- [ ] The proposed fix cites a line from the log, not a guess
- [ ] `bin/logs` ran before `bin/logs --raw`

## Why

An agent without log access invents plausible causes, and a plausible wrong cause costs more than no cause. The filter exists because the unfiltered tail is mostly successful requests. The cap is 25 lines for the same reason.
