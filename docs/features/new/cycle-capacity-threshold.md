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

This feature gives a cycle an optional capacity in estimate points, and a toggle
that says what to do at the limit. The backend measures the cycle on every write. It
warns at the limit, or it refuses the write, and the toggle decides which.

## Non-goals

- No capacity on an upcoming cycle, a completed cycle, or an archived cycle. The
  gate runs for the active cycle only.
- No capacity on a module (`Module`) or on a project.
- No capacity in work item count. Points are the only unit in this release.
- No percent thresholds. One number and one toggle, and nothing to tune.
- No override. In block mode, no role can force a write past the capacity.
- No capacity from velocity history. A person types the number.
- No new chart. The burn-down chart does not change.
- No notification, no email, and no webhook when a cycle passes its capacity.

## The rule

Two columns, one comparison. The capacity is a trip wire in points. There is no
percent math anywhere in this feature.

```
used_points      = sum of the estimate points of every work item in the cycle
incoming_points  = the points that this write adds
projected_points = used_points + incoming_points

The alert shows when       used_points      > capacity
A write is refused when    projected_points > capacity   AND   mode is block
```

One comparison, used twice. The capacity itself is not over the capacity.

| `used_points` | `capacity` | Result                  |
| ------------- | ---------- | ----------------------- |
| 28            | 40         | Green. Nothing happens. |
| 40            | 40         | Green. Nothing happens. |
| 41            | 40         | The alert shows.        |

### What each mode does

| Mode    | Above the capacity                                  | A write that lands above it   |
| ------- | --------------------------------------------------- | ----------------------------- |
| `warn`  | An amber alert renders. Every write still succeeds. | Succeeds. The alert stays.    |
| `block` | A red alert renders.                                | HTTP 400. Nothing is written. |

In `warn` mode the backend recomputes the sum after every write. The alert clears
by itself when the sum drops back under the capacity. Nobody dismisses it, and
nothing stores it.

### What both modes always allow

These four never raise the sum, so the gate never refuses them:

1. Remove a work item from the cycle.
2. Delete a work item that sits in the cycle.
3. Lower the estimate of a work item in the cycle.
4. Any write whose projected sum lands at or under the capacity.

Point 3 matters for `block` mode. A cycle that sits at 44 of 40 points is not
frozen. A person can still cut an estimate from 8 points to 3, because the
projected sum of 39 does not pass the capacity.

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
- As a project lead, I want to choose between a warning and a hard stop, so that one
  team can self-police and another cannot overfill.
- As a project member, I want the alert to clear when I move work out, so that the
  number on the screen matches the cycle.
- As a project member in a full cycle, I want to still cut an estimate, so that the
  cycle comes back under its capacity.

## UX flow

### Happy path, warn mode

1. A project admin opens the cycle form, types a capacity of 40 points, and leaves
   the toggle on Warn.
2. A member adds work items. The panel shows 28 of 40 points and no alert.
3. A member adds 12 more points. The sum reaches 40, which is the capacity itself.
4. The backend returns the verdict `ok`. No alert renders. The cycle is full and not
   over.
5. A member adds one more point. The sum reaches 41.
6. The backend returns the verdict `warn`. The panel shows an amber alert.
7. A member removes a 5-point work item. The sum drops to 36.
8. The backend returns the verdict `ok`. The alert disappears.

### Happy path, block mode

1. A project admin sets the toggle to Block on the same cycle.
2. The cycle holds 38 of 40 points. The panel shows no alert.
3. A member adds a work item worth 5 points. The projected sum is 43.
4. The backend returns 400. The toast states the three numbers, and nothing is
   written.
5. A member cuts an estimate from 8 points to 3. The projected sum is 33, so the
   write succeeds.

### States

| State   | What the user sees                                                                                             | Next action offered                    |
| ------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| Loading | The existing cycle panel skeleton. The meter renders after the progress request returns. No new loading state. | -                                      |
| Empty   | The cycle carries no capacity. No meter, no alert, and no reserved space in the panel.                         | Open the cycle form and set a capacity |
| Error   | The toast holds the message from the 400, with the three numbers in it. Nothing is written. No retry.          | Remove work, or lower an estimate      |
| Success | The meter shows the new point sum. The alert renders, or it clears, from the returned verdict.                 | -                                      |

The mockup draws every state. See [What the mockup decided](#what-the-mockup-decided).

## Data model

| Table             | Read | Write | New |
| ----------------- | ---- | ----- | --- |
| `cycles`          | Yes  | Yes   | No  |
| `issues`          | Yes  | No    | No  |
| `estimates`       | Yes  | No    | No  |
| `estimate_points` | Yes  | No    | No  |
| `cycle_issues`    | Yes  | Yes   | No  |

Two new columns, both on `cycles`. No column on `projects`.

| New field       | Type                                                 | Constraints               | Default  |
| --------------- | ---------------------------------------------------- | ------------------------- | -------- |
| `capacity`      | `PositiveIntegerField`                               | `null=True`, `blank=True` | `NULL`   |
| `capacity_mode` | `CharField(max_length=10, choices=..., default=...)` | Not null. Two values.     | `"warn"` |

The choices come from a `TextChoices` class beside the model, which copies
`EstimateType` at `apps/api/plane/db/models/estimate.py:13`:

```python
class CycleCapacityMode(models.TextChoices):
    WARN = "warn", "Warn"
    BLOCK = "block", "Block"
```

- **Migration needed?** Yes. One migration with two `AddField` operations. No
  constraint, because there is no relationship between the two columns to enforce.
- **Backfill needed?** No. `capacity` is nullable, and `capacity_mode` carries a
  default that Django writes for every existing row.
- **Migration rollback**: Reversible. `AddField` reverses cleanly. The reversal floor
  of db 0107 does not apply, because this migration sits above it. Use the
  `plane-db-downgrade` skill.

### `NULL` means no gate

`capacity` uses `null=True` and `blank=True` together. `NULL` is the only way to say
"no limit". A capacity of 0 is a real limit that refuses every add, so the two values
must not collapse into one meaning.

`capacity_mode` still holds `warn` on a cycle with no capacity. The evaluator ignores
the mode when the capacity is `NULL`, so a person can pick a mode before they pick a
number.

### Why a `TextChoices` and not a boolean

A boolean named `capacity_blocks` costs one less byte and reads worse. The API then
carries `capacity_blocks: false`, which does not say what happens instead. The
`TextChoices` puts the two behaviors in the payload by name, and it matches the
precedent the estimate model already set.

### The migration number will collide

The migration head on `dev` is `0122_alter_draftissue_assignees_alter_issue_assignees_and_more.py`.
The unmerged cycle goal branch already claims `0123_cycle_goal.py`. Whichever branch
merges second must renumber. Run `makemigrations` after the rebase, and do not hand
edit the number. Use the `plane-db-migrate` skill.

## Where the gate runs

This table is the core of the spec. A write path that the gate misses is a hole in
the gate.

Every user-facing path that raises the point sum of a cycle:

| #   | Path                                             | `path:line`                                                                           | Surface     |
| --- | ------------------------------------------------ | ------------------------------------------------------------------------------------- | ----------- |
| 1   | Add work items to a cycle, or move them in       | `apps/api/plane/app/views/cycle/issue.py:264,299`                                     | Session     |
| 2   | Add work items to a cycle                        | `apps/api/plane/api/views/cycle.py:1009`                                              | `X-API-Key` |
| 3   | Promote a draft work item into a cycle           | `apps/api/plane/app/views/workspace/draft.py:240`                                     | Session     |
| 4   | Transfer incomplete work items to another cycle  | `apps/api/plane/utils/cycle_transfer_issues.py:35`                                    | Both        |
| 5   | Raise `estimate_point` on a work item in a cycle | `apps/api/plane/app/views/issue/base.py:682`, `apps/api/plane/api/views/issue.py:806` | Both        |

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

On path 5 the gate compares the old point value with the new one. A write that lowers
the estimate always passes, in both modes.

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

The result is a cycle that sits above its capacity with no refused request behind it.
The read path handles this correctly, because the evaluator measures the whole cycle
and not the size of the write. The panel shows the alert, and the next add fails in
block mode. Risk row 6 records it.

### There is no single choke point

`CycleIssue` has no custom `save()`, and no shared serializer covers all five paths.
Path 1, path 2, and path 3 each call `CycleIssue.objects.create` or `bulk_create`
directly. The gate is therefore a call to one shared function from five places, and
not a model hook.

The precedent for that shape is `apps/api/plane/utils/cycle_transfer_issues.py`. It
is a plain function in `plane/utils/`, and both `plane/app/views/cycle/base.py:606`
and `plane/api/views/cycle.py:1250` import it. The capacity evaluator copies that
shape.

### No path runs in a transaction today

None of the five paths opens a `transaction.atomic()` block. There is no
`from django.db import transaction` in `app/views/cycle/issue.py`,
`api/views/cycle.py`, `app/views/workspace/draft.py`,
`utils/cycle_transfer_issues.py`, `app/views/issue/base.py`, or
`api/views/issue.py`.

The gate therefore has to run **before** the first write on each path, and not
between two writes. Path 1 writes twice, at `cycle/issue.py:264` and again at `:299`.
A gate placed between them leaves the `bulk_create` rows behind when the
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
cannot tell a deliberate fix from an accident. Record the defect in References on the
slice 4 pull request.

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
  "mode": "block",
  "used_points": 38,
  "incoming_points": 5,
  "projected_points": 43,
  "verdict": "ok",
  "write_allowed": false
}
```

`verdict` describes the cycle as it stands. It takes one of four values:

| `verdict` | Rule                                                              |
| --------- | ----------------------------------------------------------------- |
| `not_set` | `cycle.capacity` is `NULL`, or the project has no points estimate |
| `ok`      | `used_points` is at or under `capacity`                           |
| `warn`    | `used_points` passes `capacity`, and `capacity_mode` is `warn`    |
| `block`   | `used_points` passes `capacity`, and `capacity_mode` is `block`   |

`write_allowed` describes the write in front of it. It is `false` only when the mode
is `block` and `projected_points` passes `capacity`:

```python
write_allowed = not (mode == BLOCK and capacity is not None and projected_points > capacity)
```

The example above shows why the two fields are separate. The cycle reads `ok` at 38
of 40 points, and the 5-point write is still refused, because it lands at 43.

The field is named `verdict`, and not `state`. `CONTEXT.md` reserves the word "state"
for a work item's workflow column, which is the `State` model. A second meaning on a
cycle payload makes every review sentence ambiguous.

The caller decides what to do with the result. The evaluator raises nothing and
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

Note that `Cycle` also carries its own `timezone` field. The existing definition uses
`project.timezone` and ignores it. This feature follows the existing definition. Open
question 3 records the conflict.

## API contract

No new endpoint. Two existing payloads gain fields, and three existing endpoints gain
one error.

### 1. `PATCH /api/workspaces/{slug}/projects/{project_id}/cycles/{cycle_id}/`

The web client route. The external route is `/api/v1/...`. The two prefixes come from
`apps/api/plane/urls.py:19` and `apps/api/plane/urls.py:22`.

- **Authentication**: Session for `/api/`, `X-API-Key` for `/api/v1/`
- **Permission class**: Unchanged. The cycle views own this today.

**Request**

```json
{ "capacity": 40, "capacity_mode": "block" }
```

**Response 200**

```json
{ "id": "uuid", "name": "Sprint 14", "capacity": 40, "capacity_mode": "block" }
```

**Errors**

| Code | Trigger                                         |
| ---- | ----------------------------------------------- |
| 400  | `capacity` is negative, or it is not an integer |
| 400  | `capacity_mode` is not `warn` and not `block`   |
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
  "total_estimate_points": 41,
  "completed_estimate_points": 12,
  "total_issues": 14,
  "capacity_status": {
    "capacity": 40,
    "mode": "warn",
    "used_points": 41,
    "incoming_points": 0,
    "projected_points": 41,
    "verdict": "warn",
    "write_allowed": true
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

**Response 201**, when the write is allowed:

```json
{ "message": "success", "capacity_status": { "verdict": "warn", "used_points": 43 } }
```

**Response 400**, when the mode is `block` and the write passes the capacity:

```json
{
  "error": "The work items are worth 5 points. Sprint 14 holds 38 of 40 points, so the total reaches 43 points, which is over the 40-point capacity.",
  "error_code": "CYCLE_CAPACITY_EXCEEDED",
  "capacity_status": { "verdict": "ok", "projected_points": 43, "capacity": 40, "write_allowed": false }
}
```

**Errors**

| Code | Trigger                                                                              |
| ---- | ------------------------------------------------------------------------------------ |
| 400  | The mode is `block` and the write passes the capacity of the active cycle (new)      |
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
`packages/i18n`. The English message in `error` stays as the fallback and as the log
line.

### The two surfaces disagree about the error key

The cycle views return `{"error": "..."}`, for example at
`apps/api/plane/app/views/cycle/issue.py:232`. The cycle modal reads a different key:
`apps/web/core/components/cycles/modal.tsx:70-76` shows
`err?.detail ?? "Error in creating cycle. Please try again."`.

A 400 that carries only `error` therefore renders the generic fallback, and the three
numbers never reach the user. Slice 7 must read `error` on this response, and not
`detail`. Do not change the backend key to `detail`, because six existing handlers
already return `error` and a rename breaks each one.

### Drag and drop discards the message today

`apps/web/core/hooks/use-group-dragndrop.ts:77-93` wraps the cycle mutation in
`.catch(() => setToast(errorToastProps))`. The callback takes no argument, so a
refused drag shows a generic error and drops the arithmetic.

Slice 7 changes that catch to read the error body. Without that change, the message
appears on the modal path only. The drag path is the path a person uses most.

## Frontend plan

| Layer     | Path                                                                   | Change                                                                                                          |
| --------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Type      | `packages/types/src/cycle/cycle.ts`                                    | Changed. Add `capacity`, `capacity_mode`, and `capacity_status` beside the point sums on lines 73-78.           |
| Component | `apps/web/core/components/cycles/form.tsx:183`                         | Changed. One optional number input and one two-value toggle, after the date pair block that closes on line 183. |
| Component | `apps/web/core/components/cycles/analytics-sidebar/issue-progress.tsx` | Changed. Render the meter and the alert from `capacity_status`.                                                 |
| Component | `apps/web/core/components/cycles/active-cycle/progress.tsx`            | Changed. Render the same alert on the active cycle root.                                                        |
| Component | `apps/web/core/hooks/use-group-dragndrop.ts`                           | Changed. Read the error body in the catch.                                                                      |
| Store     | `apps/web/core/store/cycle.store.ts`                                   | **No change.** See below.                                                                                       |
| Service   | `apps/web/core/services/cycle.service.ts`                              | No change. It passes the payload through.                                                                       |
| i18n      | `packages/i18n/src/locales/en/cycle.json`                              | Changed. New keys, nested.                                                                                      |

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
  `bg-layer-1`, which is the one allowed exception for a form control. The meter track
  takes `bg-layer-1`. The two alerts replace the layer with a semantic tint:
  `bg-warning-subtle` with `border-warning-subtle` and `text-warning-primary` for
  `warn`, then `bg-danger-subtle` with `border-danger-subtle` and
  `text-danger-primary` for `block`. A tint is a color, not a fourth level. See
  `packages/tailwind-config/AGENTS.md` and the `plane-backgrounds` skill.
- **Translation keys**, in `packages/i18n/src/locales/en/cycle.json`. Use the
  `translate` skill. The file nests objects. It does not use flat dotted keys, so
  write `{ "cycle": { "capacity": { "label": "..." } } }`. The table below gives the
  access path, in the same shorthand the existing keys use, for example
  `active_cycle.empty_state.progress.title`.

  | Key                              | English                                                                                                                  |
  | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
  | `cycle.capacity.label`           | Capacity in points                                                                                                       |
  | `cycle.capacity.placeholder`     | Optional. Leave it empty for no limit.                                                                                   |
  | `cycle.capacity.mode.label`      | At the limit                                                                                                             |
  | `cycle.capacity.mode.warn`       | Warn                                                                                                                     |
  | `cycle.capacity.mode.block`      | Block                                                                                                                    |
  | `cycle.capacity.mode.hint_warn`  | Show a warning. Anyone can still add work.                                                                               |
  | `cycle.capacity.mode.hint_block` | Refuse new work. Removing work and lowering an estimate still succeed.                                                   |
  | `cycle.capacity.meter`           | {used} / {capacity} points                                                                                               |
  | `cycle.capacity.warn.title`      | Cycle is over capacity                                                                                                   |
  | `cycle.capacity.warn.body`       | This cycle holds {used} of {capacity} points. Anyone can still add work.                                                 |
  | `cycle.capacity.block.title`     | Cycle is over capacity                                                                                                   |
  | `cycle.capacity.block.body`      | This cycle holds {used} of {capacity} points. Remove work, or lower an estimate, before you add more.                    |
  | `cycle.capacity.rejected.title`  | Cannot add this work item                                                                                                |
  | `cycle.capacity.rejected.body`   | The work is worth {incoming} points. {cycle} holds {used} of {capacity} points, so the total reaches {projected} points. |

- **Accessibility**: The number input and the toggle each take a label bound by
  `htmlFor`. The toggle is a radio group with two options, and not a checkbox, because
  a checkbox cannot name the off value. Each alert takes `role="status"` for `warn`
  and `role="alert"` for `block`, so a screen reader announces the block alert and
  does not interrupt for the warn alert. The meter takes `role="progressbar"` with
  `aria-valuenow`, `aria-valuemin`, and `aria-valuemax`. Each alert carries an icon
  and a text title, so color is not the only signal.

### What the mockup decided

The mockup is [`cycle-capacity-threshold.mockup.html`](./cycle-capacity-threshold.mockup.html).
The gate in `.claude/skills/plan-feature/MOCKUP.md` says to build one. This feature
adds a panel element, and it puts two new controls on a dense form. It also has more
than two states.

| Question                          | Answer                                                                                                                |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| A cycle with no capacity          | Draw nothing. No meter, no alert, and no reserved space. Most cycles will never carry a capacity.                     |
| The `ok` verdict                  | Show the meter and no alert. An always-visible green banner trains the user to ignore the amber one.                  |
| The toggle with no capacity       | Render it, and disable it. The mode is meaningless with no number, and hiding it hides the feature.                   |
| The two alerts                    | One slot, one alert at a time. The color and the second sentence change, and the layout does not move.                |
| The refusal message               | Name three numbers: the incoming points, the current points, and the capacity. "Over capacity" alone is not enough.   |
| The meter above capacity          | Cap the bar at 100% and put the real number in the label. A bar that overflows its track reads as a rendering defect. |
| A project with no points estimate | Both controls are absent, not disabled. A disabled control invites a question that has no good answer.                |

`packages/types` is a built package. After the type change, run
`pnpm --filter @plane/types build` before any `check:types`, or the new member
reports as missing.

## Permissions

No new permission class. Each endpoint keeps the class it has today.

| Role                             | Can do                                                       | Cannot do                       |
| -------------------------------- | ------------------------------------------------------------ | ------------------------------- |
| Workspace owner, workspace admin | Set the capacity and the mode. Read every verdict.           | Force a write past the capacity |
| Project admin                    | Set the capacity and the mode. Read every verdict.           | Force a write past the capacity |
| Project member                   | Set the capacity and the mode. Read every verdict.           | Force a write past the capacity |
| Guest                            | Read the capacity verdict on a cycle the guest already sees. | Set anything. Add work items.   |

Both columns ride on the cycle update route, which already restricts writes to admin
and member. No new check is needed. Open question 1 asks whether a member setting the
capacity is correct, because that lets a member raise the number that blocks them.

## Test plan

### Backend

The precedent for a cycle contract test is
`apps/api/plane/tests/contract/app/test_cycle_issue_app.py`. The precedent for a
pure-function unit test is `apps/api/plane/tests/unit/utils/`.

Unit, in `apps/api/plane/tests/unit/utils/test_cycle_capacity.py`:

- `test_verdict_is_not_set_when_capacity_is_null` proves that `NULL` disables the gate.
- `test_verdict_is_not_set_when_project_estimate_is_categories` proves the estimate rule.
- `test_verdict_is_ok_at_28_of_40` proves the plain case the requester gave.
- `test_verdict_is_ok_at_40_of_40` proves that the capacity itself is not over the
  capacity. This is the boundary the whole feature turns on.
- `test_verdict_is_warn_at_41_of_40_in_warn_mode` proves the first point past it.
- `test_verdict_is_block_at_41_of_40_in_block_mode` proves the same in the other mode.
- `test_write_allowed_when_projected_equals_capacity_in_block_mode` proves that a
  cycle can fill to exactly its capacity.
- `test_write_refused_when_projected_passes_capacity_in_block_mode` proves the one
  refusal rule.
- `test_write_allowed_when_projected_passes_capacity_in_warn_mode` proves that warn
  mode never refuses.
- `test_write_allowed_when_incoming_points_are_negative` proves that lowering an
  estimate always passes.
- `test_capacity_of_zero_refuses_any_add_worth_a_point` proves that 0 and `NULL`
  differ. A capacity of 0 allows a sum of 0, and refuses a sum of 1.

Contract, in `apps/api/plane/tests/contract/app/test_cycle_capacity_app.py`:

- `test_patch_sets_capacity_and_mode_and_response_returns_both` proves the read
  serializer edit.
- `test_patch_rejects_an_unknown_capacity_mode` proves the choices validation.
- `test_add_work_items_under_capacity_returns_201_with_verdict_ok`.
- `test_add_work_items_to_exactly_capacity_returns_201_with_verdict_ok` proves that
  filling a cycle to 40 of 40 raises no alert in either mode.
- `test_add_work_items_past_capacity_in_warn_mode_returns_201_with_verdict_warn` proves
  that warn mode does not refuse.
- `test_add_work_items_past_capacity_in_block_mode_returns_400_with_error_code` proves
  the gate and the `error_code`.
- `test_remove_work_item_from_a_blocked_cycle_returns_200` proves that a full cycle is
  not frozen.
- `test_lower_estimate_in_a_blocked_cycle_returns_200` proves the estimate rule that
  the requester named.
- `test_refused_request_writes_no_cycle_issue_row` proves that the refusal is atomic.
  The session path writes twice, at `cycle/issue.py:264` and `:299`, and no
  transaction wraps them today, so this test fails before slice 3 adds one.
- `test_gate_does_not_run_for_an_upcoming_cycle` proves the active-cycle scope.
- `test_gate_does_not_run_for_a_completed_cycle` proves the same on the other side.
- `test_progress_endpoint_returns_capacity_status`.
- `test_estimate_point_raise_past_capacity_in_block_mode_returns_400` proves path 5.
- `test_transfer_past_capacity_in_block_mode_returns_400` proves path 4.
- `test_draft_promotion_past_capacity_in_block_mode_returns_400` proves path 3.
- `test_intake_accept_past_capacity_in_block_mode_returns_400` proves that the intake
  route inherits the gate through the shared serializer at
  `apps/api/plane/app/views/intake/base.py:414`.
- `test_estimate_point_value_edit_does_not_return_400` proves the ungated path on
  purpose. An estimate value edit must still succeed, and the cycle then reads the
  alert.
- `test_guest_cannot_set_capacity` is the permission case.

Contract, in `apps/api/plane/tests/contract/api/test_cycle_capacity_api.py`:

- `test_external_add_past_capacity_in_block_mode_returns_400` proves that the
  `X-API-Key` surface carries the same gate. Without this test the second surface
  stays open, which is the defect this feature is most likely to ship.

Run every command through the `plane-test-api` skill.

### Frontend

`apps/web` ships no test suite and no vitest config today. No automated frontend test
is possible. Verify by hand against the running stack, and record in the pull request
what was clicked.

- The capacity input and the toggle both save, and both survive a reload.
- The meter renders at the right width for 28 of 40 points.
- No alert appears at 40 of 40 points, in either mode.
- The amber alert appears at 41 of 40 points in warn mode, and a further add succeeds.
- Removing a work item clears the alert without a page reload.
- A refused add through the cycle modal shows the toast with the three numbers.
- A refused add through a drag between board groups shows the same toast, and not the
  generic one. This is the path the catch at `use-group-dragndrop.ts:77` changes.
- After a refused add, the board does not show the item.
- A cycle with no capacity renders no meter and no alert.
- A project with a categories-type estimate renders neither control.

## Slices

The spine is data model, then backend, then frontend. Seams come from
`.claude/skills/develop-slice/SEAMS.md`.

| #   | Slice                                  | Files                                                                                                                                                                                                                                                                    | Depends on | Proof                                                                                                                                                                                                                                                      | Seam                                                          |
| --- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| 1   | The two columns and both API surfaces  | `apps/api/plane/db/models/cycle.py`, a new migration, `apps/api/plane/app/serializers/cycle.py`, `apps/api/plane/api/serializers/cycle.py`                                                                                                                               | Nothing    | `test_patch_sets_capacity_and_mode_and_response_returns_both`, plus `test_patch_rejects_an_unknown_capacity_mode`                                                                                                                                          | A DRF view through `session_client`                           |
| 2   | The evaluator                          | `apps/api/plane/utils/cycle_capacity.py`, `apps/api/plane/tests/unit/utils/test_cycle_capacity.py`                                                                                                                                                                       | 1          | The ten unit tests above. No database and no HTTP.                                                                                                                                                                                                         | A pure function, called directly                              |
| 3   | The gate on the two add-to-cycle paths | `apps/api/plane/app/views/cycle/issue.py`, `apps/api/plane/api/views/cycle.py`                                                                                                                                                                                           | 2          | `test_add_work_items_past_capacity_in_block_mode_returns_400_with_error_code`, `test_refused_request_writes_no_cycle_issue_row`, `test_external_add_past_capacity_in_block_mode_returns_400`                                                               | A DRF view through `session_client` and an `X-API-Key` client |
| 4   | The gate on the other three paths      | `apps/api/plane/utils/cycle_transfer_issues.py`, `apps/api/plane/app/views/workspace/draft.py`, `apps/api/plane/app/serializers/issue.py`, `apps/api/plane/api/serializers/issue.py`                                                                                     | 2          | `test_transfer_past_capacity_in_block_mode_returns_400`, `test_draft_promotion_past_capacity_in_block_mode_returns_400`, `test_estimate_point_raise_past_capacity_in_block_mode_returns_400`, `test_intake_accept_past_capacity_in_block_mode_returns_400` | A DRF view through `session_client`                           |
| 5   | `capacity_status` on the progress body | `apps/api/plane/app/views/cycle/base.py`                                                                                                                                                                                                                                 | 2          | `test_progress_endpoint_returns_capacity_status`                                                                                                                                                                                                           | A DRF view through `session_client`                           |
| 6   | The types                              | `packages/types/src/cycle/cycle.ts`                                                                                                                                                                                                                                      | 5          | `pnpm --filter @plane/types build` then `pnpm --filter web check:types` exits 0                                                                                                                                                                            | A pure type change, so no runtime seam                        |
| 7   | The form, the meter, the alerts        | `apps/web/core/components/cycles/form.tsx`, `apps/web/core/components/cycles/analytics-sidebar/issue-progress.tsx`, `apps/web/core/components/cycles/active-cycle/progress.tsx`, `apps/web/core/hooks/use-group-dragndrop.ts`, `packages/i18n/src/locales/en/cycle.json` | 6          | Manual verification against the running stack, recorded in the pull request                                                                                                                                                                                | None. No web suite exists.                                    |

Slice 3, slice 4, and slice 5 each depend on slice 2 and on nothing else. They can run
in parallel worktrees, one `plane-env-create` stack each. Every other pair runs in
sequence.

Slice 1, 2, 3, 4, and 5 need a Docker stack, because each runs a backend test. Slice 6
needs a worktree only. Slice 7 needs a stack to verify by hand.

## Rollout

- **Feature flag?** No. Both columns are additive, and a `NULL` capacity leaves the
  product exactly as it is today. The gate cannot fire until a person types a
  capacity. A flag therefore protects nobody.
- **Staged steps**:
  1. Merge slice 1. The columns exist and both API surfaces accept them. No user sees
     a change.
  2. Merge slice 2. The evaluator exists and no caller uses it.
  3. Merge slice 3, slice 4, and slice 5. The gate runs. Only a cycle with a capacity
     is affected, and no cycle has one yet.
  4. Merge slice 6 and slice 7. The controls become visible, and a person can set a
     capacity for the first time.
- **Rollback**: Revert slice 7, then 6, then 5, 4, 3, and 2. Reverse the migration with
  the `plane-db-downgrade` skill before you revert slice 1. Two faster partial
  rollbacks exist. Set every `cycles.capacity` back to `NULL`, which disables the gate
  everywhere. Or set every `cycles.capacity_mode` to `warn`, which keeps the numbers
  and stops every refusal.

## Open questions

| #   | Question                                                                          | Decides     | Resolved                                                                                                                                       |
| --- | --------------------------------------------------------------------------------- | ----------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Can a project member set the capacity and the mode, or admin only?                | Product     | Open. The spec lets a member set both, because the cycle update route already allows it. That lets a member raise the number that blocks them. |
| 2   | Does a write that lands on exactly the capacity succeed in block mode?            | Product     | 2026-08-14. Yes. 28 of 40 is green, 40 of 40 is green, and 41 of 40 trips the wire. Both comparisons use `>`.                                  |
| 3   | Does the active check use `project.timezone` or `Cycle.timezone`?                 | Engineering | Open. The spec follows the existing definition, which uses `project.timezone`.                                                                 |
| 4   | Where does the capacity number live?                                              | Product     | 2026-08-14. On the cycle only. It is optional, and a person can change it later.                                                               |
| 5   | Percent thresholds, or one number and a toggle?                                   | Product     | 2026-08-14. One number and a toggle. No percent appears anywhere in the feature.                                                               |
| 6   | Does a warn verdict need a notification or a webhook?                             | Product     | 2026-08-14. No. It is a non-goal for this release.                                                                                             |
| 7   | Does a project admin need a workspace-wide view of cycles that are over capacity? | Product     | Open. It is out of scope here, and it is a candidate for a second feature.                                                                     |

## Assumptions

Five questions were asked. Everything below is an assumption, and a reviewer can
overturn any of it.

1. The capacity counts every work item in the cycle, and not only the incomplete ones.
   A completed point still consumed the cycle.
2. A cancelled work item still counts. The existing point sum includes it, and this
   feature does not change that sum.
3. A sub-item counts once, on its own row. The feature does not roll a child into a
   parent.
4. A person who lowers the capacity below the current point sum succeeds. The gate
   runs on a work item write, and not on a capacity write. The cycle then shows the
   alert, and the next add fails in block mode.
5. A person who switches the mode from `warn` to `block` on a cycle that already sits
   over its capacity succeeds. The switch is not a work item write.
6. `capacity` holds a whole number. No project needs a capacity of 12.5 points.
7. The default mode is `warn`. A new capacity therefore never refuses a write until
   somebody chooses that.

Assumption 4 and assumption 5 are the two most likely to be wrong. Both trade a strict
rule for a usable one. A lead who must cut the capacity mid-cycle, or tighten the mode
mid-cycle, cannot be blocked by the work that the cycle already holds.

## Risks

| Risk                                                           | Impact                                                                                       | Mitigation                                                                                                                  |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| The gate lands on one API surface only                         | A script with an `X-API-Key` walks past the capacity, and the product looks broken           | Slice 3 carries a test on the external surface, in a separate file                                                          |
| A path in the table is missed                                  | The point sum passes the capacity through a path nobody tested                               | The table names five paths and three exemptions. Slice 3 and slice 4 together cover all five                                |
| The refusal is not atomic                                      | A 400 leaves a `cycle_issues` row behind, so the cycle holds work the API says it refused    | No path opens `transaction.atomic()` today. Slice 3 and slice 4 add one, and the gate runs before the first write           |
| The read serializer edit is missed                             | The capacity saves and vanishes on reload. The defect reads as a frontend bug and is not one | Slice 1 asserts both fields in the response body, and not only a 200                                                        |
| The migration number collides with the cycle goal branch       | The second branch to merge fails `migrate` with two `0123` nodes                             | Renumber after the rebase. The spec names the head as `0122`                                                                |
| A person edits `EstimatePoint.value` and every cycle sum moves | A cycle sits above its capacity with no refused request behind it                            | Named as an ungated path above. The evaluator measures the whole cycle, so the panel shows the alert and the next add fails |
| The drag path shows a generic toast                            | The refusal message never reaches the user on the path they use most                         | Slice 7 changes the catch at `use-group-dragndrop.ts:77-93` to read the error body                                          |
| A project with a categories estimate sets a capacity by API    | The point sum is 0, so the gate never fires, and the number lies to the team                 | The evaluator returns `not_set` for that project, and the UI hides both controls                                            |
| Block mode freezes a cycle that a team needs to fix            | Nobody can bring the cycle back under its capacity                                           | Removal, deletion, and a lower estimate all pass in both modes. Two contract tests assert it                                |
| The extra query slows down every add-to-cycle write            | A hot write path gains a point sum aggregate                                                 | The evaluator runs one aggregate over `cycle_issues`, and it runs only when `capacity` is not `NULL`                        |
