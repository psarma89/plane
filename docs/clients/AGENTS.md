# Client Docs Conventions

A client page answers one question: **what are all the ways to consume Plane, and how does a user or a script reach each one?** It describes the surface, not the internals. Internals live in [`../architecture/`](../architecture/INDEX.md).

## Surface against implementation

| Content | Folder |
| --- | --- |
| "The REST API accepts an `X-API-Key` header and rate limits at 60 requests per minute." | `clients/` |
| "`APIKeyAuthentication` resolves the key and attaches the user." | [`../architecture/`](../architecture/INDEX.md) |
| "The API key check rejects a revoked token." | [`../security/`](../security/INDEX.md) |

If a sentence names a Python class or a React component, it belongs in `architecture/`. Move it.

## Availability

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
