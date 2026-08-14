---
name: plane-test-live
description: Run the Vitest suites for apps/live and packages/codemods. Use when TypeScript in apps/live or packages/codemods changed, or when someone asks whether the JavaScript tests pass. Also states what these suites do not cover, which matters because apps/live is the collaboration server and no test touches collaboration.
user_invocable: true
---

# Run the JavaScript tests

Two Vitest suites. No Docker, no `.env`, no running stack.

| Workspace           | Tests | Duration |
| ------------------- | ----- | -------- |
| `apps/live`         | 32    | 4.3 s    |
| `packages/codemods` | 33    | 0.2 s    |

## Run them

```bash
pnpm build          # required: both suites import from @plane/* dist
pnpm turbo run test
```

Expect `14 successful, 14 total`. That is 2 test tasks plus 12 build tasks,
because `turbo.json` gives the `test` task `dependsOn: ["^build"]`.

One suite:

```bash
pnpm --filter live test
pnpm --filter @plane/codemods test
```

## Subsets, from apps/live

| Scope            | Command                                                            |
| ---------------- | ------------------------------------------------------------------ |
| Watch            | `pnpm vitest`                                                      |
| Coverage         | `pnpm vitest run --coverage`                                       |
| One file         | `pnpm vitest run tests/lib/pdf/pdf-rendering.test.ts`              |
| One test by name | `pnpm vitest run -t "should render heading nodes and verify text"` |

`vitest.config.ts` includes only `tests/**/*.test.ts` and `tests/**/*.spec.ts`.
A test file outside `tests/` never runs.

## What these suites do not cover

Say this out loud when someone reads a green run as proof.

`apps/live` is the collaboration server. It runs Hocuspocus over websockets and
keeps document state in Valkey. Its 32 tests cover PDF rendering and PDF export
helpers, and they import pure functions. No test starts the server, opens a
websocket, or touches Valkey. Coverage measures 2 test files against 43 source
files.

A green `apps/live` run says nothing about whether collaboration works. Check
that by opening one document in two browser tabs.

`apps/web`, `apps/admin`, and `apps/space` have no `test` script and no test
files. The three user-facing frontends have no unit tests at all.

## Traps

| Symptom                                 | Cause                                      | Fix                                     |
| --------------------------------------- | ------------------------------------------ | --------------------------------------- |
| `Cannot find module '@plane/...'`       | Workspace packages are not built           | `pnpm build`                            |
| `EEXIST` in `packages/propel/dist`      | A `pnpm dev` is writing the same directory | Stop it, `pnpm build`, then retry       |
| Turbo succeeds without running anything | Cached result                              | Change a source file, or pass `--force` |
| A new test never runs                   | It sits outside `tests/`                   | Move it under `apps/live/tests/`        |

## Related

- `docs/sops/run-javascript-tests-sop.md` is the same procedure for a human.
- `plane-test-api` runs the 516 Python tests in Docker.
