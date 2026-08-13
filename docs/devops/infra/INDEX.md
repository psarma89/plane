# Infrastructure

One page per deployment target. Each page states what the target contains, what it needs, and how to prove it started.

Read [`AGENTS.md`](./AGENTS.md) before you add a page. Follow [`TEMPLATE.md`](./TEMPLATE.md).

## Pages

> No page exists yet. Add the first page with [`TEMPLATE.md`](./TEMPLATE.md), then list it here.

Entry format: `- [N. Title](./NN-slug.md) - one-line summary`

## Targets to document

Every row maps to a real path. This list is a backlog, not a claim that a page exists. Delete a row when you write the page.

| Target | Source | Serves |
| --- | --- | --- |
| Local development stack | `docker-compose-local.yml` | Contributor machine |
| Local test stack | `docker-compose-test.yml` | Django and pytest suite |
| Single-node Compose | `docker-compose.yml` | Small self-hosted install |
| All-in-one image | `deployments/aio/` | One-container self-hosted install |
| Docker Swarm | `deployments/swarm/` | Multi-node self-hosted install |
| Kubernetes with Helm | `deployments/kubernetes/` | Cluster self-hosted install |
| Prime CLI | `deployments/cli/` | Managed self-hosted install |
| Reverse proxy | `apps/proxy` | Ingress for every target |

## Services in the root Compose stack

Copied from `docker-compose.yml`. Update this table when a pin changes.

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
| `plane-db` | `postgres:15.7-alpine` | Primary data store |
| `plane-redis` | `valkey/valkey:7.2.11-alpine` | Cache and rate limits |
| `plane-mq` | `rabbitmq:3.13.6-management-alpine` | Celery broker |
| `plane-minio` | `minio/minio` | Object storage |

## Related

- [../../architecture/c4/containers/INDEX.md](../../architecture/c4/containers/INDEX.md) draws these containers and their traffic.
- [../cicd/INDEX.md](../cicd/INDEX.md) covers the pipelines that build the images.
- [../../sops/INDEX.md](../../sops/INDEX.md) holds install, upgrade, and backup procedures.
- [../../../CONTRIBUTING.md](../../../CONTRIBUTING.md) covers local setup with `setup.sh`.
