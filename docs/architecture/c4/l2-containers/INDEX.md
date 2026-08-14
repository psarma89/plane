# L2 Containers

Inside the Plane box: the deployable units, the traffic between them, and the runtime flows that cross them.

Read [`../AGENTS.md`](../AGENTS.md) for the shared rules, then [`AGENTS.md`](./AGENTS.md) for the L2 rules. Follow [`TEMPLATE.md`](./TEMPLATE.md).

## Pages

Entry format: `- [N. Title](./NN-slug.md) - Structural | Dynamic | Deployment - one-line summary`

- [1. Container overview](./01-container-overview.md) - Structural - All 13 Compose services, the four client-side containers, and the traffic between them.
- [2. Request lifecycle](./02-request-lifecycle.md) - Dynamic - One HTTP request from the browser to `plane-db`, through 13 middleware.

## Three page kinds

[`AGENTS.md`](./AGENTS.md) defines the structural, dynamic, and deployment kinds, and which sections each one needs.

## Backlog

This list is a backlog, not a claim that the pages exist. Delete a row when you write the page.

| Page | Kind | Containers involved |
| --- | --- | --- |
| Deployment: single-node Compose | Deployment | Every service in `docker-compose.yml` |
| Deployment: all-in-one image | Deployment | Every process in `deployments/aio/community/supervisor.conf` |
| Authentication, sessions, and API keys | Dynamic | `api`, every frontend |
| Workspace and project authorization | Dynamic | `api`, `web` |
| Background work with Celery and RabbitMQ | Dynamic | `api`, `worker`, `beat-worker`, `plane-mq` |
| File upload and object storage | Dynamic | `api`, `plane-minio`, browser |
| Caching and rate limiting | Dynamic | `api`, `plane-redis` |
| Webhooks and outbound delivery | Dynamic | `api`, `worker` |
| Notifications and email | Dynamic | `api`, `worker` |
| Migrations at runtime | Dynamic | `migrator`, `api`, `plane-db` |
| Licensing and edition gating | Dynamic | `api`, `admin` |

Document sync is not on this list. [`../l4-code/01-document-synchronisation.md`](../l4-code/01-document-synchronisation.md) already traces that flow end to end, including every container hop, so an L2 page would repeat it.

## Containers with no Compose service

A C4 container is not a Docker container. These Plane containers must appear on an L1 or L2 page even though `docker-compose.yml` does not list them. Source: [../l1-context/01-system-context.md](../l1-context/01-system-context.md), Appendix A.

| Container | Kind | Lives in this repo |
| --- | --- | --- |
| Web SPA | Client-side web application | Yes, built from `apps/web`, runs in the browser |
| Admin SPA | Client-side web application | Yes, built from `apps/admin`, runs in the browser |
| Desktop app | Desktop application | No |
| Mobile app (iOS, Android) | Mobile app | No |

The first two rows matter most, because they are easy to miss. `apps/web` and `apps/admin` both set `ssr: false`, so the `web` and `admin` services run nginx and serve static files. The application itself executes on the client device, which makes it a separate container.

Read the vocabulary section in [../AGENTS.md](../AGENTS.md) before you build a container list.

## No Kubernetes deployment page is possible

`deployments/kubernetes/community/` holds a `README.md` and nothing else. It points at an out-of-repo Helm chart. `deployments/swarm/community/swarm.sh` downloads a Compose file at run time. Neither one supports a deployment page written from source, so neither is in the backlog above.

## Services in the Compose stack

[`../../../devops/infra/INDEX.md`](../../../devops/infra/INDEX.md) holds the canonical Compose inventory, with the image and the pin for each service. Read it there, and never copy a row here, because two copies drift.

That inventory is not the full container list. Add the surfaces in the section above.

## Related

- [../l1-context/INDEX.md](../l1-context/INDEX.md) treats Plane as one box.
- [../l3-components/INDEX.md](../l3-components/INDEX.md) opens one container.
- [../../../devops/infra/INDEX.md](../../../devops/infra/INDEX.md) covers each deployment target in depth.
- [../../../sops/INDEX.md](../../../sops/INDEX.md) holds the recovery steps for each failure mode.
