# C4 Diagram Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. This file adds the rules that apply to `docs/architecture/c4/`.

C4 pages describe **structure**: what the pieces are and how they connect. They never describe file-level detail. That belongs in [`../application/`](../application/INDEX.md).

## Page set

This folder uses fixed file names, not sequential numbers. The C4 model defines the levels.

| File | Level | Scope |
| --- | --- | --- |
| `l1-context.md` | L1 | Actors, Plane as one box, and every external system |
| `l2-containers.md` | L2 | Deployable units inside the Plane boundary and the traffic between them |
| `l3-frontend.md` | L3 | Components inside the React Router apps: routes, stores, shared packages |
| `l3-backend.md` | L3 | Components inside the Django API: apps, views, serializers, tasks |
| `l3-realtime.md` | L3 | Components inside the Hocuspocus collaboration server |
| `deployment.md` | Deployment | How containers map onto Docker Compose, Swarm, and Kubernetes targets |

Add a new `l3-<name>.md` page only when a major subsystem does not fit an existing L3 page. Add the new file to [`INDEX.md`](./INDEX.md) in the same commit.

## Diagram syntax

- Use Mermaid C4 syntax for structural diagrams: `C4Context`, `C4Container`, `C4Component`.
- Use `flowchart` or `sequenceDiagram` for a flow inside an L3 page.
- Keep one diagram under about 15 nodes. Split a larger diagram into sections in the same page.

## Labels

- Keep a node description to 3 to 6 words. Put the detail in the prose table.
  - Good: `"React Router app, MobX stores"`
  - Bad: `"The main React Router web application that uses MobX stores for reactive state"`
- Keep a relationship label to 1 to 3 words. It names what flows, not why.
  - Good: `Rel(web, api, "REST, JSON")`
  - Bad: `Rel(web, api, "Sends REST requests to fetch and update work items")`
- Use an empty label (`""`) when the boundary already explains the link.

## Node names

- In L1 and L2, use the real product or service name: `Caddy`, `PostgreSQL`, `Valkey`, `RabbitMQ`, `MinIO`.
- In L2, use the Compose service name in the node ID so a reader can match the diagram to `docker-compose.yml`.
- In L3, code-level names are correct: `apps/web/core/store/`, `plane/app/views/`.
- Put the version or tier in the description, not the label. Example: `"PostgreSQL 15.7"`.

## Node order and grouping

- Mermaid lays out nodes in declaration order. Declare a node where you want it to appear.
- Group related nodes together to cut arrow crossing.
- Declare relationships in the same order as the nodes they connect.
- Use `Enterprise_Boundary` to group external systems by purpose, for example "Object storage" or "Email".
- Mark an optional or edition-gated unit in the boundary label. Example: `"(Commercial editions only)"`.

## Prose tables

Every diagram needs a table below it. The table is the source of truth.

- If a node is in the diagram, it must have a row in the table.
- The table carries the protocol, the port, the data class, and the availability.
- An external systems table needs a **Data sent** column that names the data category.
- Mark an edition-gated integration with an **Availability** column. Example: `"Community and commercial"`.

## Trust boundaries

Every L2 page needs a trust boundary table. List each zone and its exposure.

| Zone | Contains | Exposure |
| --- | --- | --- |
| Internet | Browser, mobile app, webhook consumer | Public |
| Edge | `proxy` | Public ingress |
| Application | `web`, `admin`, `space`, `api`, `live`, `worker` | Internal |
| Data | `plane-db`, `plane-redis`, `plane-mq`, `plane-minio` | Internal only |

## When to update

| Trigger | Action |
| --- | --- |
| New external system integration | Add a node and a table row to `l1-context.md` |
| New container, database, or queue | Add a node and a table row to `l2-containers.md` |
| New deployment target under `deployments/` | Add a section to `deployment.md` |
| New shared package or store area | Add a section to `l3-frontend.md` |
| New Django app or Celery task group | Add a section to `l3-backend.md` |
| A system or integration is removed | Remove the node and the row |
| A service is renamed | Update the label and the row |

## When not to update

- A new route or endpoint inside an existing module. That is too granular for L3.
- A bug fix or a refactor that keeps the same structural relationships.
- A feature that fits inside an existing component boundary.
