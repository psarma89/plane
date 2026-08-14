# Change: Service imports - move 63 files behind the store layer

> **Status:** Draft
> **Owner:** Priyam Sarma
> **Date:** 2026-08-14
> **Work item:** None
> **Pull request:** None yet. [#22](https://github.com/psarma89/plane/pull/22) adds the rule and the exemption list that this page retires.

## Why now

`apps/web` layers as `components -> hooks -> store -> services`. Only `apps/web/core/store/` imports a service. A component reads state through a hook in `apps/web/core/hooks/store/`.

63 files break that boundary. PR #22 adds a `no-restricted-imports` rule that stops the 64th, and it exempts the 63 in a second `overrides` entry in `.oxlintrc.json`.

The exemption is the trigger for this page. An exemption list with no owner and no end date is permanent. This page gives the list an owner and an order.

## Current behavior

The behavior of the product does not change. This section describes how data reaches a component today.

- A component in the exempt list constructs a service directly and calls it.
- The response lands in local React state, through `useState` or `useSWR`.
- No MobX store observes that data, so a second component cannot read it.
- Two components that need the same data each make their own request.
- An error path is handled per component, so the handling differs between files.

## New behavior

- A store slice under `apps/web/core/store/` owns the request and the response.
- The component reads the result through a hook in `apps/web/core/hooks/store/`.
- The data is observable, so a second component reads it without a second request.
- The store slice holds one error path for every consumer.
- The path is deleted from the `overrides` entry in `.oxlintrc.json`.

## Backwards compatibility

- **Compatible?** yes

No endpoint changes. No response shape changes. No user-facing string changes. The refactor is internal to `apps/web`.

## Data changes

- **Migration needed?** no.
- **Backfill needed?** no.

## Frontend impact

This page does not repeat the 63 paths. `.oxlintrc.json` holds the authoritative list, and a copy here rots on the first rename.

The table groups the list by area. The commit column counts commits in the 12 months before 2026-08-14, and it ranks the risk. A high count means many people touch that area.

| Area          |  Files | Commits | Services imported                                                       |
| ------------- | -----: | ------: | ----------------------------------------------------------------------- |
| `onboarding`  |      8 |     124 | `auth.service`, `workspace.service`                                     |
| `account`     |      7 |      73 | `auth.service`, `workspace.service`                                     |
| `core`        |      7 |      95 | `ai.service`, `auth.service`, `file.service`, `project`, `user.service` |
| `analytics`   |      5 |      41 | `analytics.service`                                                     |
| `issues`      |      5 |      69 | `ai.service`, `file.service`, `issue`, `project`, `workspace.service`   |
| `inbox`       |      4 |      60 | `file.service`, `inbox`, `project`, `workspace.service`                 |
| `exporter`    |      3 |      41 | `integrations`, `project`, `project/project-export.service`             |
| `integration` |      3 |      32 | `app_installation.service`, `integrations`, `project`                   |
| `profile`     |      3 |      19 | `user.service`                                                          |
| `project`     |      3 |      43 | `file.service`, `project`                                               |
| `settings`    |      3 |      10 | `auth.service`, `user.service`                                          |
| `core/hooks`  |      2 |       9 | `file.service`, `timezone.service`                                      |
| `cycles`      |      2 |      24 | `cycle.service`                                                         |
| `editor`      |      2 |      29 | `workspace.service`                                                     |
| `power-k`     |      2 |      16 | `workspace.service`                                                     |
| `comments`    |      1 |       9 | `file.service`                                                          |
| `home`        |      1 |       9 | `workspace.service`                                                     |
| `pages`       |      1 |       1 | `ai.service`                                                            |
| `workspace`   |      1 |      18 | `workspace.service`                                                     |
| **Total**     | **63** | **722** |                                                                         |

- **States that change**: none. Loading, empty, error, and success stay as they are.
- **New affordance**: none.
- **Background classes**: none. No `bg-*` class changes.

### Stores

Each area maps to a slice on `CoreRootStore` in `apps/web/core/store/root.store.ts`. The store for each file is decided during its own pull request, because some areas need a new slice and some extend one that exists.

Three services need a decision before the work starts. Name the owner in the first pull request that touches each one:

| Service             | Files | Question to answer first                                                                     |
| ------------------- | ----: | -------------------------------------------------------------------------------------------- |
| `workspace.service` |    15 | Does `WorkspaceRootStore` absorb all 15 call sites, or do some belong to a feature slice?    |
| `auth.service`      |    10 | Authentication runs before the store exists. State whether these call sites can move at all. |
| `file.service`      |     8 | Uploads are per component today. State whether one asset slice serves every caller.          |

### Copy changes

No translation key changes. No user-facing string changes.

## Regression plan

### Flows that must not break

`apps/web` has no test files and no `test` script. No automated test covers any flow in the table above.

| Flow                                       | Covering test | Status |
| ------------------------------------------ | ------------- | ------ |
| Sign in, sign up, password reset           | None          | Manual |
| Onboarding, from invite to first workspace | None          | Manual |
| Work item create, edit, and file upload    | None          | Manual |
| Intake triage and duplicate selection      | None          | Manual |
| Analytics charts and export download       | None          | Manual |

This is the largest risk on this page. Manual checks are the only safety net. The decision is recorded in the Rollout section.

### Manual checks for every batch

Run these four steps for every batch, against a local stack.

1. Open the browser console. Make sure that the batch adds no error.
2. Open the browser network tab. Make sure that the batch adds no duplicate request.
3. Reload each screen that the batch touched. Make sure that the data returns.
4. Sign out. Sign in again. Make sure that the screens still load.

### Manual checks per batch

Run the steps for the batch, in addition to the four steps above.

#### Batch 1

1. Open a page. Open the AI menu. Generate text.
2. Open profile settings. Change the password.
3. Open notification settings. Turn an email notification off. Reload. Make sure that the value holds.
4. Add a comment with a file attachment.
5. Open the home screen. Make sure that the Recents widget lists items.
6. Open profile activity. Download the activity export.

#### Batch 2

1. Open the command palette. Search for a work item. Select it.
2. Create a cycle. Open the cycle analytics sidebar.
3. Edit a work item description. Edit a comment.
4. Create a workspace.
5. Change the timezone in settings. Make sure that a date renders in the new timezone.

#### Batch 3

1. Open workspace integrations. Open the GitHub repository list. Open the Slack channel list.
2. Export work items to CSV. Make sure that the export appears under previous exports.
3. Open analytics. Make sure that every chart renders. Make sure that the insight table has rows.
4. Create a project. Edit the project form. Change the project cover image.

#### Batch 4

1. Open Intake. Open an intake item. Make sure that the detail loads.
2. Create an intake item with a description.
3. Mark an intake item as a duplicate.
4. Open a work item. Open the peek view. Set a parent work item.

#### Batch 5

1. Sign in with a password. Sign out. Sign in with a magic code.
2. Reset a forgotten password. Set the new password.
3. Upload a workspace image. Upload a profile image. Change the email address.
4. Delete two work items in bulk. Add an existing work item to a cycle.
5. Register a new user. Complete profile setup. Create a workspace. Invite a member.
6. Accept an invitation from a second account.

## Rollout

- **Feature flag?** no. The refactor is internal, and a flag cannot cover an import change.

### Order

Work from the lowest risk to the highest. The commit count sets the risk.

1. `pages`, `settings`, `comments`, `home`, `profile` (9 files, 48 commits).
2. `power-k`, `cycles`, `editor`, `workspace`, `core/hooks` (9 files, 96 commits).
3. `integration`, `exporter`, `analytics`, `project` (14 files, 157 commits).
4. `inbox`, `issues` (9 files, 129 commits).
5. `account`, `core`, `onboarding` (22 files, 292 commits).

Delete each path from `.oxlintrc.json` in the pull request that fixes it. The exemption list is the progress bar. When the list is empty, delete the whole `overrides` entry and raise the rule to `error`.

### Decision: manual checks, no new test coverage

Decided 2026-08-14 by Priyam Sarma.

The alternative was Playwright coverage for the five flows before batch 1. That option was rejected. The burndown does not wait for a test harness that `apps/web` has never had.

Three consequences follow from this decision. Accept all three, or reopen the decision.

1. The risk stays for the whole burndown. No batch is verified automatically.
2. Every batch needs a person at a browser. Nobody can land a batch unattended.
3. A regression reaches `dev` when a manual step is skipped. The manual steps are the only gate.

Two rules limit the cost:

- Keep each batch to one pull request, so a revert is one commit.
- If a batch grows past its listed file count, split it. A larger batch makes the manual checks unreliable.

### Rollback

Each batch is one pull request. To reverse a batch, revert the commit and restore the deleted paths to the `overrides` entry in `.oxlintrc.json`.

## Related

| Page                                                                                      | Why it matters here                                                  |
| ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| [2. apps/web: component map](../../architecture/c4/l3-components/02-web-component-map.md) | The layering this page restores, and the store the components read   |
| [../../linting.md](../../linting.md)                                                      | The rule, the exemption list, and the three steps to retire an entry |
