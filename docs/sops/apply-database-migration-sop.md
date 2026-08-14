# Apply Database Migration SOP

> **Last reviewed:** 2026-08-13
> **Owner role:** Contributor
> **Risk:** High
> **Approval:** A second contributor must confirm the snapshot from step 1 exists before you run step 4. A reversal needs the same confirmation.

## Purpose

Author, preview, apply, and reverse a Django migration against the running local stack, without losing data.

## When to use

- **Trigger**: You changed a model in `apps/api/plane/db/models`, or you need to move a running local stack to a different migration.
- **Do not use this SOP when**: You only want to run the tests. `pytest.ini` sets `--nomigrations`, so the suite never executes a migration. Read [`run-backend-tests-sop.md`](./run-backend-tests-sop.md).

This SOP covers the local Docker stack only. It makes no claim about a deployed instance.

## Read this before you reverse anything

Reversal is not generally available in this repository. The measurements below come from `apps/api/plane/db/migrations`, parsed with Python's `ast` module, and from a live reversal attempt.

| Range                                          | Behaviour on reverse                                                                                                                                  |
| ---------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `0035` to `0077`, 24 files                     | `RunPython` with no `reverse_code`. Django raises `IrreversibleError`.                                                                                |
| `0079`, `0094`, `0112`, `0113`, `0115`, `0118` | `reverse_code=migrations.RunPython.noop`. The reverse **succeeds and restores nothing**. This is the dangerous case, because it looks like it worked. |
| `0106`                                         | Has a reverse function, and that function is **broken**. See below.                                                                                   |
| `0107`                                         | The only migration below `0122` with a reverse that both exists and runs.                                                                             |

**The practical floor is `0107`, not `0077`.** A reversal aimed lower does not stop cleanly at `0077`. It crashes at `0106`:

```
File "/code/plane/db/migrations/0106_auto_20250912_0845.py", line 38,
  in reverse_set_page_sort_order
    Page.objects.update(sort_order=Page.DEFAULT_SORT_ORDER)
AttributeError: type object 'Page' has no attribute 'DEFAULT_SORT_ORDER'
```

That crash leaves the database torn. A measured run left **106 applied and 16 unapplied**.

> **Destructive:** Never reverse below `db 0107`. Restore a snapshot instead.

## Prerequisites

| Item                      | How to confirm                                                                       |
| ------------------------- | ------------------------------------------------------------------------------------ |
| The stack is running      | `docker compose -f docker-compose-local.yml ps` shows 7 services up                  |
| You know the current head | `... exec -T api python manage.py showmigrations db --settings=plane.settings.local` |
| Disk for a snapshot       | A seeded database dumps to about 900 KB                                              |

Every `manage.py` command needs `--settings=plane.settings.local`. `apps/api/manage.py` line 10 defaults `DJANGO_SETTINGS_MODULE` to `plane.settings.production`, and nothing in the compose file overrides it.

## Procedure

1. Snapshot the database. Do this before every apply and every reverse.

   ```bash
   docker compose -f docker-compose-local.yml exec -T plane-db \
     pg_dump -U plane -d plane -Fc > plane-$(date +%Y%m%d-%H%M%S).dump
   ```

   Expected result: Exit code 0, and a file of about 900 KB. No `PGPASSWORD` is needed, because the container connects over the local socket.

2. Author the migration for your model change.

   ```bash
   docker compose -f docker-compose-local.yml exec -T api \
     python manage.py makemigrations db --settings=plane.settings.local
   ```

   Expected result: A new file under `apps/api/plane/db/migrations`. To see the plan without writing the file, add `--dry-run`. With no model change, the command prints `No changes detected in app 'db'`.

3. Read the SQL before you run it.

   ```bash
   docker compose -f docker-compose-local.yml exec -T api \
     python manage.py sqlmigrate db 0123 --settings=plane.settings.local
   ```

   Expected result: The statements between `BEGIN;` and `COMMIT;`. An operation that changes nothing prints `-- (no-op)`.

> **Destructive:** Step 4 writes to the database. Confirm the snapshot from step 1 exists first.

4. Apply.

   ```bash
   docker compose -f docker-compose-local.yml exec -T api \
     python manage.py migrate db --settings=plane.settings.local
   ```

   Expected result: One `Applying db.<name>... OK` line per pending migration.

5. Confirm the head moved.

   ```bash
   docker compose -f docker-compose-local.yml exec -T api \
     python manage.py showmigrations db --settings=plane.settings.local
   ```

   Expected result: Every line reads `[X]`.

## Reversing

Only to `0107` or higher. Snapshot first.

```bash
docker compose -f docker-compose-local.yml exec -T api \
  python manage.py migrate db 0121 --settings=plane.settings.local
```

Expected result: `Unapplying db.0122_...  OK`, and `showmigrations` then reads `[ ]` for `0122`.

To see the plan first, without executing:

```bash
docker compose -f docker-compose-local.yml exec -T api \
  python manage.py migrate db 0121 --plan --settings=plane.settings.local
```

## Verification

| Check                        | Command                                                                          | Expected                                             |
| ---------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------- |
| The head is where you wanted | `... showmigrations db ...`                                                      | The target reads `[X]`, everything after reads `[ ]` |
| Nothing is pending           | `... migrate db --plan ...`                                                      | `No planned migration operations`                    |
| The data is still there      | `... shell -c "from plane.db.models import Issue; print(Issue.objects.count())"` | The count you had before                             |

Do not treat a clean `showmigrations` as proof that the data survived. The six no-op reverses leave the migration table healthy while restoring nothing.

## Rollback

Both paths below were executed against a torn database and both worked.

**Path 1, migrate forward.** Try this first after a failed reversal.

```bash
docker compose -f docker-compose-local.yml exec -T api \
  python manage.py migrate db --settings=plane.settings.local
```

In the measured run this took the state from 106 applied back to 122 applied, and the seeded row counts were unchanged: 44 issues, 8 pages, 2 projects.

This recovers the schema. It recovers data only where the forward function can recompute it. Where a no-op reverse discarded a computed column, a forward run recomputes it only if the source data still exists.

**Path 2, restore the snapshot.** Use this when path 1 leaves wrong data.

```bash
docker compose -f docker-compose-local.yml exec -T plane-db \
  pg_restore -U plane -d plane --clean --if-exists < plane-YYYYMMDD-HHMMSS.dump
```

Expected result: Exit code 0 and no error lines. A measured restore returned 122 applied migrations and 44 issues, 8 pages, 2 projects.

## Troubleshooting

| Failure                                                                                 | Cause                                                                                                                        | Fix                                                                              |
| --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `AttributeError: type object 'Page' has no attribute 'DEFAULT_SORT_ORDER'`              | You aimed a reversal below `0107`, and `0106`'s reverse function is broken                                                   | Migrate forward to recover, then use a snapshot instead                          |
| `IrreversibleError`                                                                     | The target is at or below `0077`, where 24 migrations have no `reverse_code`                                                 | Restore a snapshot. That range cannot be reversed.                               |
| The reverse succeeded but the data is unchanged or empty                                | The migration uses `reverse_code=migrations.RunPython.noop`                                                                  | Restore the snapshot. Six migrations behave this way.                            |
| `relation already exists` after an interrupted migrate                                  | `0103` and `0111` set `atomic = False` for `AddIndexConcurrently`, so an interrupt leaves an `INVALID` index and no rollback | Drop the invalid index in `psql`, then migrate again. Never interrupt those two. |
| The API logs `Waiting for database migrations to complete...` forever                   | The migrator exited before applying, and the API entrypoint polls with no timeout                                            | Run step 4, or `docker compose -f docker-compose-local.yml up migrator`          |
| `scout_apm` loads, and errors go to `plane/logs/plane-error.log` instead of the console | You omitted `--settings=plane.settings.local`, so Django used production settings                                            | Add the flag to every `manage.py` command                                        |
| `Conflicting migrations detected; multiple leaf nodes`                                  | Your local `makemigrations` picked a number that `dev` also used                                                             | Delete your local file, rebase on `dev`, run `makemigrations` again              |

## Related

| Page                                                                 | Why it matters here                                                         |
| -------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| [`run-backend-tests-sop.md`](./run-backend-tests-sop.md)             | The suite runs with `--nomigrations`, so it cannot catch a broken migration |
| [`local-development-setup-sop.md`](./local-development-setup-sop.md) | How the migrator container applies migrations at stack start                |
