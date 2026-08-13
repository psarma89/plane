# Infrastructure Docs Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. This file adds the rules that apply to `docs/devops/infra/`.

An infra page describes **one deployment target**: what it contains, how the parts connect, and what it needs to start.

## One page per target

- Files use `NN-<slug>.md`, zero-padded from `01`.
- One page covers one target under `deployments/`, or the root Compose stack.
- A new page takes the next free number. Do not renumber an existing page.
- Sections use `## N.1` and `## N.2`, and match the page number.

## Targets in this repo

Name the real path. Do not invent a target.

| Target | Source |
| --- | --- |
| Local development stack | `docker-compose-local.yml` |
| Local test stack | `docker-compose-test.yml` |
| Single-node Compose | `docker-compose.yml` |
| All-in-one image | `deployments/aio/` |
| Docker Swarm | `deployments/swarm/` |
| Kubernetes with Helm | `deployments/kubernetes/` |
| Prime CLI | `deployments/cli/` |

## Required sections

Follow [`TEMPLATE.md`](./TEMPLATE.md). Every page needs these sections.

| Section | Content |
| --- | --- |
| Header block | Source path and `Last reviewed` stamp |
| When to use | Two sentences on the case this target serves |
| Components | Table of each service, its image and pin, its port, and its role |
| Volumes and state | Table of each persistent volume and what it holds |
| Network and ingress | How traffic enters and which service terminates it |
| Required configuration | Table of variable names, never values |
| Resource floor | The minimum CPU, memory, and disk that starts the target |
| Verification | The command that proves the target came up |

## Pin every version

- Copy each image tag from the source file, character for character.
- Cite the source file next to the table.
- Never write `latest` unless the source file writes `latest`. Then say that the pin is floating.
- If a pin changes, update every page that names it in the same pull request.

## Components table

Every service in the source file needs one row. A missing row makes the page wrong, not brief.

Use the service name exactly as the source file writes it. Example: `plane-db`, not `postgres`.

## Never write a secret

- Name every environment variable. Never write a value.
- Write `<redacted>` where a value belongs.
- Never write a production hostname, an internal IP address, or a bucket name.
- Point to `.env.example` and `apps/api/.env.example` as the canonical list.

## Resource floor

State a number, not a feeling.

- Good: "2 vCPU, 4 GB memory, 10 GB disk. The stack fails to start below 2 GB memory."
- Bad: "Needs a reasonably sized machine."

If the floor is untested, write `untested`. Do not guess.

## Editions

Some components exist in commercial editions only. Mark them.

Use an **Availability** column with the value `Community`, `Commercial`, or `Both`.

## Cross-links

- Link to [`../../architecture/c4/`](../../architecture/c4/INDEX.md) for the container diagram.
- Link to [`../../sops/`](../../sops/INDEX.md) for every install, upgrade, and backup procedure.
- Link to [`../cicd/`](../cicd/INDEX.md) for the pipeline that builds the images.
