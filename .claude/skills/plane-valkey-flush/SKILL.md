---
name: plane-valkey-flush
description: Clear stale cached API responses from Plane's Valkey instance without resetting the rate limiters. Use when an endpoint serves stale data, when you need to know what shares the Valkey database, or before anyone runs FLUSHDB. Explains why FLUSHDB resets the sign-in brute-force limiter and why cache.clear() is the same command.
user_invocable: true
---

# Clear the Valkey cache safely

`FLUSHDB` resets every rate limit in the product, including the sign-in
brute-force limiter. Use the targeted delete instead.

## The safe command

```bash
docker compose -f docker-compose-local.yml exec -T api python manage.py shell -c "
from django.core.cache import cache
for pattern in ('views.decorators.cache.*', '/api/*'):
    print(pattern, cache.delete_pattern(pattern))
" --settings=plane.settings.local
```

Write the pattern **without** the `:1:` prefix. `django_redis` adds it.

Measured: this deleted the 2 view-cache keys and left the throttle key, the
email lock, and the `hocuspocus` key untouched.

## Everything shares db 0

| Key                                         | Owner                                    | Delete costs                        |
| ------------------------------------------- | ---------------------------------------- | ----------------------------------- |
| `:1:views.decorators.cache.*`               | `cache_page`, 1 view                     | Nothing. Rebuilt on next request.   |
| `:1:<path>` / `:1:<path>:<user id>`         | `cache_response`, 5 views                | Nothing. Rebuilt on next request.   |
| `:1:throttle_anon_<ip>`                     | 30/minute                                | **Limit resets**                    |
| `:1:throttle_authentication_<ip>`           | 10/minute, sign-in brute force           | **Limit resets**                    |
| `:1:throttle_email_verification_<user>`     | 3/hour                                   | **Limit resets**                    |
| `:1:api_key:<key>`                          | 60/minute                                | **Limit resets**                    |
| `<issue id>` bare UUID, `ex=600`            | `issue_activities_task.py:1531`          | Email notification silently skipped |
| `send_email_notif_<issue>_<receiver>_<ids>` | `email_notification_task.py:157`, a lock | Duplicate email becomes possible    |
| `hocuspocus:<page id>:lock`                 | redlock mutex, 1000ms                    | Nothing measurable                  |

## Proof that a flush resets the limiter

13 requests to `/api/timezones/`, which allows 10 per minute:

```
1-10: 200    11,12,13: 429    FLUSHDB: OK    next 3: 200 200 200
```

Treat a full flush as a security-relevant action.

## cache.clear() is FLUSHDB

`django_redis` implements `clear()` as `FLUSHDB`. A measured run called
`cache.clear()` against 5 keys and deleted all 5, including a raw
`hocuspocus:` key and a `send_email_notif_` lock that Django never wrote.

Never reach for `cache.clear()` when you mean "drop the cached responses".

## A flush does not touch these

| Concern      | Actually lives in                                      |
| ------------ | ------------------------------------------------------ |
| Sessions     | PostgreSQL, table `sessions`. Nobody is signed out.    |
| Page content | PostgreSQL, via `apps/live/src/extensions/database.ts` |
| Celery tasks | RabbitMQ. No result backend is configured.             |

`apps/live` uses Valkey only as a pub/sub bus, on `hocuspocus:<page id>` and
`hocuspocus:admin`. Document state is never stored there.

## Prefer the built-in invalidation

`apps/api/plane/utils/cache.py` provides `invalidate_cache` (a view decorator)
and `invalidate_cache_directly`. Stale data after a write means a missing
`invalidate_cache` decorator on the write view. A flush hides that defect.

## Traps

| Symptom                               | Cause                                                 | Fix                                 |
| ------------------------------------- | ----------------------------------------------------- | ----------------------------------- |
| `restart plane-redis` cleared nothing | RDB snapshot on the `redisdata` volume                | Use the targeted delete             |
| `delete_pattern` deleted 0 keys       | You included `:1:` in the pattern                     | Drop the prefix                     |
| No cached key ever appears locally    | `cache_response` skips the write when `DEBUG` is true | Expected. Only `cache_page` writes. |
| Rate limits vanished                  | Someone ran `cache.clear()` or `FLUSHDB`              | Wait for the window, 60s or 1h      |
| `KEYS *` hung the server              | `KEYS` blocks on the whole keyspace                   | Use `redis-cli --scan`              |

## Inspect

```bash
docker compose -f docker-compose-local.yml exec -T plane-redis redis-cli DBSIZE
docker compose -f docker-compose-local.yml exec -T plane-redis redis-cli --scan --count 100
```

Only db 0 is ever used. `redis_instance()` passes `db=0`, and `REDIS_URL`
carries no database number, so `FLUSHDB` and `FLUSHALL` are the same command.

## Related

- `docs/sops/clear-valkey-cache-sop.md` is the human procedure.
- `plane-celery-restart` covers the two background tasks that own keys here.
