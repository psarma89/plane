# Feature: Cycle capacity threshold

> **Status:** Draft
> **Owner:** Priyam Sarma
> **Date:** 2026-08-14
> **Mockup:** [`cycle-capacity-threshold.mockup.html`](./cycle-capacity-threshold.mockup.html). Open it with `open docs/features/new/cycle-capacity-threshold.mockup.html`.
> **Work item:** None yet.
> **Pull request:** {Link, once one exists}

## Goal

A team can put unlimited work into a cycle (`Cycle`). Nothing in the product states
how much work is too much. The team learns that it overcommitted at the end of the
cycle, when the burn-down chart flattens and the work moves to the next cycle.

This feature gives a cycle an optional capacity in estimate points. The backend
measures the cycle against that capacity on every write. It warns near the limit,
and it rejects a write above the limit.

## Non-goals

- No capacity on an upcoming cycle, a completed cycle, or an archived cycle. The
  gate runs for the active cycle only.
- No capacity on a module (`Module`) or on a project.
- No capacity in work item count. Points are the only unit in this release.
- No override. No role can force a write past the block threshold.
- No capacity from velocity history. A person types the number.
- No new chart. The burn-down chart does not change.
- No notification, no email, and no webhook when a cycle reaches a threshold.

## The unit is points, and that decides the scope

The point sum for a cycle already exists. `CycleProgressEndpoint` computes it in
`apps/api/plane/app/views/cycle/base.py:666-711`, and the annotation filters on
`estimate_point__estimate__type="points"`.

A project that uses a categories-type estimate therefore sums to 0. A capacity on
such a project can never fire. The capacity control is absent for that project, and
the gate does not run.

`EstimateType` in `apps/api/plane/db/models/estimate.py:13` gives the two values.
`Project.estimate` in `apps/api/plane/db/models/project.py:109` gives the link,
and it is nullable.

## User stories

- As a project lead, I want a point capacity on the active cycle, so that the team
  sees one agreed number.
- As a project member, I want a warning before the cycle fills, so that I can move
  work out in time.
- As a project member, I want the API to reject a write above the limit, so that no
  person has to police the plan.
- As a project lead, I want to tune the two percents, so that a strict team and a
  loose team both fit.

## UX flow

### Happy path

1. A project admin opens the cycle form and types a capacity of 40 points.
2. A member adds work items to the active cycle. The panel shows 28 of 40 points.
3. A member adds more work. The point sum reaches 38, which is 95% of capacity.
4. The backend returns the verdict `warn`. The panel shows an amber alert.
5. A member adds a work item worth 5 points. The backend returns 400.
6. The toast states the arithmetic. The write does not happen.

### States

| State   | What the user sees                                                                                             | Next action offered                    |
| ------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| Loading | The existing cycle panel skeleton. The meter renders after the progress request returns. No new loading state. | -                                      |
| Empty   | The cycle carries no capacity. No meter, no alert, and no reserved space in the panel.                         | Open the cycle form and set a capacity |
| Error   | The toast holds the message from the 400, with the three numbers in it. The write does not happen. No retry.   | Raise the capacity, or move work out   |
| Success | The meter shows the new point sum. The alert renders when the verdict is `warn` or `block`.                    | -                                      |

The mockup draws every state. See [What the mockup decided](#what-the-mockup-decided).

## Data model

| Table             | Read | Write | New |
| ----------------- | ---- | ----- | --- |
| `cycles`          | Yes  | Yes   | No  |
| `projects`        | Yes  | Yes   | No  |
| `issues`          | Yes  | No    | No  |
| `estimates`       | Yes  | No    | No  |
| `estimate_points` | Yes  | No    | No  |
| `cycle_issues`    | Yes  | Yes   | No  |

| New or changed field                    | Type                        | Constraints                                      | Default |
| --------------------------------------- | --------------------------- | ------------------------------------------------ | ------- |
| `cycles.capacity`                       | `PositiveIntegerField`      | `null=True`, `blank=True`                        | `NULL`  |
| `projects.cycle_capacity_warn_percent`  | `PositiveSmallIntegerField` | `MinValueValidator(1)`, `MaxValueValidator(500)` | `90`    |
| `projects.cycle_capacity_block_percent` | `PositiveSmallIntegerField` | `MinValueValidator(1)`, `MaxValueValidator(500)` | `100`   |

- **Migration needed?** Yes. One migration with three `AddField` operations, plus
  one `CheckConstraint`.
- **Backfill needed?** No. `capacity` is nullable, and the two percents carry
  defaults that Django writes for every existing row.
- **Migration rollback**: Reversible. `AddField` and `AddConstraint` both reverse
  cleanly. The reversal floor of db 0107 does not apply, because this migration sits
  above it. Use the `plane-db-downgrade` skill.

### The constraint

Add a `CheckConstraint` on `projects` so that the warn percent is not above the
block percent:

```python
models.CheckConstraint(
    check=Q(cycle_capacity_warn_percent__lte=F("cycle_capacity_block_percent")),
    name="project_cycle_capacity_warn_lte_block",
)
```

A serializer check alone is not enough. Two API surfaces write a project, so the
rule belongs in the database.

### `NULL` means no gate

`capacity` uses `null=True` and `blank=True` together. `NULL` is the only way to say
"no limit". A capacity of 0 is a real limit that blocks every write, so the two
values must not collapse into one meaning.

### The migration number will collide

The migration head on `dev` is `0122_alter_draftissue_assignees_alter_issue_assignees_and_more.py`.
The unmerged cycle goal branch already claims `0123_cycle_goal.py`. Whichever branch
merges second must renumber. Run `makemigrations` after the rebase, and do not hand
edit the number. Use the `plane-db-migrate` skill.

## Where the gate runs

This table is the core of the spec. A write path that the gate misses is a hole in
the gate.

Every user-facing path that changes the point sum of a cycle:

| #   | Path                                              | `path:line`                                                                           | Surface     |
| --- | ------------------------------------------------- | ------------------------------------------------------------------------------------- | ----------- |
| 1   | Add work items to a cycle, or move them in        | `apps/api/plane/app/views/cycle/issue.py:264,299`                                     | Session     |
| 2   | Add work items to a cycle                         | `apps/api/plane/api/views/cycle.py:1009`                                              | `X-API-Key` |
| 3   | Promote a draft work item into a cycle            | `apps/api/plane/app/views/workspace/draft.py:240`                                     | Session     |
| 4   | Transfer incomplete work items to another cycle   | `apps/api/plane/utils/cycle_transfer_issues.py:35`                                    | Both        |
| 5   | Change `estimate_point` on a work item in a cycle | `apps/api/plane/app/views/issue/base.py:682`, `apps/api/plane/api/views/issue.py:806` | Both        |

Path 4 is one function that both surfaces import. One edit covers both.

Path 5 is the only path with a real choke point. Both surfaces write `estimate_point`
through a serializer, so one edit per serializer covers every caller:

| Surface     | Serializer                                                            | The view method that calls `save()`          |
| ----------- | --------------------------------------------------------------------- | -------------------------------------------- |
| Session     | `IssueCreateSerializer`, `apps/api/plane/app/serializers/issue.py:82` | `apps/api/plane/app/views/issue/base.py:682` |
| `X-API-Key` | `IssueSerializer`, `apps/api/plane/api/serializers/issue.py:46`       | `apps/api/plane/api/views/issue.py:806`      |

The intake accept route at `apps/api/plane/app/views/intake/base.py:414` calls the
session serializer with `partial=True`. It is a caller of path 5, and not a sixth
path. The serializer edit covers it.

### Three paths that need no gate

| Path                            | `path:line`                                         | Reason            |
| ------------------------------- | --------------------------------------------------- | ----------------- |
| Remove a work item from a cycle | `apps/api/plane/app/views/cycle/issue.py:320`       | It lowers the sum |
| Workspace seed                  | `apps/api/plane/bgtasks/workspace_seed_task.py:323` | No user drives it |
| Demo data                       | `apps/api/plane/bgtasks/dummy_data_task.py:451`     | No user drives it |

A seed that a capacity blocks leaves a half-built workspace. State the exemption in
the code with a comment, so a later reader does not read it as an oversight.

### The path this feature does not gate

A person with admin rights can edit `EstimatePoint.value` through
`apps/api/plane/app/views/estimate/base.py` or
`apps/api/plane/api/views/estimate.py`. That renames a point from 5 to 8, for
example. Every work item that holds that point changes its contribution, so the sum
of every cycle in the project moves at once.

No `Issue` row and no `CycleIssue` row is written, so none of the five hooks fire.
This release does not gate that path. A gate there has to re-measure every cycle in
the project inside one estimate write. That is a different feature.

The result is a cycle that sits above its block threshold with no rejected request
behind it. The read path handles this correctly, because the evaluator measures the
whole cycle and not the size of the write. The panel shows `block`, and the next add
fails. Risk row 8 records it.

### There is no single choke point

`CycleIssue` has no custom `save()`, and no shared serializer covers all five paths.
Path 1, path 2, and path 3 each call `CycleIssue.objects.create` or
`bulk_create` directly. The gate is therefore a call to one shared function from
five places, and not a model hook.

The precedent for that shape is `apps/api/plane/utils/cycle_transfer_issues.py`.
It is a plain function in `plane/utils/`, and both `plane/app/views/cycle/base.py:606`
and `plane/api/views/cycle.py:1250` import it. The capacity evaluator copies that
shape.

### No path runs in a transaction today

None of the five paths opens a `transaction.atomic()` block. There is no
`from django.db import transaction` in `app/views/cycle/issue.py`,
`api/views/cycle.py`, `app/views/workspace/draft.py`,
`utils/cycle_transfer_issues.py`, `app/views/issue/base.py`, or
`api/views/issue.py`.

The gate therefore has to run **before** the first write on each path, and not
between two writes. Path 1 writes twice, at `cycle/issue.py:264` and again at
`:299`. A gate placed between them leaves the `bulk_create` rows behind when the
`bulk_update` is refused.

Slice 3 and slice 4 each wrap their write block in `transaction.atomic()`. That is
new behavior. It also fixes a defect that already exists. `draft.py:240` creates the
`Issue` first and the `CycleIssue` second. A bad `cycle_id` today leaves an orphan
work item, and nothing rolls it back.

### Path 3 has no completed-cycle gate today

`apps/api/plane/app/views/cycle/issue.py:232` refuses to add work to a cycle that
ended. `apps/api/plane/app/views/workspace/draft.py:240` runs no such check, so a
draft promotion can still land work in a completed cycle. That is a pre-existing
defect, and this feature does not fix it. Slice 4 must not fix it either. A reviewer
cannot tell a deliberate fix from an accident. Record the defect in References on
the slice 4 pull request.

## The evaluator

One new module: `apps/api/plane/utils/cycle_capacity.py`.

```python
def evaluate_cycle_capacity(*, cycle, project, incoming_points=0) -> dict:
    """Measure a cycle against its capacity. Return the verdict and the numbers."""
```

It returns one dictionary:

```json
{
  "capacity": 40,
  "used_points": 38,
  "incoming_points": 5,
  "projected_points": 43,
  "warn_at": 36,
  "block_at": 40,
  "warn_percent": 90,
  "block_percent": 100,
  "verdict": "block"
}
```

The field is named `verdict`, and not `state`. `CONTEXT.md` reserves the word
"state" for a work item's workflow column, which is the `State` model. A second
meaning on a cycle payload makes every review sentence ambiguous.

`verdict` takes one of four values.

| `verdict` | Rule                                                              |
| --------- | ----------------------------------------------------------------- |
| `not_set` | `cycle.capacity` is `NULL`, or the project has no points estimate |
| `ok`      | `projected_points` is less than `warn_at`                         |
| `warn`    | `projected_points` reaches `warn_at` and stays under `block_at`   |
| `block`   | `projected_points` reaches `block_at`                             |

`warn_at` is `floor(capacity * warn_percent / 100)`. `block_at` uses the same
formula with the block percent. Both are integers, because a point sum from
`EstimatePoint.value` is a float that holds whole numbers in practice.

The caller decides what to do with the verdict. The evaluator raises nothing and
writes nothing. That keeps it a pure function, so a unit test covers every boundary
with no database.

### The active cycle rule

The gate runs for the active cycle only. A cycle is active when the current time
falls between its dates. The existing definition is in
`apps/api/plane/app/views/cycle/base.py:204-205`:

```python
queryset.filter(start_date__lte=current_time_in_utc, end_date__gte=current_time_in_utc)
```

`current_time_in_utc` comes from `project.timezone` in the same file at lines
191-201. Reuse that resolution, so that two parts of the product do not disagree
about which cycle is active. A cycle with no `start_date` or no `end_date` is not
active, and the gate does not run for it.

Note that `Cycle` also carries its own `timezone` field. The existing definition
uses `project.timezone` and ignores it. This feature follows the existing
definition. Open question 2 records the conflict.

## API contract

No new endpoint. Three existing payloads gain fields, and three existing endpoints
gain one error.

### 1. `PATCH /api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/`

The web client route. The external route is `/api/v1/...`. The two prefixes come
from `apps/api/plane/urls.py:19` and `apps/api/plane/urls.py:22`.

- **Authentication**: Session for `/api/`, `X-API-Key` for `/api/v1/`
- **Permission class**: Unchanged. The cycle views own this today.

**Request**

```json
{ "capacity": 40 }
```

**Response 200**

```json
{ "id": "uuid", "name": "Sprint 14", "capacity": 40 }
```

**Errors**

| Code | Trigger                                         |
| ---- | ----------------------------------------------- |
| 400  | `capacity` is negative, or it is not an integer |
| 401  | No credential                                   |
| 403  | The role cannot edit a cycle                    |
| 404  | The cycle is not in this workspace or project   |

### 2. `GET /api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/progress/`

The route is declared at `apps/api/plane/app/urls/cycle.py:97`. The view is
`CycleProgressEndpoint` at `apps/api/plane/app/views/cycle/base.py:658`. The body is
a plain dictionary, so a new key is additive.

- **Authentication**: Session
- **Permission class**: Unchanged. `allow_permission([ROLE.ADMIN, ROLE.MEMBER, ROLE.GUEST])`

**Response 200**, with the existing keys and one new key:

```json
{
  "total_estimate_points": 38,
  "completed_estimate_points": 12,
  "total_issues": 14,
  "capacity_status": {
    "capacity": 40,
    "used_points": 38,
    "incoming_points": 0,
    "projected_points": 38,
    "warn_at": 36,
    "block_at": 40,
    "warn_percent": 90,
    "block_percent": 100,
    "verdict": "warn"
  }
}
```

The frontend reads `verdict`. It does not compare the numbers.

### 3. `POST /api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/cycle-issues/`

The add-to-cycle route. The view is `CycleIssueViewSet.create` at
`apps/api/plane/app/views/cycle/issue.py:224`. The success body today is
`{"message": "success"}` at line 316, so a new key is additive.

- **Authentication**: Session
- **Permission class**: Unchanged

**Request**

```json
{ "issues": ["uuid-a", "uuid-b"] }
```

**Response 201**, when the verdict is `ok` or `warn`:

```json
{ "message": "success", "capacity_status": { "verdict": "warn", "used_points": 38 } }
```

**Response 400**, when the verdict is `block`:

```json
{
  "error": "The work items are worth 5 points. Sprint 14 holds 38 of 40 points, so the total reaches 43 points, which is over the 40-point limit.",
  "error_code": "CYCLE_CAPACITY_EXCEEDED",
  "capacity_status": { "verdict": "block", "projected_points": 43, "block_at": 40 }
}
```

**Errors**

| Code | Trigger                                                                              |
| ---- | ------------------------------------------------------------------------------------ |
| 400  | The write puts the active cycle at or above the block threshold (new)                |
| 400  | The cycle already ended (existing, at `apps/api/plane/app/views/cycle/issue.py:232`) |
| 400  | `issues` is empty (existing, at line 228)                                            |
| 401  | No credential                                                                        |
| 403  | The role cannot edit a cycle                                                         |
| 404  | The cycle is not in this workspace or project                                        |

The same contract applies to the external route
`POST /api/v1/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/cycle-issues/`
at `apps/api/plane/api/views/cycle.py:966`.

### Why the error carries a code

`error_code` is new for this response. A frontend that matches on the message text
breaks on the next copy edit, and it cannot translate the message. The frontend
matches `CYCLE_CAPACITY_EXCEEDED` and renders a translated string from
`packages/i18n`. The English message in `error` stays as the fallback and as the
log line.

### The two surfaces disagree about the error key

The cycle views return `{"error": "..."}`, for example at
`apps/api/plane/app/views/cycle/issue.py:232`. The cycle modal reads a different
key: `apps/web/core/components/cycles/modal.tsx:70-76` shows
`err?.detail ?? "Error in creating cycle. Please try again."`.

A 400 that carries only `error` therefore renders the generic fallback, and the
three numbers never reach the user. Slice 7 must read `error` on this response, and
not `detail`. Do not change the backend key to `detail`, because six existing
handlers already return `error` and a rename breaks each one.

### Drag and drop discards the message today

`apps/web/core/hooks/use-group-dragndrop.ts:77-93` wraps the cycle mutation in
`.catch(() => setToast(errorToastProps))`. The callback takes no argument, so a
blocked drag shows a generic error and drops the arithmetic.

Slice 7 changes that catch to read the error body. Without that change, the block
message appears on the modal path only. The drag path is the path a person uses
most.

## Frontend plan

| Layer     | Path                                                                   | Change                                                                                 |
| --------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Type      | `packages/types/src/cycle/cycle.ts`                                    | Changed. Add `capacity` and `capacity_status` beside the point sums on lines 73-78.    |
| Type      | `packages/types/src/project/project.ts`                                | Changed. Add the two percents.                                                         |
| Component | `apps/web/core/components/cycles/form.tsx:183`                         | Changed. One optional number input, after the date pair block that closes on line 183. |
| Component | `apps/web/core/components/cycles/analytics-sidebar/issue-progress.tsx` | Changed. Render the meter and the alert from `capacity_status`.                        |
| Component | `apps/web/core/components/cycles/active-cycle/progress.tsx`            | Changed. Render the same alert on the active cycle root.                               |
| Store     | `apps/web/core/store/cycle.store.ts`                                   | **No change.** See below.                                                              |
| Service   | `apps/web/core/services/cycle.service.ts`                              | No change. It passes the payload through.                                              |
| i18n      | `packages/i18n/src/locales/en/cycle.json`                              | Changed. New keys, nested.                                                             |

- **Data fetching**: The existing progress request. The service method is
  `workspaceActiveCyclesProgress()` at `apps/web/core/services/cycle.service.ts:40`.
- **The store needs no edit.** `fetchActiveCycleProgress()` at
  `apps/web/core/store/cycle.store.ts:485-492` spreads the whole response body onto
  the cycle record: line 489 runs
  `set(this.cycleMap, [cycleId], { ...this.cycleMap[cycleId], ...progress })`. A new
  key on the `/progress/` body therefore reaches the component with no store code.
  Only the type has to declare it, which slice 6 does.
- **State owner**: `CycleStore` owns `cycleMap`, and `capacity_status` rides on the
  cycle record inside it.
- **Banner precedent**: `apps/web/core/components/pages/editor/content-limit-banner.tsx`
  is the closest existing component. It is a standalone threshold banner with a
  `TriangleAlert` icon, and a page renders it when it reaches a content limit. Copy
  its shape rather than the inline JSX in
  `apps/web/core/components/cycles/transfer-issues.tsx`. Two components render the
  capacity alert, so an inline block gets duplicated.
- **Background classes**: The modal and the cycle panel each take `bg-surface-1`,
  because they are siblings and the modal sits on its own plane. Each input takes
  `bg-layer-1`, which is the one allowed exception for a form control. The meter
  track takes `bg-layer-1`. The two alerts replace the layer with a semantic tint:
  `bg-warning-subtle` with `border-warning-subtle` and `text-warning-primary`, then
  `bg-danger-subtle` with `border-danger-subtle` and `text-danger-primary`. A tint is
  a color, not a fourth level. See `packages/tailwind-config/AGENTS.md` and the
  `plane-backgrounds` skill.
- **Translation keys**, in `packages/i18n/src/locales/en/cycle.json`. Use the
  `translate` skill. The file nests objects. It does not use flat dotted keys, so
  write `{ "cycle": { "capacity": { "label": "..." } } }`. The table below gives the
  access path, in the same shorthand the existing keys use, for example
  `active_cycle.empty_state.progress.title`.

  | Key                             | English                                                                                                                  |
  | ------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
  | `cycle.capacity.label`          | Capacity in points                                                                                                       |
  | `cycle.capacity.placeholder`    | Optional. Leave it empty for no limit.                                                                                   |
  | `cycle.capacity.hint`           | Warn at {warnAt} points. Block at {blockAt} points.                                                                      |
  | `cycle.capacity.meter`          | {used} / {capacity} points                                                                                               |
  | `cycle.capacity.warn.title`     | {percent}% of capacity                                                                                                   |
  | `cycle.capacity.warn.body`      | This cycle holds {used} of {capacity} points.                                                                            |
  | `cycle.capacity.block.title`    | Capacity is full                                                                                                         |
  | `cycle.capacity.block.body`     | Raise the capacity, or move work out, before you add more.                                                               |
  | `cycle.capacity.rejected.title` | Cannot add this work item                                                                                                |
  | `cycle.capacity.rejected.body`  | The work is worth {incoming} points. {cycle} holds {used} of {capacity} points, so the total reaches {projected} points. |

- **Accessibility**: The number input takes a label bound by `htmlFor`. Each alert
  takes `role="status"` for `warn` and `role="alert"` for `block`, so a screen
  reader announces the block verdict and does not interrupt for the warn verdict. The
  meter takes `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, and
  `aria-valuemax`. Each alert carries an icon and a text title, so color is not the
  only signal.

### What the mockup decided

The mockup is [`cycle-capacity-threshold.mockup.html`](./cycle-capacity-threshold.mockup.html).
The gate in `.claude/skills/plan-feature/MOCKUP.md` says to build one. This feature
adds a panel element, and it puts a new control on a dense form. It also has more
than two states.

| Question                               | Answer                                                                                                           |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| A cycle with no capacity               | Draw nothing. No meter, no alert, and no reserved space. Most cycles will never carry a capacity.                |
| The `ok` verdict                       | Show the meter and no alert. An always-visible green banner trains the user to ignore the amber one.             |
| The `warn` alert and the `block` alert | One slot, one alert at a time. The color and the verb change, and the layout does not move.                      |
| The block message                      | Name three numbers: the incoming points, the current points, and the limit. "Over capacity" alone is not enough. |
| The warn point                         | Draw a mark at the warn percent on the track in every state, so the user sees it before it fires.                |
| A project with no points estimate      | The capacity control is absent, not disabled. A disabled control invites a question that has no good answer.     |

`packages/types` is a built package. After the type change, run
`pnpm --filter @plane/types build` before any `check:types`, or the new member
reports as missing.

## Permissions

No new permission class. Each endpoint keeps the class it has today.

| Role                             | Can do                                                       | Cannot do                              |
| -------------------------------- | ------------------------------------------------------------ | -------------------------------------- |
| Workspace owner, workspace admin | Set the capacity. Set the two percents. Read every verdict.  | Force a write past the block threshold |
| Project admin                    | Set the capacity. Set the two percents. Read every verdict.  | Force a write past the block threshold |
| Project member                   | Read every verdict. Add work until the block threshold.      | Set the capacity or the two percents   |
| Guest                            | Read the capacity verdict on a cycle the guest already sees. | Set anything. Add work items.          |

The capacity field rides on the cycle update route, which already restricts writes
to admin and member. The two percents ride on the project update route, which
already restricts writes to admin. No new check is needed for either one.

## Test plan

### Backend

The precedent for a cycle contract test is
`apps/api/plane/tests/contract/app/test_cycle_issue_app.py`. The precedent for a
pure-function unit test is `apps/api/plane/tests/unit/utils/`.

Unit, in `apps/api/plane/tests/unit/utils/test_cycle_capacity.py`:

- `test_verdict_is_not_set_when_capacity_is_null` proves that `NULL` disables the gate.
- `test_verdict_is_not_set_when_project_estimate_is_categories` proves the estimate rule.
- `test_verdict_is_ok_one_point_below_warn_at` proves the lower boundary.
- `test_verdict_is_warn_exactly_at_warn_at` proves that the warn boundary is inclusive.
- `test_verdict_is_warn_one_point_below_block_at` proves the upper edge of `warn`.
- `test_verdict_is_block_exactly_at_block_at` proves that the block boundary is inclusive.
- `test_capacity_of_zero_blocks_every_write` proves that 0 and `NULL` differ.
- `test_warn_at_floors_a_fractional_percent` proves the rounding rule.

Contract, in `apps/api/plane/tests/contract/app/test_cycle_capacity_app.py`:

- `test_patch_sets_capacity_and_response_returns_it` proves the read serializer edit.
- `test_add_work_items_under_warn_returns_201_with_verdict_ok`.
- `test_add_work_items_over_warn_returns_201_with_verdict_warn` proves that a warn
  does not block.
- `test_add_work_items_over_block_returns_400_with_error_code` proves the gate and
  the `error_code`.
- `test_blocked_request_writes_no_cycle_issue_row` proves that the rejection is
  atomic. A 400 that leaves a row behind is the worst outcome of this feature. The
  session path writes twice, at `cycle/issue.py:264` and `:299`, and no transaction
  wraps them today, so this test fails before slice 3 adds one.
- `test_intake_accept_over_block_returns_400` proves that the intake route inherits
  the gate through the shared serializer at `apps/api/plane/app/views/intake/base.py:414`.
- `test_estimate_point_value_edit_does_not_return_400` proves the ungated path on
  purpose. An estimate value edit must still succeed, and the cycle then reads
  `block`.
- `test_gate_does_not_run_for_an_upcoming_cycle` proves the active-cycle scope.
- `test_gate_does_not_run_for_a_completed_cycle` proves the same on the other side.
- `test_progress_endpoint_returns_capacity_status`.
- `test_estimate_point_change_over_block_returns_400` proves path 5.
- `test_transfer_over_block_returns_400` proves path 4.
- `test_draft_promotion_over_block_returns_400` proves path 3.
- `test_project_warn_percent_above_block_percent_returns_400` proves the constraint.
- `test_guest_cannot_set_capacity` is the permission case.

Contract, in `apps/api/plane/tests/contract/api/test_cycle_capacity_api.py`:

- `test_external_add_over_block_returns_400` proves that the `X-API-Key` surface
  carries the same gate. Without this test the second surface stays open, which is
  the defect this feature is most likely to ship.

Run every command through the `plane-test-api` skill.

### Frontend

`apps/web` ships no test suite and no vitest config today. No automated frontend
test is possible. Verify by hand against the running stack, and record in the pull
request what was clicked.

- The capacity input saves a value, and the value survives a reload.
- The meter renders at the right width for 28 of 40 points.
- The amber alert appears at 38 of 40 points, and the green meter turns amber.
- A blocked add through the cycle modal shows the toast with the three numbers.
- A blocked add through a drag between board groups shows the same toast, and not
  the generic one. This is the path the catch at `use-group-dragndrop.ts:77` changes.
- After a blocked add, the board does not show the item.
- A cycle with no capacity renders no meter and no alert.
- A project with a categories-type estimate renders no capacity input.

## Slices

The spine is data model, then backend, then frontend. Seams come from
`.claude/skills/develop-slice/SEAMS.md`.

| #   | Slice                                   | Files                                                                                                                                                                                                                                                                    | Depends on | Proof                                                                                                                                                                                   | Seam                                                          |
| --- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| 1   | The three columns and both API surfaces | `apps/api/plane/db/models/cycle.py`, `apps/api/plane/db/models/project.py`, a new migration, `apps/api/plane/app/serializers/cycle.py`, `apps/api/plane/api/serializers/cycle.py`, `apps/api/plane/app/serializers/project.py`                                           | Nothing    | `test_patch_sets_capacity_and_response_returns_it`, plus `test_project_warn_percent_above_block_percent_returns_400`                                                                    | A DRF view through `session_client`                           |
| 2   | The evaluator                           | `apps/api/plane/utils/cycle_capacity.py`, `apps/api/plane/tests/unit/utils/test_cycle_capacity.py`                                                                                                                                                                       | 1          | The eight unit tests above. No database and no HTTP.                                                                                                                                    | A pure function, called directly                              |
| 3   | The gate on the two add-to-cycle paths  | `apps/api/plane/app/views/cycle/issue.py`, `apps/api/plane/api/views/cycle.py`                                                                                                                                                                                           | 2          | `test_add_work_items_over_block_returns_400_with_error_code`, `test_blocked_request_writes_no_cycle_issue_row`, `test_external_add_over_block_returns_400`                              | A DRF view through `session_client` and an `X-API-Key` client |
| 4   | The gate on the other three paths       | `apps/api/plane/utils/cycle_transfer_issues.py`, `apps/api/plane/app/views/workspace/draft.py`, `apps/api/plane/app/serializers/issue.py`, `apps/api/plane/api/serializers/issue.py`                                                                                     | 2          | `test_transfer_over_block_returns_400`, `test_draft_promotion_over_block_returns_400`, `test_estimate_point_change_over_block_returns_400`, `test_intake_accept_over_block_returns_400` | A DRF view through `session_client`                           |
| 5   | `capacity_status` on the progress body  | `apps/api/plane/app/views/cycle/base.py`                                                                                                                                                                                                                                 | 2          | `test_progress_endpoint_returns_capacity_status`                                                                                                                                        | A DRF view through `session_client`                           |
| 6   | The types                               | `packages/types/src/cycle/cycle.ts`, `packages/types/src/project/project.ts`                                                                                                                                                                                             | 5          | `pnpm --filter @plane/types build` then `pnpm --filter web check:types` exits 0                                                                                                         | A pure type change, so no runtime seam                        |
| 7   | The form, the meter, the alerts         | `apps/web/core/components/cycles/form.tsx`, `apps/web/core/components/cycles/analytics-sidebar/issue-progress.tsx`, `apps/web/core/components/cycles/active-cycle/progress.tsx`, `apps/web/core/hooks/use-group-dragndrop.ts`, `packages/i18n/src/locales/en/cycle.json` | 6          | Manual verification against the running stack, recorded in the pull request                                                                                                             | None. No web suite exists.                                    |

Slice 3 and slice 4 both depend on slice 2 and on nothing else. They can run in
parallel worktrees, one `plane-env-create` stack each. Slice 5 is also independent
of slice 3 and slice 4. Every other pair runs in sequence.

Slice 1, 2, 3, 4, and 5 need a Docker stack, because each runs a backend test.
Slice 6 needs a worktree only. Slice 7 needs a stack to verify by hand.

## Rollout

- **Feature flag?** No. Every column is additive, and a `NULL` capacity leaves the
  product exactly as it is today. The gate cannot fire until a person types a
  capacity. A flag therefore protects nobody.
- **Staged steps**:
  1. Merge slice 1. The columns exist and both API surfaces accept them. No user
     sees a change.
  2. Merge slice 2. The evaluator exists and no caller uses it.
  3. Merge slice 3, slice 4, and slice 5. The gate runs. Only a cycle with a
     capacity is affected, and no cycle has one yet.
  4. Merge slice 6 and slice 7. The control becomes visible, and a person can set a
     capacity for the first time.
- **Rollback**: Revert slice 7, then 6, then 5, 4, 3, and 2. Reverse the migration
  with the `plane-db-downgrade` skill before you revert slice 1. A faster partial
  rollback exists: set every `cycles.capacity` back to `NULL`, which disables the
  gate for every project and leaves the code in place.

## Open questions

| #   | Question                                                                                          | Decides     | Resolved                                                                         |
| --- | ------------------------------------------------------------------------------------------------- | ----------- | -------------------------------------------------------------------------------- |
| 1   | Where does the capacity number live?                                                              | Product     | 2026-08-14. On the cycle only. It is optional, and a person can change it later. |
| 2   | Does the active check use `project.timezone` or `Cycle.timezone`?                                 | Engineering | Open. The spec follows the existing definition, which uses `project.timezone`.   |
| 3   | Does a warn verdict need a notification or a webhook?                                             | Product     | 2026-08-14. No. It is a non-goal for this release.                               |
| 4   | Do the two percents belong on the project or on the workspace?                                    | Product     | 2026-08-14. On the project, next to the other project toggles.                   |
| 5   | Does a project admin need a way to see which cycles are over capacity across the whole workspace? | Product     | Open. It is out of scope here, and it is a candidate for a second feature.       |

## Assumptions

Four questions were asked. Everything below is an assumption, and a reviewer can
overturn any of it.

1. The capacity counts every work item in the cycle, and not only the incomplete
   ones. A completed point still consumed the cycle.
2. A cancelled work item still counts. The existing point sum includes it, and this
   feature does not change that sum.
3. A sub-item counts once, on its own row. The feature does not roll a child into a
   parent.
4. The gate measures the whole cycle after the write, and not the size of the write.
   A write of one point into a cycle that is already over the limit is rejected.
5. A person who lowers the capacity below the current point sum succeeds. The gate
   runs on a work item write, and not on a capacity write. The cycle then shows the
   `block` verdict, and the next add fails.
6. The two percents apply to every cycle in the project. No cycle overrides them.
7. `capacity` holds a whole number. No project needs a capacity of 12.5 points.

Assumption 5 is the one most likely to be wrong. It trades a strict rule for a
usable one. A lead who must cut the capacity mid-cycle cannot be blocked by the
work that the cycle already holds.

## Risks

| Risk                                                                 | Impact                                                                                       | Mitigation                                                                                                                                                                                |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The gate lands on one API surface only                               | A script with an `X-API-Key` walks past the limit, and the product looks broken to the team  | Slice 3 carries a test on the external surface, in a separate file                                                                                                                        |
| A path in the table is missed                                        | The point sum crosses the limit through a path nobody tested                                 | The table names five paths and two exemptions. Slice 3 and slice 4 together cover all five                                                                                                |
| The rejection is not atomic                                          | A 400 leaves a `cycle_issues` row behind, so the cycle holds work the API says it refused    | No path opens `transaction.atomic()` today. Slice 3 and slice 4 add one, and the gate runs before the first write. `test_blocked_request_writes_no_cycle_issue_row` asserts the row count |
| A person edits `EstimatePoint.value` and every cycle sum moves       | A cycle sits above its block threshold with no rejected request behind it                    | Named as an ungated path above. The evaluator measures the whole cycle, so the panel shows `block` and the next add fails                                                                 |
| The drag path shows a generic toast                                  | The block message never reaches the user on the path they use most                           | Slice 7 changes the catch at `use-group-dragndrop.ts:77-93` to read the error body                                                                                                        |
| The read serializer edit is missed                                   | The capacity saves and vanishes on reload. The defect reads as a frontend bug and is not one | Slice 1 asserts the field in the response body, and not only a 200                                                                                                                        |
| The migration number collides with the cycle goal branch             | The second branch to merge fails `migrate` with two `0123` nodes                             | Renumber after the rebase. The spec names the head as `0122`                                                                                                                              |
| A project with a categories estimate sets a capacity through the API | The point sum is 0, so the gate never fires, and the number lies to the team                 | The evaluator returns `not_set` for that project, and the UI hides the control                                                                                                            |
| The extra query slows down every add-to-cycle write                  | A hot write path gains a point sum aggregate                                                 | The evaluator runs one aggregate over `cycle_issues`, and it runs only when `capacity` is not `NULL`                                                                                      |
| A team treats the block as a bug                                     | The team raises the capacity to a number that means nothing, and the feature stops helping   | The block message names the arithmetic and the two ways out. No override exists, by decision                                                                                              |
