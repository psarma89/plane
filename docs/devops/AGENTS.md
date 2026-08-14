# DevOps Docs Conventions

DevOps pages describe **how the code ships, where it runs, and how a problem gets noticed**. They describe the current setup, not a plan.

Every page lives in one of three sub-folders.

| Sub-folder | Answers |
| --- | --- |
| [`cicd/`](./cicd/INDEX.md) | Which pipeline runs, when, and what it blocks |
| [`monitoring/`](./monitoring/INDEX.md) | Which signal exists, which alert fires, where to look |
| [`infra/`](./infra/INDEX.md) | Which deployment target exists and what it contains |

## Which sub-folder gets the page

| Question | Sub-folder |
| --- | --- |
| Does the subject run in GitHub Actions or gate a merge? | `cicd/` |
| Does the subject tell an operator that something is wrong? | `monitoring/` |
| Does the subject define what runs where, and with which resources? | `infra/` |

## DevOps pages against SOPs

A DevOps page describes the shape. An SOP gives the steps.

| Content | Folder |
| --- | --- |
| "The release pipeline builds these five images and pushes them to this registry." | `devops/cicd/` |
| "To cut a release, do these nine steps in this order." | [`../sops/`](../sops/INDEX.md) |
| "The API emits these log lines at this level." | `devops/monitoring/` |
| "To find the cause of a 502, run these queries." | [`../sops/`](../sops/INDEX.md) |

If a page starts to read as a numbered procedure, move the procedure to an SOP. Link to it.

Every infra page links to the [`../architecture/c4/l2-containers/`](../architecture/c4/l2-containers/INDEX.md) diagram that shows the same units.
