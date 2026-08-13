# SOP Conventions

An SOP is a **procedure**. A reader follows it step by step and reaches a known end state. An SOP does not explain design. Design lives in [`../architecture/`](../architecture/INDEX.md).

## Naming

- Files use `<slug>-sop.md`. Example: `database-backup-sop.md`.
- Do not number SOP files. A runbook set has no reading order.
- The slug names the task, not the system. Use `rotate-api-keys-sop.md`, not `api-keys-sop.md`.
- Use a verb in the slug where the task is an action.

## An SOP is not an architecture page

| Content | Folder |
| --- | --- |
| "Run these nine steps to restore a backup." | `sops/` |
| "The backup job writes to object storage every night." | [`../devops/infra/`](../devops/infra/INDEX.md) |
| "Celery retries a failed task three times." | [`../architecture/c4/containers/`](../architecture/c4/containers/INDEX.md) |

If a page has no numbered steps, it is not an SOP. Move it.

## Writing a step

- One action per step. Use the imperative. Use 20 words or fewer.
- Put the condition before the command: "If the container is running, stop it."
- Put the command in a fenced block. Never wrap a command across lines without a continuation.
- After a step that changes state, state the expected result.
- Never write "repeat as needed". Give the exact count or the exit condition.

Good: `3. Run `docker compose down`. Every container stops.`

Bad: `3. Bring the stack down and make sure everything is stopped properly.`

## Warnings

Put the command or the condition first. Put the risk second.

Good: "Do not run this against production. The command drops every row in the table."

Bad: "Be careful, this is dangerous, because it may drop rows."

Mark a destructive step with a `> **Destructive:**` blockquote directly above it.

## Risk level

Set a risk level in the header block. Use exactly one of three values.

| Level | Meaning |
| --- | --- |
| `Low` | Read-only, or fully reversible with no data loss |
| `Medium` | Changes state. A rollback exists and is tested. |
| `High` | Can lose data or cause an outage. Needs a second person. |

A `High` SOP must state who approves the run.

## Rollback is mandatory

The section is required. If no rollback exists, write why, and state the recovery path instead.

- Good: "No rollback. A completed migration is forward-only. Restore from the last backup with `database-restore-sop.md`."
- Bad: "N/A".

## Credentials in a step

Where a step needs a credential, name the retrieval method, not the credential.

## Staleness

- Update the `Last reviewed` stamp every time you edit a step.
- An SOP with a stamp older than 6 months needs a re-read before use. State that in the header.
- If a command changed, fix the command. Do not add a note beside a wrong command.
