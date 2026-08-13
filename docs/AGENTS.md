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

A folder that only routes to sub-folders has no `TEMPLATE.md`. Five folders route: `docs/`, `architecture/`, `architecture/c4/`, `devops/`, and `features/`. Their sub-folders hold the templates.

Before you add a page to any folder, read that folder's `AGENTS.md` and follow its `TEMPLATE.md`. No `INDEX.md` repeats that instruction.

Two rules keep this tree small.

1. **`TEMPLATE.md` is the section list.** No `AGENTS.md` repeats the sections of its own template. To learn which sections a page needs, open the template.
2. **A child `AGENTS.md` states only what differs from its parent.** Read the parent first.

An `AGENTS.md` earns its tokens by holding what a reader cannot see from the folder itself: a repository fact, a trap, or the reason behind a rule.

## Naming

- Use lower-kebab-case for every file name and folder name.
- A numbered page set uses `NN-<slug>.md`. `NN` is zero-padded and starts at `01`.
- A new page takes the next free number. Do not renumber an existing page.
- Sections inside a numbered page use `## N.1` and `## N.2`, and match the page number.
- Three folders do not number their pages, because their sets have no reading order. `sops/` uses `<slug>-sop.md`, `features/` uses the work item slug, and `cicd/` names a page after its workflow file.
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

## Versions and pins

Copy a version, an image tag, or a numeric limit from the source file, character for character. Cite that source file next to the value. Never copy a pin from one doc into another, because a stale pin then spreads to every page that trusts it.

## Secrets and values

Every folder inherits these four rules. No sub-folder repeats them.

- Name an environment variable. Never write its value.
- Write `<redacted>` where a value belongs.
- Never write a production hostname, an internal IP address, a bucket name, or a live workspace slug.
- Treat `.env.example` and `apps/api/.env.example` as the canonical variable list.

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

One exception. A verbatim quotation keeps the wording of its source, even where that wording breaks a rule above. Put it in quotation marks and name the source. Never edit a quote to satisfy a style rule.

## What does not belong in docs/

- Generated output, build artifacts, or dependency reports.
- Secrets, tokens, customer names, or production hostnames.
- A page that restates code a reader can read faster than the page.
- A planning or status note for a single conversation.

## Other files that carry rules

- [`../AGENTS.md`](../AGENTS.md) covers repo commands, code style, and test commands.
- `.github/instructions/` holds Copilot `applyTo:` instruction files. Claude Code does not load them.
- `packages/tailwind-config/AGENTS.md` defines the Canvas, Surface, and Layer background rules.
