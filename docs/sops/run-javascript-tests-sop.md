# Run JavaScript Tests SOP

> **Last reviewed:** 2026-08-13
> **Owner role:** Contributor
> **Risk:** Low

## Purpose

Run the two Vitest suites in this monorepo and read the result.

## When to use

- **Trigger**: A contributor changed TypeScript in `apps/live` or `packages/codemods`.
- **Do not use this SOP when**: You changed Python. Read [`run-backend-tests-sop.md`](./run-backend-tests-sop.md) instead.
- **Do not use this SOP when**: You want lint, formatting, or type checks. Those are static checks, and no Vitest suite runs them.

## What exists, and what does not

Two workspaces carry a `test` script. No others do.

| Workspace           | Tests | Files | Duration |
| ------------------- | ----- | ----- | -------- |
| `apps/live`         | 32    | 2     | 4.3 s    |
| `packages/codemods` | 33    | 2     | 0.2 s    |

`apps/web`, `apps/admin`, and `apps/space` have **no** test script and no test files. The three user-facing frontends have no unit tests at all. Nothing in this SOP changes that, and no command here covers them.

## What a green run does not prove

`apps/live` is the collaboration server. It runs Hocuspocus over websockets and keeps document state in Valkey.

Its 32 tests cover PDF rendering and PDF export helpers. They import pure functions. **No test starts the server, opens a websocket, or touches Valkey.** A green `apps/live` run says nothing about whether collaboration works.

To check collaboration, open a document in two browser tabs. [`local-development-setup-sop.md`](./local-development-setup-sop.md) covers that.

## Prerequisites

Complete every item before step 1.

| Item                     | How to confirm                           |
| ------------------------ | ---------------------------------------- |
| Node 22.18.0 or later    | `node --version`                         |
| Dependencies installed   | `ls node_modules/.pnpm` prints entries   |
| Workspace packages built | `ls packages/propel/dist` prints entries |

Neither suite needs Docker, a `.env` file, or a running stack.

## Procedure

1. Build the workspace packages.

   ```bash
   pnpm build
   ```

   Expected result: `16 successful`. Both suites import from `@plane/*` packages, which resolve through `dist`.

2. Run both suites.

   ```bash
   pnpm turbo run test
   ```

   Expected result: `14 successful, 14 total` in about 5 seconds. That count is 2 test tasks plus 12 build tasks, because the `test` task in `turbo.json` sets `dependsOn: ["^build"]`.

## Running one suite

```bash
pnpm --filter live test
pnpm --filter @plane/codemods test
```

Expected result: `Test Files 2 passed (2)` and `Tests 32 passed (32)` for `live`, and `33 passed (33)` for `codemods`.

## Running less than one suite

Run these from `apps/live`.

| Scope            | Command                                                            |
| ---------------- | ------------------------------------------------------------------ |
| Watch            | `pnpm vitest`                                                      |
| Coverage         | `pnpm vitest run --coverage`                                       |
| One file         | `pnpm vitest run tests/lib/pdf/pdf-rendering.test.ts`              |
| One test by name | `pnpm vitest run -t "should render heading nodes and verify text"` |

`apps/live/vitest.config.ts` sets `include` to `tests/**/*.test.ts` and `tests/**/*.spec.ts`. A test file outside `tests/` never runs.

Coverage reports on `src/**/*.ts`, so it measures the 43 source files against 2 test files.

## Verification

| Check                       | Command                              | Expected                                 |
| --------------------------- | ------------------------------------ | ---------------------------------------- |
| Both suites ran             | `pnpm turbo run test`                | `14 successful, 14 total`                |
| `apps/live` count           | `pnpm --filter live test`            | `Tests 32 passed (32)`                   |
| `codemods` count            | `pnpm --filter @plane/codemods test` | `Tests 33 passed (33)`                   |
| The run was not a cache hit | Read the Turbo summary line          | `Cached: 0 cached` after a source change |

## Rollback

No rollback. Both suites read source files and write nothing outside `coverage/` when you pass `--coverage`.

To discard a coverage report:

```bash
rm -rf apps/live/coverage
```

## Troubleshooting

| Failure                                              | Cause                                                          | Fix                                                     |
| ---------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------- |
| `Cannot find module '@plane/...'`                    | The workspace packages are not built                           | Run `pnpm build`                                        |
| `EEXIST ... packages/propel/dist`                    | A `pnpm dev` in another terminal is writing the same directory | Stop `pnpm dev`, run `pnpm build`, then start again     |
| Turbo reports success without running a test         | The result was cached                                          | Change a source file, or pass `--force`                 |
| A new test file never runs                           | It sits outside `tests/`, so `include` misses it               | Move it under `apps/live/tests/`                        |
| `turbo run test` reports 14 tasks and you expected 2 | 12 of them are the `^build` dependencies                       | Nothing to fix. Only 2 workspaces have a `test` script. |

## Related

| Page                                                                 | Why it matters here                                            |
| -------------------------------------------------------------------- | -------------------------------------------------------------- |
| [`run-backend-tests-sop.md`](./run-backend-tests-sop.md)             | The Python suite, which is 516 tests in Docker                 |
| [`local-development-setup-sop.md`](./local-development-setup-sop.md) | How to exercise collaboration in a browser, which no test does |
