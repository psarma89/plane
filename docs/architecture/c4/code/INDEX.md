# L4 Code

One algorithm, traced through classes and calls. This level is optional and rarely used.

Read [`../AGENTS.md`](../AGENTS.md) for the shared rules, then [`AGENTS.md`](./AGENTS.md) for the L4 rules and the bar a page must clear. Follow [`TEMPLATE.md`](./TEMPLATE.md).

## Pages

> No page exists yet, and an empty folder is the expected state. Read the bar below before you add one.

Entry format: `- [N. Title](./NN-slug.md) - entry point - one-line summary`

## The C4 model recommends against this level

- "This level of detail is not recommended for anything but the most important or complex components."
- On keeping one as long-lived documentation: "No, particularly for long-lived documentation because most IDEs can generate this level of detail on demand."

At this zoom the code is the source of truth. A page that restates it goes stale on the next refactor and then misleads.

Default to no page. Try the IDE first.

## The bar

Write an L4 page only when at least two statements are true.

1. A competent reader with the file open still cannot follow the logic.
2. The logic is stable. It has not changed in the last several releases.
3. Getting it wrong is expensive: data loss, a security hole, or a silent wrong answer.
4. The reasoning lives outside the code, for example in a specification or a protocol.

If the logic is hard because the code is unclear, fix the code instead.

## Try these first

| Instead of an L4 page | Do this |
| --- | --- |
| A reader needs the class or call shape | Generate it in an IDE on demand |
| The function is hard to follow | Rename the symbols and split the function |
| The rule is not obvious | Write a test that states the rule in its name |
| The reason is not obvious | Write one comment that states the why |
| The flow crosses files in one process | Write an [../components/](../components/INDEX.md) page |
| The flow crosses processes | Write a [../containers/](../containers/INDEX.md) dynamic page |

## Deleting a page here is a correct outcome

A missing page costs a reader one code read. A wrong page costs a reader a wrong belief. If an algorithm changes, rewrite the page or delete it.

## Related

- [../components/INDEX.md](../components/INDEX.md) covers the module that holds the algorithm.
- [../containers/INDEX.md](../containers/INDEX.md) covers flows that cross containers.
