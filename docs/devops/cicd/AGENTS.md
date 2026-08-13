# CI/CD Docs Conventions

A CI/CD page describes **one pipeline**. It states the trigger, the jobs, the gate, and the failure recovery.

## One page per workflow

- One page maps to one file in `.github/workflows/`.
- Name the page after the workflow file, without the extension. Example: `pull-request-build-lint-api.md`.
- Files use `NN-<slug>.md` only for a page that spans several workflows. Example: `01-required-checks.md`.
- Add the page to [`INDEX.md`](./INDEX.md) in the same commit.

## Do not restate YAML

A page that repeats the workflow file adds nothing. A reader can open the YAML.

Write the facts the YAML hides.

| Write this | Not this |
| --- | --- |
| Which failure blocks a merge, and which one only warns | The full `steps:` list |
| Why a job exists, and which incident led to it | The `runs-on` value |
| Which secret the job needs, and who grants it | The literal `env:` block |
| How long the job takes, and what makes it slow | Every action version |
| What to do when the job fails | The YAML syntax |

## Blocking against advisory

State the gate for every job. Use exactly one of three words.

| Word | Meaning |
| --- | --- |
| `Blocking` | A failure stops the merge. The check is required on the branch. |
| `Advisory` | A failure reports but does not stop the merge. |
| `Manual` | The job runs only when a person starts it. |

If a check is required in branch protection, say so. Branch protection is not visible in the YAML.

## Branch model

Name the target branch correctly. Plane uses `dev` as the integration branch. A pull request targets `dev`, not `preview`.

## Failure playbook

Every page needs a failure playbook table. Each row must be actionable.

- Good: "`pnpm check:types` fails after a package change. Run `pnpm install` and rebuild the changed package."
- Bad: "Type errors mean the types are wrong."

If the fix needs more than three steps, write an SOP and link to it.

## Secrets

- Name the secret. Never write the value.
- State the scope: repository, organization, or environment.
- State what happens on a fork, where a secret is not available.
