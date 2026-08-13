# Security Catalog Conventions

`docs/security/` is a flat, scannable **inventory of the restrictions Plane enforces today**. It is not a design doc set. That is [`../architecture/`](../architecture/INDEX.md). It is not a how-to set. That is [`../sops/`](../sops/INDEX.md).

Every row maps one runtime restriction to the code that enforces it.

Pages here use `NN-<area-slug>.md`. [`TEMPLATE.md`](./TEMPLATE.md) holds the four sections every page needs.

## Row rules

- **One control per row.** A layered control gets one row per layer. A server-side check and a client-side check are two rows.
- **`Where enforced`** holds a backticked path from the repo root, plus the symbol in backticks. Example: `` `apps/api/plane/app/permissions/project.py` (`ProjectAdminPermission`) ``.
- **`Reference`** prefers a relative link to the canonical doc. Use `[Arch](../architecture/c4/components/NN-slug.md)` or `[SOP](../sops/<slug>-sop.md)`. Write `-` when no canonical doc exists.
- **No paragraphs in a row.** If a control needs more than a sentence, the canonical doc is thin. Fix that doc. Keep the row short.

## When to add a row

Add a row when the code gains any of these.

| Code change | Catalog page |
| --- | --- |
| New DRF permission class in `apps/api/plane/app/permissions/` | Authentication and authorization |
| New `permission_classes` entry on a view | Authentication and authorization |
| New workspace or project role check | Authentication and authorization |
| Change to `APIKeyAuthentication` or API key scope | Authentication and authorization |
| New authentication backend or provider in `apps/api/plane/authentication/` | Authentication and authorization |
| New client-side route guard in `apps/web` or `apps/admin` | Authentication and authorization |
| New endpoint that reads or writes another workspace's data | Data access and tenancy |
| New raw SQL or `.extra()` call | Data access and tenancy |
| New serializer field that exposes a model field | Data access and tenancy |
| New public endpoint under `apps/api/plane/space/` | Data access and tenancy |
| New throttle class in `apps/api/plane/throttles/` | Abuse and rate limiting |
| Change to `request_body_size` middleware or `FILE_SIZE_LIMIT` | Abuse and rate limiting |
| New upload type or file extension accepted | Abuse and rate limiting |
| New route or header in `apps/proxy/Caddyfile.ce` | Network and transport |
| New Content Security Policy or security header | Network and transport |
| New WebSocket authorization check in `apps/live` | Network and transport |
| New outbound webhook target or signing change | Network and transport |
| New environment variable that holds a credential | Secrets and configuration |
| New default value that is insecure when unset | Secrets and configuration |
| New audit or security log line | Audit and logging |
| New license or edition gate | Licensing and edition gating |

If a change fits no row, add the trigger to this table in the same pull request.

## When to remove a row

Remove a row only when the control is genuinely gone. For one release cycle, leave a struck-through row with a removal date.

```markdown
| ~~N.2.X~~ | ~~Old restriction~~ | ~~`old/path.py`~~ | Removed YYYY-MM-DD |
```

## Honesty rules

- Never write an aspirational control. The catalog lists what the code does today.
- Never write a developer-discipline rule as a control. "Reviewers check for X" is not enforcement.
- If a control is best-effort, say so in the row.
- The `Known gaps` section is required. An empty list is acceptable. A missing section is not.

## Last reviewed stamp

Update the page stamp every time you add, change, or remove a row. The stamp tells a stakeholder whether the page is fresh.

## Vulnerability reporting

This folder is not the place to report a vulnerability. Follow [`../../SECURITY.md`](../../SECURITY.md).
