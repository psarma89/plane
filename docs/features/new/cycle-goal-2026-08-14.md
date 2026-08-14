# Feature: Cycle goal

> **Status:** Draft
> **Owner:** Priyam Sarma
> **Date:** 2026-08-14
> **Mockup:** [`cycle-goal-2026-08-14.mockup.html`](./cycle-goal-2026-08-14.mockup.html). Open it with `open docs/features/new/cycle-goal-2026-08-14.mockup.html`.
> **Work item:** None. This page exists to exercise the feature development flow in [`../../sops/develop-a-feature-sop.md`](../../sops/develop-a-feature-sop.md).
> **Pull request:** {Link, once one exists}

## Goal

A team cannot state what a cycle (`Cycle`) is for in a way that anyone sees. The
cycle already has a description, but that field is long-form prose in a detail
panel, so the intent of a cycle is invisible from the list where people work.

## Non-goals

- No progress tracking against the goal. This feature stores a sentence, not a
  metric.
- No goal on a module (`Module`) or on a project.
- No history of goal changes.
- No new permission. A user who can edit a cycle can edit its goal.

## Why this is not the existing description field

A reviewer must ask this, so the answer belongs in the spec.

|                  | `description`               | `goal`                                           |
| ---------------- | --------------------------- | ------------------------------------------------ |
| Type             | `TextField`, unbounded      | `CharField(max_length=255)`, single line         |
| Where it appears | The cycle detail panel only | The cycle header and every row of the cycle list |
| What it holds    | Prose, notes, links         | One sentence stating the objective               |

The split is the same one a pull request makes between its title and its body. A
field that appears in a list must be short enough to render in a row, and
`description` is not.

## User stories

- As a project lead, I want to state a cycle's objective in one line, so that
  every member sees the intent without opening the cycle.
- As a project member, I want to read the objective from the cycle list, so that I
  can tell two cycles apart at a glance.

## UX flow

### Happy path

1. The user opens the cycle create or update form.
2. The user types a goal into a single-line field under the name.
3. The user saves. The goal appears in the cycle header and in the cycle list row.

### States

| State   | What the user sees                                                            | Next action offered              |
| ------- | ----------------------------------------------------------------------------- | -------------------------------- |
| Loading | The existing cycle skeleton. No new loading state.                            | -                                |
| Empty   | No goal row in the list, and no goal line in the header. Nothing is reserved. | Open the form and add a goal     |
| Error   | The form keeps the typed value and shows the field error from the serializer  | Correct the value and save again |
| Success | The goal renders in the header and in the list row                            | -                                |

## API contract

No new endpoint. The field joins the existing cycle payloads.

### `POST /api/v1/workspaces/{slug}/projects/{project_id}/cycles/`

### `PATCH /api/v1/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/`

- **Authentication**: Session for `plane/app/`, `X-API-Key` for `plane/api/`
- **Permission class**: Unchanged. The cycle views already own this.

**Request**

```json
{
  "name": "Sprint 14",
  "goal": "Ship the export pipeline behind a flag"
}
```

**Response 200**

```json
{
  "id": "uuid",
  "name": "Sprint 14",
  "goal": "Ship the export pipeline behind a flag",
  "description": ""
}
```

**Errors**

| Code | Trigger                                       |
| ---- | --------------------------------------------- |
| 400  | `goal` is longer than 255 characters          |
| 401  | No credential                                 |
| 403  | The role cannot edit a cycle                  |
| 404  | The cycle is not in this workspace or project |

## Data model

| Table    | Read | Write | New |
| -------- | ---- | ----- | --- |
| `cycles` | Yes  | Yes   | No  |

| New or changed field | Type                        | Constraints               | Default |
| -------------------- | --------------------------- | ------------------------- | ------- |
| `goal`               | `CharField(max_length=255)` | `blank=True`, `null=True` | `NULL`  |

- **Migration needed?** Yes. One `AddField` on `cycles`.
- **Backfill needed?** No. The column is nullable, so existing rows keep `NULL`.
- **Migration rollback**: Reversible. `AddField` reverses cleanly. The reversal
  floor of db 0107 does not apply, because this migration sits above it.

`null=True` and `blank=True` together, not `blank=True` alone. The existing
`description` uses `blank=True` on a `TextField`, where the empty string is a
usable absence. On a `CharField` that a list renders, `NULL` and `""` must not be
two ways to say the same thing.

## The three serializer edits

This is the part a naive implementation gets wrong, so the spec names it.

| File                                      | Class                   | Fields declaration   | Needs an edit                                      |
| ----------------------------------------- | ----------------------- | -------------------- | -------------------------------------------------- |
| `apps/api/plane/app/serializers/cycle.py` | The write serializer    | `fields = "__all__"` | No. The field appears on its own.                  |
| `apps/api/plane/app/serializers/cycle.py` | `CycleSerializer`       | An explicit list     | **Yes.** This is the read path for the web client. |
| `apps/api/plane/api/serializers/cycle.py` | `CycleCreateSerializer` | An explicit list     | **Yes.** This is the external token surface.       |

Without the second edit, a write succeeds and the read silently omits the field.
The symptom is a value that saves and then disappears on reload, which reads as a
frontend defect and is not one.

## Frontend plan

| Layer     | Path                                                        | Change                                               |
| --------- | ----------------------------------------------------------- | ---------------------------------------------------- |
| Type      | `packages/types/src/cycle/cycle.ts`                         | Changed. Add `goal` beside `description` on line 92. |
| Service   | `apps/web/core/services/cycle.service.ts`                   | No change. It passes the payload through.            |
| Store     | `apps/web/core/store/cycle.store.ts`                        | No change. It stores the whole cycle object.         |
| Component | `apps/web/core/components/cycles/form.tsx`                  | Changed. One single-line input.                      |
| Component | `apps/web/core/components/cycles/list/cycles-list-item.tsx` | Changed. Render the goal in the row.                 |

- **Data fetching**: Unchanged. The goal arrives inside the existing cycle
  payload.
- **State owner**: `CycleStore` already owns the cycle object.
- **Background classes**: No new surface. The goal renders inside the existing
  list row and header. Follow `packages/tailwind-config/AGENTS.md` for the text
  color, and use a semantic token rather than a literal.
- **Translation keys**: `cycle.goal.label` and `cycle.goal.placeholder` in
  `packages/i18n/src/locales/en/cycle.json`. Use the `translate` skill.
- **Accessibility**: The input needs a label bound by `htmlFor`. The list row
  renders the goal as text, not as a title attribute.

### What the mockup decided

The form takes one input, so on its own it does not need a drawing. The list row
does. That row already carries a name, a progress bar, a percentage, a date range,
and a favorite control, so a new line in it is a layout decision and not a field.

The gate is in `.claude/skills/plan-feature/MOCKUP.md`.

| Question                   | Answer                                                                                               |
| -------------------------- | ---------------------------------------------------------------------------------------------------- |
| An empty goal              | Render nothing. No placeholder. A placeholder in every row is noise, and most cycles carry no goal.  |
| A goal longer than the row | Truncate on one line with an ellipsis. Do not wrap. A row that grows to three lines breaks the list. |
| The color                  | `text-tertiary`, under the cycle name. The name stays the subject of the row.                        |

Each answer is cheap now and expensive in review. None of the three appears in the
prose above, which is the reason the drawing exists.

`packages/types` is a built package. After the type changes, run
`pnpm --filter @plane/types build` before any `check:types`, or the new member
reports as missing.

## Permissions

Unchanged. The cycle views already enforce this.

| Role                             | Can do                  | Cannot do      |
| -------------------------------- | ----------------------- | -------------- |
| Workspace owner, workspace admin | Read and write the goal | -              |
| Project member                   | Read and write the goal | -              |
| Guest                            | Read the goal           | Write the goal |

## Test plan

### Backend

- A `PATCH` that sets `goal` returns the value in the response body. This proves
  the read serializer edit, which is the defect this feature is most likely to
  ship.
- A `goal` of 256 characters returns 400.
- A member of another workspace receives 404 on the cycle detail route. The
  precedent is
  `apps/api/plane/tests/contract/app/test_workspace_cycles_modules_project_scope_app.py`.
  The `workspace` fixture hardcodes `slug="test-workspace"`, so build the second
  workspace by hand.
- The external API surface returns `goal` for a request authenticated by
  `X-API-Key`.

### Frontend

`apps/web` ships no test suite and no vitest config today, so no automated
frontend test is possible. State that in the slice rather than inventing a runner.
Verify by hand against the running stack, and record what was clicked.

## Slices

Ordered along the spine in the SOP: data model, then backend, then frontend.

| #   | Slice                            | Files                                                                                                                                              | Depends on | Proof                                                                                           | Seam                                   |
| --- | -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ----------------------------------------------------------------------------------------------- | -------------------------------------- |
| 1   | The column and both API surfaces | `apps/api/plane/db/models/cycle.py`, a new migration, `apps/api/plane/app/serializers/cycle.py`, `apps/api/plane/api/serializers/cycle.py`         | Nothing    | A contract test where `PATCH` sets the goal and the response body returns it, plus the 400 case | A DRF view through `session_client`    |
| 2   | The type                         | `packages/types/src/cycle/cycle.ts`                                                                                                                | 1          | `pnpm --filter @plane/types build` then `pnpm --filter web check:types` exits 0                 | A pure type change, so no runtime seam |
| 3   | The form and the list row        | `apps/web/core/components/cycles/form.tsx`, `apps/web/core/components/cycles/list/cycles-list-item.tsx`, `packages/i18n/src/locales/en/cycle.json` | 2          | Manual verification against the running stack, recorded in the pull request                     | None. No web suite exists.             |

Slice 1 needs a worktree and a Docker stack, because it runs a contract test.
Slice 2 needs a worktree only. Slice 3 needs a stack to verify by hand.

Slices run in sequence. None of the three is independent, because each consumes
the layer below it.

## Rollout

- **Feature flag?** No. The field is additive and nullable, and a cycle with no
  goal renders exactly as it does today.
- **Staged steps**:
  1. Merge slice 1. The API accepts and returns the field. No user sees it.
  2. Merge slice 2 and slice 3. The field becomes visible.
- **Rollback**: Revert slice 3, then slice 2, then slice 1. Reverse the migration
  with the `plane-db-downgrade` skill before reverting slice 1's code.

## Open questions

| #   | Question                                                           | Decides     | Resolved                                                                                    |
| --- | ------------------------------------------------------------------ | ----------- | ------------------------------------------------------------------------------------------- |
| 1   | Does the goal belong on the cycle list row, or only on the header? | Product     | 2026-08-14, both                                                                            |
| 2   | Does the external API surface need the field in the first release? | Engineering | 2026-08-14, yes. Adding it later is a second breaking-shaped change to a published payload. |

## Assumptions

Stated because no questions were asked of the requester.

1. 255 characters is the right bound. It matches a single-line input and is the
   length Django uses for a short label elsewhere in this codebase.
2. The goal is plain text. No markdown, no mention parsing, no links.
3. The goal is not searchable in this release.
4. A cycle with no goal shows nothing. No placeholder text renders in the list.

## Risks

| Risk                                             | Impact                                                                         | Mitigation                                                             |
| ------------------------------------------------ | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| The read serializer edit is missed               | The value saves and vanishes on reload, and the bug reads as a frontend defect | Slice 1's proof asserts the field in the response body, not just a 200 |
| `goal` and `description` drift into the same use | Two fields hold prose, and neither is authoritative                            | The bound is 255 characters, and the spec states the split             |
| The type change lands without a package build    | `check:types` reports the member as missing, which reads as a typo             | Slice 2's proof runs the build before the type check                   |
