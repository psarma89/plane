# L3 Components

Inside one container: the modules, routes, stores, and models. This is where application architecture lives.

Read [`../AGENTS.md`](../AGENTS.md) for the shared rules, then [`AGENTS.md`](./AGENTS.md) for the L3 rules. Follow [`TEMPLATE.md`](./TEMPLATE.md).

## Pages

Every application container has a structural page, so this level meets the C4 completeness bar.

Entry format: `- [N. Title](./NN-slug.md) - container - Structural | Dynamic - one-line summary`

- [1. apps/api: module map](./01-api-module-map.md) - `apps/api` - Structural - Four parallel API surfaces over one model and one permission layer.
- [2. apps/web: component map](./02-web-component-map.md) - `apps/web` - Structural - Route table, 30 MobX slices, and 46 services.
- [3. apps/admin: component map](./03-admin-component-map.md) - `apps/admin` - Structural - God Mode. 4 stores and 6 settings areas.
- [4. apps/live: component map](./04-live-component-map.md) - `apps/live` - Structural - Express, Hocuspocus, and five extensions.
- [5. apps/space: component map](./05-space-component-map.md) - `apps/space` - Structural - Plane Publish. The only SSR frontend, addressed by anchor.
- [6. apps/proxy: component map](./06-proxy-component-map.md) - `apps/proxy` - Structural - The Caddy route table, in match order.

## The process test

C4 states that "all components inside a container execute in the same process space", and that a component is never the deployable unit.

So one test decides whether a page belongs here. **If two things run in separate processes, they are containers, and the page is L2.**

A Celery task definition sits in the `api` process, so it is L3. The same task executing in `worker` crosses a process, so it is L2.

## Page kinds and shapes

[`AGENTS.md`](./AGENTS.md) defines the two kinds (structural and dynamic), the two shapes (per container and per journey), and the process test that decides whether a page belongs here or in [`../l2-containers/`](../l2-containers/INDEX.md).

## Journey backlog

Every container page exists. These are journey pages, which come second. This list is a backlog, not a claim that the pages exist. Delete a row when you write the page.

| Page | Container |
| --- | --- |
| Authentication and onboarding | `apps/web` |
| Work item list, kanban, and spreadsheet layouts | `apps/web` |
| Work item detail and activity feed | `apps/web` |
| Cycles and modules | `apps/web` |
| Pages and the collaborative editor | `apps/web`, `packages/editor` |
| Analytics and dashboards | `apps/web` |
| Notifications and inbox | `apps/web` |
| Workspace settings, members, and tokens | `apps/web` |

## Container reference

Dev ports are the host ports when the app runs outside Docker with `pnpm dev`. Every container listens on its own internal port inside Docker, which [`../l2-containers/01-container-overview.md`](../l2-containers/01-container-overview.md) lists.

| Container | Path | Stack | Dev port |
| --- | --- | --- | --- |
| Web | `apps/web` | React Router 7, Vite, MobX. `ssr: false`. | 3000 |
| Admin | `apps/admin` | React Router 7, Vite. `ssr: false`. | 3001 |
| Space | `apps/space` | React Router 7, Vite. `ssr: true`. | 3002 |
| API | `apps/api` | Django, DRF, Celery | 8000 |
| Live | `apps/live` | Express, Hocuspocus, Yjs | 3100 |
| Proxy | `apps/proxy` | Caddy | n/a |

## Related

- [../l2-containers/INDEX.md](../l2-containers/INDEX.md) covers flows that cross containers.
- [../l4-code/INDEX.md](../l4-code/INDEX.md) covers one hard algorithm in call detail.
- [../../../features/INDEX.md](../../../features/INDEX.md) holds the specs that drove each journey.
- `packages/tailwind-config/AGENTS.md` defines the background class rules for every app.
