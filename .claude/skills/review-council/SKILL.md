---
name: review-council
description: Run the review tier over a diff before it merges. Use after a slice is green and before the pull request is marked ready, when someone asks for a thorough review, or when the diff was written by a model. Two tiers exist, and this skill decides which one runs. Do not use to fix what it finds, and do not use on an empty diff.
user_invocable: true
argument-hint: [pr-number | branch]
---

# Review council

A diff gets more than one reader, and the readers do not share a context. That is
the whole mechanism. An author cannot review their own work, because the reasons
that made a choice feel right are still in the room.

## Read the diff yourself first

```bash
git diff <base>...HEAD
```

Name what you check as you go. For a diff a model wrote, check in this order,
because this is the order model-written code fails.

1. **Contract gaps.** A field added to a serializer, but missing from the type,
   the service, or the store. Trace the whole path once.
2. **Tenant scoping.** A view that does not override `get_queryset()`.
3. **An optimistic update with no rollback.**
4. **An error state swallowed** rather than surfaced to the user.
5. **Architecture drift.** Right behavior, wrong location.

This order is the point. An agent that finds the defect before you do has
demonstrated automation, not judgment.

## Tier 1 runs on every pull request

Every pull request in the stack, including the spec pull request.

| Reader                                          | What it is for                                                                                        |
| ----------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `plane-django-reviewer` or `plane-web-reviewer` | The path-routed convention reader. Route by the paths in the diff. Run both when the diff spans both. |
| `/code-review`                                  | Correctness, reuse, and simplification, at `--level high` for a diff that touches a request path.     |
| `/security-review`                              | The pending changes on the branch.                                                                    |
| `/simplify`                                     | Quality only. It does not hunt for defects.                                                           |
| A Codex adversarial pass                        | A second vendor's model, so a shared blind spot does not pass twice.                                  |

Run them concurrently. They do not depend on each other, and the slowest one sets
the wall clock.

### When Codex is not reachable

Codex runs through the `codex-check` skill or the `codex-cli` MCP server. Both can
be unavailable, and both can fail quietly: the CLI has exited 0 after printing
only the prompt, and the MCP server has returned a schema error.

If a Codex pass returns no findings, prove that it ran before you record that
result. A tool that failed silently and a reviewer that found nothing produce the
same empty output, and treating the first as the second is how a review gate
becomes decoration.

When Codex is unreachable, substitute a fresh-context `reviewer` subagent on a
different model from the one that wrote the diff, and say in the pull request that
you substituted. Do not record a Codex pass that did not happen.

## Tier 2 runs once, before the stack merges

Tier 2 is expensive. It runs against the accumulated diff of the whole stack, not
per slice.

| Reader                           | What it adds                                                                                |
| -------------------------------- | ------------------------------------------------------------------------------------------- |
| `/ultrareview`                   | Breadth over the whole change set.                                                          |
| `/claude-security:scan`          | The multi-agent security pipeline with an adversarial panel.                                |
| Opus 5 and Fable 5, separately   | Two model families over the same diff. Disagreement between them is a signal worth reading. |
| A Codex pass over the full stack | The cross-vendor check, at stack scope.                                                     |

## Reconcile, do not accumulate

A finding list is not a task list. For each finding, decide.

| Question                                         | Consequence                                                                                                                      |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| Did you already have it?                         | Say so. It counts for the reviewer, not against you.                                                                             |
| Is there a quoted line?                          | Without a quoted file and line, a CRITICAL or HIGH downgrades to MEDIUM.                                                         |
| Is it on the reviewer's own false-positive list? | Reject it and move on. Both reviewer files carry one.                                                                            |
| Did this branch cause it, or find it?            | A defect this branch caused must be fixed here. A pre-existing defect can be deferred, but only in writing, on the pull request. |

That last row is the one people get wrong. A review that widens a small pull
request into a rewrite of everything it touched is its own failure. Fix what you
broke, record what you found, and keep the slice a slice.

Zero findings is a valid outcome. Narrate which tiers you checked and why the
diff passed. A clean review described well is worth more than a defect hunted
badly.

## Fix at the tip

Every fix lands as a new commit. Never amend a commit that is already in the
stack, and never rebase a stacked branch during a live session. A fix for a
defect in slice 1 goes on slice 1's branch, and the branches above it pick it up
at merge.

## Done when

- [ ] You stated your own findings before any agent ran
- [ ] The path-routed reviewer ran for every path class in the diff
- [ ] `/code-review`, `/security-review`, and `/simplify` all ran
- [ ] The Codex pass ran, or the pull request records that it was substituted
- [ ] Every CRITICAL or HIGH carries a quoted proof line
- [ ] Every finding is fixed, rejected as a known false positive, or deferred in
      writing on the pull request
- [ ] Fixes landed as new commits, with nothing amended
- [ ] Tier 2 ran once against the full stack before the merge

## Why two tiers

Running everything on every slice costs about four times a routed tier and finds
little more, because most slices touch one layer. Running everything only at the
end is cheaper still, and it is worse: a defect found against the accumulated
diff means unwinding several stacked slices, which is the exact failure that
slicing exists to prevent.

So the cheap readers run every time, and the expensive ones run once, against the
thing that is actually about to merge.
