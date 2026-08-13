# DevOps Docs Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. This file adds the rules that apply to `docs/devops/`.

DevOps pages describe **how the code ships, where it runs, and how a problem gets noticed**. They describe the current setup, not a plan.

## This folder is a router

`docs/devops/` holds no pages of its own. It has no `TEMPLATE.md`. Every page lives in one of three sub-folders.

| Sub-folder | Answers |
| --- | --- |
| [`cicd/`](./cicd/INDEX.md) | Which pipeline runs, when, and what it blocks |
| [`monitoring/`](./monitoring/INDEX.md) | Which signal exists, which alert fires, where to look |
| [`infra/`](./infra/INDEX.md) | Which deployment target exists and what it contains |

## Which sub-folder gets the page

| Question | Sub-folder |
| --- | --- |
| Does the subject run in GitHub Actions or gate a merge? | `cicd/` |
| Does the subject tell an operator that something is wrong? | `monitoring/` |
| Does the subject define what runs where, and with which resources? | `infra/` |

## DevOps pages against SOPs

A DevOps page describes the shape. An SOP gives the steps.

| Content | Folder |
| --- | --- |
| "The release pipeline builds these five images and pushes them to this registry." | `devops/cicd/` |
| "To cut a release, do these nine steps in this order." | [`../sops/`](../sops/INDEX.md) |
| "The API emits these log lines at this level." | `devops/monitoring/` |
| "To find the cause of a 502, run these queries." | [`../sops/`](../sops/INDEX.md) |

If a page starts to read as a numbered procedure, move the procedure to an SOP. Link to it.

## Never write a secret

- Name an environment variable. Never write its value.
- Write `<redacted>` where a value belongs.
- Never write a production hostname, an internal IP address, or a bucket name.
- Point to `.env.example`, `apps/api/.env.example`, or the secret store as the canonical source.

## Version and pin accuracy

- Give the exact pinned version when a page names an image or a runtime.
- Copy the version from the source file. Do not copy it from another doc.
- Cite the source file so a reader can confirm the pin. Example: `` `docker-compose.yml` ``.
- If a version changes, update every page that names it in the same pull request.

## Cross-links

- Link an infra page to the matching [`../architecture/c4/`](../architecture/c4/INDEX.md) container diagram.
- Link a monitoring page to the SOP that recovers the failure it detects.
- Link a CI/CD page to the workflow file in `.github/workflows/`.
