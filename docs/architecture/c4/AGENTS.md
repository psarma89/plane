# C4 Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. This file adds the rules that apply to every folder under `docs/architecture/c4/`.

The [C4 model](https://c4model.com/) gives four zoom levels. Together they cover system architecture and application architecture, so this tree holds every architecture page.

## This folder is a router

`docs/architecture/c4/` holds no pages of its own. It has no `TEMPLATE.md`. Every page lives in one of four level folders.

| Folder | Level | Scope |
| --- | --- | --- |
| [`context/`](./context/INDEX.md) | L1 | Actors, Plane as one box, every external system |
| [`containers/`](./containers/INDEX.md) | L2 | Deployable units, the traffic between them, and runtime flows that cross them |
| [`components/`](./components/INDEX.md) | L3 | Modules, routes, stores, and models inside one container |
| [`code/`](./code/INDEX.md) | L4 | Classes and calls for one hard algorithm. Rare. |

Each level folder carries its own `AGENTS.md` with the rules for that level. Read this file, then that one.

## Rules that apply at every level

The sections below hold once. A level folder repeats nothing from here.

### Naming

- Files use `NN-<slug>.md`, zero-padded from `01`, inside each level folder.
- A new page takes the next free number in its folder. Do not renumber an existing page.
- Sections use `## N.1` and `## N.2`, and match the page number.
- Numbers restart at `01` in each level folder. `context/01-...` and `components/01-...` can both exist.

### Diagram syntax

- Use Mermaid C4 syntax for a structural diagram: `C4Context`, `C4Container`, `C4Component`.
- Use `sequenceDiagram` for a runtime flow, and `flowchart` for a decision path.
- Keep one diagram under about 15 nodes. Split a larger diagram into sections in the same page.

### Labels

- Keep a node description to 3 to 6 words. Put the detail in the prose table.
  - Good: `"React Router app, MobX stores"`
  - Bad: `"The main React Router web application that uses MobX stores for reactive state"`
- Keep a relationship label to 1 to 3 words. It names what flows, not why.
  - Good: `Rel(web, api, "REST, JSON")`
  - Bad: `Rel(web, api, "Sends REST requests to fetch and update work items")`
- Use an empty label (`""`) when the boundary already explains the link.

### Node names

- In L1 and L2, use the real product or service name: `Caddy`, `PostgreSQL`, `Valkey`, `RabbitMQ`, `MinIO`.
- In L2, use the Compose service name in the node ID, so a reader can match the diagram to `docker-compose.yml`.
- In L3 and L4, code-level names are correct: `apps/web/core/store/`, `plane/app/views/`.
- Put the version or tier in the description, not the label. Example: `"PostgreSQL 15.7"`.

### Node order and grouping

- Mermaid lays out nodes in declaration order. Declare a node where you want it to appear.
- Group related nodes together to cut arrow crossing.
- Declare relationships in the same order as the nodes they connect.
- Use `Enterprise_Boundary` to group external systems by purpose, for example "Object storage" or "Email".
- Mark an optional or edition-gated unit in the boundary label. Example: `"(Commercial editions only)"`.

### Prose tables

Every diagram needs a table below it. The table is the source of truth.

- If a node is in the diagram, it must have a row in the table.
- The table carries the protocol, the port, the data class, and the availability.
- Keep the diagram and the table in sync. A node with no row makes the page wrong.

### Related feature specs

Every page carries a `### Related feature specs` table after the title. Add a row when a spec drives a change to the page. Use the status values `Shipped`, `Partial`, or `Draft`.

### When not to add a page

- A new route or endpoint inside a documented module. Update the existing L3 page.
- A bug fix or a refactor that keeps the same structural relationships.
- A feature that fits inside an existing component boundary.

Update an existing page before you create a new one. A thin page set that stays true beats a wide page set that rots.
