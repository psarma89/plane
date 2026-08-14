# Monitoring

One page per signal area. Each page maps a signal to an alert, and the alert to a recovery procedure.

## Pages

> No page exists yet. Add the first page with [`TEMPLATE.md`](./TEMPLATE.md), then list it here.

Entry format: `- [N. Title](./NN-slug.md) - one-line summary`

## Suggested first pages

This list is a backlog, not a claim that the pages exist. Delete a row when you write the page.

| Signal area | Primary source |
| --- | --- |
| HTTP errors and latency | `apps/proxy`, `apps/api` |
| Background queue health | `worker`, `beat-worker`, `plane-mq` |
| Database health and connections | `plane-db` |
| Cache and rate limits | `plane-redis` |
| Object storage availability | `plane-minio` |
| Real-time session health | `apps/live` |
| Client-side errors and web vitals | `apps/web`, `apps/admin`, `apps/space` |
| Product analytics events | Posthog, when configured |
| Container and process health | Every deployment target |

## Availability

State the deployment for every signal. Tooling differs between installs. [`AGENTS.md`](./AGENTS.md) defines the three values.

## Related

- [../../architecture/c4/l2-containers/INDEX.md](../../architecture/c4/l2-containers/INDEX.md) lists the failure modes these signals detect.
- [../../sops/INDEX.md](../../sops/INDEX.md) holds the recovery steps for every alert.
- [../infra/INDEX.md](../infra/INDEX.md) covers the deployment target that emits each signal.
