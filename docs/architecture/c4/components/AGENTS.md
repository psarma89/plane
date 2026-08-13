# L3 Components Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. It holds the naming, diagram, label, and table rules for every level. This file adds only what is specific to L3.

An L3 page opens **one container**. It names the modules, routes, stores, and models inside it. A reader must be able to start work without a code search.

This is where application architecture lives.

## What belongs here

| Subject | Belongs here |
| --- | --- |
| The route, store, service, and model behind one screen | Yes |
| Which MobX store owns which observable, and who reads it | Yes |
| The view, serializer, and model behind one endpoint group | Yes |
| The module layout inside `apps/api` | Yes |
| How a Celery task reaches `worker` | No. Crosses containers. Use [`../containers/`](../containers/INDEX.md). |
| Every external service Plane calls | No. Use [`../context/`](../context/INDEX.md). |
| The line-by-line logic of one hard function | No. Use [`../code/`](../code/INDEX.md). |

If a page crosses a container boundary, it is L2. Move it.

## One page per container, or per journey inside a container

Both shapes are valid. Pick by size.

| Shape | Use when | Example title |
| --- | --- | --- |
| Per container | The container is small, or you need the map first | `Components inside apps/live` |
| Per journey | The container is large and the journey is self-contained | `Web: work item detail and activity` |

`apps/api` and `apps/web` are large. Prefer per journey there. Name the container in the title. Example: `# 4. Web: cycles and modules`.

A journey is a thing a user sets out to do: sign in, plan a cycle, publish a board, administer an instance.

- **New page**: The feature adds a journey no existing page covers.
- **Update an existing page**: The feature changes behavior inside a documented journey.

A new tab on an existing settings screen updates the settings page. It does not earn a new page.

## Required sections

Follow [`TEMPLATE.md`](./TEMPLATE.md). Every page needs these sections.

| Section | Content |
| --- | --- |
| Header block | `Last reviewed` stamp, the container, and the scope |
| Related feature specs | Table of specs that drove the current behavior |
| Diagram | A Mermaid `C4Component` or `flowchart` inside the container |
| Key files | Table that maps each layer to a real path |
| Key components | The components a reader will edit, and what each renders |
| Key state | The store, its observables, and its actions |
| Key data models | The Django models the journey reads and writes |
| Data flow | A Mermaid diagram plus three summary bullets |
| Acceptance criteria | Rules taken from the code, not from intent |
| Verification | The tests and the command |

Delete a section that does not apply to the container. An `apps/live` page has no MobX store. Say so rather than leaving an empty table.

## Key files table

The table is the highest-value part of the page. Fill every row that applies. Delete a row that does not.

| Layer | Path shape |
| --- | --- |
| Route | `apps/web/app/routes/...` |
| Layout | `apps/web/core/layouts/...` |
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
| Permission | `apps/api/plane/app/permissions/...` |

## Acceptance criteria

Write each criterion from the code that enforces it, not from the product intent.

- Good: "A cycle end date before its start date returns 400 from the serializer."
- Bad: "Dates are validated correctly."

If a rule exists only in the UI, say so. Write "client-side only".

## Repo rules to respect

- Every `bg-*` class follows `packages/tailwind-config/AGENTS.md`. Name the Canvas, Surface, or Layer choice when a page documents UI.
- Every user-facing string lives in `packages/i18n/src/locales`. Name the translation key, not the English text.
- State lives in MobX stores. Name the store and the observable, not a local copy.
- Name the DRF permission class that guards each endpoint.
