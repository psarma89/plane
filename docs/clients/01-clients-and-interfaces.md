# 1. Plane clients and interfaces

> **Last reviewed:** 2026-08-12
> **Canonical references:** <https://docs.plane.so>, <https://developers.plane.so>

This document lists every way to consume Plane. It answers one question: what are all the interfaces?

Plane has two deployment models and four groups of interfaces.

```
                    ┌─────────────────────────────┐
                    │   Plane Cloud  |  Self-host  │
                    └──────────────┬──────────────┘
                                   │
       ┌───────────────┬───────────┴───────┬──────────────────┐
       │               │                   │                  │
  End-user apps   Admin surfaces    Programmatic APIs   Third-party surfaces
   web, desktop,   God Mode,         REST, webhooks,     Slack, GitHub,
   mobile, publish Prime portal      OAuth, MCP          IDEs, importers
```

## 1. Deployment models

| Model | Host | Entry point |
| --- | --- | --- |
| Plane Cloud | Plane | `https://app.plane.so` |
| Self-hosted | You | Your own domain |

Self-host methods: Docker Compose, Docker AIO, Docker Swarm, Kubernetes with Helm, Podman Quadlets, Coolify, and Portainer. The Airgapped Edition covers offline networks. Prime CLI manages a self-hosted instance.

Editions: Community Edition, Commercial Edition (Pro and Business), and Enterprise Grid.

## 2. End-user apps

| Client | Platform | Availability |
| --- | --- | --- |
| Web app | Any browser | Cloud and self-hosted |
| Desktop app | macOS Universal v2.0.0, Linux AppImage v2.0.0, Windows x64 v1.6.1 | Cloud and commercial self-hosted |
| Mobile app | iOS (App Store), Android (Google Play) | Cloud and commercial self-hosted |
| Plane Publish | Public web pages at `https://sites.plane.so` | Cloud and self-hosted |

The desktop app does not need a separate account. It uses your existing Plane credentials against Cloud or a self-hosted instance. Push notifications on mobile work on Cloud only. The Community Edition does not support the mobile app.

Plane Publish makes a board, a page, or an intake form public with one click.

Download page: <https://plane.so/download>

## 3. Admin surfaces

| Surface | Scope |
| --- | --- |
| God Mode | Instance-level administration for a self-hosted deployment |
| Workspace settings | Members, projects, tokens, and webhooks inside the web app |
| Prime portal | License and instance management for commercial editions |

## 4. Programmatic interfaces

| Interface | Endpoint | Authentication |
| --- | --- | --- |
| REST API v1 | `https://api.plane.so` (Cloud), `/api/v1/` (self-hosted) | `X-API-Key` personal access token, or OAuth bearer token |
| Public API | `/api/public/` | Anonymous, for published boards and intake forms |
| Instance API | `/api/instances/` | Instance admin |
| Webhooks | Your own URL | Shared secret |
| OAuth apps | `/auth/` | OAuth 2.0 |
| OpenAPI schema | `/api/schema/`, `/api/schema/swagger-ui/`, `/api/schema/redoc/` | Same as REST API |

The REST API has more than 180 endpoints. The rate limit is 60 requests per minute for each API key. Pagination is cursor-based.

Developer docs: <https://developers.plane.so>

## 5. MCP server

The MCP server connects AI agents to Plane. It offers more than 30 tools for projects, work items, cycles, and modules.

| Transport | Endpoint or command | Use |
| --- | --- | --- |
| HTTP with OAuth | `https://mcp.plane.so/http/mcp` | Simplest setup for Cloud |
| HTTP with PAT | Same URL with `x-api-key` and `x-workspace-slug` headers | Automation and CI/CD |
| Local stdio | `uvx plane-mcp-server stdio` | Local development and self-hosted |
| SSE (legacy) | `https://mcp.plane.so/sse` | Existing integrations |

You can deploy `plane-mcp-server` yourself with Docker Compose or Helm.

Example for Claude Code:

```bash
claude mcp add --transport http plane https://mcp.plane.so/http/mcp
```

## 6. Third-party surfaces

| Group | Products |
| --- | --- |
| Code hosting | GitHub, GitHub Enterprise Server, GitLab, GitLab Enterprise, Bitbucket |
| Communication | Slack |
| Monitoring | Sentry |
| Diagrams | Draw.io |
| AI and IDE clients | Claude, Cursor, VS Code MCP, Raycast |
| Importers | Jira, Jira Server, Linear, Asana, ClickUp, Notion, Confluence, CSV, Flatfile |

Marketplace: <https://plane.so/marketplace>

## 7. Services in this repository

| Service | Source | Route behind the proxy | Local dev port | Serves |
| --- | --- | --- | --- | --- |
| Web app | `apps/web` | `/*` | 3000 | The main product UI |
| Admin app | `apps/admin` | `/god-mode/*` | 3001 | God Mode |
| Space app | `apps/space` | `/spaces/*` | 3002 | Plane Publish |
| API server | `apps/api` | `/api/*`, `/auth/*` | 8000 | REST API, public API, auth, webhooks |
| Live server | `apps/live` | `/live/*` | 3000 | Real-time collaboration for the editor |
| Proxy | `apps/proxy` | `:80`, `:443` | n/a | Caddy reverse proxy in front of the other services |

Each container listens on its own port 3000. The proxy maps the routes above. The local dev ports differ because the apps run side by side on one host.

The desktop app, the mobile apps, and the MCP server live outside this repository.

## Sources

- <https://plane.so/download>
- <https://docs.plane.so/introduction/home>
- <https://developers.plane.so>
- <https://plane.so/marketplace>
- <https://github.com/makeplane/plane>
