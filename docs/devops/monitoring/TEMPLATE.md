# N. {Signal Area Title}

> **Last reviewed:** YYYY-MM-DD
> **Services in scope:** `api`, `worker`, `plane-mq`
> **Availability:** Self-hosted | Cloud | Both

## N.1 What breaks

Two sentences. State what a user sees when this area degrades.

## N.2 Signals

| Signal | Emitted by | Lands in | Threshold | Availability |
| --- | --- | --- | --- | --- |
| {5xx rate} | `apps/api` | {Log stream} | Above 2 percent over 5 minutes | Both |
| {Queue depth} | `plane-mq` | {Metric store or `no destination`} | `no threshold agreed` | Self-hosted |

Give a number and a window for every threshold. If no threshold is agreed, write `no threshold agreed`.

## N.3 Alerts

| Alert | Condition | Notifies | Runbook |
| --- | --- | --- | --- |
| {Alert name} | {Signal crosses threshold} | {Rota or channel} | [{SOP name}](../../sops/{slug}-sop.md) |

Every alert needs a runbook link. An alert with no runbook is a page a responder cannot act on.

## N.4 Dashboards

| View | Answers | Where |
| --- | --- | --- |
| {View name} | {The one question it answers} | {Tool name, no internal URL} |

## N.5 Known blind spots

This section is required. An empty list is acceptable.

- {What nobody watches, and why}
- {A signal that emits but has no alert}

## N.6 Configuration

| Variable | Default | Effect |
| --- | --- | --- |
| `{ENV_VAR}` | `{default}` or `no default` | What changes when you set it |

Never write a secret value. Write `<redacted>`.

## N.7 Verification

How to prove the signal still flows.

- **Command**: The command that produces the signal on purpose.
- **Expected result**: What appears, and where.
- **Cadence**: How often to run this check.

## N.8 Related

| Page | Why it matters here |
| --- | --- |
| [{L2 dynamic page}](../../architecture/c4/l2-containers/NN-slug.md) | The failure modes this area detects |
| [{Infra page}](../infra/NN-slug.md) | The target that emits these signals |
