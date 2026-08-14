---
name: plane-db-upgrade
description: Apply pending Django migrations to the running local stack, after taking a snapshot. Use when migrations are pending, when the API is stuck waiting on migrations, or after pulling a branch that added one. Writes to the database, so it snapshots first.
user_invocable: true
---

# Apply migrations

Snapshot, apply, verify. In that order.

## 1. Snapshot

Never skip this. Reversal barely works in this repository, so the dump is the
real rollback.

```bash
docker compose -f docker-compose-local.yml exec -T plane-db \
  pg_dump -U plane -d plane -Fc > plane-$(date +%Y%m%d-%H%M%S).dump
```

Exit 0, about 900 KB for a seeded database. No `PGPASSWORD` is needed: the
command runs inside the container and connects over the local socket.

## 2. See what will run

```bash
docker compose -f docker-compose-local.yml exec -T api \
  python manage.py migrate db --plan --settings=plane.settings.local
```

## 3. Apply

```bash
docker compose -f docker-compose-local.yml exec -T api \
  python manage.py migrate db --settings=plane.settings.local
```

One `Applying db.<name>... OK` per pending migration.

`--settings=plane.settings.local` is required on every `manage.py` call.
`manage.py` line 10 defaults to `plane.settings.production`.

## 4. Verify

```bash
docker compose -f docker-compose-local.yml exec -T api \
  python manage.py showmigrations db --settings=plane.settings.local
```

Every line reads `[X]`. Then confirm the data, because a healthy migration table
does not prove the rows survived:

```bash
docker compose -f docker-compose-local.yml exec -T api python manage.py shell -c \
  "from plane.db.models import Issue, Page, Project
print(Issue.objects.count(), Page.objects.count(), Project.objects.count())" \
  --settings=plane.settings.local
```

## Never interrupt 0103 or 0111

Both set `atomic = False` so they can run `AddIndexConcurrently`. PostgreSQL
cannot roll those back. An interrupt leaves an `INVALID` index behind, and the
next run fails with `relation already exists`. Drop the invalid index in `psql`
before retrying.

## Traps

| Symptom                                                               | Cause                                                                                | Fix                                                                     |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| The API logs `Waiting for database migrations to complete...` forever | The migrator container exited before applying. Its entrypoint polls with no timeout. | Run step 3, or `docker compose -f docker-compose-local.yml up migrator` |
| `env file .../apps/api/.env not found`                                | `setup.sh` has not run in this checkout                                              | `./setup.sh` from the repository root                                   |
| Errors land in `plane/logs/plane-error.log`                           | The settings flag is missing, so production settings loaded                          | Add `--settings=plane.settings.local`                                   |
| `relation already exists`                                             | An interrupted `0103` or `0111` left an `INVALID` index                              | Drop it in `psql`, then migrate again                                   |

## Related

- `plane-db-downgrade` reverses, and refuses below `0107`.
- `plane-db-migrate` authors a new migration.
- `docs/sops/apply-database-migration-sop.md` is the human procedure, risk High.
