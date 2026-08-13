# System Architecture Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. This file adds the rules that apply to `docs/architecture/system/`.

A system page traces **one runtime concern end to end**, across two or more units in `apps/`. It answers: what happens, in what order, through which services.

## What belongs here

A page belongs here when both statements are true.

1. The concern crosses two or more of `apps/api`, `apps/web`, `apps/admin`, `apps/space`, `apps/live`, or `apps/proxy`.
2. The concern exists at runtime, not only at build time or deploy time.

| Subject | Belongs here | Why |
| --- | --- | --- |
| Request lifecycle from proxy to database | Yes | Crosses proxy, app, and API |
| Background job dispatch and retry through Celery | Yes | Crosses API and worker |
| Real-time document sync | Yes | Crosses `apps/live` and the React Router apps |
| Session and token authentication | Yes | Crosses every app |
| File upload and object storage | Yes | Crosses API, storage, and the browser |
| Which MobX store owns cycle state | No | One app. Use [`../application/`](../application/INDEX.md). |
| Which GitHub Actions job gates a pull request | No | Build time. Use [`../../devops/cicd/`](../../devops/cicd/INDEX.md). |
| The steps to rotate a secret | No | A procedure. Use [`../../sops/`](../../sops/INDEX.md). |

## Naming

- Files use `NN-<slug>.md`, zero-padded from `01`.
- One page covers one concern. Do not bundle two concerns to save a number.
- A new page takes the next free number. Do not renumber an existing page.
- Sections use `## N.1` and `## N.2`, and match the page number.

## Required sections

Follow [`TEMPLATE.md`](./TEMPLATE.md). Every page needs these sections.

| Section | Content |
| --- | --- |
| Header block | `Last reviewed` stamp and the units involved |
| Related feature specs | Table of the specs that drove the current design |
| Participants | One row per service, queue, or store in the flow |
| Sequence | A Mermaid `sequenceDiagram` of the happy path |
| Failure modes | One row per failure, with the observable symptom and the recovery |
| Configuration | The environment variables that change the behavior |
| Verification | How to prove the flow still works |

## Failure modes are mandatory

A system page without a failure modes table is incomplete. For each failure, state three things.

1. What breaks.
2. What a user or an operator observes.
3. What recovers it, or which SOP recovers it.

## Configuration

- Name each environment variable in backticks, exactly as the code reads it.
- Give the default value. If there is no default, write `no default`.
- Do not paste a real secret value. Write `<redacted>`.
- Point to `.env.example` or `apps/api/.env.example` as the canonical list.

## Cross-links

- Link down to an [`../application/`](../application/INDEX.md) page for file-level detail.
- Link out to [`../c4/`](../c4/INDEX.md) for the container boundary.
- Link out to [`../../sops/`](../../sops/INDEX.md) for every recovery step.
- Link out to [`../../devops/monitoring/`](../../devops/monitoring/INDEX.md) for the signal that detects a failure.
