# Clients and Interfaces

Every way to consume Plane: the apps a person opens, the admin surfaces, the programmatic interfaces, and the third-party integrations.

Read [`AGENTS.md`](./AGENTS.md) before you add a page. Follow [`TEMPLATE.md`](./TEMPLATE.md).

## Pages

- [1. Plane clients and interfaces](./01-clients-and-interfaces.md) - Deployment models, end-user apps, admin surfaces, programmatic APIs, and the MCP server.

## Surface groups

| Group | Covered in |
| --- | --- |
| Deployment models | [01](./01-clients-and-interfaces.md) |
| End-user apps: web, desktop, mobile, publish | [01](./01-clients-and-interfaces.md) |
| Admin surfaces: God Mode, workspace settings, Prime portal | [01](./01-clients-and-interfaces.md) |
| Programmatic interfaces: REST, webhooks, OAuth | [01](./01-clients-and-interfaces.md) |
| MCP server | [01](./01-clients-and-interfaces.md) |

## Suggested next pages

Split a group out of page 01 when it grows past a short section. This list is a backlog.

| Page | Covers |
| --- | --- |
| REST API surface | Endpoint groups, pagination, rate limits, error shapes |
| Webhooks | Event catalog, payload shape, signing, retry behavior |
| OAuth applications | Scopes, flows, and token lifetime |
| MCP server | Transports, tool catalog, and self-hosting |
| Third-party integrations | Slack, GitHub, importers, and editor plugins |

## Availability values

Never state a capability without its availability. [`AGENTS.md`](./AGENTS.md) defines the four values.

## Related

- [../architecture/c4/containers/INDEX.md](../architecture/c4/containers/INDEX.md) shows the container that serves each surface.
- [../security/INDEX.md](../security/INDEX.md) lists the restriction that guards each surface.
- [../devops/infra/INDEX.md](../devops/infra/INDEX.md) covers the deployment target that hosts each surface.
