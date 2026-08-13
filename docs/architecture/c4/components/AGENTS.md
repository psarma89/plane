# L3 Components Conventions

An L3 page opens **one container**. It names the modules, routes, stores, and models inside it. A reader must be able to start work without a code search.

This is where application architecture lives.

## The process test

[`../AGENTS.md`](../AGENTS.md) defines a component and states that components inside one container share a process. One test follows, and it decides L2 against L3.

**If two things run in separate processes, they are containers, and the page is L2.**

| Pair | Same process | Level |
| --- | --- | --- |
| A route and the store it reads, in `apps/web` | Yes | L3 |
| A Django view and its serializer | Yes | L3 |
| `api` and `worker` | No | L2 |
| `web` and `live` | No | L2 |
| A Celery task definition and the view that enqueues it | Yes, both live in the `api` process | L3 |
| A Celery task running in `worker` and the view that enqueued it | No | L2 |

The last two rows matter. Where the task code lives is L3. Where the task executes is L2.

## What belongs here

| Subject | Belongs here |
| --- | --- |
| The route, store, service, and model behind one screen | Yes |
| Which MobX store owns which observable, and who reads it | Yes |
| The view, serializer, and model behind one endpoint group | Yes |
| The module layout inside `apps/api` | Yes |
| A runtime flow between two modules in the same process | Yes, dynamic kind |
| How a Celery task reaches `worker` | No. Separate process. Use [`../containers/`](../containers/INDEX.md). |
| Every external service Plane calls | No. Use [`../context/`](../context/INDEX.md). |
| The line-by-line logic of one hard function | No. Use [`../code/`](../code/INDEX.md), and usually write no page. |

## Two page kinds

| Kind | Answers | Diagram |
| --- | --- | --- |
| **Structural** | Which components exist in this container, and how do they connect? | `C4Component` |
| **Dynamic** | How do components inside this container work together for one feature? | `sequenceDiagram` |

A dynamic page belongs here when every element it names shares one process. Otherwise it is L2.

State the kind in the header block.

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

## Sections

[`TEMPLATE.md`](./TEMPLATE.md) holds the section list and the key files table.

Its key files table is the highest-value part of a page here, because it saves the reader a code search. Fill every row that applies.

Delete a section that does not apply to the container. An `apps/live` page has no MobX store. Say so rather than leaving an empty table.

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
