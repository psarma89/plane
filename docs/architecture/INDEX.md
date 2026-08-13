# Architecture

How Plane works today. Every page lives under [`c4/`](./c4/INDEX.md), organized by the four levels of the [C4 model](https://c4model.com/).

## Why one structure

C4 already spans both system architecture and application architecture. The level states the zoom, so no separate split is needed.

| Level | Reads as | Folder |
| --- | --- | --- |
| **L1 Context** | System architecture | [c4/context/](./c4/context/INDEX.md) |
| **L2 Containers** | System architecture | [c4/containers/](./c4/containers/INDEX.md) |
| **L3 Components** | Application architecture | [c4/components/](./c4/components/INDEX.md) |
| **L4 Code** | Application architecture | [c4/code/](./c4/code/INDEX.md) |

[c4/INDEX.md](./c4/INDEX.md) shows how the four levels nest.

## Where to start

| You want to | Read |
| --- | --- |
| Understand Plane for the first time | [c4/context/](./c4/context/INDEX.md), then [c4/containers/](./c4/containers/INDEX.md) |
| Trace a request from browser to database | [c4/containers/](./c4/containers/INDEX.md) |
| Change a screen or an endpoint | [c4/components/](./c4/components/INDEX.md) |
| Deploy or operate the product | [../devops/INDEX.md](../devops/INDEX.md) |

## Related areas

- [../clients/INDEX.md](../clients/INDEX.md) lists every interface a user or a script can reach.
- [../security/INDEX.md](../security/INDEX.md) lists every restriction and the code that enforces it.
- [../features/INDEX.md](../features/INDEX.md) holds the specs that drove each change.
