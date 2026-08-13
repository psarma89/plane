# Feature: <Title>

> **Status:** Draft | Agreed | In progress | Shipped | Abandoned
> **Owner:** <Name>
> **Date:** YYYY-MM-DD
> **Work item:** <Plane work item ID and link>
> **Pull request:** <Link, once one exists>

## Goal

One or two sentences. State the user problem, not the solution.

## Non-goals

At least one item. Name what this feature will not do.

- <Out of scope>
- <Out of scope>

## User stories

- As a <role>, I want <capability>, so that <outcome>.
- As a <role>, I want <capability>, so that <outcome>.

## UX flow

### Happy path

1. <User action>.
2. <System response>.
3. <End state>.

### States

Every row is required.

| State | What the user sees | Next action offered |
| --- | --- | --- |
| Loading | <Skeleton, spinner, or optimistic result> | - |
| Empty | <Message> | <Action> |
| Error | <Message and whether a retry is offered> | <Action> |
| Success | <Confirmation and where the user lands> | <Action> |

## API contract

### `<METHOD> /api/v1/<path>`

- **Authentication**: Session | `X-API-Key` | OAuth bearer
- **Permission class**: `<PermissionClass>` in `apps/api/plane/app/permissions/...`
- **Query parameters**: <name, type, required>

**Request**

```json
{
  "field": "value"
}
```

**Response 201**

```json
{
  "id": "uuid",
  "field": "value"
}
```

**Errors**

| Code | Trigger |
| --- | --- |
| 400 | <Validation failure> |
| 401 | <No credential> |
| 403 | <Role lacks permission> |
| 404 | <Resource not found or not visible> |

## Data model

| Table | Read | Write | New |
| --- | --- | --- | --- |
| `<table_name>` | Yes | Yes | No |

| New or changed field | Type | Constraints | Default |
| --- | --- | --- | --- |
| `<field>` | `<type>` | <constraints> | `<default>` |

- **Migration needed?** yes / no. If yes: <strategy>.
- **Backfill needed?** yes / no. If yes: <strategy and expected row count>.
- **Migration rollback**: <How to reverse, or why it is forward-only>.

## Frontend plan

| Layer | Path | Change |
| --- | --- | --- |
| Route | `apps/web/app/routes/...` | New / Changed |
| Component | `apps/web/core/components/...` | New / Changed |
| Hook | `apps/web/core/hooks/...` | New / Changed |
| Service | `apps/web/core/services/...` | New / Changed |
| Store | `apps/web/core/store/...` | New / Changed |
| Shared package | `packages/ui/...` | New / Changed |

- **Data fetching**: <Which service call, and which store action holds the result>.
- **State owner**: `<StoreName>` owns `<observable>`.
- **Background classes**: <Canvas, Surface, or Layer choice. See `packages/tailwind-config/AGENTS.md`.>
- **Translation keys**: `<namespace>.<key>` in `packages/i18n/src/locales`. List every new key.
- **Accessibility**: <Labels, focus order, and keyboard path>.

## Permissions

| Role | Can do | Cannot do |
| --- | --- | --- |
| Workspace owner | <Actions> | <Actions> |
| Workspace admin | <Actions> | <Actions> |
| Project member | <Actions> | <Actions> |
| Guest | <Actions> | <Actions> |

## Test plan

### Backend

- <Case that must pass, and the rule it proves>
- <Permission case: the request a non-admin must not complete>

### Frontend

- <Case that must pass, and the rule it proves>
- <Error-state case>

## Rollout

- **Feature flag?** yes / no. If yes: `<FLAG_NAME>` and its default.
- **Staged steps**:
  1. <Step>
  2. <Step>
- **Rollback**: <The exact steps to remove the feature from users>.

## Open questions

| # | Question | Decides | Resolved |
| --- | --- | --- | --- |
| 1 | <Question> | <Role> | <Date or blank> |

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| <Risk> | <What breaks> | <What we do about it> |
