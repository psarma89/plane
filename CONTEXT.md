# Context

The vocabulary of this codebase. Read it before you name anything.

Plane renamed several product concepts and never renamed the code. A plan that says "work item" and a diff that says `Issue` describe the same thing. A reader who does not know that spends the review on reconciliation of two glossaries.

Use the code name in code. Use the product name in user-facing strings and in a plan that a non-engineer reads. Never mix the two inside one sentence.

## Where the two names differ

| Product name | Code name | Note                                                          |
| ------------ | --------- | ------------------------------------------------------------- |
| Work item    | `Issue`   | The model, the stores, and most i18n keys still say `issue`   |
| Intake       | `Intake`  | Renamed from Inbox. The models contain zero `Inbox`           |
| Cycle        | `Cycle`   | A time box, not a loop. The closest external word is "sprint" |
| Module       | `Module`  | A product grouping, never a JavaScript module                 |

`Module` is the trap. In `apps/api` it is a `ProjectBaseModel` in `apps/api/plane/db/models/module.py`, a feature grouping that a work item belongs to. In `apps/web` the same word means an ES module in almost every sentence. Say "a Module record" when you mean the product concept.

## The scoping words

Every row in this database belongs to a workspace, and most belong to a project. That is the tenancy model, and it decides which base class you extend. The model counts per base class live in [`docs/architecture/plane-patterns-census.md`](./docs/architecture/plane-patterns-census.md).

| Term      | Meaning                                         | Base class           |
| --------- | ----------------------------------------------- | -------------------- |
| Workspace | The tenant. The unit of isolation               | `WorkspaceBaseModel` |
| Project   | A container inside one workspace                | `ProjectBaseModel`   |
| Neither   | A global row, for example `User` and `APIToken` | `BaseModel`          |

Pick the base class from the question "who is allowed to see this row", never from the question "which model looks similar". `apps/api/AGENTS.md` states the rest: `BaseViewSet` applies no tenant filter, so the base class alone protects nothing.

## Words this repository uses in one sense only

| Word     | It means                                            | It never means                                          |
| -------- | --------------------------------------------------- | ------------------------------------------------------- |
| State    | A work item's workflow column, the `State` model    | React state, MobX state                                 |
| Store    | A MobX store under `apps/web/core/store/`           | A data store or a database                              |
| Service  | An API client class under `apps/web/core/services/` | A backend service or a container                        |
| Capacity | The optional point limit on one cycle               | A module assignment rule, or a person's available hours |

`Capacity` needs the row because the billing comparison table in `apps/web/core/components/workspace/billing/comparison/plans.tsx` already uses the word for a paid module assignment rule. The two are unrelated.

When you need React state or component state, write "component state". When you need the database, write "the database". A plan that reuses `State` or `Store` in the generic sense is unreadable in review.

## Naming a plan

A plan is read by someone who did not write it, so it obeys three rules.

1. Name the product concept first, then the code name once, in parentheses.
2. Name real paths. A step that names no file is not a step.
3. Never introduce a new word for a thing this file already names.

A new word for an existing concept is the most expensive thing a plan can do. It costs every later reader a lookup, and the lookup fails, because the word is in no file.
