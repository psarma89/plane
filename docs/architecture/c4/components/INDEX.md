# L3 Components

Inside one container: the modules, routes, stores, and models. This is where application architecture lives.

Read [`../AGENTS.md`](../AGENTS.md) for the shared rules, then [`AGENTS.md`](./AGENTS.md) for the L3 rules. Follow [`TEMPLATE.md`](./TEMPLATE.md).

## Pages

> No page exists yet. Add the first page with [`TEMPLATE.md`](./TEMPLATE.md), then list it here.

Entry format: `- [N. Title](./NN-slug.md) - container - one-line summary`

<!-- - [1. Web: authentication and onboarding](./01-web-authentication.md) - apps/web - Sign-in, sign-up, and session handling. -->

## Two page shapes

| Shape | Use when | Example title |
| --- | --- | --- |
| Per container | The container is small, or you need the map first | `Components inside apps/live` |
| Per journey | The container is large and the journey is self-contained | `Web: work item detail and activity` |

`apps/api` and `apps/web` are large. Prefer per journey there, and name the container in the title.

## Suggested first pages

This list is a backlog, not a claim that the pages exist. Delete a row when you write the page.

| Page | Container |
| --- | --- |
| Module map | `apps/api` |
| Authentication and onboarding | `apps/web` |
| Workspace and project setup | `apps/web` |
| Work item list, kanban, and spreadsheet layouts | `apps/web` |
| Work item detail and activity feed | `apps/web` |
| Cycles and modules | `apps/web` |
| Views and filters | `apps/web` |
| Pages and the collaborative editor | `apps/web`, `packages/editor` |
| Intake and work item creation | `apps/web` |
| Analytics and dashboards | `apps/web` |
| Notifications and inbox | `apps/web` |
| Workspace settings, members, and tokens | `apps/web` |
| Instance administration (God Mode) | `apps/admin` |
| Published boards and intake forms | `apps/space` |
| Document sync and awareness | `apps/live` |

## Container reference

| Container | Path | Stack | Dev port |
| --- | --- | --- | --- |
| Web | `apps/web` | React Router 7, Vite, MobX | 3000 |
| Admin | `apps/admin` | React Router 7, Vite | 3001 |
| Space | `apps/space` | React Router 7, Vite | 3002 |
| API | `apps/api` | Django, DRF, Celery | 8000 |
| Live | `apps/live` | Express, Hocuspocus, Yjs | - |

## Related

- [../containers/INDEX.md](../containers/INDEX.md) covers flows that cross containers.
- [../code/INDEX.md](../code/INDEX.md) covers one hard algorithm in call detail.
- [../../../features/INDEX.md](../../../features/INDEX.md) holds the specs that drove each journey.
- `packages/tailwind-config/AGENTS.md` defines the background class rules for every app.
