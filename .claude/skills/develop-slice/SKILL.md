---
name: develop-slice
description: Use to implement exactly one slice from an agreed spec in docs/features/, when the user says "build this slice" or "implement slice N". Runs red, green, review, and PR. Do not use before a spec exists, do not use to plan, and do not use for two slices at once.
argument-hint: "{slice name or number}"
user_invocable: true
---

# Develop a slice

Implement one slice, test first, then hand the diff to review. Read the slice row in the spec before anything else. Read [SEAMS.md](./SEAMS.md) before you write the test.

## Process

### 1. Set up the environment

Use the `plane-env-create` skill. It creates the worktree, allocates a port block, and boots an isolated Docker stack for this branch. Use `plane-env-teardown` when the slice merges.

Not every slice needs a stack, and a stack boot costs several minutes.

| The slice changes                                                       | Needs                  |
| ----------------------------------------------------------------------- | ---------------------- |
| Types, docs, or a pure function                                         | A worktree only        |
| A migration, a view, a serializer, or anything a request passes through | A worktree and a stack |

### 2. Agree the seam

State the seam, then check it against the ranked list in [SEAMS.md](./SEAMS.md). If no correct seam exists, write one line that says so, and pick the closest one. Do not lower the assertion to fit a convenient seam. That produces a test that cannot fail.

### 3. Go red

Write the test. Run it. Show the failure.

| Code under                         | Test runner                                             |
| ---------------------------------- | ------------------------------------------------------- |
| `apps/api/`                        | The `plane-test-api` skill                              |
| `apps/live/`, `packages/codemods/` | The `plane-test-live` skill                             |
| `apps/web/`                        | No suite exists. See the note in [SEAMS.md](./SEAMS.md) |

For `apps/api`, always set the test project name first. It must carry the branch,
because a slice runs in its own worktree.

```bash
source .plane-env.sh
export COMPOSE_PROJECT_NAME="$PLANE_TEST_PROJECT_NAME"
```

Two failures make this mandatory, and a fixed name only avoids the first.

Both compose files in this repository resolve to the same project name when the
variable is unset. The test stack then joins the development stack's project, and
a later `docker compose ... --remove-orphans` deletes every container of the
development stack. Never pass `--remove-orphans` in this repository.

A single fixed name gives every checkout one test project, so a second worktree
that starts a test run joins the first run's containers and the two suites share
one database. That defeats running independent slices in parallel, which is the
reason each slice has its own worktree. Never write
`COMPOSE_PROJECT_NAME=plane-api-tests` without a branch suffix.

Sourcing `.plane-env.sh` alone is not enough, and skipping it is not a defence.
That file exports the DEVELOPMENT project name, and Docker Compose auto-loads
`.env` on every invocation anyway. Override the variable in every shell that runs
a test command. The `plane-test-api` skill carries the full commands and the
fallback for a checkout with no `.plane-env.sh`.

A test that passes before the implementation exists measures nothing. If it passes, the seam or the assertion is wrong.

### 4. Go green with the minimum code

Implement only what the test demands. Use the file list from the slice. If the diff grows wider than the slice's file list, the plan was wrong. Say that in the PR and update the spec. Do not widen quietly.

### 5. Review before the PR

Read the diff yourself first. The subagent is the second reader, not the first.

Then route by path:

| Path                         | Reviewer subagent       |
| ---------------------------- | ----------------------- |
| `apps/api/**`                | `plane-django-reviewer` |
| `apps/web/**`, `packages/**` | `plane-web-reviewer`    |

Resolve or explicitly defer every finding. Then invoke the `review-council` skill for the full per-PR review tier.

### 6. Open the PR

One commit per slice. The message names the slice and its proof.

Use the `create-pull-request` skill. It stacks the PR on the branch below it: slice 1 on the spec PR's branch, slice N on slice N-1. Do not call `gh pr create` directly. A PR based on the trunk shows every earlier slice's diff inside this one.

## Done when

- [ ] The test existed and failed before the implementation
- [ ] The test command exits 0
- [ ] If you revert the implementation, the test turns red again
- [ ] Both review passes ran: the path-routed subagent, then `review-council`
- [ ] The files changed match the slice's file list, or the spec records why not
- [ ] One commit, with a message that names the slice
- [ ] The PR is open through `create-pull-request` and diffs against the slice below it only

## Why

The failing test is the demonstration, not the paperwork. A red step before a green step is the only evidence that the test can fail. A test that cannot fail is worse than no test, because it reports a safety that does not exist.

Read the diff by hand before the subagents run. That order keeps the judgment with the engineer, and it makes the agents a second opinion instead of the first.
