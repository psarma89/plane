# L1 Context Conventions

An L1 page treats **Plane as one box**. It names who uses Plane and what Plane depends on. It never opens the box.

## What belongs here

| Subject | Belongs here |
| --- | --- |
| The user types that reach Plane | Yes |
| Every external service Plane calls | Yes |
| Every external system that calls Plane | Yes |
| The data category that crosses each boundary | Yes |
| The containers inside Plane | No. Use [`../containers/`](../containers/INDEX.md). |
| A named app such as `apps/web` | No. That is inside the box. |

If a sentence names a container, a file, or a class, the page is at the wrong level.

## Keep the page count at one, or close to it

Plane has one system context. One page covers it. Add a second page only for a genuinely separate context, for example a hosted control plane that self-hosted installs never reach.

Do not create a page per integration. An integration is a row in the external systems table.

## System landscape diagrams

C4 defines a system landscape diagram as a supplementary type. It shows several software systems inside one organization.

Plane is one software system, so no landscape page is needed today. If one becomes useful, it files here, because it operates above the container level. Name it `NN-system-landscape.md` and state which systems it covers.

## Actors

- Name the role as the product names it: workspace owner, workspace admin, project member, guest.
- Add an anonymous actor where a surface accepts unauthenticated traffic.
- State which surface each actor reaches. The L1 page lists every surface in its `Delivery surfaces` appendix.

## External systems

Every row needs a **Data sent** value. Every row also needs a **Required** value, which states whether Plane works without the integration.

Add an **Availability** value where the repository proves it, using `Cloud`, `Self-hosted`, `Both`, or `Commercial`. Omit the column when it cannot, and say so on the page. This repository builds the Community Edition only, so a page written from this source usually cannot prove which edition an integration reaches, and inventing the value is worse than omitting it.

- **Data sent** names the data category, not the field list. Example: "Email address", "Work item content", "Telemetry events".
- **Availability** uses `Cloud`, `Self-hosted`, `Both`, or `Commercial`.
- Mark an optional integration as optional. A self-hosted install can run without most of them.
- Never write a real endpoint, a bucket name, or a tenant identifier.

## Do not invent an integration

List an external system only when the repo shows it. Cite the source that proves it, for example a settings variable in `apps/api/plane/settings/` or a dependency in `docker-compose.yml`.

If a system is configured but optional, say so, and name the variable that enables it.
