# N. <Area Title>

> **Last reviewed:** YYYY-MM-DD
> **Canonical references:**
> - [Architecture: <page>](../architecture/c4/containers/NN-slug.md)
> - [SOP: <slug>](../sops/<slug>-sop.md)

## N.1 Overview

2 to 3 sentences. State what this area restricts and why it exists. A non-engineer must be able to read it.

## N.2 Controls

One control per row. A layered control gets one row per layer. Never cite a line number.

| # | Restriction | Where enforced | Reference |
| --- | --- | --- | --- |
| N.2.1 | Only a project admin can change project settings | `apps/api/plane/app/permissions/project.py` (`ProjectAdminPermission`) | [Arch](../architecture/c4/components/NN-slug.md) |
| N.2.2 | An API key request is rejected without a valid `X-API-Key` header | `apps/api/plane/api/middleware/api_authentication.py` (`APIKeyAuthentication`) | - |
| N.2.3 | A request body above the configured limit is rejected before parsing | `apps/api/plane/middleware/request_body_size.py` | - |

## N.3 Known gaps

This section is required. An empty list is acceptable. Be honest.

- <A restriction a reader expects to exist but does not, and the reason>
- <A control that is server-side only, where the client check is best-effort>
- <A control with no automated test that proves it stays in place>

## N.4 Verification

How to prove these controls still hold.

- **Tests**: `apps/api/tests/...`
- **Grep**: `grep -rn "<symbol>" apps/api/plane/`
- **CI check**: <The job that fails when the control is removed, or `none`>
- **Manual check**: <The request that must be refused, and the expected status code>
