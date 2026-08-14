---
name: create-pull-request
description: Use when opening a pull request for the current branch, including a slice in a stack. Gathers branch context, bases the pull request on the branch below it rather than on the trunk, writes the body from the repo template, and prefixes the title with a Plane work item ID when one exists.
user_invocable: true
---

# Create a pull request

## The trunk is `dev`

This fork opens every pull request against `dev`. Upstream uses `preview`, so a
default copied from upstream targets the wrong branch and shows hundreds of
unrelated commits.

Override the base only for a stacked slice, where the base is the branch below it.

## Stacking, when the branch is a slice

A stacked pull request is based on the slice below it, not on the trunk. Without
that, `gh pr create` bases on `dev` and the reviewer sees every earlier slice's
diff inside this one. On the third slice of a stack that is the difference between
a 40-line review and a 400-line review.

Record the parent when the branch is created, so it does not have to be guessed
later.

```bash
git config "branch.$(git branch --show-current).stackparent" "<parent-branch>"
```

Read it back when the pull request is opened.

```bash
PARENT=$(git config --get "branch.$(git branch --show-current).stackparent" || true)
[ -n "$PARENT" ] || PARENT=$(gh pr view "$(git branch --show-current)" --json baseRefName -q .baseRefName 2>/dev/null || true)
[ -n "$PARENT" ] || PARENT=dev
```

The fallback order matters. Git config is authoritative and costs no network. An
open pull request is the next best record, for a stack that someone opened by
hand. `dev` is last, because assuming the trunk silently is exactly the failure
this section exists to prevent.

Print the chain before opening anything, and confirm that each branch has a
recorded parent. A branch with no parent is a branch about to be based on the
trunk by accident.

## Workflow

1. **Resolve the base.** Use the stack parent when one exists. Otherwise `dev`.

2. **Gather context**, in parallel:
   - `git status -s`, to catch uncommitted work
   - `git diff <base>...HEAD --stat`, for the files changed
   - `git log <base>...HEAD --oneline`, for every commit on the branch
   - `git diff <base>...HEAD --no-color`, for the full diff
   - `git rev-parse --abbrev-ref --symbolic-full-name @{u}`, to check for an upstream
   - Read `.github/PULL_REQUEST_TEMPLATE.md`

   Use the three-dot form. `git diff <base>..HEAD` includes commits that landed on
   the base after this branch left it, which inflates the diff with other
   people's work.

3. **Resolve the work item ID.** Extract it from the branch name, for example
   `fix/silo-1146-relative-config-urls` gives `SILO-1146`. If the branch carries
   none, omit the prefix. Do not invent one.

4. **Draft the pull request.**

   Title: `[WORK-ITEM-ID] <type>: <concise summary>`, under 70 characters. Drop
   the bracketed prefix when there is no work item. The type matches the eventual
   commit type: `fix`, `feat`, `chore`, `refactor`, `docs`, `perf`.

   Body: fill every section of the template from the actual diff.

   | Section               | What goes in it                                                                                                                                               |
   | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
   | Description           | What the change does and why. Lead with the defect or the need, not the file list. The diff is readable.                                                      |
   | Type of Change        | Check every box that applies.                                                                                                                                 |
   | Screenshots and Media | Real evidence. For a backend or tooling change, paste the command and its output. A dry run that proves a destructive behavior is stronger than a screenshot. |
   | Test Scenarios        | A table of check, command, and result. Every row must be a command someone can rerun.                                                                         |
   | References            | Related pull requests, the work item, and any finding deferred out of this pull request, with the reason.                                                     |

   When the pull request is stacked, open the body with a line naming the pull
   request below it and stating that this diff is measured against that branch.

5. **Run the body through `/simple-english`** before you post it. The repo writes
   every artifact in Simplified Technical English, and a pull request body is an
   artifact. That pass removes the contractions, the semicolons, the `should`,
   and the `-ing` clause joins.

6. **Push and create.** Push with `-u` when there is no upstream. Create with
   `gh pr create --base "$PARENT" --head "$BRANCH"`, passing the body through a
   heredoc.

7. **Return the pull request URL.**

## Commit with the git CLI

Create commits with `git add` and `git commit`. Do not create them through the
GitHub API, the Contents API, `gh api`, or an MCP file-write tool. Those commits
are unsigned and a repository with required signatures rejects them.

## Done when

- [ ] The base is the stack parent, or `dev`, and never `preview`
- [ ] `git diff <base>...HEAD --stat` shows this slice only, and no earlier slice
- [ ] Every template section is filled from the real diff
- [ ] Every Test Scenarios row names a command that can be rerun
- [ ] The body passed `/simple-english`
- [ ] A stacked pull request names the one below it in its first line
- [ ] Any deferred finding is recorded in References, with its reason

## Common mistakes

- Basing on `preview`, which is upstream's trunk and not this fork's.
- Summarising only the newest commit instead of every commit on the branch.
- Using `..` instead of `...` in the diff range.
- Wrapping the body in a code fence when passing it to `gh pr create`.
- Inventing test scenarios that the diff does not support.
- Opening a stacked pull request before the one below it exists, which makes the
  base branch unresolvable.
