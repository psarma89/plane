---
name: plane-db-downgrade
description: Reverse Django migrations on the running local stack, and know which targets are unreachable. Use when you need to move the database back to an earlier migration, or when a reversal already failed and left the migration state torn. Refuses any target below db 0107, because reversing lower corrupts the database.
user_invocable: true
---

# Reverse migrations

Reversal mostly does not work here. Read the floor before you run anything.

## The floor is 0107

Measured by parsing all 122 files in `apps/api/plane/db/migrations` with Python's
`ast` module, and confirmed by a live reversal attempt.

| Range                                          | What a reverse does                                                                                                         |
| ---------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `0035` to `0077`, 24 files                     | No `reverse_code`. Django raises `IrreversibleError`.                                                                       |
| `0079`, `0094`, `0112`, `0113`, `0115`, `0118` | `reverse_code=RunPython.noop`. **Succeeds and restores nothing.** The migration table looks healthy while the data is gone. |
| `0106`                                         | Reverse function exists and is broken. Raises `AttributeError`.                                                             |
| `0107`                                         | The only reverse below `0122` that exists and runs.                                                                         |

**Never target below `0107`.** A reversal aimed lower does not stop cleanly at
`0077`. It crashes partway:

```
File "/code/plane/db/migrations/0106_auto_20250912_0845.py", line 38,
  in reverse_set_page_sort_order
    Page.objects.update(sort_order=Page.DEFAULT_SORT_ORDER)
AttributeError: type object 'Page' has no attribute 'DEFAULT_SORT_ORDER'
```

A measured attempt left the database at **106 applied, 16 unapplied**.

To reach anything below `0107`, restore a snapshot. Do not reverse.

## Reversing, when the target is 0107 or higher

1. Snapshot. This is the real rollback.

   ```bash
   docker compose -f docker-compose-local.yml exec -T plane-db \
     pg_dump -U plane -d plane -Fc > plane-$(date +%Y%m%d-%H%M%S).dump
   ```

2. Read the plan.

   ```bash
   docker compose -f docker-compose-local.yml exec -T api \
     python manage.py migrate db 0121 --plan --settings=plane.settings.local
   ```

3. Reverse.

   ```bash
   docker compose -f docker-compose-local.yml exec -T api \
     python manage.py migrate db 0121 --settings=plane.settings.local
   ```

   Expect `Unapplying db.0122_... OK`.

4. Check the data, not just the migration table.

   ```bash
   docker compose -f docker-compose-local.yml exec -T api python manage.py shell -c \
     "from plane.db.models import Issue; print(Issue.objects.count())" \
     --settings=plane.settings.local
   ```

   If the reverse crossed one of the six no-op migrations, this count or a
   column value is the only way to notice the loss.

## Recovering from a torn state

Both paths below were run against a database torn by a failed reversal.

**First, migrate forward.**

```bash
docker compose -f docker-compose-local.yml exec -T api \
  python manage.py migrate db --settings=plane.settings.local
```

In the measured run this went from 106 applied back to 122, and the seeded rows
were unchanged at 44 issues, 8 pages, 2 projects. This restores the schema. It
restores data only where the forward function can recompute it.

**Then, if the data is wrong, restore the snapshot.**

```bash
docker compose -f docker-compose-local.yml exec -T plane-db \
  pg_restore -U plane -d plane --clean --if-exists < plane-YYYYMMDD-HHMMSS.dump
```

Exit 0 and no error lines. A measured restore returned 122 applied and the same
44 issues, 8 pages, 2 projects.

## Traps

| Symptom                                                            | Cause                                     | Fix                                                |
| ------------------------------------------------------------------ | ----------------------------------------- | -------------------------------------------------- |
| `AttributeError: ... 'Page' has no attribute 'DEFAULT_SORT_ORDER'` | Target was below `0107`                   | Migrate forward, then restore a snapshot           |
| `IrreversibleError`                                                | Target at or below `0077`                 | Restore a snapshot. That range cannot be reversed. |
| Reverse succeeded, data unchanged or empty                         | One of the six no-op reverses             | Restore the snapshot                               |
| Errors go to a log file instead of the console                     | Missing `--settings=plane.settings.local` | Add it to every `manage.py` call                   |

## Related

- `plane-db-upgrade` applies migrations.
- `plane-db-migrate` authors one, and explains why writing a real `reverse_code` matters.
- `docs/sops/apply-database-migration-sop.md` is the human procedure, risk High.
