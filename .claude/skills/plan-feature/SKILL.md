---
name: plan-feature
description: Use at the start of any feature request, behavior change, or defect that needs a spec, when the user says "plan this" or hands over a work item. Produces a spec under docs/features/ as the first pull request, plus a slice DAG. Do not use for a one-line fix, and do not use once the spec and its slices exist.
argument-hint: "{feature request or work item ID}"
user_invocable: true
---

# Plan a feature

Turn a request into a reviewable spec and an ordered list of slices, each grounded in real file paths. The spec ships as the first pull request, before any code. Every later slice PR stacks on it.

## Process

### 1. Research the codebase first

Research is not optional. A spec written before the research restates the request.

1. Orient with `graphify query "{question}"`.
2. If the answer needs several searches, delegate to the `plane-explorer` subagent. It returns paths and a summary, and it keeps the exploration out of this context.
3. Name the closest existing precedent, with its real file path. A spec that names no precedent is not finished. A shape that matches a precedent is cheaper to build and cheaper to review than an invented one.

### 2. Ask at most five questions

Ask only what changes the plan. Prefer the `AskUserQuestion` tool, so the choices are explicit. Stop at five, and state the assumption you make for everything left unasked.

Questions that usually change the plan:

- Which entity owns this, and is it workspace-scoped or project-scoped?
- Does the external API at `apps/api/plane/api/` need it too, or only the web client?
- Which role can do it: guest, member, or admin only?
- What does the user see when it fails?

### 3. Pick the spec folder

Read `docs/features/AGENTS.md` and use its decision table. It routes to `docs/features/new/`, `docs/features/changes/`, or `docs/features/bugfixes/`.

Then read that sub-folder's `AGENTS.md` and `TEMPLATE.md`. The template is the section list. Follow the naming rule: `{WORK-ITEM-ID}-{slug}.md`, or `{slug}.md` when no work item exists.

### 4. Write the spec

Fill every section of the template. Set the status to `Draft`. Update the sub-folder `INDEX.md` in the same commit.

Two rules decide whether the spec is usable.

- Write each test-plan item as a test name or a command that exits 0. Prose is not a proof.
- Use the vocabulary in `CONTEXT.md`. Give the product name first and the code name once in parentheses, as in "a work item (`Issue`)".

### 5. Sketch the screen, when it earns one

Some features are hard to judge as prose. Read [`MOCKUP.md`](./MOCKUP.md), apply its gate, and build one static HTML mockup beside the spec when the gate says yes.

Most features fail the gate. A data model change, an API field, a copy edit, and one obvious input on an existing form all skip it. Record the decision in the spec either way, because a skip that is never written down cannot be told apart from a step that was missed.

Do this before the slices. The states that a mockup forces you to draw are the states that the test plan has to cover.

### 6. Cut the work into slices

Add a `## Slices` section to the spec. Order the DAG along this spine:

1. Data model changes.
2. Backend service and API changes.
3. Frontend changes.

Some work does not fit the spine, for example a docs-only slice or a pure-function refactor. Place it by judgment and state the reason in the slice row.

Every slice names four things.

| Field      | Rule                                                   |
| ---------- | ------------------------------------------------------ |
| Files      | Real paths. A slice that names no file is not a slice. |
| Depends on | Another slice, or nothing.                             |
| Proof      | The test that turns red, then green.                   |
| Seam       | See `.claude/skills/develop-slice/SEAMS.md`.           |

Dependent slices run in sequence, each stacked on the one below. Independent slices can run in parallel worktrees, one `plane-env-create` environment each.

### 7. Ship the spec as the first pull request

Use the `create-pull-request` skill. It creates the branch, writes the PR body, and records the stack base. Do not call `gh pr create` directly.

The spec PR is the deliverable of this skill. It is the only artifact the reviewer has while the first slice is still in progress, and every slice PR stacks on it. When review accepts the spec, set the status to `Agreed`.

## Done when

- [ ] The precedent feature is named, with a file path that exists
- [ ] The spec sits in the sub-folder that the decision table in `docs/features/AGENTS.md` selects
- [ ] Every template section is filled, and the status is `Draft`
- [ ] Every test-plan item is a test name or a command, with no prose items
- [ ] The spec records the mockup path, or records why the feature does not need one
- [ ] Every slice names its files, its dependency, its proof, and its seam
- [ ] The sub-folder `INDEX.md` lists the new page
- [ ] The spec PR is open, through the `create-pull-request` skill
- [ ] Every domain word in the spec appears in `CONTEXT.md`, or the spec adds it there

## Next

1. Review approves the spec. Set `Status` to `Agreed`.
2. Run `/land-slice {spec-pr}`. It merges the spec and pulls `dev`.
3. Run `/develop-slice 1`.

Land the spec before slice 1 starts. A slice that stacks on an unmerged spec branch runs two of the eleven checks, and it has to be rebased again every time the spec changes in review.

## Why

A session fails in the plan, not in the typing. Ten minutes of planning that produces only chat produces nothing a reviewer can read, disagree with, or approve. As a pull request, the spec is reviewable while the code is still in progress, and it becomes the base every slice is measured against.

Five questions is a limit, not a target. An interrogation that runs long is its own failure.
