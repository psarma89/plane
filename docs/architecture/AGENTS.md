# Architecture Docs Conventions

Architecture pages describe **how Plane works today**. They are not proposals. A proposal belongs in [`../features/`](../features/INDEX.md).

Every page lives under [`c4/`](./c4/INDEX.md). One structure covers every zoom level, because the [C4 model](https://c4model.com/) already spans both system architecture and application architecture.

| C4 level | Covers | Folder |
| --- | --- | --- |
| L1 Context | System architecture: actors, Plane as one box, external systems | [`c4/context/`](./c4/context/INDEX.md) |
| L2 Containers | System architecture: deployable units, traffic, runtime flows across containers | [`c4/containers/`](./c4/containers/INDEX.md) |
| L3 Components | Application architecture: modules, routes, stores, and models inside one container | [`c4/components/`](./c4/components/INDEX.md) |
| L4 Code | Application architecture: class and call detail for one hard algorithm | [`c4/code/`](./c4/code/INDEX.md) |

A separate `system/` and `application/` split is redundant. The level already states the zoom.

## Which level gets the page

Ask the questions in order. Stop at the first `yes`.

| Question | Level |
| --- | --- |
| Does the page name a user type or an external system outside Plane? | L1 `context/` |
| Does the page cross a container boundary, at rest or at runtime? | L2 `containers/` |
| Does the page name files, modules, stores, or models inside one container? | L3 `components/` |
| Does the page trace one algorithm through classes and calls? | L4 `code/` |

If a subject fits two levels, write the deeper page and link up. Each level folder gives its own boundary cases.

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
| New deployable unit, queue, or data store | [`c4/containers/`](./c4/containers/INDEX.md) and [`../devops/infra/`](../devops/infra/INDEX.md) |
| New external system integration | [`c4/context/`](./c4/context/INDEX.md) |
| New module, store, or model inside one app | [`c4/components/`](./c4/components/INDEX.md) |
| New or changed client surface | [`../clients/`](../clients/INDEX.md) |
| A feature spec reaches shipped state | The matching architecture page, plus the spec status |

## Relationship to feature specs

- A spec in `../features/` states what to build. An architecture page states what exists.
- When a feature ships, update the architecture page to match the built result, not the proposed design.
- If a spec goes stale, add an implementation note at the top of the spec. Do not delete the spec.
- Every architecture page carries a `### Related feature specs` table. Add a row when a spec drives a change to the page.
