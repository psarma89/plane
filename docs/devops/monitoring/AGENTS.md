# Monitoring Docs Conventions

A monitoring page answers one question: **how does an operator learn that this is broken?** It maps a signal to an alert, and the alert to a recovery.

## One page per signal area

One page covers one area: HTTP errors, queue depth, database health, storage, or client errors.

## Every signal needs four facts

A signal row without all four facts is incomplete.

1. **What emits it.** The service and the code path.
2. **Where it lands.** The log stream, the metric store, or the product analytics tool.
3. **What it means when it moves.** The threshold and the direction.
4. **What to do.** The SOP that recovers it.

A signal that nobody watches is not monitoring. Mark it `Unwatched` and say so.

## Known blind spots

An empty list is acceptable. A missing section is not, because silence reads as coverage.

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

## Cross-links

- Link every alert row to an SOP in [`../../sops/`](../../sops/INDEX.md).
- Link every signal area to the [`../../architecture/c4/containers/`](../../architecture/c4/containers/INDEX.md) dynamic page whose failure modes it detects.
