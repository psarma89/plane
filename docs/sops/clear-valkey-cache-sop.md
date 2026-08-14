# Clear Valkey Cache SOP

> **Last reviewed:** 2026-08-14
> **Owner role:** Operator
> **Risk:** Medium

## Purpose

Remove stale cached API responses from Valkey, and leave every rate limiter and lock intact.

## When to use

- **Trigger**: An endpoint returns stale data after a change, and the response is one of the 6 cached views.
- **Do not use this SOP when**: You want to invalidate one cached path. The application already does that. Read "The application invalidates its own cache" below.

## Read this before you run anything

`FLUSHDB` resets every rate limit in the product. The Django cache, the DRF throttle counters, two background-task keys, and the collaboration server all share **one Valkey database, db 0**. Nothing separates them.

The sign-in brute-force limiter is one of those counters. A measured run proved it:

| Requests to `/api/timezones/`, limit 10 per minute | Result            |
| -------------------------------------------------- | ----------------- |
| 1 to 10                                            | `200`             |
| 11, 12, 13                                         | `429`             |
| `FLUSHDB`                                          | `OK`              |
| The next 3, sent at once                           | **`200 200 200`** |

Treat a full flush as a security-relevant action. Prefer the targeted delete in the procedure.

## What lives in db 0

Measured on a running local stack.

| Key                                           | Owner                                                                    | TTL     | What a delete costs                                            |
| --------------------------------------------- | ------------------------------------------------------------------------ | ------- | -------------------------------------------------------------- |
| `:1:views.decorators.cache.*`                 | `cache_page` on `/api/timezones/`                                        | 2 hours | Nothing. The next request rebuilds it.                         |
| `:1:<request path>` and `:1:<path>:<user id>` | `cache_response` on 5 views                                              | 2 hours | Nothing. The next request rebuilds it.                         |
| `:1:throttle_anon_<ip>`                       | DRF `AnonRateThrottle`, 30 per minute                                    | 60s     | **The limit resets.**                                          |
| `:1:throttle_authentication_<ip>`             | `AuthenticationThrottle`, 10 per minute                                  | 60s     | **The sign-in brute-force limit resets.**                      |
| `:1:throttle_email_verification_<user>`       | `EmailVerificationThrottle`, 3 per hour                                  | 1 hour  | **The verification-code limit resets.**                        |
| `:1:api_key:<key>`                            | `ApiKeyRateThrottle`, 60 per minute                                      | 60s     | **The API key limit resets.**                                  |
| `<issue id>`, a bare UUID                     | `issue_activities_task.py:1531`, `ri.set(str(issue_id), origin, ex=600)` | 10 min  | The email notification for that issue is **silently skipped**. |
| `send_email_notif_<issue>_<receiver>_<ids>`   | `email_notification_task.py:157`, a lock                                 | 5 min   | A duplicate notification email becomes possible.               |
| `hocuspocus:<page id>:lock`                   | `@hocuspocus/extension-redis` 2.15.2, a redlock mutex                    | 1000ms  | Nothing measurable. The lock is held for one second.           |

The `:1:` prefix is `django_redis`. It writes `<KEY_PREFIX>:<VERSION>:<key>`, and this deployment sets no key prefix.

`AnonRateThrottle` and `AuthenticationThrottle` key shapes are measured. The other three are read from `plane/authentication/rate_limit.py` and `plane/api/rate_limit.py`.

## What a flush does not touch

Three things people expect to lose. None of them is in Valkey.

| Concern                | Where it really lives                    | Evidence                                               |
| ---------------------- | ---------------------------------------- | ------------------------------------------------------ |
| User sessions          | PostgreSQL, table `sessions`             | `SESSION_ENGINE = "plane.db.models.session"`           |
| Page and document text | PostgreSQL, through the Django API       | `apps/live/src/extensions/database.ts` fetch and store |
| Celery tasks           | RabbitMQ. Celery sets no result backend. | `CELERY_BROKER_URL` is `amqp://`                       |

A flush does not sign anyone out. A flush does not lose an unsaved edit. The collaboration server uses Valkey only as a pub/sub bus, on channels `hocuspocus:<page id>` and `hocuspocus:admin`.

## Prerequisites

| Item                | How to confirm                                                                  |
| ------------------- | ------------------------------------------------------------------------------- |
| The stack runs      | `docker compose -f docker-compose-local.yml ps` lists 8 containers              |
| Compose project set | `export COMPOSE_PROJECT_NAME=<your project>` if you run more than one stack     |
| Valkey answers      | `docker compose -f docker-compose-local.yml exec -T plane-redis redis-cli PING` |

## Procedure

1. Count the keys before you change anything.

   ```bash
   docker compose -f docker-compose-local.yml exec -T plane-redis redis-cli DBSIZE
   ```

   Expected result: an integer. A local stack with no traffic reports `0`.

2. List them. Use `--scan`, not `KEYS`.

   ```bash
   docker compose -f docker-compose-local.yml exec -T plane-redis redis-cli --scan --count 100
   ```

   Expected result: key names that match the table above. `KEYS *` blocks the server on a large database. `--scan` does not.

3. Delete only the cached responses.

   ```bash
   docker compose -f docker-compose-local.yml exec -T api python manage.py shell -c "
   from django.core.cache import cache
   for pattern in ('views.decorators.cache.*', '/api/*'):
       print(pattern, cache.delete_pattern(pattern))
   " --settings=plane.settings.local
   ```

   Expected result: one line per pattern with a count. A measured run printed `views.decorators.cache.* 2` and `/api/* 0`, and left the throttle keys, the lock, and the `hocuspocus` key in place.

   Write the pattern without the `:1:` prefix. `django_redis` adds the prefix itself.

4. Confirm the throttle keys survived.

   ```bash
   docker compose -f docker-compose-local.yml exec -T plane-redis redis-cli --scan | grep throttle
   ```

   Expected result: the throttle keys that existed before step 3. No output means either no request was throttled, or you flushed the whole database.

## Full flush, when a targeted delete cannot work

Use this only when the cache holds a value you cannot name, and only when you accept a rate-limit reset.

> **Destructive:** `FLUSHDB` resets every rate limit, including the sign-in brute-force limiter. It also drops the in-flight email notification lock, which allows a duplicate email. Do not run it against a production instance. Announce it first on a shared instance.

```bash
docker compose -f docker-compose-local.yml exec -T plane-redis redis-cli FLUSHDB
```

Expected result: `OK`. `DBSIZE` then reports `0`.

`FLUSHDB` and `FLUSHALL` do the same thing here. Only db 0 is ever used. `redis_instance()` passes `db=0`, and `REDIS_URL` carries no database number.

> **Destructive:** `cache.clear()` is not a Django-only operation. `django_redis` implements it as `FLUSHDB`. A measured run called `cache.clear()` against 5 keys and deleted all 5, including a raw `hocuspocus:` key and a `send_email_notif_` lock that Django never wrote. Treat `cache.clear()` and `FLUSHDB` as the same command.

## The application invalidates its own cache

Prefer this to any flush. `apps/api/plane/utils/cache.py` gives two helpers, and the views already use them.

| Helper                       | Use                                            |
| ---------------------------- | ---------------------------------------------- |
| `invalidate_cache(path=...)` | A decorator on the view that writes the data   |
| `invalidate_cache_directly`  | A direct call, for a path you build at runtime |

If a cached endpoint serves stale data after a write, the fix is a missing `invalidate_cache` decorator on the write view. A scheduled flush hides that defect.

## Verification

| Check                          | Command                                                                                               | Expected                 |
| ------------------------------ | ----------------------------------------------------------------------------------------------------- | ------------------------ |
| The cache entries are gone     | `... redis-cli --scan \| grep views.decorators`                                                       | No output                |
| The throttles survived         | `... redis-cli --scan \| grep throttle`                                                               | The keys from step 2     |
| The endpoint serves fresh data | `curl -s -o /dev/null -w '%{http_code}' http://localhost:${PLANE_HOST_API_PORT:-8000}/api/timezones/` | `200`                    |
| The cache repopulates          | `... redis-cli DBSIZE` after that request                                                             | Higher than after step 3 |
| Valkey is healthy              | `... redis-cli PING`                                                                                  | `PONG`                   |

## Rollback

A deleted cache entry cannot be restored. There is no rollback. Every entry rebuilds itself on the next request, so no recovery step is needed for the cache.

If you ran a full flush, the rate limits stay reset until the next window opens. Those windows are 60 seconds, except email verification, which is 1 hour.

1. Confirm the cache repopulates.

   ```bash
   curl -s -o /dev/null http://localhost:${PLANE_HOST_API_PORT:-8000}/api/timezones/
   docker compose -f docker-compose-local.yml exec -T plane-redis redis-cli DBSIZE
   ```

   Expected result: a number larger than `0`.

## Troubleshooting

| Failure                                              | Cause                                                                    | Fix                                                        |
| ---------------------------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------- |
| `docker compose restart plane-redis` cleared nothing | Valkey writes an RDB snapshot to the `redisdata` volume                  | Use step 3. A restart is not a flush.                      |
| A flush cleared more than you expected               | Everything shares db 0                                                   | Expected. Read "What lives in db 0".                       |
| `cache.delete_pattern` deleted `0` keys              | You included the `:1:` prefix in the pattern                             | Drop the prefix. `django_redis` adds it.                   |
| A cached endpoint never appears in the keyspace      | `cache_response` skips the write when `DEBUG` is true, and local sets it | Expected on a local stack. Only `cache_page` writes there. |
| Rate limits vanished after a cache clear             | `cache.clear()` runs `FLUSHDB`                                           | Use `cache.delete_pattern` instead                         |
| An email notification never arrived after a flush    | The bare-UUID origin key was deleted, so the task returned early         | Expected. The key expires in 600 seconds anyway.           |
| `KEYS *` hung the server                             | `KEYS` scans the whole keyspace in one blocking call                     | Use `--scan`                                               |

## Persistence

`plane-redis` runs `valkey/valkey:7.2.11-alpine` with the volume `redisdata:/data`. `save` is `3600 1 300 100 60 10000` and `appendonly` is `no`. Valkey writes a final snapshot on a clean shutdown.

A measured run set a key, ran `docker compose restart plane-redis`, and read the same value back. **Restarting the container does not clear the cache.** Only `docker compose down -v` removes the volume.

## Related

| Page                                                                                   | Why it matters here                                 |
| -------------------------------------------------------------------------------------- | --------------------------------------------------- |
| [`drain-and-restart-celery-workers-sop.md`](./drain-and-restart-celery-workers-sop.md) | The two background tasks that own keys in db 0      |
| [`add-environment-variable-sop.md`](./add-environment-variable-sop.md)                 | `REDIS_URL`, which every consumer reads             |
| [`local-development-setup-sop.md`](./local-development-setup-sop.md)                   | How `plane-redis` starts and where its volume lives |
