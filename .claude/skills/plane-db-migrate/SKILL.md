---
name: plane-db-migrate
description: Author a Django migration for a model change in apps/api and read the SQL it will emit, without applying it. Use after changing a model in plane/db/models, or when you need to see what makemigrations would produce. Writes a migration file. Does not touch the database.
user_invocable: true
---

# Author a migration

Creates the file and shows the SQL. Applying it is `plane-db-upgrade`.

## Every command needs the settings flag

`apps/api/manage.py` line 10 defaults `DJANGO_SETTINGS_MODULE` to
`plane.settings.production`, and nothing in the compose file overrides it.
Without `--settings=plane.settings.local` you load production settings, which
pulls in `scout_apm` and sends errors to `plane/logs/plane-error.log` instead of
the console.

## Preview first

```bash
docker compose -f docker-compose-local.yml exec -T api \
  python manage.py makemigrations db --dry-run --settings=plane.settings.local
```

Writes nothing. With no model change it prints `No changes detected in app 'db'`.

## Write the file

```bash
docker compose -f docker-compose-local.yml exec -T api \
  python manage.py makemigrations db --settings=plane.settings.local
```

The file lands in `apps/api/plane/db/migrations`, which is bind-mounted, so it
appears on the host.

App labels that carry migrations here: `db` and `license`. The rest are Django's
own (`auth`, `contenttypes`, `sessions`, `django_celery_beat`, `debug_toolbar`).

## Read the SQL before anyone applies it

```bash
docker compose -f docker-compose-local.yml exec -T api \
  python manage.py sqlmigrate db 0123 --settings=plane.settings.local
```

Prints the statements between `BEGIN;` and `COMMIT;`. An operation that changes
nothing prints `-- (no-op)`.

## Write a reverse, or say plainly that you did not

This repository is nearly impossible to reverse, and every added migration makes
it worse. Measured across the 122 files in `plane/db/migrations`:

- 24 use `RunPython` with no `reverse_code` at all.
- 6 use `reverse_code=migrations.RunPython.noop`, so a reverse succeeds and
  restores nothing.
- 1 (`0106`) has a reverse function that raises `AttributeError`, because it
  calls `Page.DEFAULT_SORT_ORDER`, which the model no longer defines.
- 1 (`0107`) has a reverse that exists and runs.

If your migration moves data, write a real `reverse_code`. If you cannot, say so
in the migration's docstring so the next person does not discover it during an
incident.

Do not set `atomic = False` unless you need `AddIndexConcurrently`. `0103` and
`0111` do, and an interrupted run there leaves an `INVALID` index with no
rollback.

## Traps

| Symptom                                                | Cause                                                                                | Fix                                                  |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------ | ---------------------------------------------------- |
| `Conflicting migrations detected; multiple leaf nodes` | Your number collides with one already on `dev`                                       | Delete your file, rebase, run `makemigrations` again |
| `No changes detected` when you expected a migration    | The model is not in `INSTALLED_APPS`, or you edited a serializer rather than a model | Confirm the change is in `plane/db/models`           |
| Errors vanish into a log file                          | The settings flag is missing                                                         | Add `--settings=plane.settings.local`                |

## Related

- `plane-db-upgrade` applies it, with a snapshot first.
- `plane-db-downgrade` reverses it, and refuses below `0107`.
- `docs/sops/apply-database-migration-sop.md` is the human procedure.
