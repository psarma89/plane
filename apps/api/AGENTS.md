# Backend conventions

This file supplements the root `AGENTS.md`. It does not restate or override the root rules.

Scope: everything under `apps/api/`. Django, Django REST Framework, Celery, PostgreSQL.

Every pattern count lives in [`docs/architecture/plane-patterns-census.md`](../../docs/architecture/plane-patterns-census.md), with the command that re-measures it. `bin/check-counts` fails when a count drifts.

## Tenant scoping has no framework safety net

`BaseViewSet.get_queryset()` in `plane/app/views/base.py` returns `self.model.objects.all()`. It applies no workspace filter and no project filter. Every viewset applies the scope itself. The census shows how pervasive the hand-written convention is.

1. Override `get_queryset()` in every new viewset.
2. Read the scope from the URL kwargs: `self.kwargs.get("slug")` and `self.kwargs.get("project_id")`. `BaseViewSet` also defines `workspace_slug` and `project_id` properties, but no view uses them. Match the code around you.
3. Keep the same scope in `get_object()`. A scoped list with an unscoped detail route is still a cross-tenant read.
4. Authorize explicitly. The base default is `[IsAuthenticated]`, which authenticates but does not authorize.

Give every new endpoint a contract test that proves a member of another workspace cannot read the data. The `workspace` fixture in `plane/tests/conftest.py` hardcodes `slug="test-workspace"`, so build a second workspace by hand with a unique slug.

## `objects.all()` applies the default manager, not the whole table

Several default managers filter. `Issue.objects` excludes soft-deleted, archived, draft, and triage rows. `State.objects` excludes triage states. Two consequences follow.

- The missing filter is the tenant filter, not every filter.
- A reverse-relation aggregate bypasses the manager. `Count("state_issue")` counts rows that the work item list does not show. Restate the exclusions in the aggregate with `filter=Q(...)`.

## Authorization

Two patterns coexist: `@allow_permission` per action, and `permission_classes` on the class. Match the file you edit, and prefer `@allow_permission` in new code. Do not mix the two in one class. The class inventory lives in `plane/app/permissions/`.

`allow_permission` carries a workspace-admin bypass. A workspace ADMIN who is a member of the project passes the check regardless of project role. A test that proves "a guest cannot do this" needs a user who is a guest at both levels. The role values live in `plane/app/permissions/base.py`.

Pick the refusal status by the mechanism that refuses:

| The request is refused by       | Status |
| ------------------------------- | ------ |
| A permission class or decorator | 403    |
| A scoped `get_queryset()`       | 404    |

`@allow_permission` returns an explicit 403 `Response` and does not raise. `permission_classes` relies on DRF, which raises `PermissionDenied`.

## Two API surfaces, three edits per view

`plane/app/` serves the web client with session auth. `plane/api/` serves external integrations with API tokens. A new field on a shared model can require a change in both. Check `plane/api/serializers/` before you declare a field change complete.

A new view takes three edits: the view module, the re-export in `plane/app/views/__init__.py`, and the route in `plane/app/urls/`. The URL modules import from `plane.app.views`, so a missing re-export fails at import time and reads like a circular import. A new serializer needs the same re-export in `plane/app/serializers/__init__.py`. A new model needs it in `plane/db/models/__init__.py`.

A serializer with a hand-written `to_representation`, such as `IssueListDetailSerializer`, does not pick a new field up. When you add a field, grep `to_representation` across `plane/app/serializers/`.

## Writes

- Wrap a multi-row write in `transaction.atomic()`. Validate the whole batch first, then open the transaction.
- Inside a transaction, delete through the queryset. An instance `.delete()` dispatches `soft_delete_related_objects.delay(...)` from `plane/db/mixins.py`, so the Celery task runs against uncommitted state.
- Before you write `bulk_create(..., ignore_conflicts=True)`, read the model. Without a unique constraint, the flag writes silent duplicates instead of an error. `IssueAssignee`, `IssueMention`, and `IssueSubscriber` carry `unique_together`. `IssueLabel` does not, so dedupe it explicitly.

## Migrations and tests

- For a model change, use the `plane-db-migrate` skill to author the migration. Use `plane-db-upgrade` to apply it and `plane-db-downgrade` to reverse it.
- Do not reformat a generated migration. `apps/api/pyproject.toml` excludes `**/migrations/*` from ruff on purpose.
- For test commands, use the `plane-test-api` skill or `docs/sops/run-backend-tests-sop.md`. For fixtures and conventions, read `plane/tests/TESTING_GUIDE.md`.
- The project-create view builds the default states inline. No signal does it. `Project.objects.create()` in a test therefore has no states, so build them explicitly.
