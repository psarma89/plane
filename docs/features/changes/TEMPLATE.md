# Change: <Feature> - <What changes>

> **Status:** Draft | Agreed | In progress | Shipped | Abandoned
> **Owner:** <Name>
> **Date:** YYYY-MM-DD
> **Work item:** <Plane work item ID and link>
> **Pull request:** <Link, once one exists>

## Why now

State the trigger. What forces this change today, and not last quarter.

## Current behavior

Include the edge cases. State the behavior, not the code.

- <What happens today>
- <Edge case today>
- <Edge case today>

## New behavior

Write this as a parallel list, so a reader can diff it against the section above.

- <What will happen instead>
- <Edge case after the change>
- <Edge case after the change>

## Contract changes

Delete this section if no endpoint changes.

### `<METHOD> /api/v1/<path>`

| Aspect | Today | After |
| --- | --- | --- |
| Request field | <shape> | <shape> |
| Response field | <shape> | <shape> |
| Error code | <code and trigger> | <code and trigger> |
| Permission class | `<Class>` | `<Class>` |

## Backwards compatibility

- **Compatible?** yes / no

If `no`, name the plan.

| Plan | Detail |
| --- | --- |
| Feature flag / API version / Deprecation window / Hard cut | <The specifics> |

For a hard cut, name the check that proved no external client depends on the old behavior.

## Data changes

- **Migration needed?** yes / no. If yes: <strategy>.
- **Backfill needed?** yes / no. If yes: <strategy and expected row count>.
- **Default for existing rows**: <value and why>.
- **Migration rollback**: <How to reverse, or why it is forward-only>.

## Frontend impact

| Screen or component | Path | What changes |
| --- | --- | --- |
| <Name> | `apps/web/core/components/...` | <Change> |

- **States that change**: <loading, empty, error, or success>.
- **New affordance**: <Button, menu item, or shortcut>.
- **Background classes**: <Canvas, Surface, or Layer choice, if UI changes>.

### Copy changes

Name the key, not the English text.

| Translation key | Action | Note |
| --- | --- | --- |
| `<namespace>.<key>` | New / Changed / Removed | <Why> |

A changed key needs a review pass across every locale in `packages/i18n/src/locales`.

## Regression plan

### Flows that must not break

| Flow | Covering test | Status |
| --- | --- | --- |
| <Flow> | `<test path>` | Exists / To add / Manual |

### Manual checks

1. <Step>.
2. <Expected result>.

## Rollout

- **Feature flag?** yes / no. If yes: `<FLAG_NAME>` and its default.
- **Staged steps**:
  1. <Step>
  2. <Step>
- **Rollback**: <The exact steps to restore the current behavior>.

## Related

| Page | Why it matters here |
| --- | --- |
| [<Architecture page>](../../architecture/application/NN-slug.md) | The journey this change alters |
| [<Bugfix record>](../bugfixes/<slug>.md) | The defect that triggered this change |
