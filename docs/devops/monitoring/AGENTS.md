# Monitoring Docs Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. This file adds the rules that apply to `docs/devops/monitoring/`.

A monitoring page answers one question: **how does an operator learn that this is broken?** It maps a signal to an alert, and the alert to a recovery.

## One page per signal area

- Files use `NN-<slug>.md`, zero-padded from `01`.
- One page covers one area: HTTP errors, queue depth, database health, storage, or client errors.
- A new page takes the next free number. Do not renumber an existing page.
- Sections use `## N.1` and `## N.2`, and match the page number.

## Every signal needs four facts

A signal row without all four facts is incomplete.

1. **What emits it.** The service and the code path.
2. **Where it lands.** The log stream, the metric store, or the product analytics tool.
3. **What it means when it moves.** The threshold and the direction.
4. **What to do.** The SOP that recovers it.

A signal that nobody watches is not monitoring. Mark it `Unwatched` and say so.

## Required sections

Follow [`TEMPLATE.md`](./TEMPLATE.md). Every page needs these sections.

| Section | Content |
| --- | --- |
| Header block | `Last reviewed` stamp and the services in scope |
| What breaks | Two sentences on the user-visible impact |
| Signals | Table of each signal, its source, its destination, and its threshold |
| Alerts | Table of each alert, its condition, its recipient, and its runbook |
| Dashboards | Table of each view, and the question it answers |
| Known blind spots | Honest list of what nobody watches |
| Verification | How to prove the signal still flows |

## Known blind spots are mandatory

The section is required. An empty list is acceptable. A missing section is not.

List every failure a reader expects to be watched but is not. Give the reason.

- Good: "Queue depth is not alerted. No metric store exists in the community deployment."
- Bad: "Monitoring is limited."

## Self-hosted against cloud

Plane runs as a self-hosted deployment and as a hosted service. The available tooling differs.

- State which deployment each signal exists in.
- Use an **Availability** column with the value `Self-hosted`, `Cloud`, or `Both`.
- Never assume a managed observability tool exists in a self-hosted install.

## Thresholds

- Give a number and a window. Example: "Above 2 percent over 5 minutes."
- Never write "high" or "elevated" without a number.
- If no threshold is agreed, write `no threshold agreed`. Do not invent one.

## Never write a secret

- Name a dashboard. Never paste an internal URL.
- Name an environment variable, for example `POSTHOG_API_KEY`. Never write its value.
- Never write an internal hostname or an IP address.

## Cross-links

- Link every alert row to an SOP in [`../../sops/`](../../sops/INDEX.md).
- Link every signal area to the [`../../architecture/system/`](../../architecture/system/INDEX.md) page whose failure modes it detects.
