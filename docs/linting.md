# Linting in Plane - How It Works

We use [OxLint](https://oxc.rs/docs/guide/usage/linter) for linting across the entire monorepo. OxLint is a single Rust binary that's 50-100x faster than ESLint, with zero Node.js dependencies at runtime.

## Key Points

1. **Single Root Config** - One `.oxlintrc.json` at the repo root handles all packages and apps
2. **No Build Required** - OxLint doesn't need TypeScript build artifacts, so lint runs independently of build
3. **Plugin Coverage** - react, typescript, jsx-a11y, import, promise, unicorn, oxc

## How to Run

From the root of the repo:

```bash
# Check for lint errors
pnpm check:lint

# Auto-fix lint errors
pnpm fix:lint
```

To lint a specific package:

```bash
pnpm turbo run check:lint --filter=@plane/ui
```

## VS Code Integration

Install the [OxLint extension](https://marketplace.visualstudio.com/items?itemName=nicolo-ribaudo.vscode-oxlint) for inline errors/warnings as you type.

## What Gets Linted

The config applies to all TypeScript and JavaScript files across:

- `apps/web`, `apps/admin`, `apps/space`, `apps/live`
- All packages in `packages/`

**Ignored paths:**

- `node_modules/`, `dist/`, `build/`, `.next/`, `.turbo/`
- Config files (`*.config.{js,mjs,cjs,ts}`)
- Public folders, coverage, storybook-static

## Rules Overview

OxLint uses category-based configuration:

| Category        | Level | What It Catches                          |
| --------------- | ----- | ---------------------------------------- |
| **correctness** | warn  | Real bugs that will cause runtime errors |
| **suspicious**  | warn  | Code patterns that are likely mistakes   |
| **perf**        | warn  | Performance anti-patterns                |

Additional rule overrides:

- `react/prop-types` off (TypeScript handles prop validation)
- `no-unused-vars` warns with `_` prefix pattern ignored
- Several noisy unicorn rules disabled

### Warning ceilings

Each package pins a `--max-warnings` ceiling in its own `check:lint` script. That number is what fails CI.

The ceilings are baselines, not targets. Measured on 2026-08-14 with `oxlint` 1.51.0, from each package directory: 1,090 real warnings across the workspace, against a ceiling total of 17,661. Seven packages sit at exactly 0, where one new warning fails the build at once. Six packages hold 99.8 percent of the remaining slack, and `apps/web` holds 67 percent of it alone.

When you remove warnings from a package, lower its ceiling in the same commit. A ceiling that stays above the real count stops guarding the package.

One caution when you edit this page. `oxfmt` reformats the category table above whenever it formats any other change in this file. Read the table rows in your diff before you commit, even when you did not mean to touch them.

## Backward Compatibility

OxLint supports `eslint-disable` comments, so existing inline suppressions continue to work.

## Suppressing Warnings

```typescript
// Single line
// eslint-disable-next-line no-unused-vars
const data = response;

// Block
/* eslint-disable no-unused-vars */
// ... code
/* eslint-enable no-unused-vars */
```

**Please use sparingly** - most warnings indicate real issues that should be fixed.

## Pre-commit Hook

Lint-staged runs automatically on commit via Husky:

- oxfmt formats your staged files
- OxLint fixes what it can (with `--deny-warnings`)

If the commit fails due to lint errors, fix them before committing.

## Architectural boundaries

The `overrides` block holds rules that enforce layering, not style.

| Rule                    | Applies to                                  | What it blocks                                                                                                                    |
| ----------------------- | ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `no-restricted-imports` | `**/core/components/**`, `**/core/hooks/**` | An import of `@/services/*`. A component reads state through a hook in `core/hooks/store/`. Only `core/store/` imports a service. |

The rule is `warn`, not `error`. The pre-commit hook runs `oxlint --fix --deny-warnings` on staged files, so a warning is already a hard block on any file you edit.

### The grandfather list

A second `overrides` entry turns the rule off for 63 files that broke the boundary before the rule existed.

The list is deliberate. Without it, the rule fuses two separate decisions:

1. New code must not import a service. This is the rule.
2. Existing code must be fixed the moment somebody touches it. This is a migration.

All 63 files are live code. 56 of them took 5 or more commits in the last 12 months. Fusing the two decisions therefore taxes anyone who works in `apps/web`, for an import that they did not write.

Treat the list as the burndown backlog. To retire an entry:

1. Move the service call into the matching store slice under `apps/web/core/store/`.
2. Read the result in the component through a hook in `apps/web/core/hooks/store/`.
3. Delete the path from the `overrides` entry in `.oxlintrc.json`.

Do not add a path to the list. A new violation must not land.

[features/changes/service-import-boundary-burndown-2026-08-14.md](./features/changes/service-import-boundary-burndown-2026-08-14.md) holds the batch order, the risk ranking, and the regression plan.

## Reference Files

- [.oxlintrc.json](../.oxlintrc.json) - OxLint configuration
- [package.json](../package.json) - Available scripts
