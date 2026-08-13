# Bugfix Records

One page per defect worth remembering. Each page records the symptom, the root cause, the fix, and the hypotheses that were wrong.

Read [`AGENTS.md`](./AGENTS.md) before you add a page. Follow [`TEMPLATE.md`](./TEMPLATE.md).

## Records

> No record exists yet. Add the first one with [`TEMPLATE.md`](./TEMPLATE.md), then list it here.

Entry format: `- [Title](./<WORK-ITEM-ID>-<slug>.md) - Severity - one-line symptom`

<!-- - [Stale chunk load failure](./WEB-8632-stale-chunk-reload.md) - S2 - Navigation failed after a deploy replaced a chunk. -->

Order this index newest first.

## Not every bug earns a page

Most defects need only a pull request and a test. Write a record when at least one statement is true.

- The defect reached users.
- The root cause was not the obvious one.
- The defect returned after an earlier fix.
- The fix crosses two or more apps.
- The defect needed a data repair.

## Severity

| Severity | Meaning |
| --- | --- |
| `S1` | Data loss, or the product is unusable for many users |
| `S2` | A core journey is broken. A workaround exists. |
| `S3` | A non-core journey is broken, or the defect is cosmetic and visible |
| `S4` | Cosmetic, or reachable only in an unusual path |

## Related

- [../changes/INDEX.md](../changes/INDEX.md) holds the behavior change when a fix alters documented behavior.
- [../../architecture/INDEX.md](../../architecture/INDEX.md) describes the flow the defect broke.
- [../../sops/INDEX.md](../../sops/INDEX.md) holds a data repair procedure when the repair is repeatable.
