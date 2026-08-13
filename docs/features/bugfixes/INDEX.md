# Bugfix Records

One page per defect worth remembering. Each page records the symptom, the root cause, the fix, and the hypotheses that were wrong.

## Records

> No record exists yet. Add the first one with [`TEMPLATE.md`](./TEMPLATE.md), then list it here.

Entry format: `- [Title](./<WORK-ITEM-ID>-<slug>.md) - Severity - one-line symptom`

<!-- - [Stale chunk load failure](./WEB-8632-stale-chunk-reload.md) - S2 - Navigation failed after a deploy replaced a chunk. -->

Order this index newest first.

## Severity

[`AGENTS.md`](./AGENTS.md) defines `S1` to `S4`, and the five triggers that decide whether a defect earns a record at all.

## Related

- [../changes/INDEX.md](../changes/INDEX.md) holds the behavior change when a fix alters documented behavior.
- [../../architecture/INDEX.md](../../architecture/INDEX.md) describes the flow the defect broke.
- [../../sops/INDEX.md](../../sops/INDEX.md) holds a data repair procedure when the repair is repeatable.
