# Plane patterns census

> **Last reviewed:** 2026-08-14

This page is the one home for every measured pattern count. The instruction files state the rules and link here. A rule survives a refactor. A count does not, so no count lives in an `AGENTS.md`.

Each row carries the command that produced its value. Run the command from the repo root to re-measure. `bin/check-counts` re-measures every row and fails when this page no longer quotes what the repository contains. A count that moved is a documentation edit, not a defect. Update the value, not the code.

Two row types exist.

- A **measured** count describes the repository. The repository wins, and this page must follow it.
- A **pinned** value is a ratchet. It must never rise. `bin/check-counts` fails when the source file moves off the pin.

## Tenant scoping in `apps/api/plane/app/views/`

The scope is hand-written per view. These counts show that the convention is pervasive, so an unscoped view is an omission.

| Pattern                               | Count | Command                                                                 |
| ------------------------------------- | ----- | ----------------------------------------------------------------------- |
| `workspace__slug` filters             | 438   | `grep -rho 'workspace__slug' apps/api/plane/app/views \| wc -l`         |
| Files with a `workspace__slug` filter | 51    | `grep -rl 'workspace__slug' apps/api/plane/app/views \| wc -l`          |
| Lines with a `project_id=` filter     | 374   | `grep -rh 'project_id=' apps/api/plane/app/views \| wc -l`              |
| Files with a `project_id=` filter     | 33    | `grep -rl 'project_id=' apps/api/plane/app/views \| wc -l`              |
| `self.kwargs.get("slug")` reads       | 54    | `grep -rho 'self.kwargs.get("slug")' apps/api/plane/app/views \| wc -l` |

## Authorization in `apps/api/plane/app/views/`

The decorator dominates, which is why `apps/api/AGENTS.md` prefers it for new code.

| Pattern                         | Count | Command                                                            |
| ------------------------------- | ----- | ------------------------------------------------------------------ |
| `@allow_permission` uses        | 196   | `grep -rho '@allow_permission' apps/api/plane/app/views \| wc -l`  |
| Files with `@allow_permission`  | 38    | `grep -rl '@allow_permission' apps/api/plane/app/views \| wc -l`   |
| `permission_classes` uses       | 43    | `grep -rho 'permission_classes' apps/api/plane/app/views \| wc -l` |
| Files with `permission_classes` | 31    | `grep -rl 'permission_classes' apps/api/plane/app/views \| wc -l`  |

## Serializers and writes in `apps/api/plane/`

The first three rows quantify the over-exposure risk that `fields = "__all__"` carries. The rest quantify the write patterns.

| Pattern                                       | Count | Command                                                                  |
| --------------------------------------------- | ----- | ------------------------------------------------------------------------ |
| `fields = "__all__"` uses                     | 96    | `grep -rho 'fields = "__all__"' apps/api/plane \| wc -l`                 |
| Files with `fields = "__all__"`               | 34    | `grep -rl 'fields = "__all__"' apps/api/plane \| wc -l`                  |
| Of those uses, under `plane/app/serializers/` | 60    | `grep -rho 'fields = "__all__"' apps/api/plane/app/serializers \| wc -l` |
| `bulk_create(` calls                          | 98    | `grep -rho 'bulk_create(' apps/api/plane \| wc -l`                       |
| `.delay(` Celery dispatches                   | 173   | `grep -rho '\.delay(' apps/api/plane \| wc -l`                           |
| `transaction.atomic` usages                   | 16    | `grep -rho 'transaction\.atomic' apps/api/plane \| wc -l`                |
| `select_related` uses                         | 216   | `grep -rho 'select_related' apps/api/plane \| wc -l`                     |
| `prefetch_related` uses                       | 91    | `grep -rho 'prefetch_related' apps/api/plane \| wc -l`                   |

The `transaction.atomic` command greps the full phrase. A bare `atomic` also matches `atomic = False` migration flags, which inflates the count.

## Model base classes in `apps/api/plane/db/models/`

`CONTEXT.md` explains what the three base classes mean.

| Base class           | Subclasses | Command                                                                              |
| -------------------- | ---------- | ------------------------------------------------------------------------------------ |
| `ProjectBaseModel`   | 41         | `grep -rhoE 'class [A-Za-z]+\(ProjectBaseModel' apps/api/plane/db/models \| wc -l`   |
| `WorkspaceBaseModel` | 13         | `grep -rhoE 'class [A-Za-z]+\(WorkspaceBaseModel' apps/api/plane/db/models \| wc -l` |
| `BaseModel`          | 32         | `grep -rhoE 'class [A-Za-z]+\(BaseModel' apps/api/plane/db/models \| wc -l`          |

## Frontend patterns in `apps/web/`

Each command scans only `.ts` and `.tsx` files.

| Pattern                   | Count | Command                                                                            |
| ------------------------- | ----- | ---------------------------------------------------------------------------------- |
| `observer(` wrappers      | 919   | `grep -rho 'observer(' --include='*.ts' --include='*.tsx' apps/web \| wc -l`       |
| `@/services` imports      | 195   | `grep -rho '@/services' --include='*.ts' --include='*.tsx' apps/web \| wc -l`      |
| `@plane/services` imports | 6     | `grep -rho '@plane/services' --include='*.ts' --include='*.tsx' apps/web \| wc -l` |
| `text-secondary` uses     | 613   | `grep -rho 'text-secondary' --include='*.ts' --include='*.tsx' apps/web \| wc -l`  |

## Lint ceilings and real warning counts

The ceilings are **pinned**. They are ratchets and must never rise. Each value is copied character for character from the `check:lint` script in the named `package.json`.

| App          | Ceiling (pinned) | Source                                                  |
| ------------ | ---------------- | ------------------------------------------------------- |
| `apps/web`   | 11957            | `grep -o 'max-warnings=[0-9]*' apps/web/package.json`   |
| `apps/admin` | 759              | `grep -o 'max-warnings=[0-9]*' apps/admin/package.json` |
| `apps/space` | 676              | `grep -o 'max-warnings=[0-9]*' apps/space/package.json` |

The warning counts are **measured**. The gap between a ceiling and its count is headroom, so a green repo-wide lint run proves nothing. These commands need `pnpm install` first.

| App          | Warnings | Command                                                               |
| ------------ | -------- | --------------------------------------------------------------------- |
| `apps/web`   | 780      | `cd apps/web && pnpm exec oxlint . 2>&1 \| grep -oE 'Found [0-9]+'`   |
| `apps/admin` | 23       | `cd apps/admin && pnpm exec oxlint . 2>&1 \| grep -oE 'Found [0-9]+'` |
| `apps/space` | 56       | `cd apps/space && pnpm exec oxlint . 2>&1 \| grep -oE 'Found [0-9]+'` |
