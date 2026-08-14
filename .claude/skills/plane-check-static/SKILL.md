---
name: plane-check-static
description: Run the lint, format, and type checks before pushing, and tell a real failure from one of the two that are already red on dev. Use when you finished a change and want the verdict CI will give, when check:format fails and you need to know whether it is your fault, or when someone asks what CI actually enforces.
user_invocable: true
---

# Run the static checks

`oxlint` lints, `oxfmt` formats. No ESLint, no Prettier. The `.prettierignore`
files in this repository are dead, and nothing reads them.

## Run them

```bash
pnpm check         # lint, format, and types together
pnpm check:lint
pnpm check:format
pnpm check:types
pnpm fix           # rewrite formatting, then apply safe lint fixes
```

Python, in the API container:

```bash
docker compose -f docker-compose-local.yml exec -T api ruff check /code
docker compose -f docker-compose-local.yml exec -T api ruff format --check /code
```

## Two checks are already red on dev

Check these before you blame your branch.

| Check                 | Current state                                        | Why                                                                                                                                    |
| --------------------- | ---------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `check:format`        | Fails on `packages/i18n/src/types/keys.generated.ts` | The build generates it and `.gitignore:118` ignores it. `oxfmt` checks it anyway. Do not "fix" it: the next build overwrites your fix. |
| `ruff format --check` | 43 of 521 files                                      | No workflow runs `ruff format`. Python formatting is unenforced.                                                                       |

`ruff check` reports `All checks passed!` since commit `0bc4335` on 2026-08-14.
That commit fixed the 3 violations, dropped `--fix` from the workflow, and
selected 15 rule families in `apps/api/pyproject.toml`.

So `pnpm check` exits 1 on a clean checkout. That is expected. Compare the
failing task name against this table before reporting a problem.

## Scope to one workspace

Always through Turbo. `check:types` has `dependsOn: ["^build"]`, so a bare
`tsc --noEmit` fails on missing `dist/*.d.ts`.

```bash
pnpm turbo run check:lint --filter=@plane/ui
pnpm turbo run check:types --filter=web
```

Apps use bare names (`web`, `admin`, `space`, `live`). Packages use the scope.

## What CI actually enforces

| Check                                              | Runs in CI                       |
| -------------------------------------------------- | -------------------------------- |
| `check:format`, `check:lint`, `check:types`, build | Yes                              |
| `ruff check --output-format=github`                | Yes, and it fails on a violation |
| `ruff format`                                      | No                               |
| Any test suite, Python or JavaScript               | No                               |

CI sets `TURBO_SCM_BASE`, so it checks only affected packages. `pnpm check`
locally checks everything. That gap is why the `i18n` failure never shows in CI.

**A draft PR runs nothing.** Every job is gated on
`github.event.pull_request.draft == false`. The same `if` also tests
`requested_reviewers != null`, but that clause never blocks, because an empty
reviewer list is not null. A draft PR shows no failures because no job ran.

## Lint ceilings

Each workspace pins an exact warning count, so one new warning fails the build.
Highest: `web` 11957, `@plane/propel` 3605, `admin` 759, `space` 676.
Zero-tolerance: `@plane/logger` and `@plane/shared-state`.

Fix the warning. Never raise a ceiling. Lower one when you remove warnings.

## Other checks

```bash
pnpm --filter=@plane/ui storybook              # port 6006
pnpm --filter=@plane/propel storybook -p 6007
npx react-doctor@latest --verbose --diff
pnpm dlx tsx packages/i18n/scripts/sync-check.ts --ci
```

`@plane/ui` and `@plane/propel` both declare `storybook dev -p 6006`, so the
second one needs an explicit port.

Do not run `addlicense` across the whole repository. `COPYRIGHT_CHECK.md` line
26 records that a monorepo-wide TypeScript run crashes OS processes. Scope it to
one directory.

## Related

- `docs/sops/run-static-checks-sop.md` is the same procedure for a human.
- `plane-test-api` and `plane-test-live` run the suites that CI does not.
