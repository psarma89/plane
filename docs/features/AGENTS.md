# Feature Docs Conventions

A feature page states **what we plan to build or change, and why**. It is a specification, not a description of the current system. The current system lives in [`../architecture/`](../architecture/INDEX.md).

Every page lives in one of three sub-folders.

| Sub-folder | Holds |
| --- | --- |
| [`new/`](./new/INDEX.md) | A capability that does not exist yet |
| [`changes/`](./changes/INDEX.md) | A change to behavior that already ships |
| [`bugfixes/`](./bugfixes/INDEX.md) | A defect: the system does not do what it claims |

## Which sub-folder gets the page

Ask the questions in order. Stop at the first `yes`.

| Question | Sub-folder |
| --- | --- |
| Does a user gain an ability they do not have today? | `new/` |
| Does the current behavior work as documented, and we want it to work differently? | `changes/` |
| Does the current behavior contradict what the product claims? | `bugfixes/` |

The boundary case: a defect whose fix changes documented behavior goes in `changes/`. Link to it from `bugfixes/`.

## Naming

[`../AGENTS.md`](../AGENTS.md) gives the work item ID prefix. One addition applies here: keep the work item ID in its original case, even though the rest of the slug is lower-kebab-case.

## Status

Every page carries a status in its header block. Use exactly one of five values.

| Status | Meaning |
| --- | --- |
| `Draft` | Written. Not agreed. |
| `Agreed` | Reviewed and accepted. Work can start. |
| `In progress` | Implementation started. |
| `Shipped` | Merged and released. |
| `Abandoned` | Will not be built. The reason is in the page. |

Never delete an abandoned page. Set the status to `Abandoned` and write the reason, so the next author does not re-propose it.

## A spec goes stale. Do not rewrite history.

When the built result differs from the spec, do two things.

1. Add an `## Implementation note` block at the top of the spec. State what changed and why.
2. Update the matching [`../architecture/`](../architecture/INDEX.md) page to describe the built result.

The architecture page is the source of truth for what exists. The spec is the record of what we intended.

## When a page reaches Shipped

Complete every step in the same pull request that ships the work.

1. Set the status to `Shipped`.
2. Add the pull request link to the header block.
3. Update the matching architecture page to describe the built result.
4. Add a row to the architecture page `### Related feature specs` table.
5. If the change touches a restriction, update the matching [`../security/`](../security/INDEX.md) page.
6. Update the sub-folder `INDEX.md`.

## Repo rules every spec must respect

Name these in the spec where they apply.

- Every user-facing string lives in `packages/i18n/src/locales`. Name the translation key.
- Every `bg-*` class follows `packages/tailwind-config/AGENTS.md`. Name the Canvas, Surface, or Layer choice.
- State lives in MobX stores. Name the store.
- A pull request targets `dev`.
