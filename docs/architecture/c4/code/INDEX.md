# L4 Code

One algorithm, traced through classes and calls. This level is optional and rarely used.

Read [`../AGENTS.md`](../AGENTS.md) for the shared rules, then [`AGENTS.md`](./AGENTS.md) for the gate a page must pass. Follow [`TEMPLATE.md`](./TEMPLATE.md).

## Pages

Entry format: `- [N. Title](./NN-slug.md) - entry point - one-line summary`

- [1. Document synchronisation](./01-document-synchronisation.md) - `apps/live/src/controllers/collaboration.controller.ts` - Keystroke to Postgres, across two `live` instances, Redis, and the REST API.

One page is the expected size of this folder. The C4 model recommends this level only for the most important or complex components, so a second page needs its own trip through the gate in [`AGENTS.md`](./AGENTS.md).

### Why this one passed the gate

Real-time document sync is the only algorithm in Plane that spans the repository and a third-party library, carries a silent data-loss failure mode, and has no test coverage on its write path. Everything else a reader needs is answerable at L3.

## Related

- [`../components/INDEX.md`](../components/INDEX.md) covers the module that holds the algorithm.
- [`../containers/INDEX.md`](../containers/INDEX.md) covers flows that cross containers.
