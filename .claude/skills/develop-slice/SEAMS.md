# Seams and mocking

Read this before you write a test. It is reached by a pointer from `SKILL.md`, not inlined, so it costs nothing on the turns that do not need it.

## The ranked seams

Verified against this checkout on 2026-08-14: `apps/api` has a real pytest suite, and `apps/live` and `packages/codemods` have real Vitest suites. `apps/web`, `apps/admin`, and `apps/space` have no `test` script and no test runner.

| Rank | Seam                                                    | Test looks like                                    | Why here                                                       |
| ---- | ------------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------------------- |
| 1    | DRF view in `apps/api/plane/app/views/`                 | Contract test through the `session_client` fixture | Where tenant scoping lives, and it has no framework safety net |
| 2    | Model, manager, or pure Python in `apps/api/plane/`     | Unit test under `apps/api/plane/tests/unit/`       | Cheap, and the suite runs against a real PostgreSQL            |
| 3    | Pure TypeScript in `apps/live/` or `packages/codemods/` | Vitest, call the function, assert the return       | The only TypeScript with a runner                              |

### The web seam is aspirational

A store action in `apps/web/core/store/` or a service class in `apps/web/core/services/` is the correct seam for frontend behavior. No runner exists: `apps/web` has no `test` script and no vitest config. A slice that needs a web test must first add the runner, and that is its own slice, not a side effect. Until then, prove web behavior at the API contract, in a pure function you extract to `@plane/utils`, or by hand in the browser.

## What you can mock

| Layer                                                 | Can mock? | Why                                                                                                                       |
| ----------------------------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------- |
| An external service the API calls, such as S3 or SMTP | Yes       | The test must not depend on the network                                                                                   |
| `Date` and randomness                                 | Yes       | Determinism                                                                                                               |
| The ORM or the database                               | No        | The suite runs a real PostgreSQL in Docker. A mocked queryset hides the scoping defects the contract tests exist to catch |
| A sibling module's function, to make the test pass    | No        | That is a design finding. The unit under test does too much                                                               |

For the fixtures (`session_client`, `api_key_client`, `workspace`, and the rest) and the Factory Boy factories (`UserFactory`, `WorkspaceFactory`, `ProjectFactory`, and the rest), read `apps/api/plane/tests/TESTING_GUIDE.md`. Do not rebuild by hand what a fixture provides.

## Every new endpoint gets a tenant contract test

`BaseViewSet` applies no workspace filter, so this test covers a defect class the framework does not. The test proves that a member of another workspace receives 404.

The trap, documented in `apps/api/AGENTS.md`: the `workspace` fixture hardcodes `slug="test-workspace"`, so build the second workspace by hand with a unique slug, for example with `WorkspaceFactory`.

Assert the correct refusal code. A scoped `get_queryset()` refuses with 404. A permission class refuses with 403. The table lives in `apps/api/AGENTS.md`.

## The three test anti-patterns

Each has a falsifiable tell, so this is a check, not a taste argument.

| Name                   | Tell                                                                                                 | Fix                                                |
| ---------------------- | ---------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| Tautological           | The assertion recomputes the expected value the same way the code does, so it passes by construction | Assert a literal, or assert the observable outcome |
| Implementation-coupled | It breaks under a refactor when the behavior did not change                                          | Move the assertion to the seam boundary            |
| Store-shape            | It asserts an internal field instead of what the caller or the user gets                             | Assert the derived value the caller reads          |

## A test name states the rule it enforces

Weak: `test_get_queryset_filters`
Strong: `test_member_of_another_workspace_cannot_read_labels`

If you cannot say in one plain sentence what defect the test catches, rewrite the test.
