# Application Architecture

One page per user journey, inside one app. Each page names the files, the components, the models, and the rules the code enforces.

Read [`AGENTS.md`](./AGENTS.md) before you add a page. Follow [`TEMPLATE.md`](./TEMPLATE.md).

## Pages

> No page exists yet. Add the first page with [`TEMPLATE.md`](./TEMPLATE.md), then list it here.

Entry format: `- [N. Title](./NN-slug.md) - one-line summary`

<!-- - [1. Authentication](./01-authentication.md) - Sign-in, sign-up, and session handling in apps/web. -->

## Suggested first pages

This list is a backlog, not a claim that the pages exist. Delete a row when you write the page.

| Journey | App |
| --- | --- |
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

## App reference

| App | Path | Stack | Dev port |
| --- | --- | --- | --- |
| Web | `apps/web` | React Router 7, Vite, MobX | 3000 |
| Admin | `apps/admin` | React Router 7, Vite | 3001 |
| Space | `apps/space` | React Router 7, Vite | 3002 |
| API | `apps/api` | Django, DRF, Celery | 8000 |
| Live | `apps/live` | Express, Hocuspocus, Yjs | - |

## Related

- [../system/INDEX.md](../system/INDEX.md) traces a concern across two or more apps.
- [../c4/INDEX.md](../c4/INDEX.md) draws the container boundaries.
- [../../features/INDEX.md](../../features/INDEX.md) holds the specs that drove each journey.
- `packages/tailwind-config/AGENTS.md` defines the background class rules for every app.
