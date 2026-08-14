# Architecture

How Plane works today. Every page lives under [`c4/`](./c4/INDEX.md), organized by the four levels of the [C4 model](https://c4model.com/).

## Why one structure

C4 already spans both system architecture and application architecture. The level states the zoom, so no separate split is needed.

[c4/INDEX.md](./c4/INDEX.md) lists the four levels and shows how they nest.

## Where to start

| You want to                              | Read                                                                                                                                         |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Understand Plane for the first time      | [1. System context](./c4/l1-context/01-system-context.md), then [1. Container overview](./c4/l2-containers/01-container-overview.md)         |
| Trace a request from browser to database | [2. Request lifecycle](./c4/l2-containers/02-request-lifecycle.md)                                                                           |
| Change an endpoint                       | [1. apps/api: module map](./c4/l3-components/01-api-module-map.md)                                                                           |
| Change a screen                          | [2. apps/web: component map](./c4/l3-components/02-web-component-map.md)                                                                     |
| Work on the collaborative editor         | [4. apps/live](./c4/l3-components/04-live-component-map.md), then [1. Document synchronisation](./c4/l4-code/01-document-synchronisation.md) |
| Deploy or operate the product            | [../devops/INDEX.md](../devops/INDEX.md)                                                                                                     |

## Coverage

L1 to L3 are complete. L1 has its one context page, L2 has the structural overview plus the request lifecycle, and every application container has an L3 structural page. L4 holds one page, which is the expected size.

The open gaps are a deployment page for Compose and for the all-in-one image, and the journey pages listed in the L3 backlog.

## Pattern census

[plane-patterns-census.md](./plane-patterns-census.md) is the one page that sits outside `c4/`. It holds every measured pattern count, with the command that re-measures each one. `bin/check-counts` fails when a count drifts. It is a census, not an architecture page, so the C4 levels do not apply to it.

## Related areas

- [c4/l1-context/01-system-context.md](./c4/l1-context/01-system-context.md) lists every actor, every external system, and every interface a user or a script can reach.
- [../security/INDEX.md](../security/INDEX.md) lists every restriction and the code that enforces it.
- [../features/INDEX.md](../features/INDEX.md) holds the specs that drove each change.
