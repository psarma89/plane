# L2 Containers

Inside the Plane box: the deployable units, the traffic between them, and the runtime flows that cross them.

Read [`../AGENTS.md`](../AGENTS.md) for the shared rules, then [`AGENTS.md`](./AGENTS.md) for the L2 rules. Follow [`TEMPLATE.md`](./TEMPLATE.md).

## Pages

> No page exists yet. Add the first page with [`TEMPLATE.md`](./TEMPLATE.md), then list it here.

Entry format: `- [N. Title](./NN-slug.md) - Structural | Dynamic | Deployment - one-line summary`

<!-- - [1. Container overview](./01-container-overview.md) - Structural - Every container and the traffic between them. -->

## Three page kinds

[`AGENTS.md`](./AGENTS.md) defines the structural, dynamic, and deployment kinds, and which sections each one needs.

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

[`../../../devops/infra/INDEX.md`](../../../devops/infra/INDEX.md) holds the canonical Compose inventory, with the image and the pin for each service. Read it there, and never copy a row here, because two copies drift.

That inventory is not the full container list. Add the surfaces in the section above.

## Related

- [../context/INDEX.md](../context/INDEX.md) treats Plane as one box.
- [../components/INDEX.md](../components/INDEX.md) opens one container.
- [../../../devops/infra/INDEX.md](../../../devops/infra/INDEX.md) covers each deployment target in depth.
- [../../../sops/INDEX.md](../../../sops/INDEX.md) holds the recovery steps for each failure mode.
