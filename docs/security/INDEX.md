# Plane Security Controls

> **Last reviewed:** 2026-08-12
> **Audience:** Security stakeholders and engineers.
> **Scope:** Restrictions the code enforces today. Not policy. Not developer discipline.

This catalog answers one question: **what does Plane restrict, and where is each restriction enforced?** Every row points at a file and a symbol, so a reader can verify a control without asking an author.

## Summary

> No page exists yet. Add the first page with [`TEMPLATE.md`](./TEMPLATE.md), then fill the `Controls` count below.

| Area | Controls | Page |
| --- | --- | --- |
| Authentication and authorization | - | `01-authentication-and-authorization.md` |
| Data access and tenancy | - | `02-data-access-and-tenancy.md` |
| Abuse and rate limiting | - | `03-abuse-and-rate-limiting.md` |
| Network and transport | - | `04-network-and-transport.md` |
| Secrets and configuration | - | `05-secrets-and-configuration.md` |
| Audit and logging | - | `06-audit-and-logging.md` |
| Licensing and edition gating | - | `07-licensing-and-edition-gating.md` |

## Enforcement points to catalog

Every entry names a real path. This list is a backlog, not a claim that a page exists.

| Enforcement point | Path | Area |
| --- | --- | --- |
| DRF permission classes | `apps/api/plane/app/permissions/` | 01 |
| Authentication backends and providers | `apps/api/plane/authentication/` | 01 |
| API key authentication | `apps/api/plane/api/middleware/api_authentication.py` | 01 |
| Public and published surfaces | `apps/api/plane/space/` | 02 |
| Database routing | `apps/api/plane/middleware/db_routing.py` | 02 |
| Throttles | `apps/api/plane/throttles/` | 03 |
| Request body size limit | `apps/api/plane/middleware/request_body_size.py` | 03 |
| Ingress routes and TLS | `apps/proxy/Caddyfile.ce` | 04 |
| Collaboration WebSocket authorization | `apps/live/src/` | 04 |
| Settings and defaults | `apps/api/plane/settings/` | 05 |
| Request logging | `apps/api/plane/middleware/logger.py` | 06 |
| License checks | `apps/api/plane/license/` | 07 |

## How to read a row

| Column | Meaning |
| --- | --- |
| `#` | Stable identifier, `N.2.X`. Other docs cite it. Do not renumber. |
| `Restriction` | One sentence. What the code refuses to do. |
| `Where enforced` | The file path and the symbol. No line numbers. |
| `Reference` | The canonical architecture page or SOP, or `-`. |

## Related

- [../architecture/INDEX.md](../architecture/INDEX.md) holds the design rationale behind each control.
- [../devops/infra/INDEX.md](../devops/infra/INDEX.md) covers infrastructure exposure per deployment target.
- [../sops/INDEX.md](../sops/INDEX.md) holds rotation, revocation, and recovery procedures.
- [../../SECURITY.md](../../SECURITY.md) is the vulnerability reporting policy. Report a vulnerability there, not here.
