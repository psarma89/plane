# L4 Code Conventions

Read [`../AGENTS.md`](../AGENTS.md) first. It holds the naming, diagram, label, and table rules for every level. This file adds only what is specific to L4.

An L4 page traces **one algorithm** through classes and calls.

## Most work needs no L4 page

The C4 model treats L4 as optional and rarely worth the maintenance. The code is the source of truth at this zoom. A page that restates it goes stale on the next refactor and then misleads.

Default to no page. Write one only when the bar below is met.

## The bar

Write an L4 page only when at least two statements are true.

1. A competent reader with the file open still cannot follow the logic.
2. The logic is stable. It has not changed in the last several releases.
3. Getting it wrong is expensive: data loss, a security hole, or a silent wrong answer.
4. The reasoning lives outside the code, for example in a specification or a protocol.

One statement is not enough. Two is the bar.

If the logic is hard because the code is unclear, fix the code. Do not document around it.

## Prefer these alternatives first

| Instead of an L4 page | Do this |
| --- | --- |
| The function is hard to follow | Rename the symbols and split the function |
| The rule is not obvious | Write a test that states the rule in its name |
| The reason is not obvious | Write one comment that states the why |
| The flow crosses files | Write an [`../components/`](../components/INDEX.md) page |
| The flow crosses containers | Write a [`../containers/`](../containers/INDEX.md) dynamic page |

An L4 page is the last option, not the first.

## What belongs here

| Subject | Belongs here |
| --- | --- |
| A conflict-resolution or merge ordering rule | Yes |
| A permission resolution that walks several role tables | Yes |
| An external protocol Plane must match exactly | Yes |
| A cache key derivation with correctness consequences | Yes |
| The classes in one module | No. Use [`../components/`](../components/INDEX.md). |
| A screen or an endpoint | No. Use [`../components/`](../components/INDEX.md). |
| Anything a reader can follow from the code | No. Write no page. |

## Required sections

Follow [`TEMPLATE.md`](./TEMPLATE.md). Every page needs these sections.

| Section | Content |
| --- | --- |
| Header block | `Last reviewed` stamp, the entry point, and the justification |
| Why this page exists | Which statements from the bar apply, and why |
| Entry point | The one symbol a reader starts from |
| Diagram | A Mermaid `classDiagram` or `sequenceDiagram` |
| Symbols | One row per class or function in the diagram |
| Rules | The invariants the algorithm holds |
| Edge cases | The inputs that break a naive implementation |
| Verification | The tests that pin each rule |

## Justification is mandatory

The `Why this page exists` section names the statements from the bar that apply. A page without it invites a page for every function.

## Guard against rot

L4 pages rot faster than any other level. Reduce the damage.

- Name a symbol, never a line number.
- Describe the rule, not the statement order.
- Point at the test that pins each rule. A test fails when the rule changes. A page does not.
- Set a review date in the header. Re-read the page when a release touches the entry point.
- If the algorithm changes, rewrite the page or delete it. Never leave a stale L4 page in place.

Deleting a stale L4 page is a correct outcome. A missing page costs a reader one code read. A wrong page costs a reader a wrong belief.
