# CI/CD

One page per pipeline. Each page states the trigger, the jobs, the merge gate, and the failure recovery.

## Pages

> No page exists yet. Add the first page with [`TEMPLATE.md`](./TEMPLATE.md), then list it here.

Entry format: `- [Title](./<slug>.md) - one-line summary`

## Workflows to document

Every row maps to a file in `.github/workflows/`. This list is a backlog, not a claim that a page exists. Delete a row when you write the page.

| Workflow file | Covers |
| --- | --- |
| `pull-request-build-lint-api.yml` | Python build and lint gate for `apps/api` |
| `pull-request-build-lint-web-apps.yml` | TypeScript build, lint, and type gate for the web apps |
| `codeql.yml` | CodeQL static analysis |
| `copyright-check.yml` | Copyright header check |
| `i18n-sync-check.yml` | Locale key parity across `packages/i18n` |
| `react-doctor.yml` | React diagnostics sweep |
| `check-version.yml` | Version bump validation |
| `build-branch.yml` | Branch image build and push |
| `feature-deployment.yml` | Preview environment for a feature branch |

## Branch model

| Branch | Role |
| --- | --- |
| `preview` | Upstream default branch |
| `dev` | Integration branch. A pull request targets `dev`. |

## Related

- [../infra/INDEX.md](../infra/INDEX.md) covers where the built images deploy.
- [../monitoring/INDEX.md](../monitoring/INDEX.md) covers the signals after deploy.
- [../../sops/INDEX.md](../../sops/INDEX.md) holds release and rollback procedures.
- [../../../CONTRIBUTING.md](../../../CONTRIBUTING.md) covers the contributor pull request process.
