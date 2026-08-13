# New Feature Spec Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. This file adds the rules that apply to `docs/features/new/`.

A page here specifies **a capability that does not exist yet**. A reader must be able to build it without asking the author a question.

## Naming

- One file per capability. `<WORK-ITEM-ID>-<slug>.md`, or `<slug>.md` when no work item exists.
- Do not add a date. A new capability is specified once.
- Do not create a folder per feature. If a spec needs an image or a diagram source, put it in `assets/<slug>/`.

## Required sections

Follow [`TEMPLATE.md`](./TEMPLATE.md). Every spec needs these sections.

| Section | Content |
| --- | --- |
| Header block | Status, owner, date, work item link, pull request link |
| Goal | The user problem, in one or two sentences |
| Non-goals | What this spec explicitly refuses to cover |
| User stories | One line each, in `As a / I want / so that` form |
| UX flow | The happy path, plus the loading, empty, error, and success states |
| API contract | Every endpoint, with the request, the response, and every error code |
| Data model | Every table touched, plus the migration and backfill answer |
| Frontend plan | Routes, components, stores, and translation keys |
| Permissions | Which role can do what |
| Test plan | The cases that must pass, backend and frontend |
| Rollout | Feature flag, staged steps, and the rollback |
| Open questions | Anything unresolved, with the person who decides |

## Non-goals are mandatory

A spec without non-goals invites scope creep. Name at least one thing this feature will not do.

## Every state, not just the happy path

The UX flow section needs four states. A spec that only describes success is incomplete.

| State | Must state |
| --- | --- |
| Loading | What the user sees while the request is in flight |
| Empty | What the user sees with no data, and the next action offered |
| Error | The message, and whether a retry is offered |
| Success | The confirmation, and where the user lands |

## API contract rules

- Give the exact method and path. Example: `POST /api/v1/workspaces/{slug}/projects/{id}/cycles/`.
- Name the authentication: session, `X-API-Key`, or OAuth bearer.
- List every error code the endpoint returns, with the trigger for each.
- Show one real request body and one real response body in a fenced `json` block.
- Never invent a field name. Match the serializer field names you plan to add.

## Data model rules

- Name every table the feature touches, read or write.
- Answer two questions explicitly: "Migration needed?" and "Backfill needed?". Write `yes` or `no`.
- If the answer is `yes`, state the migration strategy and the rollback.

## Permissions

Name the DRF permission class the endpoint will use. Example: `ProjectMemberPermission`.

State the behavior for every role that can reach the endpoint. A spec that says "admins only" without naming the class is incomplete.

## Repo rules

- Name the translation key for every user-facing string. Keys live in `packages/i18n/src/locales`.
- Name the Canvas, Surface, or Layer choice for new UI. See `packages/tailwind-config/AGENTS.md`.
- Name the MobX store that owns the new state.
- A pull request targets `dev`.

## After the feature ships

Follow the checklist in [`../AGENTS.md`](../AGENTS.md). Set the status to `Shipped`, then update the matching [`../../architecture/`](../../architecture/INDEX.md) page.
