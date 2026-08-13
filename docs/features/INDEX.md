# Features

What we plan to build or change, and why. A page here is a specification. It is not a description of the current system.

Read [`AGENTS.md`](./AGENTS.md) before you add a page.

## Sub-folders

| Sub-folder | Holds | Index |
| --- | --- | --- |
| **New** | A capability that does not exist yet | [new/INDEX.md](./new/INDEX.md) |
| **Changes** | A change to behavior that already ships | [changes/INDEX.md](./changes/INDEX.md) |
| **Bugfixes** | A defect: the system does not do what it claims | [bugfixes/INDEX.md](./bugfixes/INDEX.md) |

## Which one

```mermaid
flowchart TD
    Q1{Does a user gain a<br/>new ability?} -->|Yes| NEW[new/]
    Q1 -->|No| Q2{Does today's behavior<br/>match the docs?}
    Q2 -->|Yes| CHG[changes/]
    Q2 -->|No| BUG[bugfixes/]
```

A defect whose fix changes documented behavior goes in `changes/`. Link to it from `bugfixes/`.

## Status values

Every page carries one status in its header block.

| Status | Meaning |
| --- | --- |
| `Draft` | Written. Not agreed. |
| `Agreed` | Reviewed and accepted. Work can start. |
| `In progress` | Implementation started. |
| `Shipped` | Merged and released. |
| `Abandoned` | Will not be built. The reason is in the page. |

Never delete an abandoned page. A rejected idea is knowledge.

## Lifecycle

```mermaid
flowchart LR
    D[Draft] --> A[Agreed]
    A --> P[In progress]
    P --> S[Shipped]
    S --> ARCH[Update ../architecture/]
    D --> X[Abandoned]
    A --> X
```

When a page reaches `Shipped`, update the matching architecture page in the same pull request. The architecture page describes the built result, not the proposal.

## Related

- [../architecture/INDEX.md](../architecture/INDEX.md) describes what exists today.
- [../security/INDEX.md](../security/INDEX.md) lists the restrictions a change can affect.
- [../../CONTRIBUTING.md](../../CONTRIBUTING.md) covers the pull request process.
