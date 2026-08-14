# Standard Operating Procedures

One page per operational task. Each page gives numbered steps, a verification, and a rollback.

## Pages

- [Local Development Setup](./local-development-setup-sop.md) - Risk: Low - clone the repository, start the stack, register the instance admin, seed demo data, and snapshot the database.
- [Run Backend Tests](./run-backend-tests-sop.md) - Risk: Low - run the 516 `apps/api` pytest tests in Docker, scope a run to a marker or a single test, and read a coverage report.
- [Run JavaScript Tests](./run-javascript-tests-sop.md) - Risk: Low - run the two Vitest suites, and read what they do not cover.
- [Run Static Checks](./run-static-checks-sop.md) - Risk: Low - run lint, format, and type checks, and tell your failure from the two that are already red on dev.

Entry format: `- [Title](./<slug>-sop.md) - Risk: Low | Medium | High - one-line summary`

## Suggested first SOPs

This list is a backlog, not a claim that the pages exist. Delete a row when you write the SOP.

| Task                                             | Risk   | Area          |
| ------------------------------------------------ | ------ | ------------- |
| Cut a release and tag images                     | Medium | Release       |
| Roll back a release                              | High   | Release       |
| Apply a database migration to a running instance | High   | Database      |
| Back up PostgreSQL and object storage            | Medium | Database      |
| Restore PostgreSQL from a backup                 | High   | Database      |
| Rotate instance secrets and API keys             | Medium | Security      |
| Add or change an environment variable            | Low    | Configuration |
| Drain and restart Celery workers                 | Medium | Operations    |
| Clear the Valkey cache safely                    | Medium | Operations    |
| Diagnose a 502 from the proxy                    | Low    | Operations    |
| Upgrade a self-hosted instance                   | High   | Operations    |
| Add a locale and sync translation keys           | Low    | Contributor   |

## Risk levels

[`AGENTS.md`](./AGENTS.md) defines `Low`, `Medium`, and `High`, and states what a `High` SOP needs.

## Related

- [../devops/INDEX.md](../devops/INDEX.md) describes the shape of the systems these SOPs operate.
- [../architecture/c4/l2-containers/INDEX.md](../architecture/c4/l2-containers/INDEX.md) lists the failure modes these SOPs recover.
- [../devops/monitoring/INDEX.md](../devops/monitoring/INDEX.md) links each alert to its SOP.
