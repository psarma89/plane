# Run Static Checks SOP

> **Last reviewed:** 2026-08-14
> **Owner role:** Contributor
> **Risk:** Low

## Purpose

Run the lint, format, and type checks that this repository enforces, and know which of them CI actually runs.

## When to use

- **Trigger**: A contributor is about to push, and wants the same verdict CI will give.
- **Do not use this SOP when**: You want to run tests. Read [`run-backend-tests-sop.md`](./run-backend-tests-sop.md) or [`run-javascript-tests-sop.md`](./run-javascript-tests-sop.md).

## The tools

`oxlint` lints and `oxfmt` formats. There is no ESLint and no Prettier in any `package.json`.

The `.prettierignore` files at the repository root and under `apps/` are dead. Nothing reads them. To exclude a path from lint, use `ignorePatterns` in `.oxlintrc.json`.

## Procedure

1. Run every JavaScript check.

   ```bash
   pnpm check
   ```

   Expected result: `Failed: @plane/i18n#check:format`, exit code 1. See "Known failures" below. This is the current state of the repository, not a fault in your branch.

2. Run the three checks separately when step 1 fails, so you can tell your failure from the known one.

   ```bash
   pnpm check:lint
   pnpm check:format
   pnpm check:types
   ```

   Expected result: `check:lint` and `check:types` pass. `check:format` fails on one generated file.

3. Fix what is fixable.

   ```bash
   pnpm fix
   ```

   Expected result: `oxfmt` rewrites formatting, then `oxlint --fix` applies safe lint fixes.

4. Run the Python checks in the API container.

   ```bash
   docker compose -f docker-compose-local.yml exec -T api ruff check /code
   docker compose -f docker-compose-local.yml exec -T api ruff format --check /code
   ```

   Expected result: `All checks passed!` and `43 files would be reformatted, 478 files already formatted`. Both are the current state of `dev`.

## Scoping to one workspace

Always go through Turbo. `check:types` declares `dependsOn: ["^build"]`, so a bare `tsc --noEmit` fails on missing `dist/*.d.ts` from `@plane/*` imports.

```bash
pnpm turbo run check:lint --filter=@plane/ui
pnpm turbo run check:types --filter=web
```

Apps use bare names (`web`, `admin`, `space`, `live`). Packages use the scope (`@plane/ui`).

## Known failures on `dev`

Two checks are red before you change anything. Do not attribute either one to your branch, and do not "fix" the first one.

| Check                          | State                                                | Why                                                                                                                                                                     |
| ------------------------------ | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `pnpm check:format`            | Fails on `packages/i18n/src/types/keys.generated.ts` | The build generates that file and `.gitignore` line 118 ignores it. `oxfmt` checks it anyway. Running `pnpm fix:format` rewrites a file that the next build overwrites. |
| `ruff format --check apps/api` | 43 of 521 files would be reformatted                 | No workflow runs `ruff format`. Nothing enforces Python formatting.                                                                                                     |

`ruff check apps/api` was the third red check until 2026-08-14. It reported 3 fixable errors, and CI ran `ruff check --fix`, which repaired them inside the runner and exited 0. Commit `0bc4335` fixed the 3 violations, dropped `--fix` from the workflow, and selected 15 rule families in `apps/api/pyproject.toml`. The check now reports `All checks passed!` and it blocks a new violation.

## What CI runs, and what it does not

| Check                                                         | Workflow                               | Runs on a normal PR              |
| ------------------------------------------------------------- | -------------------------------------- | -------------------------------- |
| `check:format`, `check:lint`, `check:types`, `Build packages` | `pull-request-build-lint-web-apps.yml` | Yes                              |
| `ruff check --output-format=github`                           | `pull-request-build-lint-api.yml`      | Yes, and it fails on a violation |
| `ruff format`                                                 | None                                   | **No**                           |
| Any test suite                                                | None                                   | **No**                           |
| CodeQL, copyright, react-doctor, i18n sync                    | Their own workflows                    | Yes                              |

Three of the four jobs in `pull-request-build-lint-web-apps.yml` carry this gate:

```yaml
if: |
  github.event.pull_request.draft == false &&
  github.event.pull_request.requested_reviewers != null
```

Only the first clause has any effect. An empty reviewer list is not `null`, so a PR with no reviewer still runs every job. A **draft** PR skips them all, and the PR then shows no failures because nothing ran.

The fourth job, `check:types`, carries no gate of its own. It declares `needs: build`, so it is skipped whenever `Build packages` is skipped.

### Marking a draft ready re-runs the checks

```bash
gh pr ready <number>
```

Expected result: a new run starts within a few seconds, and the four jobs report a real conclusion instead of `skipped`.

This works because `pull-request-build-lint-web-apps.yml` answers `ready_for_review`:

```yaml
types:
  - "opened"
  - "synchronize"
  - "ready_for_review"
  - "reopened"
```

That line was missing until 2026-08-14. Without it, `gh pr ready` cleared the draft flag but fired no event the workflow answered, so all four jobs kept the `skipped` result from the draft run and nothing re-evaluated the gate. `pull-request-build-lint-api.yml` and `i18n-sync-check.yml` already listed it, so only the web-app checks behaved this way.

If you meet a pull request whose checks still read `skipped`, close it and reopen it. That fires `reopened`, which every version of the workflow answers.

```bash
gh pr close <number>
gh pr reopen <number>
```

A push fires `synchronize` and works too, but it needs a commit. The close-and-reopen pair needs none.

> **Destructive:** Do not merge a pull request whose checks read `skipped`. A skipped job is not a passing job. Read the latest run for each check name before you merge.

CI passes `TURBO_SCM_BASE`, so it checks only the affected packages. `pnpm check` locally checks everything. That is why the `i18n` failure never appears in CI.

## The other checks

| Check                      | Command                                                 |
| -------------------------- | ------------------------------------------------------- |
| Storybook, `@plane/ui`     | `pnpm --filter=@plane/ui storybook`                     |
| Storybook, `@plane/propel` | `pnpm --filter=@plane/propel storybook -p 6007`         |
| React patterns             | `npx react-doctor@latest --verbose --diff`              |
| Translation key drift      | `pnpm dlx tsx packages/i18n/scripts/sync-check.ts --ci` |

> **Destructive:** Do not run `addlicense` across the whole repository. `COPYRIGHT_CHECK.md` line 26 records that a monorepo-wide TypeScript run crashes OS processes. Scope it to one directory.

## Lint ceilings

Each workspace pins an exact warning count. The check fails at ceiling plus one, so any new warning fails the build.

| Workspace          | Ceiling | Workspace             | Ceiling |
| ------------------ | ------- | --------------------- | ------- |
| `web`              | 11957   | `@plane/ui`           | 66      |
| `@plane/propel`    | 3605    | `@plane/utils`        | 38      |
| `admin`            | 759     | `@plane/i18n`         | 9       |
| `space`            | 676     | `@plane/services`     | 6       |
| `@plane/editor`    | 416     | `@plane/hooks`        | 4       |
| `live`             | 119     | `@plane/decorators`   | 3       |
| `@plane/constants` | 2       | `@plane/types`        | 1       |
| `@plane/logger`    | 0       | `@plane/shared-state` | 0       |

Fix the warning. Do not raise a ceiling. Lower a ceiling when you remove warnings.

## Verification

| Check                             | Command                            | Expected                                      |
| --------------------------------- | ---------------------------------- | --------------------------------------------- |
| Lint is clean                     | `pnpm check:lint`                  | Exit 0                                        |
| Types are clean                   | `pnpm check:types`                 | Exit 0                                        |
| Format has only the known failure | `pnpm check:format`                | Fails on `keys.generated.ts` and nothing else |
| Python lint is clean              | `... exec -T api ruff check /code` | `All checks passed!`                          |

## Rollback

No rollback for a check. Every command in the Procedure except step 3 is read-only.

To undo step 3:

```bash
git checkout -- .
```

## Troubleshooting

| Failure                                                        | Cause                                                                                                                      | Fix                                                      |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| `tsc --noEmit` cannot find `@plane/*` types                    | You ran `tsc` directly and skipped the `^build` dependency                                                                 | Use `pnpm turbo run check:types --filter=<name>`         |
| `check:lint` fails right after you add one warning             | That workspace sits at its exact ceiling                                                                                   | Fix the warning                                          |
| A second Storybook will not start                              | `@plane/ui` and `@plane/propel` both run `storybook dev -p 6006`                                                           | Pass `-p 6007` to the second. Do not put `--` before it. |
| `too many arguments for 'dev'. Expected 0 arguments but got 2` | You wrote `pnpm --filter=<name> storybook -- -p 6007`. The `--` makes pnpm forward `-p` and `6007` as positional arguments | Drop the `--`: `pnpm --filter=<name> storybook -p 6007`  |
| A path in `.prettierignore` is still checked                   | Nothing reads those files                                                                                                  | Use `ignorePatterns` in `.oxlintrc.json`                 |
| `pnpm turbo run check:sync` says the task does not exist       | `check:sync` is a script in `packages/i18n`, not a Turbo task                                                              | Run the `pnpm dlx tsx` form above                        |
| A PR shows no check results at all                             | The PR is a draft, so the `if` gate is false                                                                               | `gh pr ready <number>`                                   |
| The checks still read `skipped` after you marked the PR ready  | The run predates the `ready_for_review` trigger, added 2026-08-14                                                           | Close the PR and reopen it, which fires `reopened`       |
| `gh stack merge` refuses a PR                                  | `gh stack submit` creates a draft by default                                                                               | `gh pr ready`, then close and reopen to run the checks   |
| A red X sits beside a green check on one commit                | `concurrency.cancel-in-progress` cancelled the older run                                                                    | Read the latest run for each check name. Cancelled is not failed. |

## Related

| Page                                                           | Why it matters here                           |
| -------------------------------------------------------------- | --------------------------------------------- |
| [`run-backend-tests-sop.md`](./run-backend-tests-sop.md)       | The Python tests, which no workflow runs      |
| [`run-javascript-tests-sop.md`](./run-javascript-tests-sop.md) | The two Vitest suites, which no workflow runs |
