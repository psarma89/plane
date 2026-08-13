# L2 Containers Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. It holds the naming, diagram, label, and table rules for every level. This file adds only what is specific to L2.

An L2 page opens the Plane box. It names the **deployable units, the traffic between them, and the runtime flows that cross them**.

## Three page kinds

This level holds the L2 static view plus two supplementary C4 views that operate on containers. State the kind in the header block.

| Kind | Answers | Diagram | C4 type |
| --- | --- | --- | --- |
| **Structural** | What runs where, and what talks to what? | `C4Container` | Container diagram (L2) |
| **Dynamic** | How does one concern travel across containers, in order? | `sequenceDiagram` | Dynamic diagram |
| **Deployment** | Where do container instances run, in one environment? | `C4Deployment` | Deployment diagram |

A dynamic page is the right home for a concern that used to need a separate system-level folder. Examples: the request lifecycle, Celery task dispatch, document sync, file upload.

A dynamic diagram can also sit at L3, when it shows components inside one container interacting. File that page in [`../components/`](../components/INDEX.md). File the page by the elements the diagram names.

## What belongs here

| Subject | Belongs here |
| --- | --- |
| The set of containers and their traffic | Yes, structural |
| How a request travels from `proxy` to `plane-db` | Yes, dynamic |
| How a Celery task reaches `worker` and reports failure | Yes, dynamic |
| How Yjs sync flows between `apps/live` and `apps/web` | Yes, dynamic |
| Where containers run on a Kubernetes target | Yes, deployment |
| A runtime flow between two modules inside `apps/web` | No. Dynamic at L3. Use [`../components/`](../components/INDEX.md). |
| Which MobX store owns cycle state | No. Use [`../components/`](../components/INDEX.md). |
| Every external service Plane calls | No. Use [`../context/`](../context/INDEX.md). |

If a page names a file inside one container, it is L3. Move it.

## A C4 container is not a Docker container

Read the vocabulary section in [`../AGENTS.md`](../AGENTS.md) before you list containers. The C4 term is broader than a Compose service.

A container is any application or data store that must run for Plane to work. Apply these rules.

- Where a container maps to a service in `docker-compose.yml`, use that service name exactly. Write `plane-db`, not `postgres`.
- Where a container has no Compose service, list it anyway. The desktop app and the mobile apps are C4 containers. Cite [`../../../clients/INDEX.md`](../../../clients/INDEX.md) as the source.
- A data store is a container. `plane-db` and the `plane-minio` bucket both count.
- `migrator` runs once and exits. Label it a one-shot container.
- Never label a component as a container. If it shares a process with other code, it is L3.

State the source of the container list on every structural page. A page built only from `docker-compose.yml` is incomplete, and must say which surfaces it leaves out.

## Deployment pages

A deployment page maps container instances onto infrastructure. It uses element types the other kinds do not.

| Element | Means |
| --- | --- |
| Deployment node | Where a container runs: a host, a VM, a Kubernetes node, a runtime. Nodes nest. |
| Infrastructure node | A supporting element: DNS, a load balancer, a firewall. |
| Container instance | One deployed instance of a container from the structural page. |

Scope one deployment page to **one deployment environment**. Do not mix production and local development in a single diagram.

Plane ships several targets. Write one page per target, or one page with one section per target.

[`../../../devops/infra/`](../../../devops/infra/INDEX.md) covers each target in operational depth: pins, volumes, resource floors, and verification. A deployment page here stays at the diagram and the mapping. Do not duplicate the infra page. Link to it.

## Required sections

Follow [`TEMPLATE.md`](./TEMPLATE.md). The template marks which sections apply to each kind.

| Section | Structural | Dynamic | Deployment |
| --- | --- | --- | --- |
| Header block with `Kind` | Required | Required | Required |
| Related feature specs | Required | Required | Required |
| Diagram | Required | Required | Required |
| Elements | Required | Required as Participants | Required as nodes and instances |
| Relationships with protocol and port | Required | Not required | Required |
| Trust boundaries | Required | Not required | Required |
| Failure modes | Not required | Required | Not required |
| Configuration | Not required | Required | Not required |
| Deployment environment | Not required | Not required | Required |
| Verification | Required | Required | Required |

## Failure modes are mandatory on a dynamic page

A dynamic page without a failure modes table is incomplete. For each failure, state three things.

1. What breaks.
2. What a user or an operator observes.
3. What recovers it, or which SOP recovers it.

## Trust boundaries are mandatory on a structural and a deployment page

List each zone and its exposure. Use this shape.

| Zone | Contains | Exposure |
| --- | --- | --- |
| Internet | Browser, mobile app, webhook consumer | Public |
| Edge | `proxy` | Public ingress |
| Application | `web`, `admin`, `space`, `api`, `live`, `worker` | Internal |
| Data | `plane-db`, `plane-redis`, `plane-mq`, `plane-minio` | Internal only |

## Pins come from the source

Copy every image pin character for character. Cite the source file next to the table. Never copy a pin from another doc.

## Configuration on a dynamic page

- Name each environment variable in backticks, exactly as the code reads it.
- Give the default value. If there is no default, write `no default`.
- Never paste a secret value. Write `<redacted>`.
- Point to `.env.example` and `apps/api/.env.example` as the canonical list.

## Cross-links

- Link down to a [`../components/`](../components/INDEX.md) page for file-level detail.
- Link up to [`../context/`](../context/INDEX.md) for the external boundary.
- Link out to [`../../../sops/`](../../../sops/INDEX.md) for every recovery step.
- Link out to [`../../../devops/monitoring/`](../../../devops/monitoring/INDEX.md) for the signal that detects a failure.
- Link out to [`../../../devops/infra/`](../../../devops/infra/INDEX.md) for the deployment target in depth.
