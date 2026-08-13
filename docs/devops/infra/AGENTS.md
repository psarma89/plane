# Infrastructure Docs Conventions

An infra page describes **one deployment target**: what it contains, how the parts connect, and what it needs to start.

## One page per target

One page covers one target under `deployments/`, or the root Compose stack.

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

## Pins

[`../../AGENTS.md`](../../AGENTS.md) gives the general pin rule. One addition applies here: never write `latest` unless the source file writes `latest`, and then say that the pin is floating.

## Components table

Every service in the source file needs one row. A missing row makes the page wrong, not brief.

Use the service name exactly as the source file writes it. Example: `plane-db`, not `postgres`.

## Resource floor

State a number, not a feeling.

- Good: "2 vCPU, 4 GB memory, 10 GB disk. The stack fails to start below 2 GB memory."
- Bad: "Needs a reasonably sized machine."

If the floor is untested, write `untested`. Do not guess.

## Editions

Some components exist in commercial editions only. Mark them.

Use an **Availability** column with the value `Community`, `Commercial`, or `Both`.

## Cross-links

Every install, upgrade, and backup procedure lives in [`../../sops/`](../../sops/INDEX.md), never on this page. [`INDEX.md`](./INDEX.md) holds the rest of the navigation.
