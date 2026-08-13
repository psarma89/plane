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

**Never use Mermaid C4 syntax.** GitHub bundles a Mermaid build that omits the C4 extension, so a `C4Context`, `C4Container`, or `C4Component` block renders as raw text. Mermaid also marks its own C4 support experimental, and states that "the syntax and properties can change in future releases".

Use these block types. GitHub renders all of them.

| Diagram | Block type |
| --- | --- |
| Structural view, at any level | `flowchart` |
| Runtime flow, ordered by time | `sequenceDiagram` |
| Decision path with branches | `flowchart` |
| Class and call shape, L4 only | `classDiagram` or `sequenceDiagram` |

A `flowchart` carries the C4 meaning through three devices: the node shape, the node class, and the `subgraph` boundary. The table below the diagram names the C4 element type for each node.

#### Node shapes

| C4 element | Shape | Example |
| --- | --- | --- |
| Person | Stadium | `member(["Workspace member"])` |
| Software system, external | Rectangle | `smtp["SMTP provider"]` |
| Container, application | Rectangle | `api["api<br/><i>Django, DRF</i>"]` |
| Container, data store | Cylinder | `db[("plane-db<br/><i>PostgreSQL</i>")]` |
| Container, queue | Subroutine | `mq[["plane-mq<br/><i>RabbitMQ</i>"]]` |
| Component | Rectangle | `views["plane/app/views/<br/><i>DRF viewsets</i>"]` |
| Boundary or zone | `subgraph` | `subgraph data["Data"]` |

Put the technology on a second line, in italics, after `<br/>`. Never put the technology in the node ID.

#### Node classes

Declare this block on every structural diagram. The colors match the C4 standard notation.

```
classDef person fill:#08427b,stroke:#052e56,color:#ffffff
classDef container fill:#1168bd,stroke:#0b4884,color:#ffffff
classDef ext fill:#999999,stroke:#6b6b6b,color:#ffffff
```

Apply a class with `class <id>,<id> <className>`.

Every class sets an explicit `color`. Never set a `fill` value without a `color` value, because GitHub renders the same page in a light theme and a dark theme. A fill with no text color becomes unreadable in one of them.

Leave every `subgraph` unstyled. The Mermaid default adapts to both GitHub themes, and a hard-coded boundary fill does not.

#### Relationships

- Write a required relationship as `A -->|"protocol"| B`.
- Write an optional or edition-gated relationship as `A -.->|"protocol"| B`.
- Quote every edge label. An unquoted label breaks on a comma or a colon.

### Never write a placeholder in angle brackets

Write a placeholder in braces: `{container-id}`, not `<container-id>`.

Both Mermaid and GitHub Markdown read `<container-id>` as an HTML tag and drop it. The diagram still parses, so the failure is silent: the page ships with empty boxes and blank table cells.

This rule covers a template, a diagram label, a table cell, and prose. Backticks do not make an angle bracket safe inside a Mermaid label.

### Labels

A label names the thing. The prose table carries the detail.

- Node description. Good: `"React Router app, MobX stores"`. Bad: `"The main React Router web application that uses MobX stores for reactive state"`.
- Relationship label names what flows, not why. Good: `-->|"REST, JSON"|`. Bad: `-->|"Sends REST requests to fetch and update work items"|`.
- Use no label when the boundary already explains the link.

### Node names

- In L1 and L2, use the real product or service name: `Caddy`, `PostgreSQL`, `Valkey`, `RabbitMQ`, `MinIO`.
- In L2, use the Compose service name in the node ID, so a reader can match the diagram to `docker-compose.yml`.
- In L3 and L4, code-level names are correct: `apps/web/core/store/`, `plane/app/views/`.
- Put the version or tier in the description, not the label. Read the pin from its source file.

### Node order and grouping

- Mermaid lays out nodes in declaration order. Declare a node where you want it to appear.
- Group related nodes together to cut arrow crossing.
- Declare relationships in the same order as the nodes they connect.
- Use a `subgraph` to group external systems by purpose, for example "Object storage" or "Email".
- Mark an optional or edition-gated unit in the boundary label. Example: `"Mobile app (commercial editions only)"`.
- Keep a structural diagram under 20 nodes. If it needs more, split the page or move detail down a level.

Pick the direction from the shape of the diagram, and check the rendered size.

| Shape | Direction |
| --- | --- |
| One central node with many peripheral nodes | `flowchart LR` |
| A few layers that stack, such as edge, application, data | `flowchart TB` |

GitHub scales a diagram down to the width of the page. A wide `TB` diagram therefore renders its labels too small to read. An `LR` diagram grows downward instead, and stays legible. Render the page and look at the result before you commit it.

### The diagram leads

A reader must get the answer from the picture. The prose exists to carry what a picture cannot: a protocol, a port, a version pin, a constraint.

- Put the diagram first, directly under the header block. Never open a page with a paragraph.
- Give a page one primary diagram. A second diagram needs its own reason.
- Follow the diagram with one element table and, where the page needs it, one relationship table.
- Every node inside the page boundary needs a row in the element table. A node with no row makes the page wrong.
- A node carrying the `ext` class needs no row. It sits outside the boundary and exists to give the reader context, so the page that owns it describes it instead. Link to that page.
- A node carrying the `person` class needs no row in the element table either. An actor belongs in the `Actors` table, under the role name the product uses.
- Write the rest as a short bullet list, never as paragraphs.

Delete a section that carries nothing. An empty table is worse than a missing one.

### Verify every diagram renders

A diagram that fails to parse ships as raw text. Check a page before you commit it.

```bash
npx -y @mermaid-js/mermaid-cli@11 -i docs/architecture/c4/<level>/<page>.md -o /tmp/render-check.md
```

The command reads every Mermaid block in the page. It exits `0` when all of them parse. It exits `1` and names the failing block otherwise.

Write the output to `/tmp`. The command also emits one `.svg` per block beside its output file, and no render artifact belongs in this repository.

### Related feature specs

A `### Related feature specs` table sits at the bottom of a page, under `Related`. Add a row when a spec drives a change to the page. Use the status values from [`../../features/AGENTS.md`](../../features/AGENTS.md).

Delete the table when no spec drove a change. An empty table pushes the diagram down the page for no gain.

### When not to add a page

- A new route or endpoint inside a documented module. Update the existing L3 page.
- A bug fix or a refactor that keeps the same structural relationships.
- A feature that fits inside an existing component boundary.

Update an existing page before you create a new one.
