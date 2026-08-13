# Change Spec Conventions

A page here specifies **a change to behavior that already ships**. The value of the page is the contrast: what happens today, and what will happen instead.

## Naming

- Files use `<WORK-ITEM-ID>-<slug>-YYYY-MM-DD.md`, or `<slug>-YYYY-MM-DD.md` without a work item.
- The date is mandatory here. One feature can change several times. The date keeps the record ordered.
- Never edit an old change page to describe a newer change. Write a new page.

## Current behavior against new behavior

Write them as parallel lists so a reader can diff them by eye.

- Include the edge cases in both. A change spec that only covers the happy path hides the risk.
- State the behavior, not the code. "A cycle with no end date sorts last" beats "the queryset orders by `end_date`".
- If the current behavior is a defect, link the record in [`../bugfixes/`](../bugfixes/INDEX.md).

## Backwards compatibility is mandatory

Answer with `yes` or `no`. Never leave it blank.

If the answer is `no`, name the plan.

| Plan | Use when |
| --- | --- |
| Feature flag | The old and the new behavior can run side by side |
| API version | An external client depends on the old response shape |
| Deprecation window | The old behavior must keep working for a stated period |
| Hard cut | No external client depends on the behavior. State how you confirmed that. |

A `Hard cut` with no evidence is not a plan. Name the check you ran.

## Regression plan is mandatory

List the flows that must not break. A change spec without this section is incomplete.

For each flow, name the test that covers it. If no test covers it, write the test in the same pull request or state the manual step.

## Copy changes

Every user-facing string change touches `packages/i18n/src/locales`.

- Name the translation key, not the English text.
- State whether the key is new, changed, or removed.
- A changed key needs a review pass across every locale. See the repo translation guidance.

## After the change ships

Follow the checklist in [`../AGENTS.md`](../AGENTS.md). Set the status to `Shipped`, then update the matching [`../../architecture/`](../../architecture/INDEX.md) page to describe the new behavior.
