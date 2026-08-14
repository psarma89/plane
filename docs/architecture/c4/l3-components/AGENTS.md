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
| How a Celery task reaches `worker` | No. Separate process. Use [`../l2-containers/`](../l2-containers/INDEX.md). |
| Every external service Plane calls | No. Use [`../l1-context/`](../l1-context/INDEX.md). |
| The line-by-line logic of one hard function | No. Use [`../l4-code/`](../l4-code/INDEX.md), and usually write no page. |

## Two page kinds

| Kind | Answers | Diagram |
| --- | --- | --- |
| **Structural** | Which components exist in this container, and how do they connect? | `flowchart` |
| **Dynamic** | How do components inside this container work together for one feature? | `sequenceDiagram` |

A dynamic page belongs here when every element it names shares one process. Otherwise it is L2.

State the kind in the header block.

## One structural page per container is the baseline

C4 sets the completeness bar at a component diagram for each container. One structural page per application container meets that bar, and that is the baseline here.

| Container | Structural page |
| --- | --- |
| `apps/api` | Yes |
| `apps/web` | Yes |
| `apps/admin` | Yes |
| `apps/space` | Yes |
| `apps/live` | Yes |
| `apps/proxy` | Yes |

A data store gets no page at this level. `plane-db`, `plane-redis`, `plane-mq`, and `plane-minio` hold no component that this repository owns.

Name the container in the title. Example: `# 2. apps/api: module map`.

### Journey pages come second

A journey is a thing a user sets out to do: sign in, plan a cycle, publish a board, administer an instance. `apps/api` and `apps/web` are large enough to earn several journey pages.

Write the container page first. A journey page with no container map has no context.

- **New page**: The feature adds a journey no existing page covers.
- **Update an existing page**: The feature changes behavior inside a documented journey.

A new tab on an existing settings screen updates the settings page. It does not earn a new page.

## Sections

[`TEMPLATE.md`](./TEMPLATE.md) holds the section list.

Its `Components` table is the highest-value part of a page here, because a real path saves the reader a code search. Give every diagram node a row, and give every row a path.

Delete a section that does not apply to the container. An `apps/live` page has no MobX store. Say so rather than leaving an empty table.

## Repo rules to respect

Apply these when a note touches them. Do not add a section for them.

- Every `bg-*` class follows `packages/tailwind-config/AGENTS.md`. Name the Canvas, Surface, or Layer choice when a page documents UI.
- Every user-facing string lives in `packages/i18n/src/locales`. Name the translation key, not the English text.
- State lives in MobX stores. Name the store and the observable, not a local copy.
- Name the DRF permission class that guards each endpoint.
- Write a constraint from the code that enforces it, not from the product intent. Good: "A cycle end date before its start date returns 400 from the serializer." Bad: "Dates are validated correctly." If a rule exists only in the UI, write "client-side only".
