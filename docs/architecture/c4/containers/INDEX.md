# L2 Containers

Inside the Plane box: the deployable units, the traffic between them, and the runtime flows that cross them.

Read [`../AGENTS.md`](../AGENTS.md) for the shared rules, then [`AGENTS.md`](./AGENTS.md) for the L2 rules. Follow [`TEMPLATE.md`](./TEMPLATE.md).

## Pages

> No page exists yet. Add the first page with [`TEMPLATE.md`](./TEMPLATE.md), then list it here.

Entry format: `- [N. Title](./NN-slug.md) - Structural | Dynamic | Deployment - one-line summary`

<!-- - [1. Container overview](./01-container-overview.md) - Structural - Every container and the traffic between them. -->

## Three page kinds

| Kind | Answers | Diagram | C4 type |
| --- | --- | --- | --- |
| **Structural** | What runs where, and what talks to what? | `C4Container` | Container diagram (L2) |
| **Dynamic** | How does one concern travel across containers, in order? | `sequenceDiagram` | Dynamic diagram |
| **Deployment** | Where do container instances run, in one environment? | `C4Deployment` | Deployment diagram |

A dynamic page covers a concern that crosses containers end to end. That is the same job a separate system-architecture folder once did. The container granularity makes it L2.

A dynamic diagram can also sit at L3, when it shows components inside one container. File that page in [../components/](../components/INDEX.md).

A deployment page is scoped to one deployment environment. Do not mix production and local development in one diagram.

## Suggested first pages

This list is a backlog, not a claim that the pages exist. Delete a row when you write the page.

| Page | Kind | Containers involved |
| --- | --- | --- |
| Container overview | Structural | Every container |
| Deployment: single-node Compose | Deployment | Every service in `docker-compose.yml` |
| Deployment: Kubernetes | Deployment | Every service, per `deployments/kubernetes/` |
| Request lifecycle and routing | Dynamic | `proxy`, `web`, `api` |
| Authentication, sessions, and API keys | Dynamic | `api`, every frontend |
| Workspace and project authorization | Dynamic | `api`, `web` |
| Background work with Celery and RabbitMQ | Dynamic | `api`, `worker`, `beat-worker`, `plane-mq` |
| Real-time collaboration and document sync | Dynamic | `live`, `web`, `plane-redis` |
| File upload and object storage | Dynamic | `api`, `plane-minio`, browser |
| Caching and rate limiting | Dynamic | `api`, `plane-redis` |
| Webhooks and outbound delivery | Dynamic | `api`, `worker` |
| Notifications and email | Dynamic | `api`, `worker` |
| Migrations at runtime | Dynamic | `migrator`, `api`, `plane-db` |
| Licensing and edition gating | Dynamic | `api`, `admin` |

## Containers with no Compose service

A C4 container is not a Docker container. These Plane containers must appear on an L1 or L2 page even though `docker-compose.yml` does not list them. Source: [../../../clients/INDEX.md](../../../clients/INDEX.md).

| Container | Kind | Availability |
| --- | --- | --- |
| Desktop app | Desktop application | Cloud and commercial self-hosted |
| Mobile app (iOS, Android) | Mobile app | Cloud and commercial self-hosted |

Read the vocabulary section in [../AGENTS.md](../AGENTS.md) before you build a container list.

## Services in the Compose stack

Read from `docker-compose.yml`. This table is not the full container list. See the section above.

Pins live in [`../../../devops/infra/INDEX.md`](../../../devops/infra/INDEX.md). Do not copy a pin here, because two copies drift.

| Service | Image or build | Role |
| --- | --- | --- |
| `proxy` | Built from `apps/proxy` | Caddy ingress and TLS |
| `web` | Built from `apps/web` | Workspace app |
| `admin` | Built from `apps/admin` | Instance admin |
| `space` | Built from `apps/space` | Published pages |
| `api` | Built from `apps/api` | Django REST API |
| `worker` | Built from `apps/api` | Celery worker |
| `beat-worker` | Built from `apps/api` | Celery beat scheduler |
| `migrator` | Built from `apps/api` | One-shot migration runner |
| `live` | Built from `apps/live` | Hocuspocus collaboration server |
| `plane-db` | `postgres` | Primary data store |
| `plane-redis` | `valkey/valkey` | Cache and rate limits. Valkey, not Redis, despite the name. |
| `plane-mq` | `rabbitmq` | Celery broker |
| `plane-minio` | `minio/minio` | Object storage |

## Related

- [../context/INDEX.md](../context/INDEX.md) treats Plane as one box.
- [../components/INDEX.md](../components/INDEX.md) opens one container.
- [../../../devops/infra/INDEX.md](../../../devops/infra/INDEX.md) covers each deployment target in depth.
- [../../../sops/INDEX.md](../../../sops/INDEX.md) holds the recovery steps for each failure mode.
