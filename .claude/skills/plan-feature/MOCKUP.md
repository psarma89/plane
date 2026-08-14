# Mockup

A mockup is one static HTML file beside the spec. It answers "what does a user see" in the time it takes to open a file.

It is a sketch of intent. It is not a screenshot, and it is not a component.

## When to build one

Build a mockup when one or more of these is true.

| Trigger                                                 | Example                                      |
| ------------------------------------------------------- | -------------------------------------------- |
| The spec adds a screen, a modal, or a panel             | A cycle detail sidebar                       |
| The spec puts something new into a layout that is dense | A field in a list row that already holds six |
| A user can reach more than two states                   | Empty, filled, truncated, error              |
| The flow crosses more than one screen                   | Create, then confirm, then land              |

Skip the mockup when all of these are true.

- The Frontend plan names no component file, or names one control whose position is obvious.
- The change is copy, translation, or a color token.
- The change is in the data model or the API only.
- The fix restores documented behavior and moves nothing on the screen.

Most features skip it. That is the expected result, not a failure of the step.

Write one line in the spec either way. Record the mockup path, or record the decision to skip and the reason. A silent skip and a forgotten step look the same.

## Rules for the file

Write HTML. A browser draws a layout, and a reviewer sees the real spacing, the real truncation, and the real colors. Fall back to Markdown with a fenced ASCII drawing only when the screen is a simple stack of blocks. State the reason for the fallback in the spec.

1. Name the file after the spec, with the suffix `.mockup.html`. Put it in the same folder. The folder `INDEX.md` lists pages. It does not list a mockup.
2. Write one file, with inline CSS. Do not load a script, a font, or a stylesheet from a network. A reviewer opens the file with `open <path>`, with no build step and no server.
3. Link `packages/tailwind-config/variables.css` with a relative path. Give every `var()` a literal fallback from that same file. The real token wins when the browser loads the stylesheet. The fallback keeps the page readable when the browser refuses a local subresource.
4. Show every state that the spec claims. An empty state that no one drew is an empty state that no one specified.
5. Label each block with the source file that it maps to.
6. Put a banner at the top. State the spec path, the date, and that the file is a sketch.
7. Keep the file under 300 lines. A mockup that needs an hour to read has failed.
8. Take the colors from the `plane-backgrounds` skill. A mockup with invented colors teaches the wrong palette.

## Verify that it renders

Open the file in the headless browser and take a screenshot. A mockup that no one opened can carry a syntax error and still look finished in a diff.

## After the feature ships

Leave the mockup alone. It records what we intended. If the shipped screen differs, state the difference in the implementation note at the top of the spec.

## Why

A layout question that is answered in prose gets answered again in review, and then a third time in the pull request. The three answers rarely match.

The states are the real product of this step. A reviewer who sees the empty row and the truncated row asks about them before the code exists, which is the only time the answer is cheap.
