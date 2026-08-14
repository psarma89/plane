---
name: land-slice
description: Use once a pull request is approved and its checks are green, to merge it and remove everything it created. Retargets a stacked base to dev, rebases, squash merges, then removes the container stack, the worktree, and the local and remote branches. Also lands a spec pull request. Do not use on an unapproved pull request, and do not use to merge a stack out of order.
argument-hint: "{pr number}"
user_invocable: true
---

# Land a slice

Merge one pull request and leave nothing behind.

Run it once per pull request, from the bottom of the stack up. The bottom is the spec. Then slice 1, then slice 2.

## Before you touch anything

Record every branch tip in the stack. A merged branch is deleted, and step 2 needs the tip that the branch had before the merge.

```bash
gh pr list --json number,headRefName,baseRefName \
  --jq '.[] | "#\(.number) \(.headRefName) <- \(.baseRefName)"'
git rev-parse origin/<branch>          # once per branch. Keep the output.
```

## Process

### 1. Retarget a stacked pull request to `dev`

A pull request based on another feature branch runs two checks. A pull request based on `dev` runs ten or eleven.

Every workflow under `.github/workflows/` filters on `branches: [preview, dev]`, so a stacked base matches no filter and the job never starts. `react-doctor.yml` declares no branch filter, which is why it is the only job that runs. Nothing reports as failed, because nothing ran.

```bash
gh pr checks <pr>            # count them before you trust them
gh pr edit <pr> --base dev
```

Retarget before the merge. A stacked pull request that merges on its own base merges unverified.

### 2. Rebase onto `dev`

The parent landed as one squash commit, so the parent's original commits still sit on this branch with different patch ids. `git rebase origin/dev` replays them, and the diff doubles.

```bash
git -C <worktree> fetch origin
git -C <worktree> rebase --onto origin/dev <old-parent-tip>
git -C <worktree> log --oneline origin/dev..HEAD     # this slice only
```

At the bottom of the stack, where the base is already `dev`, use `git rebase origin/dev`.

### 3. Prove the fresh checks pass

The retarget and the rebase both change what runs, so the green from before the rebase proves nothing. Run the repository guards first. They fail in seconds, where CI takes minutes.

```bash
./bin/check-agents-md
./bin/check-counts
git push --force-with-lease
gh pr checks <pr> --watch
```

Read a rollup with `.conclusion // .state`. A check run carries `conclusion`. A commit status carries `state` and no `conclusion`, so a filter on `conclusion` alone reports every commit status as pending forever, and the merge looks blocked when it is not.

### 4. Squash merge

```bash
gh pr merge <pr> --squash --delete-branch
```

### 5. Tear down

> **Destructive:** the teardown script removes every container and every named volume of this branch's project, including uploads. Seeding does not recreate an uploaded file. Copy anything you need first.

```bash
docker compose ls                    # find this branch's project, if it has one
.claude/skills/plane-env-teardown/scripts/env-teardown.sh
git worktree remove <worktree>       # before the branch, not after
git branch -D <branch>
git push origin --delete <branch>
git fetch --prune origin
git ls-remote --heads origin | grep <slug>    # must print nothing
```

Remove the worktree before the local branch. Git refuses to delete a branch that a worktree has checked out, and `gh pr merge --delete-branch` hits the same refusal.

That refusal costs both branches, not one. `--delete-branch` deletes the local branch first. When that step fails it stops, so it never reaches the remote, and it still exits 0 with only a warning on stderr. The merge looks clean while the branch survives on the local side and on the remote.

`git fetch --prune` does not repair this. Pruning removes a remote-tracking ref whose remote branch is gone, and this remote branch is still there. Verify with `git ls-remote`, which asks the remote, rather than with `git branch -a`, which reads the local cache.

A slice that changed no backend code has no container stack. Read `docker compose ls` rather than assuming either way.

### 6. Return to `dev`

```bash
cd <main checkout> && git checkout dev && git pull
```

## Done when

- [ ] The pull request merged, and its base was `dev`
- [ ] The full check set ran on the rebased head, not the two-check subset
- [ ] `docker compose ls` does not list the branch project
- [ ] `git worktree list` does not list the worktree
- [ ] `git ls-remote --heads origin | grep <slug>` prints nothing
- [ ] `git branch --list '*<slug>*'` prints nothing
- [ ] `dev` is pulled, and its tip is this slice's squash commit

## Next

- Another slice is waiting: run `/develop-slice {next}`. It branches from the `dev` you just pulled, so it starts with this slice already in it.
- That was the last slice: set the spec `Status` to `Shipped`, and record every pull request link in the spec.

## Why

Prefer landing each slice before starting the next one over keeping a tall stack. A stack looks faster and is not. Every pull request in it runs two checks instead of eleven, every parent merge forces a rebase of everything above it, and a defect found at the top unwinds every slice below. Stack only when a slice genuinely cannot wait for the one below it, and accept that you are trading verification for time.

A merge is the cheapest moment to leave debris, because everything still works. The stack that keeps running holds ports and a database. The worktree that stays holds a branch, so the branch cannot be deleted, so the next branch listing is wrong. None of it breaks anything today.
