# L1 Context Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. It holds the naming, diagram, label, and table rules for every level. This file adds only what is specific to L1.

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

## Required sections

Follow [`TEMPLATE.md`](./TEMPLATE.md). Every page needs these sections.

| Section | Content |
| --- | --- |
| Header block | `Last reviewed` stamp and the scope sentence |
| Related feature specs | Table of specs that drove the current design |
| Diagram | A Mermaid `C4Context` diagram |
| Actors | One row per user type, with what they do |
| External systems | One row per system, with purpose, data sent, and availability |
| Trust boundaries | One row per zone, with its exposure |
| Notes | Three summary bullets |

## Actors

- Name the role as the product names it: workspace owner, workspace admin, project member, guest.
- Add an anonymous actor where a surface accepts unauthenticated traffic.
- State which surface each actor reaches. Link to [`../../../clients/INDEX.md`](../../../clients/INDEX.md).

## External systems

Every row needs a **Data sent** value and an **Availability** value. A row without both is incomplete.

- **Data sent** names the data category, not the field list. Example: "Email address", "Work item content", "Telemetry events".
- **Availability** uses `Cloud`, `Self-hosted`, `Both`, or `Commercial`.
- Mark an optional integration as optional. A self-hosted install can run without most of them.
- Never write a real endpoint, a bucket name, or a tenant identifier.

## Do not invent an integration

List an external system only when the repo shows it. Cite the source that proves it, for example a settings variable in `apps/api/plane/settings/` or a dependency in `docker-compose.yml`.

If a system is configured but optional, say so, and name the variable that enables it.
