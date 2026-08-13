# L2 Containers Conventions

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

## Building the container list

`docker-compose.yml` is not the container list. It holds 13 services, and the C4 term is broader. [`../AGENTS.md`](../AGENTS.md) defines it.

- Where a container maps to a Compose service, use that service name exactly. Write `plane-db`, not `postgres`.
- Where a container has no Compose service, list it anyway. The desktop app and the mobile apps are C4 containers, and they live outside this repository. Cite [`../../../clients/INDEX.md`](../../../clients/INDEX.md).
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

## Failure modes carry the value on a dynamic page

[`TEMPLATE.md`](./TEMPLATE.md) marks which sections apply to each kind. One section needs more than a heading.

A dynamic page earns its keep through its failure modes table. For each failure, state three things.

1. What breaks.
2. What a user or an operator observes.
3. What recovers it, or which SOP recovers it.

## Trust boundaries

A structural page and a deployment page both list each zone and its exposure. Use this shape.

| Zone | Contains | Exposure |
| --- | --- | --- |
| Internet | Browser, mobile app, webhook consumer | Public |
| Edge | `proxy` | Public ingress |
| Application | `web`, `admin`, `space`, `api`, `live`, `worker` | Internal |
| Data | `plane-db`, `plane-redis`, `plane-mq`, `plane-minio` | Internal only |

## Configuration on a dynamic page

Name each environment variable in backticks, exactly as the code reads it. Give the default value, or write `no default`.
