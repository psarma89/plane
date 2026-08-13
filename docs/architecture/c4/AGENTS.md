# C4 Conventions

The [C4 model](https://c4model.com/) gives four zoom levels. Together they cover system architecture and application architecture, so this tree holds every architecture page.

Every page lives in one of four level folders.

| Folder | Level | Scope |
| --- | --- | --- |
| [`context/`](./context/INDEX.md) | L1 | Actors, Plane as one box, every external system |
| [`containers/`](./containers/INDEX.md) | L2 | Deployable units, the traffic between them, and runtime flows that cross them |
| [`components/`](./components/INDEX.md) | L3 | Modules, routes, stores, and models inside one container |
| [`code/`](./code/INDEX.md) | L4 | Classes and calls for one hard algorithm. Rare. |

Each level folder carries its own `AGENTS.md` with the rules for that level. Read this file, then that one.

## Vocabulary

C4 defines these terms. Use them with the C4 meaning, not a local meaning.

| Term | C4 definition |
| --- | --- |
| Person | An actor, role, or persona that uses the software system. |
| Software system | The highest level of abstraction. Made up of one or more containers. |
| Container | "An application or a data store. A container is something that needs to be running in order for the overall software system to work." |
| Component | "A grouping of related functionality encapsulated behind a well-defined interface." |
| Code | Classes, interfaces, objects, and functions that implement a component. |

Two rules follow from those definitions. Both decide which folder a page belongs in.

1. **A container is the unit of deployment.** A component is not. "With the C4 model, components are not separately deployable units. Instead, it's the container that's the deployable unit."
2. **Components inside one container share a process.** "All components inside a container execute in the same process space." If two things run in separate processes, they are containers, and the page is L2.

### A C4 container is not a Docker container

The C4 term predates Docker and is broader. C4 states: "From one perspective, it's unfortunate that containerisation has become popular, because many software developers now associate the term 'container' with Docker."

A C4 container is any application or data store that must run. The list includes a server-side web application, a client-side web application, a desktop application, a mobile app, a database, a blob store, a file system, a shell script, and a console application.

[`containers/`](./containers/INDEX.md) applies this to Plane and gives the rules for building a container list.

## Supplementary diagrams

Beyond the four levels, C4 defines three optional supplementary diagram types. This tree has no fifth folder. Each type files under the level of the elements it shows.

| Supplementary type | Shows | Files under | Needed for Plane |
| --- | --- | --- | --- |
| System landscape | Several software systems inside one organization | [`context/`](./context/INDEX.md) | No. Plane is one software system. |
| Dynamic | How elements work together at runtime, for one feature or use case | [`containers/`](./containers/INDEX.md) or [`components/`](./components/INDEX.md) | Yes |
| Deployment | How container instances map onto infrastructure, per deployment environment | [`containers/`](./containers/INDEX.md) | Yes |

**Dynamic diagrams can sit at more than one level.** C4 states: "you can show software systems, containers, or components interacting at runtime." File the page by the elements the diagram names. A flow between `api` and `worker` is L2. A flow between two modules inside `apps/web` is L3.

## Rules that apply at every level

The sections below hold at every level. A level folder does not repeat them.

### Naming

[`../../AGENTS.md`](../../AGENTS.md) gives the `NN-<slug>.md` rules. One addition applies here: numbering restarts at `01` in each level folder, so `context/01-...` and `components/01-...` can both exist.

### Diagram syntax

- Use Mermaid C4 syntax for a structural diagram: `C4Context`, `C4Container`, `C4Component`.
- Use `sequenceDiagram` for a runtime flow, and `flowchart` for a decision path.

### Labels

A label names the thing. The prose table carries the detail.

- Node description. Good: `"React Router app, MobX stores"`. Bad: `"The main React Router web application that uses MobX stores for reactive state"`.
- Relationship label names what flows, not why. Good: `Rel(web, api, "REST, JSON")`. Bad: `Rel(web, api, "Sends REST requests to fetch and update work items")`.
- Use an empty label (`""`) when the boundary already explains the link.

### Node names

- In L1 and L2, use the real product or service name: `Caddy`, `PostgreSQL`, `Valkey`, `RabbitMQ`, `MinIO`.
- In L2, use the Compose service name in the node ID, so a reader can match the diagram to `docker-compose.yml`.
- In L3 and L4, code-level names are correct: `apps/web/core/store/`, `plane/app/views/`.
- Put the version or tier in the description, not the label. Read the pin from its source file.

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

Every page carries a `### Related feature specs` table after the title. Add a row when a spec drives a change to the page. Use the status values from [`../../features/AGENTS.md`](../../features/AGENTS.md).

### When not to add a page

- A new route or endpoint inside a documented module. Update the existing L3 page.
- A bug fix or a refactor that keeps the same structural relationships.
- A feature that fits inside an existing component boundary.

Update an existing page before you create a new one. A thin page set that stays true beats a wide page set that rots.
