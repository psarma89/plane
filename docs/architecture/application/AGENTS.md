# Application Architecture Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. This file adds the rules that apply to `docs/architecture/application/`.

An application page describes **one user journey inside one app**. It names the files. A reader must be able to open the journey and start work without a code search.

## What belongs here

A page belongs here when it names components, stores, models, or routes inside a single unit of `apps/`.

| Subject | Belongs here | Why |
| --- | --- | --- |
| How the work item detail panel loads and saves a field | Yes | One app, one journey |
| Which MobX store owns cycle state and who subscribes | Yes | One app |
| How God Mode instance settings persist | Yes | One app |
| How a published board renders in `apps/space` | Yes | One app |
| How Celery delivers a task to a worker | No | Crosses units. Use [`../system/`](../system/INDEX.md). |
| The container boundary between `web` and `api` | No | Structural. Use [`../c4/`](../c4/INDEX.md). |

## One page per journey

A journey is a thing a user sets out to do: sign in, plan a cycle, publish a board, administer an instance.

- **New page**: The feature adds a journey no existing page covers.
- **Update an existing page**: The feature changes behavior inside a journey a page already covers.

A new tab on an existing settings screen updates the settings page. It does not earn a new page.

## Naming

- Files use `NN-<slug>.md`, zero-padded from `01`.
- A new page takes the next free number. Do not renumber an existing page.
- Sections use `## N.1` and `## N.2`, and match the page number.
- Name the app in the page title when the journey exists in one app only. Example: `# 7. Admin: instance settings`.

## Required sections

Follow [`TEMPLATE.md`](./TEMPLATE.md). Every page needs these sections.

| Section | Content |
| --- | --- |
| Related feature specs | Table of specs that drove the current behavior |
| Key files | Table that maps each layer to a real path |
| Key components | The components a reader will edit, and what each renders |
| Key data models | The Django models the journey reads and writes |
| Data flow | A Mermaid diagram plus three summary bullets |
| Acceptance criteria | Rules taken from the code, not from intent |

## Key files table

The table is the highest-value part of the page. Fill every row that applies. Delete a row that does not.

| Layer | Path shape |
| --- | --- |
| Route | `apps/web/app/routes/...` |
| Page or layout | `apps/web/core/layouts/...` |
| Component | `apps/web/core/components/...` |
| Hook | `apps/web/core/hooks/...` |
| Service | `apps/web/core/services/...` |
| Store | `apps/web/core/store/...` |
| Shared package | `packages/ui/...`, `packages/types/...` |
| API URL | `apps/api/plane/app/urls/...` |
| API view | `apps/api/plane/app/views/...` |
| Serializer | `apps/api/plane/app/serializers/...` |
| Model | `apps/api/plane/db/models/...` |
| Background task | `apps/api/plane/bgtasks/...` |

## Acceptance criteria

Write each criterion from the code that enforces it, not from the product intent.

- Good: "A cycle end date before its start date returns 400 from the serializer."
- Bad: "Dates are validated correctly."

If a rule exists only in the UI, say so. Write "client-side only".

## Repo rules to respect

- Every `bg-*` class follows `packages/tailwind-config/AGENTS.md`. Name the Canvas, Surface, or Layer choice when a page documents new UI.
- Every user-facing string lives in `packages/i18n/src/locales`. Name the translation key, not the English text.
- State lives in MobX stores. Name the store and the observable, not a local copy.
