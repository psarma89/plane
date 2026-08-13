# Architecture Docs Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. This file adds the rules that apply to `docs/architecture/`.

Architecture pages describe **how Plane works today**. They are not proposals. A proposal belongs in [`../features/`](../features/INDEX.md).

## This folder is a router

`docs/architecture/` holds no pages of its own. It has no `TEMPLATE.md`. Every page lives in one of three sub-folders.

| Sub-folder | Zoom level | Answers |
| --- | --- | --- |
| [`c4/`](./c4/INDEX.md) | Whole product | What are the pieces and how do they connect? |
| [`system/`](./system/INDEX.md) | Across apps | How does a runtime concern work end to end? |
| [`application/`](./application/INDEX.md) | Inside one app | Which files build this screen or endpoint? |

## Which sub-folder gets the page

Ask the questions in order. Stop at the first `yes`.

| Question | Sub-folder |
| --- | --- |
| Does the page draw a boundary between containers, actors, or external systems? | `c4/` |
| Does the concern cross two or more of `apps/`, and does it exist at runtime? | `system/` |
| Does the page name components, stores, models, or routes inside one app? | `application/` |

Examples:

| Page subject | Sub-folder |
| --- | --- |
| The set of deployable containers and the traffic between them | `c4/` |
| How a Celery task reaches a worker and reports failure | `system/` |
| How Yjs document sync works across `apps/live` and `apps/web` | `system/` |
| How the work item detail panel loads and saves a field | `application/` |
| Which MobX store owns cycle state in `apps/web` | `application/` |

If a subject fits two sub-folders, write the deepest page and link up. A `system/` page can link to an `application/` page for file-level detail.

## Scope of the repo

Plane is a pnpm and Turbo monorepo. Name the real paths.

| Unit | Path | Stack |
| --- | --- | --- |
| REST API and server | `apps/api` | Django, Django REST Framework, Celery |
| Main web app | `apps/web` | React Router 7, Vite, MobX |
| Instance admin (God Mode) | `apps/admin` | React Router 7, Vite |
| Public publish app | `apps/space` | React Router 7, Vite |
| Real-time collaboration server | `apps/live` | Node, Express, Hocuspocus, Yjs |
| Reverse proxy | `apps/proxy` | Caddy |
| Shared packages | `packages/*` | TypeScript |
| Deployment targets | `deployments/*` | Docker, Helm, Swarm |

## Cross-folder duties

Update these pages in the same pull request that changes the code.

| Code change | Also update |
| --- | --- |
| New or changed permission, role check, or API key scope | [`../security/`](../security/INDEX.md) matching catalog page |
| New deployable unit, queue, or data store | [`./c4/l2-containers.md`](./c4/INDEX.md) and [`../devops/infra/`](../devops/infra/INDEX.md) |
| New external system integration | [`./c4/l1-context.md`](./c4/INDEX.md) |
| New or changed client surface | [`../clients/`](../clients/INDEX.md) |
| A feature spec reaches shipped state | The matching architecture page, plus the spec status |

## Relationship to feature specs

- A spec in `../features/` states what to build. An architecture page states what exists.
- When a feature ships, update the architecture page to match the built result, not the proposed design.
- If a spec goes stale, add an implementation note at the top of the spec. Do not delete the spec.
- Every `system/` and `application/` page carries a `### Related feature specs` table. Add a row when a spec drives a change to the page.
