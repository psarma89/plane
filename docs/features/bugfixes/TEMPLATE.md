# Bugfix: <Symptom>

> **Status:** In progress | Shipped
> **Severity:** S1 | S2 | S3 | S4
> **Reported:** YYYY-MM-DD
> **Fixed:** YYYY-MM-DD
> **Work item:** <Plane work item ID and link>
> **Pull request:** <Link>

## Symptom

What a user observed. Use their words where possible. Do not describe the cause here.

## Blast radius

| Question | Answer |
| --- | --- |
| Who was affected | <Role, workspace type, or deployment> |
| How many | <Count or estimate, with the basis for the estimate> |
| How long | <First occurrence to fix, in dates> |
| Data corrupted | yes / no |
| Deployments affected | Cloud / Self-hosted / Both |

## Reproduction

The exact steps. A reader must be able to trigger the defect.

1. <Step>.
2. <Step>.
3. Observed: <What happens>.
4. Expected: <What must happen>.

**Environment**: <Version, browser, or deployment target where it reproduces>.

## Root cause

One cause, named in code.

`<path/to/file>` (`<symbol>`) <what it does wrong>.

<Two or three sentences on why that produces the symptom.>

## Fix

| Path | Change |
| --- | --- |
| `<path>` | <What changed> |

<One or two sentences on why this change resolves the cause, not the symptom.>

## Regression test

| Test | Path | Proves |
| --- | --- | --- |
| `<test name>` | `<path>` | <The rule it enforces> |

The test must fail before the fix and pass after. If no automated test is possible, state the reason and give the manual check.

## Rejected hypotheses

The highest-value section. Save the next reader the search you already did.

| Suspected cause | Ruled out because |
| --- | --- |
| <Hypothesis> | <Evidence> |
| <Hypothesis> | <Evidence> |

## Data repair

Delete this section if no data was corrupted.

> **Destructive:** State the guard. Never record a query that runs without a `WHERE` clause.

- **Affected rows**: <count>
- **Repair**: <Query or script, with the guard>
- **Repeatable procedure**: [<SOP name>](../../sops/<slug>-sop.md) or `not repeatable`

## Follow-up

What this class of defect can still cause elsewhere.

| Risk | Where | Action |
| --- | --- | --- |
| <Same pattern> | `<path>` | <Work item link or `accepted`> |

## Related

| Page | Why it matters here |
| --- | --- |
| [<Architecture page>](../../architecture/application/NN-slug.md) | The journey this defect broke |
| [<Change spec>](../changes/<slug>-YYYY-MM-DD.md) | The behavior change the fix required |
