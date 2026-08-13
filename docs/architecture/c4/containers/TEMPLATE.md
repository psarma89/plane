# N. <Title>

> **Last reviewed:** YYYY-MM-DD
> **Level:** L2 Containers
> **Kind:** Structural | Dynamic | Deployment
> **Deployment environment:** <Required on a deployment page. One environment only. Delete otherwise.>
> **Scope:** One sentence. For a dynamic page, state where the flow starts and where it ends.

### Related feature specs

| Spec | Description | Status |
| --- | --- | --- |
| [<Feature name>](../../../features/new/<slug>.md) | One-line summary | Shipped / Partial / Draft |

## N.1 Diagram

Keep the block that matches the page kind. Delete the others.

### Structural

```mermaid
C4Container
    title Plane containers

    Person(user, "Workspace member", "Uses Plane in a browser")

    Container_Boundary(plane, "Plane") {
        Container(proxy, "proxy", "Caddy", "Routes ingress by path")
        Container(web, "web", "React Router, MobX", "Workspace app")
        Container(api, "api", "Django, DRF", "REST API and auth")
        Container(worker, "worker", "Celery", "Runs deferred work")
    }

    ContainerDb(db, "plane-db", "PostgreSQL 15.7", "Primary data store")
    ContainerQueue(mq, "plane-mq", "RabbitMQ 3.13.6", "Celery broker")

    Rel(user, proxy, "HTTPS")
    Rel(proxy, web, "HTTP")
    Rel(proxy, api, "HTTP")
    Rel(api, db, "SQL")
    Rel(api, mq, "AMQP")
    Rel(mq, worker, "AMQP")
```

### Dynamic

```mermaid
sequenceDiagram
    participant U as User
    participant W as web
    participant A as api
    participant Q as plane-mq
    participant K as worker
    participant D as plane-db

    U->>W: Action
    W->>A: POST /api/v1/...
    A->>D: Write row
    A->>Q: Enqueue task
    A-->>W: 201 Created
    Q->>K: Deliver task
    K->>D: Update row
```

### Deployment

Scope this diagram to one deployment environment.

```mermaid
C4Deployment
    title Plane on <target>, <environment> environment

    Deployment_Node(host, "Host", "<OS, size>") {
        Deployment_Node(dockerEngine, "Docker Engine", "<version>") {
            Container(proxy, "proxy", "Caddy", "Ingress and TLS")
            Container(api, "api", "Django, DRF", "REST API")
            ContainerDb(db, "plane-db", "PostgreSQL 15.7", "Primary data store")
        }
    }

    Deployment_Node(dns, "DNS", "Infrastructure node") {
        Container(record, "A record", "-", "Points at the host")
    }

    Rel(record, proxy, "Resolves to")
    Rel(proxy, api, "HTTP")
    Rel(api, db, "SQL")
```

## N.2 Elements

On a dynamic page, title this section `Participants`. On a deployment page, add a `Node` column and list container instances.

| Container | Technology | Responsibility | Exposure | Compose service |
| --- | --- | --- | --- | --- |
| `proxy` | Caddy | Terminates TLS and routes ingress by path | Public | yes |
| `api` | Django, DRF | Serves REST endpoints and authentication | Internal | yes |
| `plane-db` | PostgreSQL 15.7 | Stores workspaces, projects, and work items | Internal only | yes |
| Desktop app | <framework> | Runs the workspace app on a desktop | Client device | no |
| Mobile app | iOS, Android | Runs the workspace app on a phone | Client device | no |

Source of the pins: `docker-compose.yml`. Source of the non-Compose containers: [`../../../clients/INDEX.md`](../../../clients/INDEX.md).

State what this list leaves out. A container list built only from Compose is incomplete.

## N.3 Relationships

Structural and deployment pages. Delete on a dynamic page.

| From | To | Protocol | Port | Carries |
| --- | --- | --- | --- | --- |
| `proxy` | `api` | HTTP | 8000 | REST requests |
| `api` | `plane-db` | TCP | 5432 | SQL queries |
| `api` | `plane-mq` | AMQP | 5672 | Task messages |

## N.4 Trust boundaries

Structural and deployment pages. Delete on a dynamic page.

| Zone | Contains | Exposure |
| --- | --- | --- |
| Internet | <Nodes> | Public |
| Edge | `proxy` | Public ingress |
| Application | <Nodes> | Internal |
| Data | <Nodes> | Internal only |

## N.5 Deployment nodes

Deployment pages only. Delete on a structural or dynamic page.

| Node | Type | Nested in | Holds | Instances |
| --- | --- | --- | --- | --- |
| <Host> | Deployment node | - | <Containers> | 1 |
| <Docker Engine> | Deployment node | <Host> | <Containers> | 1 |
| <DNS> | Infrastructure node | - | - | - |
| <Load balancer> | Infrastructure node | - | - | - |

Operational depth for this target lives in [`../../../devops/infra/`](../../../devops/infra/INDEX.md). Do not duplicate it. Link to it.

## N.6 Failure modes

Dynamic pages only. Delete on a structural or deployment page. This section is mandatory on a dynamic page.

| Failure | Observable symptom | Recovery |
| --- | --- | --- |
| <Broker unreachable> | <Task never runs, no error in the UI> | [<SOP name>](../../../sops/<slug>-sop.md) |
| <Migration not applied> | <500 on first request to the endpoint> | <Steps or SOP link> |

## N.7 Configuration

Dynamic pages only. Delete on a structural or deployment page.

| Variable | Default | Effect |
| --- | --- | --- |
| `<ENV_VAR>` | `<default>` or `no default` | What changes when you set it |

Canonical list: [`.env.example`](../../../../.env.example) and [`apps/api/.env.example`](../../../../apps/api/.env.example).

## N.8 Notes

- **Primary path**: The route through the diagram when every step succeeds.
- **Branch**: The main decision point and both outcomes.
- **Design choice**: Something a reader cannot guess from the code.

## N.9 Verification

- **Tests**: `apps/api/tests/...`
- **Command**: The exact command that exercises this flow or starts these containers.
- **Expected result**: The observable proof.

## N.10 Related

| Page | Why it matters here |
| --- | --- |
| [<L1 page>](../context/NN-slug.md) | The external boundary around these containers |
| [<L3 page>](../components/NN-slug.md) | File-level detail inside one container |
| [<Infra page>](../../../devops/infra/NN-slug.md) | How these containers deploy |
| [<Security page>](../../../security/NN-slug.md) | The restriction enforced here |
