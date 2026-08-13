# Bugfix Record Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. This file adds the rules that apply to `docs/features/bugfixes/`.

A page here records **a defect and its fix**. The system did not do what it claims. The record exists so the same class of defect does not return.

## Not every bug earns a page

Most defects need only a pull request and a test. Write a record when at least one statement is true.

| Write a record when | Reason |
| --- | --- |
| The defect reached users | The blast radius needs a written account |
| The root cause was not the obvious one | The wrong hypothesis is worth recording |
| The defect returned after an earlier fix | The pattern matters more than this instance |
| The fix crosses two or more apps | No single pull request holds the whole picture |
| The defect needed a data repair | The repair steps must be reproducible |

A one-line typo fix with a test does not need a page.

## Naming

- Files use `<WORK-ITEM-ID>-<slug>.md`. Example: `WEB-8632-stale-chunk-reload.md`.
- Without a work item ID, use `<slug>-YYYY-MM-DD.md`.
- Name the symptom in the slug, not the fix. `stale-chunk-load-failure` beats `add-reload-handler`.

## Required sections

Follow [`TEMPLATE.md`](./TEMPLATE.md). Every record needs these sections.

| Section | Content |
| --- | --- |
| Header block | Status, severity, dates, work item link, pull request link |
| Symptom | What a user observed, in their words where possible |
| Blast radius | Who was affected, how many, and for how long |
| Reproduction | The exact steps that trigger the defect |
| Root cause | The single cause, named in code |
| Fix | What changed, and why that resolves the cause |
| Regression test | The test that fails before the fix and passes after |
| Rejected hypotheses | What looked like the cause and was not |
| Follow-up | Related defects this class of bug can still cause |

## Root cause is one cause

Name one cause. A record with three causes has no cause.

- Good: "The route loader read `project.id` before the store resolved. `undefined` reached the service call."
- Bad: "A race condition and some missing validation combined with a caching issue."

If the defect genuinely needed two independent faults, say so and name both. That is rare. State that it is rare.

## Regression test is mandatory

Every record names a test that fails before the fix and passes after.

- Give the test path and the test name.
- The test name must state the rule, not the code path. See the repo testing guidance.
- If no automated test is possible, say why, and give the manual check instead. "Not testable" without a reason is not acceptable.

## Rejected hypotheses

This section is the highest-value part of the record. It saves the next reader the search you already did.

List what you suspected and why you ruled it out. Two or three entries is normal.

## Severity

Set a severity in the header block. Use exactly one of four values.

| Severity | Meaning |
| --- | --- |
| `S1` | Data loss, or the product is unusable for many users |
| `S2` | A core journey is broken. A workaround exists. |
| `S3` | A non-core journey is broken, or the defect is cosmetic and visible |
| `S4` | Cosmetic, or reachable only in an unusual path |

## Data repair

If the defect corrupted data, do two things.

1. Record the repair query or script in the record, with the affected row count.
2. If the repair is repeatable, write an SOP in [`../../sops/`](../../sops/INDEX.md) and link it.

> **Destructive:** Never paste a repair query that runs without a `WHERE` clause. State the guard.

## When the fix changes documented behavior

The record stays here. The behavior change gets a page in [`../changes/`](../changes/INDEX.md). Link the two.
