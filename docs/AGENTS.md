# Docs Conventions

`docs/` holds the knowledge that the code cannot state by itself: structure, procedure, decisions, and specifications. Read this file before you add or edit any file under `docs/`.

## Folder roles

| Folder | Answers | Reads like |
| --- | --- | --- |
| [`architecture/`](./architecture/INDEX.md) | How does Plane work today? | Reference |
| [`clients/`](./clients/INDEX.md) | What are all the ways to consume Plane? | Reference |
| [`devops/`](./devops/INDEX.md) | How does the code ship, run, and stay watched? | Reference and procedure |
| [`features/`](./features/INDEX.md) | What do we plan to build or change? | Specification |
| [`security/`](./security/INDEX.md) | What does Plane restrict, and where? | Catalog |
| [`sops/`](./sops/INDEX.md) | How do I do this task, step by step? | Procedure |

Pick the folder by the question that the page answers. If two folders fit, write the page in one folder. Add a cross-link from the other.

## Every folder has the same three files

| File | Purpose | Required |
| --- | --- | --- |
| `AGENTS.md` | Conventions for the folder. The rules to follow to add a page. | Yes |
| `INDEX.md` | The folder landing page. States the purpose and links every file in the folder. | Yes |
| `TEMPLATE.md` | The skeleton for a new page in the folder. | Only where the folder holds pages |

A folder that only routes to sub-folders has no `TEMPLATE.md`. `architecture/`, `devops/`, and `features/` are routers. Their sub-folders hold the templates.

A child `AGENTS.md` states only what differs from its parent. Read the parent `AGENTS.md` first.

## Naming

- Use lower-kebab-case for every file name and folder name.
- A numbered page set uses `NN-<slug>.md`. `NN` is zero-padded and starts at `01`.
- A new page takes the next free number. Do not renumber an existing page.
- Sections inside a numbered page use `## N.1` and `## N.2`, and match the page number.
- `sops/` uses `<slug>-sop.md` and no number, because a runbook set has no reading order.
- If a page tracks one Plane work item, prefix the slug with the work item ID. Example: `WEB-8632-stale-chunk-reload.md`.

## INDEX.md maintenance

Update the folder `INDEX.md` in the same commit that adds, renames, or deletes a page. An `INDEX.md` that misses a file is a broken index.

Entry format for a numbered set: `- [N. Title](./NN-slug.md) - one-line summary`.

## Links and code references

- Link another doc with a relative path. Example: `../security/INDEX.md`.
- Reference source code as a backticked path from the repo root. Example: `` `apps/api/plane/app/views/issue/base.py` ``.
- Name the symbol (class, function, or decorator) in backticks next to the path.
- Never cite a line number. Line numbers rot on the next edit.
- Never link to a source blob URL. The commit hash rots.

## Diagrams

- Write diagrams in Mermaid inside a fenced `mermaid` block. GitHub renders it.
- Keep one diagram under about 15 nodes. Split a larger diagram into focused sections in the same page.
- Add a prose table below every diagram. The table holds the detail. The diagram holds the shape.

## Dates and staleness

- Write every date as `YYYY-MM-DD`. Never write a relative date such as "last month".
- A page with a `> **Last reviewed:** YYYY-MM-DD` header needs a fresh stamp on every content edit.

## Language

Write every page in Simplified Technical English.

- Write one instruction per sentence in a procedure. Use 20 words or fewer.
- Use 25 words or fewer in a descriptive sentence. Keep one topic per paragraph.
- Use active voice and simple tenses. Do not join clauses with an `-ing` verb form.
- Use only `can`, `will`, and `must`. Delete `should`, `may`, `might`, and `would`.
- Put the condition before the command: "If the check fails, read the job log."
- Do not use contractions. Do not use semicolons. Write two sentences instead.
- Use one word for one meaning across the whole folder.
- Write more than two items as a vertical list.

## What does not belong in docs/

- Generated output, build artifacts, or dependency reports.
- Secrets, tokens, customer names, or production hostnames.
- A page that restates code a reader can read faster than the page.
- A planning or status note for a single conversation.

## Related

- [`../AGENTS.md`](../AGENTS.md) covers repo commands, code style, and test commands.
- `.github/instructions/` holds Copilot `applyTo:` instruction files. Claude Code does not load them.
- `packages/tailwind-config/AGENTS.md` defines the Canvas, Surface, and Layer background rules.
