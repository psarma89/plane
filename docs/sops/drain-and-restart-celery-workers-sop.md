# Drain and Restart Celery Workers SOP

> **Last reviewed:** 2026-08-14
> **Owner role:** Operator
> **Risk:** Medium

## Purpose

Restart the Celery worker and the beat worker without loss of the tasks that run at that moment.

## When to use

- **Trigger**: You changed task code, you changed `apps/api/.env`, or the worker stopped consuming.
- **Do not use this SOP when**: You only changed a beat schedule. Restart `beat-worker` alone. Step 7 covers that case.

## Read this before you run anything

`docker compose restart worker` destroys every task that runs at that moment. The task is not retried. Two settings cause this, and neither is a mistake you can fix from the command line.

| Setting                      | Effective value | Source                                        |
| ---------------------------- | --------------- | --------------------------------------------- |
| `task_acks_late`             | `False`         | Celery default. The repository never sets it. |
| `worker_prefetch_multiplier` | `4`             | Celery default. The repository never sets it. |
| `task_time_limit`            | `None`          | Celery default. A task can run forever.       |
| `result_backend`             | `None`          | Absent. Every task result is discarded.       |

`task_acks_late = False` means the broker acknowledges a message when the worker hands it to a pool process. The message leaves RabbitMQ before the task runs. If the process dies, nothing remains to redeliver.

Read the effective values on your own stack:

```bash
docker compose -f docker-compose-local.yml exec -T api python -c \
  "from plane.celery import app; print(app.conf.task_acks_late, app.conf.worker_prefetch_multiplier, app.conf.result_backend)"
```

Expected result: `False 4 None`.

## What a hard restart costs, measured

A measured run enqueued 20 tasks of 45 seconds each against a worker with concurrency 15.

| Stage                        | Result                                             |
| ---------------------------- | -------------------------------------------------- |
| After the enqueue            | 15 tasks executing, 5 messages unacknowledged      |
| `docker compose stop worker` | Returned after 11 seconds, container exit code 137 |
| Tasks lost                   | **15. They never ran again.**                      |
| Tasks recovered              | 5. RabbitMQ requeued the unacknowledged messages.  |

Exit code 137 is `128 + 9`, which means SIGKILL. Docker Compose sends SIGTERM, waits for the grace period, then sends SIGKILL. No service in `docker-compose-local.yml` declares `stop_grace_period`, so the grace period is the Docker Compose default of 10 seconds.

## The worker never receives SIGTERM

A longer grace period does not help. A second measured run used `docker compose stop -t 90 worker`. The command returned after 91 seconds and the container still exited 137. The worker log contained no shutdown line.

The cause is the entrypoint:

```bash
# apps/api/bin/docker-entrypoint-worker.sh, last line
celery -A plane worker -l info
```

The line has no `exec`. Bash stays as PID 1 and Celery runs as a child. Bash defers a signal while it waits for a foreground child, so Celery never sees the SIGTERM that Docker sends to PID 1. Confirm this on your own stack:

```bash
docker compose -f docker-compose-local.yml exec -T worker ps -eo pid,ppid,args | head -3
```

Expected result: PID 1 is `/bin/bash ./bin/docker-entrypoint-worker.sh`. Celery is a child.

`apps/api/bin/docker-entrypoint-api.sh` uses `exec`. The worker and the beat entrypoints do not.

## Prerequisites

Complete every item before step 1.

| Item                | How to confirm                                                                                                                |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| The stack runs      | `docker compose -f docker-compose-local.yml ps` lists 8 containers                                                            |
| You know the queue  | `docker compose -f docker-compose-local.yml exec -T api python -c "from plane.celery import app; print(app.conf.broker_url)"` |
| Compose project set | `export COMPOSE_PROJECT_NAME=<your project>` if you run more than one stack                                                   |

## Procedure

1. List the tasks that run now.

   ```bash
   docker compose -f docker-compose-local.yml exec -T worker \
     celery -A plane inspect active
   ```

   Expected result: `- empty -` when the worker is idle. A list of task names when it is busy.

2. Read the queue depth.

   ```bash
   docker compose -f docker-compose-local.yml exec -T plane-mq \
     rabbitmqctl list_queues -p plane name messages_ready messages_unacknowledged
   ```

   Expected result: a `celery` row. `messages_unacknowledged` counts the messages the worker holds in its prefetch buffer.

3. Stop the worker from accepting new tasks, and let the running tasks finish.

   ```bash
   docker compose -f docker-compose-local.yml exec -T worker \
     bash -c 'kill -TERM $(pgrep -P 1)'
   ```

   Expected result: the command returns at once. The worker log prints `worker: Warm shutdown (MainProcess)`.

   `pgrep -P 1` selects the one child of PID 1, which is the Celery MainProcess.

> **Destructive:** Do not use `pkill -TERM -f celery`. Every pool child shares the MainProcess command line, so that pattern signals all 15 children and kills the running tasks. A measured run lost all 3 in-flight tasks that way.

4. Wait for the container to exit and return.

   ```bash
   docker compose -f docker-compose-local.yml exec -T worker \
     celery -A plane inspect active
   ```

   Expected result: `1 node online.` again, with a new container ID. The wait equals the longest running task.

   The `worker` service declares `restart: unless-stopped`. Celery exits 0 after the drain, and Docker starts the container again. One command drains and restarts.

5. Confirm the drain lost nothing.

   ```bash
   docker compose -f docker-compose-local.yml logs worker --since 10m | grep -c "Warm shutdown"
   ```

   Expected result: `1` or more. A count of `0` means the tasks died under SIGKILL.

   The restart policy reuses the same container, so the log survives the drain.

6. Confirm the worker registered its tasks.

   ```bash
   docker compose -f docker-compose-local.yml exec -T worker \
     celery -A plane inspect registered | grep -c "plane\."
   ```

   Expected result: `46` on `dev`.

7. Restart the beat worker, if the schedule changed.

   ```bash
   docker compose -f docker-compose-local.yml restart beat-worker
   ```

   Expected result: the log prints `DatabaseScheduler: Schedule changed.`

   A hard restart of `beat-worker` is safe. Beat runs no task itself. It only sends messages. `django_celery_beat.schedulers.DatabaseScheduler` keeps `last_run_at` in PostgreSQL, so the state survives the kill. Beat does not catch up. A window that closes during the restart is skipped until the next window.

## Verification

| Check                     | Command                                                                                                                                                               | Expected         |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| The worker consumes again | `... exec -T worker celery -A plane inspect active`                                                                                                                   | `1 node online.` |
| The drain was warm        | `... logs worker --since 10m \| grep -c "Warm shutdown"`                                                                                                              | `1` or more      |
| The queue drains          | `... exec -T plane-mq rabbitmqctl list_queues -p plane name messages_ready`                                                                                           | `celery 0`       |
| Tasks are registered      | `... exec -T worker celery -A plane inspect registered \| grep -c "plane\."`                                                                                          | `46`             |
| Beat holds its schedule   | `... exec -T api python manage.py shell -c "from django_celery_beat.models import PeriodicTask; print(PeriodicTask.objects.count())" --settings=plane.settings.local` | `13`             |

## Rollback

A drained task cannot be un-drained. There is no rollback. Use the recovery path.

1. Find the tasks that the restart lost. Read the worker log from before the restart.

   ```bash
   docker compose -f docker-compose-local.yml logs worker --since 30m | grep "Task .* received"
   ```

2. Enqueue each lost task again by hand.

   ```bash
   docker compose -f docker-compose-local.yml exec -T api python manage.py shell -c \
     "from plane.bgtasks.cleanup_task import delete_api_logs; delete_api_logs.delay()" \
     --settings=plane.settings.local
   ```

3. Start the worker again, if the container did not return.

   ```bash
   docker compose -f docker-compose-local.yml up -d worker
   ```

## The permanent fix, verified but not applied

Two lines remove the need for step 3. This repository does not carry them yet.

| File                                         | Change                           |
| -------------------------------------------- | -------------------------------- |
| `apps/api/bin/docker-entrypoint-worker.sh`   | Prefix the last line with `exec` |
| `docker-compose-local.yml`, service `worker` | Add `stop_grace_period: 120s`    |

A measured run applied both, then ran `docker compose restart worker` against one 45-second task. The command took 43 seconds and the task finished. Without the two lines the same command took 11 seconds and the task died.

Apply the same two lines to `beat-worker` for consistency.

## Troubleshooting

| Failure                                         | Cause                                                          | Fix                                                                       |
| ----------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Container exit code 137                         | SIGKILL after the 10 second grace period                       | Use step 3, not `restart` or `stop`                                       |
| `docker compose stop -t 90` still exits 137     | Bash is PID 1 and never forwards the signal                    | Use step 3. Read "The worker never receives SIGTERM".                     |
| The drain killed the tasks anyway               | You used `pkill -f celery`, which matched all 15 pool children | Use `kill -TERM $(pgrep -P 1)`                                            |
| `Received unregistered task of type '...'`      | Nothing on the worker imports the task module                  | Add the module to `CELERY_IMPORTS` in `apps/api/plane/settings/common.py` |
| The task ran once and the result is gone        | `result_backend` is `None`, so results are discarded           | Expected. Read the effect in the database, not from `AsyncResult`.        |
| `rabbitmqctl list_queues` shows no `celery` row | You read the default vhost                                     | Pass `-p plane`. The broker URL ends in `/plane`.                         |
| The container restarts by itself after a drain  | The service declares `restart: unless-stopped`                 | Expected. That is how step 3 restarts the worker.                         |

## Known defects on dev

Each row is real on `dev` at the time of the last review. None is fixed here.

| Defect                                                                                               | Effect                                                                          |
| ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `docker-entrypoint-worker.sh` and `docker-entrypoint-beat.sh` do not use `exec`                      | Docker cannot stop either process cleanly                                       |
| `apps/api/plane/app/views/project/invite.py:108` calls `.delay()` on a list, not on the task         | A project invitation raises `AttributeError`. The invitation email never sends. |
| `plane.bgtasks.project_invitation_task.project_invitation` is the one declared task never registered | The same defect. Nothing imports the module.                                    |
| `apps/api/plane/celery.py` schedules `delete_old_s3_link` twice, at 01:30 and at 03:45               | The task runs twice a day. The two entry names differ by one character.         |

Confirm the registration gap yourself:

```bash
docker compose -f docker-compose-local.yml exec -T worker \
  celery -A plane inspect registered | grep -c "plane\."
```

Expected result: `46`. The repository declares 47 tasks.

## Related

| Page                                                                   | Why it matters here                                         |
| ---------------------------------------------------------------------- | ----------------------------------------------------------- |
| [`add-environment-variable-sop.md`](./add-environment-variable-sop.md) | Why `restart` never applies an `env_file` change            |
| [`local-development-setup-sop.md`](./local-development-setup-sop.md)   | How the worker and the beat worker start in the first place |
| [`apply-database-migration-sop.md`](./apply-database-migration-sop.md) | The beat schedule that lives in PostgreSQL                  |
