# L2 Containers Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. It holds the naming, diagram, label, and table rules for every level. This file adds only what is specific to L2.

An L2 page opens the Plane box. It names the **deployable units, the traffic between them, and the runtime flows that cross them**.

## Two page kinds

This level holds both a static view and a dynamic view. Both are L2, because both stay at container granularity.

| Kind | Answers | Diagram |
| --- | --- | --- |
| **Structural** | What runs where, and what talks to what? | `C4Container` |
| **Dynamic** | How does one concern travel across containers, in order? | `sequenceDiagram` |

A dynamic page is the right home for a concern that used to need a separate system-level folder. Examples: the request lifecycle, Celery task dispatch, document sync, file upload.

State the kind in the header block. Use `Structural` or `Dynamic`.

## What belongs here

| Subject | Belongs here |
| --- | --- |
| The set of deployable containers and their traffic | Yes, structural |
| How a request travels from `proxy` to `plane-db` | Yes, dynamic |
| How a Celery task reaches `worker` and reports failure | Yes, dynamic |
| How Yjs sync flows between `apps/live` and `apps/web` | Yes, dynamic |
| How containers map onto a deployment target | Yes, structural |
| Which MobX store owns cycle state | No. Use [`../components/`](../components/INDEX.md). |
| Every external service Plane calls | No. Use [`../context/`](../context/INDEX.md). |

If a page names a file inside one container, it is L3. Move it.

## Required sections

Follow [`TEMPLATE.md`](./TEMPLATE.md). The template marks which sections apply to each kind.

| Section | Structural | Dynamic |
| --- | --- | --- |
| Header block with `Kind` | Required | Required |
| Related feature specs | Required | Required |
| Diagram | Required | Required |
| Elements | Required | Required as Participants |
| Relationships with protocol and port | Required | Not required |
| Trust boundaries | Required | Not required |
| Failure modes | Not required | Required |
| Configuration | Not required | Required |
| Verification | Required | Required |

## Failure modes are mandatory on a dynamic page

A dynamic page without a failure modes table is incomplete. For each failure, state three things.

1. What breaks.
2. What a user or an operator observes.
3. What recovers it, or which SOP recovers it.

## Trust boundaries are mandatory on a structural page

List each zone and its exposure. Use this shape.

| Zone | Contains | Exposure |
| --- | --- | --- |
| Internet | Browser, mobile app, webhook consumer | Public |
| Edge | `proxy` | Public ingress |
| Application | `web`, `admin`, `space`, `api`, `live`, `worker` | Internal |
| Data | `plane-db`, `plane-redis`, `plane-mq`, `plane-minio` | Internal only |

## Container names come from the source

Use the Compose service name exactly as `docker-compose.yml` writes it. Write `plane-db`, not `postgres`.

Copy every image pin character for character. Cite the source file next to the table.

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
