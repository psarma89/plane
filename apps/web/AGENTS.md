# Frontend conventions

This file supplements the root `AGENTS.md`. It does not restate or override the root rules.

Scope: `apps/web/`. React Router v7 in client-only mode, Vite, MobX, Tailwind.

Every pattern count lives in [`docs/architecture/plane-patterns-census.md`](../../docs/architecture/plane-patterns-census.md), with the command that re-measures it.

## Where code goes

- Put a new API client in `core/services/` and import it as `@/services`. The `@plane/services` package exists, but the local directory wins by import count. The census holds the numbers.
- Register a new MobX store at the narrowest root store that owns its data lifetime. The tree is nested. A store scoped to issue detail registers on `core/store/issue/issue-details/root.store.ts`, not on `core/store/root.store.ts`.
- Promote a store to `@plane/shared-state` only when a second app needs it.
- `EmptyStateCompact` lives in `packages/propel/src/empty-state/compact-empty-state.tsx`. The export name and the file name are inverted, so search for the export, not the file name.

## MobX rules

Wrap every component that reads an observable in `observer`. The convention is pervasive, so a missing wrapper is an omission, not a style choice.

- Mutate an observable inside an action only, never from a component. Register a new action in the class's `makeObservable` call.
- Clear store state on a workspace or project switch. Stale cross-tenant state in the UI is a real defect.
- An optimistic update needs a rollback path, because the API can reject the change. Copy `issueUpdate` in `core/store/issue/helpers/base-issues.store.ts`: snapshot, mutate, call, catch, restore. The bulk actions in the same file call the API first and carry no rollback. They are a known gap, not a precedent.

## Client-only rendering

`react-router.config.ts` sets `ssr: false`. The build emits a static client bundle. Do not introduce a pattern that assumes server rendering or server-side data loading.

## Traps

- **`@plane/types` is a built package, not source.** Its exports point at the built `dist` output, and `pnpm --filter web check:types` does not build workspace dependencies. After you edit `packages/types/src/`, run `pnpm --filter @plane/types build` first. Without the build, the new type reports `has no exported member`, which reads like a typo in the import.
- **Issue stores construct the root store at import time.** `core/store/issue/helpers/base-issues-utils.ts` imports `@/lib/store-context` at module load. A test that imports an issue store throws `Class extends value undefined`. Mock the context before the import under test: `vi.mock("@/lib/store-context", () => ({ store: {} }))`. This app ships no test suite today, so the first test will meet this.
- **The URL validators disagree across the stack.** `checkURLValidity` in `packages/utils/src/string.ts` accepts `example.com` on purpose. Django's `URLField` rejects it, so the save returns a 400 that the user cannot act on. Add a protocol prefix before submit, as `core/components/issues/issue-detail/links/create-update-link-modal.tsx` does. The serializer is the contract. The client validator is a convenience.
- **Bulk operations are an enterprise stub in this build.** `IssueService.bulkOperations` posts to a `bulk-operation-issues` route that this backend does not serve. `core/components/issues/bulk-operations/root.tsx` renders only an upgrade banner. Do not assume that backend route or that mount point.

## Strings

Every user-facing string is an i18n key. For any change under `packages/i18n/src/locales/`, use the `translate` skill. The key prefix is not the file name. `work-item.json` holds keys under `issue.*`, `sub_work_item.*`, `issue_comment.*`, and more. Search for an existing key before you add one.

## States and checks

A feature is complete when it has a loading state, an error state, and an empty state where a list can be empty. Use `Loader` from `@plane/ui` and `EmptyStateCompact` from `@plane/propel`. For background and text classes, the root `AGENTS.md` points at the `plane-backgrounds` skill.

For lint, format, and type checks, use the `plane-check-static` skill or `docs/sops/run-static-checks-sop.md`. The oxlint ceiling in `package.json` is a historical high-water mark far above the real warning count, so a repo-wide lint run proves nothing. Lint the files you touched. The census holds the ceiling and the current count.
