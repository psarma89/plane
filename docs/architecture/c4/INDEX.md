# C4 Architecture Diagrams

Structural view of Plane with the [C4 model](https://c4model.com/). Four zoom levels, from system context down to components.

Read [`AGENTS.md`](./AGENTS.md) before you add a page. Follow [`TEMPLATE.md`](./TEMPLATE.md).

## Levels

| Level | Scope | Page |
| --- | --- | --- |
| **L1 Context** | Actors, Plane as one box, external systems | `l1-context.md` |
| **L2 Containers** | Deployable units and the traffic between them | `l2-containers.md` |
| **L3 Frontend** | Components inside the React Router apps | `l3-frontend.md` |
| **L3 Backend** | Components inside the Django API | `l3-backend.md` |
| **L3 Realtime** | Components inside the Hocuspocus collaboration server | `l3-realtime.md` |
| **Deployment** | Container to deployment target mapping | `deployment.md` |

Start at L1 for the shape of the product. Drill into L2 and L3 as needed.

> No page exists yet. This index lists the planned page set. Add a page with [`TEMPLATE.md`](./TEMPLATE.md), then replace its row above with a link and a one-line summary.

## Format

Every page uses Mermaid. GitHub, VS Code, and most markdown viewers render it without a plugin. Every diagram has a prose table below it that carries the detail.

## Related

- [../INDEX.md](../INDEX.md) is the architecture landing page.
- [../system/INDEX.md](../system/INDEX.md) traces one runtime concern across apps.
- [../application/INDEX.md](../application/INDEX.md) names the files inside one app.
- [../../devops/infra/INDEX.md](../../devops/infra/INDEX.md) covers each deployment target in detail.
