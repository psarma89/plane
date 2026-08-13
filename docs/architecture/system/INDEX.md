# System Architecture

One page per runtime concern that crosses two or more units in `apps/`. Each page traces the concern end to end and lists its failure modes.

Read [`AGENTS.md`](./AGENTS.md) before you add a page. Follow [`TEMPLATE.md`](./TEMPLATE.md).

## Pages

> No page exists yet. Add the first page with [`TEMPLATE.md`](./TEMPLATE.md), then list it here.

Entry format: `- [N. Title](./NN-slug.md) - one-line summary`

<!-- - [1. Request lifecycle](./01-request-lifecycle.md) - How a browser request reaches PostgreSQL and returns. -->

## Suggested first pages

This list is a backlog, not a claim that the pages exist. Delete a row when you write the page.

| Concern | Units involved |
| --- | --- |
| Request lifecycle and routing | `apps/proxy`, `apps/web`, `apps/api` |
| Authentication, sessions, and API keys | `apps/api`, all Next.js apps |
| Workspace, project, and role authorization | `apps/api`, `apps/web` |
| Background work with Celery and RabbitMQ | `apps/api`, `worker`, `beat-worker`, `plane-mq` |
| Real-time collaboration and document sync | `apps/live`, `apps/web` |
| File upload and object storage | `apps/api`, `plane-minio`, browser |
| Caching and rate limiting | `apps/api`, `plane-redis` |
| Webhooks and outbound delivery | `apps/api`, `worker` |
| Notifications and email | `apps/api`, `worker` |
| Database schema and migrations at runtime | `apps/api`, `migrator`, `plane-db` |
| Licensing and edition gating | `apps/api`, `apps/admin` |
| Internationalization at runtime | `packages/i18n`, all Next.js apps |

## Related

- [../c4/INDEX.md](../c4/INDEX.md) draws the container boundaries these flows cross.
- [../application/INDEX.md](../application/INDEX.md) names the files inside one app.
- [../../sops/INDEX.md](../../sops/INDEX.md) holds the recovery steps for each failure mode.
- [../../devops/monitoring/INDEX.md](../../devops/monitoring/INDEX.md) holds the signals that detect a failure.
