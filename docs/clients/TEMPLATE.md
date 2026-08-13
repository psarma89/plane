# N. <Surface Title>

> **Last reviewed:** YYYY-MM-DD
> **Canonical reference:** <https://docs.plane.so/...> or <https://developers.plane.so>

## N.1 Overview

Two sentences. State what this surface is for, and who uses it.

## N.2 Surfaces

Every row needs an availability value.

| Surface | Platform | Entry point | Availability |
| --- | --- | --- | --- |
| <Name> | <Browser, iOS, CLI, HTTP> | `<URL or command>` | Cloud / Self-hosted / Both / Commercial |

## N.3 Access

| Aspect | Value |
| --- | --- |
| Entry point | `<URL or command>` |
| Authentication | <Session, `X-API-Key`, OAuth bearer, or anonymous> |
| Rate limit | <Number and window, or `none`> |
| Pagination | <Cursor, offset, or `not paginated`> |
| Versioning | <Path version, header, or `unversioned`> |

## N.4 Availability

| Deployment | Edition | Offers this surface |
| --- | --- | --- |
| Cloud | - | yes / no |
| Self-hosted | Community | yes / no |
| Self-hosted | Commercial | yes / no |

Name the tier where a capability needs one.

## N.5 Known constraints

What this surface cannot do. A reader plans around a stated limit.

- <Limit, with the number where one exists>
- <Capability a reader expects and will not find>

## N.6 Related

| Page | Why it matters here |
| --- | --- |
| [<L2 structural page>](../architecture/c4/containers/NN-slug.md) | The container that serves this surface |
| [<Security page>](../security/NN-slug.md) | The restriction that guards this surface |
| [<Infra page>](../devops/infra/NN-slug.md) | The target that hosts this surface |
