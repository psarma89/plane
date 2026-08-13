# L4 Code Conventions

An L4 page zooms into **one component** and traces its implementation through classes and calls.

## The C4 model recommends against this level

Read the canonical guidance before you write anything here.

- "This level of detail is not recommended for anything but the most important or complex components."
- On whether to keep such a diagram as long-lived documentation: "No, particularly for long-lived documentation because most IDEs can generate this level of detail on demand."
- "Ideally this diagram would be automatically generated using tooling (e.g. an IDE or UML modelling tool)."

An empty `code/` folder is a correct and expected state. The code is the source of truth at this zoom. A page that restates it goes stale on the next refactor and then misleads.

## An L4 page zooms into a component

The entry point must be a component that an [`../components/`](../components/INDEX.md) page already documents. Link to that page.

If no L3 page covers the area, write the L3 page first. An L4 page with no L3 parent has no context.

## The gate

Write an L4 page only when all three statements hold.

1. The rule is **non-local**. It spans several symbols, or it comes from a specification or protocol outside the code.
2. Misunderstanding it is **expensive**: data loss, a security hole, or a silent wrong answer.
3. Code, tests, and a generated view **do not already carry it**. An IDE renders the class and call shape on demand, but it cannot render intent.

If the logic is hard because the code is unclear, fix the code. Do not document around it.

## Prefer these alternatives first

| Instead of an L4 page | Do this |
| --- | --- |
| A reader needs the class or call shape | Generate it in an IDE on demand |
| The function is hard to follow | Rename the symbols and split the function |
| The rule is not obvious | Write a test that states the rule in its name |
| The reason is not obvious | Write one comment that states the why |
| The flow crosses files in one process | Write an [`../components/`](../components/INDEX.md) page |
| The flow crosses processes | Write a [`../containers/`](../containers/INDEX.md) dynamic page |
| The flow crosses processes AND the rule depends on that crossing | Keep it here, and say why in `Why this page exists` |

An L4 page is the last option, not the first.

## A diagram here may name another process

The table above sends a cross-process flow to L2. One exception holds.

Keep the page here when the invariant itself depends on the crossing. Document synchronisation is the example: its correctness rests on a distributed lock between two `live` instances, so a single-process diagram would omit the rule the page exists to state.

The test is what the page is for. An L2 dynamic page answers "which containers does this touch, and in what order". An L4 page answers "which rule holds, and what breaks it". Where the second question needs a second process on the diagram, draw it.

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

## Justification

[`TEMPLATE.md`](./TEMPLATE.md) holds the section list. Its `Why this page exists` section names which parts of the gate apply, and why a generated view does not answer the question. A page without that section invites a page for every function.

## Guard against rot

L4 pages rot faster than any other level. Reduce the damage.

- Name a symbol, never a line number.
- Describe the rule, not the statement order.
- Point at the test that pins each rule. A test fails when the rule changes. A page does not.
- Set a review date in the header. Re-read the page when a release touches the entry point.
- If the algorithm changes, rewrite the page or delete it. Never leave a stale L4 page in place.

Deleting a stale L4 page is a correct outcome. A missing page costs a reader one code read. A wrong page costs a reader a wrong belief.
