---
name: plane-celery-restart
description: Drain and restart the Plane Celery worker without losing the tasks that are running. Use before restarting the worker after a task-code or apps/api/.env change, when the worker stopped consuming, or when a background job silently never ran. Explains why docker compose restart worker destroys every in-flight task and never retries it.
user_invocable: true
---

# Drain and restart the Celery worker

`docker compose restart worker` loses every running task, permanently. Use the
drain below instead.

## The one command

```bash
docker compose -f docker-compose-local.yml exec -T worker \
  bash -c 'kill -TERM $(pgrep -P 1)'
```

Running tasks finish. Celery exits 0. `restart: unless-stopped` starts the
container again by itself, so this drains **and** restarts.

Watch for `worker: Warm shutdown (MainProcess)` in the log. The wait equals the
longest running task.

**Never use `pkill -TERM -f celery`.** All 15 pool children share the
MainProcess command line, so that pattern kills the running tasks. `pgrep -P 1`
selects only the one child of PID 1.

## Why restart loses the work

| Setting                      | Effective | Consequence                                          |
| ---------------------------- | --------- | ---------------------------------------------------- |
| `task_acks_late`             | `False`   | The ack happens before the task runs. No redelivery. |
| `worker_prefetch_multiplier` | `4`       | The worker holds `4 x concurrency` messages.         |
| `task_time_limit`            | `None`    | A task can run forever.                              |
| `result_backend`             | `None`    | Results are discarded. `AsyncResult` never returns.  |

None of the four is set anywhere in the repository. All four are Celery
defaults.

Measured on concurrency 15, with 20 tasks of 45 seconds:

| Command                      | Outcome                                       |
| ---------------------------- | --------------------------------------------- |
| `docker compose stop worker` | 11s, exit 137. **15 tasks lost, 5 requeued.** |
| `docker compose stop -t 90`  | 91s, exit 137, no shutdown line. Same loss.   |
| `kill -TERM $(pgrep -P 1)`   | Exit 0. All tasks finished.                   |

## SIGTERM never reaches Celery

`apps/api/bin/docker-entrypoint-worker.sh` ends with `celery -A plane worker -l
info` and no `exec`. Bash stays PID 1 and defers signals while a foreground
child runs, so Celery never sees the SIGTERM that Docker sends. A longer
`-t` does not help.

```bash
docker compose -f docker-compose-local.yml exec -T worker ps -eo pid,ppid,args | head -3
```

PID 1 is bash. `apps/api/bin/docker-entrypoint-api.sh` uses `exec`. The worker
and beat entrypoints do not.

## The two-line fix

Verified, not applied to the repository.

1. Prefix the last line of `apps/api/bin/docker-entrypoint-worker.sh` with `exec`.
2. Add `stop_grace_period: 120s` to the `worker` service.

With both, `docker compose restart worker` took 43 seconds against one
45-second task and the task finished.

## Beat is safe to restart hard

```bash
docker compose -f docker-compose-local.yml restart beat-worker
```

Beat runs no task. It only sends messages. `DatabaseScheduler` keeps
`last_run_at` in PostgreSQL, so 13 `PeriodicTask` rows survive the kill. Beat
does not catch up. A window that closes during the restart is skipped.

## Registration is an import chain, not a list

`CELERY_IMPORTS` in `apps/api/plane/settings/common.py` names only 9 modules.
`autodiscover_tasks()` finds nothing, because Plane keeps tasks in
`plane/bgtasks/*_task.py` and not in `tasks.py`. The other tasks register
because Django imports the views that import them.

A module that no view imports is never registered. Its messages are
**discarded**, not retried:

```
ERROR/MainProcess] Received unregistered task of type '...'.
The message has been ignored and discarded.
```

```bash
docker compose -f docker-compose-local.yml exec -T worker \
  celery -A plane inspect registered | grep -c "plane\."
```

Returns `46` on `dev`. The repository declares 47.

## Known defects on dev

| Defect                                                                  | Effect                                             |
| ----------------------------------------------------------------------- | -------------------------------------------------- |
| `plane/app/views/project/invite.py:108` calls `.delay()` on a list      | `AttributeError`. Invitation emails never send.    |
| `project_invitation` is the one declared task never registered          | Same cause. No module imports it.                  |
| `plane/celery.py` schedules `delete_old_s3_link` at 01:30 **and** 03:45 | It runs twice a day. The names differ by one char. |

## Traps

| Symptom                             | Cause                                       | Fix                             |
| ----------------------------------- | ------------------------------------------- | ------------------------------- |
| Exit code 137                       | SIGKILL after the 10s default grace period  | Use the drain command           |
| The drain killed the tasks          | `pkill -f celery` matched the pool children | Use `kill -TERM $(pgrep -P 1)`  |
| `list_queues` shows no `celery` row | You read the default vhost                  | Pass `-p plane`                 |
| The task ran and the result is gone | `result_backend` is `None`                  | Read the effect in the database |
| The container came back on its own  | `restart: unless-stopped`                   | Expected. That is the restart.  |

## Related

- `docs/sops/drain-and-restart-celery-workers-sop.md` is the human procedure.
- `plane-env-var` explains why `restart` never applies an `env_file` change.
