# {Pipeline Title}

> **Last reviewed:** YYYY-MM-DD
> **Workflow file:** `.github/workflows/{name}.yml`
> **Gate:** Blocking | Advisory | Manual

## Purpose

Two sentences. State what breaks if this pipeline does not run.

## Triggers

| Event | Branch filter | Path filter | Notes |
| --- | --- | --- | --- |
| `pull_request` | `dev` | `apps/api/**` | Skips when no Python file changes |
| `push` | `dev` | - | - |
| `workflow_dispatch` | - | - | Manual run |

## Jobs

| Job | Runs | Gate | Typical duration |
| --- | --- | --- | --- |
| `{job-id}` | `{command}` | Blocking | {n} min |
| `{job-id}` | `{command}` | Advisory | {n} min |

State whether each blocking job is a required check in branch protection. Branch protection is not visible in the workflow file.

## Secrets and permissions

Names only. Never write a value.

| Name | Scope | Used for | Available on a fork |
| --- | --- | --- | --- |
| `{SECRET_NAME}` | Repository | {purpose} | No |

| Permission | Level | Why |
| --- | --- | --- |
| `contents` | read | Checkout |
| `security-events` | write | Upload scan results |

## Failure playbook

Each row must be actionable. If a fix needs more than three steps, write an SOP and link to it.

| Failure | Cause | Fix |
| --- | --- | --- |
| {Job name fails with X} | {Root cause} | {Command or SOP link} |

## Cost and duration

- Typical wall-clock time: {n} min.
- Slowest job: `{job-id}`, because {reason}.
- Cache: {what is cached, and what invalidates it}.

## Related

| Page | Why it matters here |
| --- | --- |
| [{Infra page}](../infra/NN-slug.md) | Where the artifacts deploy |
| [{SOP}](../../sops/{slug}-sop.md) | The procedure this pipeline supports |
