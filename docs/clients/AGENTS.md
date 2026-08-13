# Client Docs Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. This file adds the rules that apply to `docs/clients/`.

A client page answers one question: **what are all the ways to consume Plane, and how does a user or a script reach each one?** It describes the surface, not the internals. Internals live in [`../architecture/`](../architecture/INDEX.md).

## Naming

- Files use `NN-<slug>.md`, zero-padded from `01`.
- A new page takes the next free number. Do not renumber an existing page.
- Sections use `## N.1` and `## N.2`, and match the page number.

## Surface against implementation

| Content | Folder |
| --- | --- |
| "The REST API accepts an `X-API-Key` header and rate limits at 60 requests per minute." | `clients/` |
| "`APIKeyAuthentication` resolves the key and attaches the user." | [`../architecture/`](../architecture/INDEX.md) |
| "The API key check rejects a revoked token." | [`../security/`](../security/INDEX.md) |

If a sentence names a Python class or a React component, it belongs in `architecture/`. Move it.

## Required sections

Follow [`TEMPLATE.md`](./TEMPLATE.md). Every page needs these sections.

| Section | Content |
| --- | --- |
| Header block | `Last reviewed` stamp and the canonical external doc link |
| Overview | Two sentences on what this surface is for |
| Surfaces | Table of each client, its platform, and its availability |
| Access | The entry point, the authentication, and the limits |
| Availability | Which deployment model and which edition offers it |
| Known constraints | What the surface cannot do |

## Availability is mandatory

Plane ships as a hosted service and as a self-hosted deployment. Editions differ. Never state a capability without its availability.

| Column value | Meaning |
| --- | --- |
| `Cloud` | The hosted service only |
| `Self-hosted` | A self-hosted deployment only |
| `Both` | Both deployment models |
| `Commercial` | Commercial editions only. Name the tier. |

A row without an availability value is incomplete.

## Versions and endpoints

- Copy an endpoint path character for character. Example: `/api/v1/`.
- Give a version only where the source states one. Never round a version.
- State a rate limit as a number and a window. Example: "60 requests per minute for each API key."
- Where a number comes from external documentation, link that documentation.

## External links

- Prefer the canonical Plane documentation site for a user-facing detail.
- Prefer the developer documentation site for an API detail.
- Use an angle-bracket link for a bare URL. Example: `<https://developers.plane.so>`.
- If an external number contradicts the code, trust the code and note the conflict.

## Never write a secret

Never write a real API key, a token, or a workspace slug from a live install. Use a placeholder.

## Cross-links

- Link to [`../architecture/c4/containers/`](../architecture/c4/containers/INDEX.md) for the container that serves each surface.
- Link to [`../security/`](../security/INDEX.md) for the restriction that guards each surface.
- Link to [`../devops/infra/`](../devops/infra/INDEX.md) for the deployment target that hosts each surface.
