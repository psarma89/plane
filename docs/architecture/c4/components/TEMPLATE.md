# N. <Container>: <Journey or Map Title>

> **Last reviewed:** YYYY-MM-DD
> **Level:** L3 Components
> **Container:** `apps/web`
> **Scope:** One sentence. State what the user does and what the outcome is.

### Related feature specs

| Spec | Description | Status |
| --- | --- | --- |
| [<Feature name>](../../../features/new/<slug>.md) | One-line summary | Shipped / Partial / Draft |

## N.1 Component diagram

```mermaid
C4Component
    title Components inside apps/web for <journey>

    Container_Boundary(web, "web") {
        Component(route, "Route", "React Router", "Loads the screen")
        Component(view, "Detail panel", "React", "Renders and edits fields")
        Component(store, "<Store>", "MobX", "Owns the observable state")
        Component(svc, "<Service>", "TypeScript", "Calls the REST API")
    }

    Container(api, "api", "Django, DRF", "REST API")

    Rel(route, view, "Renders")
    Rel(view, store, "Reads, dispatches")
    Rel(store, svc, "Calls")
    Rel(svc, api, "REST, JSON")
```

## N.2 Key files

Delete a row that does not apply.

| Layer | File |
| --- | --- |
| Route | `apps/web/app/routes/...` |
| Layout | `apps/web/core/layouts/...` |
| Component | `apps/web/core/components/...` |
| Hook | `apps/web/core/hooks/...` |
| Service | `apps/web/core/services/...` |
| Store | `apps/web/core/store/...` |
| Shared package | `packages/ui/...` |
| API URL | `apps/api/plane/app/urls/...` |
| API view | `apps/api/plane/app/views/...` |
| Serializer | `apps/api/plane/app/serializers/...` |
| Permission | `apps/api/plane/app/permissions/...` |
| Model | `apps/api/plane/db/models/...` |
| Background task | `apps/api/plane/bgtasks/...` |

## N.3 Key components

**`<ComponentName>`** renders <what>. It <key behavior>. It blocks <user-facing constraint>.

- Background classes: `bg-surface-1` with `bg-layer-1` children. See `packages/tailwind-config/AGENTS.md`.
- Translation keys: `<namespace>.<key>` in `packages/i18n/src/locales`.

## N.4 Key state

Delete this section on a container with no store, for example `apps/live`. Say why rather than leaving an empty table.

**`<StoreName>`** (`apps/web/core/store/...`)

| Observable | Type | Purpose |
| --- | --- | --- |
| `<name>` | `<type>` | What it holds and who reads it |

| Action | Effect |
| --- | --- |
| `<actionName>` | What it changes, and which service it calls |

## N.5 Key data models

**`<ModelName>`** (`<table_name>` table, `apps/api/plane/db/models/...`)

| Field | Type | Constraints |
| --- | --- | --- |
| `id` | UUID | Primary key, default `uuid4()` |
| `name` | CharField(255) | Not null |
| `created_at` | DateTimeField | Auto add |

- Note any storage decision a reader cannot guess. Example: "Soft-deleted, not removed."

## N.6 Data flow

```mermaid
flowchart TD
    A[User action] --> B[Component handler]
    B --> C[Store action]
    C --> D[Service call]
    D --> E[API view]
    E --> F{Valid?}
    F -->|Yes| G[Persist and return 200]
    F -->|No| H[Return 400 with field errors]
    G --> I[Store updates observable]
    H --> J[Component shows inline error]
```

- **Primary path**: The route through the flow when every step succeeds.
- **Branch**: The main decision point and both outcomes.
- **Design choice**: Something a reader cannot guess from the code.

## N.7 Acceptance criteria

Write each rule from the code that enforces it. Mark a UI-only rule as "client-side only".

- <Validation rule and where it is enforced>
- <Permission boundary, with the DRF permission class that enforces it>
- <Error handling behavior the user sees>

## N.8 Verification

- **Tests**: `apps/api/tests/...`, `apps/web/...`
- **Command**: The exact command that exercises this journey.

## N.9 Related

| Page | Why it matters here |
| --- | --- |
| [<L2 page>](../containers/NN-slug.md) | The flow that crosses into this container |
| [<L4 page>](../code/NN-slug.md) | Call detail for one hard function here |
| [<Security page>](../../../security/NN-slug.md) | The restriction enforced here |
