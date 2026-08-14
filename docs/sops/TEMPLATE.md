# <Task Title> SOP

> **Last reviewed:** YYYY-MM-DD
> **Owner role:** <Who owns this procedure>
> **Risk:** Low | Medium | High
> **Approval:** <Required for High risk. Name the role, not a person.>

## Purpose

One sentence. State the end state a reader reaches.

## When to use

- **Trigger**: <The event or the alert that starts this procedure>
- **Do not use this SOP when**: <The case where another SOP applies. Link it.>

## Prerequisites

Complete every item before step 1.

| Item | How to confirm |
| --- | --- |
| <Access or role> | <Command or check> |
| <Tool and version> | `<command> --version` |
| <State the system must be in> | <Command or check> |

## Procedure

One action per step. Use the imperative. Give the expected result after a step that changes state.

1. <Action>.

   ```bash
   <command>
   ```

   Expected result: <What appears>.

2. <Action>.

   ```bash
   <command>
   ```

   Expected result: <What appears>.

> **Destructive:** Step 3 deletes data. Confirm the backup from step 2 exists first.

3. <Action>.

   ```bash
   <command>
   ```

   Expected result: <What appears>.

## Verification

Prove the procedure worked. Do not rely on the absence of an error.

| Check | Command | Expected |
| --- | --- | --- |
| <What to confirm> | `<command>` | `<output>` |

## Rollback

This section is required. If no rollback exists, state why and give the recovery path.

1. <Action to undo>.

   ```bash
   <command>
   ```

## Troubleshooting

| Failure | Cause | Fix |
| --- | --- | --- |
| <Error text> | <Root cause> | <Command or SOP link> |

## Related

| Page | Why it matters here |
| --- | --- |
| [<L2 dynamic page>](../architecture/c4/l2-containers/NN-slug.md) | The flow this procedure touches |
| [<Infra page>](../devops/infra/NN-slug.md) | The target this procedure runs against |
| [<Monitoring page>](../devops/monitoring/NN-slug.md) | The alert that triggers this procedure |
